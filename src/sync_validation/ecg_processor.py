"""ECG processing, R-peak detection, 1 Hz HR derivation, and monitor latency analysis."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import scipy.signal as signal


def clean_ecg_isolated_nans(
    ecg_raw: np.ndarray,
    max_gap: int = 1,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Linearly interpolate ONLY isolated single-sample delimiter NaNs in memory.

    Addresses ISS-13 / ISS-13b: Multi-sample gaps (length > max_gap) are NOT interpolated
    and are flagged with indices and counts logged, protecting QRS complexes from distortion.
    Original array is unmodified; operations execute strictly on an in-memory copy.

    Args:
        ecg_raw: Input ECG waveform.
        max_gap: Maximum contiguous NaN count eligible for interpolation (default 1).

    Returns:
        (ecg_clean, info_dict)
    """
    ecg = np.array(ecg_raw, copy=True, dtype=np.float64).flatten()
    nans = np.isnan(ecg)
    total_nans = int(np.sum(nans))

    if total_nans == 0:
        return ecg, {
            "total_nan_count": 0,
            "isolated_nan_count": 0,
            "isolated_indices": [],
            "multi_sample_gap_count": 0,
            "multi_sample_gap_indices": [],
            "uninterpolated_nan_count": 0,
            "has_multi_sample_gaps": False,
        }

    # Group contiguous NaNs into runs
    runs = []
    in_run = False
    start_idx = 0
    for i, is_nan in enumerate(nans):
        if is_nan and not in_run:
            in_run = True
            start_idx = i
        elif not is_nan and in_run:
            in_run = False
            runs.append((start_idx, i - start_idx))
    if in_run:
        runs.append((start_idx, len(nans) - start_idx))

    isolated_indices = []
    multi_sample_runs = []
    valid_indices = np.where(~nans)[0]

    if len(valid_indices) == 0:
        return ecg, {
            "total_nan_count": total_nans,
            "isolated_nan_count": 0,
            "isolated_indices": [],
            "multi_sample_gap_count": 1,
            "multi_sample_gap_indices": [list(range(len(ecg)))],
            "uninterpolated_nan_count": total_nans,
            "has_multi_sample_gaps": True,
        }

    for start, length in runs:
        if length <= max_gap:
            # Interpolate isolated single-sample NaN
            for idx in range(start, start + length):
                isolated_indices.append(idx)
                ecg[idx] = np.interp(idx, valid_indices, ecg[valid_indices])
        else:
            # Multi-sample gap: do NOT interpolate; flag it
            multi_sample_runs.append(list(range(start, start + length)))

    uninterpolated_count = sum(len(r) for r in multi_sample_runs)

    info = {
        "total_nan_count": total_nans,
        "isolated_nan_count": len(isolated_indices),
        "isolated_indices": isolated_indices,
        "multi_sample_gap_count": len(multi_sample_runs),
        "multi_sample_gap_indices": multi_sample_runs,
        "uninterpolated_nan_count": uninterpolated_count,
        "has_multi_sample_gaps": len(multi_sample_runs) > 0,
    }

    return ecg, info


def clean_ecg_nans(
    ecg_raw: np.ndarray,
    only_isolated: bool = True,
    fill_boundary: bool = True,
) -> Tuple[np.ndarray, int, List[int]]:
    """Clean isolated NaNs in an in-memory copy of ecg_lead2.

    If only_isolated=True (default per ISS-13b), only isolated single-sample NaNs
    are interpolated; multi-sample gaps are not interpolated.
    If fill_boundary=False, boundary delimiter NaNs at index 0 or -1 are restored to NaN.
    """
    if only_isolated:
        clean_arr, info = clean_ecg_isolated_nans(ecg_raw, max_gap=1)
        if not fill_boundary and len(ecg_raw) > 0:
            if np.isnan(ecg_raw[0]):
                clean_arr[0] = np.nan
            if np.isnan(ecg_raw[-1]):
                clean_arr[-1] = np.nan
        return clean_arr, info["total_nan_count"], info["isolated_indices"]

    ecg = np.array(ecg_raw, copy=True, dtype=np.float64).flatten()
    nans = np.isnan(ecg)
    nan_count = int(np.sum(nans))
    nan_indices = [int(i) for i in np.where(nans)[0]]

    if nan_count > 0:
        valid_indices = np.where(~nans)[0]
        if len(valid_indices) == 0:
            return ecg, nan_count, nan_indices
        ecg[nan_indices] = np.interp(nan_indices, valid_indices, ecg[valid_indices])
        if not fill_boundary and len(ecg_raw) > 0:
            if np.isnan(ecg_raw[0]):
                ecg[0] = np.nan
            if np.isnan(ecg_raw[-1]):
                ecg[-1] = np.nan

    return ecg, nan_count, nan_indices



