# PHASE 5: EXISTING PROJECT & PRIOR RUN AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Prior Audited Run:** `outputs/phase5/run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

In accordance with Phase 5 Task 1, an exhaustive, independent audit was performed on the existing project workspace, source code modules, prior Phase 5 execution artifacts (`outputs/phase5/run_001/`), Phase 4 completion records, and the underlying dataset inventory.

The audit verified that the core KAN architecture, comparative baselines (CNN, MLP, Mean baseline), feature extractor, training-fold-only target normalizer, and 24-fold LOSO cross-validation infrastructure are fully implemented, synthetically validated, and covered by 100 passing unit and integration tests.

However, an audit of prior Phase 5 execution (`run_001`) confirmed that **no real-data model training has ever executed**. The Phase 2A Finalization Gate remains officially **`OPEN`**, and explicit user authorization for real-data fitting and persistent ML tensor export has not been granted. Consequently, prior `run_001` appropriately completed only non-training checks and halted real-data fitting without fabricating any checkpoints, training logs, or predictions.

---

## 2. Core Source Code Module Inspection

The actual repository source files were inspected line-by-line prior to any modifications:

### A. `src/kan/kan_layer.py` (Inspected: 168 lines)
- **Mathematical Formulation:** Implements authentic univariate Cox-de Boor B-splines on network edges:
  $$\phi_{j, i}(x_i) = w_{b, j, i} \cdot \text{SiLU}(x_i) + w_{s, j, i} \cdot \sum_m c_{j, i, m} B_{m, k}(x_i)$$
- **Spline Recursion:** `evaluate_b_splines` computes degree-$k$ basis functions ($k=3$, cubic) across an extended uniform grid without adaptive knot movement, ensuring mathematical stability and strict determinism.
- **Edge Contraction:** Uses `tf.einsum("bin,oin->boi", bases, self.spline_coeffs)` to evaluate basis activations across all input-output connections.
- **Parameters:** Trainable weights `w_base`, `w_spline`, and `spline_coeffs`.

### B. `src/kan/kan_model.py` (Inspected: 246 lines)
- **`ConvFeatureExtractor`:** 1D convolutional backbone downsampling 3,333 filtered radar displacement samples to 16 latent features via 3 Conv1D layers (filters: 8, 16, 16; kernels: 15, 11, 7; strides: 4, 4, 2) with MaxPooling and GlobalAveragePooling1D. Total parameters: **3,360**.
- **`KANFeatureRegressor`:** 2-layer KAN regression head (`[16, 8, 1]`) operating on 16 latent features. Total parameters: **1,360**.
- **`KANRegressor`:** Full proposed model combining `ConvFeatureExtractor` + `KANFeatureRegressor`. Supports dual-input interface (raw 3,333-sample windows or 16 pre-extracted features). Total parameters: **4,720**.
- **`CNNRegressor`:** Pure CNN comparative baseline sharing the same 3,360-parameter backbone with a linear readout (`Dense(1)`). Total parameters: **3,377**.
- **`MLPRegressor`:** Controlled MLP baseline sharing the same 3,360-parameter backbone with a 2-layer Dense head (`Dense(8, activation='silu') -> Dense(1)`). Total parameters: **3,505**.
- **`MeanPredictorBaseline`:** Non-parametric baseline predicting training fold target mean ($\mu_{y,\text{train}}$). Total parameters: **0**.

### C. `src/kan/normalization.py` (Inspected: 115 lines)
- **`TargetNormalizer`:** Implements Z-score normalization strictly on training targets.
- **Leakage Guards:** Raises `RuntimeError` if `transform()` or `inverse_transform()` is invoked before `fit()`.
- **Zero-Variance Guard:** If target standard deviation is below `1e-6`, sets $\sigma = 1.0$ to prevent division by zero.
- **BPM Inversion:** Accurately maps normalized predictions $\hat{y}_{\text{norm}}$ back to physical BPM ($\hat{y}_{\text{BPM}} = \hat{y}_{\text{norm}} \cdot \sigma + \mu$).

### D. `src/kan/loso_evaluator.py` (Inspected: 361 lines)
- **`LOSOEvaluator`:** Partitions the accepted window manifest into 24 subject-independent folds.
- **Gate Blocker:** Inspects `outputs/phase2a/step2b_consistency_audit.md` and halts persistent training if gate is `OPEN`.
- **Synthetic Benchmark:** Verifies gradient flow, loss reduction, and inverse transformation accuracy on synthetic multitone signals.

