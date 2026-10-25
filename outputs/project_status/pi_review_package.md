# PRINCIPAL INVESTIGATOR (PI) GOVERNANCE REVIEW PACKAGE
## Phase 2A Scientific Gate Closure & Phase 2C Real-Data Authorization

**Project:** *A Subject-Independent Kolmogorov-Arnold Network (KAN)-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Repository Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Document Output Path:** [`outputs/project_status/pi_review_package.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/project_status/pi_review_package.md)  
**Review Execution Date:** October 2026  
**Auditor / Roles:** Senior ML Research Engineer, Biomedical Signal-Processing Specialist, Scientific Reproducibility Auditor  
**Governance Status:** **`PENDING FORMAL PI REVIEW & EXECUTION`**  
**Gate Status:** Strictly **`OPEN`** | **Preflight Verdict:** **`NO-GO`** (10 PASS, 6 FAIL)  

---

## 1. Governance Boundary & Preamble

> [!IMPORTANT]
> **Zero Automated Sign-Off Policy:**  
> In compliance with strict biomedical research integrity standards, the engineering team and automated AI agents **cannot** sign on behalf of the Principal Investigator, select governance options, populate `approved_by` fields, or fabricate digital signatures and authorization dates.
> 
> All real-data label generation (`outputs/supervised_dataset/run_002`) and real-data model training (`outputs/phase5/run_real_001`) remain **strictly blocked and fail-closed** until the Principal Investigator personally reviews this package and executes the formal intake protocol.

---

## 2. Master Review Matrix: The Six Governance Blockers

The following table summarizes the six pending governance items, the engineering recommendations, supporting empirical evidence, associated uncertainties, risks of alternatives, and the exact sign-off fields required.

| Item ID | Governance Subject | Engineering Recommendation | Empirical Evidence Base | Scientific Uncertainties | Risks of Alternative Options | Exact Field to Complete |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **D13** | **Window-Level Max RR Gap Rule** | **Option A (Retain $3.0\text{ s}$ threshold)** | Across all 48 recordings and 1,104 candidate windows, cohort max observed RR interval is **$1.2920\text{ s}$** (`VS02_Apnea`). Rejection rate is **$0.00\%$** ($100\%$ window yield retained). | Severe bradycardia or pause episodes ($< 20\text{ BPM}$) in pathological cohorts could exceed $3.0\text{ s}$, but VITALSENSE contains healthy subjects. | **Option B (Drop rule):** Risks admitting windows with severe localized pauses, ectopic dropout, or lead dislodgement artifacts.<br>**Option C (Revise to $4.0\text{ s}$):** Overly permissive ($40\%$ of window) without yield gain. | [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L38-L49) **Section 2.2** (lines 38–49): Check Option, Name, Title, Institution, Signature, Date. |
| **D14** | **Minimum Valid Beats per Recording** | **Option A (Retain $\ge 20\text{ beats}$ threshold)** | Cohort beat counts range from **99 beats** (`VS10_Resting`) to **157 beats** (`VS14_Apnea`) with mean $129.2 \pm 14.8$ beats. Zero of 48 recordings rejected ($0.0\%$). | Does not evaluate rhythm regularity, but duration coverage ($>85\%$) and physiological rate limits ($35\text{--}185\text{ BPM}$) independently ensure signal quality. | **Option B (Drop rule):** Removes defense-in-depth lower bound; a corrupted or truncated file ($< 30\text{ s}$) with an erroneous beat could pass duration checks.<br>**Option C (Revise to 30/50 beats):** Zero yield impact (min 99 beats), but modifies test baselines. | [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L67-L78) **Section 3.2** (lines 67–78): Check Option, Name, Title, Institution, Signature, Date. |
| **D15** | **Pipeline Runner Output Guard** | **Option A (Approve programmatic safeguard)** | Programmatic safeguard in [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py) raises `ValueError` if `output_dir` is missing and `PermissionError` if `outputs/phase2a` overwrite attempted without explicit flag. Verified by 3 tests. | Requires all CLI scripts and automated runners to pass explicit output paths; zero runtime uncertainty. | **Option B (Procedural only):** High risk of accidental silent baseline corruption or race condition overwrites during parallel test executions or automated CLI runs. | [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L94-L104) **Section 4.2** (lines 94–104): Check Option, Name, Title, Institution, Signature, Date. |
| **SPEC-v1** | **Label Specification v1.0.0 Approval** | **APPROVE Specification v1.0.0** | Frozen canonical SHA-256 digest: `ae5c6780...`. Uses Lead II harmonic mean $\text{HR} = 60.0 / \text{mean}(w\_rrs)$, absolute Pan-Tompkins refinement, delimiter NaN interpolation. Excludes commercial monitor `HR` ($+6.21\text{ s}$ lag). | Invariance design: Populating `approved_by` does not alter canonical hash because canonical hashing excludes `approved_by` and `spec_sha256`. | **Reject / Revise:** Invalidates frozen specification hash, requires rewriting generator regression tests, and resets Phase 2A/2C audit timeline. | 1. [`label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L4) **Line 4:** `"approved_by": "<PI Name>"`<br>2. [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L123-L133) **Section 5.2** (lines 123–133): Check APPROVED, Name, Title, Institution, Signature, Date. |
| **HW-SYNC** | **Hardware Timing Acknowledgement** | **CONFIRM Limitation Acknowledged & Mandated** | Comprehensive byte-level audit of all 96 MAT files in `data/VITALSENSE_120_DATASET` confirmed zero PPS hardware lines, TTL triggers, or shared digitizer clocks. $T_0 = 0.0\text{ s}$ is an operational assumption. | Physiological pulse transit time (PTT, $\sim 100\text{--}250\text{ ms}$) and startup delays cannot be decoupled without hardware triggers, but impact on 10-s window average HR is minor. | **Decline / Omit:** Failing to cite `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` invites scientific retraction or reviewer rejection over unsubstantiated hardware synchronization claims. | [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L146-L152) **Section 6.2** (lines 146–152): PI Name, Signature, Date. |
| **GATE-AUTH** | **Phase 2A Gate Closure Authorization** | **AUTHORIZE Gate Closure & Phase 2C Entry** | 28 Phase 2A consistency issues tracked: 12 resolved in code/tests, 9 documented physical limitations, 7 pending this sign-off. Test suite passes 220 automated tests. Supervised generator ready. | Real-data radar SNR in certain apnea recordings may have higher noise than synthetic benchmarks, to be quantified under 24-subject LOSO protocol in Phase 5. | **Premature Authorization:** Violates governance if signed before Items 1–5.<br>**Decline Authorization:** Leaves gate permanently OPEN and blocks supervised real-data training. | 1. [`pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L174-L181) **Section 7.3** (lines 174–181): Check AUTHORIZED, Name, Signature, Date.<br>2. Create signed [`investigator_decision.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/investigator_decision.md).<br>3. [`step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md#L14) **Line 14:** Set status to CLOSED. |

---

## 3. Detailed Scientific Review & Rationale per Decision

### 3.1 Decision D13 — Window-Level Maximum RR Gap Rule
- **Target File:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) Section 2.2
- **Engineering Recommendation:** **Option A: RETAIN threshold at $3.0\text{ s}$.**
- **Evidence:** Diagnostic audit across all 1,104 candidate windows in the VITALSENSE cohort confirms that the maximum observed RR interval in any window is $1.2920\text{ s}$ (`VS02_Apnea`). 99% of all window-maximum RR intervals fall below $1.214\text{ s}$. The $3.0\text{ s}$ rule produces **zero yield loss** ($1,104 / 1,104$ windows retained).
- **Uncertainty:** Whether pathological cardiac arrest or extreme bradycardia ($< 20\text{ BPM}$) could be rejected. The VITALSENSE study design enrolled healthy adult volunteers, rendering this threshold completely non-restrictive for valid sinus beats while preventing unflagged sensor detachment artifacts.
- **Risk:** Dropping the rule (Option B) exposes the training dataset to localized dropout bursts where sparse valid beats sum to $> 8.0\text{ s}$ but miss severe transient disturbances.

### 3.2 Decision D14 — Minimum Valid Beats Per Recording
- **Target File:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) Section 3.2
- **Engineering Recommendation:** **Option A: RETAIN threshold at $\ge 20\text{ beats}$ per 120-s recording.**
- **Evidence:** Analysis of all 48 ECG recordings reveals that the minimum beat count in any 120-second recording is **99 beats** (`VS10_Resting`), while the maximum is **157 beats** (`VS14_Apnea`). The mean cohort beat count is $129.2 \pm 14.8$ beats. A threshold of 20 beats rejects **0 of 48 recordings** ($0.0\%$ rejection).
- **Uncertainty:** At the minimum physiological heart rate limit ($35\text{ BPM}$), a 120-second recording with $85\%$ coverage ($102\text{ s}$) produces a theoretical floor of $\approx 59.5\text{ beats}$. The 20-beat threshold is therefore a relaxed lower boundary.
- **Risk:** Option B (dropping the rule) relies entirely on temporal coverage percentages; an anomalous file with a corrupt timestamp header could satisfy duration math while containing near-zero valid beats.

### 3.3 Decision D15 — Pipeline Runner Output Directory Guard
- **Target File:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) Section 4.2
- **Engineering Recommendation:** **Option A: APPROVE programmatic code safeguard in `src/sync_validation/runner.py`.**
- **Evidence:** Implementation in [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py) programmatically intercepts missing `output_dir` arguments (raising `ValueError`) and prevents unauthorized writes into `outputs/phase2a` (raising `PermissionError`). Verified by 3 dedicated automated tests in [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py). Baseline cryptographic hashes remain bit-for-bit unchanged.
- **Uncertainty:** None. All automated test suites and entry points have been adapted to supply explicit output paths.
- **Risk:** Option B (procedural documentation only) relies on human operator discipline, leaving historical baselines vulnerable to silent overwriting during automated testing or retraining.

### 3.4 Decision SPEC-v1 — Label Specification v1.0.0 Approval
- **Target File:** [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L4) Line 4 and [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L123-L133) Section 5.2
- **Engineering Recommendation:** **APPROVE `label_spec_v1.json` as the frozen reference ground-truth specification.**
- **Evidence:** Specification defines:
  1. Windowing: 10.0-s duration, 5.0-s hop, continuous temporal formula yielding exactly 23 windows per recording (1,104 candidate windows).
  2. Ground Truth: Continuous ECG Lead II (`ecg_lead2`). Commercial monitor `HR` array strictly excluded due to $+6.21\text{ s}$ systematic latency.
  3. Preprocessing: Delimiter NaN interpolation (`clean_ecg_nans`) with `only_isolated: true, fill_boundary: true`.
  4. Detection: Pan-Tompkins with absolute peak refinement $\text{argmax}(|\text{filtered}|)$, resolving inverted lead morphology (`VS19`).
  5. Label Formula: Harmonic mean $\text{HR} = 60.0 / \text{mean}(w\_rrs)$.
  6. SQI: Outlier bounds $35\text{--}185\text{ BPM}$, covered duration $> 8.0\text{ s}$, max RR gap $< 3.0\text{ s}$.
- **Uncertainty:** Canonical hash invariance: the validator's canonical hashing function intentionally strips `"approved_by"` and `"spec_sha256"`. Populating the PI's name in `label_spec_v1.json:4` preserves the canonical digest (`ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`).
- **Risk:** Rejecting the specification requires recalibrating all window boundaries and invalidates historical baseline comparisons.

### 3.5 Decision HW-SYNC — Mandatory Hardware Timing Limitation Acknowledgement
- **Target File:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) Section 6.2
- **Engineering Recommendation:** **CONFIRM and mandate `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.**
- **Evidence:** Physical byte-level inspection of all 96 MAT files in the VITALSENSE dataset confirmed the absence of external TTL triggers, PPS lines, or synchronized master clocks.
- **Uncertainty:** Physiological pulse transit time (PTT) introduces a small, variable physiological delay ($\sim 100\text{--}250\text{ ms}$) between ECG ventricular depolarization (R-peak) and radar chest wall displacement. While this delay prevents true microsecond cross-modal phase alignment, its impact on 10-second average heart rate estimation is negligible.
- **Risk:** Failing to explicitly acknowledge this physical limitation creates false scientific claims regarding hardware synchronization, creating severe peer-review and retraction vulnerability.

### 3.6 Decision GATE-AUTH — Phase 2A Gate Closure Authorization
- **Target File:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) Section 7.3
- **Engineering Recommendation:** **AUTHORIZE Phase 2A gate closure upon executing Decisions D13–D15 and signing the label spec and hardware acknowledgement.**
- **Evidence:** All 28 Phase 2A consistency audit items are completely accounted for (12 resolved in software/tests, 9 documented limitations, 7 addressed by this decision package). The full test suite passes 220 tests. The supervised generator is completely guarded and ready.
- **Uncertainty:** Real-data radar signal quality under apnea and motion conditions will be rigorously quantified during Phase 5 LOSO evaluation.
- **Risk:** Authorizing without PI review violates research governance; leaving the gate open blocks execution of Phase 2C dataset generation and Phase 5 real-data training.