def detect_r_peaks(
    ecg_clean: np.ndarray,
    fs: float = 500.0,
    min_bpm: float = 35.0,
    max_bpm: float = 175.0,
) -> Dict[str, Any]:
    """Detect ECG R-peaks using a Pan-Tompkins style bandpass and integration method.

    Pipeline:
      1. Butterworth bandpass filter (5-15 Hz, order 2) isolating QRS complex.
      2. First-difference derivative to emphasize QRS slope.
      3. Pointwise squaring to nonlinearly amplify high-frequency energy.
      4. Moving window average (150 ms = 75 samples at 500 Hz).
      5. Adaptive thresholding with minimum refractory period.
      6. Local peak refinement on filtered ECG.
      7. Physiological RR interval validation (0.34s to 1.71s).

    Args:
        ecg_clean: In-memory 1D ECG array with NaNs removed.
        fs: Sampling rate in Hz (default 500.0).
        min_bpm: Minimum physiological HR threshold.
        max_bpm: Maximum physiological HR threshold.

    Returns:
        Dictionary containing peak indices, timestamps, RR intervals, and QC metrics.
    """
    ecg = ecg_clean.flatten()
    n_samples = len(ecg)
    duration_s = n_samples / fs

    if n_samples < int(fs * 2.0):
        return {
            "status": "INSUFFICIENT_LENGTH",
            "peaks": np.array([], dtype=int),
            "peak_times": np.array([], dtype=float),
            "rr_intervals": np.array([], dtype=float),
            "valid_rr_mask": np.array([], dtype=bool),
            "inst_hr": np.array([], dtype=float),
            "valid_peak_count": 0,
            "mean_rr_s": np.nan,
            "std_rr_s": np.nan,
            "rmssd_ms": np.nan,
            "mean_hr_bpm": np.nan,
            "qc_verdict": "FAIL",
            "notes": "ECG length shorter than 2 seconds",
        }

    # 1. Bandpass filter 5 - 15 Hz
    nyq = 0.5 * fs
    low = 5.0 / nyq
    high = 15.0 / nyq
    b, a = signal.butter(2, [low, high], btype="bandpass")
    ecg_filt = signal.filtfilt(b, a, ecg)

    # 2. Derivative
    diff = np.diff(ecg_filt, prepend=ecg_filt[0])

    # 3. Squaring
    squared = diff ** 2

    # 4. Moving window average integration (~150 ms)
    win_len = max(3, int(0.15 * fs))
    kernel = np.ones(win_len) / win_len
    mwa = signal.convolve(squared, kernel, mode="same")

    # 5. Peak picking with adaptive threshold
    # Min distance corresponding to max_bpm
    min_distance = int((60.0 / max_bpm) * fs)
    threshold = 0.3 * np.percentile(mwa, 90)

    cand_peaks, _ = signal.find_peaks(mwa, distance=min_distance, height=threshold)

    # 6. Refine to local peak on filtered ECG
    refined = []
    search_radius = int(0.08 * fs)  # 80 ms
    for p in cand_peaks:
        start = max(0, p - search_radius)
        end = min(n_samples, p + search_radius)
        if end > start:
            refined.append(start + np.argmax(np.abs(ecg_filt[start:end])))

    peaks = np.unique(refined) if len(refined) > 0 else np.array([], dtype=int)

    if len(peaks) < 3:
        return {
            "status": "INSUFFICIENT_PEAKS",
            "peaks": peaks,
            "peak_times": peaks / fs,
            "rr_intervals": np.array([], dtype=float),
            "valid_rr_mask": np.array([], dtype=bool),
            "inst_hr": np.array([], dtype=float),
            "valid_peak_count": len(peaks),
            "mean_rr_s": np.nan,
            "std_rr_s": np.nan,
            "rmssd_ms": np.nan,
            "mean_hr_bpm": np.nan,
            "qc_verdict": "FAIL",
            "notes": f"Only {len(peaks)} R-peaks detected across {duration_s:.1f}s",
        }

    # 7. Physiological RR interval validation
    peak_times = peaks / fs
    rr_intervals = np.diff(peak_times)

    min_rr = 60.0 / max_bpm
    max_rr = 60.0 / min_bpm
    valid_rr_mask = (rr_intervals >= min_rr) & (rr_intervals <= max_rr)

    valid_rr = rr_intervals[valid_rr_mask]
    if len(valid_rr) < 5:
        qc_verdict = "WARNING_FEW_VALID_BEATS"
    else:
        qc_verdict = "PASS"

    mean_rr = float(np.mean(valid_rr)) if len(valid_rr) > 0 else np.nan
    std_rr = float(np.std(valid_rr)) if len(valid_rr) > 1 else np.nan
    rmssd = float(np.sqrt(np.mean(np.diff(valid_rr) ** 2)) * 1000.0) if len(valid_rr) > 2 else np.nan
    inst_hr = 60.0 / rr_intervals
    mean_hr = float(60.0 / mean_rr) if mean_rr > 0 else np.nan

    r_peaks_payload = {
        "peaks": peaks,
        "peak_times": peak_times,
        "rr_intervals": rr_intervals,
        "valid_rr_mask": valid_rr_mask,
    }
    sqi = compute_ecg_sqi(r_peaks_payload, duration_s=duration_s)

    return {
        "status": "SUCCESS",
        "peaks": peaks,
        "peak_times": peak_times,
        "rr_intervals": rr_intervals,
        "valid_rr_mask": valid_rr_mask,
        "inst_hr": inst_hr,
        "valid_peak_count": len(peaks),
        "mean_rr_s": mean_rr,
        "std_rr_s": std_rr,
        "rmssd_ms": rmssd,
        "mean_hr_bpm": mean_hr,
        "qc_verdict": qc_verdict,
        "sqi_verdict": sqi["sqi_verdict"],
        "sqi_coverage": sqi["beat_coverage_ratio"],
        "sqi_max_gap_s": sqi["max_rr_gap_s"],
        "sqi_result": sqi,
        "notes": f"Detected {len(peaks)} peaks; {np.sum(valid_rr_mask)}/{len(rr_intervals)} valid RR intervals; SQI={sqi['sqi_verdict']}",
    }


