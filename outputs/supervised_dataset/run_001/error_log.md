# Supervised Dataset Generation: Error & Blocker Log

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Supervised Dataset Generation Implementation & Quality Audit  
**Run ID:** `run_001`  
**Execution Timestamp:** 2026-10-15T15:13:00Z  

---

## 1. Governance & Execution Blockers

### Blocker 1: Phase 2A Finalization Gate Open
- **Affected Operation:** Persistent binary training tensor generation (`X_radar.npy`, `y_hr.npy`).
- **Classification:** **`GOVERNANCE_GATE_BLOCKER`** (Mandatory Stop Condition per Rule 4 and Rule 5).
- **Recorded Error:**
  ```text
  LabelGenerationBlockedError: Supervised persistent dataset generation (binary arrays / ML tensors) is BLOCKED:
  Phase 2A Finalization Gate status is 'OPEN' (must be formally CLOSED), and authorization_granted is 'False'.
  In compliance with project execution rules, candidate, accepted, and rejected window manifests were generated
  in dry-run diagnostic mode, but persistent supervised training arrays were withheld.
  ```
- **Technical Action Taken:** Operates in diagnostic dry-run mode. Generates `candidate_window_manifest.csv`, `accepted_window_manifest.csv`, and `rejected_window_manifest.csv`, but halts saving persistent training arrays until formal gate sign-off.

---

## 2. Data-Quality Exclusions & Signal Discrepancies

### Issue 1: Boundary Delimiter NaN in `VS10_Resting_Mindray.mat`
- **Affected Operation:** In-memory delimiter NaN linear interpolation (`ECGReferenceValidator.analyze_missing_samples`).
- **Classification:** **`PHYSIOLOGICAL_DATA_QUALITY_ISSUE`**.
- **Description:** `VS10_Resting_Mindray.mat` contains a single delimiter NaN at sample index `0` (`nan_indices = [0, 501, 1002, ..., 59619]`). Because index 0 has no preceding valid sample within the recording, linear interpolation without boundary extrapolation is impossible.
- **Traceback / Error String:**
  `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`
- **Impact:** All 22 candidate windows of `VS10_Resting` were explicitly rejected and documented in `rejected_window_manifest.csv`.

### Issue 2: Ectopic RR Intervals in `VS16` (Apnea & Resting)
- **Affected Operation:** Window-level physiological bound screening (`compute_window_reference_hr`).
- **Classification:** **`PHYSIOLOGICAL_SIGNAL_ANOMALY`**.
- **Description:** Four 10-second windows in subject `VS16` (`VS16_Apnea` windows 4 and 5; `VS16_Resting` windows 0 and 1) contained premature ventricular beats or local non-physiological intervals ($RR_i < 0.3243\text{ s}$ or $> 1.7143\text{ s}$).
- **Impact:** All 4 affected windows were rejected and documented in `rejected_window_manifest.csv` with reason `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`.

### Issue 3: Marginal Window Coverage in `VS03_Resting` Window 0
- **Affected Operation:** Window-level SQI coverage screening (`compute_window_reference_hr`).
- **Classification:** **`PHYSIOLOGICAL_WINDOW_EDGE_COVERAGE_ISSUE`**.
- **Description:** In `VS03_Resting` window 0 ($t \in [0.0\text{ s}, 10.0\text{ s})$), the valid RR interval coverage was 84.96%, narrowly missing the approved 85.0% threshold.
- **Impact:** Window 0 was rejected with reason `RR_COVERAGE_BELOW_85_PCT (84.96%)`.

### Issue 4: Respiration Duration Discrepancy in `VS24_Resting_Mindray.mat`
- **Affected Operation:** Cross-device duration validation.
- **Classification:** **`METADATA_ARRAY_LENGTH_DISCREPANCY`**.
- **Description:** `VS24_Resting_Mindray.mat` contains 30,600 respiration samples at 256.0 Hz ($119.53125\text{ s}$), representing a 0.46875s mismatch against nominal 120.0s.
- **Impact:** Documented in synchronization manifest. Radar and ECG arrays matched at 120.0s (40,000 and 60,000 samples).

---

## 3. Implementation Code Errors & Bug Fixes During Stage

### Resolved Variable Typo in Initial Run
- **Affected File:** `src/phase3/supervised_dataset_generator.py`, line 202.
- **Classification:** **`CODE_IMPLEMENTATION_TYPO` (Resolved)**.
- **Recorded Traceback:**
  ```text
  Traceback (most recent call last):
    File "src/phase3/supervised_dataset_generator.py", line 410, in <module>
      manifest = generator.execute_dataset_audit()
    File "src/phase3/supervised_dataset_generator.py", line 202, in execute_dataset_audit
      rec_sqi_fail_count += 1
  UnboundLocalError: local variable 'rec_sqi_fail_count' referenced before assignment
  ```
- **Correction:** Replaced `rec_sqi_fail_count` with the defined variable `recording_sqi_fail_count`. Re-executed immediately with exit code 0.
