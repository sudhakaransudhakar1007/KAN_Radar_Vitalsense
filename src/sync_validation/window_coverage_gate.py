"""Window-level RR interval coverage gate for ECG reference validation.

Evaluates whether rolling 10-second ECG analysis windows have sufficient physiological
beat coverage to qualify as reliable ground truth for radar heart-rate estimation.
"""

from typing import Any, Dict, List, Optional
import numpy as np


def evaluate_window_rr_coverage(
    r_peaks: Dict[str, Any],
    total_duration_s: float = 120.0,
    win_sec: float = 10.0,
    hop_sec: float = 5.0,
    min_coverage: float = 0.80,
    strict_inequality: bool = True,
) -> List[Dict[str, Any]]:
    """Evaluate window-level RR interval coverage across rolling analysis windows.

    A rolling grid of windows across total_duration_s is constructed.
    For total_duration_s = 120.0, win_sec = 10.0, hop_sec = 5.0, this yields
    exactly 23 windows (offsets 0.0s, 5.0s, ..., 110.0s).

    Definition of Coverage:
    -----------------------
    For each window [w_start, w_end], consider every adjacent pair of valid R-peaks
    (r_i, r_{i+1}) with detection times (t_i, t_{i+1}). If the interval overlaps
    [w_start, w_end], the covered duration contributed by that interval is:
        overlap = max(0.0, min(t_{i+1}, w_end) - max(t_i, w_start))
    The window coverage fraction is:
        coverage_fraction = covered_duration_s / win_sec

    Physiological Plausibility:
    ---------------------------
    An interval is valid only if both R-peaks are finite/valid and the RR interval
    itself is physiologically plausible:
        0.30 s <= RR <= 2.00 s  (corresponding to 30 bpm to 200 bpm).
    Any interval outside this range (e.g. cardiac arrest, dropped beats, pause > 2s)
    is treated as a gap and contributes ZERO coverage.

    Gate Acceptance Rule:
    ---------------------
    A window is ACCEPTED if and only if:
        coverage_fraction > min_coverage  (when strict_inequality=True, default)
        coverage_fraction >= min_coverage (when strict_inequality=False)
    Any window with 0 beats inside [w_start, w_end] or containing an explicit NaN
    flag / NaN peak is REJECTED. Missing beats are never interpolated or imputed.

    Parameters
    ----------
    r_peaks : dict
        Dictionary containing detected R-peaks. Expected keys:
        - 'peak_times': 1D array-like of peak timestamps in seconds, OR
        - 'peaks': 1D array-like of peak sample indices (requires 'fs' in dict).
        Optional keys:
        - 'has_nan': bool flag indicating unhandled NaN in input.
        - 'status': status string (e.g. 'FAIL', 'INSUFFICIENT_PEAKS').
    total_duration_s : float
        Total duration of the recording in seconds (default: 120.0).
    win_sec : float
        Window duration in seconds (default: 10.0).
    hop_sec : float
        Hop / step size between successive windows in seconds (default: 5.0).
    min_coverage : float
        Minimum required RR coverage fraction (default: 0.80).
    strict_inequality : bool
        If True, requires coverage > min_coverage (strict inequality, default).
        If False, requires coverage >= min_coverage.

    Returns
    -------
    List[Dict[str, Any]]
        List of window evaluation dicts (length 23 for standard 120s/10s/5s grid),
        each containing:
        - 'window_idx': int (0-based)
        - 'start_s': float
        - 'end_s': float
        - 'beat_count': int (number of beats inside [start_s, end_s])
        - 'rr_interval_count': int (number of valid physiological RR intervals overlapping window)
        - 'covered_duration_s': float (total valid seconds covered)
        - 'coverage_fraction': float (covered_duration_s / win_sec)
        - 'status': 'ACCEPTED' or 'REJECTED'
        - 'rejection_reason': None if ACCEPTED, else descriptive string
    """
    if win_sec <= 0.0 or hop_sec <= 0.0:
        raise ValueError("win_sec and hop_sec must be positive.")
    if total_duration_s < win_sec:
        raise ValueError("total_duration_s must be >= win_sec.")

    # 1. Parse peak times
    global_nan_flag = False
    raw_peak_times = None

    if "peak_times" in r_peaks and r_peaks["peak_times"] is not None:
        raw_peak_times = np.asarray(r_peaks["peak_times"], dtype=float)
    elif "peaks" in r_peaks and r_peaks["peaks"] is not None:
        fs = float(r_peaks.get("fs", 2000.0))
        raw_peak_times = np.asarray(r_peaks["peaks"], dtype=float) / fs
    else:
        raw_peak_times = np.array([], dtype=float)

    if r_peaks.get("has_nan", False) or r_peaks.get("status") == "FAIL":
        global_nan_flag = True

    if np.isnan(raw_peak_times).any():
        global_nan_flag = True

    valid_peak_times = raw_peak_times[~np.isnan(raw_peak_times)] if len(raw_peak_times) > 0 else np.array([], dtype=float)
    valid_peak_times = np.sort(valid_peak_times)

    # 2. Identify valid physiological RR intervals
    # Plausible range: 0.30s <= RR <= 2.00s (30 - 200 bpm)
    MIN_PHYSIOLOGICAL_RR = 0.30
    MAX_PHYSIOLOGICAL_RR = 2.00

    valid_intervals: List[tuple[float, float]] = []
    if len(valid_peak_times) >= 2:
        for i in range(len(valid_peak_times) - 1):
            t1 = float(valid_peak_times[i])
            t2 = float(valid_peak_times[i + 1])
            rr = t2 - t1
            if MIN_PHYSIOLOGICAL_RR <= rr <= MAX_PHYSIOLOGICAL_RR:
                valid_intervals.append((t1, t2))

    # 3. Construct window grid
    n_windows = int(np.floor((total_duration_s - win_sec) / hop_sec)) + 1
    results: List[Dict[str, Any]] = []

    for w_idx in range(n_windows):
        w_start = float(w_idx * hop_sec)
        w_end = float(w_start + win_sec)

        # Count beats falling inside [w_start, w_end]
        # Check raw peaks for NaNs falling in this window range
        nan_in_window = False
        if global_nan_flag and len(raw_peak_times) > 0:
            nan_in_window = True

        beat_count = int(np.sum((valid_peak_times >= w_start) & (valid_peak_times <= w_end)))

        # Compute valid RR interval overlap
        covered_duration_s = 0.0
        rr_interval_count = 0

        for t1, t2 in valid_intervals:
            # Check overlap between [t1, t2] and [w_start, w_end]
            overlap = max(0.0, min(t2, w_end) - max(t1, w_start))
            if overlap > 0.0:
                covered_duration_s += overlap
                rr_interval_count += 1

        coverage_fraction = float(covered_duration_s / win_sec)

        # Evaluate acceptance rule
        # Rule: STRICT inequality (coverage > min_coverage) by default
        status = "REJECTED"
        rejection_reason: Optional[str] = None

        if nan_in_window:
            status = "REJECTED"
            rejection_reason = "NAN_IN_BEATS"
        elif beat_count == 0:
            status = "REJECTED"
            rejection_reason = "ZERO_BEATS"
        else:
            is_covered = (
                (coverage_fraction > min_coverage)
                if strict_inequality
                else (coverage_fraction >= min_coverage)
            )
            if is_covered:
                status = "ACCEPTED"
                rejection_reason = None
            else:
                status = "REJECTED"
                ineq_str = ">" if strict_inequality else ">="
                rejection_reason = (
                    f"INSUFFICIENT_RR_COVERAGE: {coverage_fraction:.4f} not {ineq_str} {min_coverage:.2f}"
                )

        results.append({
            "window_idx": w_idx,
            "start_s": w_start,
            "end_s": w_end,
            "beat_count": beat_count,
            "rr_interval_count": rr_interval_count,
            "covered_duration_s": round(covered_duration_s, 6),
            "coverage_fraction": round(coverage_fraction, 6),
            "status": status,
            "rejection_reason": rejection_reason,
        })

    return results
