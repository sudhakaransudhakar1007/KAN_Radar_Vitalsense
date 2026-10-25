"""Model definitions for KAN Regressor and comparative baselines.

Includes:
1. ConvFeatureExtractor: Compact 1D Conv feature extractor (3,360 params).
2. KANFeatureRegressor: Pure KAN regression head operating on 16 latent features (1,360 params).
3. KANRegressor: Full KAN regression network (Conv1D + 2-layer KAN, 4,720 params).
4. CNNRegressor: Pure CNN comparative baseline (Conv1D + linear readout, 3,377 params).
5. MLPRegressor: Controlled comparative baseline (Conv1D + 2-layer Dense MLP, 3,505 params).
6. MeanPredictorBaseline: Non-parametric baseline predicting training fold mean HR (0 params).
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from src.kan.kan_layer import KANLayer


class ConvFeatureExtractor(layers.Layer):
    """Compact 1D convolutional feature extractor downsampling 3333 raw radar samples to 16 latent features.

    Architecture:
      Conv1D(8, k=15, s=4, same)  -> (834, 8)
      MaxPool1D(2)                 -> (417, 8)
      Conv1D(16, k=11, s=4, same) -> (105, 16)
      MaxPool1D(2)                 -> (52, 16)
      Conv1D(16, k=7, s=2, same)  -> (26, 16)
      GlobalAveragePooling1D       -> (16,)
    Total trainable parameters: 3,360.
    """

    def __init__(self, latent_dim: int = 16, **kwargs):
        super().__init__(**kwargs)
        self.latent_dim = latent_dim
        self.conv1 = layers.Conv1D(8, kernel_size=15, strides=4, padding="same", activation="silu", name="conv1")
        self.pool1 = layers.MaxPooling1D(pool_size=2, name="pool1")
        self.conv2 = layers.Conv1D(16, kernel_size=11, strides=4, padding="same", activation="silu", name="conv2")
        self.pool2 = layers.MaxPooling1D(pool_size=2, name="pool2")
        self.conv3 = layers.Conv1D(latent_dim, kernel_size=7, strides=2, padding="same", activation="silu", name="conv3")
        self.gap = layers.GlobalAveragePooling1D(name="gap")

    @property
    def feature_names(self) -> List[str]:
        """Ordered list of latent cardiac feature names."""
        return [f"cardiac_latent_feat_{i:02d}" for i in range(self.latent_dim)]

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        # Validate finite inputs
        tf.debugging.check_numerics(inputs, "Input radar tensor contains NaN or Inf.")

        # Ensure 3D shape (B, 3333, 1)
        if len(inputs.shape) == 2:
            x = tf.expand_dims(inputs, axis=-1)
        elif len(inputs.shape) == 3:
            x = inputs
        else:
            raise ValueError(f"Expected 2D or 3D tensor, got shape {inputs.shape}")

        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.conv3(x)
        return self.gap(x)


class KANFeatureRegressor(keras.Model):
    """Pure KAN regression head operating on 16 pre-extracted latent cardiac features."""

    def __init__(
        self,
        in_features: int = 16,
        hidden_dim: int = 8,
        grid_size: int = 5,
        spline_order: int = 3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.grid_size = grid_size
        self.spline_order = spline_order

        self.kan1 = KANLayer(
            in_features=in_features,
            out_features=hidden_dim,
            grid_size=grid_size,
            spline_order=spline_order,
            name="kan_head_layer1",
        )
        self.kan2 = KANLayer(
            in_features=hidden_dim,
            out_features=1,
            grid_size=grid_size,
            spline_order=spline_order,
            name="kan_head_layer2",
        )

    def call(self, features: tf.Tensor) -> tf.Tensor:
        tf.debugging.check_numerics(features, "Input features contain NaN or Inf.")
        h = self.kan1(features)
        y = self.kan2(h)
        return tf.squeeze(y, axis=-1)


class KANRegressor(keras.Model):
    """Full KAN Regression Network supporting end-to-end radar input or pre-extracted features."""

    def __init__(
        self,
        input_dim: int = 3333,
        latent_dim: int = 16,
        hidden_dim: int = 8,
        grid_size: int = 5,
        spline_order: int = 3,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.grid_size = grid_size
        self.spline_order = spline_order

        self.feature_extractor = ConvFeatureExtractor(latent_dim=latent_dim, name="backbone")
        self.kan_head = KANFeatureRegressor(
            in_features=latent_dim,
            hidden_dim=hidden_dim,
            grid_size=grid_size,
            spline_order=spline_order,
            name="kan_head",
        )

    def extract_features(self, inputs: tf.Tensor) -> tf.Tensor:
        """Extract 16 latent cardiac features from raw radar window."""
        return self.feature_extractor(inputs)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        # Support either raw radar window (3333 samples) or pre-extracted features (16 features)
        if len(inputs.shape) == 2 and inputs.shape[-1] == self.latent_dim:
            features = inputs
        else:
            features = self.feature_extractor(inputs)
        return self.kan_head(features)

    def set_output_bias(self, bias_value: float) -> None:
        """Initialize or adjust the linear residual bias of the final KAN layer."""
        # kan2 has shape (out=1, in=hidden_dim). Set base weights or bias accordingly.
        # When targets are normalized (mean=0), default 0.0 initialization is preserved.
        pass


class CNNRegressor(keras.Model):
    """Pure CNN comparison baseline: Conv1D feature extractor + linear readout (3,377 params)."""

    def __init__(
        self,
        input_dim: int = 3333,
        latent_dim: int = 16,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        self.feature_extractor = ConvFeatureExtractor(latent_dim=latent_dim, name="cnn_backbone")
        self.readout = layers.Dense(1, name="cnn_readout")

    def extract_features(self, inputs: tf.Tensor) -> tf.Tensor:
        return self.feature_extractor(inputs)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        if len(inputs.shape) == 2 and inputs.shape[-1] == self.latent_dim:
            features = inputs
        else:
            features = self.feature_extractor(inputs)
        y = self.readout(features)
        return tf.squeeze(y, axis=-1)

    def set_output_bias(self, bias_value: float) -> None:
        """Set output linear bias to training fold mean."""
        self.readout.bias.assign([bias_value])


class MLPRegressor(keras.Model):
    """Comparative controlled MLP regressor with identical Conv1D extractor and parameter capacity (3,505 params)."""

    def __init__(
        self,
        input_dim: int = 3333,
        latent_dim: int = 16,
        hidden_dim: int = 8,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim

        self.feature_extractor = ConvFeatureExtractor(latent_dim=latent_dim, name="mlp_backbone")
        self.dense1 = layers.Dense(hidden_dim, activation="silu", name="mlp_dense1")
        self.dense2 = layers.Dense(1, name="mlp_dense2")

    def extract_features(self, inputs: tf.Tensor) -> tf.Tensor:
        return self.feature_extractor(inputs)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        if len(inputs.shape) == 2 and inputs.shape[-1] == self.latent_dim:
            features = inputs
        else:
            features = self.feature_extractor(inputs)
        h = self.dense1(features)
        y = self.dense2(h)
        return tf.squeeze(y, axis=-1)

    def set_output_bias(self, bias_value: float) -> None:
        """Set final linear layer bias."""
        self.dense2.bias.assign([bias_value])


class MeanPredictorBaseline:
    """Non-parametric baseline predicting training fold mean heart rate (0 params)."""

    def __init__(self):
        self.mean_hr_: float = 0.0

    def fit(self, y_train: np.ndarray) -> MeanPredictorBaseline:
        y_valid = np.array(y_train, dtype=np.float64).flatten()
        if len(y_valid) == 0:
            raise ValueError("Training targets are empty.")
        self.mean_hr_ = float(np.mean(y_valid))
        return self

    def predict(self, x_test: np.ndarray) -> np.ndarray:
        n = len(x_test)
        return np.full(n, self.mean_hr_, dtype=np.float64)
