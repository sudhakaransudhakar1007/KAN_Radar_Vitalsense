"""Script to execute S1 (ECG harmonization) and S2 (diagnostic baselines)."""

import csv
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio

sys.path.insert(0, str(Path(".").resolve()))
from src.phase3.ecg_reference import ECGReferenceValidator
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator
from src.sync_validation.ecg_processor import clean_ecg_nans, detect_r_peaks
from src.sync_validation.cardiac_radar_validator import (
    estimate_window_hr_multi_estimator,
    extract_radar_cardiac_signal,
)



def main():
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    all_mindray = sorted(list(data_dir.glob("*/*_Mindray.mat")))

    # Initialise phase 3 validator & generator
    p3_val = ECGReferenceValidator(fs_ecg=500.0)
    p3_gen = SupervisedDatasetGenerator(dataset_dir=data_dir, output_dir=Path("outputs/closure/scratch"))

    # S1 Data collection
    s1_rec_records = []
    s1_win_records = []

    print("Running S1 in-memory across all 48 recordings...")
    for m_path in all_mindray:
        rec_id = m_path.stem.replace("_Mindray", "")
        sub, cond = rec_id.split("_")
        r_path = m_path.parent / f"{rec_id}.mat"

        m_mat = sio.loadmat(m_path)
        ecg_raw = m_mat["ecg_lead2"].flatten()

        # ECG cleaning: for VS10_Resting use sync_validation clean for both
        if rec_id == "VS10_Resting":
            ecg_clean_sync, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True)
            ecg_clean_p3 = ecg_clean_sync
        else:
            miss = p3_val.analyze_missing_samples(ecg_raw)
            ecg_clean_p3 = miss.cleaned_ecg_in_memory
            ecg_clean_sync, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True)

        # 1. Detect R-peaks with both detectors
        # Pipeline A (Phase 3)
        res_p3 = p3_val.detect_r_peaks_pan_tompkins(ecg_clean_p3)
        p3_peaks = res_p3.peak_indices
        p3_times = res_p3.peak_times_s


        # Pipeline B (sync_validation)
        res_sync = detect_r_peaks(ecg_clean_sync, fs=500.0)
        sync_peaks = res_sync.get("peaks", np.array([]))
        sync_times = res_sync.get("peak_times", np.array([]))
        sync_valid_mask = res_sync.get("valid_rr_mask", np.array([]))

        # Peak matching within +/- 20 ms (10 samples at 500 Hz)
        # Tolerance: 0.020s
        matched_p3 = 0
        if len(p3_times) > 0 and len(sync_times) > 0:
            for pt in p3_times:
                if np.min(np.abs(sync_times - pt)) <= 0.020:
                    matched_p3 += 1
            match_frac = matched_p3 / len(p3_times)
        else:
            match_frac = 1.0 if len(p3_times) == len(sync_times) == 0 else 0.0

        s1_rec_records.append({
            "recording": rec_id,
            "scenario": cond,
            "n_peaks_p3": len(p3_peaks),
            "n_peaks_sync": len(sync_peaks),
            "peak_match_frac_20ms": round(match_frac, 4),
        })

        # 2. Window HR comparison for the 22 windows (win_len=10s, hop=5s)
        # Setup sync_validation inst_hr
        if len(sync_times) > 1:
            sync_rr = res_sync.get("rr_intervals", np.array([]))
            sync_inst_hr = (60.0 / sync_rr)[sync_valid_mask]
            sync_beat_times = sync_times[1:][sync_valid_mask]
        else:
            sync_inst_hr = np.array([])
            sync_beat_times = np.array([])

        for k in range(22):
            t_s = round(k * 5.0, 3)
            t_e = round(t_s + 10.0, 3)

            # Pipeline A HR (Phase 3 compute_window_reference_hr)
            p3_hr_h, p3_hr_a, rr_cnt, cov_pct, max_gap, is_valid, rej_reason = (
                p3_gen.compute_window_reference_hr(t_s, t_e, res_p3)
            )

            # Pipeline B HR (sync_validation cardiac_radar_validator definition)
            in_win = (sync_beat_times >= t_s) & (sync_beat_times < t_e)
            if np.sum(in_win) > 0:
                sync_hr = float(np.mean(sync_inst_hr[in_win]))
            else:
                sync_hr = np.nan

            s1_win_records.append({
                "recording": rec_id,
                "scenario": cond,
                "window_idx": k,
                "p3_hr_harmonic": p3_hr_h,
                "p3_hr_arithmetic": p3_hr_a,
                "p3_is_valid": is_valid,
                "p3_rej_reason": rej_reason,
                "sync_hr": sync_hr,
            })

    df_rec = pd.DataFrame(s1_rec_records)
    df_win = pd.DataFrame(s1_win_records)

    # Save S1 detailed outputs to closure
    df_rec.to_csv("outputs/closure/s1_recording_peak_comparison.csv", index=False)
    df_win.to_csv("outputs/closure/s1_window_hr_comparison.csv", index=False)

    print("\n=== S1: RECORDING-LEVEL R-PEAK COMPARISON ===")
    print(df_rec.to_string())

    print("\n=== S1: SCENARIO-LEVEL WINDOW HR DIFFERENCES ===")
    for cond in ["Resting", "Apnea"]:
        sub = df_win[df_win["scenario"] == cond].copy()
        # Filter where both produced finite HR
        both_valid = sub.dropna(subset=["p3_hr_harmonic", "sync_hr"]).copy()
        both_valid["diff"] = (both_valid["p3_hr_harmonic"] - both_valid["sync_hr"]).abs()
        both_valid["diff_arith"] = (both_valid["p3_hr_arithmetic"] - both_valid["sync_hr"]).abs()

        mean_diff = both_valid["diff"].mean()
        max_diff = both_valid["diff"].max()
        gt1 = (both_valid["diff"] > 1.0).sum()
        gt3 = (both_valid["diff"] > 3.0).sum()

        mean_diff_a = both_valid["diff_arith"].mean()
        max_diff_a = both_valid["diff_arith"].max()

        print(f"Scenario: {cond}")
        print(f"  Valid windows in both: {len(both_valid)} / {len(sub)}")
        print(f"  Harmonic vs Sync HR: Mean Abs Diff = {mean_diff:.4f} bpm, Max Abs Diff = {max_diff:.4f} bpm")
        print(f"  Windows with Diff > 1.0 bpm: {gt1} ({gt1/len(both_valid)*100:.1f}%)")
        print(f"  Windows with Diff > 3.0 bpm: {gt3} ({gt3/len(both_valid)*100:.1f}%)")
        print(f"  Arithmetic vs Sync HR: Mean Abs Diff = {mean_diff_a:.4f} bpm, Max Abs Diff = {max_diff_a:.4f} bpm")

    # Compare with run_001 accepted manifest
    df_acc = pd.read_csv("outputs/supervised_dataset/run_001/accepted_window_manifest.csv")
    df_acc["key"] = df_acc["subject_id"] + "_" + df_acc["condition"] + "_" + df_acc["window_index"].astype(str)
    df_win["key"] = df_win["recording"] + "_" + df_win["window_idx"].astype(str)

    merged = df_win.merge(df_acc[["key", "reference_hr_bpm"]], on="key")
    print(f"\nMerged with run_001 accepted windows: {len(merged)} windows")
    for cond in ["Resting", "Apnea"]:
        sub_m = merged[merged["scenario"] == cond]
        # Diff between p3_hr_harmonic in memory and accepted manifest
        p3_diff = (sub_m["p3_hr_harmonic"] - sub_m["reference_hr_bpm"]).abs().mean()
        # Diff between sync_hr and accepted manifest
        sync_diff = (sub_m["sync_hr"] - sub_m["reference_hr_bpm"]).abs().mean()
        print(f"Scenario {cond} vs run_001 accepted reference_hr_bpm:")
        print(f"  Mean Abs Diff (In-memory Phase 3 vs manifest): {p3_diff:.4f} bpm")
        print(f"  Mean Abs Diff (sync_validation HR vs manifest): {sync_diff:.4f} bpm")

    print("\n=== S2: BASELINES ON EXISTING LABELS ===")
    # (a) LOSO Constant-Mean Predictor
    # Evaluate across all accepted windows in df_acc
    print("Evaluating LOSO Constant-Mean Predictor on accepted_window_manifest.csv...")
    df_acc["y"] = df_acc["reference_hr_bpm"]
    subjects = df_acc["subject_id"].unique()

    # Overall LOSO
    overall_errs = []
    overall_sq_errs = []
    for s in subjects:
        train = df_acc[df_acc["subject_id"] != s]
        test = df_acc[df_acc["subject_id"] == s]
        pred = train["y"].mean()
        overall_errs.extend((test["y"] - pred).abs().tolist())
        overall_sq_errs.extend(((test["y"] - pred) ** 2).tolist())

    loso_overall_mae = np.mean(overall_errs)
    loso_overall_rmse = np.sqrt(np.mean(overall_sq_errs))

    # Scenario-specific LOSO
    loso_scen = {}
    for cond in ["Resting", "Apnea"]:
        sub_df = df_acc[df_acc["condition"] == cond]
        errs = []
        sq_errs = []
        for s in subjects:
            train = sub_df[sub_df["subject_id"] != s]
            test = sub_df[sub_df["subject_id"] == s]
            if len(test) == 0:
                continue
            pred = train["y"].mean()
            errs.extend((test["y"] - pred).abs().tolist())
            sq_errs.extend(((test["y"] - pred) ** 2).tolist())
        loso_scen[cond] = {
            "n": len(errs),
            "mae": np.mean(errs),
            "rmse": np.sqrt(np.mean(sq_errs)),
        }

    print(f"LOSO Overall: N={len(overall_errs)}, MAE={loso_overall_mae:.4f} bpm, RMSE={loso_overall_rmse:.4f} bpm")
    for cond in ["Resting", "Apnea"]:
        print(f"LOSO {cond}: N={loso_scen[cond]['n']}, MAE={loso_scen[cond]['mae']:.4f} bpm, RMSE={loso_scen[cond]['rmse']:.4f} bpm")

    # (b) Zero-shift Radar Spectral Estimator
    # Use existing estimators in cardiac_radar_validator
    print("\nEvaluating Zero-Shift Radar Spectral Estimators vs accepted labels...")
    unpadded_errs = []
    parabolic_errs = []
    scen_unpadded = {"Resting": [], "Apnea": []}
    scen_parabolic = {"Resting": [], "Apnea": []}

    # Cache preprocessed radar signals per recording
    radar_cardiac_cache = {}

    for _, row in df_acc.iterrows():
        rec_id = row["subject_id"] + "_" + row["condition"]
        cond = row["condition"]
        if rec_id not in radar_cardiac_cache:
            r_path = data_dir / row["subject_id"] / f"{rec_id}.mat"
            r_mat = sio.loadmat(r_path)
            vitsig = r_mat["VitalSig"].flatten()
            cardiac_sig = extract_radar_cardiac_signal(vitsig, rad_fs=333.3333333333333)
            radar_cardiac_cache[rec_id] = cardiac_sig

        cardiac_sig = radar_cardiac_cache[rec_id]
        idx_s = int(row["radar_sample_start"])
        idx_e = int(row["radar_sample_end"])
        w = cardiac_sig[idx_s:idx_e]

        est = estimate_window_hr_multi_estimator(w, rad_fs=333.3333333333333)
        y_true = row["reference_hr_bpm"]

        err_unp = abs(est["unpadded_bin_bpm"] - y_true)
        err_para = abs(est["parabolic_bpm"] - y_true)

        unpadded_errs.append(err_unp)
        parabolic_errs.append(err_para)
        scen_unpadded[cond].append(err_unp)
        scen_parabolic[cond].append(err_para)

    print(f"Radar Spectral Zero-Shift Overall (N={len(unpadded_errs)} windows):")
    print(f"  Unpadded FFT Peak MAE: {np.mean(unpadded_errs):.4f} bpm")
    print(f"  Parabolic Peak MAE:    {np.mean(parabolic_errs):.4f} bpm")

    for cond in ["Resting", "Apnea"]:
        print(f"Radar Spectral Zero-Shift {cond} (N={len(scen_unpadded[cond])} windows):")
        print(f"  Unpadded FFT Peak MAE: {np.mean(scen_unpadded[cond]):.4f} bpm")
        print(f"  Parabolic Peak MAE:    {np.mean(scen_parabolic[cond]):.4f} bpm")


if __name__ == "__main__":
    main()
