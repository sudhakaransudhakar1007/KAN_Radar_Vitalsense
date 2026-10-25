"""Update step2b_issue_register.csv for Stage 2HI: items H3 and H4."""

import csv
import pandas as pd
from pathlib import Path


def main():
    csv_path = Path("outputs/phase2a/step2b_issue_register.csv")
    df = pd.read_csv(csv_path)
    print("Initial rows:", len(df))

    old_evidence = {}
    for i in ["ISS-07", "ISS-08", "ISS-09", "ISS-10", "ISS-12", "ISS-21"]:
        old_evidence[i] = df.loc[df["issue_id"] == i, "evidence"].values[0]

    new_evidence = {
        "ISS-07": "Rule best_lag_s >= 4 lumps lags < 4s into NEAR_ZERO_LATENCY, assigning it to -3s (VS05_Apnea) and +3s (VS13_Apnea) with contradictory reason 'curve flatness' when is_ambiguous was False. categorize_monitor_latency is wired at runner.py:164; the v2 results reflect it in outputs/closure/v2/ but outputs/phase2a/ is not regenerated.",
        "ISS-08": "Rule requires only len(valid_rr) >= 5 beats in 120 seconds to award PASS verdict. compute_ecg_sqi runs inside detect_r_peaks and its verdict is not exported; amplitude stability UNSPECIFIED / NOT VALIDATED.",
        "ISS-09": "10-second window yields native frequency resolution of 0.1 Hz = 6.0 bpm; estimator has no parabolic interpolation or zero-padding. estimate_peak_frequency_parabolic is wired inside compute_window_level_hr_agreement; the multi-estimator outputs are not exported; outputs/phase2a/ is not regenerated.",
        "ISS-10": "Trial shifts in [-5, +5]s were optimized and evaluated on the same 23 windows; diagnostic split proves chosen lag fails to generalize on held-out windows. estimate_window_hr_multi_estimator is wired inside compute_window_level_hr_agreement; the multi-estimator outputs are not exported; outputs/phase2a/ is not regenerated.",
        "ISS-12": "File is uncompressed 1.4 MB, contains double-precision floats, 0 NaNs, and 30,600 respiration samples (vs integer ADC counts, compressed ~230 KB, ~120 NaNs, and 30,720 samples in all other 47 files). truncate_respiration_dynamic_length_in_memory is TEST_ONLY; the pipeline already truncates to the minimum length after resampling (runner.py:128 via resample_signals_to_2000hz); the tail-truncation assumption is NOT_VERIFIABLE (see ISS-22).",
        "ISS-21": "Single-sample delimiter NaN interpolation guard (formerly tracked as ISS-13b; only isolated NaNs interpolated, max_gap=1; multi-sample gaps un-interpolated); verified across all 48 Mindray files (5,629 isolated NaNs, 0 multi-sample gaps, 1 edge NaN at index 0 of VS10_Resting filled by nearest value). clean_ecg_isolated_nans is wired through clean_ecg_nans; outputs/phase2a/ is not regenerated.",
    }

    for i, ev in new_evidence.items():
        df.loc[df["issue_id"] == i, "evidence"] = ev

    # Add ISS-23 per H4 if not already present
    if "ISS-23" not in df["issue_id"].values:
        iss23 = {
            "issue_id": "ISS-23",
            "severity": "Medium",
            "file_or_function": "src/sync_validation/cardiac_radar_validator.py:267; src/sync_validation/respiratory_validator.py:225",
            "evidence": "Surrogate columns are not reproducible between runs or diverge from baseline: cardiac_surrogate_mae uses unseeded np.random.permutation; surrogate_control_corr in outputs/phase2a reflects historical circular shift whereas current code uses Fourier phase randomization (N=5).",
            "scientific_risk": "Non-reproducible surrogate metrics prevent exact regression verification and obscure whether statistical null thresholds are consistently satisfied.",
            "recommended_action": "Implement fixed, recorded seeds in the future prespecified N >= 1000 surrogate protocol.",
            "status": "OPEN",
        }
        df = pd.concat([df, pd.DataFrame([iss23])], ignore_index=True)

    df.to_csv(csv_path, index=False, quoting=csv.QUOTE_MINIMAL)
    print("Updated", csv_path, "total rows:", len(df))

    # Validate with strict csv.reader
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, strict=True)
        rows = list(reader)
    print("Strict csv.reader validation: PASS, total rows (inc header):", len(rows))
    for idx, r in enumerate(rows):
        assert len(r) == 7, f"Row {idx} has {len(r)} columns instead of 7"

    # Validate with pandas
    df_v = pd.read_csv(csv_path)
    print("pandas validation: PASS, shape:", df_v.shape)
    print("Status counts:\n", df_v["status"].value_counts().to_dict())

    print("\n=== CHANGED EVIDENCE CELLS ===")
    for i in ["ISS-07", "ISS-08", "ISS-09", "ISS-10", "ISS-12", "ISS-21"]:
        print(f"[{i}] OLD:\n  {old_evidence[i]}")
        print(f"[{i}] NEW:\n  {df_v.loc[df_v['issue_id']==i, 'evidence'].values[0]}\n")

    print("=== NEW ROW ISS-23 ===")
    print(df_v[df_v["issue_id"] == "ISS-23"].to_dict(orient="records")[0])


if __name__ == "__main__":
    main()
