# Forensic Audit: CNN Baseline Parameter Count and Architectural Reconciliation (Contradiction D)

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Neural Network Architect, Scientific ML Reviewer, & TensorFlow Specialist  
**Artifact File:** `outputs/phase7b/run_001/cnn_parameter_count_reconciliation.md`  

---

## 1. Audited Claim vs Demonstrated Empirical Truth

| Architectural Component | Phase 7 Report Claim | Source Code & Runtime Truth (`src/kan/`) | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Convolution Type** | Standard Conv1D | **Standard Conv1D (not grouped, not depthwise)** | 🟢 **CONFIRMED STANDARD** |
| **Backbone Layer Count** | 4 Convolutional layers | **3 Convolutional layers + 2 MaxPool layers** | 🔴 **REPORTING ERROR REFUTED** |
| **Layer 1** | Conv1D(1, 16, k=15) [$256$ params] | **Conv1D(8, k=15, s=4) [128 params]** | 🔴 **REPORTING ERROR REFUTED** |
| **Layer 2** | Conv1D(16, 32, k=11) [$5,664$ params] | **Conv1D(16, k=11, s=4) [1,424 params]** | 🔴 **REPORTING ERROR REFUTED** |
| **Layer 3** | Conv1D(32, 64, k=7) [$14,368$ params] | **Conv1D(16, k=7, s=2) [1,808 params]** | 🔴 **REPORTING ERROR REFUTED** |
| **Layer 4** | Conv1D(64, 128, k=5) [$41,088$ params] | **Non-existent** | 🔴 **REPORTING ERROR REFUTED** |
| **Pooling Mechanism** | AdaptiveAvgPool1D | **GlobalAveragePooling1D (downsampling to 16)** | 🟢 **CLARIFIED** |
| **Backbone Total Params** | Claimed $3,360$ (hypothetical gave $>60,000$) | **Exactly 3,360 trainable parameters** | 🟢 **EMPIRICALLY VERIFIED** |
| **Readout Head** | Linear readout ($17$ params) | **`Dense(1)` readout (16 weights + 1 bias = 17)** | 🟢 **EMPIRICALLY VERIFIED** |
| **Full CNN Total Params** | $3,377$ | **Exactly 3,377 trainable parameters** ($3360 + 17$) | 🟢 **EMPIRICALLY VERIFIED** |

---

## 2. Source Code Architecture Inspection

### 2.1 The Convolutional Backbone (`ConvFeatureExtractor`)
In [`src/kan/kan_model.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L28-L50):
```python
28: class ConvFeatureExtractor(layers.Layer):
29:     """Compact 1D convolutional feature extractor downsampling 3333 raw radar samples to 16 latent features.
30: 
31:     Architecture:
32:       Conv1D(8, k=15, s=4, same)  -> (834, 8)
33:       MaxPool1D(2)                 -> (417, 8)
34:       Conv1D(16, k=11, s=4, same) -> (105, 16)
35:       MaxPool1D(2)                 -> (52, 16)
36:       Conv1D(16, k=7, s=2, same)  -> (26, 16)
37:       GlobalAveragePooling1D       -> (16,)
38:     Total trainable parameters: 3,360.
39:     """
40: 
41:     def __init__(self, latent_dim: int = 16, **kwargs):
42:         super().__init__(**kwargs)
43:         self.latent_dim = latent_dim
44:         self.conv1 = layers.Conv1D(8, kernel_size=15, strides=4, padding="same", activation="silu", name="conv1")
45:         self.pool1 = layers.MaxPooling1D(pool_size=2, name="pool1")
46:         self.conv2 = layers.Conv1D(16, kernel_size=11, strides=4, padding="same", activation="silu", name="conv2")
47:         self.pool2 = layers.MaxPooling1D(pool_size=2, name="pool2")
48:         self.conv3 = layers.Conv1D(latent_dim, kernel_size=7, strides=2, padding="same", activation="silu", name="conv3")
49:         self.gap = layers.GlobalAveragePooling1D(name="gap")
```

### 2.2 The Full CNN Baseline (`CNNRegressor`)
In [`src/kan/kan_model.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L162-L192):
```python
162: class CNNRegressor(keras.Model):
163:     """Pure CNN comparison baseline: Conv1D feature extractor + linear readout (3,377 params)."""
164: 
165:     def __init__(
166:         self,
167:         input_dim: int = 3333,
168:         latent_dim: int = 16,
169:         **kwargs,
170:     ):
171:         super().__init__(**kwargs)
172:         self.input_dim = input_dim
173:         self.latent_dim = latent_dim
174: 
175:         self.feature_extractor = ConvFeatureExtractor(latent_dim=latent_dim, name="cnn_backbone")
176:         self.readout = layers.Dense(1, name="cnn_readout")
```

