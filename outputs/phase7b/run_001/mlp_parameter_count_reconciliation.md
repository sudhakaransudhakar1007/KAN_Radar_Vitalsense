# Forensic Audit: MLP Baseline Parameter Count and Architectural Reconciliation (Contradiction C)

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Neural Network Architect, Scientific ML Reviewer, & TensorFlow Specialist  
**Artifact File:** `outputs/phase7b/run_001/mlp_parameter_count_reconciliation.md`  

---

## 1. Audited Claim vs Demonstrated Empirical Truth

| Architectural Feature | Phase 7 Report Claim | Source Code & Runtime Truth (`src/kan/`) | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Model Scope** | Standalone MLP without backbone | **End-to-End Regressor (Backbone + Head)** | 🔴 **REPORTING ERROR REFUTED** |
| **Architecture** | $128 \rightarrow 24 \rightarrow 8 \rightarrow 1$ | **Backbone (Conv1D) + Head ($16 \rightarrow 8 \rightarrow 1$)** | 🔴 **REPORTING ERROR REFUTED** |
| **Backbone Parameters** | Omitted from calculation | **3,360 parameters** (`ConvFeatureExtractor`) | 🟢 **EMPIRICALLY VERIFIED** |
| **Head Layer 1 Parameters** | Claimed $3,096$ ($128 \times 24 + 24$) | **136 parameters** (`Dense(8)` on 16 inputs: $16 \times 8 + 8$) | 🔴 **REPORTING ERROR REFUTED** |
| **Head Layer 2 Parameters** | Claimed $200$ ($24 \times 8 + 8$) | **9 parameters** (`Dense(1)` on 8 inputs: $8 \times 1 + 1$) | 🔴 **REPORTING ERROR REFUTED** |
| **Head Layer 3 Parameters** | Claimed $9$ ($8 \times 1 + 1$) | **Non-existent** (head has only 2 layers) | 🔴 **REPORTING ERROR REFUTED** |
| **Head Parameter Subtotal** | Unreported / arithmetic $3,305$ | **145 parameters** ($136 + 9$) | 🟢 **EMPIRICALLY VERIFIED** |
| **Total Trainable Parameters** | Claimed $3,505$ (contradicted by $3,305$) | **Exactly 3,505 parameters** ($3,360 + 145$) | 🟢 **EMPIRICALLY VERIFIED** |

---

## 2. Source Code Architecture Inspection

