# Forensic Audit: KAN Parameter Count and Architectural Reconciliation (Contradiction B)

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Neural Network Architect, Scientific ML Reviewer, & TensorFlow Specialist  
**Artifact File:** `outputs/phase7b/run_001/kan_parameter_count_reconciliation.md`  

---

## 1. Audited Claim vs Demonstrated Empirical Truth

| Architectural Feature | Phase 7 Report Claim | Source Code & Runtime Truth (`src/kan/`) | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **KAN Head Architecture** | Single-layer $128 \rightarrow 1$ | **Two-layer KAN: $16 \rightarrow 8 \rightarrow 1$** | 🔴 **REPORTING ERROR REFUTED** |
| **Layer 1 ($16 \rightarrow 8$) Params** | Unreported | **1,280 trainable params** ($128 + 128 + 1024$) | 🟢 **VERIFIED FROM CODE** |
| **Layer 2 ($8 \rightarrow 1$) Params** | Unreported | **80 trainable params** ($8 + 8 + 64$) | 🟢 **VERIFIED FROM CODE** |
| **KAN Head Trainable Total** | Claimed $1,360$ (arithmetic gave $1,153$) | **Exactly 1,360 trainable parameters** | 🟢 **EMPIRICALLY VERIFIED** |
| **Non-Trainable Parameters** | Claimed $1,280$ "grid parameters" | **0 non-trainable parameters** | 🔴 **REPORTING ERROR REFUTED** |
| **Grid Representation** | Described as untrainable weight variable | **`tf.constant` tensor buffer (shape: 12)** | 🟢 **VERIFIED FROM CODE** |
| **Backbone Parameters** | $3,360$ | **3,360 trainable parameters** | 🟢 **EMPIRICALLY VERIFIED** |
| **Full KAN Total Parameters** | $4,720$ | **Exactly 4,720 trainable parameters** ($3360 + 1360$) | 🟢 **EMPIRICALLY VERIFIED** |

---

## 2. Source Code Architecture Inspection

