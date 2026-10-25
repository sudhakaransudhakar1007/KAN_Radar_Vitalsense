# PHASE 4D: COMPARATIVE BASELINES INTEGRATION & SPECIFICATION AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 3: Comparison Baselines  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. Overview of Comparative Baselines

To evaluate whether the non-linear spline parameterization of KAN confers genuine advantages for physiological Doppler radar regression, four comparative baselines were audited:

| Baseline Model | Model Class | Trainable Parameters | Architecture & Mechanism | Interface & Target Units |
| :--- | :--- | :---: | :--- | :--- |
| **`CNNRegressor`** | Deep 1D Convolutional | **3,377** | 3-stage Conv1D backbone (3,360 params) + GlobalAvgPool1D + Dense(1) linear readout (17 params). | Dual: $(B, 3333)$ or $(B, 16) \to (B,)$ [BPM via normalizer]. |
| **`MLPRegressor`** | Deep Conv-MLP | **3,505** | 3-stage Conv1D backbone (3,360 params) + Dense(8, SiLU) (136 params) + Dense(1) (9 params). | Dual: $(B, 3333)$ or $(B, 16) \to (B,)$ [BPM via normalizer]. |
| **`MeanPredictorBaseline`** | Non-parametric | **0** | Fits empirical training fold mean $\bar{y}_{\text{train}}$; predicts constant scalar. | Fits $y_{\text{train}} \to$ predicts $(N,)$ scalar BPM array. |
| **Classical Autocorrelation** | Signal Processing | N/A | **Implementation Gap:** Missing mathematical specification. | **Documented Gap (Outside Scope)** |

---

## 2. Deep Baselines Verification (`CNNRegressor` and `MLPRegressor`)

### A. CNN Regressor (`CNNRegressor`):
- **Backbone:** Identical `ConvFeatureExtractor` shared across all neural models, ensuring controlled feature capacity:
  - Conv1: 8 filters ($k=15, s=4$) $\to$ MaxPool1D(2)
  - Conv2: 16 filters ($k=11, s=4$) $\to$ MaxPool1D(2)
  - Conv3: 16 filters ($k=7, s=2$) $\to$ GlobalAveragePooling1D
  - Backbone parameters: $128 + 1,424 + 1,808 = \mathbf{3,360\text{ parameters}}$.
- **Readout:** Single linear Dense layer ($16 \to 1$): $(16 \times 1) + 1 = \mathbf{17\text{ parameters}}$.
- **Total Trainable Parameters:** $3,360 + 17 = \mathbf{3,377\text{ parameters}}$.
- **Forward & Backward Verification:** Executed on synthetic data; verified finite forward output and finite gradients on all weights.

### B. Controlled MLP Regressor (`MLPRegressor`):
- **Structure:** Identical Conv1D backbone (3,360 params) + 2-layer Dense network ($16 \to 8 \to 1$).
  - Dense 1: $(16 \times 8) + 8 = 136$ parameters (SiLU activation).
  - Dense 2: $(8 \times 1) + 1 = 9$ parameters (Linear output).
- **Total Trainable Parameters:** $3,360 + 136 + 9 = \mathbf{3,505\text{ parameters}}$.
- **Role in Study:** Isolates whether replacing standard matrix multiplication with B-spline univariate functions improves generalization.

### C. Non-Parametric Mean Baseline (`MeanPredictorBaseline`):
- Evaluates the stationary lower bound of prediction accuracy.
- Computes training fold target mean $\bar{y}_{\text{train}} = \frac{1}{N} \sum y_i$.
- Returns an array filled with $\bar{y}_{\text{train}}$. Verified finite output shape $(N,)$.

---

## 3. Audit of Classical Autocorrelation Baseline (Specification Gap)

Task 3 explicitly instructs:
> *"Inspect the classical autocorrelation baseline. If it is missing or not integrated, implement it only if its intended algorithm is sufficiently specified by the existing project. Otherwise document the exact missing specification. Do not silently substitute a different algorithm."*

### Findings of Repository Audit:
1. **Search Results:** An exhaustive search of the entire workspace for `autocorrelation` returned zero matches in source code or project documentation.
2. **Missing Specifications:** The project lacks the necessary scientific and engineering specifications to implement a canonical autocorrelation baseline, including:
   - **Lag Search Window:** The exact sampling rate is $333.3333\text{ Hz}$. For heart rate in $[35, 185]\text{ BPM}$, the expected cardiac period is $T \in [0.3243, 1.7143]\text{ s}$, corresponding to lag indices $\tau \in [108, 571]\text{ samples}$. However, whether autocorrelation is computed on raw phase, demodulated displacement, or bandpassed cardiac Doppler is unspecified.
   - **Preprocessing Pre-Filter:** Order, cutoffs, and filter type for isolating the cardiac fundamental from the respiratory harmonic prior to autocorrelation are unspecified.
   - **Peak-Picking Criterion:** Minimum peak prominence, thresholding, parabolic sub-sample interpolation, and harmonic rejection criteria (to prevent picking the respiratory second harmonic or cardiac second harmonic) are unspecified.
   - **Fallback Policy:** Policy for windows where no peak exceeds the confidence threshold (e.g., NaN vs. mean imputation) is unspecified.

### Auditor Decision:
In strict compliance with the prompt mandate (*"document the exact missing specification. Do not silently substitute a different algorithm"*), the classical autocorrelation baseline is cataloged as a **documented specification gap**. An ad-hoc algorithm has not been silently invented.
