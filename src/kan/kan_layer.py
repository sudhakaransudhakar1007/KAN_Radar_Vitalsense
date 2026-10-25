"""Kolmogorov-Arnold Network (KAN) Layer implementation with B-spline basis functions.

Implements univariate spline activations on edges as formulated by Liu et al. (2024):
    phi_{j, i}(x_i) = w_{b, j, i} * SiLU(x_i) + w_{s, j, i} * sum_m (c_{j, i, m} * B_{m, k}(x_i))
    y_j = sum_{i=1}^{d_in} phi_{j, i}(x_i)
"""

from __future__ import annotations

import os
import tempfile
from typing import Optional, Tuple

import numpy as np

# Configure non-interactive tempdir for libraries
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def evaluate_b_splines(
    x: tf.Tensor,
    grid: tf.Tensor,
    spline_order: int = 3,
) -> tf.Tensor:
    """Compute Cox-de Boor B-spline basis functions over a uniform grid.

    Args:
        x: Input tensor of shape (batch_size, in_features).
        grid: 1D grid tensor of knot locations of shape (num_knots,).
        spline_order: Degree k of B-splines (default k=3 for cubic splines).

    Returns:
        Basis tensor of shape (batch_size, in_features, num_splines).
    """
    # x shape: (B, D, 1)
    x_exp = tf.expand_dims(x, axis=-1)
    grid_exp = tf.reshape(grid, [1, 1, -1])

    # Degree 0: indicator function for knot intervals [g_i, g_{i+1})
    bases = tf.cast(
        (x_exp >= grid_exp[:, :, :-1]) & (x_exp < grid_exp[:, :, 1:]),
        dtype=tf.float32,
    )

    # Cox-de Boor recursion for degrees 1 to spline_order
    for p in range(1, spline_order + 1):
        left_denom = grid_exp[:, :, p:-1] - grid_exp[:, :, :-(p + 1)] + 1e-8
        left_term = ((x_exp - grid_exp[:, :, :-(p + 1)]) / left_denom) * bases[:, :, :-1]

        right_denom = grid_exp[:, :, (p + 1):] - grid_exp[:, :, 1:-p] + 1e-8
        right_term = ((grid_exp[:, :, (p + 1):] - x_exp) / right_denom) * bases[:, :, 1:]

        bases = left_term + right_term

    return bases


class KANLayer(layers.Layer):
    """Production Kolmogorov-Arnold Network (KAN) Layer in Keras/TensorFlow.

    Replaces fixed matrix multiplication and static activations with learnable
    univariate spline functions on every input-output connection.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        grid_size: int = 5,
        spline_order: int = 3,
        grid_range: Tuple[float, float] = (-1.0, 1.0),
        base_activation: str = "silu",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.in_features = in_features
        self.out_features = out_features
        self.grid_size = grid_size
        self.spline_order = spline_order
        self.grid_range = grid_range
        self.base_activation_name = base_activation

        # Construct extended uniform knot vector
        h = (grid_range[1] - grid_range[0]) / float(grid_size)
        knots = np.linspace(
            grid_range[0] - spline_order * h,
            grid_range[1] + spline_order * h,
            grid_size + 2 * spline_order + 1,
            dtype=np.float32,
        )
        self.grid = tf.constant(knots, dtype=tf.float32)
        self.num_splines = len(knots) - (spline_order + 1)

    def build(self, input_shape):
        """Initialize trainable base weights, spline scales, and spline coefficients."""
        # Base linear weights: (out_features, in_features)
        init_wb = keras.initializers.GlorotUniform()
        self.w_base = self.add_weight(
            name="w_base",
            shape=(self.out_features, self.in_features),
            initializer=init_wb,
            trainable=True,
        )

        # Spline scaling parameter: (out_features, in_features)
        init_ws = keras.initializers.Ones()
        self.w_spline = self.add_weight(
            name="w_spline",
            shape=(self.out_features, self.in_features),
            initializer=init_ws,
            trainable=True,
        )

        # B-spline basis coefficients: (out_features, in_features, num_splines)
        init_c = keras.initializers.RandomNormal(mean=0.0, stddev=0.1)
        self.spline_coeffs = self.add_weight(
            name="spline_coeffs",
            shape=(self.out_features, self.in_features, self.num_splines),
            initializer=init_c,
            trainable=True,
        )

        super().build(input_shape)

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        """Forward pass of KAN layer: y_j = sum_i [w_b * SiLU(x_i) + w_s * sum_m (c_m * B_m(x_i))]."""
        # 1. Base activation term: SiLU(x) = x * sigmoid(x)
        if self.base_activation_name == "silu":
            base_out = inputs * tf.sigmoid(inputs)
        else:
            base_out = tf.nn.relu(inputs)

        # Base linear mapping: (B, in_feat) x (in_feat, out_feat) -> (B, out_feat)
        y_base = tf.matmul(base_out, tf.transpose(self.w_base))

        # 2. B-spline basis evaluation: (B, in_feat, num_splines)
        # Clamp inputs to grid range to avoid boundary extrapolation divergence
        x_clamped = tf.clip_by_value(inputs, self.grid_range[0], self.grid_range[1])
        bases = evaluate_b_splines(x_clamped, self.grid, self.spline_order)

        # Spline contraction over basis coefficients:
        # bases: (B, in_feat, num_splines)
        # spline_coeffs: (out_feat, in_feat, num_splines)
        # einsum 'bin,oin->boi' computes the evaluated univariate splines for each edge
        spline_val = tf.einsum("bin,oin->boi", bases, self.spline_coeffs)

        # Scale by w_spline and sum across input features:
        # spline_val * w_spline: (B, out_feat, in_feat)
        y_spline = tf.reduce_sum(spline_val * tf.expand_dims(self.w_spline, axis=0), axis=-1)

        # 3. Total layer output: (B, out_features)
        return y_base + y_spline

    def get_config(self):
        config = super().get_config()
        config.update({
            "in_features": self.in_features,
            "out_features": self.out_features,
            "grid_size": self.grid_size,
            "spline_order": self.spline_order,
            "grid_range": self.grid_range,
            "base_activation": self.base_activation_name,
        })
        return config
