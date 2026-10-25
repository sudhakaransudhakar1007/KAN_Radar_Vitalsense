# PRINCIPAL INVESTIGATOR (PI) PENDING ACTIONS FOR HUMAN REVIEW

**Document ID:** `outputs/closure/pi_pending_actions_for_human_review.md`  
**Execution Stage:** Phase 6B.8 — Implementation and Closure Readiness  
**Target Milestone:** Resolution of Phase 2A/2C Scientific Gate Blockers  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Engineering Role:** Senior Biomedical Signal-Processing Researcher, Test Engineer & Research Governance Auditor  
**Governance State:** **`PENDING FORMAL PI REVIEW & EXECUTION`**  
**Scientific Gate Status:** Strictly **`OPEN`** ([`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md))  
**Preflight Verification Verdict:** Strictly **`NO-GO`** (`10 PASS, 6 FAIL`)  
**Real-Data Operations:** Strictly **`BLOCKED`**  

---

## 1. Executive Summary & Review Scope

The automated Phase 2C preflight suite ([`src/closure/phase2c_preflight.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py)) confirms that all 10 code, unit test, dataset inventory, cryptographic hash, and isolation checks are in a **`PASS`** state. Exactly six checks fail because they represent formal governance determinations and human signatures that cannot legitimately be automated.

> [!IMPORTANT]
> **Separation of Engineering Advice from Official Authority:**
> The engineering team has conducted extensive empirical analyses and provided concrete technical recommendations. However, **engineering recommendations are NOT approvals**. Under institutional research integrity standards, no software engineer, test script, or AI assistant possesses the authority to sign research governance decisions.
>
> All six pending items must be reviewed, selected, and signed by an authorized **human Principal Investigator (PI)**.

---

## 2. Master Governance Blocker & Action Register

The table below summarizes the six pending human actions required to transition the Phase 2A/2C Scientific Gate from **`OPEN`** to **`CLOSED`**:

| Blocker ID | Preflight Check | Target Artifact & Section | Engineering Recommendation (Advice Only) | Evidence to Review | Human Signature Required? |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **B-01** | `GOV_DECISION_D13` | [`pi_signoff_intake_protocol.md:38-49`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L38-L49) | **Option A (Retain $3.0\text{ s}$ threshold)** | Cohort max RR gap $1.292\text{ s}$; $0/1,104$ windows rejected ($100\%$ yield retained). | **YES** |
| **B-02** | `GOV_DECISION_D14` | [`pi_signoff_intake_protocol.md:67-78`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L67-L78) | **Option A (Retain $\ge 20\text{ beats}$ threshold)** | Cohort beat count $99\text{--}157$; $0/48$ recordings rejected ($100\%$ yield retained). | **YES** |
| **B-03** | `GOV_DECISION_D15` | [`pi_signoff_intake_protocol.md:94-104`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L94-L104) | **Option A (Approve programmatic guard)** | Tests passing (3/3); protects audited Phase 2A baseline from silent overwrite. | **YES** |
| **B-04** | `GOV_LABEL_SPEC_APPROVAL` | [`label_spec_v1.json:4`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L4) & [`protocol:123-133`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L123-L133) | **APPROVE Specification v1.0.0** | Canonical SHA-256 `ae5c6780...`; Lead II continuous harmonic mean HR; 1,104 windows. | **YES** |
| **B-05** | `GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT` | [`pi_signoff_intake_protocol.md:146-152`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L146-L152) | **CONFIRM Limitation Acknowledged** | Byte-level audit of 96 MAT files; no PPS/TTL clock; nominal $T_0 = 0.0\text{ s}$ baseline. | **YES** |
| **B-06** | `GOV_PHASE2A_GATE_CLOSURE_AUTH` | [`pi_signoff_intake_protocol.md:174-181`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L174-L181) | **AUTHORIZE Gate Transition** | 28 Phase 2A issues audited (12 resolved, 9 limitations, 7 open); unlocks Phase 2C `run_002`. | **YES** |

---

## 3. Detailed Specification for Each Pending Action

