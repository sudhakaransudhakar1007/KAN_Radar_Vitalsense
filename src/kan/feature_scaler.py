"""Feature scaling and normalization utilities for radar feature tensors.

Enforces:
1. Strict fitting ONLY on inner-training subjects (zero validation or test leakage).
2. Serialization of fitted mean and scale parameters to JSON.
3. Numerical stability guards against zero or near-zero variance.
4. Runtime dimension validation and non-finite value checks.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np


@dataclass
class ScalerState:
    """State record of fitted feature scaler parameters."""
    scaling_type: str
    feature_dim: int
    mean: List[float]
    scale: List[float]
    sample_count: int
    is_fitted: bool


class FeatureScaler:
    """Feature normalizer fitted strictly on training fold features."""

    def __init__(
        self,
        scaling_type: str = "standard",
        min_scale_threshold: float = 1e-6,
    ):
        """Initialize FeatureScaler.

        Args:
            scaling_type: "standard" (zero mean, unit variance) or "minmax" ([0, 1]).
            min_scale_threshold: Lower bound for divisor to prevent division by zero.
        """
        if scaling_type not in {"standard", "minmax", "none"}:
            raise ValueError(f"Unsupported scaling_type: '{scaling_type}'. Must be 'standard', 'minmax', or 'none'.")
        self.scaling_type = scaling_type
        self.min_scale_threshold = float(min_scale_threshold)
        self.mean_: Optional[np.ndarray] = None
        self.scale_: Optional[np.ndarray] = None
        self.feature_dim_: Optional[int] = None
        self.sample_count_: int = 0
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray) -> FeatureScaler:
        """Fit scaler strictly on training features.

        Args:
            X: 2D array of shape (num_samples, feature_dim).

        Returns:
            self
        """
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim != 2:
            raise ValueError(f"FeatureScaler expects 2D array (samples, features), got shape {arr.shape}")
        if arr.shape[0] == 0:
            raise ValueError("Cannot fit FeatureScaler on empty samples.")
        if arr.shape[1] == 0:
            raise ValueError("Cannot fit FeatureScaler with zero feature dimensions.")
        if np.any(~np.isfinite(arr)):
            raise ValueError("Training feature tensor contains non-finite values (NaN or Inf).")

        self.sample_count_ = arr.shape[0]
        self.feature_dim_ = arr.shape[1]

        if self.scaling_type == "none":
            self.mean_ = np.zeros(self.feature_dim_, dtype=np.float64)
            self.scale_ = np.ones(self.feature_dim_, dtype=np.float64)
        elif self.scaling_type == "standard":
            mean = np.mean(arr, axis=0)
            std = np.std(arr, axis=0)
            # Guard against zero or near-zero variance
            scale = np.where(std < self.min_scale_threshold, 1.0, std)
            self.mean_ = mean
            self.scale_ = scale
        elif self.scaling_type == "minmax":
            min_val = np.min(arr, axis=0)
            max_val = np.max(arr, axis=0)
            diff = max_val - min_val
            scale = np.where(diff < self.min_scale_threshold, 1.0, diff)
            self.mean_ = min_val
            self.scale_ = scale

        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform features using fitted training statistics without refitting.

        Args:
            X: 2D array of shape (num_samples, feature_dim).

        Returns:
            Transformed float32 array.
        """
        if not self.is_fitted or self.mean_ is None or self.scale_ is None:
            raise RuntimeError("FeatureScaler must be fitted before transform.")

        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim != 2:
            raise ValueError(f"FeatureScaler expects 2D array, got shape {arr.shape}")
        if arr.shape[1] != self.feature_dim_:
            raise ValueError(
                f"Feature dimension mismatch: expected {self.feature_dim_}, got {arr.shape[1]}"
            )
        if np.any(~np.isfinite(arr)):
            raise ValueError("Input feature tensor contains non-finite values (NaN or Inf).")

        X_norm = (arr - self.mean_) / self.scale_
        return X_norm.astype(np.float32)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit on training features and return transformed training array."""
        return self.fit(X).transform(X)

    def inverse_transform(self, X_scaled: np.ndarray) -> np.ndarray:
        """Convert scaled features back to original scale."""
        if not self.is_fitted or self.mean_ is None or self.scale_ is None:
            raise RuntimeError("FeatureScaler must be fitted before inverse_transform.")

        arr = np.asarray(X_scaled, dtype=np.float64)
        if arr.ndim != 2:
            raise ValueError(f"FeatureScaler expects 2D array, got shape {arr.shape}")
        if arr.shape[1] != self.feature_dim_:
            raise ValueError(
                f"Feature dimension mismatch: expected {self.feature_dim_}, got {arr.shape[1]}"
            )
        if np.any(~np.isfinite(arr)):
            raise ValueError("Input feature tensor contains non-finite values (NaN or Inf).")

        return (arr * self.scale_ + self.mean_).astype(np.float64)

    def to_dict(self) -> Dict[str, Any]:
        """Convert fitted state to dictionary."""
        if not self.is_fitted or self.mean_ is None or self.scale_ is None:
            raise RuntimeError("Cannot serialize unfitted FeatureScaler.")
        return asdict(
            ScalerState(
                scaling_type=self.scaling_type,
                feature_dim=int(self.feature_dim_),
                mean=[float(v) for v in self.mean_],
                scale=[float(v) for v in self.scale_],
                sample_count=self.sample_count_,
                is_fitted=self.is_fitted,
            )
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FeatureScaler:
        """Restore scaler from dictionary."""
        scaler = cls(scaling_type=data["scaling_type"])
        scaler.feature_dim_ = int(data["feature_dim"])
        scaler.mean_ = np.array(data["mean"], dtype=np.float64)
        scaler.scale_ = np.array(data["scale"], dtype=np.float64)
        scaler.sample_count_ = int(data["sample_count"])
        scaler.is_fitted = bool(data["is_fitted"])
        return scaler

    def save_json(self, filepath: Union[str, Path]) -> Path:
        """Save fitted scaler parameters to JSON."""
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return p

    @classmethod
    def load_json(cls, filepath: Union[str, Path]) -> FeatureScaler:
        """Load fitted scaler parameters from JSON."""
        p = Path(filepath)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls.from_dict(data)
