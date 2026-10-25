# PHASE 5: COMPREHENSIVE SUBJECT-INDEPENDENT KAN TRAINING & BASELINE AUDIT REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Execution Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer, Scientific ML Auditor & Reproducibility Reviewer  
**Stage Verdict:** **BLOCKED — PHASE 2A GATE OPEN OR TRAINING AUTHORIZATION MISSING**  

---

## 1. Executive Summary

Phase 5 was initiated to evaluate the proposed Kolmogorov–Arnold Network (KAN) regression framework and comparison baselines (CNN, MLP, Mean Predictor) on the VITALSENSE 120-GHz FMCW radar dataset under a strict 24-fold Leave-One-Subject-Out (LOSO) cross-validation protocol.

In accordance with Phase 5 Section 1 mandatory governance rules:
1. The **Phase 2A Finalization Gate was confirmed to be officially `OPEN`** in `outputs/phase2a/step2b_consistency_audit.md`.
2. The user has **not granted explicit authorization** to close the gate or export persistent real-data training tensors.
3. Therefore, **real-data model fitting was strictly withheld**. In compliance with scientific reproducibility and anti-fabrication standards, no model checkpoints, training logs, or prediction CSVs were fabricated.
4. All non-training verification tasks were executed in full:
   - Complete inventory and label audit of all 1,029 accepted windows and 27 rejected windows.
   - Comprehensive audit of all 24 LOSO cross-validation folds (0.0% data leakage verified).
   - Empirical model capacity and CPU inference latency benchmarking.
   - Automated test suite execution: **100 / 100 tests passed (100%)**.

---

## 2. Gate Decision & Authorization Audit

| Audit Item | Inspection Finding | Governance Action |
| :--- | :--- | :--- |
| **Phase 2A Gate Status** | Officially **`OPEN`** (`outputs/phase2a/step2b_consistency_audit.md`, line 9) | Real-data training cannot proceed automatically. |
| **User Authorization** | User provided Phase 5 instructions subject to gate closure, without explicit closure approval | Real-data training blocked; non-training checks authorized. |
| **Hardware Clock Sync** | `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` operational convention | Nominal alignment documented as experimental limitation. |
| **Bedside Monitor HR** | Systematic $+6.21\text{ s}$ delay confirmed by cross-correlation | Bedside monitor HR permanently disqualified as ground truth. |
| **Training Tensors** | No persistent binary tensors exported to disk | Anti-leakage and gate integrity preserved. |

---

## 3. Dataset & Reference Label Audit

- **Subject Cohort:** 24 healthy human subjects (`S01` to `S24`).
- **Experimental Conditions:** 48 total recordings (24 `rest`, 24 `post_exercise`).
- **Radar Sampling:** $f_s \approx 333.333\text{ Hz}$ ($T_s = 3.0\text{ ms}$), 120-GHz FMCW micro-Doppler radar.
- **Reference ECG Sampling:** $f_{s,\text{ECG}} = 1,000\text{ Hz}$.
- **Window Segmentation:** 10.0-second window length, 5.0-second stride ($50\%$ overlap).
- **Window Counts:**
  - Total candidate windows: **1,056** ($22\text{ windows/recording} \times 48$).
  - Accepted windows: **1,029** ($97.44\%$).
  - Disqualified windows: **27** ($2.56\%$), all during post-exercise recovery due to electrode noise ($\text{Coverage}_{\text{RR}} < 85\%$ or $\Delta t_{\text{gap}} > 3.0\text{ s}$).
- **Ground Truth Derivation:** Harmonic mean of detected ECG R-peaks ($\text{HR}_{\text{ref}} = 60 / \overline{RR}$).

---

## 4. LOSO Cross-Validation Partitioning & Leakage Audit

A comprehensive structural audit of the 24 evaluation folds confirmed:
- **Coupled Condition Holding:** Both `rest` and `post_exercise` sessions of test subject $S_k$ are held out simultaneously in fold $k$.
- **Validation Subset Rule:** Deterministic cyclic selection of 3 validation subjects from the 23-subject training pool (e.g., 20 training subjects, 3 validation subjects, 1 test subject).
- **Target & Feature Normalization:** Normalization parameters ($\mu, \sigma$) are estimated **strictly on the 20 training subjects**.
- **Data Leakage:** **0.0% data leakage**. Every subject is evaluated in held-out test position exactly once, summing to exactly 1,029 windows.

---

## 5. Model Capacity & Empirical Latency Benchmark

Inference latency and parameter counts were benchmarked on the host CPU over 200 timed forward passes:

| Model Architecture | Input Modality | Trainable Parameters | Float32 Weight Size | Mean CPU Latency | Real-Time Factor (RTF)* |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **KANRegressor** (Proposed) | 14 Features | **4,720** | **18.88 KB** | **2.368 ms** | $0.00047$ |
| **MLPRegressor** (Baseline) | 14 Features | **3,505** | **14.02 KB** | **1.360 ms** | $0.00027$ |
| **CNNRegressor** (Baseline) | Raw Radar (3,333) | **3,377** | **13.51 KB** | **1.123 ms** | $0.00022$ |
| **MeanPredictor** (Sanity) | Summary Statistic | **0** | **0.00 KB** | **0.002 ms** | $< 0.000001$ |
| **Classical Autocorrelation** | Temporal Signal | 0 | 0.00 KB | *Unimplemented* | *N/A* |

*\*Real-Time Factor (RTF) relative to 5.0 s stride. RTF $\ll 1.0$ confirms suitability for edge deployment.*

---

## 6. Training Output Inventory Status

Per Phase 5 Section 9 rules, all empirical training outputs that could not be generated due to the gate block are formally cataloged:
- `outputs/phase5/run_001/checkpoints/`: **NOT GENERATED (0 CHECKPOINTS SAVED)**
- `outputs/phase5/run_001/training_history/`: **NOT GENERATED (REAL-DATA TRAINING BLOCKED BY GATE)**
- `outputs/phase5/run_001/fold_metrics.csv`: **NOT GENERATED (REAL-DATA TRAINING BLOCKED BY GATE)**
- `outputs/phase5/run_001/per_subject_metrics.csv`: **NOT GENERATED (REAL-DATA TRAINING BLOCKED BY GATE)**
- `outputs/phase5/run_001/heldout_predictions.csv`: **NOT GENERATED (REAL-DATA TRAINING BLOCKED BY GATE)**

Zero data files or metrics were fabricated.

---

## 7. Automated Testing & Verification Record

The complete test suite of 100 automated unit and integration tests was executed:
- **Result:** **100 passed, 0 failed** in 26.47 seconds.
- **Coverage:** Verified signal quality indices, ECG R-peak processing, 0.8–3.0 Hz radar filtering, 24-fold LOSO isolation, target normalizer leakage guards, KAN/MLP/CNN parameter counts and forward passes, constant-prediction Pearson fallback, and governance gate blocker enforcement.

---

## 8. Path to Unblocking Real-Data Training

To authorize and execute real-data 24-fold LOSO training, the user must explicitly provide:
1. Formal statement approving the **closure of the Phase 2A Finalization Gate** under the documented `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` convention and $+6.21\text{ s}$ monitor HR delay disqualification.
2. Formal **authorization to export persistent supervised ML tensors and fit models** on real VITALSENSE data.

Upon receipt of this explicit directive, the 24-fold LOSO training script can be executed immediately.
