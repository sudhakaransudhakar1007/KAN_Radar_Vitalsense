"""Unit tests for Phase 6 ModelEvaluator with exact known analytical solutions."""

from __future__ import annotations

import numpy as np
import pytest

from src.kan.evaluator import ModelEvaluator


def test_perfect_predictions():
    """Verify metrics when predictions perfectly match ground truth."""
    y_true = np.array([60.0, 70.0, 80.0, 90.0])
    y_pred = np.array([60.0, 70.0, 80.0, 90.0])

    res = ModelEvaluator.compute_detailed_metrics(y_true, y_pred)
    assert res.mae_bpm == 0.0
    assert res.rmse_bpm == 0.0
    assert res.bias_bpm == 0.0
    assert res.medae_bpm == 0.0
    assert res.std_error_bpm == 0.0
    assert res.max_error_bpm == 0.0
    assert res.pearson_r == 1.0
    assert res.spearman_rho == 1.0
    assert res.within_3bpm_pct == 100.0
    assert res.within_5bpm_pct == 100.0
    assert res.within_10bpm_pct == 100.0
    assert res.bland_altman_lower_loa == 0.0
    assert res.bland_altman_upper_loa == 0.0


def test_constant_prediction_bias():
    """Verify metrics with a constant additive prediction bias (+2.5 BPM)."""
    y_true = np.array([60.0, 70.0, 80.0, 90.0])
    y_pred = y_true + 2.5

    res = ModelEvaluator.compute_detailed_metrics(y_true, y_pred)
    assert res.mae_bpm == 2.5
    assert res.rmse_bpm == 2.5
    assert res.bias_bpm == 2.5
    assert res.medae_bpm == 2.5
    assert res.std_error_bpm == 0.0
    assert res.max_error_bpm == 2.5
    assert res.pearson_r == 1.0
    assert res.spearman_rho == 1.0
    assert res.within_3bpm_pct == 100.0
    assert res.within_5bpm_pct == 100.0
    assert res.within_10bpm_pct == 100.0
    assert res.bland_altman_lower_loa == 2.5
    assert res.bland_altman_upper_loa == 2.5


def test_zero_variance_and_undefined_correlation():
    """Verify defensive handling when true targets have zero variance."""
    y_true = np.array([72.0, 72.0, 72.0, 72.0])
    y_pred = np.array([70.0, 74.0, 71.0, 73.0])

    res = ModelEvaluator.compute_detailed_metrics(y_true, y_pred)
    # Correlation must gracefully evaluate to 0.0 without throwing exceptions
    assert res.pearson_r == 0.0
    assert res.pearson_pvalue == 1.0
    assert res.spearman_rho == 0.0
    assert res.spearman_pvalue == 1.0
    assert res.mae_bpm == 1.5
    assert res.bias_bpm == 0.0


def test_nan_inf_input_rejection():
    """Verify runtime rejection of NaN and Inf values."""
    with pytest.raises(ValueError, match="non-finite"):
        ModelEvaluator.compute_detailed_metrics([60.0, np.nan], [60.0, 65.0])

    with pytest.raises(ValueError, match="non-finite"):
        ModelEvaluator.compute_detailed_metrics([60.0, 70.0], [60.0, np.inf])


def test_empty_or_insufficient_samples():
    """Verify input validation on empty arrays or length mismatch."""
    with pytest.raises(ValueError, match="empty arrays"):
        ModelEvaluator.compute_detailed_metrics([], [])

    with pytest.raises(ValueError, match="Length mismatch"):
        ModelEvaluator.compute_detailed_metrics([60.0, 70.0], [60.0])


def test_bland_altman_calculations():
    """Verify exact Bland-Altman Limits of Agreement with known values.
    
    y_true = [60, 70, 80, 90]
    y_pred = [61, 73, 79, 94]
    errors = [1, 3, -1, 4]
    mean bias = 7 / 4 = 1.75
    std_err (ddof=1) = sqrt(14.75 / 3) = 2.21735578
    lower_loa = 1.75 - 1.96 * 2.21735578 = -2.5960
    upper_loa = 1.75 + 1.96 * 2.21735578 = 6.0960
    """
    y_true = np.array([60.0, 70.0, 80.0, 90.0])
    y_pred = np.array([61.0, 73.0, 79.0, 94.0])

    res = ModelEvaluator.compute_detailed_metrics(y_true, y_pred)
    assert res.bias_bpm == 1.75
    assert res.std_error_bpm == 2.217
    assert res.bland_altman_lower_loa == -2.596
    assert res.bland_altman_upper_loa == 6.096


def test_tolerance_percentages():
    """Verify exact clinical tolerance percentages with known error vector.
    
    errors = [1.0, 2.5, 3.5, 5.0, 8.0] (5 samples)
    abs_errors = [1.0, 2.5, 3.5, 5.0, 8.0]
    within +/- 3: [1.0, 2.5] -> 2 / 5 = 40%
    within +/- 5: [1.0, 2.5, 3.5, 5.0] -> 4 / 5 = 80%
    within +/- 10: all 5 -> 5 / 5 = 100%
    """
    y_true = np.array([60.0, 60.0, 60.0, 60.0, 60.0])
    y_pred = np.array([61.0, 62.5, 63.5, 65.0, 68.0])

    res = ModelEvaluator.compute_detailed_metrics(y_true, y_pred)
    assert res.within_3bpm_pct == 40.0
    assert res.within_5bpm_pct == 80.0
    assert res.within_10bpm_pct == 100.0


def test_paired_statistical_comparisons():
    """Verify paired t-test and Wilcoxon tests between comparative models."""
    y_true = np.array([60.0, 65.0, 70.0, 75.0, 80.0])
    preds_a = np.array([60.5, 65.2, 70.8, 74.9, 80.3]) # MAE = 0.54
    preds_b = np.array([63.0, 68.0, 74.0, 79.0, 85.0]) # MAE = 3.80

    comp = ModelEvaluator.compare_models(preds_a, preds_b, y_true, "ModelA", "ModelB")
    assert comp["mae_model_a"] < comp["mae_model_b"]
    assert comp["paired_ttest"]["significant_at_05"] is True
    assert comp["paired_ttest"]["p_value"] < 0.05
    assert comp["wilcoxon_test"]["p_value"] < 0.1

    # Test identical predictions
    comp_same = ModelEvaluator.compare_models(preds_a, preds_a, y_true, "ModelA", "ModelA_Copy")
    assert comp_same["mae_difference"] == 0.0
    assert comp_same["paired_ttest"]["t_statistic"] == 0.0
    assert comp_same["paired_ttest"]["p_value"] == 1.0
    assert comp_same["wilcoxon_test"]["p_value"] == 1.0
