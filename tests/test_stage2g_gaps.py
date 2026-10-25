"""Tests for Stage 2G: Window-level RR coverage gate and NaN edge/burst cases.

Covers:
- Window RR coverage gate: coverage 0.79 (fail), 0.80 (fail, strict inequality),
  0.81 (pass), all-invalid, NaN in beats, long RR gap.
- NaN cleaning edge/burst cases: NaN at index 0, NaN at index -1,
  burst of 2 at boundary (start/end), and all-NaN arrays.
"""

import numpy as np
import pytest

from src.sync_validation.window_coverage_gate import evaluate_window_rr_coverage
from src.sync_validation.ecg_processor import clean_ecg_isolated_nans, clean_ecg_nans


class TestWindowRRCoverageGate:
    """Tests for evaluate_window_rr_coverage (G3 gate)."""

    def test_coverage_0_79_fails(self):
        """Coverage of 0.79 (7.9s in 10s window) is REJECTED (< 0.80)."""
        # 8 intervals of 1.0s, last interval 0.9s: total 7.9s
        peaks = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.9]
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
            strict_inequality=True,
        )
        assert len(res) == 1
        w = res[0]
        assert abs(w["coverage_fraction"] - 0.79) < 1e-5
        assert w["status"] == "REJECTED"
        assert "INSUFFICIENT_RR_COVERAGE" in w["rejection_reason"]

    def test_coverage_0_80_fails_strict_inequality(self):
        """Coverage of exactly 0.80 (8.0s in 10s window) is REJECTED under strict inequality (> 0.80)."""
        # 8 intervals of 1.0s: total 8.0s in [0, 10]
        peaks = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
            strict_inequality=True,
        )
        assert len(res) == 1
        w = res[0]
        assert abs(w["coverage_fraction"] - 0.80) < 1e-5
        assert w["status"] == "REJECTED"
        assert "INSUFFICIENT_RR_COVERAGE" in w["rejection_reason"]
        assert "not > 0.80" in w["rejection_reason"]

    def test_coverage_0_81_passes(self):
        """Coverage of 0.81 (8.1s in 10s window) is ACCEPTED (> 0.80)."""
        # Intervals totaling 8.1s in [0, 10]
        peaks = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.1]
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
            strict_inequality=True,
        )
        assert len(res) == 1
        w = res[0]
        assert abs(w["coverage_fraction"] - 0.81) < 1e-5
        assert w["status"] == "ACCEPTED"
        assert w["rejection_reason"] is None

    def test_all_invalid_rr_fails(self):
        """Window where all RR intervals exceed physiological bounds (0.3s-2.0s) has 0 coverage and is REJECTED."""
        peaks = [0.0, 5.0, 10.0]  # RR = 5.0s, non-physiological
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
        )
        assert len(res) == 1
        w = res[0]
        assert w["coverage_fraction"] == 0.0
        assert w["rr_interval_count"] == 0
        assert w["status"] == "REJECTED"

    def test_nan_in_peaks_fails(self):
        """Window containing explicit NaN in peak times is REJECTED with NAN_IN_BEATS."""
        peaks = [1.0, np.nan, 3.0]
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
        )
        assert len(res) == 1
        w = res[0]
        assert w["status"] == "REJECTED"
        assert w["rejection_reason"] == "NAN_IN_BEATS"

    def test_long_rr_gap_fails(self):
        """Window with a 5.0s physiological gap between clusters only accumulates valid interval durations."""
        # [1, 2] is 1s, [7, 8] is 1s. The interval [2, 7] is 5.0s (> 2.0s), so contributes 0.
        peaks = [1.0, 2.0, 7.0, 8.0]
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
        )
        assert len(res) == 1
        w = res[0]
        assert abs(w["coverage_fraction"] - 0.20) < 1e-5
        assert w["rr_interval_count"] == 2
        assert w["status"] == "REJECTED"

    def test_zero_beats_fails(self):
        """Window with 0 beats is REJECTED with ZERO_BEATS."""
        res = evaluate_window_rr_coverage(
            {"peak_times": []},
            total_duration_s=10.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
        )
        assert len(res) == 1
        w = res[0]
        assert w["beat_count"] == 0
        assert w["status"] == "REJECTED"
        assert w["rejection_reason"] == "ZERO_BEATS"

    def test_grid_count_120s(self):
        """Standard 120s duration with 10s window and 5s hop generates exactly 23 windows."""
        # Uniform 1 Hz peaks across 120s
        peaks = np.arange(1.0, 120.0, 1.0)
        res = evaluate_window_rr_coverage(
            {"peak_times": peaks},
            total_duration_s=120.0,
            win_sec=10.0,
            hop_sec=5.0,
            min_coverage=0.80,
        )
        assert len(res) == 23
        assert res[0]["start_s"] == 0.0
        assert res[0]["end_s"] == 10.0
        assert res[-1]["start_s"] == 110.0
        assert res[-1]["end_s"] == 120.0
        for w in res:
            assert w["status"] == "ACCEPTED"