---

## 3. Mathematical Layer-by-Layer Parameter Breakdown

All convolutions are standard 1D convolutions where:
$$\text{Parameters} = (\text{kernel\_size} \times \text{in\_channels} \times \text{out\_channels}) + \text{out\_channels (biases)}$$

1. **`conv1`:** `kernel_size = 15`, `in_channels = 1`, `out_channels = 8`, `strides = 4`:
   $$\text{Weights} = 15 \times 1 \times 8 = 120$$
   $$\text{Biases} = 8$$
   $$\text{Subtotal} = 120 + 8 = 128\text{ parameters}$$
2. **`pool1`:** `pool_size = 2`:
   $$\text{Subtotal} = 0\text{ parameters}$$
3. **`conv2`:** `kernel_size = 11`, `in_channels = 8`, `out_channels = 16`, `strides = 4`:
   $$\text{Weights} = 11 \times 8 \times 16 = 1,408$$
   $$\text{Biases} = 16$$
   $$\text{Subtotal} = 1,408 + 16 = 1,424\text{ parameters}$$
4. **`pool2`:** `pool_size = 2`:
   $$\text{Subtotal} = 0\text{ parameters}$$
5. **`conv3`:** `kernel_size = 7`, `in_channels = 16`, `out_channels = 16`, `strides = 2`:
   $$\text{Weights} = 7 \times 16 \times 16 = 1,792$$
   $$\text{Biases} = 16$$
   $$\text{Subtotal} = 1,792 + 16 = 1,808\text{ parameters}$$
6. **`gap`:** `GlobalAveragePooling1D`:
   $$\text{Subtotal} = 0\text{ parameters}$$

$$\mathbf{\text{Backbone Total}} = 128 + 1,424 + 1,808 = \mathbf{3,360\text{ parameters}}$$

7. **`readout`:** `Dense(1)` on 16 latent inputs:
   $$\text{Weights} = 16 \times 1 = 16$$
   $$\text{Bias} = 1$$
   $$\text{Readout Subtotal} = 16 + 1 = 17\text{ parameters}$$

$$\mathbf{\text{Full Model Total}} = 3,360 + 17 = \mathbf{3,377\text{ parameters}}$$

---

## 4. Empirical Verification via Model Instantiation

Executed runtime Python inspection script [`scratch/verify_params.py`](file:///C:/Users/admin/.gemini/antigravity/brain/2aee08b1-0663-462c-814d-4f0ee6599ca8/scratch/verify_params.py):

```text
1. ConvFeatureExtractor (inherits from layers.Layer)
Total trainable variables: 6
  Var: kernel               | Shape: (15, 1, 8)      | Count: 120
  Var: bias                 | Shape: (8,)            | Count: 8
  Var: kernel               | Shape: (11, 8, 16)     | Count: 1408
  Var: bias                 | Shape: (16,)           | Count: 16
  Var: kernel               | Shape: (7, 16, 16)     | Count: 1792
  Var: bias                 | Shape: (16,)           | Count: 16
Total trainable params: 3360
Total non-trainable params: 0

4. CNNRegressor (Full model: Backbone + Linear readout)
Backbone params: 3360
  Readout var: kernel       | Shape: (16, 1)         | Count: 16
  Readout var: bias         | Shape: (1,)            | Count: 1
Readout params: 17
Total CNN params: 3377
```

---

## 5. Root-Cause Explanation of the Phase 7 Contradiction

The Phase 7 report author correctly recorded the numbers **3,360** and **3,377**, but fabricated a narrative architectural description without checking [`src/kan/kan_model.py:44-49`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L44-L49):
- The author listed a 4-layer network: Conv1D(1, 16, 15) $\rightarrow$ Conv1D(16, 32, 11) $\rightarrow$ Conv1D(32, 64, 7) $\rightarrow$ Conv1D(64, 128, 5).
- If that hypothetical 4-layer network were built, its parameter count would be:
  $$256 + 5,664 + 14,368 + 41,088 = 61,376\text{ parameters}$$
  which exceeds 3,360 by over $1,700\%$.
- The true source code implements a 3-layer convolutional network downsampling from 3,333 to 16 latent features, perfectly yielding 3,360 parameters for the backbone and 3,377 parameters for the full CNN regressor.

## 6. Audit Conclusion & Remediation
- **Software Implementation Status:** **VERIFIED CORRECT.** The true architecture is 3 standard Conv1D layers (128, 1424, 1808 params) yielding 3,360 backbone parameters, plus a 17-parameter `Dense(1)` readout yielding 3,377 parameters.
- **Code Modifications Needed:** **NONE.**
- **Reporting Remediation:** All documentation must cite the true 3-layer Conv1D architecture downsampling to 16 latent features.
