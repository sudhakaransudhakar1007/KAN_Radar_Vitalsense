"""Unit and regression tests for Phase 4 KAN model, baselines, LOSO evaluation, and gate enforcement.

Tests:
1. KANLayer forward pass, B-spline basis evaluation, and output shapes.
2. KANRegressor and MLPRegressor forward pass with 3333 input samples.
3. MeanPredictorBaseline fit and predict logic.
4. Leave-One-Subject-Out (LOSO) fold partitioning: 24 subjects, zero cross-subject leakage.
5. Gate blocker enforcement: Phase 2A gate status 'OPEN' blocks real-data training.
6. Metric computation: MAE, RMSE, Pearson r, within +/-3 bpm, within +/-5 bpm.
7. Deliverable verification: all 9 Phase 4 run_001 deliverables exist and conform to schema.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf

from src.kan.kan_layer import KANLayer
from src.kan.kan_model import ConvFeatureExtractor, KANRegressor, MLPRegressor, MeanPredictorBaseline
from src.kan.loso_evaluator import EvaluationMetrics, FoldSplitInfo, LOSOEvaluator


# ==============================================================================
# 1. KAN Layer & Model Architecture Tests
# ==============================================================================

def test_kan_layer_forward_and_shapes():
    """Verify that KANLayer computes forward pass and preserves expected tensor shapes."""
    batch_size = 4
    in_features = 16
    out_features = 8
    grid_size = 5
    spline_order = 3

    layer = KANLayer(
        in_features=in_features,
        out_features=out_features,
        grid_size=grid_size,
        spline_order=spline_order,
    )
    x = tf.random.normal((batch_size, in_features))
    y = layer(x)

    assert y.shape == (batch_size, out_features)
    assert layer.spline_coeffs.shape == (out_features, in_features, layer.num_splines)
    assert layer.w_base.shape == (out_features, in_features)
    assert layer.w_spline.shape == (out_features, in_features)


def test_conv_feature_extractor_shape():
    """Verify ConvFeatureExtractor downsamples 3333 raw samples to latent_dim (16)."""
    extractor = ConvFeatureExtractor(latent_dim=16)
    x = tf.random.normal((3, 3333, 1))
    z = extractor(x)
    assert z.shape == (3, 16)


def test_kan_regressor_forward():
    """Verify KANRegressor full model forward pass and output scalar shape."""
    model = KANRegressor(input_dim=3333, latent_dim=16, hidden_dim=8)
    x = tf.random.normal((2, 3333))
    out = model(x)
    assert out.shape == (2,)


def test_mlp_regressor_forward():
    """Verify MLPRegressor controlled baseline forward pass."""
    model = MLPRegressor(input_dim=3333, latent_dim=16, hidden_dim=8)
    x = tf.random.normal((2, 3333))
    out = model(x)
    assert out.shape == (2,)


def test_mean_predictor_baseline():
    """Verify MeanPredictorBaseline fit and predict."""
    baseline = MeanPredictorBaseline()
    y_train = np.array([60.0, 70.0, 80.0])
    baseline.fit(y_train)
    assert baseline.mean_hr_ == pytest.approx(70.0, abs=1e-5)

    x_dummy = np.zeros((4, 3333))
    y_pred = baseline.predict(x_dummy)
    assert len(y_pred) == 4
    assert np.all(y_pred == 70.0)


# ==============================================================================
# 2. Metric Computation Tests
# ==============================================================================

def test_compute_metrics():
    """Verify biomedical evaluation metrics calculation."""
    y_true = np.array([60.0, 70.0, 80.0])
    y_pred = np.array([62.0, 71.0, 78.0])

    metrics = LOSOEvaluator.compute_metrics(y_true, y_pred)

    # MAE = (|2| + |1| + |-2|) / 3 = 5/3 = 1.667
    assert metrics.mae_bpm == pytest.approx(1.667, abs=0.01)
    # RMSE = sqrt((4 + 1 + 4)/3) = sqrt(3) = 1.732
    assert metrics.rmse_bpm == pytest.approx(1.732, abs=0.01)
    # All errors are <= 2.0, so within 3 and 5 bpm should be 100%
    assert metrics.within_3bpm_pct == 100.0
    assert metrics.within_5bpm_pct == 100.0
    assert metrics.pearson_r > 0.9


# ==============================================================================
# 3. LOSO Cross-Validation Partitioning Tests
# ==============================================================================

def test_loso_fold_partitioning_leakage_free():
    """Verify all 24 subjects are partitioned into 24 folds with zero cross-subject leakage."""
    evaluator = LOSOEvaluator()
    evaluator.load_manifest()
    folds = evaluator.build_loso_folds()

    assert len(folds) == 24
    total_test_windows = sum(f.test_windows for f in folds)
    assert total_test_windows == 1029

    for f in folds:
        assert f.subject_leakage_detected is False
        assert f.train_subject_count == 23
        assert f.train_windows + f.test_windows == 1029
        assert f.test_windows > 0


# ==============================================================================
# 4. Gate Enforcement & Blocker Tests
# ==============================================================================

def test_gate_blocker_enforcement():
    """Verify that Phase 2A gate status 'OPEN' blocks persistent real-data training."""
    evaluator = LOSOEvaluator()
    is_blocked, gate_status, blocker_reason = evaluator.check_gate_status()

    assert is_blocked is True
    assert gate_status == "OPEN"
    assert "BLOCKED" in blocker_reason


# ==============================================================================
# 5. Phase 4 Deliverables Verification Tests
# ==============================================================================

def test_deliverable_artifacts_presence_and_validity():
    """Verify that all 9 required deliverable files exist in outputs/phase4/run_001/."""
    run_dir = Path(__file__).resolve().parent.parent / "outputs" / "phase4" / "run_001"
    required_files = [
        "run_manifest.json",
        "input_validation_report.md",
        "model_architecture_summary.md",
        "fold_split_manifest.csv",
        "training_config.json",
        "baseline_comparison_report.md",
        "test_execution_record.md",
        "error_log.md",
        "phase4_final_report.md",
    ]

    for filename in required_files:
        filepath = run_dir / filename
        assert filepath.exists(), f"Missing required deliverable: {filename}"
        assert filepath.stat().st_size > 0, f"Deliverable is empty: {filename}"

    # Verify run manifest contents
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["stage"] == "PHASE_4_KAN_MODEL_DEVELOPMENT_AND_EVALUATION"
    assert manifest["execution_status"] == "INFRASTRUCTURE_VERIFIED_REAL_TRAINING_BLOCKED"
    assert manifest["gate_enforcement"]["phase2a_gate_status"] == "OPEN"
    assert manifest["gate_enforcement"]["is_blocked"] is True

    # Verify fold split manifest contents
    df_folds = pd.read_csv(run_dir / "fold_split_manifest.csv")
    assert len(df_folds) == 24
    assert set(df_folds["test_subject"].unique()) == {f"VS{i:02d}" for i in range(1, 25)}
    assert (df_folds["subject_leakage_detected"] == False).all()