In [`src/kan/kan_model.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L194-L228):
```python
194: class MLPRegressor(keras.Model):
195:     """Comparative controlled MLP regressor with identical Conv1D extractor and parameter capacity (3,505 params)."""
196: 
197:     def __init__(
198:         self,
199:         input_dim: int = 3333,
200:         latent_dim: int = 16,
201:         hidden_dim: int = 8,
202:         **kwargs,
203:     ):
204:         super().__init__(**kwargs)
205:         self.input_dim = input_dim
206:         self.latent_dim = latent_dim
207:         self.hidden_dim = hidden_dim
208: 
209:         self.feature_extractor = ConvFeatureExtractor(latent_dim=latent_dim, name="mlp_backbone")
210:         self.dense1 = layers.Dense(hidden_dim, activation="silu", name="mlp_dense1")
211:         self.dense2 = layers.Dense(1, name="mlp_dense2")
```

The model operates in dual-input mode:
- Raw radar input: $(B, 3333) \rightarrow \text{ConvFeatureExtractor} \rightarrow (B, 16) \rightarrow \text{Dense}(8) \rightarrow \text{Dense}(1) \rightarrow (B,)$
- Latent feature input: $(B, 16) \rightarrow \text{Dense}(8) \rightarrow \text{Dense}(1) \rightarrow (B,)$

---

## 3. Mathematical Layer-by-Layer Parameter Breakdown

### 3.1 Feature Extractor Backbone (`ConvFeatureExtractor`)
- Identical shared backbone used across CNN, KAN, and MLP:
  - `conv1`: `Conv1D(8, k=15, s=4)` $\implies (15 \times 1 \times 8) + 8 = 128$
  - `conv2`: `Conv1D(16, k=11, s=4)` $\implies (11 \times 8 \times 16) + 16 = 1,424$
  - `conv3`: `Conv1D(16, k=7, s=2)` $\implies (7 \times 16 \times 16) + 16 = 1,808$
$$\mathbf{\text{Backbone Subtotal}} = 128 + 1,424 + 1,808 = \mathbf{3,360\text{ parameters}}$$

### 3.2 MLP Regression Head
- **Layer 1 (`dense1`):** `Dense(8)` on $16$ latent features:
  - Kernel weights: shape $(16, 8) \implies 128\text{ parameters}$
  - Bias: shape $(8,) \implies 8\text{ parameters}$
  $$\text{Dense1 Subtotal} = 128 + 8 = 136\text{ parameters}$$
- **Layer 2 (`dense2`):** `Dense(1)` on $8$ hidden features:
  - Kernel weights: shape $(8, 1) \implies 8\text{ parameters}$
  - Bias: shape $(1,) \implies 1\text{ parameter}$
  $$\text{Dense2 Subtotal} = 8 + 1 = 9\text{ parameters}$$
$$\mathbf{\text{Head Subtotal}} = 136 + 9 = \mathbf{145\text{ parameters}}$$

### 3.3 Full `MLPRegressor` Total
$$\mathbf{\text{Total Trainable Parameters}} = 3,360 + 145 = \mathbf{3,505\text{ parameters}}$$

---

## 4. Empirical Verification via Model Instantiation

Executed runtime Python inspection script [`scratch/verify_params.py`](file:///C:/Users/admin/.gemini/antigravity/brain/2aee08b1-0663-462c-814d-4f0ee6599ca8/scratch/verify_params.py):

```text
5. MLPRegressor (Full model: Backbone + 2 Dense layers)
Backbone params: 3360
MLP Head variables:
  Var: kernel               | Shape: (16, 8)         | Count: 128
  Var: bias                 | Shape: (8,)            | Count: 8
  Var: kernel               | Shape: (8, 1)          | Count: 8
  Var: bias                 | Shape: (1,)            | Count: 1
Dense1 params: 136
Dense2 params: 9
Total MLP params: 3505
```
- Total trainable parameters: **3,505**.
- Total non-trainable parameters: **0**.
- Total registered weight tensors: **8** (6 in backbone + 2 in head).

---

## 5. Root-Cause Explanation of the Phase 7 Contradiction

The Phase 7 report author knew that the model had 3,505 total parameters. However:
1. The author mistakenly assumed that `MLPRegressor` was a standalone multilayer perceptron without the convolutional backbone.
2. The author attempted to reverse-engineer a 3-layer architecture matching ~3,500 parameters from an imagined 128-dimensional latent space:
   $$128 \to 24 \implies 128 \times 24 + 24 = 3,096$$
   $$24 \to 8 \implies 24 \times 8 + 8 = 200$$
   $$8 \to 1 \implies 8 \times 1 + 1 = 9$$
3. The sum of those reverse-engineered numbers was $3,096 + 200 + 9 = 3,305$. The author nonetheless reported the total as 3,505, leaving a 200-parameter contradiction in the text.
4. In reality, the true latent dimension is **16** (not 128), and the model includes the **3,360-parameter convolutional backbone**. The true head has $136 + 9 = 145$ parameters, perfectly satisfying:
   $$3,360 + 145 = 3,505$$

## 6. Audit Conclusion & Remediation
- **Software Implementation Status:** **VERIFIED CORRECT.** The implemented `MLPRegressor` is a valid, parameter-controlled baseline consisting of the 3,360-parameter `ConvFeatureExtractor` and a 145-parameter 2-layer Dense head ($16 \to 8 \to 1$).
- **Code Modifications Needed:** **NONE.**
- **Reporting Remediation:** All documentation must cite the verified architecture (`ConvFeatureExtractor` [3,360] + `Dense(8)` [136] + `Dense(1)` [9] = 3,505).
