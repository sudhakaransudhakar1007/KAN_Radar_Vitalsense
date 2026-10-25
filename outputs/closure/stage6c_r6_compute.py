"""
R6(b) Script: Recompute LOSO constant-mean baseline & zero-shift radar spectral MAE on run_001.
Author: Antigravity Assistant (Stage 6C)
Diagnostic only on UNAPPROVED run_001 labels.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import scipy.io as sio

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.sync_validation.cardiac_radar_validator import (
    extract_radar_cardiac_signal,
    estimate_window_hr_multi_estimator
)

def main():
    manifest_p = repo_root / "outputs/supervised_dataset/run_001/accepted_window_manifest.csv"
    assert manifest_p.exists(), f"Missing manifest: {manifest_p}"
    
    df = pd.read_csv(manifest_p)
    print(f"Loaded {manifest_p.name}: {len(df)} accepted windows.")
    
    # 1. Leave-One-Subject-Out (LOSO) Constant-Mean Baseline
    # Targets: reference_hr_bpm (harmonic)
    subjects = sorted(df['subject_id'].unique())
    n_subjects = len(subjects)
    
    loso_preds = np.zeros(len(df))
    for s in subjects:
        test_mask = (df['subject_id'] == s)
        train_mask = ~test_mask
        mean_train = df.loc[train_mask, 'reference_hr_bpm'].mean()
        loso_preds[test_mask] = mean_train
        
    df['loso_pred'] = loso_preds
    df['loso_err'] = df['reference_hr_bpm'] - df['loso_pred']
    df['loso_abs_err'] = df['loso_err'].abs()
    df['loso_sq_err'] = df['loso_err'] ** 2
    
    # Overall LOSO metrics
    overall_loso_mae = df['loso_abs_err'].mean()
    overall_loso_rmse = np.sqrt(df['loso_sq_err'].mean())
    
    print("\n=== R6(b) LOSO Constant-Mean Baseline (Diagnostic on UNAPPROVED run_001 labels) ===")
    print(f"Overall (N={len(df)} windows, {n_subjects} subjects):")
    print(f"  LOSO Constant-Mean MAE:  {overall_loso_mae:.4f} bpm")
    print(f"  LOSO Constant-Mean RMSE: {overall_loso_rmse:.4f} bpm")
    
    for cond in ["Resting", "Apnea"]:
        sub_df = df[df['condition'] == cond]
        sub_mae = sub_df['loso_abs_err'].mean()
        sub_rmse = np.sqrt(sub_df['loso_sq_err'].mean())
        print(f"Scenario {cond} (N={len(sub_df)} windows):")
        print(f"  LOSO Constant-Mean MAE:  {sub_mae:.4f} bpm")
        print(f"  LOSO Constant-Mean RMSE: {sub_rmse:.4f} bpm")

    # 2. Zero-Shift Unpadded Radar Spectral MAE on run_001 Accepted Windows
    data_dir = repo_root.parent / "data/VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = repo_root / "data/VITALSENSE_120_DATASET"
        
    rad_fs = 333.3333333333333
    cache_radar = {}
    
    rad_errs_unpadded = []
    rad_errs_parabolic = []
    cond_errs_unpadded = {"Resting": [], "Apnea": []}
    cond_errs_parabolic = {"Resting": [], "Apnea": []}
    
    print("\nComputing zero-shift radar spectral estimates across 1,029 accepted windows...")
    for idx, row in df.iterrows():
        sub = row['subject_id']
        cond = row['condition']
        w_idx = row['window_index']
        ref_hr = row['reference_hr_bpm']
        
        rad_f = data_dir / sub / f"{sub}_{cond}.mat"
        if rad_f not in cache_radar:
            mat = sio.loadmat(str(rad_f))
            raw_vitsig = mat["VitalSig"].flatten()
            cardiac_sig = extract_radar_cardiac_signal(raw_vitsig, rad_fs=rad_fs)
            cache_radar[rad_f] = cardiac_sig
        else:
            cardiac_sig = cache_radar[rad_f]
            
        t_s = w_idx * 5.0
        t_e = t_s + 10.0
        idx_s = int(t_s * rad_fs)
        idx_e = int(t_e * rad_fs)
        w = cardiac_sig[idx_s:idx_e]
        
        est = estimate_window_hr_multi_estimator(w, rad_fs)
        hr_unpad = est["unpadded_bin_bpm"]
        hr_para = est["parabolic_bpm"]
        
        err_unpad = abs(hr_unpad - ref_hr)
        err_para = abs(hr_para - ref_hr)
        
        rad_errs_unpadded.append(err_unpad)
        rad_errs_parabolic.append(err_para)
        cond_errs_unpadded[cond].append(err_unpad)
        cond_errs_parabolic[cond].append(err_para)
        
    print("\n=== R6(b) Zero-Shift Radar Spectral MAE (Diagnostic on UNAPPROVED run_001 labels) ===")
    print(f"Overall (N={len(rad_errs_unpadded)} windows):")
    print(f"  Zero-shift Unpadded FFT argmax bin MAE: {np.mean(rad_errs_unpadded):.4f} bpm")
    print(f"  Zero-shift 3-Point Parabolic MAE:       {np.mean(rad_errs_parabolic):.4f} bpm")
    for cond in ["Resting", "Apnea"]:
        print(f"Scenario {cond} (N={len(cond_errs_unpadded[cond])} windows):")
        print(f"  Zero-shift Unpadded FFT argmax bin MAE: {np.mean(cond_errs_unpadded[cond]):.4f} bpm")
        print(f"  Zero-shift 3-Point Parabolic MAE:       {np.mean(cond_errs_parabolic[cond]):.4f} bpm")

if __name__ == "__main__":
    main()
