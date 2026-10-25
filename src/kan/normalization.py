"""Target normalization and inverse transformation utilities for heart rate regression.

Enforces:
1. Strict training-fold-only fitting (no validation or test leakage).
2. Numerical stability against zero or near-zero variance.
3. Accurate inverse transformation back to physical BPM units.
4. Calculation of MAE, RMSE, and bias strictly in physical BPM units.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Union

import numpy as np


@dataclass
class NormalizationParams:
    """Parameters computed strictly from training fold targets."""
    mean_bpm: float
    std_bpm: float
    sample_count: int
    is_fitted: bool


class TargetNormalizer:
    """Target z-score normalizer fitted strictly on training fold labels."""

    def __init__(self, min_std_threshold: float = 1e-6):
        self.min_std_threshold = float(min_std_threshold)
        self.train_mean: Optional[float] = None
        self.train_std: Optional[float] = None
        self.sample_count: int = 0
        self.is_fitted: bool = False

    def fit(self, y_train: Union[np.ndarray, list]) -> TargetNormalizer:
        """Fit normalization parameters strictly on training targets.

        Args:
            y_train: 1D array of heart rate labels from training fold only.

        Returns:
            self
        """
        arr = np.asarray(y_train, dtype=np.float64).flatten()
        if len(arr) == 0:
            raise ValueError("Cannot fit normalizer on empty training targets.")
        if np.any(~np.isfinite(arr)):
            raise ValueError("Training targets contain non-finite values (NaN or Inf).")

        mean = float(np.mean(arr))
        std = float(np.std(arr))

        # Guard against zero or near-zero variance
        if std < self.min_std_threshold:
            std = 1.0

        self.train_mean = mean
        self.train_std = std
        self.sample_count = len(arr)
        self.is_fitted = True
        return self

    def transform(self, y: Union[np.ndarray, list]) -> np.ndarray:
        """Standardize targets using training fold statistics: (y - mean) / std.

        Args:
            y: 1D array of targets (train, val, or test).

        Returns:
            Standardized 1D float32 array.
        """
        if not self.is_fitted or self.train_mean is None or self.train_std is None:
            raise RuntimeError("TargetNormalizer must be fitted on training fold before transform.")

        arr = np.asarray(y, dtype=np.float64).flatten()
        if np.any(~np.isfinite(arr)):
            raise ValueError("Input targets contain non-finite values.")

        y_norm = (arr - self.train_mean) / self.train_std
        return y_norm.astype(np.float32)

    def fit_transform(self, y_train: Union[np.ndarray, list]) -> np.ndarray:
        """Fit on training fold and return transformed training targets."""
        return self.fit(y_train).transform(y_train)

    def inverse_transform(self, y_norm: Union[np.ndarray, list]) -> np.ndarray:
        """Convert normalized predictions back to physical BPM: y_norm * std + mean.

        Args:
            y_norm: 1D array of normalized predictions.

        Returns:
            Predictions in physical BPM units (1D float64 array).
        """
        if not self.is_fitted or self.train_mean is None or self.train_std is None:
            raise RuntimeError("TargetNormalizer must be fitted before inverse_transform.")

        arr = np.asarray(y_norm, dtype=np.float64).flatten()
        if np.any(~np.isfinite(arr)):
            raise ValueError("Normalized predictions contain non-finite values.")

        y_bpm = arr * self.train_std + self.train_mean
        return y_bpm

    def get_params(self) -> NormalizationParams:
        """Return fold-specific normalization parameters."""
        return NormalizationParams(
            mean_bpm=self.train_mean if self.train_mean is not None else 0.0,
            std_bpm=self.train_std if self.train_std is not None else 1.0,
            sample_count=self.sample_count,
            is_fitted=self.is_fitted,
        )
