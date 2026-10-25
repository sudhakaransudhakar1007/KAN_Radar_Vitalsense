# PHASE 4B: ERROR LOG & AUDIT DEFECT REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Audit Stage:** Phase 4B — Issue and Defect Tracking  
**Audit File:** `outputs/phase4/audit_run_001/error_log.md`  

---

## 1. Audited Issues Register

| Issue ID | Severity | Category | Description | Root Cause | Status & Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISS-P4B-01** | CRITICAL (METHODOLOGICAL) | Synthetic Benchmark | Synthetic benchmark showed high Pearson $r$ ($>0.85$) but MAE $\approx 68.6$ BPM. | Targets unnormalized ($55-90$ BPM); Huber loss gradient clipped ($\pm 1.0$); weights initialized near 0; only 5 epochs. Outputs reached only $3.85$ BPM, yielding Bias = $-69.37$ BPM. | **RESOLVED & DOCUMENTED:** Proves code execution only. Required mitigation for real training: target z-score normalization and output bias initialization to $\bar{y}_{\text{train}}$. |
| **ISS-P4B-02** | MINOR (DOCUMENTATION) | Architecture Comments | Informal code comments in `kan_model.py` stated Conv1 output shape as `833` and Conv2 as `104`. | Integer division truncation ($3333 // 4 = 833$) vs. TensorFlow `"same"` padding ceiling division ($\lceil 3333 / 4 \rceil = 834$, $\lceil 417 / 4 \rceil = 105$). | **RESOLVED & RECONCILED:** Actual runtime tensor graph verified: $834 \to 417 \to 105 \to 52 \to 26 \to 16$. Code comment reconciled in audit report. |
| **ISS-P4B-03** | INFORMATIONAL | Constant Prediction Metric | Pearson correlation for `MeanPredictorBaseline` evaluates to $\frac{0}{0} = \text{NaN}$ due to zero prediction variance ($\sigma_{\hat{y}} = 0$). | Mathematical definition of Pearson $r$. | **DOCUMENTED:** Framework uses programmatic fallback convention ($r = 0.0$ when $\sigma \le 10^{-6}$). Clarified in documentation. |
| **ISS-P4B-04** | BLOCKING (GOVERNANCE) | Governance Gate | Real-data persistent supervised training is blocked. | Phase 2A Finalization Gate status is officially `OPEN` in `step2b_consistency_audit.md`. | **ENFORCED:** Mandatory Rule 4 observed; real-data training withheld until formal user gate closure. |
| **ISS-P4B-05** | SCIENTIFIC LIMITATION | Hardware Synchronization | Zero physical hardware trigger or clock synchronization channels exist across 96 MAT files. | Independent hardware oscillators on radar digitizer and Mindray monitor. | **DOCUMENTED & TAGGED:** All windows cataloged under `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` operational assumption. |
