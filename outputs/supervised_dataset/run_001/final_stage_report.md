# Supervised Dataset Generation: Final Stage Report

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Dataset:** VITALSENSE (Subjects VS01–VS24, Resting and Apnea)  
**Stage:** Supervised Dataset Generation Implementation & Quality Audit  
**Run ID:** `run_001`  
**Output Directory:** `outputs/supervised_dataset/run_001`  
**Execution Timestamp:** 2026-10-15T15:20:00Z  
**Author:** Senior Biomedical Signal Processing & Scientific ML Engineering Team  
**Stage Status:**  
`SUPERVISED DATASET AUDIT & MANIFESTS GENERATED — PERSISTENT ML TENSORS BLOCKED BY PHASE 2A GATE`  

---

## 1. Executive Summary & Core Answers

In strict compliance with the project charter, Mandatory Rules 1–9, and the Phase 2A governance boundaries:

1. **Did supervised dataset generation actually run?**  
   **`EXECUTED` (in Diagnostic Dry-Run Mode).** The pipeline loaded all 48 candidate radar/reference recording pairs, filtered radar signals with the user-approved 0.8–3.0 Hz bandpass filter, segmented all 1,056 candidate windows ($48 \times 22$), performed Pan-Tompkins QRS detection, evaluated window-level SQI, paired instantaneous ECG HR labels, and generated the complete manifest suite.
2. **Did the Phase 2A gate permit persistent dataset generation?**  
   **`BLOCKED`.** Project records confirm that the Phase 2A Finalization Gate remains formally **`OPEN`** (`step2b_consistency_audit.md`). In accordance with Mandatory Rule 4 and Rule 5, saving persistent binary model-training arrays (`X_radar.npy`, `y_hr.npy`) was halted.
3. **Actual Accepted / Rejected Counts:**  
   - **Candidate Windows:** Exactly **1,056 windows** (22 windows/recording $\times$ 48 recordings).
   - **Accepted Windows:** Exactly **1,029 windows (97.44%)** across 47 recordings.
   - **Rejected Windows:** Exactly **27 windows (2.56%)** across 4 recordings.
4. **Label Validity & Synchronization Limitations:**  
   - 100% of accepted labels fall within $[47.52, 82.89]\text{ bpm}$ ($35\text{--}185\text{ bpm}$ bounds). Zero NaNs, zero non-finite values, zero duplicates.
   - Synchronization is **`UNVERIFIED`** at the hardware clock level; pairing relies on the prespecified nominal zero-offset convention ($t_0 = 0.0\text{ s}$).
5. **Tests Run & Actual Results:**  
   - **75 passed, 0 failed in 9.17s** across 10 test suites (48 baseline + 19 Phase 3 + 8 new dataset tests).
6. **Implementation Errors & Unresolved Issues:**  
   - One transient variable typo in prototype execution was identified, corrected, and documented in `error_log.md`.
   - `VS10_Resting` contains a delimiter NaN at sample index 0, causing exclusion of its 22 windows.
   - `VS16` contains 4 non-physiological ectopic RR intervals (rejected).
   - `VS03_Resting` contains 1 window with 84.96% coverage (rejected).
7. **Is the dataset ready for independent scientific review?**  
   **`VERIFIED` (Ready for Audit & Review).** All candidate, accepted, and rejected windows are exhaustively cataloged with complete cryptographic provenance and explicit exclusion rationales.
8. **Machine Learning Model Training:**  
   **`NOT_STARTED`.** Zero KAN, MLP, CNN, or other models were trained.

---

## 2. Status Accounting Across All Stage Tasks

| Task Description | Formal Status | Evidence & Output Artifacts |
| :--- | :---: | :--- |
| **Task 1: Inspect & Plan** | `EXECUTED`, `VERIFIED` | Reusable components audited; `run_manifest.json` and `dataset_generation_config.json` generated. |
| **Task 2: ECG Reference Labels** | `EXECUTED`, `USER_APPROVED` | Pan-Tompkins QRS detection; harmonic mean formula ($60 / \overline{RR}$); documented in `reference_label_audit.md`. |
| **Task 3: Radar Window Generation** | `EXECUTED`, `USER_APPROVED` | 0.8–3.0 Hz bandpass filter; 10s window, 5s hop, 22 windows/rec, 1660-sample tail exclusion. |
| **Task 4: Match Windows & Labels** | `EXECUTED`, `VERIFIED` | Midpoint interval mapping under nominal zero-offset ($t_0 = 0.0\text{ s}$) documented in `synchronization_assumptions_record.md`. |
| **Task 5: QC & Provenance Tracking** | `EXECUTED`, `VERIFIED` | 1,056 candidate records cataloged in `candidate_window_manifest.csv`, `accepted_window_manifest.csv`, and `rejected_window_manifest.csv`. |
| **Task 6: Validate Dataset** | `EXECUTED`, `VERIFIED` | Zero NaNs, zero duplicates; statistics detailed in `dataset_validation_report.md`. |
| **Task 7: Tests & Error Preservation** | `EXECUTED`, `VERIFIED` | 75/75 passing tests documented in `test_execution_record.md`; transient typo logged in `error_log.md`. |
| **Persistent Training Array Storage** | `BLOCKED` | Writable `.npy`/`.h5` tensor export halted pending formal Phase 2A gate closure. |
| **Phase 4 KAN Model Training** | `NOT_STARTED` | Zero models trained. |

