# PRINCIPAL INVESTIGATOR (PI) REVIEW & SIGN-OFF ACTION CHECKLIST

**Document ID:** `outputs/closure/pi_review_action_checklist.md`  
**Execution Stage:** Phase 6B.8 — Implementation and Closure Readiness  
**Target Gate:** Phase 2A/2C Scientific Gate Closure & Phase 2C Authorization  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Engineering Role:** Senior Biomedical Signal-Processing Researcher, Test Engineer & Research Governance Auditor  
**Current Governance State:** **`PENDING FORMAL PI REVIEW & EXECUTION`**  
**Scientific Gate Status:** Strictly **`OPEN`**  
**Preflight Check Verdict:** Strictly **`NO-GO`** (`10 PASS, 6 FAIL`)  

---

## 1. Overview & Instructions for the Principal Investigator

This checklist provides the exact, line-by-line instructions for the Principal Investigator (or authorized human reviewer) to execute the six pending governance items required to close the Phase 2A Scientific Gate and authorize Phase 2C real-data supervised label generation.

> [!IMPORTANT]
> **No Automated Execution:** Automated scripts cannot sign these items. All sign-off fields must be executed manually by a designated human investigator.
>
> **Fail-Closed Protection:** The repository blocks all real-data operations until `phase2c_preflight.py` returns **`GO`** (16/16 checks passing).

### Required Files for Review:
1. Intake Protocol Document: [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md)
2. Label Specification JSON: [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json)
3. Technical Trade-Off Analysis: [`outputs/closure/pi_decision_recommendations.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md)

---

## 2. Formatting Rules & Parsing Requirements

The automated governance validator ([`src/closure/pi_signoff_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/pi_signoff_validator.py)) parses these markdown blocks directly. To ensure successful validation:

1. **Dates Must Be ISO 8601:** Format must be strictly `YYYY-MM-DD` (e.g. `2026-10-22`). Non-ISO dates (such as `10/22/2026` or `October 22, 2026`) will fail automated validation.
2. **No Placeholder Characters:** Remove all underscores (`_____`), brackets, or keywords like `TODO`, `TBD`, or `PENDING`.
3. **Checkbox Format:** Use `[X]` (capital X) to indicate selected options and approvals.
4. **Signature Field:** Digital signatures or typed full legal names (e.g. `/s/ Dr. Jane Doe`) are accepted by the syntactic validator.
5. **Specification Hash Invariance:** In `label_spec_v1.json`, only edit the `"approved_by"` field on line 4. Do not alter any other keys or formatting, ensuring the canonical hash remains `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`.

---

## 3. Step-by-Step Action Items

### Step 1: Execute Decision D13 (Window-Level Maximum RR Gap Rule)
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 38–49 (Section 2.2)
- **Engineering Recommendation:** Option A (Retain $3.0\text{ s}$ threshold; $0\%$ data loss).
- **Action Required:** Select option, provide PI name, title, institution, signature, and date:
```markdown
[X] OPTION A: RETAIN window-level maximum RR gap threshold at 3.0 s (Ensures consistency with recording-level SQI).
[ ] OPTION B: DROP window-level max-gap rule (Rely exclusively on cumulative valid RR duration coverage >= 80%).
[ ] OPTION C: REVISE window-level max-gap threshold to an alternative physiological limit (e.g. 4.0 s).

Selected Option (A, B, or C): Option A
Principal Investigator Name:  Dr. Jane Doe
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               University Medical Center
PI Signature:                 /s/ Dr. Jane Doe
Date of Execution:            2026-10-22
```

---

### Step 2: Execute Decision D14 (Minimum Valid Beats Per Recording)
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 67–78 (Section 3.2)
- **Engineering Recommendation:** Option A (Retain $\ge 20\text{ beats}$ threshold; cohort min is 99 beats; $0\%$ data loss).
- **Action Required:** Select option, provide PI name, title, institution, signature, and date:
```markdown
[X] OPTION A: RETAIN minimum valid beat threshold of >= 20 beats per 120 s recording.
[ ] OPTION B: DROP beat count threshold (Rely strictly on duration coverage > 85% of recording).
[ ] OPTION C: REVISE beat count threshold to an alternative count (e.g. 30 beats).

Selected Option (A, B, or C): Option A
Principal Investigator Name:  Dr. Jane Doe
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               University Medical Center
PI Signature:                 /s/ Dr. Jane Doe
Date of Execution:            2026-10-22
```

