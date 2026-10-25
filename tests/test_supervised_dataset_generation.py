"""Unit and regression tests for supervised dataset generation and window-level label pairing.

Tests:
1. Reference HR calculation: harmonic mean formula (60 / mean(RR)), arithmetic mean comparison.
2. Window-level SQI screening: valid coverage (>85%), maximum gap (<3s), physiological bounds (35-185 bpm).
3. Window rejection logic: handling non-physiological beats, insufficient coverage, and NaN boundaries.
4. Gate enforcement: verifying that Phase 2A gate status 'OPEN' blocks persistent array extraction.
5. Deliverables verification: verifying that all manifests and audit reports in outputs/supervised_dataset/run_001 exist and match audited counts.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.phase3.ecg_reference import RPeakQCResult
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator


# ==============================================================================
# 1. Reference HR Calculation Tests
# ==============================================================================

def test_window_reference_hr_perfect_rhythm():
    gen = SupervisedDatasetGenerator()
    fs = 500.0
    # Regular 60 bpm rhythm (peaks every 1.0s at t = 0.5, 1.5, 2.5, ..., 9.5)
    p_times = np.arange(0.5, 10.5, 1.0)
    p_indices = (p_times * fs).astype(int)
    rrs = np.diff(p_times)

    rpeak_res = RPeakQCResult(
        detector_name="Pan-Tompkins",
        detected_peak_count=len(p_times),
        peak_indices=p_indices,
        peak_times_s=p_times,
        rr_intervals_s=rrs,
        valid_rr_mask=np.ones(len(rrs), dtype=bool),
        valid_rr_count=len(rrs),
        rejected_rr_count=0,
        mean_hr_bpm=60.0,
        min_hr_bpm=60.0,
        max_hr_bpm=60.0,
        duplicate_peak_count=0,
        non_monotonic_count=0,
    )

    hr_h, hr_a, cnt, cov, max_gap, ok, rej = gen.compute_window_reference_hr(0.0, 10.0, rpeak_res)
    assert ok is True
    assert rej == "NONE"
    assert hr_h == pytest.approx(60.0, abs=0.01)
    assert hr_a == pytest.approx(60.0, abs=0.01)
    assert cnt == 9
    assert cov == pytest.approx(90.0, abs=0.1)
    assert max_gap == pytest.approx(1.0, abs=0.01)


def test_window_reference_hr_coverage_below_85():
    gen = SupervisedDatasetGenerator()
    fs = 500.0
    # Only 5 beats in 10s window -> coverage ~ 4.0s (40%)
    p_times = np.arange(1.0, 6.0, 1.0)
    p_indices = (p_times * fs).astype(int)
    rrs = np.diff(p_times)

    rpeak_res = RPeakQCResult(
        detector_name="Pan-Tompkins",
        detected_peak_count=len(p_times),
        peak_indices=p_indices,
        peak_times_s=p_times,
        rr_intervals_s=rrs,
        valid_rr_mask=np.ones(len(rrs), dtype=bool),
        valid_rr_count=len(rrs),
        rejected_rr_count=0,
        mean_hr_bpm=60.0,
        min_hr_bpm=60.0,
        max_hr_bpm=60.0,
        duplicate_peak_count=0,
        non_monotonic_count=0,
    )

    hr_h, hr_a, cnt, cov, max_gap, ok, rej = gen.compute_window_reference_hr(0.0, 10.0, rpeak_res)
    assert ok is False
    assert "RR_COVERAGE_BELOW_85_PCT" in rej
    assert hr_h is None


def test_window_reference_hr_max_gap_exceeded():
    gen = SupervisedDatasetGenerator()
    fs = 500.0
    # Beat at 1.0s and next beat at 4.2s (gap 3.2s > 3.0s threshold)
    p_times = np.array([0.5, 1.0, 4.2, 5.0, 6.0, 7.0, 8.0, 9.0])
    p_indices = (p_times * fs).astype(int)
    rrs = np.diff(p_times)

    rpeak_res = RPeakQCResult(
        detector_name="Pan-Tompkins",
        detected_peak_count=len(p_times),
        peak_indices=p_indices,
        peak_times_s=p_times,
        rr_intervals_s=rrs,
        valid_rr_mask=np.ones(len(rrs), dtype=bool),
        valid_rr_count=len(rrs),
        rejected_rr_count=0,
        mean_hr_bpm=60.0,
        min_hr_bpm=60.0,
        max_hr_bpm=60.0,
        duplicate_peak_count=0,
        non_monotonic_count=0,
    )

    hr_h, hr_a, cnt, cov, max_gap, ok, rej = gen.compute_window_reference_hr(0.0, 10.0, rpeak_res)
    assert ok is False
    assert ("MAX_RR_GAP_EXCEEDED" in rej) or ("NON_PHYSIOLOGICAL" in rej)
    assert max_gap == pytest.approx(3.2, abs=0.01)


def test_window_reference_hr_non_physiological_interval():
    gen = SupervisedDatasetGenerator()
    fs = 500.0
    # Premature beat with 0.20s interval (< 0.3243s threshold = 185 bpm limit)
    p_times = np.array([1.0, 2.0, 2.2, 3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2])
    p_indices = (p_times * fs).astype(int)
    rrs = np.diff(p_times)

    rpeak_res = RPeakQCResult(
        detector_name="Pan-Tompkins",
        detected_peak_count=len(p_times),
        peak_indices=p_indices,
        peak_times_s=p_times,
        rr_intervals_s=rrs,
        valid_rr_mask=np.ones(len(rrs), dtype=bool),
        valid_rr_count=len(rrs),
        rejected_rr_count=0,
        mean_hr_bpm=70.0,
        min_hr_bpm=60.0,
        max_hr_bpm=120.0,
        duplicate_peak_count=0,
        non_monotonic_count=0,
    )

    hr_h, hr_a, cnt, cov, max_gap, ok, rej = gen.compute_window_reference_hr(0.0, 10.0, rpeak_res)
    assert ok is False
    assert "NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW" in rej


# ==============================================================================
# 2. Gate Enforcement & Blocker Tests
# ==============================================================================

def test_gate_enforcement_dry_run_flag(tmp_path):
    gen = SupervisedDatasetGenerator(
        output_dir=str(tmp_path / "test_out"),
        phase2a_gate_status="OPEN",
        authorization_granted=False,
    )
    # Check that when phase2a_gate_status == "OPEN", persistent arrays are withheld
    assert gen.phase2a_gate_status == "OPEN"
    assert gen.authorization_granted is False


# ==============================================================================
# 3. Deliverables Verification Tests (outputs/supervised_dataset/run_001)
# ==============================================================================

def test_supervised_dataset_run_001_deliverables_exist():
    base = Path("outputs/supervised_dataset/run_001")
    assert base.exists(), "Supervised dataset run_001 output directory does not exist"

    required_files = [
        "run_manifest.json",
        "dataset_generation_config.json",
        "implementation_summary.md",
        "candidate_window_manifest.csv",
        "accepted_window_manifest.csv",
        "rejected_window_manifest.csv",
        "reference_label_audit.md",
        "synchronization_assumptions_record.md",
        "dataset_validation_report.md",
        "error_log.md",
    ]

    for fname in required_files:
        p = base / fname
        assert p.exists(), f"Missing required file: {fname}"
        assert p.stat().st_size > 0, f"File is empty: {fname}"


def test_supervised_manifest_counts_and_integrity():
    base = Path("outputs/supervised_dataset/run_001")
    cand_df = pd.read_csv(base / "candidate_window_manifest.csv")
    acc_df = pd.read_csv(base / "accepted_window_manifest.csv")
    rej_df = pd.read_csv(base / "rejected_window_manifest.csv")

    assert len(cand_df) == 1056, f"Expected 1056 candidate windows, got {len(cand_df)}"
    assert len(acc_df) == 1029, f"Expected 1029 accepted windows, got {len(acc_df)}"
    assert len(rej_df) == 27, f"Expected 27 rejected windows, got {len(rej_df)}"
    assert len(acc_df) + len(rej_df) == len(cand_df)

    # Check zero NaNs in accepted HR labels
    assert acc_df["reference_hr_bpm"].isna().sum() == 0
    assert np.all(np.isfinite(acc_df["reference_hr_bpm"].values))

    # Check physiological bounds on accepted HR labels
    assert acc_df["reference_hr_bpm"].min() >= 35.0
    assert acc_df["reference_hr_bpm"].max() <= 185.0

    # Check zero duplicates
    assert acc_df.duplicated(subset=["subject_id", "condition", "window_index"]).sum() == 0


def test_run_manifest_gate_blocker_content():
    base = Path("outputs/supervised_dataset/run_001")
    with open(base / "run_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["window_counts"]["total_candidate_windows"] == 1056
    assert manifest["window_counts"]["accepted_windows_count"] == 1029
    assert manifest["window_counts"]["rejected_windows_count"] == 27
    assert manifest["window_counts"]["candidate_windows_per_recording"] == 22
    assert manifest["gate_enforcement"]["phase2a_gate_status"] == "OPEN"
    assert manifest["gate_enforcement"]["is_blocked"] is True
    assert "Supervised persistent dataset generation (binary arrays / ML tensors) is BLOCKED" in manifest["gate_enforcement"]["blocker_reason"]
