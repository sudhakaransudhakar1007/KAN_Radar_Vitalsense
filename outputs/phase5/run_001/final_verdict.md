# PHASE 5: FINAL SCIENTIFIC VERDICT & GATE DECISION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Execution Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer, Scientific ML Auditor & Reproducibility Reviewer  

---

## FINAL VERDICT

# `BLOCKED — PHASE 2A GATE OPEN OR TRAINING AUTHORIZATION MISSING`

---

## 1. Governance Justification & Gate Inspection

In strict adherence to the project execution protocol and scientific reproducibility standards, real-data model training was **BLOCKED** based on the following findings:

1. **Phase 2A Finalization Gate Remains Officially OPEN:**
   Inspection of `outputs/phase2a/step2b_consistency_audit.md` confirms that the Phase 2A Finalization Gate status is **`OPEN`** (reconciliation partial, addendum required before finalization, supervised-label generation not yet approved, hardware clock synchronization unverified).
2. **Explicit User Training Authorization is Missing:**
   The user prompt instructed the agent to proceed *"subject to explicit Phase 2A gate closure and real-data training authorization"* and specifically mandated: *"If the gate remains OPEN or authorization is absent, do not train on real data. Produce a BLOCKED verdict, explain the exact missing authorization, and complete only non-training checks. Do not close the gate automatically."*
3. **No Automatic Gate Closure:**
   Per mandatory governance rules, the AI assistant cannot unilaterally or automatically close a governance gate. Gate closure requires explicit human investigator sign-off.

---

## 2. Non-Training Verification Status

While real-data model fitting was blocked, all non-training validation tasks were executed and verified with zero fabrication:

- [x] **Dataset & Reference Label Audit:**
  - 24 subjects, 48 recording sessions.
  - 1,029 accepted windows, 27 rejected windows (all due to audited SQI thresholds: $< 85\%$ RR coverage or $> 3.0\text{ s}$ gap).
  - Harmonic mean reference heart rate ($60 / \overline{RR}$).
  - Permanent disqualification of bedside monitor HR due to confirmed $+6.21\text{ s}$ smoothing delay.
  - Operational timing convention preserved: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.
- [x] **LOSO Cross-Validation Integrity Audit:**
  - 24 evaluation folds with coupled condition holding (`rest` and `post_exercise` held out together).
  - Deterministic 3-subject cyclic validation pool per fold.
  - Training-fold-only target normalization (Z-score parameters $\mu, \sigma$ derived strictly from 20 training subjects).
  - Verified **0.0% data leakage** across subjects.
- [x] **Training Configuration Standardized:**
  - Adam optimizer ($\eta = 10^{-3}$, weight decay $= 10^{-4}$), batch size 16, MSE loss on normalized targets, patience 7 epochs on validation MSE.
- [x] **Model Capacity & Empirical CPU Latency Benchmark:**
  - `KANRegressor`: 4,720 parameters, 2.368 ms/sample latency.
  - `MLPRegressor`: 3,505 parameters, 1.360 ms/sample latency.
  - `CNNRegressor`: 3,377 parameters, 1.123 ms/sample latency.
  - `MeanPredictorBaseline`: 0 parameters, 0.002 ms/sample latency.
  - `Classical Autocorrelation`: Explicitly documented implementation gap.
- [x] **Checkpoint & Output Manifest Audited:**
  - 0 model checkpoints saved.
  - Real-data training outputs (`fold_metrics.csv`, `per_subject_metrics.csv`, `heldout_predictions.csv`, `training_history/`) formally recorded as **NOT GENERATED**.
- [x] **Automated Test Suite Verified:**
  - **100 / 100 tests passed** across 13 modules in 26.47 seconds.

---

## 3. Mandatory Requirements to Lift the Block

To close the Phase 2A Finalization Gate and authorize Phase 5 real-data training, the user must explicitly submit:

1. **Formal Gate Closure Statement:**
   > *"I approve the formal closure of the Phase 2A Finalization Gate under the documented UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 operational convention and the permanent disqualification of bedside monitor HR."*
2. **Explicit Real-Data Training Authorization:**
   > *"I authorize the export of persistent supervised ML tensors and the execution of real-data 24-fold LOSO training for the KAN, CNN, MLP, and baseline models."*

Until both statements are explicitly provided, the framework will remain in its verified, pre-training state.
