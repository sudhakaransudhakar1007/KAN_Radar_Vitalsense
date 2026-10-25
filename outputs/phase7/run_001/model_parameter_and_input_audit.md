# PHASE 7: MODEL ARCHITECTURES, INPUT CONTRACTS & PARAMETER COUNT AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Scientific ML Auditor & Python/TensorFlow Reviewer  

---

## 1. Executive Summary

In compliance with Phase 7 Task F, an independent architectural and parameter audit was conducted across the proposed Kolmogorov–Arnold Network (KAN) and comparison baseline models. All models were instantiated in isolation to evaluate layer structures, input/output tensor contracts, trainable versus non-trainable parameter counts, and memory footprints.

The audit confirms that all model objects match their documented specifications, strictly enforce feature isolation from ECG reference channels, and maintain architectural capacity parity between comparative baselines.

---

## 2. Trainable, Non-Trainable & Full-Model Parameter Breakdown

Direct programmatic inspection of model weights and layer structures verified:

| Component / Model Class | Subsystem Role | Trainable Parameters | Non-Trainable Parameters | Total Parameters | Float32 Weight Memory |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`ConvFeatureExtractor`** | 1D Conv Backbone | **3,360** | 0 | **3,360** | $13.44\text{ KB}$ |
| **`KANFeatureRegressor`** | 2-Layer B-Spline Head | **1,360** | 0 | **1,360** | $5.44\text{ KB}$ |
| **`KANRegressor`** (Proposed) | Backbone (3,360) + KAN Head (1,360) | **4,720** | 0 | **4,720** | $18.88\text{ KB}$ |
| **`MLPRegressor`** (Baseline) | Backbone (3,360) + Dense Head (145) | **3,505** | 0 | **3,505** | $14.02\text{ KB}$ |
| **`CNNRegressor`** (Baseline) | Backbone (3,360) + Linear Head (17) | **3,377** | 0 | **3,377** | $13.51\text{ KB}$ |
| **`MeanPredictorBaseline`** | Non-parametric Training Mean | **0** | 0 | **0** | $0.00\text{ KB}$ |
| **`TargetNormalizer`** | Target Standardization Utility | **0** | 0 | **0** | $0.00\text{ KB}$ |

### Detailed Layer Weight Dimensions:
1. **`ConvFeatureExtractor` (Backbone: 3,360 parameters):**
   - Conv1: `(15, 1, 8)` kernel + `(8,)` bias = $120 + 8 = 128$
   - Conv2: `(11, 8, 16)` kernel + `(16,)` bias = $1,408 + 16 = 1,424$
   - Conv3: `(7, 16, 16)` kernel + `(16,)` bias = $1,792 + 16 = 1,808$
2. **`KANFeatureRegressor` (KAN Head: 1,360 parameters):**
   - Layer 1 (`16 -> 8`): `w_base` $(8, 16) = 128$; `w_spline` $(8, 16) = 128$; `spline_coeffs` $(8, 16, 8) = 1,024 \implies 1,280$
   - Layer 2 (`8 -> 1`): `w_base` $(1, 8) = 8$; `w_spline` $(1, 8) = 8$; `spline_coeffs` $(1, 8, 8) = 64 \implies 80$
3. **`MLPRegressor` (MLP Head: 145 parameters):**
   - Dense 1 (`16 -> 8`): `(16, 8)` weights + `(8,)` bias = $128 + 8 = 136$
   - Dense 2 (`8 -> 1`): `(8, 1)` weights + `(1,)` bias = $8 + 1 = 9$
4. **`CNNRegressor` (Linear Readout: 17 parameters):**
   - Dense (`16 -> 1`): `(16, 1)` weights + `(1,)` bias = $16 + 1 = 17$

---

## 3. Input/Output Contracts & Data Isolation

1. **Input Interface:**
   - Raw waveform ingestion: Accepts $(B, 3333)$ or $(B, 3333, 1)$ float32 tensors containing filtered radar chest-wall displacement.
   - Dual interface: Can ingest pre-extracted $(B, 16)$ latent features directly.
   - Feature naming: Neutral names `latent_feat_00` through `latent_feat_15` enforced.
   - Zero ECG leakage: No R-peak timestamps, RR intervals, or reference ECG voltages enter the model tensors.
2. **Output Contract:**
   - Model produces a 1D scalar $(B,)$ in standardized target units ($\mu=0, \sigma=1$).
   - `TargetNormalizer.inverse_transform()` converts output back to physical BPM:
     $$\hat{y}_{\text{BPM}} = \hat{y}_{\text{norm}} \cdot \sigma_{y,\text{train}} + \mu_{y,\text{train}}$$
3. **Mean Baseline Contract:**
   - Predicts constant $\mu_{y,\text{train}}$ across all test windows.
   - Handles zero variance defensively ($r \equiv 0.0$) to avoid undefined division.

---

## 4. Verified vs. Unverified Scientific Claims

| Scientific Claim | Verification State | Evidentiary Basis |
| :--- | :---: | :--- |
| **Model Architectures & Parameter Counts** | **VERIFIED** | Verified from instantiated Keras/PyTorch model objects |
| **Gradient Flow & Loss Reduction** | **VERIFIED** | Verified on synthetic multitone signals (`test_synthetic_end_to_end_integration_pipeline`) |
| **Target Normalization Inversion to BPM** | **VERIFIED** | Verified round-trip accuracy ($< 10^{-5}\text{ BPM}$ error) |
| **Single-Window CPU Inference Latency** | **VERIFIED** | Empirical benchmark on host CPU ($2.368\text{ ms}$ for KAN; RTF: $0.00047$) |
| **Real-Data Generalization Across Subjects**| **UNVERIFIED** | Real-data training blocked by Phase 2A gate; 0 real-data checkpoints exist |
| **Empirical Superiority of KAN over CNN/MLP**| **UNVERIFIED** | No comparative real-data metrics exist; claims of superiority are prohibited |
| **Clinical Efficacy in Cardiac Patients** | **UNVERIFIED** | Dataset limited to healthy volunteers; arrhythmia claims prohibited |
