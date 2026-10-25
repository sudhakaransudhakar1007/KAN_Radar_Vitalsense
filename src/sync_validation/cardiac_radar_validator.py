"""Radar-to-ECG cardiac timing investigation and window-level HR agreement."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import scipy.signal as signal


def extract_radar_cardiac_signal(
    vitalsig: np.ndarray,
    rad_fs: float = 333.3333333333333,
    low_hz: float = 0.8,
    high_hz: float = 3.0,
    order: int = 3,
) -> np.ndarray:
    """Extract cardiac micro-motion band from radar chest displacement.

    Bandpass: 0.8 Hz (48 bpm) to 3.0 Hz (180 bpm).
    Zero-phase filtering preserves event timing without phase distortion.
    """
    sig = np.array(vitalsig, copy=True, dtype=np.float64).flatten()
    if np.any(np.isnan(sig)):
        v_idx = np.where(~np.isnan(sig))[0]
        n_idx = np.where(np.isnan(sig))[0]
        sig[n_idx] = np.interp(n_idx, v_idx, sig[v_idx])

    nyq = 0.5 * rad_fs
    b, a = signal.butter(order, [low_hz / nyq, high_hz / nyq], btype="bandpass")
    return signal.filtfilt(b, a, sig)


def estimate_peak_frequency_parabolic(
    mags: np.ndarray,
    freqs: np.ndarray,
    mask: np.ndarray,
) -> float:
    """3-point parabolic peak interpolation on frequency spectrum.

    Addresses ISS-09: Refines discrete peak frequency by fitting a parabola
    through the peak bin and its two adjacent neighbors:
        delta = (A_{k+1} - A_{k-1}) / (2 * (2*A_k - A_{k-1} - A_{k+1}))
    reducing discretization error well below the native 6.0 bpm bin width.
    """
    sub_mags = mags[mask]
    sub_freqs = freqs[mask]
    if len(sub_mags) < 3:
        return float(sub_freqs[np.argmax(sub_mags)]) if len(sub_mags) > 0 else 0.0

    k = int(np.argmax(sub_mags))
    if k == 0 or k == len(sub_mags) - 1:
        return float(sub_freqs[k])

    a_left = float(sub_mags[k - 1])
    a_mid = float(sub_mags[k])
    a_right = float(sub_mags[k + 1])

    denom = 2.0 * (2.0 * a_mid - a_left - a_right)
    if abs(denom) < 1e-12:
        return float(sub_freqs[k])

    delta = (a_right - a_left) / denom
    delta = max(-0.5, min(0.5, delta))

    df = sub_freqs[1] - sub_freqs[0] if len(sub_freqs) > 1 else 0.0
    return float(sub_freqs[k] + delta * df)


def estimate_window_hr_multi_estimator(
    w: np.ndarray,
    rad_fs: float,
    band: Tuple[float, float] = (0.8, 3.0),
) -> Dict[str, float]:
    """Estimate cardiac HR across multiple frequency-domain estimators per ISS-09.

    Estimators:
      1. 'unpadded_bin': Original unpadded FFT with discrete argmax bin selection.
      2. 'parabolic': 3-point parabolic peak interpolation on unpadded FFT.
      3. 'zeropad_4x': Exactly 4x zero-padding (N_fft = 4 * len(w)), providing spectral
         interpolation (evaluation on a 4x finer frequency grid) with NO change in native resolution.
      4. 'zeropad_4x_parabolic': Combined 4x zero-padding plus 3-point parabolic peak interpolation.
    """
    n_win = len(w)
    w_win = w * np.hamming(n_win)

    # 1. Unpadded FFT
    w_fft = np.fft.rfft(w_win)
    freqs = np.fft.rfftfreq(n_win, d=1.0 / rad_fs)
    mags = np.abs(w_fft)
    mask = (freqs >= band[0]) & (freqs <= band[1])

    discrete_f = freqs[mask][np.argmax(mags[mask])] if np.any(mask) else np.nan
    parabolic_f = estimate_peak_frequency_parabolic(mags, freqs, mask) if np.any(mask) else np.nan

    # 2. 4x Zero-padded FFT (exactly 4x window length: N_pad = 4 * n_win)
    n_pad = 4 * n_win
    w_fft_4x = np.fft.rfft(w_win, n=n_pad)
    freqs_4x = np.fft.rfftfreq(n_pad, d=1.0 / rad_fs)
    mags_4x = np.abs(w_fft_4x)
    mask_4x = (freqs_4x >= band[0]) & (freqs_4x <= band[1])

    zeropad_f = freqs_4x[mask_4x][np.argmax(mags_4x[mask_4x])] if np.any(mask_4x) else np.nan
    zeropad_parabolic_f = estimate_peak_frequency_parabolic(mags_4x, freqs_4x, mask_4x) if np.any(mask_4x) else np.nan

    return {
        "unpadded_bin_bpm": float(discrete_f * 60.0) if np.isfinite(discrete_f) else np.nan,
        "parabolic_bpm": float(parabolic_f * 60.0) if np.isfinite(parabolic_f) else np.nan,
        "zeropad_4x_bpm": float(zeropad_f * 60.0) if np.isfinite(zeropad_f) else np.nan,
        "zeropad_4x_parabolic_bpm": float(zeropad_parabolic_f * 60.0) if np.isfinite(zeropad_parabolic_f) else np.nan,
    }


def compute_window_level_hr_agreement(
    vitalsig: np.ndarray,
    rad_fs: float,
    r_peak_result: Dict[str, Any],
    win_sec: float = 10.0,
    hop_sec: float = 5.0,
    trial_shifts_s: Optional[List[float]] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Evaluate window-level HR agreement between radar cardiac signal and ECG ground truth.

    Addresses ISS-09 & ISS-10:
      - Primary metric: Zero-shift agreement (tau = 0.0s).
      - Diagnostic exploratory metric: Best trial shift evaluated in [-5, +5]s.
      - Extra estimators: Parabolic peak interpolation and exactly 4x zero-padding.
    """
    if trial_shifts_s is None:
        trial_shifts_s = [-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0]

    peaks = r_peak_result.get("peaks", np.array([]))
    peak_times = r_peak_result.get("peak_times", np.array([]))
    rr_intervals = r_peak_result.get("rr_intervals", np.array([]))
    valid_mask = r_peak_result.get("valid_rr_mask", np.array([]))

    if len(peaks) < 3 or np.sum(valid_mask) < 3:
        return {
            "status": "INSUFFICIENT_ECG",
            "zero_shift_mae_bpm": np.nan,
            "zero_shift_corr": np.nan,
            "best_shift_s": np.nan,
            "best_shift_mae_bpm": np.nan,
            "polarity_inverted_mae_bpm": np.nan,
            "shift_profile": [],
            "notes": "Insufficient valid ECG beats",
        }

    beat_times = peak_times[1:][valid_mask]
    inst_hr = (60.0 / rr_intervals)[valid_mask]

    cardiac_sig = extract_radar_cardiac_signal(vitalsig, rad_fs)
    total_dur_s = len(vitalsig) / rad_fs
    n_win = int((total_dur_s - win_sec) / hop_sec) + 1

    # Extract baseline radar HRs at tau = 0 across all estimators
    rad_hrs_zero = []
    rad_hrs_parabolic = []
    rad_hrs_4x = []
    rad_hrs_4x_para = []
    ecg_hrs_zero = []

    for i in range(n_win):
        t_s = i * hop_sec
        t_e = t_s + win_sec
        idx_s = int(t_s * rad_fs)
        idx_e = int(t_e * rad_fs)
        w = cardiac_sig[idx_s:idx_e]

        # Multi-estimator HR evaluation
        est = estimate_window_hr_multi_estimator(w, rad_fs)
        rad_hrs_zero.append(est["unpadded_bin_bpm"])
        rad_hrs_parabolic.append(est["parabolic_bpm"])
        rad_hrs_4x.append(est["zeropad_4x_bpm"])
        rad_hrs_4x_para.append(est["zeropad_4x_parabolic_bpm"])

        # ECG window average
        in_win = (beat_times >= t_s) & (beat_times < t_e)
        if np.sum(in_win) > 0:
            ecg_hrs_zero.append(float(np.mean(inst_hr[in_win])))
        else:
            ecg_hrs_zero.append(np.nan)

    rad_arr = np.array(rad_hrs_zero)
    rad_arr_para = np.array(rad_hrs_parabolic)
    rad_arr_4x = np.array(rad_hrs_4x)
    rad_arr_4x_para = np.array(rad_hrs_4x_para)
    ecg_arr = np.array(ecg_hrs_zero)
    valid = ~np.isnan(ecg_arr)

    zero_mae = float(np.mean(np.abs(rad_arr[valid] - ecg_arr[valid])))
    zero_corr = float(np.corrcoef(rad_arr[valid], ecg_arr[valid])[0, 1]) if len(rad_arr[valid]) > 1 else 0.0

    zero_mae_para = float(np.mean(np.abs(rad_arr_para[valid] - ecg_arr[valid]))) if np.sum(valid) > 0 else np.nan
    zero_mae_4x = float(np.mean(np.abs(rad_arr_4x[valid] - ecg_arr[valid]))) if np.sum(valid) > 0 else np.nan
    zero_mae_4x_para = float(np.mean(np.abs(rad_arr_4x_para[valid] - ecg_arr[valid]))) if np.sum(valid) > 0 else np.nan

    # Scan trial shifts on radar window timing
    shift_profile = []
    for tau in trial_shifts_s:

        rad_hrs_tau = []
        ecg_hrs_tau = []
        for i in range(n_win):
            t_s = i * hop_sec
            t_e = t_s + win_sec
            t_rad_s = t_s + tau
            t_rad_e = t_e + tau

            if t_rad_s < 0 or t_rad_e > total_dur_s:
                continue

            idx_s = int(t_rad_s * rad_fs)
            idx_e = int(t_rad_e * rad_fs)
            w = cardiac_sig[idx_s:idx_e]

            w_fft = np.fft.rfft(w * np.hamming(len(w)))
            freqs = np.fft.rfftfreq(len(w), d=1.0 / rad_fs)
            mask = (freqs >= 0.8) & (freqs <= 3.0)
            peak_f = freqs[mask][np.argmax(np.abs(w_fft[mask]))]
            rad_hrs_tau.append(float(peak_f * 60.0))

            in_win = (beat_times >= t_s) & (beat_times < t_e)
            if np.sum(in_win) > 0:
                ecg_hrs_tau.append(float(np.mean(inst_hr[in_win])))
            else:
                ecg_hrs_tau.append(np.nan)

        rad_tau_arr = np.array(rad_hrs_tau)
        ecg_tau_arr = np.array(ecg_hrs_tau)
        v_tau = ~np.isnan(ecg_tau_arr)
        if np.sum(v_tau) > 5:
            mae_tau = float(np.mean(np.abs(rad_tau_arr[v_tau] - ecg_tau_arr[v_tau])))
            corr_tau = float(np.corrcoef(rad_tau_arr[v_tau], ecg_tau_arr[v_tau])[0, 1])
        else:
            mae_tau = np.nan
            corr_tau = np.nan

        shift_profile.append({
            "shift_s": tau,
            "mae_bpm": round(mae_tau, 4) if np.isfinite(mae_tau) else np.nan,
            "corr": round(corr_tau, 4) if np.isfinite(corr_tau) else np.nan,
            "valid_windows": int(np.sum(v_tau)),
        })

    valid_shifts = [p for p in shift_profile if np.isfinite(p["mae_bpm"])]
    best_shift_entry = min(valid_shifts, key=lambda x: x["mae_bpm"]) if valid_shifts else None

    # Polarity inverted test (-vitalsig)
    # FFT magnitude is invariant to sign inversion, but let's verify
    inv_cardiac = -cardiac_sig
    inv_rad_hrs = []
    for i in range(n_win):
        t_s = i * hop_sec
        t_e = t_s + win_sec
        idx_s = int(t_s * rad_fs)
        idx_e = int(t_e * rad_fs)
        w = inv_cardiac[idx_s:idx_e]
        w_fft = np.fft.rfft(w * np.hamming(len(w)))
        freqs = np.fft.rfftfreq(len(w), d=1.0 / rad_fs)
        mask = (freqs >= 0.8) & (freqs <= 3.0)
        peak_f = freqs[mask][np.argmax(np.abs(w_fft[mask]))]
        inv_rad_hrs.append(float(peak_f * 60.0))
    inv_arr = np.array(inv_rad_hrs)
    inv_mae = float(np.mean(np.abs(inv_arr[valid] - ecg_arr[valid])))

    # Surrogate shuffled control
    rng = np.random.default_rng(seed)
    shuffled_ecg = rng.permutation(ecg_arr[valid])
    surr_mae = float(np.mean(np.abs(rad_arr[valid] - shuffled_ecg)))

    return {
        "status": "SUCCESS",
        "primary_metric": "zero_shift",
        "zero_shift_mae_bpm": round(zero_mae, 4),
        "zero_shift_corr": round(zero_corr, 4),
        "zero_shift_mae_parabolic_bpm": round(zero_mae_para, 4) if np.isfinite(zero_mae_para) else np.nan,
        "zero_shift_mae_4x_zeropad_bpm": round(zero_mae_4x, 4) if np.isfinite(zero_mae_4x) else np.nan,
        "zero_shift_mae_4x_parabolic_bpm": round(zero_mae_4x_para, 4) if np.isfinite(zero_mae_4x_para) else np.nan,
        "estimators_mae_comparison": {
            "unpadded_bin_mae_bpm": round(zero_mae, 4),
            "parabolic_mae_bpm": round(zero_mae_para, 4) if np.isfinite(zero_mae_para) else np.nan,
            "zeropad_4x_mae_bpm": round(zero_mae_4x, 4) if np.isfinite(zero_mae_4x) else np.nan,
            "zeropad_4x_parabolic_mae_bpm": round(zero_mae_4x_para, 4) if np.isfinite(zero_mae_4x_para) else np.nan,
        },
        "best_shift_role": "diagnostic_exploratory_only",
        "best_shift_s": best_shift_entry["shift_s"] if best_shift_entry else 0.0,
        "best_shift_mae_bpm": best_shift_entry["mae_bpm"] if best_shift_entry else zero_mae,
        "polarity_inverted_mae_bpm": round(inv_mae, 4),
        "surrogate_control_mae_bpm": round(surr_mae, 4),
        "surrogate_seed": seed,
        "shift_profile": shift_profile,
        "notes": (
            f"Zero shift MAE (primary): {zero_mae:.2f} bpm (parabolic: {zero_mae_para:.2f}, "
            f"4x zeropad: {zero_mae_4x:.2f}); Diagnostic best shift: {best_shift_entry['shift_s'] if best_shift_entry else 0.0:+.1f}s"
        ),
    }


def synthetic_known_offset_test(
    duration_s: float = 60.0,
    fs: float = 333.3333333333333,
    true_offset_s: float = 0.050,  # 50 ms known shift
) -> Dict[str, Any]:
    """Test known-offset recovery using synthetic test signal with known artificial lag."""
    t = np.arange(int(duration_s * fs)) / fs
    # Synthesize multi-harmonic heartbeat + respiration signal
    sig1 = np.sin(2 * np.pi * 0.25 * t) + 0.3 * np.sin(2 * np.pi * 1.2 * t)

    # Shift sig2 by true_offset_s
    offset_samples = int(true_offset_s * fs)
    sig2 = np.roll(sig1, offset_samples)

    # Cross-correlate
    c = signal.correlate(sig2, sig1, mode="full")
    lags = signal.correlation_lags(len(sig2), len(sig1), mode="full")
    peak_lag_samples = lags[np.argmax(c)]
    est_offset_s = peak_lag_samples / fs
    error_s = abs(est_offset_s - true_offset_s)

    return {
        "true_offset_s": true_offset_s,
        "estimated_offset_s": est_offset_s,
        "error_s": error_s,
        "passed": bool(error_s < (1.0 / fs)),
    }
