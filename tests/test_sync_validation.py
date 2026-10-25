"""Automated unit and synthetic control tests for Phase 2A Step 2 synchronization validation."""

from __future__ import annotations

import numpy as np
import pytest

from src.sync_validation.cardiac_radar_validator import (
    compute_window_level_hr_agreement,
    extract_radar_cardiac_signal,
    synthetic_known_offset_test,
)
from src.sync_validation.ecg_processor import (
    clean_ecg_nans,
    derive_1hz_ecg_hr,
    detect_r_peaks,
    scan_monitor_hr_lag,
)
from src.sync_validation.respiratory_validator import (
    compute_respiratory_xcorr,
    compute_surrogate_respiratory_control,
    resample_signals_to_2000hz,
)


class TestECGProcessor:
    """Tests for ECG cleaning, R-peak detection, and monitor HR latency scan."""

    def test_clean_ecg_nans_isolated(self):
        """Test that isolated NaNs are properly detected and interpolated."""
        raw = np.array([10.0, 12.0, np.nan, 16.0, 18.0], dtype=float)
        clean, count, indices = clean_ecg_nans(raw)
        assert count == 1
        assert indices == [2]
        assert not np.isnan(clean).any()
        assert np.isclose(clean[2], 14.0)
        # Verify original array unchanged
        assert np.isnan(raw[2])

    def test_clean_ecg_nans_no_nans(self):
        """Test array without NaNs passes through unchanged."""
        raw = np.array([1.0, 2.0, 3.0], dtype=float)
        clean, count, indices = clean_ecg_nans(raw)
        assert count == 0
        assert len(indices) == 0
        np.testing.assert_array_equal(clean, raw)

    def test_detect_r_peaks_synthetic(self):
        """Test R-peak detector on synthetic ECG with known heart rate (60 bpm = 1 beat/sec)."""
        fs = 500.0
        duration_s = 10.0
        t = np.arange(int(duration_s * fs)) / fs
        # Synthesize ECG-like signal with QRS spikes at exactly t = 1, 2, ..., 9
        ecg = np.zeros_like(t)
        true_beats = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        for b in true_beats:
            idx = int(b * fs)
            # Add narrow QRS spike
            ecg[idx - 5 : idx + 5] = [20, 50, 100, 300, 500, 300, 100, 50, 20, 0]

        result = detect_r_peaks(ecg, fs=fs, min_bpm=40.0, max_bpm=150.0)
        assert result["status"] == "SUCCESS"
        assert result["valid_peak_count"] >= 8
        assert np.isclose(result["mean_hr_bpm"], 60.0, atol=2.0)
        assert result["qc_verdict"] == "PASS"

    def test_detect_r_peaks_insufficient_length(self):
        """Test that overly short ECG returns INSUFFICIENT_LENGTH."""
        short_ecg = np.zeros(100)
        result = detect_r_peaks(short_ecg, fs=500.0)
        assert result["status"] == "INSUFFICIENT_LENGTH"
        assert result["qc_verdict"] == "FAIL"

    def test_derive_1hz_ecg_hr(self):
        """Test derivation of 1 Hz instantaneous HR grid."""
        peaks = np.array([500, 1000, 1500, 2000, 2500])  # beats at 1s, 2s, 3s, 4s, 5s (60 bpm)
        r_peak_result = {
            "peaks": peaks,
            "peak_times": peaks / 500.0,
            "rr_intervals": np.diff(peaks / 500.0),
            "valid_rr_mask": np.ones(len(peaks) - 1, dtype=bool),
        }
        t_grid, hr_1hz, conv = derive_1hz_ecg_hr(r_peak_result, total_seconds=10)
        assert len(t_grid) == 10
        assert len(hr_1hz) == 10
        assert np.allclose(hr_1hz, 60.0)

    def test_scan_monitor_hr_lag_sign_convention(self):
        """Test that positive lag correctly detects when monitor lags behind ECG.

        If ECG has a step change at t=20s and monitor shows the step change at t=26s,
        the lag should be detected at +6s.
        """
        ecg_hr = np.full(120, 60.0)
        ecg_hr[20:] = 80.0  # Step change at t=20s

        # Monitor shows same step change delayed by +6s (at t=26s)
        mon_hr = np.full(120, 60.0)
        mon_hr[26:] = 80.0

        scan = scan_monitor_hr_lag(ecg_hr, mon_hr, max_lag_s=10)
        assert scan["status"] == "SUCCESS"
        assert scan["best_lag_s"] == 6
        assert np.isclose(scan["best_mae_bpm"], 0.0)
        assert scan["zero_lag_mae_bpm"] > 0.0

    def test_scan_monitor_hr_lag_ambiguous(self):
        """Test that constant HR series correctly triggers ambiguity flag."""
        ecg_hr = np.full(120, 65.0)
        mon_hr = np.full(120, 65.0)
        scan = scan_monitor_hr_lag(ecg_hr, mon_hr, max_lag_s=10)
        assert scan["status"] == "SUCCESS"
        assert scan["is_ambiguous"] is True
        assert scan["best_mae_bpm"] == 0.0


