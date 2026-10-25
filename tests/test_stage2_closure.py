"""Stage 2 closure tests for open Phase 2A / Step 2B issues (ISS-07, 08, 09, 10, 12, 13b)."""

from __future__ import annotations

import numpy as np
import pytest

from src.sync_validation.respiratory_validator import (
    truncate_respiration_dynamic_length_in_memory,
    resample_signals_to_2000hz,
)
from src.sync_validation.ecg_processor import (
    clean_ecg_isolated_nans,
    clean_ecg_nans,
    compute_ecg_sqi,
    detect_r_peaks,
)
from src.sync_validation.cardiac_radar_validator import (
    estimate_peak_frequency_parabolic,
    estimate_window_hr_multi_estimator,
    compute_window_level_hr_agreement,
)
from src.sync_validation.runner import categorize_monitor_latency


class TestStage2ISS12DynamicArrayLengths:
    """ISS-12: Dynamic array length querying and trailing tail truncation in-memory."""

    def test_truncate_mismatched_durations_in_memory(self):
        rad_fs = 333.3333333333333
        ref_fs = 256.0
        # VS24_Resting case: 40,000 radar (120.0s), 30,600 respiration (119.53125s)
        v_raw = np.ones(40000, dtype=float) * 1.5
        r_raw = np.ones(30600, dtype=float) * 0.8

        v_trunc, r_trunc, info = truncate_respiration_dynamic_length_in_memory(
            v_raw, rad_fs, r_raw, ref_fs
        )

        assert info["has_length_mismatch"] is True
        assert np.isclose(info["common_duration_s"], 119.53125, atol=1e-3)
        assert len(r_trunc) == 30600
        assert len(v_trunc) == int(np.floor(119.53125 * rad_fs))
        # Ensure original arrays unchanged on disk/memory
        assert len(v_raw) == 40000
        assert len(r_raw) == 30600

    def test_truncate_matching_durations(self):
        rad_fs = 333.3333333333333
        ref_fs = 256.0
        # Standard case: 40,000 radar, 30,720 respiration (both 120.0s)
        v_raw = np.ones(40000, dtype=float)
        r_raw = np.ones(30720, dtype=float)

        v_trunc, r_trunc, info = truncate_respiration_dynamic_length_in_memory(
            v_raw, rad_fs, r_raw, ref_fs
        )

        assert info["has_length_mismatch"] is False
        assert info["respiration_samples_excluded"] == 0
        assert len(v_trunc) == 40000
        assert len(r_trunc) == 30720


class TestStage2ISS13bSingleSampleNaNInterpolation:
    """ISS-13b: Interpolate isolated single-sample delimiter NaNs; multi-sample gaps rejected."""

    def test_clean_isolated_single_sample_nans(self):
        raw = np.array([10.0, 12.0, np.nan, 16.0, 18.0], dtype=float)
        clean, info = clean_ecg_isolated_nans(raw, max_gap=1)

        assert info["total_nan_count"] == 1
        assert info["isolated_nan_count"] == 1
        assert info["isolated_indices"] == [2]
        assert info["has_multi_sample_gaps"] is False
        assert info["uninterpolated_nan_count"] == 0
        assert np.isclose(clean[2], 14.0)
        # Original array unmodified
        assert np.isnan(raw[2])

    def test_reject_multi_sample_nan_gaps(self):
        # 3 contiguous NaNs (multi-sample gap)
        raw = np.array([10.0, np.nan, np.nan, np.nan, 20.0], dtype=float)
        clean, info = clean_ecg_isolated_nans(raw, max_gap=1)

        assert info["total_nan_count"] == 3
        assert info["isolated_nan_count"] == 0
        assert info["has_multi_sample_gaps"] is True
        assert info["multi_sample_gap_count"] == 1
        assert info["multi_sample_gap_indices"] == [[1, 2, 3]]
        assert info["uninterpolated_nan_count"] == 3
        # Multi-sample gap must NOT be interpolated (remains NaN)
        assert np.isnan(clean[1:4]).all()

    def test_mixed_isolated_and_multi_sample_nans(self):
        # Index 2 is isolated; Indices 5,6 form a 2-sample gap
        raw = np.array([10.0, 12.0, np.nan, 16.0, 18.0, np.nan, np.nan, 24.0], dtype=float)
        clean, info = clean_ecg_isolated_nans(raw, max_gap=1)

        assert info["total_nan_count"] == 3
        assert info["isolated_nan_count"] == 1
        assert info["isolated_indices"] == [2]
        assert info["has_multi_sample_gaps"] is True
        assert info["uninterpolated_nan_count"] == 2
        # Isolated sample interpolated
        assert np.isclose(clean[2], 14.0)
        # Multi-sample gap preserved as NaN
        assert np.isnan(clean[5]) and np.isnan(clean[6])