### Action 1: Decision D13 — Window-Level Maximum RR Gap Rule
- **Exact File to Edit:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
- **Exact Section & Lines:** Section 2.2, Lines 38–49
- **Fields Requiring Completion:**
  1. Radio Checkbox: `[X] OPTION A` (or Option B / Option C)
  2. `Selected Option (A, B, or C):`
  3. `Principal Investigator Name:`
  4. `PI Academic / Clinical Title:`
  5. `PI Institution:`
  6. `PI Signature:`
  7. `Date of Execution:` (Format: `YYYY-MM-DD`)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** Select **Option A (Retain $3.0\text{ s}$ threshold)**.  
  > **Rationale:** In [`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98), rejecting windows with an internal RR interval $\ge 3.0\text{ s}$ guards against unflagged sinus pauses, lead disconnection artifacts, or severe ectopic dropouts without sacrificing any valid data. It maintains mathematical symmetry with recording-level SQI.
- **Evidence the PI Must Review:**
  1. [`outputs/closure/window_coverage_gate_diagnostic.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_coverage_gate_diagnostic.csv): Evaluated across all 48 recordings and all 1,104 candidate windows ($24\text{ subjects} \times 2\text{ conditions} \times 23\text{ windows}$). The cohort maximum observed window RR interval is **$1.2920\text{ s}$** (in `VS02_Apnea`). Exactly **0 of 1,104 windows ($0.00\%$)** exceed $3.0\text{ s}$.
  2. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 1`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#1-decision-d13-window-level-maximum-rr-gap-rule).
- **Human Signature Required?**
  **YES.** Physical or verified digital signature of the Principal Investigator is mandatory.

---

### Action 2: Decision D14 — Minimum Valid Beats Per Recording
- **Exact File to Edit:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
- **Exact Section & Lines:** Section 3.2, Lines 67–78
- **Fields Requiring Completion:**
  1. Radio Checkbox: `[X] OPTION A` (or Option B / Option C)
  2. `Selected Option (A, B, or C):`
  3. `Principal Investigator Name:`
  4. `PI Academic / Clinical Title:`
  5. `PI Institution:`
  6. `PI Signature:`
  7. `Date of Execution:` (Format: `YYYY-MM-DD`)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** Select **Option A (Retain $\ge 20\text{ beats}$ threshold)**.  
  > **Rationale:** In [`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283), this rule enforces a defensive baseline sanity floor preventing empty, silent, or severely corrupted files from being processed, with zero cost to valid data yield.
- **Evidence the PI Must Review:**
  1. Empirical beat count distribution across all 48 recordings in the VITALSENSE cohort ($120.0\text{ s}$ @ $500\text{ Hz}$):
     - Minimum: **99 beats** (`VS10_Resting`)
     - Maximum: **157 beats** (`VS14_Apnea`)
     - Mean $\pm$ SD: **$129.2 \pm 14.8\text{ beats}$**
     - Cohort rejection rate at $\ge 20$ beats: **$0 / 48$ recordings ($0.00\%$)**.
  2. Theoretical physiological lower bound: At $35\text{ BPM}$ with $\ge 85\%$ coverage ($102.0\text{ s}$), theoretical floor is $\approx 59.5\text{ beats}$.
  3. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 2`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#2-decision-d14-minimum-valid-beats-per-recording).
- **Human Signature Required?**
  **YES.** Physical or verified digital signature of the Principal Investigator is mandatory.

---

### Action 3: Decision D15 — Pipeline Runner Output Directory Guard
- **Exact File to Edit:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
- **Exact Section & Lines:** Section 4.2, Lines 94–104
- **Fields Requiring Completion:**
  1. Radio Checkbox: `[X] OPTION A` (or Option B)
  2. `Selected Option (A or B):`
  3. `Principal Investigator Name:`
  4. `PI Academic / Clinical Title:`
  5. `PI Institution:`
  6. `PI Signature:`
  7. `Date of Execution:` (Format: `YYYY-MM-DD`)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** Select **Option A (Approve programmatic safeguard)**.  
  > **Rationale:** In [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py), requiring an explicit `output_dir` and blocking writes to `outputs/phase2a` programmatically protects audited baseline files against accidental destruction or non-reproducible overwriting during testing.
- **Evidence the PI Must Review:**
  1. Implementation in [`src/sync_validation/runner.py:34-45`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L34-L45).
  2. Passing automated test suite in [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) (3/3 passing).
  3. Confirmed bit-for-bit SHA-256 hashes of audited baseline files:
     - `outputs/phase2a/step2b_consistency_audit.md`: `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f`
     - `outputs/phase2a/sync_validation_results.csv`: `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10`
  4. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 3`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#3-decision-d15-pipeline-runner-default-output_dir-safeguard).