---

### Step 3: Execute Decision D15 (Pipeline Runner Default `output_dir` Safeguard)
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 94–104 (Section 4.2)
- **Engineering Recommendation:** Option A (Approve programmatic code guard to prevent baseline overwrite).
- **Action Required:** Select option, provide PI name, title, institution, signature, and date:
```markdown
[X] OPTION A: APPROVE programmatic code safeguard in src/sync_validation/runner.py (Requires explicit output_dir; blocks unauthorized overwrite of outputs/phase2a/).
[ ] OPTION B: REJECT code safeguard and revert to procedural documentation only.

Selected Option (A or B):     Option A
Principal Investigator Name:  Dr. Jane Doe
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               University Medical Center
PI Signature:                 /s/ Dr. Jane Doe
Date of Execution:            2026-10-22
```

---

### Step 4: Approve Ground-Truth Label Specification (`label_spec_v1.json`)
This step requires actions in **two separate files**:

#### Action 4A: Sign Protocol Section 5.2
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 123–133 (Section 5.2)
- **Engineering Recommendation:** Approve specification v1.0.0.
- **Action Required:**
```markdown
[X] APPROVED: I hereby approve outputs/closure/spec/label_spec_v1.json (SHA-256: a0f7a85e...) as the frozen, canonical reference label specification for the project.
[ ] REJECTED: Revisions required prior to approval.

Approval Determination:       APPROVED
Approved By (PI Full Name):   Dr. Jane Doe
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               University Medical Center
PI Signature:                 /s/ Dr. Jane Doe
Date of Approval:             2026-10-22
```

#### Action 4B: Populate `approved_by` in `label_spec_v1.json`
- **File:** `outputs/closure/spec/label_spec_v1.json`
- **Location:** Line 4
- **Action Required:** Change `"approved_by": ""` to:
```json
  "approved_by": "Dr. Jane Doe",
```
> [!NOTE]
> Populating `"approved_by"` does NOT change the canonical SHA-256 hash (`ae5c6780...`), because the canonical hashing function deliberately omits `"approved_by"` and `"spec_sha256"`.

---

### Step 5: Execute Mandatory Hardware Timing Limitation Acknowledgement
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 146–152 (Section 6.2)
- **Engineering Recommendation:** Acknowledge nominal $T_0 = 0.0\text{ s}$ baseline and mandate `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` across all future project publications.
- **Action Required:**
```markdown
I formally acknowledge and confirm that hardware clock synchronization between the 120-GHz FMCW radar and the reference ECG digitizer is unverified. I mandate that all future publications, project documentation, model cards, and benchmark tables must explicitly cite the standardized limitation: 'UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0'.

Acknowledged By (PI Name):    Dr. Jane Doe
PI Signature:                 /s/ Dr. Jane Doe
Date of Acknowledgement:      2026-10-22
```

---

### Step 6: Authorize Phase 2A Gate Closure & Phase 2C Execution
- **File:** `outputs/closure/pi_signoff_intake_protocol.md`
- **Location:** Lines 174–181 (Section 7.3)
- **Engineering Recommendation:** Authorize transition from `OPEN` to `CLOSED`.
- **Action Required:**
```markdown
I hereby confirm that upon execution of Sections 2 through 6 above, the Phase 2A/2C Scientific Gate is authorized to transition from OPEN to CLOSED. I authorize the engineering team to generate the canonical Phase 2C supervised dataset ('run_002') in strict accordance with label_spec_v1.json.

Gate Closure Authorization:   [X] AUTHORIZED    [ ] NOT AUTHORIZED
Principal Investigator Name:  Dr. Jane Doe
PI Signature:                 /s/ Dr. Jane Doe
Date:                         2026-10-22
```