### 2.1 The Two-Layer KAN Head Definition
In [`src/kan/kan_model.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L76-L107):
```python
76: class KANFeatureRegressor(keras.Model):
77:     """Pure KAN regression head operating on 16 pre-extracted latent cardiac features."""
78: 
79:     def __init__(
80:         self,
81:         in_features: int = 16,
82:         hidden_dim: int = 8,
83:         grid_size: int = 5,
84:         spline_order: int = 3,
85:         **kwargs,
86:     ):
87:         super().__init__(**kwargs)
88:         self.in_features = in_features
89:         self.hidden_dim = hidden_dim
90:         self.grid_size = grid_size
91:         self.spline_order = spline_order
92: 
93:         self.kan1 = KANLayer(
94:             in_features=in_features,
95:             out_features=hidden_dim,
96:             grid_size=grid_size,
97:             spline_order=spline_order,
98:             name="kan_head_layer1",
99:         )
100:         self.kan2 = KANLayer(
101:             in_features=hidden_dim,
102:             out_features=1,
103:             grid_size=grid_size,
104:             spline_order=spline_order,
105:             name="kan_head_layer2",
106:         )
```

### 2.2 Parameter Formulation per KAN Layer
In [`src/kan/kan_layer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_layer.py#L86-L125), each `KANLayer` defines:
- Extended uniform knot vector of length:
  $$\text{num\_knots} = \text{grid\_size} + 2 \times \text{spline\_order} + 1 = 5 + 2(3) + 1 = 12$$
- Spline basis function count:
  $$\text{num\_splines} = \text{num\_knots} - (\text{spline\_order} + 1) = 12 - 4 = 8$$
- Trainable variables registered in `build()`:
  1. `w_base`: shape `(out_features, in_features)` $\implies \text{out} \times \text{in}$ parameters.
  2. `w_spline`: shape `(out_features, in_features)` $\implies \text{out} \times \text{in}$ parameters.
  3. `spline_coeffs`: shape `(out_features, in_features, num_splines)` $\implies \text{out} \times \text{in} \times 8$ parameters.

$$\text{Total Parameters per KANLayer} = (\text{out} \times \text{in}) \times (1 + 1 + 8) = 10 \times (\text{out} \times \text{in})$$

---

## 3. Mathematical Layer-by-Layer Parameter Proof

### Layer 1: `kan_head_layer1` ($16 \rightarrow 8$)
- `in_features` = $16$, `out_features` = $8$, `num_splines` = $8$
- `w_base`: $(8, 16) = 128\text{ parameters}$
- `w_spline`: $(8, 16) = 128\text{ parameters}$
- `spline_coeffs`: $(8, 16, 8) = 1,024\text{ parameters}$
$$\mathbf{\text{Subtotal Layer 1}} = 128 + 128 + 1,024 = \mathbf{1,280\text{ parameters}}$$

### Layer 2: `kan_head_layer2` ($8 \rightarrow 1$)
- `in_features` = $8$, `out_features` = $1$, `num_splines` = $8$
- `w_base`: $(1, 8) = 8\text{ parameters}$
- `w_spline`: $(1, 8) = 8\text{ parameters}$
- `spline_coeffs`: $(1, 8, 8) = 64\text{ parameters}$
$$\mathbf{\text{Subtotal Layer 2}} = 8 + 8 + 64 = \mathbf{80\text{ parameters}}$$

### Total Head Parameters (`KANFeatureRegressor`)
$$\mathbf{\text{Total Trainable Parameters}} = 1,280 + 80 = \mathbf{1,360\text{ parameters}}$$

### Full Pipeline Model (`KANRegressor`)
- Backbone `feature_extractor` (`ConvFeatureExtractor`): $3,360\text{ parameters}$
- Regression Head (`KANFeatureRegressor`): $1,360\text{ parameters}$
$$\mathbf{\text{Full Model Total}} = 3,360 + 1,360 = \mathbf{4,720\text{ parameters}}$$

---

## 4. Empirical Verification via Model Instantiation

Executed runtime Python inspection script [`scratch/verify_params.py`](file:///C:/Users/admin/.gemini/antigravity/brain/2aee08b1-0663-462c-814d-4f0ee6599ca8/scratch/verify_params.py):

```text
2. KANFeatureRegressor (inherits from keras.Model)
Total trainable variables: 6
  Var: w_base               | Shape: (8, 16)         | Count: 128
  Var: w_spline             | Shape: (8, 16)         | Count: 128
  Var: spline_coeffs        | Shape: (8, 16, 8)      | Count: 1024
  Var: w_base               | Shape: (1, 8)          | Count: 8
  Var: w_spline             | Shape: (1, 8)          | Count: 8
  Var: spline_coeffs        | Shape: (1, 8, 8)       | Count: 64
Total trainable params: 1360
Total non-trainable params: 0
Total registered weights: 6
Layers in kan_head:
  Layer: kan_head_layer1 (KANLayer)
    in_features=16, out_features=8, grid_size=5, spline_order=3
    grid shape: (12,), is_tensor: True, is_variable: False
  Layer: kan_head_layer2 (KANLayer)
    in_features=8, out_features=1, grid_size=5, spline_order=3
    grid shape: (12,), is_tensor: True, is_variable: False

3. KANRegressor (Full model: Backbone + KAN head)
Backbone params: 3360
Head params: 1360
Total trainable params: 4720
```

### Clarification on Spline Knots ("Grid Parameters")
- `self.grid = tf.constant(knots, dtype=tf.float32)`
- `self.grid` is an immutable `tf.Tensor` constant buffer of length $12$.
- It is **not** a `tf.Variable`, is **not** registered in `self.weights`, `self.trainable_variables`, or `self.non_trainable_variables`, and consumes **zero parameter slots**.

---

## 5. Root-Cause Explanation of the Phase 7 Contradiction

The Phase 7 report author correctly noted the overall totals ($1,360$ head params, $4,720$ full params), but failed to inspect the layer structure in [`src/kan/kan_model.py:93-106`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L93-L106).
- The author assumed the head was a single-layer mapping from an imagined 128-dimensional latent space directly to 1 output.
- Seeing the number $1,280$ in historical notes (which is actually the parameter count of Layer 1: $16 \to 8$), the author conflated it with the grid knot calculation ($128 \times 10 = 1280$) and labeled it "untrainable grid parameters".
- The author then attempted to sum base weights (128), spline weights (1024), and an imagined bias (1), producing $1,153$ and leaving a glaring arithmetic contradiction with $1,360$.

## 6. Audit Conclusion & Remediation
- **Software Implementation Status:** **VERIFIED CORRECT.** The true two-layer KAN head ($16 \to 8 \to 1$) has exactly $1,360$ trainable parameters ($1,280 + 80$). Full `KANRegressor` has exactly $4,720$ parameters.
- **Code Modifications Needed:** **NONE.** The source code is mathematically consistent.
- **Reporting Remediation:** All documentation must cite the true two-layer architecture ($16 \to 8 \to 1$) and the verified parameter breakdown ($1280 + 80 = 1360$).
