"""Stage 6 Label Specification and Verification Test Suite.

Verifies:
1. Exact continuous-time windowing: 23 windows per 120s recording, boundary sample ranges.
2. NaN boundary cleaning: clean_ecg_nans handles leading/trailing delimiter NaNs without propagating.
3. Polarity-invariant QRS refinement: detect_r_peaks with abs refinement handles inverted signals.
4. Strict all-or-nothing outlier rejection: 1 non-phys RR rejects entire window despite valid coverage.
5. Strict coverage gate: 7.99s covered duration is rejected; 8.01s is accepted.
6. Harmonic mean HR formula (60 / mean(RR)) vs arithmetic mean instantaneous HR.
7. Midpoint assignment rule: interval spanning boundary assigned to exactly one window.
8. Execution guard: SupervisedDatasetGenerator strictly fails when investigator_decision.md is absent.
9. Deterministic surrogate: surrogate control MAE is 100% reproducible with fixed seed.
10. Static check: monitor HR is strictly forbidden from label generation path in src/phase3/.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from src.phase3.ecg_reference import (
    ECGReferenceValidator,
    RPeakQCResult,
    clean_ecg_nans,
    detect_r_peaks,
)
from src.phase3.supervised_dataset_generator import (
    SupervisedDatasetGenerator,
    WindowLabelRecord,
)
from src.sync_validation.cardiac_radar_validator import (
    compute_window_level_hr_agreement,
)


# ==============================================================================
# 1. Continuous-Time Windowing & Boundary Ranges (23 windows / 120s)
# ==============================================================================

def test_23_windows_per_120s_and_exact_boundary_ranges():
    """Verify exact continuous-time windowing yields 23 windows with zero tail truncation."""
    fs_radar = 1000.0 / 3.0  # 333.333333... Hz
    fs_ecg = 500.0
    total_radar_samples = 40000  # 120s
    total_ecg_samples = 60000    # 120s
    win_sec = 10.0
    hop_sec = 5.0
    num_windows = 23

    radar_boundaries = []
    ecg_boundaries = []

    for k in range(num_windows):
        t_start = round(k * hop_sec, 3)
        t_end = round(t_start + win_sec, 3)

        # Radar sample bounds
        r_start = int(round(k * hop_sec * fs_radar))
        r_end = r_start + int(round(win_sec * fs_radar))
        radar_boundaries.append((t_start, t_end, r_start, r_end))

        # ECG sample bounds
        e_start = int(round(t_start * fs_ecg))
        e_end = int(round(t_end * fs_ecg))
        ecg_boundaries.append((t_start, t_end, e_start, e_end))

    # Verify count
    assert len(radar_boundaries) == 23
    assert len(ecg_boundaries) == 23

    # First window
    assert radar_boundaries[0] == (0.0, 10.0, 0, 3333)
    assert ecg_boundaries[0] == (0.0, 10.0, 0, 5000)

    # 23rd window (k = 22)
    assert radar_boundaries[22] == (110.0, 120.0, 36667, 40000)
    assert ecg_boundaries[22] == (110.0, 120.0, 55000, 60000)

    # Zero sample overrun
    assert radar_boundaries[22][3] == total_radar_samples
    assert ecg_boundaries[22][3] == total_ecg_samples


# ==============================================================================
# 2. NaN Boundary Cleaning
# ==============================================================================

def test_clean_ecg_nans_fill_boundary_no_propagation():
    """Verify clean_ecg_nans with fill_boundary=True handles leading/trailing NaNs without propagating."""
    # Signal with leading NaN at 0, internal isolated NaN at 3, trailing NaN at 5
    raw_ecg = np.array([np.nan, 2.0, 3.0, np.nan, 5.0, np.nan], dtype=np.float64)
    cleaned, nan_cnt, isolated_idx = clean_ecg_nans(raw_ecg, only_isolated=True, fill_boundary=True)

    assert nan_cnt == 3
    assert np.isnan(cleaned).sum() == 0, "Cleaned signal must contain zero NaNs"

    # Leading NaN filled with nearest valid sample (index 1 = 2.0)
    assert cleaned[0] == pytest.approx(2.0)
    # Internal NaN interpolated (between 3.0 and 5.0 -> 4.0)
    assert cleaned[3] == pytest.approx(4.0)
    # Trailing NaN filled with nearest valid sample (index 4 = 5.0)
    assert cleaned[5] == pytest.approx(5.0)


def test_clean_ecg_nans_multi_sample_gap_rejected():
    """Verify multi-sample gaps (> 1 contiguous NaN) are not interpolated."""
    raw_ecg = np.array([1.0, np.nan, np.nan, 4.0], dtype=np.float64)
    cleaned, nan_cnt, isolated_idx = clean_ecg_nans(raw_ecg, only_isolated=True, fill_boundary=True)

    # Multi-sample gap remains uninterpolated
    assert np.isnan(cleaned).sum() == 2


# ==============================================================================
# 3. Detect R-Peaks with Abs Refinement (Polarity Inversion)
# ==============================================================================

def test_detect_r_peaks_inverted_polarity_refinement():
    """Verify detect_r_peaks with abs refinement recovers inverted QRS complexes identically."""
    fs = 500.0
    duration_s = 15.0
    t = np.arange(int(duration_s * fs)) / fs

    # Synthesize regular ECG with sharp positive QRS complexes at 1.0s intervals (60 bpm)
    ecg_normal = np.zeros_like(t)
    for p_t in np.arange(1.0, 14.0, 1.0):
        idx = int(p_t * fs)
        ecg_normal[idx - 5 : idx + 5] = 2.0 * np.exp(-0.5 * ((np.arange(-5, 5)) / 1.5) ** 2)

    # Invert polarity (simulate VS19)
    ecg_inverted = -1.0 * ecg_normal

    res_normal = detect_r_peaks(ecg_normal, fs=fs, min_bpm=35.0, max_bpm=185.0)
    res_inverted = detect_r_peaks(ecg_inverted, fs=fs, min_bpm=35.0, max_bpm=185.0)

    assert res_normal["status"] == "SUCCESS"
    assert res_inverted["status"] == "SUCCESS"
    assert len(res_normal["peaks"]) == len(res_inverted["peaks"])
    assert np.allclose(res_normal["peaks"], res_inverted["peaks"], atol=2)


# ==============================================================================
# 4. Strict All-Or-Nothing Outlier Rejection
# ==============================================================================

def test_strict_all_or_nothing_rejection():
    """Verify synthetic window with 10 physiological RR + 1 non-physiological RR is rejected."""
    gen = SupervisedDatasetGenerator()

    # 10 physiological intervals of 0.8s (75 bpm) = 8.0s duration
    # Followed by 1 non-physiological interval of 0.20s (300 bpm, min allowed is 0.3243s)
    # Total intervals = 11, total beats = 12
    p_times = [0.5]
    for _ in range(10):
        p_times.append(p_times[-1] + 0.8)
    p_times.append(p_times[-1] + 0.20)  # non-physiological beat
    p_times = np.array(p_times)

    # Window bounds: [0.0, 10.0]
    hr_h, hr_a, cnt, cov, max_gap, is_valid, rej = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times})

    assert is_valid is False
    assert hr_h is None
    assert rej == "NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW"


# ==============================================================================
# 5. Strict Coverage Gate: 7.99s vs 8.01s
# ==============================================================================

def test_coverage_gate_boundary_7_99s_vs_8_01s():
    """Verify coverage gate rejects window with 7.99s covered duration and accepts 8.01s."""
    gen = SupervisedDatasetGenerator()

    # Case A: 7.99s total covered duration
    # 8 intervals of 0.99875s = 7.99s
    p_times_a = [1.0]
    for _ in range(8):
        p_times_a.append(p_times_a[-1] + 7.99 / 8.0)
    p_times_a = np.array(p_times_a)

    hr_h, hr_a, cnt, cov, max_gap, ok_a, rej_a = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times_a})
    assert ok_a is False
    assert "RR_COVERAGE_BELOW_8.0S" in rej_a

    # Case B: 8.01s total covered duration
    # 8 intervals of 1.00125s = 8.01s (all ~60 bpm, physiological)
    p_times_b = [1.0]
    for _ in range(8):
        p_times_b.append(p_times_b[-1] + 8.01 / 8.0)
    p_times_b = np.array(p_times_b)

    hr_h, hr_a, cnt, cov, max_gap, ok_b, rej_b = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times_b})
    assert ok_b is True
    assert rej_b == "NONE"
    assert hr_h is not None


# ==============================================================================
# 6. Harmonic Mean HR Formula vs Arithmetic Mean
# ==============================================================================

def test_harmonic_hr_formula_vs_arithmetic_hr():
    """Verify reference HR strictly implements harmonic mean (60 / mean(RR))."""
    gen = SupervisedDatasetGenerator()

    # Construct window with five 0.601s intervals (~99.83 bpm) and five 1.001s intervals (~59.94 bpm)
    # Total coverage = 5 * 0.601 + 5 * 1.001 = 8.01s (> 8.0s threshold)
    # Mean RR = 0.801s
    # Harmonic HR = 60.0 / 0.801 = 74.91 bpm
    # Arithmetic HR = (5 * (60/0.601) + 5 * (60/1.001)) / 10 = 79.89 bpm
    intervals = [0.601] * 5 + [1.001] * 5
    p_times = [0.5]
    for dt in intervals:
        p_times.append(p_times[-1] + dt)
    p_times = np.array(p_times)

    hr_h, hr_a, cnt, cov, max_gap, ok, rej = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times})

    assert ok is True
    assert hr_h == pytest.approx(74.91, abs=0.05)
    assert hr_a == pytest.approx(79.89, abs=0.05)
    assert abs(hr_h - hr_a) >= 4.90


# ==============================================================================
# 7. RR Midpoint Assignment Rule
# ==============================================================================

def test_rr_midpoint_boundary_assignment_exactly_once():
    """Verify an interval straddling boundary is assigned to exactly one disjoint window partition."""
    gen = SupervisedDatasetGenerator()

    # Beat spanning across t = 10.0s:
    # Beat 1 at 9.6s, Beat 2 at 10.6s -> midpoint = 10.1s
    # In disjoint partition [0.0, 10.0) vs [10.0, 20.0):
    # Midpoint 10.1s must NOT belong to [0.0, 10.0), and MUST belong to [10.0, 20.0)
    p_times = np.array([9.6, 10.6])

    # Window [0.0, 10.0)
    _, _, cnt_0, _, _, _, rej_0 = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times})
    assert cnt_0 == 0
    assert rej_0 == "NO_RR_INTERVALS_IN_WINDOW"

    # Window [10.0, 20.0)
    mids = (p_times[:-1] + p_times[1:]) / 2.0
    in_win_1 = (mids >= 10.0) & (mids < 20.0)
    assert np.sum(in_win_1) == 1


# ==============================================================================
# 8. Execution Guard: investigator_decision.md Absent
# ==============================================================================

def test_generator_fails_when_investigator_decision_absent():
    """Verify SupervisedDatasetGenerator execution halts if investigator_decision.md is absent."""
    spec_hash = "ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44"
    gen = SupervisedDatasetGenerator(spec_sha256=spec_hash)

    # Ensure decision file does not exist
    dec_file = Path("outputs/closure/investigator_decision.md")
    assert not dec_file.exists(), "investigator_decision.md must not exist before investigator sign-off"

    with pytest.raises(RuntimeError) as exc_info:
        gen.execute_dataset_audit()

    assert "investigator_decision.md does not exist" in str(exc_info.value)


# ==============================================================================
# 9. Deterministic Surrogate Across Runs with Same Seed
# ==============================================================================

def test_surrogate_test_deterministic_across_runs_with_same_seed():
    """Verify cardiac surrogate control MAE is 100% deterministic with fixed seed."""
    rad_fs = 333.3333
    ecg_fs = 500.0
    duration_s = 60.0
    t1 = np.arange(int(30.0 * rad_fs)) / rad_fs
    t2 = np.arange(int(30.0 * rad_fs)) / rad_fs
    # Radar signal with frequency transition: 1.0 Hz (60 bpm) to 2.0 Hz (120 bpm)
    vitalsig = np.concatenate([np.sin(2 * np.pi * 1.0 * t1), np.sin(2 * np.pi * 2.0 * t2)])

    # Mock R-peak result with varying instantaneous HR (1.0s to 0.5s intervals)
    p_times = np.concatenate([np.arange(1.0, 30.0, 1.0), np.arange(30.0, 59.0, 0.5)])
    rrs = np.diff(p_times)
    rpeak_dict = {
        "peaks": (p_times * ecg_fs).astype(int),
        "peak_times": p_times,
        "rr_intervals": rrs,
        "valid_rr_mask": np.ones(len(rrs), dtype=bool),
    }

    res1 = compute_window_level_hr_agreement(vitalsig, rad_fs, rpeak_dict, seed=42)
    res2 = compute_window_level_hr_agreement(vitalsig, rad_fs, rpeak_dict, seed=42)
    res3 = compute_window_level_hr_agreement(vitalsig, rad_fs, rpeak_dict, seed=12345)

    assert res1["status"] == "SUCCESS"
    assert res1["surrogate_seed"] == 42
    assert res1["surrogate_control_mae_bpm"] == res2["surrogate_control_mae_bpm"]
    # With non-constant radar and ECG HR profiles, different seeds yield different control MAEs
    assert res1["surrogate_control_mae_bpm"] != res3["surrogate_control_mae_bpm"]


# ==============================================================================
# 10. Static Check: Monitor HR Forbidden in Label Path
# ==============================================================================

def test_static_check_monitor_hr_never_read_in_label_path():
    """Statically verify that monitor HR channel is never accessed in label-generation path."""
    label_path_files = [
        Path("src/phase3/supervised_dataset_generator.py"),
        Path("src/phase3/ecg_reference.py"),
        Path("src/phase3/window_generator.py"),
    ]

    for p in label_path_files:
        if not p.exists():
            p = Path("kan_radar_HR") / p
        assert p.exists(), f"File {p} must exist"
        content = p.read_text(encoding="utf-8")
        # Ensure 'HR' channel is not loaded as reference ground truth
        assert 'channels["HR"]' not in content, f"Forbidden access to monitor HR in {p.name}"
        assert "channels['HR']" not in content, f"Forbidden access to monitor HR in {p.name}"