---

## 4. Automated Verification Procedure

Immediately after completing Steps 1 through 6, execute the read-only preflight check from the project root:

```powershell
python kan_radar_HR/src/closure/phase2c_preflight.py
```

### Expected Output Upon Successful PI Execution:
```
=================================================================
PHASE 2C PREFLIGHT VERIFICATION REPORT
=================================================================
Gate Status:                 CLOSED
Preflight Verdict:           GO
Authorized for Phase 2C:     True
Summary:                     {'PASS': 16, 'FAIL': 0, 'WARN': 0}

--- DETAILED CHECK RESULTS ---
  [PASS  ] [GOVERNANCE      ] GOV_DECISION_D13: Valid D13 decision selection, signature, and date.
  [PASS  ] [GOVERNANCE      ] GOV_DECISION_D14: Valid D14 decision selection, signature, and date.
  [PASS  ] [GOVERNANCE      ] GOV_DECISION_D15: Valid D15 decision selection, signature, and date.
  [PASS  ] [GOVERNANCE      ] GOV_LABEL_SPEC_APPROVAL: Approved by: Dr. Jane Doe
  [PASS  ] [GOVERNANCE      ] GOV_LABEL_SPEC_HASH: Canonical content SHA-256 matched: ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44
  [PASS  ] [GOVERNANCE      ] GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT: Hardware timing limitation explicitly acknowledged and signed.
  [PASS  ] [GOVERNANCE      ] GOV_PHASE2A_RECONCILIATION_ADDENDUM: Addendum present; tracks all 28 Phase 2A issues.
  [PASS  ] [GOVERNANCE      ] GOV_PHASE2A_GATE_CLOSURE_AUTH: Formal gate closure explicitly authorized by PI.
  [PASS  ] [LABEL_SPEC      ] LABEL_SPEC_INTEGRITY: Canonical hash matched (ae5c67808b9a...), window parameters and SQI validated.
  [PASS  ] [RECONCILIATION  ] PHASE2A_ADDENDUM_INTEGRITY: Addendum presents complete audit for all 28 issues (12 resolved, 9 documented limitations, 7 open).
  [PASS  ] [RECONCILIATION  ] PHASE2A_BASELINE_HASH: Phase 2A baseline hash verified bit-for-bit (6c4391bf1f8b...).
  [PASS  ] [SOURCE_DATA     ] SOURCE_DATASET_INVENTORY: Complete cohort verified: 48 radar recordings and 48 reference ECG MAT files.
  [PASS  ] [ISOLATION       ] OUTPUT_ISOLATION_RUN_002: Confirmed: outputs/supervised_dataset/run_002 does not exist (isolation preserved).
  [PASS  ] [ISOLATION       ] OUTPUT_ISOLATION_REAL_TRAINING: Confirmed: outputs/phase5/run_real_001 does not exist (training isolation preserved).
  [PASS  ] [WINDOWING       ] WINDOW_DENOMINATOR_CONSISTENCY: Denominator verified: exactly 1104 candidate windows across 48 recordings (1104 accepted under SQI).
  [PASS  ] [HARDWARE_LIMITATION] HARDWARE_TIMING_LIMITATION_GUARD: Hardware timing limitation UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 strictly documented in spec and intake protocol.
=================================================================
ALL PREFLIGHT CHECKS PASSED. Ready for controlled Phase 2C execution.
=================================================================
```

---

## 5. Authorized Phase 2C Execution (Post-Approval Only)

Only after the preflight verification command outputs `Preflight Verdict: GO` and exit code `0`, the engineering team is authorized to execute:

```powershell
python kan_radar_HR/src/phase3/supervised_dataset_generator.py `
  --spec kan_radar_HR/outputs/closure/spec/label_spec_v1.json `
  --output_dir kan_radar_HR/outputs/supervised_dataset/run_002
```

This will safely generate `outputs/supervised_dataset/run_002` containing exactly 1,104 supervised window feature-label pairs with cryptographic SHA-256 manifests.