class TestRespiratoryValidator:
    """Tests for respiratory resampling, cross-correlation, and surrogate controls."""

    def test_resample_signals_to_2000hz(self):
        """Test rational resampling to 2000 Hz from 333.33 Hz and 256.0 Hz."""
        vitsig = np.zeros(40000)
        resp = np.zeros(30720)
        v_2000, r_2000 = resample_signals_to_2000hz(vitsig, 333.3333333333333, resp, 256.0)
        assert len(v_2000) == 240000
        assert len(r_2000) == 240000

    def test_resample_signals_truncated(self):
        """Test resampling with truncated respiration (e.g. VS24 resting 30600 samples)."""
        vitsig = np.zeros(40000)
        resp = np.zeros(30600)
        v_2000, r_2000 = resample_signals_to_2000hz(vitsig, 333.3333333333333, resp, 256.0)
        assert len(v_2000) == len(r_2000)
        assert len(v_2000) == 239063

    def test_compute_respiratory_xcorr_known_lag(self):
        """Test recovery of known time lag in respiratory signals."""
        fs = 2000
        t = np.arange(10 * fs) / fs
        # Synthetic breathing signal (0.25 Hz = 15 breaths/min)
        resp = np.sin(2 * np.pi * 0.25 * t)

        # Shift radar signal by +10 samples = +5.0 ms
        vitsig = np.roll(resp, -10)

        res = compute_respiratory_xcorr(vitsig, resp, max_lag_sec=5.0)
        assert res["status"] == "SUCCESS"
        assert np.isclose(res["pos_lag_ms"], 5.0, atol=1.0)
        assert res["pos_corr"] > 0.95
        assert res["polarity"] == 1

    def test_compute_respiratory_xcorr_polarity_inversion(self):
        """Test that inverted signal yields negative correlation and polarity = -1."""
        fs = 2000
        t = np.arange(10 * fs) / fs
        resp = np.sin(2 * np.pi * 0.25 * t)
        vitsig_inverted = -resp

        res = compute_respiratory_xcorr(vitsig_inverted, resp, max_lag_sec=5.0)
        assert res["status"] == "SUCCESS"
        assert res["polarity"] == -1
        assert res["abs_corr"] < -0.90

    def test_compute_respiratory_xcorr_low_variation(self):
        """Test that near-flat signal (e.g. strict breath hold) returns INSUFFICIENT_VARIATION."""
        v = np.zeros(4000)
        r = np.zeros(4000)
        res = compute_respiratory_xcorr(v, r)
        assert res["status"] == "INSUFFICIENT_VARIATION"
        assert np.isnan(res["pos_lag_ms"])

    def test_compute_surrogate_respiratory_control(self):
        """Test that phase-randomized surrogate reduces correlation below original perfect match."""
        fs = 2000
        t = np.arange(60 * fs) / fs
        # Amplitude-modulated breathing with broadband physiological noise
        resp = np.sin(2 * np.pi * 0.25 * t) * (1.0 + 0.3 * np.cos(2 * np.pi * 0.05 * t)) + 0.5 * np.random.randn(len(t))
        vitsig = resp.copy()

        ctrl = compute_surrogate_respiratory_control(vitsig, resp)
        assert np.isfinite(ctrl["max_surrogate_corr"])
        # Original correlation is 1.0; surrogate must be reduced
        assert ctrl["max_surrogate_corr"] < 0.75


class TestCardiacRadarValidator:
    """Tests for cardiac band filtering, window HR agreement, and synthetic controls."""

    def test_extract_radar_cardiac_signal(self):
        """Test bandpass filtering isolates 0.8-3.0 Hz frequencies."""
        fs = 333.3333333333333
        t = np.arange(int(30 * fs)) / fs
        # Signal with low freq (0.2 Hz breathing) and cardiac freq (1.5 Hz = 90 bpm)
        raw = np.sin(2 * np.pi * 0.2 * t) + 0.5 * np.sin(2 * np.pi * 1.5 * t)
        cardiac = extract_radar_cardiac_signal(raw, fs)

        # Cardiac signal should have suppressed low frequency
        assert np.std(cardiac) > 0.0
        # Peak frequency in cardiac band should be 1.5 Hz
        fft_c = np.fft.rfft(cardiac)
        freqs = np.fft.rfftfreq(len(cardiac), d=1.0 / fs)
        peak_f = freqs[np.argmax(np.abs(fft_c))]
        assert np.isclose(peak_f, 1.5, atol=0.1)

    def test_synthetic_known_offset(self):
        """Test recovery of known synthetic offset in oscillatory signals."""
        res = synthetic_known_offset_test(duration_s=30.0, true_offset_s=0.060)
        assert res["passed"] is True
        assert np.isclose(res["estimated_offset_s"], 0.060, atol=0.005)

    def test_window_level_hr_agreement_synthetic(self):
        """Test window-level HR agreement on time-varying synthetic radar and ECG signals."""
        fs = 333.3333333333333
        duration_s = 60.0
        t = np.arange(int(duration_s * fs)) / fs

        # Time-varying HR: 1.0 Hz (60 bpm) for first 30s, 1.5 Hz (90 bpm) for last 30s
        phase = np.where(t < 30.0, 2 * np.pi * 1.0 * t, 2 * np.pi * 1.0 * 30.0 + 2 * np.pi * 1.5 * (t - 30.0))
        vitsig = np.sin(phase)

        # R-peaks matching 1.0 Hz (dt = 1.0s) for t < 30s, then 1.5 Hz (dt = 0.667s) for t >= 30s
        beats_part1 = np.arange(1.0, 30.0, 1.0)
        beats_part2 = np.arange(30.0, 59.0, 0.6667)
        peak_times = np.concatenate([beats_part1, beats_part2])
        peaks = (peak_times * 500.0).astype(int)
        r_peaks = {
            "peaks": peaks,
            "peak_times": peak_times,
            "rr_intervals": np.diff(peak_times),
            "valid_rr_mask": np.ones(len(peak_times) - 1, dtype=bool),
        }

        res = compute_window_level_hr_agreement(vitsig, fs, r_peaks, win_sec=10.0, hop_sec=5.0)
        assert res["status"] == "SUCCESS"
        assert res["zero_shift_mae_bpm"] < 5.0
        assert np.isclose(res["best_shift_s"], 0.0, atol=1.0)
