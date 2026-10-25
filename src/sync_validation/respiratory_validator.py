"""Respiratory cross-correlation validation module reproducing author TechValidation.m."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import scipy.signal as signal


def resample_signals_to_2000hz(
    vitalsig: np.ndarray,
    rad_fs: float = 333.3333333333333,
    respiration: np.ndarray = None,
    ref_fs: float = 256.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Resample radar VitalSig and Mindray respiration in-memory to 2000 Hz.

    Replicates the exact sample-rate conversion from TechValidation.m:
      - Radar: 333.3333 Hz -> 2000 Hz (ratio 6 : 1)
      - Respiration: 256.0 Hz -> 2000 Hz (ratio 125 : 16)

    Signals are truncated to their minimum common length.
    Source arrays are NOT modified and resampled arrays are NOT saved to disk.
    """
    v_raw = np.array(vitalsig, copy=True, dtype=np.float64).flatten()
    r_raw = np.array(respiration, copy=True, dtype=np.float64).flatten()

    # Clean isolated NaNs if present
    if np.any(np.isnan(v_raw)):
        v_idx = np.where(~np.isnan(v_raw))[0]
        n_idx = np.where(np.isnan(v_raw))[0]
        v_raw[n_idx] = np.interp(n_idx, v_idx, v_raw[v_idx])

    if np.any(np.isnan(r_raw)):
        v_idx = np.where(~np.isnan(r_raw))[0]
        n_idx = np.where(np.isnan(r_raw))[0]
        r_raw[n_idx] = np.interp(n_idx, v_idx, r_raw[v_idx])

    # Polyphase rational resampling
    # 2000 / (1000/3) = 6
    v_2000 = signal.resample_poly(v_raw, 6, 1)

    # 2000 / 256 = 125 / 16
    ref_fs_int = int(round(ref_fs))
    if ref_fs_int == 256:
        r_2000 = signal.resample_poly(r_raw, 125, 16)
    else:
        # Fallback for arbitrary fs
        r_2000 = signal.resample_poly(r_raw, 2000, ref_fs_int)

    min_len = min(len(v_2000), len(r_2000))
    return v_2000[:min_len], r_2000[:min_len]


