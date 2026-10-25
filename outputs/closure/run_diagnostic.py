"""Diagnostic runner for window-level coverage gate evaluation across 48 Mindray files."""

import glob
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scipy.io as sio
import numpy as np
import pandas as pd
from src.sync_validation.ecg_processor import detect_r_peaks, clean_ecg_nans
from src.sync_validation.window_coverage_gate import evaluate_window_rr_coverage


def run():
    data_dir = PROJECT_ROOT.parent / "data" / "VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = PROJECT_ROOT / "data" / "VITALSENSE_120_DATASET"

    mindray_files = sorted(list(data_dir.glob("*/*_Mindray.mat")))
    print(f"Found {len(mindray_files)} Mindray files in {data_dir}.")

    rows = []

    for fpath in mindray_files:
        fname = Path(fpath).name
        # fname e.g. VS01_Resting_Mindray.mat
        stem = fname.replace("_Mindray.mat", "")
        parts = stem.split("_")
        sub_id = parts[0]
        cond = parts[1]

        mat = sio.loadmat(fpath)
        ecg = mat["ecg_lead2"].flatten()

        # Clean NaNs in-memory
        ecg_clean, nan_count, nan_indices = clean_ecg_nans(ecg)

        # Detect R-peaks (Stage 2 version with clean_ecg_nans and SQI)
        r_peaks = detect_r_peaks(ecg_clean, fs=500.0)

        # Evaluate window RR coverage
        win_res = evaluate_window_rr_coverage(
            r_peaks,
            total_duration_s=120.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
            strict_inequality=True,
        )

        total_w = len(win_res)
        acc_w = sum(1 for w in win_res if w["status"] == "ACCEPTED")
        rej_w = total_w - acc_w
        pass_rate = acc_w / total_w if total_w > 0 else 0.0

        # Collect unique rejection reasons
        reasons = sorted(list(set(w["rejection_reason"] for w in win_res if w["rejection_reason"] is not None)))
        reasons_str = "; ".join(reasons) if reasons else "NONE"

        rows.append({
            "subject_id": sub_id,
            "condition": cond,
            "total_windows": total_w,
            "accepted_windows": acc_w,
            "rejected_windows": rej_w,
            "pass_rate": round(pass_rate, 4),
            "rejection_reasons": reasons_str,
        })

    df = pd.DataFrame(rows)
    out_csv = Path("outputs/closure/window_coverage_gate_diagnostic.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")

    print("\n=== SUMMARY ===")
    print(f"Total recordings: {len(df)}")
    print(f"Total windows: {df['total_windows'].sum()}")
    print(f"Total accepted: {df['accepted_windows'].sum()}")
    print(f"Total rejected: {df['rejected_windows'].sum()}")
    overall_pass = df["accepted_windows"].sum() / df["total_windows"].sum()
    print(f"Overall pass rate: {overall_pass:.4f} ({overall_pass*100:.2f}%)")

    for cond in ["Resting", "Apnea"]:
        sub = df[df["condition"] == cond]
        tw = sub["total_windows"].sum()
        aw = sub["accepted_windows"].sum()
        rw = sub["rejected_windows"].sum()
        pr = aw / tw if tw > 0 else 0.0
        print(f"{cond}: {aw}/{tw} accepted ({pr*100:.2f}%), {rw} rejected")

    # Rejection reason breakdown
    print("\n=== REJECTION REASONS ===")
    all_reasons = []
    for r in df["rejection_reasons"]:
        if r != "NONE":
            all_reasons.extend(r.split("; "))
    reason_series = pd.Series(all_reasons).value_counts()
    print(reason_series.to_string())


if __name__ == "__main__":
    run()
