"""Comprehensive analysis script for STAGE 5B requirement B5.

Sub-tasks:
  B5(a): VS19 polarity: for all 48 recordings print the median raw ECG value
         at sync_validation R-peaks and at Phase 3 R-peaks, and the sign of
         the bandpassed value at each (summary table, no sample dumps).
         State whether VS19 differs from the rest.
  B5(b): Counterfactual: apply the same interval-assignment rule and the same HR
         definition to both detectors' peaks and report windows with difference > 1 bpm
         and > 3 bpm before and after, overall and excluding VS19.
  B5(c): For the 5 windows rejected by Phase 3 for RR range or coverage (VS03_Resting
         window 21 and the 4 VS16 windows: VS16_Apnea 10, 11; VS16_Resting 9, 10):
         print the RR list of the window in seconds, mark the offending interval,
         and say whether the pattern looks like an ectopic beat or a detection error.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio
from scipy import signal

sys.path.insert(0, str(Path(".").resolve()))
from src.phase3.ecg_reference import ECGReferenceValidator
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator
from src.sync_validation.ecg_processor import clean_ecg_nans, detect_r_peaks


def main():
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    all_mindray = sorted(list(data_dir.glob("*/*_Mindray.mat")))
    p3_val = ECGReferenceValidator(fs_ecg=500.0)
    p3_gen = SupervisedDatasetGenerator(dataset_dir=data_dir, output_dir=Path("outputs/closure/scratch"))

    fs = 500.0
    nyq = 0.5 * fs
    low = 5.0 / nyq
    high = 15.0 / nyq
    b, a = signal.butter(2, [low, high], btype="bandpass")

    # =========================================================================
    # PART A: VS19 Polarity Check across all 48 recordings
    # =========================================================================
    polarity_records = []

    # Store peak data for B5(b)
    recording_data = {}

    for m_path in all_mindray:
        rec_id = m_path.stem.replace("_Mindray", "")
        sub, cond = rec_id.split("_")
        m_mat = sio.loadmat(m_path)
        ecg_raw = m_mat["ecg_lead2"].flatten()

        if rec_id == "VS10_Resting":
            ecg_clean, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True)
            ecg_clean_p3 = ecg_clean
        else:
            miss = p3_val.analyze_missing_samples(ecg_raw)
            ecg_clean_p3 = miss.cleaned_ecg_in_memory
            ecg_clean, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True)

        ecg_filt = signal.filtfilt(b, a, ecg_clean)

        # Detect peaks
        res_p3 = p3_val.detect_r_peaks_pan_tompkins(ecg_clean_p3)
        p3_peaks = res_p3.peak_indices

        res_sync = detect_r_peaks(ecg_clean, fs=fs)
        sync_peaks = res_sync.get("peaks", np.array([], dtype=int))

        # Values at peaks
        p3_raw_vals = ecg_raw[p3_peaks] if len(p3_peaks) > 0 else np.array([])
        p3_filt_vals = ecg_filt[p3_peaks] if len(p3_peaks) > 0 else np.array([])

        sync_raw_vals = ecg_raw[sync_peaks] if len(sync_peaks) > 0 else np.array([])
        sync_filt_vals = ecg_filt[sync_peaks] if len(sync_peaks) > 0 else np.array([])

        med_p3_raw = float(np.median(p3_raw_vals)) if len(p3_raw_vals) > 0 else np.nan
        med_p3_filt = float(np.median(p3_filt_vals)) if len(p3_filt_vals) > 0 else np.nan
        sign_p3_filt = "+" if med_p3_filt > 0 else ("-" if med_p3_filt < 0 else "0")

        med_sync_raw = float(np.median(sync_raw_vals)) if len(sync_raw_vals) > 0 else np.nan
        med_sync_filt = float(np.median(sync_filt_vals)) if len(sync_filt_vals) > 0 else np.nan
        sign_sync_filt = "+" if med_sync_filt > 0 else ("-" if med_sync_filt < 0 else "0")

        polarity_records.append({
            "recording": rec_id,
            "n_p3": len(p3_peaks),
            "med_p3_raw": round(med_p3_raw, 4),
            "med_p3_filt": round(med_p3_filt, 4),
            "sign_p3_filt": sign_p3_filt,
            "n_sync": len(sync_peaks),
            "med_sync_raw": round(med_sync_raw, 4),
            "med_sync_filt": round(med_sync_filt, 4),
            "sign_sync_filt": sign_sync_filt,
        })

        recording_data[rec_id] = {
            "res_p3": res_p3,
            "res_sync": res_sync,
            "cond": cond,
            "p3_peaks": p3_peaks,
            "sync_peaks": sync_peaks,
            "fs": fs,
        }

    df_pol = pd.DataFrame(polarity_records)
    print("=== B5(a) ECG POLARITY TABLE ACROSS ALL 48 RECORDINGS ===")
    print(df_pol.to_string(index=False))

    # =========================================================================
    # PART B: Counterfactual Harmonization Experiment
    # =========================================================================
    # Compare window HR across the 22 windows (win_len=10s, hop=5s):
    # Rule 1: Original (Phase 3: harmonic, midpoint; Sync: arithmetic, second peak)
    # Rule 2: Harmonized midpoint, harmonic HR for both
    # Rule 3: Harmonized midpoint, arithmetic HR for both
    # Rule 4: Harmonized second-peak, harmonic HR for both
    # Rule 5: Harmonized second-peak, arithmetic HR for both

    win_records = []
    for rec_id, d in recording_data.items():
        res_p3 = d["res_p3"]
        res_sync = d["res_sync"]
        cond = d["cond"]

        p3_times = res_p3.peak_times_s
        sync_times = res_sync.get("peak_times", np.array([]))

        # Prep RR intervals
        # Phase 3
        p3_rr = np.diff(p3_times) if len(p3_times) > 1 else np.array([])
        p3_mids = (p3_times[:-1] + p3_times[1:]) / 2.0 if len(p3_times) > 1 else np.array([])
        p3_sec = p3_times[1:] if len(p3_times) > 1 else np.array([])

        # Sync
        sync_rr = res_sync.get("rr_intervals", np.array([]))
        sync_mask = res_sync.get("valid_rr_mask", np.array([]))
        # Sync times has length len(sync_peaks)
        sync_mids = (sync_times[:-1] + sync_times[1:]) / 2.0 if len(sync_times) > 1 else np.array([])
        sync_sec = sync_times[1:] if len(sync_times) > 1 else np.array([])

        for k in range(22):
            t_s = round(k * 5.0, 3)
            t_e = round(t_s + 10.0, 3)

            # --- ORIGINAL S1 METHOD ---
            p3_hr_orig, p3_hr_a_orig, _, _, _, is_valid_p3, _ = p3_gen.compute_window_reference_hr(t_s, t_e, res_p3)

            in_win_sync_orig = (sync_sec >= t_s) & (sync_sec < t_e) & sync_mask
            if np.sum(in_win_sync_orig) > 0:
                sync_hr_orig = float(np.mean((60.0 / sync_rr)[in_win_sync_orig]))
            else:
                sync_hr_orig = np.nan

            # --- HARMONIZED 1: Midpoint assignment + Harmonic HR ---
            # Phase 3 on midpoint
            m_p3_mid = (p3_mids >= t_s) & (p3_mids < t_e)
            rr_p3_mid = p3_rr[m_p3_mid]
            hr_p3_harm_mid = 60.0 / np.mean(rr_p3_mid) if len(rr_p3_mid) > 0 else np.nan

            # Sync on midpoint
            m_sync_mid = (sync_mids >= t_s) & (sync_mids < t_e) & sync_mask
            rr_sync_mid = sync_rr[m_sync_mid]
            hr_sync_harm_mid = 60.0 / np.mean(rr_sync_mid) if len(rr_sync_mid) > 0 else np.nan

            # --- HARMONIZED 2: Midpoint assignment + Arithmetic HR ---
            hr_p3_arith_mid = float(np.mean(60.0 / rr_p3_mid)) if len(rr_p3_mid) > 0 else np.nan
            hr_sync_arith_mid = float(np.mean(60.0 / rr_sync_mid)) if len(rr_sync_mid) > 0 else np.nan

            # --- HARMONIZED 3: Second peak assignment + Harmonic HR ---
            m_p3_sec = (p3_sec >= t_s) & (p3_sec < t_e)
            rr_p3_sec = p3_rr[m_p3_sec]
            hr_p3_harm_sec = 60.0 / np.mean(rr_p3_sec) if len(rr_p3_sec) > 0 else np.nan

            m_sync_sec = (sync_sec >= t_s) & (sync_sec < t_e) & sync_mask
            rr_sync_sec = sync_rr[m_sync_sec]
            hr_sync_harm_sec = 60.0 / np.mean(rr_sync_sec) if len(rr_sync_sec) > 0 else np.nan

            # --- HARMONIZED 4: Second peak assignment + Arithmetic HR ---
            hr_p3_arith_sec = float(np.mean(60.0 / rr_p3_sec)) if len(rr_p3_sec) > 0 else np.nan
            hr_sync_arith_sec = float(np.mean(60.0 / rr_sync_sec)) if len(rr_sync_sec) > 0 else np.nan

            win_records.append({
                "recording": rec_id,
                "scenario": cond,
                "window_idx": k,
                "is_vs19": (rec_id.startswith("VS19")),
                "orig_p3_hr": p3_hr_orig,
                "orig_sync_hr": sync_hr_orig,
                "hr_p3_harm_mid": hr_p3_harm_mid,
                "hr_sync_harm_mid": hr_sync_harm_mid,
                "hr_p3_arith_mid": hr_p3_arith_mid,
                "hr_sync_arith_mid": hr_sync_arith_mid,
                "hr_p3_harm_sec": hr_p3_harm_sec,
                "hr_sync_harm_sec": hr_sync_harm_sec,
                "hr_p3_arith_sec": hr_p3_arith_sec,
                "hr_sync_arith_sec": hr_sync_arith_sec,
            })

    df_win = pd.DataFrame(win_records)

    print("\n=== B5(b) COUNTERFACTUAL HARMONIZATION RESULTS ===")
    configs = [
        ("Original (P3 Harmonic Midpoint vs Sync Arithmetic 2ndPeak)", "orig_p3_hr", "orig_sync_hr"),
        ("Harmonized: Midpoint + Harmonic HR", "hr_p3_harm_mid", "hr_sync_harm_mid"),
        ("Harmonized: Midpoint + Arithmetic HR", "hr_p3_arith_mid", "hr_sync_arith_mid"),
        ("Harmonized: 2nd Peak + Harmonic HR", "hr_p3_harm_sec", "hr_sync_harm_sec"),
        ("Harmonized: 2nd Peak + Arithmetic HR", "hr_p3_arith_sec", "hr_sync_arith_sec"),
    ]

    for title, col_a, col_b in configs:
        sub = df_win.dropna(subset=[col_a, col_b]).copy()
        sub["diff"] = (sub[col_a] - sub[col_b]).abs()
        n_tot = len(sub)
        gt1 = (sub["diff"] > 1.0).sum()
        gt3 = (sub["diff"] > 3.0).sum()
        mean_d = sub["diff"].mean()
        max_d = sub["diff"].max()

        sub_no_vs19 = sub[~sub["is_vs19"]]
        n_no_vs19 = len(sub_no_vs19)
        gt1_no = (sub_no_vs19["diff"] > 1.0).sum()
        gt3_no = (sub_no_vs19["diff"] > 3.0).sum()
        mean_d_no = sub_no_vs19["diff"].mean()
        max_d_no = sub_no_vs19["diff"].max()

        print(f"\n--- {title} ---")
        print(f"  OVERALL (N={n_tot} windows):")
        print(f"    Mean Abs Diff: {mean_d:.4f} bpm | Max: {max_d:.4f} bpm")
        print(f"    Diff > 1 bpm: {gt1} / {n_tot} ({gt1/n_tot*100:.2f}%)")
        print(f"    Diff > 3 bpm: {gt3} / {n_tot} ({gt3/n_tot*100:.2f}%)")
        print(f"  EXCLUDING VS19 (N={n_no_vs19} windows):")
        print(f"    Mean Abs Diff: {mean_d_no:.4f} bpm | Max: {max_d_no:.4f} bpm")
        print(f"    Diff > 1 bpm: {gt1_no} / {n_no_vs19} ({gt1_no/n_no_vs19*100:.2f}%)")
        print(f"    Diff > 3 bpm: {gt3_no} / {n_no_vs19} ({gt3_no/n_no_vs19*100:.2f}%)")

    # =========================================================================
    # PART C: The 5 Rejected Windows in Phase 3
    # =========================================================================
    print("\n=== B5(c) 5 PHASE 3 REJECTED WINDOWS ===")
    # Target windows:
    # VS03_Resting win 21
    # VS16_Apnea win 10, win 11
    # VS16_Resting win 9, win 10

    target_wins = [
        ("VS03_Resting", 21),
        ("VS16_Apnea", 10),
        ("VS16_Apnea", 11),
        ("VS16_Resting", 9),
        ("VS16_Resting", 10),
    ]

    for rec_id, w_idx in target_wins:
        d = recording_data[rec_id]
        res_p3 = d["res_p3"]
        t_s = round(w_idx * 5.0, 3)
        t_e = round(t_s + 10.0, 3)

        p_times = res_p3.peak_times_s
        rrs = np.diff(p_times)
        mids = (p_times[:-1] + p_times[1:]) / 2.0

        mask = (mids >= t_s) & (mids < t_e)
        w_rrs = rrs[mask]
        w_mids = mids[mask]

        p3_h, p3_a, rr_cnt, cov_pct, max_gap, is_valid, rej_reason = (
            p3_gen.compute_window_reference_hr(t_s, t_e, res_p3)
        )

        print(f"\nRecording: {rec_id} | Window Index: {w_idx} (Time: [{t_s}s, {t_e}s])")
        print(f"  Rejection Reason: {rej_reason}")
        print(f"  Coverage: {cov_pct}% | Max Gap: {max_gap}s | Valid: {is_valid}")
        print(f"  Total RR intervals in window: {len(w_rrs)}")
        for idx, (rr, m) in enumerate(zip(w_rrs, w_mids)):
            bpm = 60.0 / rr
            is_phys = (p3_gen.min_rr_s <= rr <= p3_gen.max_rr_s)
            offend = " <-- OFFENDING NON-PHYSIOLOGICAL INTERVAL" if not is_phys else ""
            print(f"    RR[{idx}]: {rr:.4f} s ({bpm:.2f} bpm) [midpoint: {m:.3f}s]{offend}")


if __name__ == "__main__":
    main()
