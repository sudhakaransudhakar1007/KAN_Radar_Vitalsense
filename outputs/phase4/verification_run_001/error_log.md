# PHASE 4C: ERROR LOG & VERIFICATION ISSUE REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Verification Stage:** Phase 4C — Error and Discrepancy Tracking  
**Verification File:** `outputs/phase4/verification_run_001/error_log.md`  

---

## 1. Verified Issue Tracking Table

| Issue ID | Severity | Category | Description & Evidence File | Root Cause | Status & Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISS-P4C-01** | CRITICAL | Benchmark | Synthetic benchmark produces high Pearson $r$ ($>0.85$) but MAE $\approx 63 - 69$ BPM. Evidence: `synthetic_test_predictions.csv`. | Targets unnormalized ($55-90$ BPM); Huber loss gradient clipped ($\pm 1.0$); weights initialized near 0; short training horizon. Models predict $\approx 10$ BPM, producing Bias $\approx -63$ BPM. | **VERIFIED & MITIGATION MANDATED:** Target z-score normalization and output bias initialization to $\bar{y}_{\text{train}}$ are mandatory prior to real-data training. |
| **ISS-P4C-02** | INFORMATIONAL | Metrics | Pearson correlation for `MeanPredictorBaseline` evaluates to $\frac{0}{0} = \text{NaN}$ due to zero prediction variance. Evidence: `synthetic_metric_recalculation.md`. | Mathematical definition of Pearson correlation. | **VERIFIED & DOCUMENTED:** Explicit code fallback in `loso_evaluator.py` returns $r = 0.0$ when $\sigma_{\hat{y}} \le 10^{-6}$. Documented as programmatic convention. |
| **ISS-P4C-03** | MINOR | Documentation | Informal inline comments in `kan_model.py` stated Conv1 output shape as `833` and Conv2 as `104`. Evidence: `architecture_reverification.md`. | Integer division truncation ($3333 // 4 = 833$) vs. TensorFlow `"same"` padding ceiling division ($\lceil 3333 / 4 \rceil = 834$). | **VERIFIED & RECONCILED:** Runtime tensor graph confirmed: $834 \to 417 \to 105 \to 52 \to 26 \to 16$. Documented in audit and verification reports. |
| **ISS-P4C-04** | BLOCKING | Governance | Real-data persistent supervised training is blocked. Evidence: `outputs/phase2a/step2b_consistency_audit.md`. | Phase 2A Finalization Gate status is officially `OPEN`. Mandatory Rule 4 prohibits training without formal gate closure. | **ENFORCED:** Model training on real radar signals withheld. All pipelines verified via synthetic validation. |
| **ISS-P4C-05** | SCIENTIFIC | Hardware Timing | Physical hardware clock synchronization is unverified. Evidence: 96 raw MAT files. | Absence of shared trigger or clock channels between radar and Mindray digitizers. | **VERIFIED & TAGGED:** All windows cataloged under `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` operational assumption. |