---

## 3. Prior Run Inventory & Evidence Audit

| Item | Existing State | Concrete Evidence | Required Action |
| :--- | :--- | :--- | :--- |
| **Dataset validation** | Completed (diagnostic dry-run) | `outputs/supervised_dataset/run_001/accepted_window_manifest.csv` (1,029 accepted, 27 rejected) | Revalidate window counts, signal fields, sampling rate, and pairing. |
| **Training authorization** | **MISSING / NOT GRANTED** | `outputs/phase2a/step2b_consistency_audit.md` (lines 9–16: Gate officially OPEN) | Enforce real-data training block; report blocker. |
| **KAN implementation** | Verified and tested | `src/kan/kan_layer.py`, `src/kan/kan_model.py` (4,720 params) | Audit architecture, parameters, and B-spline formulation. |
| **Feature pipeline** | Verified and tested | `ConvFeatureExtractor` in `src/kan/kan_model.py` (16 latent features) | Verify radar-only inputs, neutral naming, no ECG leakage. |
| **Target normalization** | Verified and tested | `src/kan/normalization.py` (`TargetNormalizer`) | Verify training-fold-only fitting and round-trip inversion. |
| **LOSO split** | Verified and partitioned | `outputs/phase4/completion_run_001/fold_split_manifest.csv` (24 folds) | Verify 0% leakage, coupled condition holding, test isolation. |
| **KAN training** | **NOT EXECUTED (BLOCKED)** | `outputs/phase5/run_001/checkpoint_manifest.md` (0 checkpoints) | Maintain real-data training block until user authorization. |
| **CNN baseline** | Verified (synthetic only) | `src/kan/kan_model.py` (3,377 params) | Evaluate complexity and latency; maintain real-data block. |
| **MLP baseline** | Verified (synthetic only) | `src/kan/kan_model.py` (3,505 params) | Evaluate complexity and latency; maintain real-data block. |
| **Mean baseline** | Verified and tested | `src/kan/kan_model.py` (0 params) | Verify constant prediction handling ($r = 0.0$). |
| **Autocorrelation baseline**| **UNIMPLEMENTED** | Phase 4 completion report (`baseline_integration_report.md`) | Register explicit specification gap; do not invent ad-hoc code. |
| **Held-out predictions** | **NOT GENERATED** | `outputs/phase5/run_001/checkpoint_manifest.md` | Mark as NOT GENERATED; do not fabricate. |
| **Metrics and uncertainty**| Verified on synthetic data | Synthetic test: KAN MAE = 3.01 BPM | Define metrics rigorously; real-data metrics NOT GENERATED. |
| **Checkpoints** | **0 CHECKPOINTS SAVED** | System-wide search: 0 `.pt`, `.h5`, or `.keras` files | Catalog as NOT GENERATED. |
| **Tests** | **100 / 100 PASSED** | `pytest tests/ -v` (100 passed in 26.47s) | Record test execution results across 13 test files. |

---

## 4. Findings on Prior Phase 5 `run_001`

1. **No Real-Data Model Fitting:** In `outputs/phase5/run_001/`, no models were trained on real VITALSENSE data. The auditor appropriately halted model fitting upon detecting that the Phase 2A Finalization Gate was `OPEN`.
2. **Zero Fabrication:** The prior run did not fabricate checkpoints, prediction CSVs, or fold metrics. It generated 10 non-training audit documents and cataloged all empirical training files as `NOT GENERATED`.
3. **Reproducibility of Latency Benchmarks:** CPU latency measurements were performed on synthetic inputs and verified:
   - `KANRegressor`: 4,720 params, 2.368 ms/sample latency.
   - `MLPRegressor`: 3,505 params, 1.360 ms/sample latency.
   - `CNNRegressor`: 3,377 params, 1.123 ms/sample latency.
   - `MeanPredictorBaseline`: 0 params, 0.002 ms/sample latency.
4. **Action for `run_002`:** Because no training checkpoints exist to resume, `run_002` must perform a comprehensive, end-to-end verification and audit, preserving all previous runs and formalizing the exact scientific state of the project.
