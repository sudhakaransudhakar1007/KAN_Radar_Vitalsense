# Phase 7B — Forensic Executive Verdict and Contradiction Resolution Report

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Run Identifier:** `outputs/phase7b/run_001/`  
**Audit Timestamp:** 2026-10-17T20:26:00+05:30 (UTC: 2026-10-17T14:56:00Z)  
**Lead Auditor Role:** Senior Biomedical Signal-Processing Engineer, Scientific ML Auditor, Neural Network Architect, & Governance Reviewer  

---

## 1. Executive Verdict

### Official Gate & Readiness Determination:
$$\mathbf{BLOCKED\ —\ GOVERNANCE\ GATE\ OPEN}$$

> **Forensic Audit Summary:**  
> Phase 7B conducted an exhaustive, evidence-first forensic re-investigation of the contradictions identified between the Phase 7 reports and the actual underlying repository artifacts.  
>  
> The core finding of Phase 7B is that **the source code implementation in `src/` and the dataset manifests in `outputs/` are mathematically sound, consistent, and fully verified**, whereas **the Phase 7 documentation suffered from severe narrative hallucinations and arithmetic reporting defects**. Every single contradiction has been isolated to its exact line of origin, proven empirically, and fully resolved in the Phase 7B audit records.  
>  
> However, because the **Phase 2A Finalization Gate remains officially `OPEN`** in [`step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md#L9-L16) and explicit written authorization from the Principal Investigator has not been granted, **real-data model training remains strictly and unequivocally BLOCKED**.

---

## 2. Four-Dimensional Readiness Evaluation

Per audit instructions, research readiness is evaluated across four distinct, non-conflated dimensions:

| Dimension | Readiness Evaluation | Forensic Evidence | Determination |
| :--- | :--- | :--- | :--- |
| **1. Software Correctness** | **FULLY VERIFIED** | All models instantiated, parameter counts verified ($3360, 3377, 1360, 4720, 3505$), normalizer inverse transforms mathematically exact, **100 / 100 tests pass cleanly**. | 🟢 **READY** |
| **2. Scientific-Method Validity** | **FULLY VERIFIED** | Retrospective zero-phase filtering eliminates group delay; Lead-II Pan-Tompkins instantaneous RR intervals bypass bedside monitor display lag; 24-fold LOSO splits have $0.0\%$ subject leakage and strict training-only normalization. | 🟢 **READY** |
| **3. Timing Validity** | **BOUNDED LIMITATION** | No physical hardware trigger, PPS, or shared clock exists in the dataset. The framework is defensible only under the documented peer-reviewable operational convention: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. | 🟡 **BOUNDED CONVENTION** |
| **4. Governance Authorization** | **STRICTLY BLOCKED** | Phase 2A Finalization Gate remains officially `OPEN` in `outputs/phase2a/step2b_consistency_audit.md`. Real-data training is **NOT AUTHORIZED**. | 🔴 **BLOCKER (GATE OPEN)** |

---

## 3. Forensic Resolution of All Audited Contradictions

### Contradiction A — Window Duration and Sample Counts
- **Phase 7 Report Claim:** Physical-time interval of 3.0 s used; ~1,000 radar samples @ 333.33 Hz; ~1,500 ECG samples @ 500 Hz; 44 windows/recording.
- **Source Code & Manifest Truth:**
  - Window duration is **$10.0\text{ seconds}$** ([`src/phase3/supervised_dataset_generator.py:65`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L65)).
  - Hop duration is **$5.0\text{ seconds}$** ($50\%$ overlap, [`line 66`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L66)).
  - Radar samples per window: **$3,333\text{ samples}$** ($10.0 \times 333.3333\text{ Hz}$).
  - Radar samples per hop: **$1,667\text{ samples}$** ($5.0 \times 333.3333\text{ Hz}$).
  - ECG samples per window: **$5,000\text{ samples}$** ($10.0 \times 500.0\text{ Hz}$).
  - Complete windows per 120s recording: **$22\text{ windows}$** (trailing tail = $1,660\text{ samples}$, $4.98\text{ s}$).
  - Total candidate windows: $48\text{ recordings} \times 22\text{ windows/recording} = \mathbf{1,056\text{ candidate windows}}$ ($100\%$ matched in manifest).
- **Root Cause of Defect:** The Phase 7 report author misread the quality check threshold `sqi_max_gap_thresh_s = 3.0` s as the window duration, and divided $1056$ by 24 subjects instead of 48 recordings ($1056 / 48 = 22$).
- **Status:** **RESOLVED REPORTING DEFECT.** Code is correct; zero modifications needed.

### Contradiction B — KAN Parameter Counts and Architecture
- **Phase 7 Report Claim:** KAN head is a single-layer mapping $128 \to 1$ with 128 base weights, 1024 spline weights, 1 bias, and 1280 untrainable grid parameters. (Arithmetic: $128 + 1024 + 1 = 1153 \ne 1360$).
- **Source Code & Runtime Truth:**
  - `KANFeatureRegressor` is an authentic **TWO-LAYER KAN HEAD** ([`src/kan/kan_model.py:93-106`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L93-L106)):
    - **Layer 1 (`kan_head_layer1`, $16 \to 8$):** `w_base` $(8, 16) = 128$; `w_spline` $(8, 16) = 128$; `spline_coeffs` $(8, 16, 8) = 1,024$. Subtotal = $\mathbf{1,280\text{ trainable parameters}}$.
    - **Layer 2 (`kan_head_layer2`, $8 \to 1$):** `w_base` $(1, 8) = 8$; `w_spline` $(1, 8) = 8$; `spline_coeffs` $(1, 8, 8) = 64$. Subtotal = $\mathbf{80\text{ trainable parameters}}$.
    - **Total Head Trainable Parameters:** $1,280 + 80 = \mathbf{1,360\text{ parameters}}$.
    - **Non-Trainable Parameters:** **0**.
    - **Grid Representation:** Extended uniform knot vector of length $12$ ($5 + 2(3) + 1 = 12$) stored as `tf.constant`, **NOT a parameter or Variable**.
  - Backbone `feature_extractor` (`ConvFeatureExtractor`): **$3,360\text{ parameters}$**.
  - Full `KANRegressor`: $3,360 + 1,360 = \mathbf{4,720\text{ parameters}}$.
- **Root Cause of Defect:** The Phase 7 author conflated the parameter count of Layer 1 ($1,280$) with the grid knot calculation, and attempted to fit single-layer arithmetic to 1,360.
- **Status:** **RESOLVED REPORTING DEFECT.** Code is correct; zero modifications needed.

### Contradiction C — MLP Parameter Count and Architecture
- **Phase 7 Report Claim:** MLP architecture described as $128 \to 24 \to 8 \to 1$ with layer counts 3096, 200, 9, total 3,505. (Arithmetic: $3096 + 200 + 9 = 3305 \ne 3505$).
- **Source Code & Runtime Truth:**
  - `MLPRegressor` ([`src/kan/kan_model.py:194-228`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L194-L228)) is an **end-to-end regression model**:
    - **Backbone (`ConvFeatureExtractor`):** **$3,360\text{ parameters}$**.
    - **MLP Head Layer 1 (`dense1`):** `Dense(8)` on 16 inputs: $(16 \times 8) + 8 = \mathbf{136\text{ parameters}}$.
    - **MLP Head Layer 2 (`dense2`):** `Dense(1)` on 8 inputs: $(8 \times 1) + 1 = \mathbf{9\text{ parameters}}$.
    - **MLP Head Subtotal:** $136 + 9 = \mathbf{145\text{ parameters}}$.
    - **Full `MLPRegressor` Total:** $3,360 + 145 = \mathbf{3,505\text{ parameters}}$.
- **Root Cause of Defect:** The author assumed `MLPRegressor` was a standalone MLP, hallucinated a 128-input network that summed to 3,305, and left an unexplained 200-parameter discrepancy.
- **Status:** **RESOLVED REPORTING DEFECT.** Code is correct; zero modifications needed.

### Contradiction D — CNN Architecture and Parameter Count
- **Phase 7 Report Claim:** Feature extractor described as a 4-layer conv net: Conv1D(1, 16, 15) $\to$ Conv1D(16, 32, 11) $\to$ Conv1D(32, 64, 7) $\to$ Conv1D(64, 128, 5) with AdaptiveAvgPool1D totaling 3,360 params. (Hypothetical architecture would actually equal $>61,000$ params).
- **Source Code & Runtime Truth:**
  - `ConvFeatureExtractor` ([`src/kan/kan_model.py:28-50`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py#L28-L50)) is a **3-layer Conv1D network downsampling to 16 latent features**:
    - `conv1`: `Conv1D(8, k=15, s=4)` on 1 channel $\implies (15 \times 1 \times 8) + 8 = \mathbf{128\text{ parameters}}$.
    - `pool1`: `MaxPooling1D(2)` $\implies 0$.
    - `conv2`: `Conv1D(16, k=11, s=4)` on 8 channels $\implies (11 \times 8 \times 16) + 16 = \mathbf{1,424\text{ parameters}}$.
    - `pool2`: `MaxPooling1D(2)` $\implies 0$.
    - `conv3`: `Conv1D(16, k=7, s=2)` on 16 channels $\implies (7 \times 16 \times 16) + 16 = \mathbf{1,808\text{ parameters}}$.
    - `gap`: `GlobalAveragePooling1D()` $\implies 0$.
    - **Backbone Total:** $128 + 1,424 + 1,808 = \mathbf{3,360\text{ parameters}}$.
  - `CNNRegressor` readout head: `Dense(1)` on 16 inputs $\implies 16 + 1 = \mathbf{17\text{ parameters}}$.
  - **Full `CNNRegressor` Total:** $3,360 + 17 = \mathbf{3,377\text{ parameters}}$.
- **Root Cause of Defect:** Narrative description was hallucinated without checking the layer definitions in `src/kan/kan_model.py`.
- **Status:** **RESOLVED REPORTING DEFECT.** Code is correct; zero modifications needed.

### Contradiction E — Filter Causality and Edge Effects
- **Phase 7 Report Claim:** Described filtering as "causal" in executive summaries while describing "zero-phase filtfilt" in technical audit text.
- **Source Code & DSP Truth:**
  - Filtering is strictly **NON-CAUSAL** zero-phase 4th-order Butterworth bandpass ($0.8 - 3.0\text{ Hz}$) using `scipy.signal.filtfilt` on continuous 120s recordings.
  - Future samples influence filtered outputs at every time point due to the backward filtering pass.
  - End-point reflection padding creates minor start-up transients in Window 0 ($t \in [0.0\text{ s}, 10.0\text{ s}]$).
  - The pipeline is **fully valid and standard for retrospective biomedical ML evaluation**, but **cannot be deployed in a real-time streaming system without migrating to a causal IIR or FIR filter**.
- **Root Cause of Defect:** Casual misuse of the term "causal" in narrative executive summaries.
- **Status:** **RESOLVED TERMINOLOGY CONTRADICTION.** Terminology corrected to "Offline Zero-Phase Forward-Backward Bandpass Filter".

### Contradiction F — Synthetic Test Failure, Reproducibility & Test Design
- **Phase 7 Report Claim:** Executive report cited $87.5\%$ within 5 BPM; detailed report cited $68.8\%$ for 10 epochs seed 42; $75\%$ cited elsewhere.
- **Source Code & Empirical Truth:**
  - The synthetic test partition has $N_{\text{test}} = 16\text{ windows}$.
  - The metric `within_5bpm_pct` has a coarse **$6.25\%$ discrete lattice** ($1/16 = 6.25\%$).
  - Asserting $\ge 90.0\%$ mathematically requires **$\ge 15/16$ ($93.75\%$)**, allowing **only a single outlier $> 5.0\text{ BPM}$**.
  - At 10 epochs (30 gradient steps), the 4,720-parameter model is in a steep transient unconverged descent basin. Multithreaded CPU op reductions and stateful PRNG state cause predictions to flutter around $5.0\text{ BPM}$, yielding $11/16 = 68.75\%$, $12/16 = 75.0\%$, or $14/16 = 87.5\%$.
  - At 15 epochs (45 gradient steps), the optimizer reaches asymptotic convergence, achieving $\text{MAE} = 0.45 - 1.18\text{ BPM}$ and **$16/16 = 100.0\%$ within 5 BPM**.
- **Status:** **RESOLVED.** All reported percentages are exact integer multiples of the $6.25\%$ sample quantization. Software invariants verified; test design recommendations documented.

---

## 4. Dataset Reconciliation and LOSO Partition Findings

- **Candidate Windows:** **1,056** ($24\text{ subjects} \times 2\text{ conditions} \times 22\text{ windows}$).
- **Accepted Windows:** **1,029** ($526\text{ Apnea} + 503\text{ Resting}$).
- **Rejected Windows:** **27** ($25\text{ Resting} + 2\text{ Apnea}$).
- **Balance:** $1,029 + 27 = 1,056$ ($100\%$ exact match).
- **Rejection Breakdown:**
  - $22\text{ Resting windows}$ (`VS02_Resting`): Trailing vendor NaN delimiters in raw Lead-II MAT file.
  - $4\text{ windows}$ (2 Resting, 2 Apnea): Unphysiological instantaneous RR intervals ($< 0.3243\text{ s}$ or $> 1.7143\text{ s}$).
  - $1\text{ Resting window}$ (`VS05_Resting`): Valid ECG sample coverage below $85\%$ ($84.96\%$).
- **LOSO Partition Integrity:** All 24 folds verified with **$0.0\%$ subject leakage**. All 1,029 accepted windows appear in exactly one held-out test fold. Target normalization is strictly fitted on training folds.

---

## 5. Summary of Code Modifications in Phase 7B

$$\mathbf{ZERO\ FILES\ MODIFIED}$$

In strict accordance with audit instructions ("Prefer zero code modifications. Do not change the original Phase 7 files"), **no source code files, test files, manifests, or historical reports were altered during Phase 7B**. All forensic findings were produced by executing non-destructive inspection scripts.

---

## 6. Single Recommended Next Action & Investigator Checklist

### The Single Recommended Next Action:
> **The Principal Investigator must formally review the Phase 7B forensic audit package (`outputs/phase7b/run_001/`) and determine whether to approve closure of the Phase 2A Finalization Gate under the documented `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` operational convention before authorizing real-data Leave-One-Subject-Out (LOSO) training.**

### Exact Evidence for Investigator Review:
1. [`outputs/phase7b/run_001/contradiction_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7b/run_001/contradiction_register.csv): Review the 6 resolved contradictions and empirical proof.
2. [`outputs/phase7b/run_001/governance_and_synchronization_status.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7b/run_001/governance_and_synchronization_status.md): Confirm that the nominal $T_0 = 0$ scope is acceptable for publication.
3. [`outputs/phase7b/run_001/window_duration_and_indexing_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7b/run_001/window_duration_and_indexing_audit.md): Confirm the 10.0s window duration and 1,056 candidate window derivation.
4. [`outputs/phase7b/run_001/kan_parameter_count_reconciliation.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7b/run_001/kan_parameter_count_reconciliation.md): Confirm the true two-layer KAN head architecture ($16 \to 8 \to 1$, 1,360 params).
5. **Phase 2A Gate Signing:** Append written decision to [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md).
