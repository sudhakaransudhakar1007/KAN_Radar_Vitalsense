"""2x2 Ablation Study on Respiratory Cross-Correlation across all 48 recordings.

Ablation factors:
  Factor A: Normalization (Raw unnormalized vs Demeaned + Unit-Variance)
  Factor B: Length Matching (Unequal zero-padded vs Truncated to minimum length)

Evaluates:
  C1: Raw + Unequal (Authors' method)
  C2: Raw + Truncated
  C3: Normalized + Unequal
  C4: Normalized + Truncated (Pipeline method)
  Also tests whether search window bounds (max_lag_sec = 30.0s) alter any peak.
"""

from fractions import Fraction
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio
import scipy.signal as signal

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    data_dir = PROJECT_ROOT.parent / "data" / "VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = PROJECT_ROOT / "data" / "VITALSENSE_120_DATASET"

    df_pub = pd.read_csv("outputs/closure/authors_technical_validation_results.csv")
    df_p2a = pd.read_csv("outputs/phase2a/sync_validation_results.csv")

    rad_files = sorted(list(data_dir.glob("VS*/VS*.mat")))
    rad_files = [f for f in rad_files if not f.name.endswith("_Mindray.mat")]

    rows = []

    for rad_path in rad_files:
        stem = rad_path.stem
        sub_id, cond = stem.split("_")
        ref_path = rad_path.parent / f"{stem}_Mindray.mat"

        rad_mat = sio.loadmat(str(rad_path))
        ref_mat = sio.loadmat(str(ref_path))

        vitsig = rad_mat["VitalSig"].flatten()
        rad_fs = float(rad_mat["Radar"]["fs"][0, 0][0, 0])

        resp = ref_mat["respiration"].flatten()
        ref_fs_resp = float(ref_mat["Fs_resp"][0, 0]) if "Fs_resp" in ref_mat else 256.0

        # Polyphase rational factors
        p_rad = Fraction(2000.0 / rad_fs).limit_denominator(1000).numerator
        q_rad = Fraction(2000.0 / rad_fs).limit_denominator(1000).denominator

        p_resp = Fraction(2000.0 / ref_fs_resp).limit_denominator(1000).numerator
        q_resp = Fraction(2000.0 / ref_fs_resp).limit_denominator(1000).denominator

        v_re = signal.resample_poly(vitsig, p_rad, q_rad)
        r_re = signal.resample_poly(resp, p_resp, q_resp)

        min_len = min(len(v_re), len(r_re))
        v_trunc = v_re[:min_len]
        r_trunc = r_re[:min_len]

        # C1: Raw + Unequal (Authors)
        c1 = signal.correlate(r_re, v_re, mode="full")
        l1 = signal.correlation_lags(len(r_re), len(v_re), mode="full")
        lag_c1 = float(l1[np.argmax(c1)] * 0.5)

        # C2: Raw + Truncated
        c2 = signal.correlate(r_trunc, v_trunc, mode="full")
        l2 = signal.correlation_lags(min_len, min_len, mode="full")
        lag_c2 = float(l2[np.argmax(c2)] * 0.5)

        # C3: Normalized + Unequal
        rn_uneq = (r_re - np.mean(r_re)) / (np.std(r_re) + 1e-12)
        vn_uneq = (v_re - np.mean(v_re)) / (np.std(v_re) + 1e-12)
        c3 = signal.correlate(rn_uneq, vn_uneq, mode="full")
        l3 = signal.correlation_lags(len(r_re), len(v_re), mode="full")
        lag_c3 = float(l3[np.argmax(c3)] * 0.5)

        # C4: Normalized + Truncated (Pipeline)
        rn_tr = (r_trunc - np.mean(r_trunc)) / (np.std(r_trunc) + 1e-12)
        vn_tr = (v_trunc - np.mean(v_trunc)) / (np.std(v_trunc) + 1e-12)
        c4 = signal.correlate(rn_tr, vn_tr, mode="full")
        l4 = signal.correlation_lags(min_len, min_len, mode="full")
        lag_c4 = float(l4[np.argmax(c4)] * 0.5)

        # C4_bounded: Normalized + Truncated with +/- 30s window
        max_lag_samples = int(30.0 * 2000)
        mask = np.abs(l4) <= max_lag_samples
        c4_win = c4[mask]
        l4_win = l4[mask]
        lag_c4_bounded = float(l4_win[np.argmax(c4_win)] * 0.5)

        # Published author lag
        pub_row = df_pub[(df_pub["subjectID"] == sub_id) & (df_pub["scenario"] == cond)]
        pub_lag = float(pub_row["timeLag_ms"].values[0])

        # Pipeline phase2a lag
        p2a_row = df_p2a[(df_p2a["subject_id"] == sub_id) & (df_p2a["condition"] == cond)]
        p2a_lag = float(p2a_row["respiratory_lag_ms"].values[0])

        rows.append({
            "recording_id": stem,
            "subjectID": sub_id,
            "scenario": cond,
            "published_lag_ms": pub_lag,
            "pipeline_lag_ms": p2a_lag,
            "C1_raw_unequal": lag_c1,
            "C2_raw_truncated": lag_c2,
            "C3_norm_unequal": lag_c3,
            "C4_norm_truncated": lag_c4,
            "C4_bounded": lag_c4_bounded,
        })

    df = pd.DataFrame(rows)
    df.to_csv("outputs/closure/respiratory_2x2_ablation.csv", index=False)
    print(f"Saved outputs/closure/respiratory_2x2_ablation.csv with {len(df)} rows.\n")

    # Analyze each condition
    conditions = [
        ("C1 (Raw, Unequal - Authors)", "C1_raw_unequal"),
        ("C2 (Raw, Truncated)", "C2_raw_truncated"),
        ("C3 (Normalized, Unequal)", "C3_norm_unequal"),
        ("C4 (Normalized, Truncated - Pipeline)", "C4_norm_truncated"),
    ]

    print("=== ABLATION RESULTS SUMMARY (N=48) ===")
    for label, col in conditions:
        diff_auth = (df[col] - df["published_lag_ms"]).abs()
        matches_auth = int((diff_auth <= 0.5).sum())
        max_diff_auth = float(diff_auth.max())

        diff_pipe = (df[col] - df["pipeline_lag_ms"]).abs()
        matches_pipe = int((diff_pipe <= 0.5).sum())
        max_diff_pipe = float(diff_pipe.max())

        print(f"\n--- {label} ---")
        print(f"  Matches with Authors (|diff| <= 0.5 ms):  {matches_auth:2d} / 48 ({matches_auth/48*100:.1f}%) | Max |diff|: {max_diff_auth:7.2f} ms")
        print(f"  Matches with Pipeline (|diff| <= 0.5 ms): {matches_pipe:2d} / 48 ({matches_pipe/48*100:.1f}%) | Max |diff|: {max_diff_pipe:7.2f} ms")

    # Specific rows requested: VS01_Apnea, VS18_Resting, VS24_Resting
    print("\n=== SPECIFIC ROWS: VS01_Apnea, VS18_Resting, VS24_Resting ===")
    spec_rows = df[df["recording_id"].isin(["VS01_Apnea", "VS18_Resting", "VS24_Resting"])]
    spec_cols = ["recording_id", "published_lag_ms", "pipeline_lag_ms", "C1_raw_unequal", "C2_raw_truncated", "C3_norm_unequal", "C4_norm_truncated"]
    print(spec_rows[spec_cols].to_string(index=False))

    # Search window bound check: does bounded search change peak?
    diff_bound = (df["C4_norm_truncated"] - df["C4_bounded"]).abs()
    bound_changes = int((diff_bound > 0.0).sum())
    print(f"\n=== SEARCH BOUNDS EFFECT ===")
    print(f"Recordings where +/- 30s search window changes peak: {bound_changes} / 48")
    if bound_changes > 0:
        print(df[diff_bound > 0.0][["recording_id", "C4_norm_truncated", "C4_bounded"]])


if __name__ == "__main__":
    main()
