"""Execution script for K1 and K2 requirements."""

import csv
from datetime import datetime, timezone
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio

sys.path.insert(0, str(Path(".").resolve()))
from src.sync_validation.ecg_processor import clean_ecg_nans, detect_r_peaks



def mtime_str(p: Path) -> str:
    mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
    return mtime.strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    print("=== K1: MODIFICATION TIMES ===")
    phase3_files = sorted(Path("src/phase3").glob("*.py"))
    print("src/phase3 files:")
    for f in phase3_files:
        print(f"  {f.name:35s}: {mtime_str(f)}")

    run001_dir = Path("outputs/supervised_dataset/run_001")
    run001_files = sorted(run001_dir.glob("*.*"))
    print("\noutputs/supervised_dataset/run_001 files:")
    for f in run001_files:
        print(f"  {f.name:35s}: {mtime_str(f)}")

    print("\n=== K1: REJECTED MANIFEST VALUE COUNTS ===")
    rej_path = run001_dir / "rejected_window_manifest.csv"
    df_rej = pd.read_csv(rej_path)
    print("Overall rejection_reason value counts:")
    print(df_rej["rejection_reason"].value_counts())

    print("\nRejection reasons per recording (counts only):")
    df_rej["recording"] = df_rej["subject_id"] + "_" + df_rej["condition"]
    per_rec = df_rej.groupby(["recording", "rejection_reason"]).size().reset_index(name="count")
    for _, row in per_rec.iterrows():
        print(f"  {row['recording']:15s} | {row['rejection_reason']:50s} | count = {row['count']}")

    print("\nExact rejection_reason strings for VS10_Resting:")
    vs10_reasons = df_rej[df_rej["recording"] == "VS10_Resting"]["rejection_reason"].unique()
    for r in vs10_reasons:
        print(f"  '{r}'")

    print("\n=== K1: IN-MEMORY VS10_RESTING ECG EXPERIMENT ===")
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")
    mat_path = data_dir / "VS10" / "VS10_Resting_Mindray.mat"
    mat = sio.loadmat(mat_path)
    ecg_raw = mat["ecg_lead2"].flatten()

    print(f"VS10_Resting ecg_raw len: {len(ecg_raw)}, isnan[0]: {np.isnan(ecg_raw[0])}, total NaNs: {np.isnan(ecg_raw).sum()}")

    # Test 1: clean_ecg_nans with only_isolated=False
    clean_f, n_f, _ = clean_ecg_nans(ecg_raw, only_isolated=False)
    res_f = detect_r_peaks(clean_f, fs=500.0)

    # Test 2: clean_ecg_nans with current default (only_isolated=True)
    clean_t, n_t, _ = clean_ecg_nans(ecg_raw, only_isolated=True)
    res_t = detect_r_peaks(clean_t, fs=500.0)

    print(f"clean_ecg_nans(only_isolated=False): status={res_f['status']}, valid_peak_count={res_f['valid_peak_count']}, NaNs cleaned={n_f}")
    print(f"clean_ecg_nans(only_isolated=True) : status={res_t['status']}, valid_peak_count={res_t['valid_peak_count']}, NaNs cleaned={n_t}")
    print(f"Beat count identical: {res_f['valid_peak_count'] == res_t['valid_peak_count']}")
    if len(res_f["peaks"]) > 0 and len(res_t["peaks"]) > 0:
        print(f"Max abs peak diff: {np.max(np.abs(res_f['peaks'] - res_t['peaks']))} samples")

    print("\n=== K2: AGGREGATE LABEL STATISTICS (ACCEPTED MANIFEST) ===")
    acc_path = run001_dir / "accepted_window_manifest.csv"
    df_acc = pd.read_csv(acc_path)
    print("Overall accepted rows:", len(df_acc))

    for cond in ["Resting", "Apnea"]:
        sub_df = df_acc[df_acc["condition"] == cond]
        vals = sub_df["reference_hr_bpm"]
        outside = ((vals < 40.0) | (vals > 180.0)).sum()
        print(f"\nCondition: {cond}")
        print(f"  Row count: {len(sub_df)}")
        print(f"  Mean:      {vals.mean():.2f} bpm")
        print(f"  Std:       {vals.std():.2f} bpm")
        print(f"  Min:       {vals.min():.2f} bpm")
        print(f"  Max:       {vals.max():.2f} bpm")
        print(f"  Outside [40, 180] bpm: {outside}")


if __name__ == "__main__":
    main()
