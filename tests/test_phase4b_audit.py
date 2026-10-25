"""Unit and regression tests for Phase 4B targeted audit and training readiness review.

Tests:
1. Exact layer-by-layer tensor shapes in ConvFeatureExtractor and KANRegressor.
2. Parameter count verification for KAN (4,720) and MLP (3,505).
3. Window arithmetic verification: 3,333 window samples, 1,667 stride, 1,660 tail samples.
4. Total unique accepted windows count equals 1,029.
5. LOSO fold partitioning across all 24 subjects: zero subject leakage.
6. Constant predictor Pearson correlation fallback test.
7. Verification of all 9 Phase 4B audit run deliverables.
"""

from __future__ import annotations

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
from src.kan.loso_evaluator import LOSOEvaluator


def test_layer_by_layer_shapes():
    """Verify exact tensor shapes across all convolutional and pooling stages."""
    x = tf.zeros((2, 3333, 1), dtype=tf.float32)
    extractor = ConvFeatureExtractor(latent_dim=16)

    x1 = extractor.conv1(x)
    assert x1.shape == (2, 834, 8)
    p1 = extractor.pool1(x1)
    assert p1.shape == (2, 417, 8)
    x2 = extractor.conv2(p1)
    assert x2.shape == (2, 105, 16)
    p2 = extractor.pool2(x2)
    assert p2.shape == (2, 52, 16)
    x3 = extractor.conv3(p2)
    assert x3.shape == (2, 26, 16)
    gap = extractor.gap(x3)
    assert gap.shape == (2, 16)


def test_model_parameter_counts():
    """Verify exact trainable parameter counts for KAN and MLP."""
    kan = KANRegressor()
    kan(tf.zeros((1, 3333)))
    assert kan.count_params() == 4720

    mlp = MLPRegressor()
    mlp(tf.zeros((1, 3333)))
    assert mlp.count_params() == 3505


def test_window_arithmetic_exactness():
    """Verify exact sampling rate, window length, stride, and trailing tail."""
    fs_exact = 1000.0 / 3.0  # 333.3333333333333 Hz
    total_samples = 40000
    assert total_samples / fs_exact == 120.0

    window_samples = round(10.0 * fs_exact)
    stride_samples = round(5.0 * fs_exact)
    assert window_samples == 3333
    assert stride_samples == 1667

    # 22 windows: index 0 to 21
    last_end = 21 * stride_samples + window_samples
    assert last_end == 38340
    tail = total_samples - last_end
    assert tail == 1660
    assert tail / fs_exact == pytest.approx(4.98, abs=1e-5)


def test_accepted_manifest_uniqueness_and_count():
    """Verify exactly 1,029 unique accepted windows exist in the manifest."""
    manifest_path = Path(__file__).resolve().parent.parent / "outputs" / "supervised_dataset" / "run_001" / "accepted_window_manifest.csv"
    assert manifest_path.exists()
    df = pd.read_csv(manifest_path)
    assert len(df) == 1029
    unique_keys = df.drop_duplicates(subset=["subject_id", "condition", "window_index"])
    assert len(unique_keys) == 1029


def test_all_24_loso_folds_isolation():
    """Verify all 24 folds have 0% subject leakage and sum to 1,029 test windows."""
    evaluator = LOSOEvaluator()
    evaluator.load_manifest()
    folds = evaluator.build_loso_folds()
    assert len(folds) == 24

    total_test = 0
    for fold in folds:
        assert fold.subject_leakage_detected is False
        assert fold.train_subject_count == 23
        assert fold.train_windows + fold.test_windows == 1029
        total_test += fold.test_windows

    assert total_test == 1029


def test_constant_prediction_pearson_fallback():
    """Verify that constant predictions return r = 0.0 under the programmatic convention."""
    y_true = np.array([60.0, 70.0, 80.0, 90.0])
    y_pred_constant = np.full(4, 75.0)  # zero variance
    metrics = LOSOEvaluator.compute_metrics(y_true, y_pred_constant)
    assert metrics.pearson_r == 0.0
    assert metrics.mae_bpm == 10.0


def test_phase4b_audit_deliverables_presence():
    """Verify that all 9 required deliverable markdown files exist in outputs/phase4/audit_run_001/."""
    audit_dir = Path(__file__).resolve().parent.parent / "outputs" / "phase4" / "audit_run_001"
    required = [
        "implementation_audit_report.md",
        "synthetic_benchmark_diagnostic.md",
        "architecture_shape_audit.md",
        "window_arithmetic_audit.md",
        "loso_leakage_audit.md",
        "phase2a_readiness_review.md",
        "test_execution_record.md",
        "error_log.md",
        "final_audit_report.md",
    ]
    for filename in required:
        file_path = audit_dir / filename
        assert file_path.exists(), f"Missing Phase 4B deliverable: {filename}"
        assert file_path.stat().st_size > 0, f"Empty Phase 4B deliverable: {filename}"