- **Human Signature Required?**
  **YES.** Physical or verified digital signature of the Principal Investigator is mandatory.

---

### Action 4: Ground-Truth Label Specification Approval (`label_spec_v1.json`)
- **Exact Files to Edit:**
  1. Protocol: [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) (Section 5.2, Lines 123–133)
  2. Spec JSON: [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) (Line 4)
- **Fields Requiring Completion:**
  - In `pi_signoff_intake_protocol.md`:
    1. Radio Checkbox: `[X] APPROVED` (or `[ ] REJECTED`)
    2. `Approval Determination:` (`APPROVED`)
    3. `Approved By (PI Full Name):`
    4. `PI Academic / Clinical Title:`
    5. `PI Institution:`
    6. `PI Signature:`
    7. `Date of Approval:` (Format: `YYYY-MM-DD`)
  - In `label_spec_v1.json`:
    - Line 4: `"approved_by": "<PI Full Name>"` (must match the protocol approver name)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** **Approve `label_spec_v1.json` as the frozen, canonical ground-truth label specification**.  
  > **Rationale:** Standardizes reference ground truth exclusively on continuous ECG Lead II R-peak harmonic mean heart rate, formally disqualifying the commercial monitor `HR` array (due to $+6.21\text{ s}$ systematic latency).
- **Evidence the PI Must Review:**
  1. Specification content in [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json).
  2. Canonical content SHA-256 digest: `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`.
  3. Raw baseline file SHA-256 digest: `a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8`.
  4. Hash invariance design: The canonical hash explicitly omits `"approved_by"` and `"spec_sha256"`. When the PI writes their name into `"approved_by"`, the canonical digest remains identical, allowing automated preflight checks to pass.
  5. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 4`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#4-formal-approval-of-ground-truth-label-specification-label_spec_v1json).
- **Human Signature Required?**
  **YES.** Physical/digital signature in the protocol document AND typed full name in `label_spec_v1.json`.

---

### Action 5: Mandatory Hardware Timing Limitation Acknowledgement
- **Exact File to Edit:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
- **Exact Section & Lines:** Section 6.2, Lines 146–152
- **Fields Requiring Completion:**
  1. `Acknowledged By (PI Name):`
  2. `PI Signature:`
  3. `Date of Acknowledgement:` (Format: `YYYY-MM-DD`)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** **Formally acknowledge and mandate `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` across all future project publications, benchmark tables, and model cards**.  
  > **Rationale:** Protects scientific honesty and prevents false claims of hardware synchronization. The experimental setup used nominal $T_0 = 0.0\text{ s}$ alignment without shared digitizer clocks or physical TTL trigger pulses.
- **Evidence the PI Must Review:**
  1. Byte-level audit of all 96 MAT files in `../data/VITALSENSE_120_DATASET` confirming zero hardware PPS lines or trigger clocks.
  2. Audit of Phase 2A issue ISS-02 in [`outputs/closure/phase2a_reconciliation_addendum.md:lines 37-44`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_reconciliation_addendum.md#item-iss-02-absence-of-hardware-digitizer-synchronization-clocks).
  3. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 5`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#5-mandatory-hardware-timing-limitation-acknowledgement).
- **Human Signature Required?**
  **YES.** Physical or verified digital signature of the Principal Investigator is mandatory.

---

