"""Integration and unit tests for Phase 5 KAN training implementation.

Tests:
1. Framework-correct forward and backward passes.
2. Split isolation and subject disjointness.
3. Train-only feature scaling and target normalization.
4. Invalid dimensions and non-finite value handling.
5. Checkpoint save/load and prediction equivalence.
6. Reproducibility under configured random seeds.
7. Fail-closed real-data gate enforcement.
8. Synthetic-only input isolation and labeling.
9. CLI argument validation and output provenance.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import tensorflow as tf
from tensorflow import keras

from src.kan.feature_scaler import FeatureScaler
from src.kan.kan_layer import KANLayer
from src.kan.kan_model import KANRegressor
from src.kan.loso_evaluator import GateBlockerError
from src.kan.normalization import TargetNormalizer
from src.kan.train_cli import main as cli_main
from src.kan.trainer import (
    KANTrainer,
    TrainingConfig,
    build_loso_splits_with_inner_val,
    generate_synthetic_dataset,
    set_deterministic_seeds,
    verify_gate_approval_for_real_data,
)


@pytest.fixture
def temp_run_dir():
    """Provides an isolated temporary directory for test artifacts."""
    d = Path(tempfile.mkdtemp(prefix="phase5_test_run_"))
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_framework_forward_and_backward_passes():
    """Verify framework-correct forward and backward gradient passes for KAN in TensorFlow/Keras."""
    set_deterministic_seeds(42)
    input_dim = 120
    batch_size = 4
    model = KANRegressor(input_dim=input_dim, latent_dim=16, hidden_dim=8, grid_size=5, spline_order=3)

    x = tf.random.normal((batch_size, input_dim))
    y = tf.constant([0.5, -0.2, 0.8, -0.5], dtype=tf.float32)

    optimizer = keras.optimizers.Adam(learning_rate=0.01)

    with tf.GradientTape() as tape:
        preds = model(x, training=True)
        loss = tf.reduce_mean(tf.square(preds - y))

    grads = tape.gradient(loss, model.trainable_variables)

    # Check that all trainable variables receive valid finite, non-zero gradients
    assert len(grads) > 0
    for g, v in zip(grads, model.trainable_variables):
        assert g is not None, f"Gradient for {v.name} is None."
        assert np.all(np.isfinite(g.numpy())), f"Gradient for {v.name} contains NaN/Inf."

    # Verify optimizer step updates weights
    initial_loss = float(loss.numpy())
    optimizer.apply_gradients(zip(grads, model.trainable_variables))

    # Second forward pass
    preds_after = model(x, training=False)
    new_loss = float(tf.reduce_mean(tf.square(preds_after - y)).numpy())
    assert new_loss < initial_loss, f"Expected loss to decrease after gradient step: {new_loss} vs {initial_loss}"


def test_split_isolation_and_disjointness():
    """Verify strict 3-way subject disjointness: train, val, and test subjects never overlap."""
    manifest_df, _, _ = generate_synthetic_dataset(num_subjects=8, windows_per_subject=5, seed=42)
    splits = build_loso_splits_with_inner_val(manifest_df, val_subjects_count=2, seed=42)

    assert len(splits) == 8
    all_subjects = set(manifest_df["subject_id"].unique())

    for split in splits:
        s_tr = set(split.train_subjects)
        s_va = set(split.val_subjects)
        s_te = {split.test_subject}

        # Assert zero overlap between any pair
        assert len(s_tr & s_va) == 0, f"Fold {split.fold} train and val overlap: {s_tr & s_va}"
        assert len(s_tr & s_te) == 0, f"Fold {split.fold} train and test overlap: {s_tr & s_te}"
        assert len(s_va & s_te) == 0, f"Fold {split.fold} val and test overlap: {s_va & s_te}"

        # Assert full coverage of all subjects
        assert (s_tr | s_va | s_te) == all_subjects
        assert not split.subject_leakage_detected
        assert split.train_samples > 0
        assert split.val_samples > 0
        assert split.test_samples > 0


def test_train_only_feature_and_target_normalization():
    """Verify feature scaling and target normalizer are fitted ONLY on inner-training data."""
    # 1. FeatureScaler train-only fit
    scaler = FeatureScaler(scaling_type="standard")
    X_train = np.array([[10.0, 100.0], [20.0, 200.0], [30.0, 300.0]], dtype=np.float64)
    X_val = np.array([[40.0, 400.0]], dtype=np.float64)

    scaler.fit(X_train)
    assert scaler.is_fitted
    np.testing.assert_allclose(scaler.mean_, [20.0, 200.0])

    # Transform without refitting
    X_val_scaled = scaler.transform(X_val)
    # Expected: (40 - 20) / std(10, 20, 30) = 20 / 8.1649658 = 2.4494897
    expected_std = np.std(X_train, axis=0)
    expected_val_scaled = (X_val - scaler.mean_) / expected_std
    np.testing.assert_allclose(X_val_scaled, expected_val_scaled, rtol=1e-5)

    # Inverse transform
    X_val_recon = scaler.inverse_transform(X_val_scaled)
    np.testing.assert_allclose(X_val_recon, X_val, rtol=1e-5)

    # 2. TargetNormalizer train-only fit
    target_norm = TargetNormalizer()
    y_train = np.array([60.0, 70.0, 80.0], dtype=np.float64)
    y_test = np.array([75.0], dtype=np.float64)

    target_norm.fit(y_train)
    assert target_norm.is_fitted
    assert target_norm.train_mean == 70.0

    y_test_norm = target_norm.transform(y_test)
    y_test_bpm = target_norm.inverse_transform(y_test_norm)
    np.testing.assert_allclose(y_test_bpm, y_test, rtol=1e-5)


def test_invalid_dimensions_and_non_finite_values():
    """Verify runtime rejection of invalid tensor dimensions and non-finite values."""
    scaler = FeatureScaler()

    # Non-2D inputs
    with pytest.raises(ValueError, match="expects 2D array"):
        scaler.fit(np.zeros(10))

    # Empty inputs
    with pytest.raises(ValueError, match="empty samples"):
        scaler.fit(np.zeros((0, 5)))

    # NaN / Inf in features
    with pytest.raises(ValueError, match="non-finite"):
        scaler.fit(np.array([[1.0, np.nan], [2.0, 3.0]]))
    with pytest.raises(ValueError, match="non-finite"):
        scaler.fit(np.array([[1.0, np.inf], [2.0, 3.0]]))

    # Dimension mismatch during transform
    scaler.fit(np.array([[1.0, 2.0], [3.0, 4.0]]))
    with pytest.raises(ValueError, match="Feature dimension mismatch"):
        scaler.transform(np.array([[1.0, 2.0, 3.0]]))

    # TargetNormalizer with NaN
    norm = TargetNormalizer()
    with pytest.raises(ValueError, match="non-finite"):
        norm.fit([60.0, np.nan, 80.0])


def test_checkpoint_save_load_prediction_equivalence(temp_run_dir):
    """Verify that saving and reloading best model weights yields identical predictions."""
    set_deterministic_seeds(42)
    input_dim = 64
    x = tf.random.normal((5, input_dim))

    model1 = KANRegressor(input_dim=input_dim, latent_dim=16, hidden_dim=8)
    preds1 = model1(x).numpy()

    weights_file = temp_run_dir / "test_checkpoint.weights.h5"
    model1.save_weights(str(weights_file))

    model2 = KANRegressor(input_dim=input_dim, latent_dim=16, hidden_dim=8)
    # Build model variables
    model2(tf.zeros((1, input_dim)))
    model2.load_weights(str(weights_file))
    preds2 = model2(x).numpy()

    max_diff = float(np.max(np.abs(preds1 - preds2)))
    assert max_diff == 0.0, f"Prediction mismatch after checkpoint reload: max diff = {max_diff}"


def test_reproducibility_under_configured_seed(temp_run_dir):
    """Verify deterministic training outputs under identical configured seeds."""
    manifest_df, X, y = generate_synthetic_dataset(num_subjects=4, windows_per_subject=4, window_len=100, seed=42)

    cfg1 = TrainingConfig(
        run_id="repro_1",
        mode="synthetic",
        seed=42,
        epochs=3,
        batch_size=4,
        output_dir=str(temp_run_dir / "run1"),
    )
    trainer1 = KANTrainer(cfg1)
    res1 = trainer1.execute_training(
        custom_manifest=manifest_df, custom_X=X, custom_y=y, max_folds=1
    )

    cfg2 = TrainingConfig(
        run_id="repro_2",
        mode="synthetic",
        seed=42,
        epochs=3,
        batch_size=4,
        output_dir=str(temp_run_dir / "run2"),
    )
    trainer2 = KANTrainer(cfg2)
    res2 = trainer2.execute_training(
        custom_manifest=manifest_df, custom_X=X, custom_y=y, max_folds=1
    )

    assert res1["mean_mae_bpm"] == res2["mean_mae_bpm"], "MAE differed between identical seed runs."
    assert res1["mean_rmse_bpm"] == res2["mean_rmse_bpm"], "RMSE differed between identical seed runs."


def test_fail_closed_real_data_gate_enforcement():
    """Verify that attempting real-data training aborts with GateBlockerError when gate is OPEN."""
    base_dir = Path(__file__).resolve().parents[1]
    is_approved, reason = verify_gate_approval_for_real_data(base_dir)

    # In current state, gate must NOT be approved
    assert not is_approved, "Expected gate approval to be FALSE in current codebase."

    cfg = TrainingConfig(mode="real", output_dir="outputs/phase5/blocked_run")
    trainer = KANTrainer(cfg, base_dir=base_dir)

    with pytest.raises(GateBlockerError, match="Real-data training BLOCKED"):
        trainer.execute_training()


def test_synthetic_only_input_isolation(temp_run_dir):
    """Verify synthetic mode outputs are isolated and clearly labeled SYNTHETIC_BENCHMARK."""
    cfg = TrainingConfig(
        run_id="test_synth_isolation",
        mode="synthetic",
        seed=42,
        epochs=2,
        batch_size=8,
        synthetic_subjects_count=4,
        synthetic_windows_per_subject=4,
        output_dir=str(temp_run_dir / "synth_out"),
    )
    trainer = KANTrainer(cfg)
    results = trainer.execute_training(max_folds=2)

    out_p = Path(cfg.output_dir)
    assert out_p.exists()

    # Verify metadata labels
    meta = json.loads((out_p / "run_metadata.json").read_text(encoding="utf-8"))
    assert meta["benchmark_type"] == "SYNTHETIC_BENCHMARK"
    assert meta["mode"] == "synthetic"

    # Verify split manifest subjects
    splits_df = pd.read_csv(out_p / "fold_split_manifest.csv")
    for subj in splits_df["test_subject"]:
        assert subj.startswith("SYNTH_"), f"Unexpected non-synthetic subject: {subj}"

    # Verify summary metrics label
    summary = json.loads((out_p / "summary_metrics.json").read_text(encoding="utf-8"))
    assert summary["benchmark_status"] == "SYNTHETIC_BENCHMARK"


def test_cli_argument_validation_and_output_provenance(temp_run_dir):
    """Verify CLI interface parses arguments, applies overrides, and produces provenance artifacts."""
    out_dir = str(temp_run_dir / "cli_run")
    cli_args = [
        "--run-id", "test_cli_execution",
        "--output-dir", out_dir,
        "--synthetic",
        "--epochs", "2",
        "--batch-size", "8",
        "--max-folds", "1",
        "--seed", "123",
        "--model-type", "kan",
    ]

    ret = cli_main(cli_args)
    assert ret == 0

    p = Path(out_dir)
    assert (p / "run_metadata.json").exists()
    assert (p / "training_config.json").exists()
    assert (p / "fold_split_manifest.csv").exists()
    assert (p / "summary_metrics.json").exists()
    assert (p / "predictions_all_folds.csv").exists()
    assert (p / "phase5_synthetic_run_report.md").exists()

    # Check that fold 1 checkpoint and scalers were saved
    fold1_dir = p / "folds" / "fold_01"
    assert (fold1_dir / "best_model.weights.h5").exists()
    assert (fold1_dir / "feature_scaler.json").exists()
    assert (fold1_dir / "target_normalizer.json").exists()
    assert (fold1_dir / "feature_schema.json").exists()
    assert (fold1_dir / "history.json").exists()
    assert (fold1_dir / "predictions_test.csv").exists()


def test_phase6_evaluator_synthetic(temp_run_dir):
    """Verify Phase 6 ModelEvaluator on synthetic prediction artifacts."""
    from src.kan.evaluator import ModelEvaluator

    # Create dummy predictions CSV
    preds_p = temp_run_dir / "test_preds.csv"
    df = pd.DataFrame({
        "subject_id": ["S1", "S1", "S2", "S2"],
        "y_true_bpm": [60.0, 65.0, 70.0, 75.0],
        "y_pred_bpm": [61.0, 64.0, 72.0, 74.0],
    })
    df.to_csv(preds_p, index=False)

    res = ModelEvaluator.evaluate_predictions_file(preds_p)
    assert res["total_windows"] == 4
    assert res["total_subjects"] == 2
    assert res["pooled_metrics"]["mae_bpm"] == 1.25
    assert res["pooled_metrics"]["within_3bpm_pct"] == 100.0

    # Model comparison test
    comp = ModelEvaluator.compare_models(
        preds_model_a=np.array([61.0, 64.0, 72.0, 74.0]),
        preds_model_b=np.array([62.0, 66.0, 73.0, 76.0]),
        y_true=np.array([60.0, 65.0, 70.0, 75.0]),
        model_a_name="KAN",
        model_b_name="MLP",
    )
    assert comp["mae_model_a"] == 1.25
    assert comp["mae_model_b"] == 1.75
    assert comp["sample_count"] == 4