class TestStage2ISS08SignalQualityIndex:
    """ISS-08: Multi-parameter SQI (coverage > 85%, max gap < 3s, amplitude unvalidated)."""

    def test_sqi_partial_on_good_ecg(self):
        # 120s synthetic ECG at 60 bpm (1 beat/s, 119 intervals of 1.0s = 119s coverage)
        peak_times = np.arange(0.5, 120.0, 1.0)
        rr = np.diff(peak_times)
        valid_mask = np.ones(len(rr), dtype=bool)

        payload = {
            "peaks": (peak_times * 500).astype(int),
            "peak_times": peak_times,
            "rr_intervals": rr,
            "valid_rr_mask": valid_mask,
        }
        sqi = compute_ecg_sqi(payload, duration_s=120.0)

        assert sqi["beat_coverage_ratio"] > 0.85
        assert sqi["max_rr_gap_s"] < 3.0
        # Amplitude stability unvalidated -> verdict is SQI_PARTIAL, recording-level PASS cannot be granted
        assert sqi["sqi_verdict"] == "SQI_PARTIAL"
        assert sqi["recording_level_pass"] is False
        assert sqi["amplitude_stability_status"] == "UNSPECIFIED / NOT VALIDATED"

    def test_sqi_fail_on_large_gap(self):
        # ECG with a 5-second dropped-beat gap
        p1 = np.arange(0.5, 50.0, 1.0)
        p2 = np.arange(55.5, 120.0, 1.0)  # 5.5s gap between 49.5 and 55.5
        peak_times = np.concatenate([p1, p2])
        rr = np.diff(peak_times)
        valid_mask = (rr >= 0.34) & (rr <= 1.71)  # 5.5s RR is rejected

        payload = {
            "peaks": (peak_times * 500).astype(int),
            "peak_times": peak_times,
            "rr_intervals": rr,
            "valid_rr_mask": valid_mask,
        }
        sqi = compute_ecg_sqi(payload, duration_s=120.0)

        assert sqi["max_rr_gap_s"] >= 3.0
        assert sqi["sqi_verdict"] == "SQI_FAIL"
        assert sqi["recording_level_pass"] is False

    def test_sqi_fail_on_low_coverage(self):
        # Only 50 beats in 120s (coverage ~ 50s / 120s = 41.7% < 85%)
        peak_times = np.arange(1.0, 51.0, 1.0)
        rr = np.diff(peak_times)
        valid_mask = np.ones(len(rr), dtype=bool)

        payload = {
            "peaks": (peak_times * 500).astype(int),
            "peak_times": peak_times,
            "rr_intervals": rr,
            "valid_rr_mask": valid_mask,
        }
        sqi = compute_ecg_sqi(payload, duration_s=120.0)

        assert sqi["beat_coverage_ratio"] < 0.85
        assert sqi["sqi_verdict"] == "SQI_FAIL"
        assert sqi["recording_level_pass"] is False