### Action 6: Phase 2A Gate Closure Authorization & Transition to Phase 2C
- **Exact File to Edit:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
- **Exact Section & Lines:** Section 7.3, Lines 174–181
- **Fields Requiring Completion:**
  1. Radio Checkbox: `[X] AUTHORIZED` (or `[ ] NOT AUTHORIZED`)
  2. `Gate Closure Authorization:` (`AUTHORIZED`)
  3. `Principal Investigator Name:`
  4. `PI Signature:`
  5. `Date:` (Format: `YYYY-MM-DD`)
- **Engineering Recommendation (ADVICE ONLY):**
  > **Recommendation:** **Authorize gate closure from `OPEN` to `CLOSED` and authorize Phase 2C execution, conditional upon Actions 1 through 5 being signed**.  
  > **Rationale:** All 28 technical issues from Phase 2A have been accounted for (12 resolved in code, 9 documented limitations, 7 pending governance sign-off). Signing this block authorizes generating the canonical 1,104-window real-data supervised dataset (`outputs/supervised_dataset/run_002`).
- **Evidence the PI Must Review:**
  1. Comprehensive status register of all 28 issues in [`outputs/closure/phase2a_reconciliation_addendum.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_reconciliation_addendum.md).
  2. Master 5-dimension decision matrix in [`outputs/closure/final_go_no_go_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/final_go_no_go_report.md).
  3. Detailed trade-off analysis in [`outputs/closure/pi_decision_recommendations.md:Section 6`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#6-phase-2a-gate-closure-authorization--transition-to-phase-2c).
- **Human Signature Required?**
  **YES.** Physical or verified digital signature of the Principal Investigator is mandatory.

---

## 4. Strict Protocol Formatting Rules for the Reviewer

The automated parser [`src/closure/pi_signoff_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/pi_signoff_validator.py) checks every field syntactically. When completing the documents:

1. **Date Format:** Must strictly follow ISO 8601 `YYYY-MM-DD` (e.g. `2026-10-22`). Any other format (e.g. `10/22/2026` or `Oct 22, 2026`) will trigger `FAIL`.
2. **Eliminate All Placeholders:** Replace all underscores (`_______`), empty brackets, or terms such as `TODO`, `TBD`, and `PENDING`.
3. **Checkbox Notation:** Mark selections with uppercase `[X]`.
4. **Signature Field:** Acceptable inputs include digital signature markers or typed legal name (e.g. `/s/ Dr. Jane Doe`).
5. **JSON Editing Safety:** In [`label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json), edit **only** line 4 (`"approved_by"`). Do not touch any other line or key, ensuring the canonical digest remains `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`.

---

## 5. Verification & Transition Steps Post-Execution

Once all six actions have been completed by the Principal Investigator:

### Step 1: Run Preflight Check
Execute the read-only preflight verification script:
```powershell
python kan_radar_HR/src/closure/phase2c_preflight.py
```
- **Current Pre-Execution Output:** Exit code `1`, Gate: `OPEN`, Verdict: `NO-GO` (10 PASS, 6 FAIL).
- **Expected Post-Execution Output:** Exit code `0`, Gate: `CLOSED`, Verdict: `GO` (16 PASS, 0 FAIL).

### Step 2: Controlled Generation of Phase 2C Supervised Labels
*Only after Step 1 returns exit code 0 (`GO`)*, execute:
```powershell
python kan_radar_HR/src/phase3/supervised_dataset_generator.py `
  --spec kan_radar_HR/outputs/closure/spec/label_spec_v1.json `
  --output_dir kan_radar_HR/outputs/supervised_dataset/run_002
```

---

## 6. Current Operational Status & Safety Boundary Confirmation

- **Scientific Gate Status:** **`OPEN`**
- **Preflight Verdict:** **`NO-GO`**
- **Real-Data Supervised Labels (`outputs/supervised_dataset/run_002`):** **DOES NOT EXIST** (`False`)
- **Real-Data Model Training (`outputs/phase5/run_real_001`):** **DOES NOT EXIST** (`False`)
- **Protected Baseline Hashes:** Verified bit-for-bit identical against historical digests.
- **Unsigned Fields:** Preserved strictly pending genuine human PI review and execution.
