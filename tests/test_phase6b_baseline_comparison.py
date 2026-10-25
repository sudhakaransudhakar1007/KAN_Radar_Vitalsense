"""Unit and contract tests for Phase 6B multi-model baseline comparison."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import tensorflow as tf

from src.kan.evaluator import ModelEvaluator
from src.kan.kan_model import CNNRegressor, KANRegressor, MLPRegressor, MeanPredictorBaseline
from src.kan.trainer import KANTrainer, TrainingConfig, generate_synthetic_dataset


def test_multi_model_io_contracts():
    """Verify that KAN, MLP, CNN, and MeanPredictor obey identical I/O contracts."""
    batch_size = 4
    input_dim = 100
    x_tensor = tf.random.normal((batch_size, input_dim))
    x_numpy = x_tensor.numpy()
    y_train = np.array([65.0, 70.0, 75.0, 80.0])

    # KAN
    kan = KANRegressor(input_dim=input_dim, latent_dim=16, hidden_dim=8)
    y_kan = kan(x_tensor)
    assert y_kan.shape == (batch_size,), f"KAN output shape mismatch: {y_kan.shape}"

    # MLP
    mlp = MLPRegressor(input_dim=input_dim, latent_dim=16, hidden_dim=8)
    y_mlp = mlp(x_tensor)
    assert y_mlp.shape == (batch_size,), f"MLP output shape mismatch: {y_mlp.shape}"

    # CNN
    cnn = CNNRegressor(input_dim=input_dim, latent_dim=16)
    y_cnn = cnn(x_tensor)
    assert y_cnn.shape == (batch_size,), f"CNN output shape mismatch: {y_cnn.shape}"

    # Mean Baseline
    mean_model = MeanPredictorBaseline()
    mean_model.fit(y_train)
    y_mean = mean_model.predict(x_numpy)
    assert y_mean.shape == (batch_size,), f"MeanBaseline output shape mismatch: {y_mean.shape}"
    np.testing.assert_allclose(y_mean, np.full(batch_size, 72.5))


def test_mean_baseline_strict_training_only_fit():
    """Verify MeanPredictor fits strictly on training labels without test leakage."""
    y_train = np.array([60.0, 70.0, 80.0])
    y_test = np.array([120.0]) # Outlier test target

    model = MeanPredictorBaseline()
    model.fit(y_train)
    assert model.mean_hr_ == 70.0

    preds = model.predict(np.zeros((1, 50)))
    assert preds[0] == 70.0


def test_phase6b_comparison_artifacts_presence_and_schema():
    """Verify Phase 6B baseline comparison artifacts on disk."""
    base_out = Path(__file__).resolve().parents[1] / "outputs" / "phase6b"
    assert (base_out / "baseline_comparison_summary.json").exists()
    assert (base_out / "pooled_comparison.csv").exists()
    assert (base_out / "per_subject_comparison.csv").exists()
    assert (base_out / "statistical_tests.json").exists()

    pooled_df = pd.read_csv(base_out / "pooled_comparison.csv")
    expected_models = {"KAN", "MLP", "CNN", "MEAN"}
    assert set(pooled_df["model"]) == expected_models

    per_subj_df = pd.read_csv(base_out / "per_subject_comparison.csv")
    assert len(per_subj_df) == 32 # 4 models x 8 subjects
    assert set(per_subj_df["subject_id"].unique()) == {
        f"SYNTH_S{i:02d}" for i in range(1, 9)
    }

    stat_data = json.loads((base_out / "statistical_tests.json").read_text(encoding="utf-8"))
    assert "KAN_vs_MLP" in stat_data
    assert "KAN_vs_CNN" in stat_data
    assert "KAN_vs_MEAN" in stat_data


def test_subject_level_vs_window_level_hypothesis_qualification():
    """Verify qualification of subject-level vs pseudoreplicated window-level tests."""
    base_out = Path(__file__).resolve().parents[1] / "outputs" / "phase6b"
    stat_data = json.loads((base_out / "statistical_tests.json").read_text(encoding="utf-8"))

    # For KAN vs MLP:
    # Subject-level must NOT claim significance at 0.05
    mlp_subj = stat_data["KAN_vs_MLP"]["subject_level_n8"]
    assert mlp_subj["paired_ttest"]["significant_at_05"] is False
    assert mlp_subj["wilcoxon_test"]["significant_at_05"] is False

    # For KAN vs MEAN:
    # Subject-level MUST confirm significance at 0.05
    mean_subj = stat_data["KAN_vs_MEAN"]["subject_level_n8"]
    assert mean_subj["paired_ttest"]["significant_at_05"] is True
    assert mean_subj["wilcoxon_test"]["significant_at_05"] is True


def test_phase6b_reproducibility_manifest_and_artifact_validator():
    """Verify that reproducibility manifest exists and artifact validator passes without error."""
    from src.kan.artifact_validator import validate_synthetic_run_artifacts

    base_out = Path(__file__).resolve().parents[1] / "outputs" / "phase6b"
    manifest_p = base_out / "reproducibility_manifest.json"
    assert manifest_p.exists(), f"Missing reproducibility manifest: {manifest_p}"

    manifest_data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert manifest_data["benchmark_name"] == "PHASE_6B_FAIR_SYNTHETIC_BASELINE_COMPARISON"
    assert "KAN" in manifest_data["models"]
    assert "MLP" in manifest_data["models"]
    assert "CNN" in manifest_data["models"]
    assert "MEAN" in manifest_data["models"]

    # Run automated validator
    report = validate_synthetic_run_artifacts(base_out)
    assert report["status"] == "PASS", f"Artifact validator failed: {report['errors']}"
    assert len(report["errors"]) == 0
    assert len(report["models_validated"]) == 4