def compute_ecg_sqi(
    r_peak_result: Dict[str, Any],
    duration_s: float = 120.0,
    coverage_threshold: float = 0.85,
    max_gap_threshold_s: float = 3.0,
) -> Dict[str, Any]:
    """Compute multi-parameter ECG Signal Quality Index (SQI) per ISS-08.

    Coverage Definition:
      - Denominator: Total recording duration in seconds (duration_s, typically 120.0s).
      - Numerator: Sum of durations of valid physiological RR intervals (sum(valid_rr)).
      - Invalid/rejected RR intervals contribute 0.0 seconds to the coverage numerator.
      - Requirement: beat_coverage > 0.85 (85%).

    Max Gap Definition:
      - Evaluates the maximum time elapsed between consecutive valid R-peaks across the recording.
      - Also checks lead-in from t=0s to first valid peak, and lead-out from last valid peak to duration_s.
      - Requirement: max_rr_gap < 3.0s.

    Amplitude Stability:
      - Marked UNSPECIFIED / NOT VALIDATED (no clinically validated threshold approved).
      - Because this parameter remains unvalidated, a recording-level PASS cannot be granted.

    Verdict:
      - 'SQI_FAIL': If coverage <= 0.85 or max_rr_gap >= 3.0s.
      - 'SQI_PARTIAL': If coverage > 0.85 and max_rr_gap < 3.0s, pending amplitude stability validation.
      - 'PASS': Prohibited (cannot be granted per gate rules).
    """
    peaks = r_peak_result.get("peaks", np.array([]))
    peak_times = r_peak_result.get("peak_times", np.array([]))
    rr_intervals = r_peak_result.get("rr_intervals", np.array([]))
    valid_mask = r_peak_result.get("valid_rr_mask", np.array([]))

    if len(peaks) < 2 or len(rr_intervals) == 0 or len(valid_mask) == 0:
        return {
            "sqi_verdict": "SQI_FAIL",
            "recording_level_pass": False,
            "beat_coverage_ratio": 0.0,
            "beat_coverage_s": 0.0,
            "total_duration_s": duration_s,
            "coverage_threshold": coverage_threshold,
            "max_rr_gap_s": duration_s,
            "max_gap_threshold_s": max_gap_threshold_s,
            "amplitude_stability_status": "UNSPECIFIED / NOT VALIDATED",
            "valid_beat_count": 0,
            "total_beat_count": len(peaks),
            "reason": "Insufficient detectable R-peaks (< 2)",
        }

    valid_rr = rr_intervals[valid_mask]
    valid_coverage_s = float(np.sum(valid_rr))
    coverage_ratio = float(valid_coverage_s / duration_s) if duration_s > 0 else 0.0

    valid_indices = np.where(valid_mask)[0]
    if len(valid_indices) == 0:
        max_gap_s = duration_s
    else:
        valid_peak_idx = np.unique(np.concatenate([valid_indices, valid_indices + 1]))
        valid_peak_times = peak_times[valid_peak_idx]
        gaps = np.diff(valid_peak_times) if len(valid_peak_times) > 1 else np.array([duration_s])
        start_gap = valid_peak_times[0] if len(valid_peak_times) > 0 else duration_s
        end_gap = duration_s - valid_peak_times[-1] if len(valid_peak_times) > 0 else duration_s
        all_gaps = np.concatenate([[start_gap], gaps, [end_gap]])
        max_gap_s = float(np.max(all_gaps))

    coverage_pass = coverage_ratio > coverage_threshold
    gap_pass = max_gap_s < max_gap_threshold_s

    if not coverage_pass or not gap_pass:
        sqi_verdict = "SQI_FAIL"
        reason = f"Coverage {coverage_ratio*100:.1f}% (need >85%) or max gap {max_gap_s:.2f}s (need <3.0s)"
    else:
        sqi_verdict = "SQI_PARTIAL"
        reason = (
            f"Coverage ({coverage_ratio*100:.1f}%) and max gap ({max_gap_s:.2f}s) pass; "
            "amplitude stability UNSPECIFIED / NOT VALIDATED; recording-level PASS cannot be granted"
        )

    return {
        "sqi_verdict": sqi_verdict,
        "recording_level_pass": False,
        "beat_coverage_ratio": round(coverage_ratio, 4),
        "beat_coverage_s": round(valid_coverage_s, 2),
        "total_duration_s": duration_s,
        "coverage_threshold": coverage_threshold,
        "max_rr_gap_s": round(max_gap_s, 4),
        "max_gap_threshold_s": max_gap_threshold_s,
        "amplitude_stability_status": "UNSPECIFIED / NOT VALIDATED",
        "valid_beat_count": int(np.sum(valid_mask)),
        "total_beat_count": len(peaks),
        "reason": reason,
    }



