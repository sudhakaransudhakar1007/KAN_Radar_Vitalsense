# PHASE 5: BASELINE ARCHITECTURES & COMPARATIVE SPECIFICATION AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

In compliance with Phase 5 Task 8, a systematic comparative audit of the proposed Kolmogorov–Arnold Network (KAN) and all comparison baselines was conducted. The audit verified architectural capacity matching, feature parity between KAN and MLP, and non-parametric training-only calculation for the Mean Predictor.

Furthermore, an independent audit of the **classical autocorrelation baseline** was conducted. As identified in Phase 4, classical autocorrelation lacks an approved, mathematically specified algorithmic definition. In strict accordance with Task 8, this method remains cataloged as **NOT IMPLEMENTED**, and the exact missing technical specifications are detailed below.

---

## 2. Comparative Baseline Architectures & Feature Parity

| Model | Classification | Input Modality | Latent Capacity | Output Head | Trainable Parameters | Status |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: |
| **KANRegressor** | **Proposed Model** | 3,333 Radar Samples | 16 Latent Feats | 2-layer B-Spline KAN (`[16, 8, 1]`) | **4,720** | Verified (Real-data blocked) |
| **MLPRegressor** | Neural Baseline | 3,333 Radar Samples | 16 Latent Feats | 2-layer Dense MLP (`[16, 8, 1]`) | **3,505** | Verified (Real-data blocked) |
| **CNNRegressor** | Neural Baseline | 3,333 Radar Samples | 16 Latent Feats | Linear Readout (`Dense(1)`) | **3,377** | Verified (Real-data blocked) |
| **MeanPredictor**| Sanity Baseline | Summary Statistic | N/A | Non-parametric Training Mean | **0** | Verified (Real-data blocked) |
| **Autocorrelation**| Classical Baseline | 3,333 Radar Samples | N/A | Peak-lag estimation | 0 | **NOT IMPLEMENTED** |

### A. Architectural Feature Parity: KAN vs. MLP
To isolate the true scientific benefit of learnable univariate B-splines on edges versus standard matrix multiplications with static activations:
- Both `KANRegressor` and `MLPRegressor` employ the **identical 3,360-parameter convolutional backbone** (`ConvFeatureExtractor`).
- Both extract the exact same 16-dimensional latent feature vector.
- Both heads have identical layer width topology: `16 -> 8 -> 1`.
- The performance delta between KAN and MLP in future authorized training will therefore isolate the inductive bias of spline basis functions rather than differences in feature representation or backbone depth.

### B. Sanity Baseline: Mean Predictor
- `MeanPredictorBaseline` (`src.kan.kan_model.py`, line 230) computes $\mu_{y,\text{train}} = \frac{1}{N}\sum_{i \in \text{Train}} y_i$ strictly from the 20 training subjects in each fold.
- For all held-out test windows, it predicts constant $\hat{y} = \mu_{y,\text{train}}$.
- **Pearson Handling:** Because $\sigma_{\hat{y}} = 0$, Pearson correlation $r$ is mathematically undefined ($\frac{0}{0}$). A defensive fallback $r \equiv 0.0$ is enforced in code to prevent division-by-zero crashes.

---

## 3. Formal Audit of Classical Autocorrelation Implementation Gap

Phase 5 Task 8 explicitly instructs:
> *"The previous Phase 4 report identified a specification gap for the classical autocorrelation baseline. Do not invent its algorithm and present it as an established baseline. If a previously approved, sufficiently specified implementation now exists, audit and evaluate it. Otherwise: Report it as not implemented or not evaluated; list the missing filtering, lag-search, peak-selection, and harmonic-handling specifications; do not claim a complete comparison against autocorrelation."*

### Detailed Audit Finding:
No approved algorithmic specification for classical radar autocorrelation exists in the repository. Unassisted autocorrelation on chest-wall displacement is mathematically ill-posed due to severe respiration-to-cardiac harmonic interference.

### Missing Technical Specifications:
1. **Cardiac Band Separation Filter:** High-amplitude chest motion from respiration (typically $0.15 - 0.4\text{ Hz}$, with amplitudes $10 - 50\times$ larger than heartbeat displacement) creates strong autocorrelation lobes. The filter order, group-delay characteristics, and attenuation depth required to isolate cardiac micro-Doppler motion without phase distortion are unspecified.
2. **Lag Search Range:** The exact lag search boundaries $[\tau_{\min}, \tau_{\max}]$ corresponding to physiological cardiac rates (e.g., $35 - 185\text{ BPM} \implies \tau \in [0.324\text{ s}, 1.714\text{ s}]$, or $108 - 571\text{ samples}$ at $333.33\text{ Hz}$) must be formalized.
3. **Respiration Harmonic Cancellation:** In resting conditions, the 2nd harmonic ($2f_R$) and 3rd harmonic ($3f_R$) of respiration frequently fall in the $0.6 - 1.2\text{ Hz}$ band, directly overlapping resting heart rates ($36 - 72\text{ BPM}$). Without an approved adaptive harmonic rejection algorithm, classical autocorrelation selects the breathing harmonic peak, producing unrepresentative and artificially depressed baseline results.
4. **Peak Selection & Prominence Criteria:** A mathematically unambiguous rule defining whether to select the first post-zero peak, the global maximum in $[\tau_{\min}, \tau_{\max}]$, or a prominence-thresholded peak is missing.

### Conclusion:
In compliance with scientific reporting rules, classical autocorrelation is formally recorded as **`NOT IMPLEMENTED / NOT EVALUATED`**. No speculative or ad-hoc autocorrelation numbers will be claimed.
