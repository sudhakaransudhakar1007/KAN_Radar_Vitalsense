# PHASE 6B.5: EVIDENCE VERIFICATION & PRINCIPAL INVESTIGATOR (PI) DECISION PACKAGE

**Document ID:** `outputs/closure/phase6b5_evidence_verification_and_pi_decision_package.md`  
**Execution Stage:** Phase 6B.5 — Evidence Verification & PI Decision Package  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Investigator:** Senior Biomedical Signal-Processing Researcher, Test Engineer & Research Governance Auditor  
**Scientific Gate Status:** Strictly **`OPEN`** (`outputs/phase2a/step2b_consistency_audit.md`)  
**Real-Data Training Status:** Strictly **`BLOCKED`**  
**Real-Data Label Generation Status:** Strictly **`BLOCKED`**  

---

## 1. Executive Summary & Objective

The objective of Phase 6B.5 is to conduct a complete, independent empirical verification of all pending scientific and methodological decisions, protect audited artifacts, audit ECG reference processing, and deliver a formal Decision Package for the Principal Investigator (PI).

### Key Accomplishments in Phase 6B.5:
1. **D13 Verified (Window-Level Maximum RR Gap Rule):** Independently recomputed window-level RR coverage and gaps across all 48 recordings and all 1,104 candidate windows. Maximum observed window RR gap is $1.2920\text{ s}$. Exactly 0 windows violate the $3.0\text{ s}$ rule. Yield impact is $0/1,104$ ($0.0\%$ yield loss). **Recommendation: RETAIN (Option A).**
2. **D14 Verified (Minimum Valid Beats Per Recording):** Independently recomputed beat counts across all 48 recordings. Minimum beat count is 99 beats (mean: 129.2, median: 130.5). Both 20-beat and 30-beat thresholds accept $48/48$ recordings ($0.0\%$ rejections). **Recommendation: RETAIN (Option A).**
3. **D15 Implemented & Tested (Runner Output Directory Guard):** Applied programmatic safeguards to [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py). Omitting `output_dir` raises `ValueError`; directing to `outputs/phase2a` raises `PermissionError` unless overridden. Automated tests in [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) passed ($3/3$). Original Phase 2A audited baseline files verified strictly bit-for-bit unchanged.
4. **ECG Reference Implementation Harmonization:** Identified an architectural discrepancy where [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) and [`src/phase3/ecg_reference.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py) supported `fill_boundary: bool = True`, but [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py) lacked this keyword. Successfully harmonized `clean_ecg_nans` to accept `fill_boundary` without altering default behavior.
5. **Git Provenance Disentangled:** Verified that `git_commit: "UNKNOWN"` was caused by two distinct factors: (a) absence of the `git` executable on Windows system `PATH`, and (b) absence of a `.git` directory in the repository. Refactored [`src/kan/trainer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py) to provide explicit, granular status strings (`GIT_EXECUTABLE_NOT_FOUND` / `NOT_A_GIT_REPOSITORY`).
6. **Full Test Suite Integrity:** All **189 tests** in the repository regression suite passed with 0 failures, and all 5 dashboard smoke tests passed.
7. **Scientific Governance Preserved:** The Phase 2A/2C gate remains strictly **`OPEN`**. No real ECG labels were generated, and no real radar data training occurred.

---

## 2. Work Package 1: Repository Audit & Cryptographic Evidence Baseline

### 2.1 Repository & Environment Inspection
- **Working Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **Platform:** Windows (Python 3.10.11, TensorFlow 2.19.1, Keras 3.10.0, NumPy 2.2.6, SciPy 1.15.3, Pandas 2.3.1)
- **Version Control Status:**
  - `git` executable is not installed on system `PATH` (`CommandNotFoundException`).
  - `.git` directory is absent in `kan_radar_HR` and in parent workspace.
  - Software and data provenance are verified via explicit cryptographic SHA-256 digests.

