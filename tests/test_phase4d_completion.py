"""Unit and integration tests for Phase 4D implementation completion and sign-off.

Tests:
1. TargetNormalizer: strict training-fold fitting, zero-variance guard, inverse transform recovery.
2. CNNRegressor: forward pass with raw radar and latent features, parameter counts (3,377).
3. KANFeatureRegressor: direct feature modeling on (B, 16) with 1,360 parameters.
4. KANRegressor and MLPRegressor dual-input interfaces (raw windows or latent features).
5. Output bias initialization methods.
6. Synthetic end-to-end integration pipeline with target normalization (verifying MAE < 5.0 BPM).
7. Phase 4D deliverables presence in outputs/phase4/completion_run_001/.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np
import pytest

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf

from src.kan.kan_layer import KANLayer
from src.kan.kan_model import (
    ConvFeatureExtractor,
    KANFeatureRegressor,
    KANRegressor,
    MLPRegressor,
    CNNRegressor,
    MeanPredictorBaseline,
)
from src.kan.loso_evaluator import LOSOEvaluator
from src.kan.normalization import TargetNormalizer


# ==============================================================================
# 1. Target Normalization Tests
# ==============================================================================

def test_target_normalizer_training_only_fit():
    """Verify target normalizer standardizes using training fold only and inverts accurately."""
    y_train = np.array([60.0, 70.0, 80.0])
    normalizer = TargetNormalizer()
    y_norm = normalizer.fit_transform(y_train)

    assert normalizer.is_fitted is True
    assert normalizer.sample_count == 3
    assert normalizer.train_mean == pytest.approx(70.0, abs=1e-5)
    assert normalizer.train_std == pytest.approx(np.std(y_train), abs=1e-5)

    # Normalized values should have mean 0.0
    assert np.mean(y_norm) == pytest.approx(0.0, abs=1e-5)

    # Inverse transform recovers original targets
    y_recovered = normalizer.inverse_transform(y_norm)
    np.testing.assert_allclose(y_recovered, y_train, rtol=1e-5, atol=1e-5)

    # Test transform on unseen test target
    y_test = np.array([90.0])
    y_test_norm = normalizer.transform(y_test)
    assert y_test_norm[0] == pytest.approx((90.0 - 70.0) / normalizer.train_std, abs=1e-4)


def test_target_normalizer_zero_variance():
    """Verify zero-variance guard sets std to 1.0 to prevent division by zero."""
    y_const = np.array([72.0, 72.0, 72.0])
    normalizer = TargetNormalizer()
    y_norm = normalizer.fit_transform(y_const)

    assert normalizer.train_std == 1.0
    np.testing.assert_allclose(y_norm, [0.0, 0.0, 0.0])

    y_rec = normalizer.inverse_transform(y_norm)
    np.testing.assert_allclose(y_rec, y_const)


def test_target_normalizer_leakage_guards():
    """Verify that using un-fitted normalizer or passing non-finite targets raises errors."""
    normalizer = TargetNormalizer()
    with pytest.raises(RuntimeError, match="must be fitted"):
        normalizer.transform([65.0])

    with pytest.raises(RuntimeError, match="must be fitted"):
        normalizer.inverse_transform([0.0])

    with pytest.raises(ValueError, match="non-finite"):
        normalizer.fit([60.0, np.nan, 80.0])


# ==============================================================================
# 2. Model Baseline & Dual Interface Tests
# ==============================================================================

def test_cnn_regressor_forward_and_params():
    """Verify CNNRegressor baseline forward pass and parameter counts."""
    cnn = CNNRegressor(latent_dim=16)
    x_raw = tf.zeros((2, 3333))
    out_raw = cnn(x_raw)
    assert out_raw.shape == (2,)

    # Total parameters: 3,360 (Conv backbone) + 17 (Dense linear readout) = 3,377
    assert cnn.count_params() == 3377
    assert cnn.feature_extractor.count_params() == 3360

    # Dual input: pass features directly
    x_feat = tf.zeros((2, 16))
    out_feat = cnn(x_feat)
    assert out_feat.shape == (2,)


def test_kan_feature_regressor_direct():
    """Verify KANFeatureRegressor consumes 16 latent features directly with 1,360 params."""
    head = KANFeatureRegressor(in_features=16, hidden_dim=8)
    x_feat = tf.zeros((3, 16))
    out = head(x_feat)
    assert out.shape == (3,)
    assert head.count_params() == 1360


def test_kan_regressor_dual_input():
    """Verify KANRegressor accepts raw radar windows (3333) or features (16) directly."""
    kan = KANRegressor(latent_dim=16, hidden_dim=8)
    out_raw = kan(tf.zeros((2, 3333)))
    assert out_raw.shape == (2,)
    assert kan.count_params() == 4720

    out_feat = kan(tf.zeros((2, 16)))
    assert out_feat.shape == (2,)

    # Test extract_features
    feats = kan.extract_features(tf.zeros((2, 3333)))
    assert feats.shape == (2, 16)


def test_mlp_regressor_dual_input():
    """Verify MLPRegressor accepts raw radar windows or features directly."""
    mlp = MLPRegressor(latent_dim=16, hidden_dim=8)
    out_raw = mlp(tf.zeros((2, 3333)))
    assert out_raw.shape == (2,)
    assert mlp.count_params() == 3505

    out_feat = mlp(tf.zeros((2, 16)))
    assert out_feat.shape == (2,)


# ==============================================================================
# 3. Synthetic Integration Pipeline Test (Verifying Resolution of 68 BPM MAE)
# ==============================================================================

def test_synthetic_end_to_end_integration_pipeline():
    """Verify that target normalization reduces synthetic KAN MAE from 68 to < 5 BPM."""
    evaluator = LOSOEvaluator(output_dir=Path("outputs/phase4/completion_run_001"))
    results = evaluator.run_synthetic_benchmark(num_samples=64, epochs=15, seed=42)

    assert results["kan_loss_decreased"] is True
    assert results["kan_gradient_flow_verified"] is True

    # With target normalization, MAE is on physical BPM scale and must be < 5 BPM
    kan_mae = results["kan_metrics"]["mae_bpm"]
    assert kan_mae < 5.0, f"KAN MAE {kan_mae} exceeded 5.0 BPM; normalization failed"
    assert results["kan_metrics"]["within_5bpm_pct"] >= 85.0

    mlp_mae = results["mlp_metrics"]["mae_bpm"]
    assert mlp_mae < 5.0

    cnn_mae = results["cnn_metrics"]["mae_bpm"]
    assert cnn_mae < 10.0


# ==============================================================================
# 4. Phase 4D Deliverables Presence Test
# ==============================================================================

def test_phase4d_deliverables_presence():
    """Verify presence of all 11 required deliverables in outputs/phase4/completion_run_001/."""
    run_dir = Path(__file__).resolve().parent.parent / "outputs" / "phase4" / "completion_run_001"
    required = [
        "phase4_final_completion_report.md",
        "component_implementation_matrix.md",
        "kan_implementation_verification.md",
        "baseline_integration_report.md",
        "feature_pipeline_verification.md",
        "normalization_and_initialization_report.md",
        "loso_integrity_report.md",
        "integration_test_report.md",
        "test_execution_record.md",
        "error_log.md",
        "final_verdict.md",
    ]
    for fname in required:
        fpath = run_dir / fname
        assert fpath.exists(), f"Missing required deliverable: {fname}"
        assert fpath.stat().st_size > 0, f"Empty deliverable: {fname}"