class TestStage2ISS09ISS10MultiEstimatorSpectralRefinement:
    """ISS-09 & ISS-10: 4x zero-padding and 3-point parabolic peak interpolation."""

    def test_parabolic_peak_interpolation_accuracy(self):
        # Pure sine wave at 1.25 Hz (75.0 bpm) on a 10s window (df = 0.1 Hz)
        fs = 333.3333333333333
        t = np.arange(int(10.0 * fs)) / fs
        true_f = 1.25  # exactly halfway between 1.2 Hz and 1.3 Hz discrete bins
        sig = np.sin(2 * np.pi * true_f * t)

        est = estimate_window_hr_multi_estimator(sig, fs)

        # Unpadded discrete bin is quantized near 1.2 Hz (72 bpm) or 1.3 Hz (78 bpm)
        assert np.isclose(est["unpadded_bin_bpm"], 72.0, atol=0.2) or np.isclose(est["unpadded_bin_bpm"], 78.0, atol=0.2)
        # Parabolic interpolation refines closer to true 75.0 bpm
        assert abs(est["parabolic_bpm"] - 75.0) < abs(est["unpadded_bin_bpm"] - 75.0)
        # 4x zero-padding evaluates on 4x finer grid (df = 0.025 Hz = 1.5 bpm)
        assert abs(est["zeropad_4x_bpm"] - 75.0) <= 1.5

    def test_zero_shift_is_primary_metric_and_best_shift_diagnostic(self):
        fs = 333.3333333333333
        t = np.arange(int(30.0 * fs)) / fs
        vitsig = np.sin(2 * np.pi * 1.2 * t)
        beats = np.arange(1.0, 29.0, 0.8333)
        r_peaks = {
            "peaks": (beats * 500).astype(int),
            "peak_times": beats,
            "rr_intervals": np.diff(beats),
            "valid_rr_mask": np.ones(len(beats) - 1, dtype=bool),
        }

        res = compute_window_level_hr_agreement(vitsig, fs, r_peaks, win_sec=10.0, hop_sec=5.0)

        assert res["status"] == "SUCCESS"
        assert res["primary_metric"] == "zero_shift"
        assert res["best_shift_role"] == "diagnostic_exploratory_only"
        assert "zero_shift_mae_bpm" in res
        assert "zero_shift_mae_parabolic_bpm" in res
        assert "zero_shift_mae_4x_zeropad_bpm" in res
        assert "estimators_mae_comparison" in res


class TestStage2ISS07MonitorLatencyCategorization:
    """ISS-07: Separates negative lags, near-zero (|tau| <= 1s), small non-zero, and large lags."""

    def test_negative_lag_categorization(self):
        # VS05_Apnea case: -3s optimal lag
        status, reason = categorize_monitor_latency(best_lag_s=-3.0, is_ambiguous=False, mae_improvement_bpm=0.5)
        assert status == "NEGATIVE_LAG_OBSERVED"
        assert "curve flatness" not in reason
        assert "negative shift" in reason

    def test_near_zero_lag_categorization(self):
        status_0, reason_0 = categorize_monitor_latency(best_lag_s=0.0, is_ambiguous=False)
        assert status_0 == "NEAR_ZERO_LATENCY"
        assert "curve flatness" not in reason_0

        status_1, reason_1 = categorize_monitor_latency(best_lag_s=1.0, is_ambiguous=False)
        assert status_1 == "NEAR_ZERO_LATENCY"
        assert "curve flatness" not in reason_1

    def test_small_nonzero_lag_categorization(self):
        # VS13_Apnea case: +3s optimal lag
        status, reason = categorize_monitor_latency(best_lag_s=3.0, is_ambiguous=False, mae_improvement_bpm=0.6)
        assert status == "SMALL_NONZERO_LAG"
        assert "curve flatness" not in reason
        assert "small positive shift" in reason

    def test_empirical_latency_categorization(self):
        # Typical 6s display delay
        status, reason = categorize_monitor_latency(best_lag_s=6.0, is_ambiguous=False, mae_improvement_bpm=2.4)
        assert status == "EMPIRICAL_LATENCY_OBSERVED"
        assert "curve flatness" not in reason
        assert "display/averaging delay" in reason

    def test_ambiguous_low_hrv_cites_curve_flatness(self):
        status, reason = categorize_monitor_latency(best_lag_s=2.0, is_ambiguous=True, mae_improvement_bpm=0.05)
        assert status == "INCONCLUSIVE_LOW_HRV"
        assert "curve flatness" in reason
