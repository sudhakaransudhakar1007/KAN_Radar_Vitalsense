# PHASE 4B: FINAL AUDIT REPORT & SCIENTIFIC TRAINING READINESS REVIEW

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 4B — Targeted Implementation Audit and Training Readiness Review  
**Audit Run ID:** `audit_run_001`  
**Execution Date:** October 15, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer, Scientific ML Auditor, & Reproducibility Reviewer  

---

## 1. Final Audit Verdict

**FINAL VERDICT:**
### **2. AUDIT PASSED WITH DOCUMENTED LIMITATIONS — GATE DECISION REQUIRED**

---

## 2. Evidence Supporting the Verdict

### A. Items That Passed Verification (Audit Passed):
1. **Authentic B-Spline KAN Implementation:**
   The `KANLayer` in `src/kan/kan_layer.py` was verified to be a mathematically authentic, differentiable implementation of the recursive Cox-de Boor cubic B-spline algorithm ($k=3$, uniform knot vector $G=5$, 4,720 total parameters). It is **not** an MLP substitute.
2. **Controlled Comparative Baselines:**
   Both `MLPRegressor` (3,505 parameters) and `MeanPredictorBaseline` (0 parameters) are functional and provide principled benchmarks for ablation.
3. **Exact Dataset Window Arithmetic:**
   The 10.0-second window length (3,333 samples at exact $f_s = 1000/3$ Hz), 5.0-second stride (1,667 samples), and 4.98-second trailing tail (1,660 samples) were verified with 0 discrepancy across all 48 recordings. Exactly 1,029 unique valid windows exist in `accepted_window_manifest.csv`.
4. **Subject-Independent LOSO Isolation:**
   All 24 folds ($VS01$ through $VS24$) were audited. Zero subject leakage exists across training and testing partitions ($0\%$). Both Resting and Apnea recordings of the held-out subject are isolated together.
5. **Governance Compliance:**
   No real-data training occurred. No persistent tensors were exported. No previous phase outputs were overwritten.

### B. Documented Limitations (Gate Decision Required):
1. **Synthetic Benchmark Scalability Limitation (Defect Diagnosed):**
   The synthetic benchmark produced an MAE of $\approx 68.6$ BPM for KAN despite high Pearson $r$. The audit proved this is due to unnormalized target scaling and short training horizons under Huber loss (causing predictions to hover around $3.85$ BPM). This proves code execution and gradient flow, but **not** meaningful calibrated physiological learning. Target normalization and output bias initialization are mandatory before real-data training.
2. **Absence of Physical Hardware Clock Synchronization:**
   Zero hardware trigger or clock synchronization markers exist in the 96 MAT files. Sample-to-sample alignment relies on the unverified operational convention that $t_0 = 0.0$ s.
3. **Phase 2A Finalization Gate Remains Open:**
   The Phase 2A Finalization Gate remains officially **`OPEN`** in `outputs/phase2a/step2b_consistency_audit.md`. Real-data persistent supervised training cannot proceed without explicit user gate approval.

---

## 3. Next Authorized Action

The next scientifically authorized action is:

1. **User Gate Decision:** The user reviews this Phase 4B targeted audit report and decides whether to formally close the Phase 2A Finalization Gate under the documented `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` convention.
2. **Pre-Training Enhancements:** Upon gate closure, implement target z-score normalization and output bias initialization in `loso_evaluator.py` to ensure proper convergence.
3. **Authorized Real-Data LOSO Training:** Execute the 24-fold LOSO training of KANRegressor, MLPRegressor, and MeanPredictorBaseline on the 1,029 accepted radar windows.
