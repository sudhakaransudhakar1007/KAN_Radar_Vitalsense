"""
Stage 7A E3: Boundary-NaN code path and in-memory trace for VS10_Resting.
Author: Antigravity Assistant (Stage 7A)
"""
import sys
from pathlib import Path
import numpy as np
import scipy.io as sio

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.sync_validation.ecg_processor import (
    clean_ecg_isolated_nans,
    clean_ecg_nans as sync_clean_ecg_nans,
    detect_r_peaks as sync_detect_r_peaks
)
from src.phase3.ecg_reference import (
    clean_ecg_nans as phase3_clean_ecg_nans,
    detect_r_peaks as phase3_detect_r_peaks,
    ECGReferenceValidator
)

def main():
    mat_p = repo_root.parent / "data/VITALSENSE_120_DATASET/VS10/VS10_Resting_Mindray.mat"
    mat = sio.loadmat(str(mat_p))
    ecg_raw = mat["ecg_lead2"].flatten()
    
    print("=== E3. In-Memory Trace for VS10_Resting ===")
    print(f"Total raw ECG samples: {len(ecg_raw)}")
    raw_nans = np.where(np.isnan(ecg_raw))[0]
    print(f"Raw NaN count: {len(raw_nans)}")
    print(f"Raw NaN indices: {raw_nans.tolist()}")
    print(f"Is index 0 NaN?: {0 in raw_nans}")
    
    # 1. Sync validation cleaning: clean_ecg_nans(ecg_raw, only_isolated=True)
    sync_cleaned, n_nans_sync, iso_idx = sync_clean_ecg_nans(ecg_raw, only_isolated=True)
    sync_remaining_nans = np.where(np.isnan(sync_cleaned))[0]
    print(f"\n1. Calling src.sync_validation.ecg_processor.clean_ecg_nans(only_isolated=True):")
    print(f"   Remaining NaNs count: {len(sync_remaining_nans)}")
    print(f"   Remaining NaN indices: {sync_remaining_nans.tolist()}")
    print(f"   Does index 0 get filled?: {0 not in sync_remaining_nans}")
    
    # 2. Phase 3 cleaning: clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)
    p3_cleaned, n_nans_p3, iso_idx_p3 = phase3_clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)
    p3_remaining_nans = np.where(np.isnan(p3_cleaned))[0]
    print(f"\n2. Calling src.phase3.ecg_reference.clean_ecg_nans(only_isolated=True, fill_boundary=True):")
    print(f"   Remaining NaNs count: {len(p3_remaining_nans)}")
    print(f"   Does index 0 get filled?: {0 not in p3_remaining_nans}")
    print(f"   Value used to fill index 0: {p3_cleaned[0]} (raw sample at index 1 is {ecg_raw[1]})")
    
    # 3. Beat counts with only_isolated=True vs only_isolated=False
    # (a) only_isolated=True, fill_boundary=True
    c_true, _, _ = phase3_clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)
    res_true = phase3_detect_r_peaks(c_true, fs=500.0, min_bpm=35.0, max_bpm=185.0)
    beats_true = len(res_true["peaks"])
    valid_beats_true = int(np.sum(res_true["valid_rr_mask"]))
    
    # (b) only_isolated=False, fill_boundary=True
    c_false, _, _ = phase3_clean_ecg_nans(ecg_raw, only_isolated=False, fill_boundary=True)
    res_false = phase3_detect_r_peaks(c_false, fs=500.0, min_bpm=35.0, max_bpm=185.0)
    beats_false = len(res_false["peaks"])
    valid_beats_false = int(np.sum(res_false["valid_rr_mask"]))
    
    print(f"\n3. Beat Counts for VS10_Resting:")
    print(f"   With only_isolated=True, fill_boundary=True:  peaks={beats_true}, valid_RR={valid_beats_true}")
    print(f"   With only_isolated=False, fill_boundary=True: peaks={beats_false}, valid_RR={valid_beats_false}")
    print(f"   Difference: {beats_true - beats_false} peaks")
    
    # (c) Also test with legacy detector
    val = ECGReferenceValidator()
    legacy_res = val.detect_r_peaks_pan_tompkins(c_true)
    print(f"   Legacy Pan-Tompkins detector on c_true: peaks={len(legacy_res.peak_indices)}, valid_RR={legacy_res.valid_rr_count}")
    
    # 4. Check stage6_dryrun.py function calls
    dryrun_p = repo_root / "outputs/closure/stage6_dryrun.py"
    dryrun_lines = dryrun_p.read_text(encoding="utf-8").splitlines()
    print(f"\n4. Function Chain in stage6_dryrun.py:")
    for i, l in enumerate(dryrun_lines):
        if "clean_ecg_nans" in l or "detect_r_peaks" in l:
            print(f"   Line {i+1}: {l.strip()}")

if __name__ == "__main__":
    main()
