"""Stage 2F boundary and reason string tests for categorize_monitor_latency."""

from __future__ import annotations

import pytest
from src.sync_validation.runner import categorize_monitor_latency


class TestStage2FMonitorLatencyBoundaries:
    """A5: Comprehensive boundary and neutral wording tests."""

    def test_tau_negative_boundary_strict(self):
        # tau = -1.0001 is strictly < -1.0s -> NEGATIVE_LAG_OBSERVED
        status, reason = categorize_monitor_latency(best_lag_s=-1.0001, is_ambiguous=False, mae_improvement_bpm=1.0)
        assert status == "NEGATIVE_LAG_OBSERVED"
        assert "-1.0s" in reason
        assert "non-causal artifact" not in reason
        assert "cause NOT_VERIFIABLE (hardware timing UNVERIFIED)" in reason
        assert "curve flatness" not in reason

    def test_tau_minus_one_is_near_zero(self):
        # tau = -1.0 is within |tau| <= 1.0s -> NEAR_ZERO_LATENCY
        status, reason = categorize_monitor_latency(best_lag_s=-1.0, is_ambiguous=False)
        assert status == "NEAR_ZERO_LATENCY"
        assert "-1.0s" in reason
        assert "|tau| <= 1.0s" in reason
        assert "curve flatness" not in reason

    def test_tau_zero_has_no_negative_zero(self):
        # tau = 0.0 -> formatted as +0.0s, no "-0s"
        status, reason = categorize_monitor_latency(best_lag_s=0.0, is_ambiguous=False)
        assert status == "NEAR_ZERO_LATENCY"
        assert "+0.0s" in reason
        assert "-0" not in reason
        assert "curve flatness" not in reason

    def test_tau_plus_one_is_near_zero(self):
        # tau = +1.0 -> NEAR_ZERO_LATENCY
        status, reason = categorize_monitor_latency(best_lag_s=1.0, is_ambiguous=False)
        assert status == "NEAR_ZERO_LATENCY"
        assert "+1.0s" in reason
        assert "|tau| <= 1.0s" in reason
        assert "curve flatness" not in reason

    def test_tau_just_above_one_is_small_nonzero(self):
        # tau = 1.0001 -> SMALL_NONZERO_LAG
        status, reason = categorize_monitor_latency(best_lag_s=1.0001, is_ambiguous=False, mae_improvement_bpm=1.2)
        assert status == "SMALL_NONZERO_LAG"
        assert "+1.0s" in reason
        assert "1.0s < tau < 4.0s" in reason
        assert "cause NOT_VERIFIABLE (hardware timing UNVERIFIED)" in reason
        assert "curve flatness" not in reason

    def test_tau_just_below_four_is_small_nonzero(self):
        # tau = 3.999 -> SMALL_NONZERO_LAG
        status, reason = categorize_monitor_latency(best_lag_s=3.999, is_ambiguous=False, mae_improvement_bpm=1.2)
        assert status == "SMALL_NONZERO_LAG"
        assert "+4.0s" in reason
        assert "1.0s < tau < 4.0s" in reason
        assert "cause NOT_VERIFIABLE (hardware timing UNVERIFIED)" in reason
        assert "curve flatness" not in reason

    def test_tau_four_is_empirical_latency(self):
        # tau = 4.0 -> EMPIRICAL_LATENCY_OBSERVED
        status, reason = categorize_monitor_latency(best_lag_s=4.0, is_ambiguous=False, mae_improvement_bpm=2.5)
        assert status == "EMPIRICAL_LATENCY_OBSERVED"
        assert "+4.0s" in reason
        assert "reflects display/averaging delay" not in reason
        assert "cause NOT_VERIFIABLE (hardware timing UNVERIFIED)" in reason
        assert "curve flatness" not in reason

    def test_neutral_reason_strings_across_conditions(self):
        # Check forbidden phrases are absent across various lags
        for test_tau in [-5.0, -1.0001, -1.0, 0.0, 1.0, 1.0001, 3.999, 4.0, 7.5]:
            _, reason = categorize_monitor_latency(best_lag_s=test_tau, is_ambiguous=False, mae_improvement_bpm=1.0)
            assert "non-causal artifact" not in reason
            assert "reflects display/averaging delay" not in reason
            assert "curve flatness" not in reason

    def test_curve_flatness_only_when_ambiguous(self):
        _, reason_amb = categorize_monitor_latency(best_lag_s=2.5, is_ambiguous=True, mae_improvement_bpm=0.02)
        assert "curve flatness" in reason_amb

        _, reason_unamb = categorize_monitor_latency(best_lag_s=2.5, is_ambiguous=False, mae_improvement_bpm=1.5)
        assert "curve flatness" not in reason_unamb