def derive_1hz_ecg_hr(
    r_peak_result: Dict[str, Any],
    total_seconds: int = 120,
) -> Tuple[np.ndarray, np.ndarray, str]:
    """Derive continuous 1 Hz ECG-based HR series from validated R-peaks.

    Mapping convention:
      - R-peaks define instantaneous heart rates HR_i = 60 / RR_i at beat time t_beat.
      - Piecewise linear interpolation evaluates continuous instantaneous HR
        at exact integer second timestamps t = 0, 1, 2, ..., total_seconds - 1.
      - At boundaries before first beat or after last beat, edge values are held constant.

    Args:
        r_peak_result: Result dictionary from detect_r_peaks.
        total_seconds: Total duration in seconds (default 120).

    Returns:
        (t_grid, hr_1hz, convention_description)
    """
    t_grid = np.arange(total_seconds, dtype=float)
    peaks = r_peak_result.get("peaks", np.array([]))
    peak_times = r_peak_result.get("peak_times", np.array([]))
    rr_intervals = r_peak_result.get("rr_intervals", np.array([]))
    valid_mask = r_peak_result.get("valid_rr_mask", np.array([]))

    if len(peaks) < 3 or np.sum(valid_mask) < 3:
        # Fallback to NaN array if insufficient peaks
        hr_1hz = np.full(total_seconds, np.nan, dtype=float)
        return t_grid, hr_1hz, "INSUFFICIENT_PEAKS_FOR_1HZ_MAPPING"

    beat_times = peak_times[1:][valid_mask]
    inst_hr = (60.0 / rr_intervals)[valid_mask]

    hr_1hz = np.interp(t_grid, beat_times, inst_hr)
    convention = "Piecewise linear interpolation of 60/RR at beat times onto integer second grid t in [0, 119]s"
    return t_grid, hr_1hz, convention