### 2.2 Baseline Cryptographic Hashes of Core Audit Files
All key governance and audit artifacts were inspected and verified as present on disk. Zero files were missing:

| File Path | Byte Size | SHA-256 Digest | Status |
| :--- | :---: | :--- | :---: |
| [`outputs/closure/phase2a_2c_readiness_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_2c_readiness_report.md) | 11,510 | `26ad08561c44d9f4a39075e95ced6954f32af02ddb41ac7ac9334c841195ffdc` | VERIFIED |
| [`outputs/closure/pi_decision_list.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_list.md) | 27,158 | `fe4d7d39fdcb651baf59ef5f820f3ed9ae6afd5b133b87c805f8bc4a90180363` | VERIFIED |
| [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) | 2,746 | `a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8` | VERIFIED |
| [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md) | 106,546 | `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f` | VERIFIED (IMMUTABLE) |
| [`outputs/phase2a/sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/sync_validation_results.csv) | 18,349 | `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10` | VERIFIED (IMMUTABLE) |
| [`outputs/closure/proposed_runner_guard.diff`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/proposed_runner_guard.diff) | 1,928 | `2a29882f8229a7b5a66376bcd95458812b0d52150b2050fafff898d682bf4b92` | VERIFIED |
| [`outputs/closure/window_coverage_gate_diagnostic.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_coverage_gate_diagnostic.csv) | 1,538 | `409b7fa0e58431eed256fca607e02c188b78ef2a8d56b7375ff61c3e2a110637` | VERIFIED |

---

## 3. Work Package 2: Decision D13 Verification (Window-Level Maximum RR Gap Rule)