class TestNaNCleaningEdgeAndBurstCases:
    """Tests documenting NaN edge/burst case behavior in clean_ecg_isolated_nans & clean_ecg_nans."""

    def test_nan_at_index_0(self):
        """Single NaN at index 0 is isolated (gap=1); nearest valid neighbor fills it."""
        arr = np.array([np.nan, 2.0, 3.0, 4.0])
        clean_arr, info = clean_ecg_isolated_nans(arr, max_gap=1)
        assert not np.isnan(clean_arr[0])
        assert clean_arr[0] == 2.0
        assert info["total_nan_count"] == 1
        assert info["isolated_nan_count"] == 1
        assert info["isolated_indices"] == [0]
        assert info["multi_sample_gap_count"] == 0
        assert not info["has_multi_sample_gaps"]

        # Also via clean_ecg_nans default
        c_nans, count, indices = clean_ecg_nans(arr)
        assert clean_arr[0] == 2.0
        assert count == 1
        assert indices == [0]

    def test_nan_at_index_minus_1(self):
        """Single NaN at index -1 (tail) is isolated (gap=1); nearest valid neighbor fills it."""
        arr = np.array([1.0, 2.0, 3.0, np.nan])
        clean_arr, info = clean_ecg_isolated_nans(arr, max_gap=1)
        assert not np.isnan(clean_arr[-1])
        assert clean_arr[-1] == 3.0
        assert info["total_nan_count"] == 1
        assert info["isolated_nan_count"] == 1
        assert info["isolated_indices"] == [3]
        assert info["multi_sample_gap_count"] == 0

    def test_burst_of_2_at_start_boundary(self):
        """Burst of 2 NaNs at start is a multi-sample gap (gap=2 > max_gap=1); left UNINTERPOLATED."""
        arr = np.array([np.nan, np.nan, 3.0, 4.0])
        clean_arr, info = clean_ecg_isolated_nans(arr, max_gap=1)
        assert np.isnan(clean_arr[0])
        assert np.isnan(clean_arr[1])
        assert clean_arr[2] == 3.0
        assert info["total_nan_count"] == 2
        assert info["isolated_nan_count"] == 0
        assert info["multi_sample_gap_count"] == 1
        assert info["uninterpolated_nan_count"] == 2
        assert info["has_multi_sample_gaps"] is True

    def test_burst_of_2_at_end_boundary(self):
        """Burst of 2 NaNs at end is a multi-sample gap (gap=2 > max_gap=1); left UNINTERPOLATED."""
        arr = np.array([1.0, 2.0, np.nan, np.nan])
        clean_arr, info = clean_ecg_isolated_nans(arr, max_gap=1)
        assert clean_arr[0] == 1.0
        assert clean_arr[1] == 2.0
        assert np.isnan(clean_arr[2])
        assert np.isnan(clean_arr[3])
        assert info["total_nan_count"] == 2
        assert info["isolated_nan_count"] == 0
        assert info["multi_sample_gap_count"] == 1
        assert info["uninterpolated_nan_count"] == 2
        assert info["has_multi_sample_gaps"] is True

    def test_all_nan_array(self):
        """All-NaN array contains only multi-sample gap; all elements remain NaN."""
        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        clean_arr, info = clean_ecg_isolated_nans(arr, max_gap=1)
        assert np.all(np.isnan(clean_arr))
        assert info["total_nan_count"] == 4
        assert info["isolated_nan_count"] == 0
        assert info["multi_sample_gap_count"] == 1
        assert info["uninterpolated_nan_count"] == 4
        assert info["has_multi_sample_gaps"] is True
