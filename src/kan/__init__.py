"""Kolmogorov-Arnold Network (KAN) regression framework for radar heart-rate estimation.

Implements B-spline KAN layers, baseline comparative models, and Leave-One-Subject-Out (LOSO)
cross-validation evaluation protocols.
"""

from __future__ import annotations

from src.kan.evaluator import ModelEvaluator
from src.kan.feature_scaler import FeatureScaler
from src.kan.kan_layer import KANLayer
from src.kan.kan_model import KANRegressor, MLPRegressor, MeanPredictorBaseline
from src.kan.loso_evaluator import LOSOEvaluator, GateBlockerError
from src.kan.trainer import KANTrainer, TrainingConfig

__all__ = [
    "FeatureScaler",
    "KANLayer",
    "KANRegressor",
    "MLPRegressor",
    "MeanPredictorBaseline",
    "LOSOEvaluator",
    "GateBlockerError",
    "KANTrainer",
    "TrainingConfig",
    "ModelEvaluator",
]
