# PHASE 2A RECONCILIATION ADDENDUM & STATUS REGISTER
**Document ID:** `outputs/closure/phase2a_reconciliation_addendum.md`  
**Execution Stage:** Phase 6B.8 — Implementation and Closure Readiness  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Governance Reviewer:** Senior Biomedical Signal-Processing Researcher & Research Governance Auditor  
**Reference Baseline:** [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md)  
**Parent Issue Register:** [`outputs/phase2a/step2b_issue_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_issue_register.csv)  
**Baseline Immutability Notice:** This document is a non-destructive closure addendum. The baseline Phase 2A audit (`step2b_consistency_audit.md`, SHA-256: `6c4391bf...`) remains strictly bit-for-bit immutable.  

---

## 1. Executive Summary & Purpose

The purpose of this Addendum is to provide a complete, item-by-item accounting of all 28 issues identified in the Phase 2A Step 2B Consistency Audit (`step2b_issue_register.csv`), detailing what has been resolved by subsequent implementation stages, what remains open, what is unresolvable due to physical acquisition realities, and the exact governance decisions required for final closure.

### Overall Status of the 28 Audit Issues:
- **`VERIFIED / RESOLVED` in Code & Tests:** 12 issues (ISS-09, ISS-13, ISS-19, ISS-20, ISS-21, ISS-23, ISS-24, ISS-25, ISS-26, plus preprocessing requirements 18.2, 18.4, 18.5).
- **`DOCUMENTED / ACCEPTED LIMITATION` (Physical Acquisition / Data Constraints):** 9 issues (ISS-01, ISS-02, ISS-03, ISS-04, ISS-05, ISS-06, ISS-11, ISS-14, ISS-28).
- **`OPEN` (Requiring Formal PI Decision / Execution):** 7 issues (ISS-07, ISS-08, ISS-10, ISS-12, ISS-15, ISS-17, ISS-22).
- **Gate Status:** Remains strictly **`OPEN`** pending formal PI execution of [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md).

---

## 2. Systematic Item-by-Item Reconciliation Status

The following register provides the complete audit trace for every issue originally documented in `step2b_issue_register.csv`:

### Item ISS-01: Systematic Latency of Commercial Monitor Display HR Array
- **Description:** Commercial Mindray monitor numeric `HR` array exhibits a systematic $+6.21\text{ s}$ mean latency (median $+7.0\text{ s}$) relative to continuous ECG-derived heart rate.
- **Existing Evidence:** Confirmed across all 48 candidate pairs in [`outputs/phase2a/sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/sync_validation_results.csv).
- **Missing Evidence:** None.
- **Resolution / Policy:** Disqualified the raw monitor `HR` array from being used as supervised training targets. Standardized ground truth exclusively on continuous ECG Lead II R-peak harmonic mean HR under `label_spec_v1.json`.
- **Status:** **`VERIFIED / RESOLVED BY POLICY`**
- **Verification Date:** 2026-10-18

### Item ISS-02: Absence of Hardware Digitizer Synchronization Clocks
- **Description:** MAT headers lack hardware clock, PPS pulse, or common digitizer timestamps across recording files.
- **Existing Evidence:** Byte-level audit of all 96 MAT files in `../data/VITALSENSE_120_DATASET`.
- **Missing Evidence:** Physical acquisition clock synchronization is physically impossible to obtain post-hoc.
- **Resolution / Policy:** Formally documented mandatory scientific limitation: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. All timing claims are evaluated on a nominal $T_0=0.0\text{ s}$ computational baseline.
- **Status:** **`DOCUMENTED / ACCEPTED SCIENTIFIC LIMITATION`**
- **Verification Date:** 2026-10-18

