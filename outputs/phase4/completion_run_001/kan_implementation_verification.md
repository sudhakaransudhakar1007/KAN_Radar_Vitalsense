# PHASE 4D: KAN IMPLEMENTATION VERIFICATION & REPRODUCIBILITY AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 2: KAN Verification  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. Mathematical Authenticity of B-Spline Functions

The Kolmogorov-Arnold Network implementation in `src/kan/kan_layer.py` was verified against the theoretical formulation:
1. **Cox-de Boor Recurrence Relation:**
   The layer evaluates piecewise polynomial B-spline basis functions of order $k=3$ (degree 3, cubic splines) over a uniform knot grid $G=5$ across $[-1.0, 1.0]$. The extended knot vector comprises:
   $$N_{\text{knots}} = G + 2k + 1 = 5 + 6 + 1 = \mathbf{12\text{ knots}}$$
   The knot vector spans $[-2.2, 2.2]$ with uniform spacing $h = 0.4$. The number of active basis splines per 1D univariate function is:
   $$N_{\text{splines}} = N_{\text{knots}} - (k + 1) = 12 - 4 = \mathbf{8\text{ basis splines}}$$
2. **Trainable Spline Parameterization:**
   The univariate activation $\phi_{j, i}(x_i)$ on each edge between input $i$ and output $j$ is parameterized by:
   $$\phi_{j, i}(x_i) = w_{b, j, i} \cdot \text{SiLU}(x_i) + w_{s, j, i} \sum_{m=0}^{7} c_{j, i, m} B_m(x_i)$$
   - Spline coefficients `spline_coeffs`: 3D tensor of shape $(\text{out\_features}, \text{in\_features}, 8)$.
   - Base linear weights `w_base`: 2D tensor of shape $(\text{out\_features}, \text{in\_features})$.
   - Spline scaling weights `w_spline`: 2D tensor of shape $(\text{out\_features}, \text{in\_features})$.
3. **Genuine KAN Confirmation:**
   The implementation replaces static fixed activations with learnable univariate spline curves on edges, summed at nodes. It is an authentic KAN layer, not a dense MLP mislabeled as KAN.

---

## 2. Forward and Backward Passes, Gradients & Shapes

The KAN architecture was tested for numerical stability, backward gradient flow, and shape preservation:

### A. Tensor Shape Progression:
- **`KANFeatureRegressor` (Pure KAN Head):**
  - Input: $(B, 16)$
  - Layer 1 (`KANLayer`, $16 \to 8$): $(B, 8)$
  - Layer 2 (`KANLayer`, $8 \to 1$): $(B, 1)$
  - Output (Squeezed): $(B,)$
  - Parameters: $(8 \times 16 \times 8 + 8 \times 16 + 8 \times 16) + (1 \times 8 \times 8 + 1 \times 8 + 1 \times 8) = 1,280 + 80 = \mathbf{1,360\text{ parameters}}$.
- **`KANRegressor` (End-to-End Network):**
  - Input: $(B, 3333)$ or $(B, 3333, 1)$
  - Conv1D Backbone: $(B, 3333, 1) \to (B, 16)$ (3,360 parameters)
  - KAN Head: $(B, 16) \to (B,)$ (1,360 parameters)
  - Total Trainable Parameters: $3,360 + 1,360 = \mathbf{4,720\text{ parameters}}$.

### B. Finite Gradients & Backpropagation:
- A forward and backward pass was executed on a batch of synthetic inputs with Huber and MSE losses.
- All gradients with respect to `spline_coeffs`, `w_base`, `w_spline`, and the convolutional backbone were strictly finite (no NaNs, no Infs).
- All gradients had non-zero magnitudes ($> 10^{-12}$), confirming active backpropagation through all spline basis functions.

### C. Determinism Under Fixed Seeds:
- Two independent model initializations and synthetic training runs with fixed seed ($42$) produced identical loss trajectories and identical prediction outputs to 6 decimal places.

### D. Invalid Input Handling:
- Passing non-finite inputs (NaN or Inf) triggers TensorFlow assertion checks (`tf.debugging.check_numerics`).
- Passing mismatched tensor dimensions triggers explicit shape validation errors.
