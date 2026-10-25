# PHASE 5: FEATURE PIPELINE, TARGET NORMALIZATION & TRAINING CONFIGURATION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  

---

## 1. Feature Extraction Pipeline (Task 5)

### A. Radar-Only Input Interface
- **Input Modality:** 1D radar chest-wall displacement signal ($N = 3,333\text{ samples}$, $10.0\text{ s}$ duration at $333.33\text{ Hz}$).
- **Pre-filtering:** 4th-order zero-phase Butterworth bandpass filter ($0.8 - 3.0\text{ Hz}$).
- **ECG Isolation:** ECG data is strictly quarantined and used exclusively as reference target labels ($\text{HR}_{\text{ref}}$) and evaluation metadata. Zero ECG-derived values enter the feature pipeline.

### B. Feature Extractor Architecture (`ConvFeatureExtractor`)
- **Class:** `ConvFeatureExtractor` (`src.kan.kan_model.py`)
- **Layer Breakdown:**
  1. `Conv1D(8, kernel=15, stride=4, padding="same", activation="silu")` $\to (834, 8)$
  2. `MaxPooling1D(pool_size=2)` $\to (417, 8)$
  3. `Conv1D(16, kernel=11, stride=4, padding="same", activation="silu")` $\to (105, 16)$
  4. `MaxPooling1D(pool_size=2)` $\to (52, 16)$
  5. `Conv1D(16, kernel=7, stride=2, padding="same", activation="silu")` $\to (26, 16)$
  6. `GlobalAveragePooling1D()` $\to (16,)$
- **Trainable Parameters:** 3,360 parameters.
- **Latent Feature Nomenclature:** Neutral names `latent_feat_00` through `latent_feat_15` are enforced. In strict adherence to Task 5, no unverified physiological labels (such as "cardiac ejection peak" or "respiratory harmonic") are assigned without formal ablation evidence.

---

## 2. Fold-Specific Target Normalization & Initialization (Task 6)

### A. Target Z-Score Standardization
Target normalization is governed by `TargetNormalizer` (`src.kan.normalization.py`):
$$y_{\text{norm}} = \frac{y_{\text{BPM}} - \mu_{y,\text{train}}}{\sigma_{y,\text{train}}}$$
- **Training-Only Fitting:** $\mu_{y,\text{train}}$ and $\sigma_{y,\text{train}}$ are computed strictly from the 20 training subjects in fold $k$.
- **Validation and Test Isolation:** Validation and test targets are transformed using $\mu_{y,\text{train}}$ and $\sigma_{y,\text{train}}$ without refitting.
- **Zero-Variance Guard:** If $\sigma_{y,\text{train}} < 1.0 \times 10^{-6}$, $\sigma$ is pinned to $1.0$ to prevent division by zero.

### B. Physical BPM Inversion & Metric Calculation
Model outputs are converted back to physical heart rate units prior to metric computation:
$$\hat{y}_{\text{BPM}} = \hat{y}_{\text{norm}} \cdot \sigma_{y,\text{train}} + \mu_{y,\text{train}}$$
All biomedical evaluation metrics (MAE, RMSE, bias, error tolerance percentages) are calculated strictly in physical BPM.

### C. Output Bias Initialization
When training on standardized targets ($\mu = 0.0, \sigma = 1.0$), the output bias is initialized to $0.0$, preserving zero-mean gradient symmetry without leaking validation or test statistics.

---

## 3. Proposed KAN Model Specifications (Task 7)

- **Model Class:** `KANRegressor` (`src.kan.kan_model.py`)
- **Input Dimension:** $3,333$ raw samples (or $16$ pre-extracted features via dual interface).
- **Latent Dimension:** $16$ features.
- **KAN Regression Head:** `KANFeatureRegressor(in_features=16, hidden_dim=8)`
  - Layer 1: `KANLayer(16, 8, grid_size=5, spline_order=3)`
  - Layer 2: `KANLayer(8, 1, grid_size=5, spline_order=3)`
- **Spline Topology:**
  - B-spline degree: $k = 3$ (cubic B-splines)
  - Knot intervals: $G = 5$ ($G + k = 8$ basis functions per edge)
  - Knot grid range: $[-1.0, 1.0]$ with static grid evaluation
  - Base activation: $\text{SiLU}(x) = x \cdot \sigma(x)$
- **Trainable Parameters:** **4,720** parameters (3,360 Conv backbone + 1,360 KAN head).

---

## 4. Optimization Hyperparameters & Checkpoint Protocol

| Hyperparameter | Value | Scientific Rationale |
| :--- | :--- | :--- |
| **Loss Function** | Mean Squared Error (MSE) | Convex quadratic penalty on standardized target space |
| **Optimizer** | Adam ($\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$) | Adaptive moment estimation for spline and linear weights |
| **Learning Rate** | $1.0 \times 10^{-3}$ ($0.001$) | Stable learning rate for Cox-de Boor B-splines |
| **Weight Decay** | $1.0 \times 10^{-4}$ ($0.0001$) | $L_2$ regularization on spline basis coefficients |
| **Batch Size** | 16 | Balanced gradient variance across heterogeneous subjects |
| **Maximum Epochs** | 30 | Upper boundary for subject convergence |
| **Early Stopping Metric** | Validation MSE | Monitored exclusively on the 3 deterministic validation subjects |
| **Early Stopping Patience**| 7 epochs | Halts training upon validation plateau |
| **Checkpoint Rule** | Minimum Validation MSE | Checkpoint restored prior to held-out test evaluation |
| **Random Seed** | 42 | Fixed for `numpy`, `tensorflow`, and `random` |