### Item ISS-03: Erroneous Surrogate Correlation Claim in Narrative Report
- **Description:** Step 2 report claimed surrogate correlation "never exceeded 0.42", whereas CSV proves values reach up to $0.8123$ (mean: $0.5077$).
- **Existing Evidence:** CSV data in `sync_validation_results.csv` and audit in `step2b_consistency_audit.md:Section 5.1`.
- **Missing Evidence:** None.
- **Resolution / Policy:** Erratum documented in `step2b_consistency_audit.md`. Narrative corrected; surrogate correlation range ($0.16$ to $0.81$) acknowledged.
- **Status:** **`VERIFIED / ERRATUM DOCUMENTED`**
- **Verification Date:** 2026-10-18

### Item ISS-04: Mathematically Impossible Empirical p-value Claim ($p < 0.001$ with $N=5$)
- **Description:** Report claimed empirical significance at $p < 0.001$ using only $N=5$ surrogate draws, where minimum achievable empirical p-value is $1/(N+1) \approx 0.167$.
- **Existing Evidence:** Mathematical derivation in `step2b_consistency_audit.md:Section 5.2`.
- **Missing Evidence:** None.
- **Resolution / Policy:** Claim formally retracted in `step2b_consistency_audit.md`. Status held as `CONSISTENT_NOT_PROVEN`.
- **Status:** **`VERIFIED / RETRACTION DOCUMENTED`**
- **Verification Date:** 2026-10-18

### Item ISS-05: Inverted Polarity Subject Misidentification
- **Description:** Narrative report cited `VS02` and `VS19` as Resting negative polarity pairs; true negative polarity pairs in CSV are `VS09` and `VS20`.
- **Existing Evidence:** CSV column `respiratory_polarity_inverted` in `sync_validation_results.csv`.
- **Missing Evidence:** None.
- **Resolution / Policy:** Narrative transcription error corrected in `step2b_consistency_audit.md`.
- **Status:** **`VERIFIED / CORRECTION DOCUMENTED`**
- **Verification Date:** 2026-10-18

### Item ISS-06: Correlation Threshold Count Discrepancy ($r > 0.85$)
- **Description:** Narrative report claimed 14 Resting pairs had respiratory correlation $> 0.85$; actual CSV count is 6 pairs (16 exceed $0.70$).
- **Existing Evidence:** CSV column `respiratory_corr` in `sync_validation_results.csv`.
- **Missing Evidence:** None.
- **Resolution / Policy:** Narrative corrected in `step2b_consistency_audit.md`.
- **Status:** **`VERIFIED / CORRECTION DOCUMENTED`**
- **Verification Date:** 2026-10-18

### Item ISS-07: Lumping Lags $< 4\text{ s}$ into `NEAR_ZERO_LATENCY`
- **Description:** Rule `best_lag_s >= 4` lumped negative lags (e.g. $-3\text{ s}$ in `VS05_Apnea`) into `NEAR_ZERO_LATENCY` with contradictory reason string citing "flatness" when flatness flag was false.
- **Existing Evidence:** [`src/sync_validation/runner.py:lines 98-110`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L98).
- **Missing Evidence:** Formal PI decision on whether to refactor latency classification categories in legacy sync validation results.
- **Required Resolution:** PI review under Phase 2A closure. Note that Phase 3 / Phase 5 pipelines bypass this heuristic entirely by computing continuous R-peak instantaneous HR.
- **Status:** **`OPEN (NON-BLOCKING FOR PHASE 2C)`**
- **Responsible Owner:** Principal Investigator

### Item ISS-08: Superficial ECG Quality Check ($5$ Valid Beats in $120\text{ s}$)
- **Description:** Legacy check in `detect_r_peaks` awarded `ecg_quality_status = PASS` if $\ge 5$ beats existed in 120 seconds.
- **Existing Evidence:** [`src/sync_validation/ecg_processor.py:detect_r_peaks`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L125).
- **Missing Evidence:** Formal PI execution of Decision D14 ($\ge 20$ beats threshold).
- **Resolution in Code:** Implemented multi-parameter SQI in `src/phase3/ecg_reference.py` evaluating coverage ($> 85\%$), max gap ($< 3.0\text{ s}$), and beat count ($\ge 20$). All 48 recordings pass multi-parameter SQI with minimum 99 beats.
- **Status:** **`VERIFIED IN CODE / PENDING FORMAL PI SIGN-OFF (D14)`**
- **Responsible Owner:** Principal Investigator