---

## 4. Verification of Pipelines & Isolation Architecture

### 4.1 Real-Data Training CLI & Configuration Verification
The real-data training pipeline was inspected and verified without launching execution:
- **CLI Entry Point:** [`src/kan/train_cli.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/train_cli.py)
- **Configuration File:** [`configs/kan_loso_default.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/configs/kan_loso_default.json)
- **Gate Check Implementation:** In [`src/kan/trainer.py:137-196`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py#L137-L196), `verify_gate_approval_for_real_data()` enforces a 5-artifact fail-closed check:
  1. `step2b_consistency_audit.md` contains `FINALIZATION GATE CLOSED` and `SUPERVISED TRAINING PERMITTED`.
  2. `gate_checklist.csv` contains zero unresolved blocker statuses.
  3. `label_spec_v1.json` contains a non-empty `approved_by` field and status `APPROVED`.
  4. `spec_status_note.md` does not contain `DRAFT_UNAPPROVED`.
  5. `investigator_decision.md` exists on disk.
- **Fail-Closed Verification:** When `--real` is supplied while the gate is open, `execute_training()` raises `GateBlockerError`, halting execution before reading any real radar data.

### 4.2 Synthetic-Only Training Path Isolation
- In [`src/kan/trainer.py:198-250`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py#L198-L250), `generate_synthetic_dataset()` generates synthetic physiological waveforms in-memory using sinusoidal chest displacement equations and deterministic noise.
- The synthetic path does **NOT** access, open, or read any MAT files from `data/VITALSENSE_120_DATASET` or any ground-truth labels.
- All synthetic windows and manifests are explicitly stamped with `is_synthetic: True` and `benchmark_label: "SYNTHETIC_BENCHMARK"`.

---

## 5. Exact Files Inspected During Audit

1. [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) (Intake protocol structure, lines 1–181)
2. [`outputs/closure/pi_decision_recommendations.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md) (Technical trade-off analysis, lines 1–332)
3. [`outputs/closure/pi_review_action_checklist.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_review_action_checklist.md) (Step-by-step human action checklist, lines 1–219)
4. [`outputs/closure/final_go_no_go_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/final_go_no_go_report.md) (Master 5-dimension determination matrix, lines 1–109)
5. [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) (Canonical ground-truth specification, lines 1–85)
6. [`src/kan/train_cli.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/train_cli.py) (CLI entry point, lines 1–155)
7. [`src/kan/trainer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/trainer.py) (Trainer implementation, gate enforcement lines 137–196, synthetic generator lines 198–250)
8. [`configs/kan_loso_default.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/configs/kan_loso_default.json) (Training configuration parameters)
9. [`tests/test_demo_simulation.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_demo_simulation.py) (Automated test suite, 16 passed tests)

---

## 6. Single Next Human Action Required

> [!IMPORTANT]
> **Physical Execution of PI Sign-Off Protocol:**  
> The Principal Investigator must open [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) and complete the required sign-off blocks:
> 1. **Section 2.2 (lines 38–49):** Decision D13 (Window max RR gap rule).
> 2. **Section 3.2 (lines 67–78):** Decision D14 (Minimum beats per recording).
> 3. **Section 4.2 (lines 94–104):** Decision D15 (Pipeline runner output guard).
> 4. **Section 5.2 (lines 123–133) & [`label_spec_v1.json:4`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L4):** Label specification approval.
> 5. **Section 6.2 (lines 146–152):** Hardware timing limitation acknowledgement.
> 6. **Section 7.3 (lines 174–181):** Phase 2A gate closure authorization.
> 
> Once signed, execute:
> ```powershell
> python kan_radar_HR/src/closure/phase2c_preflight.py
> ```
> To verify that the preflight verdict transitions from `NO-GO` to `GO`.