def truncate_respiration_dynamic_length_in_memory(
    vitalsig: np.ndarray,
    rad_fs: float,
    respiration: np.ndarray,
    ref_fs: float,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Dynamically evaluate raw array durations and truncate mismatched respiration in memory.

    Addresses ISS-12: When recordings have mismatched sample counts (e.g. VS24_Resting with
    30,600 samples ~119.53s vs standard 30,720 samples 120.0s), dynamically query array lengths
    and truncate trailing tail to the common minimum duration strictly in memory.
    The source files and arrays remain completely unmodified on disk.

    Returns:
        (vitalsig_common, respiration_common, info_dict)
    """
    v = np.array(vitalsig, copy=True, dtype=np.float64).flatten()
    r = np.array(respiration, copy=True, dtype=np.float64).flatten()

    dur_v = len(v) / rad_fs
    dur_r = len(r) / ref_fs
    common_dur_s = min(dur_v, dur_r)

    n_v = min(len(v), int(np.floor(common_dur_s * rad_fs)))
    n_r = min(len(r), int(np.floor(common_dur_s * ref_fs)))

    info = {
        "original_vitalsig_samples": len(v),
        "original_respiration_samples": len(r),
        "vitalsig_duration_s": dur_v,
        "respiration_duration_s": dur_r,
        "common_duration_s": common_dur_s,
        "truncated_vitalsig_samples": n_v,
        "truncated_respiration_samples": n_r,
        "respiration_samples_excluded": len(r) - n_r,
        "has_length_mismatch": abs(dur_v - dur_r) > 1e-4,
    }

    return v[:n_v], r[:n_r], info


def compute_respiratory_xcorr(
    vitsig_2000: np.ndarray,
    resp_2000: np.ndarray,
    max_lag_sec: float = 30.0,
) -> Dict[str, Any]:
    """Compute cross-correlation and time lag reproducing TechValidation.m.

    Sign and Lag Convention:
      Cross-correlation c = correlate(resp, vitsig, mode='full').
      lags = correlation_lags(len(resp), len(vitsig)).
      Peak lag in seconds = lag_samples * 0.5e-3 (since fs = 2000 Hz, dt = 0.5 ms).
      Peak lag in milliseconds = lag_seconds * 1000.
      A positive lag (lag > 0) means the reference respiration leads radar displacement,
      or radar displacement appears delayed by lag.

    Polarity Analysis:
      - Positive peak: argmax(c)
      - Absolute peak: argmax(|c|). If sign is negative, chest expansion corresponds
        to decreasing radar displacement (distance towards radar decreases).

    Args:
        vitsig_2000: Resampled radar VitalSig at 2000 Hz.
        resp_2000: Resampled Mindray respiration at 2000 Hz.
        max_lag_sec: Search window limit around zero lag (default +/- 30s).

    Returns:
        Dictionary with positive lag, absolute lag, polarity, correlation coefficients, and peak uniqueness.
    """
    v = np.array(vitsig_2000, dtype=np.float64)
    r = np.array(resp_2000, dtype=np.float64)
    n = len(v)

    if n < 2000:
        return {
            "status": "INSUFFICIENT_LENGTH",
            "pos_lag_ms": np.nan,
            "pos_corr": np.nan,
            "abs_lag_ms": np.nan,
            "abs_corr": np.nan,
            "polarity": 0,
            "peak_uniqueness": np.nan,
            "notes": "Signal length shorter than 1 second",
        }

    v_std = np.std(v)
    r_std = np.std(r)

    # Check for near-constant signal (e.g. strict breath hold during apnea)
    if v_std < 1e-5 or r_std < 1e-5:
        return {
            "status": "INSUFFICIENT_VARIATION",
            "pos_lag_ms": np.nan,
            "pos_corr": np.nan,
            "abs_lag_ms": np.nan,
            "abs_corr": np.nan,
            "polarity": 0,
            "peak_uniqueness": np.nan,
            "notes": "Signal standard deviation too low for reliable cross-correlation",
        }

    # Normalize to zero-mean unit-variance
    vn = (v - np.mean(v)) / v_std
    rn = (r - np.mean(r)) / r_std

    c = signal.correlate(rn, vn, mode="full") / n
    lags = signal.correlation_lags(n, n, mode="full")

    # Restrict to search window
    max_lag_samples = int(max_lag_sec * 2000)
    mask = np.abs(lags) <= max_lag_samples
    c_win = c[mask]
    lags_win = lags[mask]

    # 1. Positive peak (TechValidation.m exact method)
    pos_idx = np.argmax(c_win)
    pos_lag_samples = lags_win[pos_idx]
    pos_lag_ms = float(pos_lag_samples * 0.5)
    pos_corr = float(c_win[pos_idx])

    # 2. Absolute peak (polarity check)
    abs_idx = np.argmax(np.abs(c_win))
    abs_lag_samples = lags_win[abs_idx]
    abs_lag_ms = float(abs_lag_samples * 0.5)
    abs_corr = float(c_win[abs_idx])
    polarity = 1 if abs_corr >= 0 else -1

    # 3. Peak uniqueness / secondary peak ratio
    # Exclude +/- 1000 samples (+/- 0.5s) around primary peak
    surround_mask = np.abs(lags_win - pos_lag_samples) > 1000
    if np.any(surround_mask):
        sec_peak = float(np.max(c_win[surround_mask]))
        peak_uniqueness = round(pos_corr / (sec_peak + 1e-6), 3) if pos_corr > 0 else 0.0
    else:
        peak_uniqueness = 1.0

    return {
        "status": "SUCCESS",
        "pos_lag_ms": round(pos_lag_ms, 2),
        "pos_corr": round(pos_corr, 4),
        "abs_lag_ms": round(abs_lag_ms, 2),
        "abs_corr": round(abs_corr, 4),
        "polarity": polarity,
        "polarity_matches_positive": bool(pos_lag_samples == abs_lag_samples),
        "peak_uniqueness": peak_uniqueness,
        "notes": f"Peak corr {pos_corr:.4f} at {pos_lag_ms:.2f} ms; Polarity {polarity:+d}",
    }


def compute_surrogate_respiratory_control(
    vitsig_2000: np.ndarray,
    resp_2000: np.ndarray,
    num_surrogates: int = 5,
) -> Dict[str, Any]:
    """Compute phase-randomized surrogate control to quantify chance correlation.

    Preserves power spectral density (exact frequency content) while randomizing
    Fourier phases (Theiler et al., 1992), destroying temporal synchronization.
    """
    v = np.array(vitsig_2000, dtype=np.float64)
    r = np.array(resp_2000, dtype=np.float64)
    n = len(v)

    if n < 4000 or np.std(v) < 1e-5 or np.std(r) < 1e-5:
        return {"mean_surrogate_corr": np.nan, "max_surrogate_corr": np.nan}

    vn = (v - np.mean(v)) / np.std(v)
    rn = (r - np.mean(r)) / np.std(r)

    fft_v = np.fft.rfft(vn)
    rng = np.random.default_rng(42)

    surr_corrs = []
    for _ in range(num_surrogates):
        phases = rng.uniform(0, 2 * np.pi, len(fft_v))
        random_phasors = np.exp(1j * phases)
        random_phasors[0] = 1.0
        v_surr = np.fft.irfft(fft_v * random_phasors, n=n)
        v_surr = (v_surr - np.mean(v_surr)) / (np.std(v_surr) + 1e-12)

        c = signal.correlate(rn, v_surr, mode="full") / n
        surr_corrs.append(float(np.max(np.abs(c))))

    return {
        "mean_surrogate_corr": round(float(np.mean(surr_corrs)), 4),
        "max_surrogate_corr": round(float(np.max(surr_corrs)), 4),
    }