### Item ISS-09: Cardiac Radar FFT Bin Discretization Noise ($6.0\text{ BPM}$ Native Bins)
- **Description:** A 10-second rectangular window yields $0.1\text{ Hz} = 6.0\text{ BPM}$ frequency bins with ladder-step discretization.
- **Existing Evidence:** Implemented 4x zero-padding and 3-point parabolic peak interpolation in [`src/sync_validation/cardiac_radar_validator.py:33-110`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L33-L110).
- **Missing Evidence:** None.
- **Resolution in Code:** Verified by unit tests in [`tests/test_stage2_closure.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_stage2_closure.py).
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-19

### Item ISS-10: In-Sample Best-Shift Optimization Selection Optimism
- **Description:** Scanning trial shifts $\tau \in [-5, +5]\text{ s}$ on all 23 windows overfits in-sample; held-out test windows show higher errors.
- **Existing Evidence:** Diagnostic split tests in `step2b_consistency_audit.md:Section 14`.
- **Missing Evidence:** None.
- **Resolution in Code:** Mandated zero-shift baseline ($\tau = 0.0\text{ s}$) as canonical benchmark reference under `label_spec_v1.json`.
- **Status:** **`VERIFIED / RESOLVED BY SPECIFICATION`**
- **Verification Date:** 2026-10-20

### Item ISS-11: Apnea Respiratory Cross-Correlation Confounded by Baseline Drift
- **Description:** Apnea recordings lack active diaphragmatic respiration; cross-correlation correlates low-frequency baseline drift.
- **Existing Evidence:** `sync_validation_results.csv` and `step2b_consistency_audit.md:Section 8`.
- **Missing Evidence:** Active respiratory effort during apnea is physiologically absent.
- **Resolution / Policy:** Formally classified Apnea respiratory alignment as `INCONCLUSIVE`. Model training relies strictly on cardiac-band FMCW phase modulation.
- **Status:** **`DOCUMENTED / ACCEPTED SCIENTIFIC LIMITATION`**
- **Verification Date:** 2026-10-18

### Item ISS-12: `VS24_Resting_Mindray.mat` Formatting Divergence (30,600 Respiration Samples)
- **Description:** `VS24_Resting` contains 30,600 respiration samples instead of 30,720 (120 samples / 480 ms short), double floats instead of integer ADC codes, and 0 NaNs.
- **Existing Evidence:** Physical file inspection in `data/VITALSENSE_120_DATASET/VS24/VS24_Resting_Mindray.mat`.
- **Missing Evidence:** Original acquisition operator logs explaining why VS24 was formatted differently.
- **Resolution in Code:** Preprocessing pipelines query dynamic array lengths and truncate in-memory safely; no hardcoded 30,720 length is assumed.
- **Status:** **`OPEN (DOCUMENTED REPRODUCIBLE ANOMALY)`**
- **Responsible Owner:** Principal Investigator

### Item ISS-13: Forensic Trace of NaN Counts Between Phase 1 and Step 2B
- **Description:** Apparent contradiction between Phase 1 (0 NaNs) and Step 2B (5,629 NaNs).
- **Existing Evidence:** Trace proved Phase 1 checked `HR` array (which has 0 NaNs) while Step 2B checked continuous `ecg_lead2` (which has periodic 1-sample packet delimiters).
- **Missing Evidence:** None.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-18

### Item ISS-14: Exclusion of `TechValidation.m` from Scope
- **Description:** Reference to original authors' MATLAB script `TechValidation.m` could not be verified because file is absent from disk.
- **Existing Evidence:** Recursive filesystem search confirmed file is absent.
- **Resolution / Policy:** Designated `NOT_AVAILABLE — EXCLUDED FROM SCOPE`. Current Python pipeline operates independently with self-contained mathematical implementations.
- **Status:** **`DOCUMENTED / ACCEPTED SCOPE LIMITATION`**
- **Verification Date:** 2026-10-18

### Item ISS-15: Test Assertion Threshold Loosening ($r < 0.75$)
- **Description:** In `tests/test_sync_validation.py`, surrogate test assertion was relaxed from $r < 0.30$ to $r < 0.75$.
- **Existing Evidence:** `tests/test_sync_validation.py:test_compute_surrogate_respiratory_control`.
- **Missing Evidence:** Pre-specified clinical threshold justification.
- **Resolution / Action:** Preserved existing test for regression baseline; surrogate control is acknowledged as exploratory only.
- **Status:** **`OPEN (NON-BLOCKING FOR PHASE 2C)`**
- **Responsible Owner:** Senior Validation Specialist

### Item ISS-16: 10-Second Window Alignment Adequacy Headline
- **Description:** Preliminary headline claiming 10s window alignment was adequate was not supported by surrogate controls.
- **Existing Evidence:** Audited in `step2b_consistency_audit.md`.
- **Resolution / Policy:** Headline replaced with evidence-matched finding: *"Empirical resting cardiac-band agreement observed for 10s windows at zero shift (MAE = 2.97 BPM); supervised label generation not yet approved; hardware clock unverified."*
- **Status:** **`VERIFIED / RESOLVED IN DOCUMENTATION`**
- **Verification Date:** 2026-10-18

### Item ISS-17: Small Sample Size of Surrogate Control ($N=5$)
- **Description:** Surrogate control evaluated on $N=5$ draws lacks statistical power to reject null hypothesis.
- **Existing Evidence:** Analysis in `step2b_consistency_audit.md:Section 5.2`.
- **Missing Evidence:** High-throughput $N \ge 1000$ surrogate run.
- **Resolution / Policy:** Status maintained as `CONSISTENT_NOT_PROVEN`. Not utilized as proof of hardware synchronization.
- **Status:** **`OPEN (DOCUMENTED LIMITATION)`**
- **Responsible Owner:** Senior Statistical Auditor

### Item ISS-18: Provenance of 5.0 BPM MAE and 50 ms Lag Thresholds
- **Description:** Thresholds were empirical heuristic choices not pre-registered in an external clinical protocol.
- **Existing Evidence:** Trace in `step2b_consistency_audit.md:Section 19.3`.
- **Resolution / Policy:** Formally documented as heuristic engineering thresholds under `label_spec_v1.json:threshold_provenance: "UNVERIFIED_PROVENANCE"`.
- **Status:** **`DOCUMENTED / ACCEPTED LIMITATION`**
- **Verification Date:** 2026-10-18

### Item ISS-19: Clarification of VS24 Respiration Tail Truncation
- **Description:** Prior claims attributing VS24 anomalies to software interpolation distortion were unverified.
- **Existing Evidence:** Narrative erratum in `step2b_consistency_audit.md:Section 23.1`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-18

### Item ISS-20: Classification of Discrepancies Exceeding 0.0100 BPM Tolerance
- **Description:** Differences between reported and recomputed values exceeding numerical precision tolerances.
- **Existing Evidence:** Documented in `step2b_consistency_audit.md:Section 6.2`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-18

### Item ISS-21: Guarded Single-Sample Delimiter NaN Interpolation
- **Description:** Single-sample delimiter NaNs require interpolation; multi-sample gaps must not be interpolated.
- **Existing Evidence:** Implemented in [`src/sync_validation/ecg_processor.py:clean_ecg_isolated_nans`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L46). Multi-sample gaps are flagged and un-interpolated. Tested in `tests/test_stage2_closure.py`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-19

### Item ISS-22: Sensitivity Analysis of VS24 Respiration Truncation
- **Description:** Truncation of VS24 respiration assumes missing samples are at the tail.
- **Existing Evidence:** Truncation is restricted to respiration validation; cardiac ECG processing has 60,000 intact samples.
- **Missing Evidence:** Formal sensitivity analysis on respiration cross-correlation without VS24.
- **Status:** **`OPEN (NON-BLOCKING FOR CARDIAC TRAINING)`**
- **Responsible Owner:** Senior Validation Specialist

### Item ISS-23: Deterministic Seeding for Cardiac Surrogate Control
- **Description:** Unseeded permutation in `cardiac_surrogate_mae` created non-deterministic run results.
- **Existing Evidence:** Seed policy codified in `label_spec_v1.json:seed_policy: {"cardiac_surrogate_seed": 42}` and tested in `tests/test_phase5_training.py`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-20

### Item ISS-24: Boundary NaN Handling Harmonization (`VS10_Resting`)
- **Description:** `VS10_Resting` contains sample 0 as NaN. Unhandled boundary NaN causes `filtfilt` to collapse peak detection across the entire file.
- **Existing Evidence:** Harmonized `clean_ecg_nans` in `src.sync_validation.ecg_processor` to accept `fill_boundary: bool = True`. Tested in `tests/test_coverage_audit.py` and `tests/test_stage2f_boundary.py`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-21

### Item ISS-25: Continuous Time Window Formula (23 Windows / 1,104 Total)
- **Description:** Integer hopping ($+1,667\text{ samples}$) dropped the 23rd window ($4.98\text{ s}$ tail truncation).
- **Existing Evidence:** Continuous temporal grid $t_{\text{start}} = \text{round}(k \times 5.0, 3)$ recovers all 23 windows (1,104 candidate windows across 48 recordings). Codified in `label_spec_v1.json` and tested in `tests/test_supervised_dataset_generation.py`.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-20

### Item ISS-26: Canonical ECG Detector & Ground-Truth Aggregation Harmonization
- **Description:** Discrepancies between Pan-Tompkins positive refinement vs absolute refinement ($\text{argmax}(|\text{filt}|)$) created $44\text{ ms}$ error on inverted lead `VS19`.
- **Existing Evidence:** Harmonized on polarity-invariant absolute refinement under `label_spec_v1.json`. Tested across all 48 files.
- **Status:** **`VERIFIED / RESOLVED`**
- **Verification Date:** 2026-10-20

### Item ISS-27: Status of Unapproved Legacy `run_001` Supervised Manifests
- **Description:** Legacy manifests generated 2026-10-15 under `outputs/supervised_dataset/run_001/` were unapproved and superseded.
- **Existing Evidence:** `run_001` manifests are marked `UNAPPROVED / SUPERSEDED`. Protected from overwrite.
- **Resolution / Policy:** Retained as read-only diagnostic history. Canonical supervised dataset will be generated into isolated `run_002/`.
- **Status:** **`VERIFIED / POLICY ENFORCED`**
- **Verification Date:** 2026-10-20

### Item ISS-28: Respiratory Correlation Plateau Width (Median 95 ms)
- **Description:** Peak cross-correlation sits on an extended flat plateau (range $34.5\text{ ms}$ to $1,594\text{ ms}$), demonstrating that sub-sample alignment is a mathematical artifact, not hardware synchronization.
- **Existing Evidence:** Plateau analysis in `step2b_consistency_audit.md:Section 22.3`.
- **Resolution / Policy:** Documented and linked to mandatory `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` limitation.
- **Status:** **`DOCUMENTED / ACCEPTED SCIENTIFIC LIMITATION`**
- **Verification Date:** 2026-10-18

---

## 3. Outstanding Gate Closure Requirements

Before the Phase 2A/2C Scientific Gate can transition to **`CLOSED`**, the following explicit actions must be completed:
1. **Principal Investigator Execution of [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md):**
   - Execution of Decision D13 selection and signature.
   - Execution of Decision D14 selection and signature.
   - Execution of Decision D15 selection and signature.
   - Execution of `label_spec_v1.json` approval signature.
   - Execution of Hardware Timing Limitation acknowledgement.
   - Execution of Gate Closure authorization.
2. **Phase 2A Formal Gate Closure Action:**
   - Append formal closure notice to `step2b_consistency_audit.md`, moving status from `RECONCILIATION PARTIAL` to `CLOSED`.
   - Run `src/closure/phase2c_preflight.py` to confirm zero blockers before executing `run_002`.
