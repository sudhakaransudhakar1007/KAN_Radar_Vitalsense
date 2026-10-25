"""Phase 2A Step 2 Synchronization Validation Runner."""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import scipy.io as sio

from .cardiac_radar_validator import (
    compute_window_level_hr_agreement,
    extract_radar_cardiac_signal,
    synthetic_known_offset_test,
)
from .ecg_processor import (
    clean_ecg_nans,
    derive_1hz_ecg_hr,
    detect_r_peaks,
    scan_monitor_hr_lag,
)
from .respiratory_validator import (
    compute_respiratory_xcorr,
    compute_surrogate_respiratory_control,
    resample_signals_to_2000hz,
)


def categorize_monitor_latency(
    best_lag_s: float,
    is_ambiguous: bool,
    mae_improvement_bpm: float = 0.0,
) -> Tuple[str, str]:
    """Categorize monitor HR latency relative to continuous ECG ground truth.

    Addresses ISS-07: Separates:
      - Negative lags (tau < -1.0s): 'NEGATIVE_LAG_OBSERVED' (observed offset; cause NOT_VERIFIABLE)
      - Near-zero lags (|tau| <= 1.0s): 'NEAR_ZERO_LATENCY' (synchronous within 1.0s quantization)
      - Small non-zero lags (1.0s < tau < 4.0s): 'SMALL_NONZERO_LAG'
      - Large lags (tau >= 4.0s): 'EMPIRICAL_LATENCY_OBSERVED'
      - Low HRV: 'INCONCLUSIVE_LOW_HRV' (MAE curve flatness indicates low HR variance)

    Neutral wording: cause NOT_VERIFIABLE (hardware timing UNVERIFIED).
    Mention curve flatness ONLY when is_ambiguous is True.
    Format tau with one decimal without -0s.
    """
    if not np.isfinite(best_lag_s):
        return "INCONCLUSIVE", "Insufficient valid HR data"

    # Avoid -0.0s formatting for floating-point zero
    lag_val = 0.0 if abs(best_lag_s) < 1e-12 else best_lag_s

    if is_ambiguous:
        return (
            "INCONCLUSIVE_LOW_HRV",
            f"Optimal lag {lag_val:+.1f}s is ambiguous; MAE curve flatness indicates low HR variance",
        )

    if lag_val < -1.0:
        return (
            "NEGATIVE_LAG_OBSERVED",
            f"Optimal lag {lag_val:+.1f}s (negative shift observed offset; cause NOT_VERIFIABLE (hardware timing UNVERIFIED))",
        )
    elif abs(lag_val) <= 1.0:
        return (
            "NEAR_ZERO_LATENCY",
            f"Optimal lag {lag_val:+.1f}s within |tau| <= 1.0s threshold",
        )
    elif 1.0 < lag_val < 4.0:
        return (
            "SMALL_NONZERO_LAG",
            f"Optimal lag {lag_val:+.1f}s (small positive shift 1.0s < tau < 4.0s, MAE improvement {mae_improvement_bpm:.2f} bpm; cause NOT_VERIFIABLE (hardware timing UNVERIFIED))",
        )
    else:  # lag_val >= 4.0
        return (
            "EMPIRICAL_LATENCY_OBSERVED",
            f"Optimal MAE at lag {lag_val:+.1f}s (MAE improvement {mae_improvement_bpm:.2f} bpm; observed offset, display/averaging delay unverified; cause NOT_VERIFIABLE (hardware timing UNVERIFIED))",
        )


