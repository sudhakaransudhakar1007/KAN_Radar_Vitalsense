# PHASE 4D: ERROR LOG & LIMITATIONS REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 10: Error & Defect Register  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. Phase 4D Defect & Status Register

| Issue ID | Severity | Category | Description | Root Cause | Status & Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISS-P4D-01** | CRITICAL (RESOLVED) | Normalization | Synthetic benchmark produced $\approx 68.6$ BPM MAE due to scale mismatch under Huber loss. | Targets unnormalized ($55-90$ BPM) while outputs started near 0 BPM. | **RESOLVED:** Implemented `TargetNormalizer` in `src/kan/normalization.py`. Fold-specific z-score standardization reduced KAN synthetic MAE from 68.6 to 1.319 BPM. |
| **ISS-P4D-02** | INFORMATIONAL | Architecture | Missing standalone `CNNRegressor` baseline class in model definitions. | `ConvFeatureExtractor` existed (3,360 params) but lacked a standalone single-head baseline class. | **RESOLVED:** Implemented `CNNRegressor` in `src/kan/kan_model.py` (3,377 total params). Verified with automated unit tests. |
| **ISS-P4D-03** | SPECIFICATION GAP | Classical Baseline | Classical autocorrelation baseline is missing from repository. | Project specifications lacked mathematical details on pre-filtering, lag search window, and harmonic suppression. | **DOCUMENTED GAP:** Documented in `baseline_integration_report.md` per Task 3 instructions. An ad-hoc algorithm was not silently substituted. |
| **ISS-P4D-04** | BLOCKING (GOVERNANCE)| Governance Gate | Phase 2A Finalization Gate status is officially `OPEN`. | Step 2B audit concluded with reconciliation partial and unverified hardware timing. | **ENFORCED:** Mandatory Rule 4 observed; real-data model training strictly blocked until formal user approval. |
| **ISS-P4D-05** | SCIENTIFIC LIMITATION | Hardware Timing | Absence of physical hardware trigger or clock synchronization markers in 96 raw MAT files. | Independent hardware oscillators on radar digitizer and Mindray monitor. | **DOCUMENTED & PRESERVED:** All windows cataloged under `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` operational assumption. |
