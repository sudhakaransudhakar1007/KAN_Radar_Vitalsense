# PHASE 4C: ARCHITECTURE & KAN MATHEMATICS RE-VERIFICATION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Verification Stage:** Phase 4C — Model Architecture and Spline Formulation Review  
**Verification File:** `outputs/phase4/verification_run_001/architecture_reverification.md`  

---

## 1. Line-by-Line Code Inspection of `src/kan/kan_layer.py`

The implementation of `KANLayer` in `src/kan/kan_layer.py` was re-verified against the original mathematical formulation of Kolmogorov-Arnold Networks (Liu et al., 2024):

### A. Extended Uniform Knot Vector (`self.grid`):
- Grid range: $[-1.0, 1.0]$.
- Grid intervals: $G = 5$.
- Spline degree: $k = 3$ (cubic B-splines).
- Grid spacing: $h = \frac{1.0 - (-1.0)}{5} = 0.4$.
- Knot vector definition (lines 86–94):
  $$\text{knots} = \text{linspace}(-1.0 - 3(0.4), 1.0 + 3(0.4), 5 + 2(3) + 1) = \text{linspace}(-2.2, 2.2, 12)$$
- Verified total knot count: $N_{\text{knots}} = 12$.
- Number of basis splines: $N_{\text{splines}} = N_{\text{knots}} - (k + 1) = 12 - 4 = \mathbf{8\text{ splines}}$.

### B. Recursive Cox-de Boor Algorithm (`evaluate_b_splines`, lines 26–58):
- **Degree 0 Basis:**
  Evaluated using strict half-open interval indicator functions:
  $$B_{i, 0}(x) = \begin{cases} 1 & \text{if } t_i \le x < t_{i+1} \\ 0 & \text{otherwise} \end{cases}$$
- **Degrees 1, 2, 3 Recursion:**
  Implements the recursive Cox-de Boor formula with numerical stability epsilon ($\epsilon = 10^{-8}$):
  $$B_{i, p}(x) = \frac{x - t_i}{t_{i+p} - t_i + \epsilon} B_{i, p-1}(x) + \frac{t_{i+p+1} - x}{t_{i+p+1} - t_{i+1} + \epsilon} B_{i+1, p-1}(x)$$
- Verified: Computes exact cubic B-spline basis functions for each input feature.

### C. Layer Transformation and Learnable Weights:
For input vector $\mathbf{x} \in \mathbb{R}^{\text{in}}$, the $j$-th output neuron computes:
$$y_j = \sum_{i=1}^{\text{in}} \left[ w_{b, j, i} \cdot \text{SiLU}(x_i) + w_{s, j, i} \sum_{m=0}^{7} c_{j, i, m} B_m(x_i) \right]$$
- `w_base` ($\mathbf{W}_b$): Shape $(\text{out}, \text{in})$ — residual linear weights with SiLU activation.
- `w_spline` ($\mathbf{W}_s$): Shape $(\text{out}, \text{in})$ — trainable spline scale weights.
- `spline_coeffs` ($\mathbf{C}$): Shape $(\text{out}, \text{in}, 8)$ — trainable B-spline coefficients.

**Auditor Conclusion:** The layer is an **authentic, fully differentiable Kolmogorov-Arnold Network layer**. It does not substitute dense matrices or static non-linearities for the spline evaluations.

---

## 2. Re-Verification of Tensor Shapes and Parameters

An empirical execution with input tensor shape $(2, 3333, 1)$ re-verified the exact shapes and parameter counts:

```
Input Radar Window:                          (2, 3333, 1)
  │
  ├──► Conv1D (8 filters, k=15, s=4, same):  (2, 834, 8)     [Params: (15*1*8) + 8 = 128]
  ├──► MaxPool1D (pool=2, stride=2):         (2, 417, 8)     [Params: 0]
  ├──► Conv1D (16 filters, k=11, s=4, same): (2, 105, 16)    [Params: (11*8*16) + 16 = 1,424]
  ├──► MaxPool1D (pool=2, stride=2):         (2, 52, 16)     [Params: 0]
  ├──► Conv1D (16 filters, k=7, s=2, same):  (2, 26, 16)     [Params: (7*16*16) + 16 = 1,808]
  ├──► GlobalAveragePooling1D:               (2, 16)         [Params: 0]
  │                                                           [Conv Feature Extractor Subtotal: 3,360]
  │
  ├──► KANLayer 1 (16 in -> 8 out, k=3, G=5):(2, 8)          [Splines: 8*16*8 = 1,024; Base: 128; Scale: 128 = 1,280]
  ├──► KANLayer 2 (8 in -> 1 out, k=3, G=5): (2, 1)          [Splines: 1*8*8 = 64; Base: 8; Scale: 8 = 80]
  └──► Squeeze (axis=-1):                    (2,)            [Total KANRegressor Trainable Params: 4,720]
```

### Parameter Breakdown Comparison:
| Model Component | Parameter Dimension | Trainable Count | Verification Status |
| :--- | :--- | :---: | :---: |
| **Conv1D Stage 1** | $15 \times 1 \times 8 + 8$ | 128 | **VERIFIED** |
| **Conv1D Stage 2** | $11 \times 8 \times 16 + 16$ | 1,424 | **VERIFIED** |
| **Conv1D Stage 3** | $7 \times 16 \times 16 + 16$ | 1,808 | **VERIFIED** |
| **KANLayer 1 Splines** | $8 \times 16 \times 8$ | 1,024 | **VERIFIED** |
| **KANLayer 1 Base Weights** | $8 \times 16$ | 128 | **VERIFIED** |
| **KANLayer 1 Scale Weights**| $8 \times 16$ | 128 | **VERIFIED** |
| **KANLayer 2 Splines** | $1 \times 8 \times 8$ | 64 | **VERIFIED** |
| **KANLayer 2 Base Weights** | $1 \times 8$ | 8 | **VERIFIED** |
| **KANLayer 2 Scale Weights**| $1 \times 8$ | 8 | **VERIFIED** |
| **Total `KANRegressor`** | — | **4,720** | **VERIFIED** |
| **Total `MLPRegressor`** | $3,360 + (16 \times 8 + 8) + (8 \times 1 + 1)$ | **3,505** | **VERIFIED** |
| **Total `MeanPredictorBaseline`** | Non-parametric | **0** | **VERIFIED** |

---

## 3. Discrepancy Reconciliation Summary

1. **Inline Comment Rounding:** The informal inline comments stating `833` and `104` were confirmed to be integer division approximations ($3333 // 4 = 833$). The actual TensorFlow `"same"` padding graph uses ceiling division ($\lceil 3333/4 \rceil = 834$).
2. **Dimension Flow:** The graph reduces 3,333 radar samples to 16 latent cardiac features, avoiding spline parameter explosion ($426,624$ parameters for a direct KAN vs. $4,720$ parameters for the implemented Conv-KAN).
