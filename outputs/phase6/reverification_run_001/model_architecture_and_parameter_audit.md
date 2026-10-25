# PHASE 6: MODEL ARCHITECTURES, TENSOR SHAPES & PARAMETER AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Scientific ML Auditor & Python/TensorFlow Reviewer  

---

## 1. Executive Summary

In compliance with Phase 6 Task 5, an independent mathematical and software audit of the proposed Kolmogorov–Arnold Network (KAN) and comparison baseline architectures was conducted. Trainable parameter counts, layer-by-layer tensor shapes, weight matrices, and input/output interfaces were independently computed and verified directly from source code.

This audit definitively resolves the historical reporting discrepancy regarding CNN parameter counts (3,360 vs. 3,377) and confirms that all models exhibit valid gradient interfaces, dual-input compatibility, and strict feature isolation from ECG ground truth.

---

## 2. Independent Model Parameter Count Audit

The exact parameter counts were computed by instantiating each model and inspecting its trainable variables:

| Model / Subsystem Class | Architectural Components | Input Dimension | Output Dimension | Trainable Parameters | Float32 Weight Memory |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`ConvFeatureExtractor`** | 3 Conv1D layers + MaxPool + GAP | $(B, 3333, 1)$ | $(B, 16)$ | **3,360** | **$13.44\text{ KB}$** |
| **`CNNRegressor`** | `ConvFeatureExtractor` + `Dense(1)` | $(B, 3333)$ / $(B, 16)$ | $(B,)$ | **3,377** | **$13.51\text{ KB}$** |
| **`KANFeatureRegressor`** | 2-layer B-spline KAN (`[16, 8, 1]`) | $(B, 16)$ | $(B,)$ | **1,360** | **$5.44\text{ KB}$** |
| **`KANRegressor`** (Proposed) | Backbone (3,360) + KAN head (1,360) | $(B, 3333)$ / $(B, 16)$ | $(B,)$ | **4,720** | **$18.88\text{ KB}$** |
| **`MLPRegressor`** (Baseline) | Backbone (3,360) + Dense head (145) | $(B, 3333)$ / $(B, 16)$ | $(B,)$ | **3,505** | **$14.02\text{ KB}$** |
| **`MeanPredictorBaseline`** | Non-parametric training mean | N/A | $(B,)$ | **0** | **$0.00\text{ KB}$** |
| **`TargetNormalizer`** | Target Z-score standardization | $(N,)$ | $(N,)$ | **0** | **$0.00\text{ KB}$** |

---

## 3. Resolution of the CNN Parameter Discrepancy (3,360 vs. 3,377)

Task 5 instructed:
> *"Investigate the reported CNN discrepancy: Feature-extraction backbone: 3,360 parameters; CNN model with linear readout: 3,377 parameters. Determine whether these numbers refer to different components or whether an actual inconsistency exists."*

### Authoritative Finding:
The audit proves that **no inconsistency exists**. The two reported numbers refer to distinct, hierarchical components of the model codebase:
1. **The Convolutional Backbone (`ConvFeatureExtractor`):**
   - Layer 1 (`Conv1D`): $15 \times 1 \times 8 \text{ (kernel)} + 8 \text{ (bias)} = 128$
   - Layer 2 (`Conv1D`): $11 \times 8 \times 16 \text{ (kernel)} + 16 \text{ (bias)} = 1,424$
   - Layer 3 (`Conv1D`): $7 \times 16 \times 16 \text{ (kernel)} + 16 \text{ (bias)} = 1,808$
   - **Total Backbone Parameters:** $128 + 1,424 + 1,808 = \mathbf{3,360\text{ parameters}}$.
2. **The Full CNN Model (`CNNRegressor`):**
   - Incorporates the `ConvFeatureExtractor` backbone ($3,360$ parameters).
   - Plus a linear regression readout layer (`Dense(1)`): $16 \times 1 \text{ (weights)} + 1 \text{ (bias)} = 17$ parameters.
   - **Total `CNNRegressor` Parameters:** $3,360 + 17 = \mathbf{3,377\text{ parameters}}$.

The historical reports were accurate; however, prior narrative summaries occasionally cited 3,360 as the "CNN backbone parameter count" and 3,377 as the "total CNN model parameter count" without clearly distinguishing the sub-layer from the full model.

---

## 4. KAN B-Spline Implementation & Mathematical Formulation

Inspection of `src/kan/kan_layer.py` confirms authentic, publication-grade implementation of Kolmogorov–Arnold Network layers (Liu et al., 2024):
1. **Cox-de Boor B-Spline Basis Recursion (`evaluate_b_splines`):**
   - Basis order: $k = 3$ (cubic B-splines).
   - Uniform knot vector: $G = 5$ intervals over $[-1.0, 1.0]$.
   - Extended knot vector length: $G + 2k + 1 = 12$ knots.
   - Number of spline basis functions per edge: $12 - (3 + 1) = 8$ basis functions.
2. **Edge Activation Formula:**
   $$\phi_{j, i}(x_i) = w_{b, j, i} \cdot \text{SiLU}(x_i) + w_{s, j, i} \cdot \sum_{m=1}^8 c_{j, i, m} B_{m, 3}(x_i)$$
   where $w_b$ is a base linear weight, $w_s$ is a spline scale factor, and $c_{j, i, m}$ are learnable spline basis coefficients.
3. **Layer Tensor Contraction:**
   Implemented via optimized tensor contraction:
   ```python
   spline_val = tf.einsum("bin,oin->boi", bases, self.spline_coeffs)
   y_spline = tf.reduce_sum(spline_val * tf.expand_dims(self.w_spline, axis=0), axis=-1)
   return y_base + y_spline
   ```
4. **Parameter Breakdown of KAN Head (`[16, 8, 1]`):**
   - Layer 1 (`16 -> 8`): $8 \times 16 \text{ (base)} + 8 \times 16 \text{ (scale)} + 8 \times 16 \times 8 \text{ (coeffs)} = 128 + 128 + 1,024 = 1,280$
   - Layer 2 (`8 -> 1`): $1 \times 8 \text{ (base)} + 1 \times 8 \text{ (scale)} + 1 \times 8 \times 8 \text{ (coeffs)} = 8 + 8 + 64 = 80$
   - **Total KAN Head Parameters:** $1,280 + 80 = \mathbf{1,360\text{ parameters}}$.
   - **Total `KANRegressor`:** $3,360 + 1,360 = \mathbf{4,720\text{ parameters}}$.

---

## 5. Architectural Quality, Isolation & Normalization

1. **Feature Input Isolation:** All model inputs originate strictly from filtered 1D radar signals. No ECG-derived values (R-peak timestamps, instantaneous RR intervals, or monitor HR) enter the model input tensors.
2. **Dual-Input Compatibility:** Both `KANRegressor` and `CNNRegressor` support dual interfaces: they can ingest raw 3,333-sample windows or pre-extracted 16-dimensional feature representations.
3. **Target Normalization Rigor:** `TargetNormalizer` is fitted strictly on training targets ($y_{\text{train}}$) and raises runtime errors if invoked before fitting. Inverse transformation back to physical BPM ($\hat{y}_{\text{BPM}} = \hat{y}_{\text{norm}} \cdot \sigma + \mu$) is mathematically exact.
4. **Mean Predictor Baseline:** Evaluates $\mu_{y,\text{train}}$ from training folds only and handles zero prediction variance with a documented defensive convention ($r \equiv 0.0$).
