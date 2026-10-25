"""Targeted tests for ECG window coverage definitions, boundary straddling, and mathematical bounds.

Audits the phenomenon where unclipped midpoint-assigned interval sums reach 110.28%,
contrasting with clipped geometric overlap bounded strictly <= 100.0%, and verifying
that ground-truth heart rate and acceptance verdicts are invariant.
"""

from pathlib import Path
import numpy as np
import pytest

from src.sync_validation.window_coverage_gate import evaluate_window_rr_coverage
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator


def test_synthetic_boundary_straddling_exceeds_100_pct():
    """Verify that unclipped interval summation can mathematically exceed 100% when beats straddle borders."""
    win_s = 10.0
    t_start = 10.0
    t_end = 20.0
    
    # Construct R-peaks such that:
    # First interval: [9.5s, 10.7s], length = 1.2s. Midpoint = 10.1s in [10.0, 20.0).
    # Middle intervals: 9 intervals of 0.9s from 10.7s to 18.8s. All midpoints inside.
    # Last interval: [18.8s, 20.6s], length = 1.8s. Midpoint = 19.7s in [10.0, 20.0).
    peaks = [9.5, 10.7]
    cur = 10.7
    for _ in range(9):
        cur += 0.9
        peaks.append(round(cur, 3))
    peaks.append(20.6)
    peaks = np.array(peaks, dtype=float)
    
    rrs = np.diff(peaks)
    mids = (peaks[:-1] + peaks[1:]) / 2.0
    
    # Check assigned intervals
    mask = (mids >= t_start) & (mids < t_end)
    w_rrs = rrs[mask]
    
    unclipped_sum = float(np.sum(w_rrs))
    unclipped_pct = (unclipped_sum / win_s) * 100.0
    
    # All intervals assigned
    assert len(w_rrs) == len(rrs)
    # Total span is 20.6 - 9.5 = 11.1s > 10.0s
    assert unclipped_sum > 10.0
    assert unclipped_pct > 100.0
    assert round(unclipped_pct, 1) == 111.0


def test_clipped_geometric_overlap_strictly_bounded_at_100_pct():
    """Verify that clipped geometric overlap is strictly bounded in [0.0, 1.0] (<= 100%)."""
    # Using the same synthetic straddling peaks
    peaks = np.array([9.5, 10.7, 11.6, 12.5, 13.4, 14.3, 15.2, 16.1, 17.0, 17.9, 18.8, 20.6], dtype=float)
    
    # In evaluate_window_rr_coverage, intervals are clipped: max(0, min(t2, w_end) - max(t1, w_start))
    r_peaks_dict = {"peak_times": peaks, "fs": 500.0}
    eval_res = evaluate_window_rr_coverage(
        r_peaks_dict,
        total_duration_s=30.0,
        win_sec=10.0,
        hop_sec=5.0,
        min_coverage=0.80,
    )
    
    # Find window for [10.0, 20.0]
    win_10_20 = [w for w in eval_res if abs(w["start_s"] - 10.0) < 1e-4][0]
    
    assert win_10_20["covered_duration_s"] <= 10.0
    assert win_10_20["coverage_fraction"] <= 1.0
    # Exactly 10.0s covered because valid physiological intervals span continuously across [10.0, 20.0]
    assert round(win_10_20["coverage_fraction"], 4) == 1.0000
    assert win_10_20["status"] == "ACCEPTED"


def test_generator_and_gate_both_accept_real_maximum_case():
    """Verify VS13_Apnea window 16 under both unclipped and clipped definitions."""
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")
    
    target_mat = data_dir / "VS13" / "VS13_Apnea_Mindray.mat"
    if not target_mat.exists():
        pytest.skip("Dataset file VS13_Apnea_Mindray.mat not present.")
    
    import scipy.io as sio
    from src.phase3.ecg_reference import clean_ecg_nans
    from src.sync_validation.ecg_processor import detect_r_peaks
    
    mat = sio.loadmat(str(target_mat))
    ecg = mat["ecg_lead2"].flatten()
    ecg_clean, _, _ = clean_ecg_nans(ecg, fill_boundary=True)
    r_peaks = detect_r_peaks(ecg_clean, fs=500.0)
    
    # 1. SupervisedDatasetGenerator evaluation on window 16 (t_start=80.0, t_end=90.0)
    gen = SupervisedDatasetGenerator()
    hr_h, hr_a, n_rrs, cov_pct, max_gap, ok, reason = gen.compute_window_reference_hr(80.0, 90.0, r_peaks)
    
    assert ok is True
    assert round(cov_pct, 2) == 110.28  # Exactly matches reported empirical value
    assert max_gap < 3.0
    assert hr_h is not None and 35.0 <= hr_h <= 185.0
    
    # 2. evaluate_window_rr_coverage evaluation on same window
    gate_res = evaluate_window_rr_coverage(r_peaks, total_duration_s=120.0, win_sec=10.0, hop_sec=5.0)
    win_16_gate = gate_res[16]
    
    assert win_16_gate["start_s"] == 80.0
    assert win_16_gate["end_s"] == 90.0
    assert win_16_gate["status"] == "ACCEPTED"
    assert win_16_gate["covered_duration_s"] <= 10.0
    assert win_16_gate["coverage_fraction"] == 1.0  # Fully covered within boundary


@pytest.mark.parametrize("sub_id,cond,win_idx,expected_unclipped_pct,expected_clipped_bound", [
    ("VS03", "Resting", 0, 84.96, 1.0),   # Minimum coverage case in dataset
    ("VS07", "Apnea", 17, 99.32, 1.0),    # Median coverage case in dataset
    ("VS13", "Apnea", 16, 110.28, 1.0),   # Maximum coverage case in dataset
])
def test_representative_coverage_cases(sub_id, cond, win_idx, expected_unclipped_pct, expected_clipped_bound):
    """Verify minimum, median, and maximum coverage cases across both methods."""
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")
    
    mat_path = data_dir / sub_id / f"{sub_id}_{cond}_Mindray.mat"
    if not mat_path.exists():
        pytest.skip(f"Dataset file {mat_path.name} not present.")
    
    import scipy.io as sio
    from src.phase3.ecg_reference import clean_ecg_nans
    from src.sync_validation.ecg_processor import detect_r_peaks
    
    mat = sio.loadmat(str(mat_path))
    ecg = mat["ecg_lead2"].flatten()
    ecg_clean, _, _ = clean_ecg_nans(ecg, fill_boundary=True)
    r_peaks = detect_r_peaks(ecg_clean, fs=500.0)
    
    t_start = round(win_idx * 5.0, 3)
    t_end = round(t_start + 10.0, 3)
    
    # 1. SupervisedDatasetGenerator unclipped assigned sum
    gen = SupervisedDatasetGenerator()
    hr_h, hr_a, n_rrs, cov_pct, max_gap, ok, reason = gen.compute_window_reference_hr(t_start, t_end, r_peaks)
    assert ok is True
    assert round(cov_pct, 2) == expected_unclipped_pct
    assert max_gap < 3.0
    assert 35.0 <= hr_h <= 185.0
    
    # 2. window_coverage_gate clipped geometric overlap
    gate_res = evaluate_window_rr_coverage(r_peaks, total_duration_s=120.0, win_sec=10.0, hop_sec=5.0)
    win_gate = gate_res[win_idx]
    assert win_gate["status"] == "ACCEPTED"
    assert win_gate["covered_duration_s"] <= 10.0
    assert win_gate["coverage_fraction"] <= expected_clipped_bound
    assert win_gate["coverage_fraction"] > 0.80  # All cases exceed 80% threshold