def scan_monitor_hr_lag(
    hr_ecg_1hz: np.ndarray,
    hr_monitor: np.ndarray,
    max_lag_s: int = 10,
) -> Dict[str, Any]:
    """Scan relative lag between ECG-derived 1 Hz HR and monitor HR array.

    Sign convention:
      Positive lag (tau > 0) means the monitor series appears later than the
      ECG-derived series (i.e., monitor HR updates with latency tau: mon[t] ~ ecg[t - tau]).
      Negative lag (tau < 0) means monitor series appears earlier.

    Overlapping comparison:
      For tau >= 0:
        mon_slice = hr_monitor[tau : 120]
        ecg_slice = hr_ecg_1hz[0 : 120 - tau]
      For tau < 0:
        mon_slice = hr_monitor[0 : 120 + tau]
        ecg_slice = hr_ecg_1hz[-tau : 120]

    Args:
        hr_ecg_1hz: 1 Hz ECG-derived HR array of length 120.
        hr_monitor: 120-element monitor HR array.
        max_lag_s: Maximum lag in seconds to scan (+/- max_lag_s).

    Returns:
        Dictionary with lag scan profile, best MAE shift, best corr shift, zero-shift comparison, and ambiguity.
    """
    ecg_hr = np.array(hr_ecg_1hz, dtype=float).flatten()
    mon_hr = np.array(hr_monitor, dtype=float).flatten()

    if len(ecg_hr) != 120 or len(mon_hr) != 120 or np.any(np.isnan(ecg_hr)):
        return {
            "status": "INSUFFICIENT_DATA",
            "best_lag_s": np.nan,
            "best_mae_bpm": np.nan,
            "best_corr": np.nan,
            "zero_lag_mae_bpm": np.nan,
            "zero_lag_corr": np.nan,
            "mae_improvement_bpm": np.nan,
            "is_ambiguous": True,
            "lag_profile": [],
            "notes": "Invalid or incomplete HR series",
        }

    lag_profile = []
    for tau in range(-max_lag_s, max_lag_s + 1):
        if tau >= 0:
            sub_mon = mon_hr[tau:120]
            sub_ecg = ecg_hr[0:120 - tau]
        else:
            sub_mon = mon_hr[0:120 + tau]
            sub_ecg = ecg_hr[-tau:120]

        n_samples = len(sub_mon)
        mae = float(np.mean(np.abs(sub_mon - sub_ecg)))
        if np.std(sub_mon) > 1e-4 and np.std(sub_ecg) > 1e-4:
            corr = float(np.corrcoef(sub_mon, sub_ecg)[0, 1])
        else:
            corr = 0.0

        lag_profile.append({
            "lag_s": tau,
            "mae_bpm": round(mae, 4),
            "corr": round(corr, 4),
            "valid_samples": n_samples,
        })

    # Find best shift by minimum MAE
    best_mae_entry = min(lag_profile, key=lambda x: x["mae_bpm"])
    # Find best shift by maximum correlation
    best_corr_entry = max(lag_profile, key=lambda x: x["corr"])
    zero_entry = [p for p in lag_profile if p["lag_s"] == 0][0]

    best_lag = best_mae_entry["lag_s"]
    best_mae = best_mae_entry["mae_bpm"]
    best_corr = best_mae_entry["corr"]
    zero_mae = zero_entry["mae_bpm"]
    zero_corr = zero_entry["corr"]
    mae_improvement = round(zero_mae - best_mae, 4)

    # Ambiguity check: check if MAE variation across entire scan is small (< 0.25 bpm)
    mae_range = max(p["mae_bpm"] for p in lag_profile) - min(p["mae_bpm"] for p in lag_profile)
    is_ambiguous = bool(mae_range < 0.25)

    return {
        "status": "SUCCESS",
        "best_lag_s": best_lag,
        "best_mae_bpm": best_mae,
        "best_corr": best_corr,
        "best_corr_lag_s": best_corr_entry["lag_s"],
        "max_corr": best_corr_entry["corr"],
        "zero_lag_mae_bpm": zero_mae,
        "zero_lag_corr": zero_corr,
        "mae_improvement_bpm": mae_improvement,
        "is_ambiguous": is_ambiguous,
        "mae_range_bpm": round(mae_range, 4),
        "lag_profile": lag_profile,
        "notes": f"Best MAE at lag {best_lag:+d}s (MAE {best_mae:.2f} vs zero {zero_mae:.2f} bpm; Corr {best_corr:+.2f})",
    }