---

## 3. Window Segmentation & Excluded Tail Verification

- **Sampling Rate:** $f_s = 333.3333\text{ Hz}$ ($40,000\text{ samples} / 120.000\text{ s}$).
- **Window Length:** $L = \text{round}(10.0 \times 333.3333) = 3333\text{ samples}$.
- **Hop Size:** $H = \text{round}(5.0 \times 333.3333) = 1667\text{ samples}$.
- **Window Indices:** $k \in \{0, 1, \dots, 21\}$ (22 complete windows).
- **Start Indices:** $s_k = k \times 1667 \implies [0, 1667, 3334, \dots, 35007]$.
- **Last Sample Processed:** $35007 + 3333 = 38,340$.
- **Excluded Trailing Tail:** Exactly **1,660 samples ($4.9800\text{ seconds}$)** per recording.
- **Verification:** Candidate 22 would require sample end $36,674 + 3333 = 40,007 > 40,000$. Zero silent zero-padding applied.

---

## 4. Rejection Inventory & Technical Justifications

Exactly **27 of 1,056 windows (2.56%)** were rejected across 4 recordings:

1. **`VS10_Resting` (22 windows, 100% of recording):**
   - **Reason:** `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`.
   - **Cause:** Delimiter NaN at sample index `0` precluded internal linear interpolation without boundary extrapolation.
2. **`VS16_Apnea` (2 windows, windows 4 and 5):**
   - **Reason:** `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`.
   - **Cause:** Ectopic beat cluster with non-physiological intervals ($RR < 0.3243\text{ s}$ or $> 1.7143\text{ s}$).
3. **`VS16_Resting` (2 windows, windows 0 and 1):**
   - **Reason:** `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`.
   - **Cause:** Local ectopic beat or artifact violating physiological boundaries.
4. **`VS03_Resting` (1 window, window 0):**
   - **Reason:** `RR_COVERAGE_BELOW_85_PCT (84.96%)`.
   - **Cause:** First window coverage was 84.96%, falling just short of the 85.0% threshold.

---

## 5. Summary of Physical & Methodological Limitations

1. **Hardware Synchronization:** `UNVERIFIED`. No common clock, TTL trigger, or PPS pulse exists in the 96 files. Nominal alignment ($t_0 = 0.0\text{ s}$) is an operational assumption.
2. **Monitor HR Disqualification:** The Mindray monitor's 120-point `HR` array exhibits a $+6.21\text{ s}$ average display latency and is strictly disqualified.
3. **Apnea Respiratory Correlation:** Inconclusive due to voluntary breath-holding.
4. **Respiration Duration Discrepancy:** `VS24_Resting` contains 30,600 respiration samples ($119.53125\text{ s}$, 0.46875s mismatch).
5. **Subject Independence Requirement:** Random shuffling of windows across subjects is strictly prohibited; evaluation must follow strict subject-stratified splits (LOSO recommended).

---

## 6. Readiness Decision for Moving to Phase 4 (KAN Modeling)

- **Audit & Manifest Readiness:** **COMPLETE & VERIFIED.** All candidate window slices, reference HR labels, and quality manifests are generated and validated.
- **Gate Blocker:** The Phase 2A Finalization Gate remains officially **`OPEN`**.
- **Next User Action Required:**
  To close Phase 3, authorize persistent tensor export, and initiate Phase 4 (KAN Framework Implementation under LOSO cross-validation), the user must explicitly confirm:
  1. **Formal closure of the Phase 2A Finalization Gate.**
  2. **Authorization to export persistent supervised dataset arrays (`X_radar.npy`, `y_hr.npy`).**
  3. **Authorization to initiate Phase 4 model training.**
