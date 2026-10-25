# PHASE 6: DISCREPANCY & CORRECTIVE ACTION REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  

---

## 1. Executive Summary

In accordance with Phase 6 Task 11 and scientific auditing standards, all discrepancies, documentation inconsistencies, mathematical misstatements, and test flakiness identified during the independent re-verification of Phase 2A through Phase 5 were logged.

Every registered item includes the historical claim, the independently verified physical reality, the root cause, the scientific severity, and the specific corrective action taken or recommended.

---

## 2. Master Discrepancy & Corrective Action Register

### Discrepancy 01: Inverted Condition Distribution of Disqualified Windows
- **Historical Claim (Phase 5 Report):**
  `outputs/phase5/run_002/dataset_validation_report.md` (Section 4) asserted:
  > *"All 27 disqualified windows occurred during Apnea sessions under high physiological stress. All 528 candidate windows from Resting sessions met 100% of SQI criteria."*
- **Independently Verified Reality:**
  Direct programmatic inspection of `rejected_window_manifest.csv` reveals:
  - **25 rejected windows occurred during `Resting` recordings.**
  - **Only 2 rejected windows occurred during `Apnea` recordings.**
  - Rejection breakdown: 22 boundary NaN / delimiter errors, 4 non-physiological RR intervals, 1 RR coverage below $85\%$.
- **Root Cause:** An erroneous narrative assumption by prior auditors that physical stress during apnea was the sole cause of window rejection, ignoring lead-off / boundary NaN delimiter artifacts in resting recordings.
- **Scientific Severity:** Moderate (narrative error; total accepted count of 1,029 windows was mathematically unaffected).
- **Corrective Action:** Documented and corrected in [`dataset_and_label_integrity_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/dataset_and_label_integrity_audit.md).

---

### Discrepancy 02: Misstated ECG Reference Sampling Rate (1,000 Hz vs. 500 Hz)
- **Historical Claim (Phase 5 Report):**
  `outputs/phase5/run_002/dataset_validation_report.md` (Section 2B) stated:
  > *"Reference ECG Sampling: 1,000 Hz (10,000 samples per 10s window)."*
- **Independently Verified Reality:**
  Inspection of raw MAT metadata in `VS01_Resting_Mindray.mat` proves:
  - Field `Fs_ecg` is **$500\text{ Hz}$**.
  - Shape of `ecg_lead2` is $(60000, 1)$ across $120.0\text{ s}$ ($60,000 / 500 = 120.0\text{ s}$).
  - Number of samples per 10-second window is **$5,000\text{ samples}$**, not $10,000$.
- **Root Cause:** Copy-paste from an generic biomedical specification rather than verifying actual MAT metadata.
- **Scientific Severity:** Low for software (the loader dynamically reads `Fs_ecg` from the file itself); High for documentation accuracy.
- **Corrective Action:** Documented in [`dataset_and_label_integrity_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/dataset_and_label_integrity_audit.md).

---

### Discrepancy 03: CNN Parameter Ambiguity (3,360 vs. 3,377)
- **Historical Claim (Phase 4 & 5 Reports):**
  CNN parameters were reported in some tables as 3,360 and in others as 3,377.
- **Independently Verified Reality:**
  - `ConvFeatureExtractor` (backbone) has exactly **3,360 parameters**.
  - `CNNRegressor` (full model with `Dense(1)` readout) has exactly **3,377 parameters** ($3,360 + 16 \text{ weights} + 1 \text{ bias} = 3,377$).
- **Root Cause:** Imprecise labeling of sub-components vs. end-to-end models.
- **Scientific Severity:** Low (both counts are mathematically exact).
- **Corrective Action:** Clarified with layer-by-layer breakdown in [`model_architecture_and_parameter_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/model_architecture_and_parameter_audit.md).

---

### Discrepancy 04: Test Suite Regression in `test_phase4d_completion.py` (99/100 vs. 100/100)
- **Historical Claim (Phase 5 Report):**
  `outputs/phase5/run_002/test_execution_record.md` claimed 100/100 tests passed.
- **Independently Verified Reality:**
  Current test run yields **99 passed, 1 failed**:
  `tests/test_phase4d_completion.py::test_synthetic_end_to_end_integration_pipeline`
  Failed assertion: `assert results["kan_metrics"]["within_5bpm_pct"] >= 90.0` (actual: `87.5%`).
- **Root Cause:** Brittle assertion threshold on a 16-sample synthetic test set ($14/16 = 87.5\%$). The core normalization objective (`kan_mae < 5.0 BPM`) passed.
- **Scientific Severity:** Moderate (causes automated CI test suite to exit with code 1).
- **Corrective Action:** Logged in [`test_execution_record.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/test_execution_record.md). In strict adherence to Phase 6 safety rules, source code was preserved unmodified; recommended adjusting threshold to `>= 80.0%` in post-audit refactoring.

---

### Discrepancy 05: Unimplemented Classical Autocorrelation Baseline
- **Historical Claim (Phase 4 / 5 Objectives):**
  Classical autocorrelation was listed as a required comparison baseline.
- **Independently Verified Reality:**
  Zero implementation exists in `src/`. The method cannot operate on raw radar displacement without an approved respiration harmonic cancellation filter.
- **Root Cause:** Open technical specification gap.
- **Scientific Severity:** Moderate (prevents classical-vs-neural comparison).
- **Corrective Action:** Formally cataloged in [`autocorrelation_baseline_gap.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/autocorrelation_baseline_gap.md) with 6 explicit unresolved technical prerequisites.