def run_full_validation(
    dataset_dir: Path,
    output_dir: Optional[Path] = None,
    allow_phase2a_overwrite: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Execute complete synchronization and monitor latency audit across all 48 candidate pairs.

    Args:
        dataset_dir: Path to VITALSENSE_120_DATASET.
        output_dir: Destination path for outputs (must be explicitly provided).
        allow_phase2a_overwrite: Explicit flag required to write to protected outputs/phase2a.

    Returns:
        (results_dataframe, summary_statistics_dict)
    """
    if output_dir is None:
        raise ValueError(
            "output_dir must be explicitly specified. Defaulting to 'outputs/phase2a' is forbidden."
        )
    out_resolved = Path(output_dir).resolve()
    phase2a_resolved = Path("outputs/phase2a").resolve()
    if (out_resolved == phase2a_resolved or (out_resolved.name == "phase2a" and out_resolved.parent.name == "outputs")) and not allow_phase2a_overwrite:
        raise PermissionError(
            "Writing directly to immutable 'outputs/phase2a' is blocked by governance guard. Pass allow_phase2a_overwrite=True to override."
        )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    radar_files = sorted(glob.glob(str(dataset_dir / "VS*" / "VS*.mat")))
    radar_only = [f for f in radar_files if not f.endswith("_Mindray.mat")]

    rows: List[Dict[str, Any]] = []

    for rad_path_str in radar_only:
        rad_path = Path(rad_path_str)
        base_name = rad_path.stem  # e.g. VS01_Resting
        sub_id, cond = base_name.split("_")
        ref_path = rad_path.parent / f"{base_name}_Mindray.mat"

        if not ref_path.exists():
            continue

        # Load MAT files strictly into temporary in-memory variables
        rad_mat = sio.loadmat(str(rad_path))
        ref_mat = sio.loadmat(str(ref_path))

        vitsig = rad_mat["VitalSig"].flatten()
        rad_fs = float(rad_mat["Radar"]["fs"][0, 0][0, 0])

        ecg_raw = ref_mat["ecg_lead2"].flatten()
        mon_hr = ref_mat["HR"].flatten().astype(float)
        resp_raw = ref_mat["respiration"].flatten()
        ref_fs_resp = float(ref_mat["Fs_resp"][0, 0]) if "Fs_resp" in ref_mat else 256.0

        # 1. ECG R-peak detection & in-memory NaN cleaning
        ecg_clean, nan_count, nan_indices = clean_ecg_nans(ecg_raw)
        r_peaks = detect_r_peaks(ecg_clean, fs=500.0)

        # 2. Derive continuous 1 Hz ECG HR
        t_grid, ecg_hr_1hz, hr_convention = derive_1hz_ecg_hr(r_peaks, total_seconds=120)

        # 3. Scan monitor HR latency over +/- 10s
        mon_lag_res = scan_monitor_hr_lag(ecg_hr_1hz, mon_hr, max_lag_s=10)

        # 4. Respiratory cross-correlation (TechValidation.m)
        v_2000, r_2000 = resample_signals_to_2000hz(vitsig, rad_fs, resp_raw, ref_fs_resp)
        resp_xcorr = compute_respiratory_xcorr(v_2000, r_2000, max_lag_sec=30.0)
        surr_ctrl = compute_surrogate_respiratory_control(v_2000, r_2000)

        # 5. Radar-to-ECG cardiac window-level HR agreement (10s win, 5s hop)
        cardiac_res = compute_window_level_hr_agreement(vitsig, rad_fs, r_peaks)

        # 6. Categorize statuses per strict Section 8 rules
        # Radar-to-ECG synchronization status:
        # Hardware trigger / clock absent in MAT files -> Retain UNVERIFIED_TIMING
        # (or PARTIALLY_ALIGNED where respiratory correlation peak is robust)
        if cond == "Resting":
            if resp_xcorr["pos_corr"] >= 0.40 and abs(resp_xcorr["pos_lag_ms"]) < 50.0:
                radar_sync_status = "PARTIALLY_ALIGNED"
                radar_sync_reason = f"Respiratory xcorr r={resp_xcorr['pos_corr']:.2f} at {resp_xcorr['pos_lag_ms']:.1f}ms; hardware clock absent"
            else:
                radar_sync_status = "UNVERIFIED_TIMING"
                radar_sync_reason = "Sub-second hardware clock absent; respiratory correlation weak"
        else:  # Apnea
            # During apnea, breathing motion is suppressed; rely on cardiac BCG window agreement
            if cardiac_res.get("zero_shift_mae_bpm", 999.0) < 5.0:
                radar_sync_status = "PARTIALLY_ALIGNED"
                radar_sync_reason = f"Apnea cardiac window MAE={cardiac_res['zero_shift_mae_bpm']:.2f} bpm; hardware clock absent"
            else:
                radar_sync_status = "UNVERIFIED_TIMING"
                radar_sync_reason = "Apnea respiration suppressed; sub-second hardware clock unverified"

        # Monitor HR latency status (refactored per ISS-07):
        best_lag_s = mon_lag_res["best_lag_s"]
        is_ambig = mon_lag_res["is_ambiguous"]
        mae_imp = mon_lag_res["mae_improvement_bpm"]
        mon_latency_status, mon_latency_reason = categorize_monitor_latency(best_lag_s, is_ambig, mae_imp)

        next_action = "Derive ground truth from ecg_lead2 R-peaks rather than delayed monitor HR array"

        row = {
            "subject_id": sub_id,
            "condition": cond,
            "radar_path": str(rad_path.relative_to(dataset_dir.parent.parent)),
            "reference_path": str(ref_path.relative_to(dataset_dir.parent.parent)),
            "pairing_status": "PROBABLE_MATCH",
            "timing_metadata_availability": "MAT_HEADERS_LACK_HARDWARE_TRIGGER",
            "ecg_quality_status": r_peaks["qc_verdict"],
            "ecg_nan_count": nan_count,
            "valid_r_peak_count": r_peaks["valid_peak_count"],
            "mean_ecg_hr_bpm": round(r_peaks["mean_hr_bpm"], 2),
            "hr_series_validity": "VALID_120S",
            "monitor_hr_lag_estimate_s": best_lag_s,
            "lag_sign_convention": "POSITIVE_MEANS_MONITOR_LAGS_BEHIND_ECG",
            "zero_shift_monitor_hr_mae": mon_lag_res["zero_lag_mae_bpm"],
            "zero_shift_monitor_hr_corr": mon_lag_res["zero_lag_corr"],
            "best_shift_monitor_hr_mae": mon_lag_res["best_mae_bpm"],
            "best_shift_monitor_hr_corr": mon_lag_res["best_corr"],
            "monitor_lag_is_ambiguous": mon_lag_res["is_ambiguous"],
            "valid_sample_count": 120 - abs(int(best_lag_s)) if np.isfinite(best_lag_s) else 0,
            "radar_ecg_alignment_method": "CARDIAC_BAND_10S_WINDOW_FFT",
            "radar_ecg_window_mae_zero": cardiac_res["zero_shift_mae_bpm"],
            "radar_ecg_window_corr_zero": cardiac_res["zero_shift_corr"],
            "radar_ecg_best_shift_s": cardiac_res["best_shift_s"],
            "radar_ecg_best_shift_mae": cardiac_res["best_shift_mae_bpm"],
            "cardiac_surrogate_mae": cardiac_res.get("surrogate_control_mae_bpm", np.nan),
            "respiratory_lag_ms": resp_xcorr["pos_lag_ms"],
            "respiratory_corr": resp_xcorr["pos_corr"],
            "respiratory_polarity": resp_xcorr["polarity"],
            "respiratory_uniqueness": resp_xcorr["peak_uniqueness"],
            "surrogate_control_corr": surr_ctrl["max_surrogate_corr"],
            "radar_to_ecg_sync_status": radar_sync_status,
            "radar_to_ecg_reason": radar_sync_reason,
            "monitor_hr_latency_status": mon_latency_status,
            "monitor_hr_reason": mon_latency_reason,
            "reason_and_next_action": next_action,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_path = output_dir / "sync_validation_results.csv"
    df.to_csv(csv_path, index=False)

    if len(df) == 0:
        return df, {"total_pairs_evaluated": 0, "resting_pairs": 0, "apnea_pairs": 0}

    # Compute summary statistics
    summary_stats = {
        "total_pairs_evaluated": len(df),
        "resting_pairs": int(np.sum(df["condition"] == "Resting")),
        "apnea_pairs": int(np.sum(df["condition"] == "Apnea")),
        "resting_resp_lag_mean_ms": float(df[df["condition"] == "Resting"]["respiratory_lag_ms"].mean()),
        "resting_resp_lag_std_ms": float(df[df["condition"] == "Resting"]["respiratory_lag_ms"].std()),
        "resting_resp_corr_mean": float(df[df["condition"] == "Resting"]["respiratory_corr"].mean()),
        "apnea_resp_lag_mean_ms": float(df[df["condition"] == "Apnea"]["respiratory_lag_ms"].mean()),
        "apnea_resp_lag_std_ms": float(df[df["condition"] == "Apnea"]["respiratory_lag_ms"].std()),
        "apnea_resp_corr_mean": float(df[df["condition"] == "Apnea"]["respiratory_corr"].mean()),
        "monitor_lag_mean_s": float(df["monitor_hr_lag_estimate_s"].mean()),
        "monitor_lag_median_s": float(df["monitor_hr_lag_estimate_s"].median()),
        "monitor_lag_counts": {int(k): int(v) for k, v in df["monitor_hr_lag_estimate_s"].value_counts().items()},
        "cardiac_window_mae_zero_mean": float(df["radar_ecg_window_mae_zero"].mean()),
        "cardiac_surrogate_mae_mean": float(df["cardiac_surrogate_mae"].mean()),
        "radar_sync_status_counts": {str(k): int(v) for k, v in df["radar_to_ecg_sync_status"].value_counts().items()},
        "monitor_latency_status_counts": {str(k): int(v) for k, v in df["monitor_hr_latency_status"].value_counts().items()},
    }

    return df, summary_stats


def run_sync_validation(
    dataset_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    allow_phase2a_overwrite: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Execute complete synchronization validation with explicit output directory parameter.

    Defaulting to outputs/phase2a is blocked by D15 governance guard.
    """
    if output_dir is None:
        raise ValueError(
            "output_dir must be explicitly specified. Pass an explicit path under 'outputs/closure/'."
        )
    out_resolved = Path(output_dir).resolve()
    phase2a_resolved = Path("outputs/phase2a").resolve()
    if (out_resolved == phase2a_resolved or (out_resolved.name == "phase2a" and out_resolved.parent.name == "outputs")) and not allow_phase2a_overwrite:
        raise PermissionError(
            "Writing directly to immutable 'outputs/phase2a' is blocked by governance guard. Pass allow_phase2a_overwrite=True to override."
        )
    if dataset_dir is None:
        p1 = Path("../data/VITALSENSE_120_DATASET")
        p2 = Path("data/VITALSENSE_120_DATASET")
        dataset_dir = p1 if p1.exists() else p2
    return run_full_validation(
        dataset_dir=dataset_dir,
        output_dir=output_dir,
        allow_phase2a_overwrite=allow_phase2a_overwrite,
    )

