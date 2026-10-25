# PHASE 4: MODEL ARCHITECTURE SUMMARY & CAPACITY ANALYSIS

## 1. Architectural Motivation & Dimensionality Management
Connecting raw 10-second radar windows ($N = 3,333$ samples) directly into a Kolmogorov-Arnold Network (KAN) would cause extreme parameter explosion. A direct KAN layer with $3,333$ inputs, 16 outputs, grid size 5, and spline order 3 would require:
$$\text{Spline Weights} = 3333 \times 16 \times (5 + 3) = 426,624 \text{ parameters}$$
Given that the dataset contains 1,029 accepted windows, a model with $>400,000$ parameters would overfit catastrophically.

To prevent this, we employ a compact **1D Convolutional Feature Extractor** to downsample the cardiac Doppler signal to 16 latent physiological representations, followed by a 2-layer B-spline KAN regressor.

## 2. KAN Regressor Architecture (`KANRegressor`)
- **Stage 1: Conv1D Cardiac Feature Extractor**
  - Layer 1: Conv1D(filters=8, kernel=15, stride=4, padding='same', activation='silu') $\to$ MaxPool1D(2)
  - Layer 2: Conv1D(filters=16, kernel=11, stride=4, padding='same', activation='silu') $\to$ MaxPool1D(2)
  - Layer 3: Conv1D(filters=16, kernel=7, stride=2, padding='same', activation='silu')
  - GlobalAveragePooling1D $\to$ Latent vector $\mathbf{z} \in \mathbb{R}^{16}$
- **Stage 2: Differentiable B-Spline KAN Regressor**
  - Layer 1: `KANLayer(in_features=16, out_features=8, grid_size=5, spline_order=3)`
    - Cox-de Boor B-spline basis functions of degree $k=3$
    - Trainable spline coefficients: $16 \times 8 \times 8 = 1,024$
    - Trainable base linear weights: $16 \times 8 = 128$
    - Trainable spline scale weights: $16 \times 8 = 128$
  - Layer 2: `KANLayer(in_features=8, out_features=1, grid_size=5, spline_order=3)`
    - Trainable spline coefficients: $8 \times 1 \times 8 = 64$
    - Trainable base linear weights: $8 \times 1 = 8$
    - Trainable spline scale weights: $8 \times 1 = 8$
- **Total KAN Regressor Parameters:** 4,720

## 3. Comparative Baseline Architectures
1. **`MLPRegressor` (Controlled Deep Baseline):**
   - Identical Conv1D Feature Extractor (16 latent features)
   - Dense Layer 1: 16 $\to$ 8 (SiLU activation)
   - Dense Layer 2: 8 $\to$ 1 (Linear output)
   - Total Parameters: 3,505
2. **`MeanPredictorBaseline` (Non-Parametric Benchmark):**
   - Fits training fold mean heart rate $\bar{y}_{\text{train}}$
   - Predicts $\hat{y} = \bar{y}_{\text{train}}$ for all test windows
   - Zero learned parameters; establishes the absolute lower performance bound.