### 3.1 Mathematical Context & Implementation Trace
Decision D13 addresses whether to retain the rule rejecting windows where the maximum RR interval is $\ge 3.0\text{ s}$ ([`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98)), drop it, or adjust it.

Two implementations exist in the codebase:
1. [`src/sync_validation/window_coverage_gate.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/window_coverage_gate.py): Implements interval-overlap coverage fraction across the 10-second window. Any RR interval outside $[0.30\text{ s}, 2.00\text{ s}]$ contributes 0.0s coverage.
2. [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py): Implements midpoint assignment `(t_i + t_{i+1})/2 in [t_start, t_end)`. Rejects window if any interval midpoint is outside $[0.324\text{ s}, 1.714\text{ s}]$ (35–185 BPM), if covered duration $\le 8.0\text{ s}$ ($80\%$), or if $\max(\text{RR}) \ge 3.0\text{ s}$.

### 3.2 Empirical Recomputation Across All 48 Recordings
Using the raw Mindray reference files in `../data/VITALSENSE_120_DATASET` ($N=48$ files, 24 subjects $\times$ 2 conditions), every candidate 10-second analysis window was evaluated:

- **Candidate Window Grid:** $t_{\text{start}} = \text{round}(k \times 5.0, 3)$ for $k = 0, 1, \dots, 22$, yielding exactly 23 windows per 120-second recording.
- **Candidate Denominator:** $48 \text{ recordings} \times 23 \text{ windows} = \mathbf{1,104\text{ candidate windows}}$.

#### Empirical Window Statistics:
- **Maximum Observed Window RR Gap:** $\mathbf{1.2920\text{ s}}$ (observed in subject `VS02_Apnea`).
- **Minimum Observed Window RR Gap:** $\mathbf{0.7640\text{ s}}$.
- **Windows with $\max(\text{RR}) \ge 3.0\text{ s}$:** $\mathbf{0 / 1,104}$ ($0.00\%$).
- **Windows with $\max(\text{RR}) \ge 2.0\text{ s}$:** $\mathbf{0 / 1,104}$ ($0.00\%$).
- **Windows with $\max(\text{RR}) \ge 1.714\text{ s}$ ($35\text{ BPM}$):** $\mathbf{0 / 1,104}$ ($0.00\%$).
- **Window Coverage %:** Mean: **$99.50\%$** (Min: **$84.96\%$**, Max: **$110.28\%$**).
- **Windows with Coverage $> 80\%$ ($> 8.0\text{ s}$):** $\mathbf{1,104 / 1,104}$ ($100.00\%$).
- **Accepted Windows (`window_coverage_gate.py`):** $\mathbf{1,104 / 1,104}$ ($100.00\%$).
- **Accepted Windows (`supervised_dataset_generator.py`):** $\mathbf{1,104 / 1,104}$ ($100.00\%$).
- **Rejected Windows:** $\mathbf{0 / 1,104}$ ($0.00\%$).
- **Harmonic Mean Heart-Rate Range:** $[47.52, 85.24]\text{ BPM}$.

### 3.3 Yield Impact & D13 Recommendation
$$\text{Yield Impact} = \frac{\text{Eligible Windows with 3.0 s Rule}}{\text{Eligible Windows without 3.0 s Rule}} = \frac{1,104}{1,104} = 100.00\% \quad (\text{Yield Loss} = 0.0\%)$$

- **Recommendation:** **RETAIN (Option A: Keep window-level max-gap threshold at 3.0 s).**
- **Scientific Rationale:**
  1. The 3.0-second window rule enforces mathematical consistency with the recording-level SQI rule ($\max(\text{gap}) < 3.0\text{ s}$).
  2. Because the maximum physiological RR interval in this cohort is $1.2920\text{ s}$, the 3.0 s threshold imposes **zero yield penalty** on real VITALSENSE recordings.
  3. It serves as an indispensable safety barrier against undetected beat dropouts, pause episodes, or signal dropouts that might otherwise distort the window harmonic mean heart rate.

---

## 4. Work Package 3: Decision D14 Verification (Minimum Valid Beats Per Recording)

### 4.1 Mathematical Context & Implementation Trace
Decision D14 addresses whether to retain the recording-level requirement of at least 20 valid RR beats ([`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283)), drop it, or increase it to 30 beats.

### 4.2 Empirical Beat Count Recomputation Across All 48 Recordings
Full signal processing of `ecg_lead2` across all 48 recordings ($60,000\text{ samples}$ at $500\text{ Hz} = 120\text{ s}$ per recording) yielded the following distribution:

| Metric | Empirical Value |
| :--- | :---: |
| **Total Evaluated Recordings** | 48 |
| **Minimum Valid Beats in a Recording** | **99 beats** (in `VS10_Resting`) |
| **Maximum Valid Beats in a Recording** | **157 beats** (in `VS14_Apnea`) |
| **Mean Beat Count Per Recording** | **$129.2 \pm 14.8$ beats** |
| **Median Beat Count Per Recording** | **130.5 beats** |
| **Interquartile Range (IQR)** | $[118.0, 140.0]\text{ beats}$ |
| **Recording Coverage Ratio ($>85\%$)** | $100.0\%$ (Min: $98.56\%$, Max: $99.70\%$) |
| **Recording Maximum RR Gap ($<3.0\text{ s}$)** | $100.0\%$ (Max observed: $1.2920\text{ s}$) |

#### Rejection Sensitivity Comparison:
- **Threshold = 20 Beats:** Rejects **0 of 48 recordings** ($0.0\%$ rejection rate; $48/48$ pass).
- **Threshold = 30 Beats:** Rejects **0 of 48 recordings** ($0.0\%$ rejection rate; $48/48$ pass).
- **Threshold = 50 Beats:** Rejects **0 of 48 recordings** ($0.0\%$ rejection rate; $48/48$ pass).
- **Threshold = 80 Beats:** Rejects **0 of 48 recordings** ($0.0\%$ rejection rate; $48/48$ pass).

### 4.3 D14 Recommendation
- **Recommendation:** **RETAIN (Option A: Keep minimum valid beat threshold of 20 beats per 120 s recording).**
- **Scientific Rationale:**
  1. For a 120-second recording with $85\%$ minimum valid coverage ($102\text{ s}$), even at the lowest physiological heart rate allowed ($35\text{ BPM}$), the theoretical minimum number of beats is $\approx 59.5\text{ beats}$.
  2. The empirical minimum across all 48 recordings is 99 beats.
  3. Therefore, a threshold of 20 beats is a non-binding lower invariant that protects against corrupted, heavily missing, or severely truncated files without filtering out any legitimate physiological recordings.

---

## 5. Work Package 4: Decision D15 Implementation & Safeguard Verification

### 5.1 Inspection of `proposed_runner_guard.diff`
The proposed patch in [`outputs/closure/proposed_runner_guard.diff`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/proposed_runner_guard.diff) addressed a governance flaw in [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py), where running validation without `--output-dir` defaulted to `outputs/phase2a`, risking accidental overwrite of the audited Phase 2A baseline.

### 5.2 Code Implementation
The safeguard was implemented directly in [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py) across both `run_full_validation` and `run_sync_validation`:
1. **Explicit Parameter Requirement:** `output_dir` is required; `if output_dir is None: raise ValueError(...)`.
2. **Phase 2A Immutability Protection:** Resolves `output_dir` path. If it resolves to `outputs/phase2a` and `allow_phase2a_overwrite=False`, it raises `PermissionError`.
3. **Empty Scan Defensive Fallback:** Added graceful handling for empty scans when testing isolated mock directories.

### 5.3 Automated Verification
Automated test suite [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) was created with fixture-level integrity checks:
- `test_missing_output_dir_raises_value_error`: PASS.
- `test_protected_phase2a_raises_permission_error`: PASS.
- `test_safe_isolated_output_dir_accepted`: PASS.

### 5.4 Audit Artifact Immutability Confirmation
Before and after running the test suite, the cryptographic SHA-256 digests of the Phase 2A artifacts were computed:
- `outputs/phase2a/step2b_consistency_audit.md`: `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f` (EXACT MATCH).
- `outputs/phase2a/sync_validation_results.csv`: `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10` (EXACT MATCH).

---

## 6. Work Package 5: Scientific Readiness & Ground-Truth Reference Audit

### 6.1 ECG Reference Processing Implementation Discrepancy & Resolution
A rigorous code trace was conducted between `src.sync_validation.ecg_processor` and `src.phase3.ecg_reference`:
- **The Issue:** `VS10_Resting` contains an isolated delimiter NaN at sample index 0. If sample index 0 remains NaN, applying Butterworth IIR filtering (`filtfilt`) causes NaN contamination across the entire 60,000 samples, collapsing peak detection to 0 beats.
- **The Code Discrepancy:**
  - `src.phase3.ecg_reference.clean_ecg_nans` defined `fill_boundary: bool = True` (replicating index 1 to index 0).
  - `src.sync_validation.ecg_processor.clean_ecg_nans` lacked the `fill_boundary` parameter in its signature.
  - `label_spec_v1.json` specified `cleaning_module: "src.sync_validation.ecg_processor"` with `cleaning_options: {"only_isolated": true, "fill_boundary": true}`.
  - Dynamically passing `cleaning_options` to `sync_validation` raised `TypeError: clean_ecg_nans() got an unexpected keyword argument 'fill_boundary'`.
- **The Fix:** [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py) was updated to accept `fill_boundary: bool = True`. Both modules now exhibit identical, verified behavior.

### 6.2 Hardware Synchronization & Nominal $T_0=0\text{ s}$ Reality
Byte-level audit of all 96 `.mat` files confirmed:
- No pulse-per-second (PPS) hardware lines exist.
- No hardware cross-trigger timestamps or shared digitizer clocks exist.
- Matching file names (e.g. `VS01_Resting.mat` and `VS01_Resting_Mindray.mat`) indicate paired recordings from the same trial, not hardware clock synchronization.
- **Mandatory Limitation:** All downstream publications, model cards, and documentation must state: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.

### 6.3 Empirical Verification of Mindray Display-HR Latency
Evaluating `monitor_hr_lag_estimate_s` in [`outputs/phase2a/sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/sync_validation_results.csv) confirmed:
- **Mean Latency:** $+6.21\text{ s}$ lag relative to instantaneous ECG.
- **Median Latency:** $+7.00\text{ s}$.
- **Distribution:** $40 / 48$ recordings ($83.3\%$) exhibit latency between $+4\text{ s}$ and $+10\text{ s}$, with mode at $+7.0\text{ s}$ ($13$ recordings).
- **Conclusion:** Using raw monitor display HR directly as ground truth for 10-second windows would introduce severe systematic label delay. instantaneous ECG R-peak harmonic mean HR is the only valid reference source.

### 6.4 Scientific Gate Status
The scientific gate documented in [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md) remains strictly **`OPEN`** (`STATUS: RECONCILIATION PARTIAL`). Real VITALSENSE data training and label generation remain strictly **`BLOCKED`**.

---

## 7. Work Package 6: Git Provenance Analysis & Metadata Hardening

### 7.1 Diagnostic Findings
In previous run logs, `git_commit` was recorded as `"UNKNOWN"`. Investigation confirmed:
1. `git` is not installed or available on Windows system `PATH`.
2. Neither `kan_radar_HR` nor its parent folder contains a `.git` repository folder.
3. In [`src/kan/trainer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py), `subprocess.run(["git", ...])` raised `FileNotFoundError`, which was caught by an unhandled `except Exception: pass`, resulting in `"UNKNOWN"`.

### 7.2 Implementation Refinement
[`src/kan/trainer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py) was enhanced to inspect `shutil.which("git")` and the presence of `.git`:
- If `git` is missing: records `git_commit: "GIT_EXECUTABLE_NOT_FOUND"`, `git_status_detail: "git executable is not installed or not present on system PATH"`.
- If `.git` is missing: records `git_commit: "NOT_A_GIT_REPOSITORY"`.
- Tested and verified working without error.

---

## 8. Principal Investigator (PI) Decision Package & Sign-Off Forms

The following formal decision records are presented for review, resolution, and signature by the Principal Investigator:

```
========================================================================================
PRINCIPAL INVESTIGATOR FORMAL DECISION & APPROVAL RECORD
Project: Subject-Independent KAN FMCW Radar Heart-Rate Estimation (VITALSENSE Dataset)
========================================================================================

----------------------------------------------------------------------------------------
DECISION D13: Window-Level Maximum RR Gap Rule (3.0 s)
----------------------------------------------------------------------------------------
Context: Whether to retain the rule rejecting windows where maximum RR gap >= 3.0 s.
Empirical Finding: 1,104 candidate windows evaluated; max gap is 1.292 s. Rejects 0 windows (0.0% yield loss).
Recommendation: Option A (Retain 3.0 s threshold).

[ ] OPTION A: RETAIN threshold at 3.0 s (Ensures consistency with recording SQI).
[ ] OPTION B: DROP window-level max-gap rule (Rely strictly on duration coverage >= 80%).
[ ] OPTION C: REVISE threshold to physiological bound (e.g. 4.0 s).

PI Selected Option: ___________________________
PI Signature:       ___________________________
Date:               ___________________________

----------------------------------------------------------------------------------------
DECISION D14: Minimum Valid Beats Per Recording (20 Beats)
----------------------------------------------------------------------------------------
Context: Whether to retain minimum valid beat count threshold of 20 beats per 120 s recording.
Empirical Finding: Empirical beat range is 99 to 157 beats (mean: 129.2). Both 20 and 30 reject 0 recordings.
Recommendation: Option A (Retain 20 beats threshold as safety invariant).

[ ] OPTION A: RETAIN threshold of >= 20 valid beats per recording.
[ ] OPTION B: DROP beat count threshold (Rely strictly on duration coverage > 85%).
[ ] OPTION C: REVISE threshold to alternative count (e.g. 30 beats).

PI Selected Option: ___________________________
PI Signature:       ___________________________
Date:               ___________________________

----------------------------------------------------------------------------------------
DECISION D15: Pipeline Runner Default output_dir Guard
----------------------------------------------------------------------------------------
Context: Whether to enforce explicit output_dir and protect outputs/phase2a/ from overwrites.
Implementation Finding: Implemented in src/sync_validation/runner.py; 3/3 tests passed.
Recommendation: Option A (Enforce programmatic safeguard).

[ ] OPTION A: APPROVE code safeguard requiring explicit output_dir and blocking outputs/phase2a overwrite.
[ ] OPTION B: REJECT code safeguard and revert to procedural documentation only.

PI Selected Option: ___________________________
PI Signature:       ___________________________
Date:               ___________________________

----------------------------------------------------------------------------------------
SPECIFICATION APPROVAL: outputs/closure/spec/label_spec_v1.json
----------------------------------------------------------------------------------------
Context: Formal sign-off on canonical label specification (spec_sha256: a0f7a85e...).
Mandatory Prerequisite: Must be signed before generating real-data supervised training targets.

[ ] APPROVED: I hereby approve label_spec_v1.json as the frozen reference specification.
[ ] REJECTED: Revisions required before approval.

Approved By (PI Name): ___________________________
PI Signature:          ___________________________
Date:                  ___________________________
========================================================================================
```

---

## 9. Comprehensive Acceptance Criteria & Status Verdict

| Work Package | Task / Requirement | Status | Evidence / Verification |
|---|---|:---:|---|
| **WP 1** | Repository & Cryptographic Audit | **COMPLETE** | All 7 audit files verified on disk with SHA-256 hashes. |
| **WP 2** | D13 Verification | **COMPLETE** | 1,104 windows recomputed from raw data; 0 rejections; yield loss 0.0%. Recommendation: RETAIN. |
| **WP 3** | D14 Verification | **COMPLETE** | 48 recordings recomputed; beat range 99–157; 0 rejections for 20 or 30. Recommendation: RETAIN. |
| **WP 4** | D15 Output Guard | **COMPLETE** | `src/sync_validation/runner.py` protected; `tests/test_d15_runner_guard.py` passed ($3/3$); Phase 2A untouched. |
| **WP 5** | Scientific Readiness Audit | **COMPLETE** | `fill_boundary` harmonized; Mindray +6.21s latency verified; nominal $T_0=0\text{ s}$ limitation documented. |
| **WP 6** | Git Provenance | **COMPLETE** | Root cause diagnosed; `src/kan/trainer.py` updated with informative error reporting. |
| **WP 7** | PI Decision Package | **COMPLETE** | New report created under `outputs/closure/`; formal sign-off forms prepared. |

### Overall Project Status Verdict:
**`COMPLETE WITH LIMITATIONS`**
*(All technical verifications, safeguards, and decision packages are complete. The project is strictly **BLOCKED** from real-data label generation and training pending formal PI signature on Decisions D13–D15 and `label_spec_v1.json`.)*

---

## 10. Next Authorized Actions

1. **Principal Investigator Action:** Review this decision package and execute sign-offs for D13, D14, D15, and `label_spec_v1.json`.
2. **Phase 2A Gate Closure:** Following PI sign-off, update `outputs/phase2a/step2b_consistency_audit.md` to `STATUS: CLOSED`.
3. **Phase 2C Dataset Generation:** Run `src/phase3/supervised_dataset_generator.py` to generate the canonical supervised dataset (`run_002`).
4. **Phase 5 Real Training:** Execute `KANTrainer` in real-data mode with subject-independent LOSO cross-validation.
