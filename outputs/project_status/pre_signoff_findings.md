# PRE-SIGNOFF AUDIT FINDINGS & GOVERNANCE MECHANISM REPORT

**Project:** *A Subject-Independent Kolmogorov-Arnold Network (KAN)-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Repository Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Document Path:** [`outputs/project_status/pre_signoff_findings.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/project_status/pre_signoff_findings.md)  
**Execution Timestamp:** 2026-10-25  
**Evaluation Mode:** Read-Only Audit (Zero file modifications, zero gate state alterations, zero label generation, zero real-data model training)  

---

## 1. Baseline Hash Check vs. In-Place Modification of Consistency Audit

### 1.1 Question
*If line 14 (or line 9) of `step2b_consistency_audit.md` is modified from `RECONCILIATION PARTIAL` to `CLOSED`, would the baseline-hash check in `src/closure/phase2c_preflight.py` still PASS? If it fails, what is the sanctioned closure mechanism and exact steps the PI must follow?*

### 1.2 Inspection & Determination
- **Direct Path Verification:** The file referenced by preflight is [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md) (no file exists at `outputs/closure/step2b_consistency_audit.md`).
- **Preflight Hash Logic:** In [`src/closure/phase2c_preflight.py:293-330`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py#L293-L330), the checker executes:
  ```python
  h = hashlib.sha256(audit_file.read_bytes()).hexdigest().lower()
  if h != EXPECTED_PHASE2A_AUDIT_SHA256:
      # Preflight check PHASE2A_BASELINE_HASH FAILS
  ```
  Where `EXPECTED_PHASE2A_AUDIT_SHA256 = "6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f"`.
- **Verdict on In-Place Modification:** **`WOULD FAIL`**. If an investigator or engineer edits line 14 (or line 9) of `outputs/phase2a/step2b_consistency_audit.md` to change status to `CLOSED`, the file's raw SHA-256 byte digest changes. This causes `PHASE2A_BASELINE_HASH` to fail with `Audit hash mismatch`, permanently blocking preflight with a `NO-GO` verdict.

### 1.3 Sanctioned Closure Mechanism
The repository enforces a **Non-Destructive Closure Addendum Architecture**:
1. **Bit-for-Bit Immutability of Phase 2A:** The baseline Phase 2A audit ([`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md)) is frozen as an immutable historical record (`6c4391bf...`).
2. **Reconciliation Addendum:** [`outputs/closure/phase2a_reconciliation_addendum.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_reconciliation_addendum.md) explicitly declares in line 9:
   > *"Baseline Immutability Notice: This document is a non-destructive closure addendum. The baseline Phase 2A audit (step2b_consistency_audit.md, SHA-256: 6c4391bf...) remains strictly bit-for-bit immutable."*
3. **Formal Gate Authorization:** The formal gate closure is executed exclusively through **Section 7.3** of [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L174-L181) and confirmed by the existence of a signed [`outputs/closure/investigator_decision.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/investigator_decision.md).

### 1.4 Exact Steps the PI Must Follow
1. Do **NOT** edit `outputs/phase2a/step2b_consistency_audit.md`. Leave it completely untouched.
2. Open [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md).
3. Complete Sections 2.2 (D13), 3.2 (D14), 4.2 (D15), 5.2 (Label Spec), and 6.2 (Hardware Timing Acknowledgement).
4. In Section 7.3, check `[X] AUTHORIZED`, enter PI Name, PI Signature, and Date (`YYYY-MM-DD`).
5. Copy [`outputs/closure/investigator_decision_template.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/investigator_decision_template.md) to [`outputs/closure/investigator_decision.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/investigator_decision.md), filling in the PI signature and date.

---

## 2. Mapping of the 7 Pending Phase 2A Issues to Sign-Off Items

In [`outputs/closure/phase2a_reconciliation_addendum.md:20`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_reconciliation_addendum.md#L20) and [`outputs/closure/pi_decision_recommendations.md:302`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#L302), seven Phase 2A issues are tracked as pending. All 7 map directly into the six PI sign-off items:

| Phase 2A Issue ID | Description from Consistency Register | Mapped Governance Sign-Off Item | Mapping Status | Resolution / Clinical Impact |
| :--- | :--- | :--- | :--- | :--- |
| **ISS-07** | Lumping lags $< 4\text{ s}$ into `NEAR_ZERO_LATENCY` in legacy runner | **Item 6: Gate Closure Authorization (GATE-AUTH)** | **MAPPED** | Legacy Phase 2A reporting artifact. Bypassed in Phase 3/5 by continuous R-peak instantaneous HR. Accepted under gate closure addendum. |
| **ISS-08** | Superficial ECG quality check ($5$ valid beats in $120\text{ s}$) | **Item 2: Decision D14 & Item 1: Decision D13** | **MAPPED** | Resolved in code by multi-parameter SQI ($\ge 20$ beats, $> 85\%$ coverage, max gap $< 3.0\text{ s}$). Formally approved via Decisions D14 and D13. |
| **ISS-10** | In-sample shift optimization selection optimism ($\tau \in [-5, +5]\text{ s}$) | **Item 4: Label Spec v1.0.0 & Item 3: Decision D15** | **MAPPED** | Resolved by specification: zero-shift baseline ($\tau = 0.0\text{ s}$) codified in `label_spec_v1.json`. Runner guard D15 prevents unconstrained search overwrites. |
| **ISS-12** | `VS24_Resting_Mindray.mat` formatting divergence ($30,600$ samples) | **Item 6: Gate Closure Authorization (GATE-AUTH)** | **MAPPED** | Documented reproducible anomaly affecting respiration only. ECG has full 60,000 samples. Dynamic length handling implemented in code. Accepted under gate closure. |
| **ISS-15** | Test assertion threshold loosening ($r < 0.75$) in surrogate control | **Item 6: Gate Closure Authorization (GATE-AUTH)** | **MAPPED** | Exploratory surrogate test threshold. Acknowledged as non-blocking for cardiac supervised training. Formally closed under gate authorization. |
| **ISS-17** | Small surrogate control sample size ($N=5$) | **Item 5: Hardware Timing Acknowledgement (HW-SYNC)** | **MAPPED** | Demonstrates that surrogate tests cannot mathematically prove hardware synchronization; directly reinforces mandatory citation of `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. |
| **ISS-22** | Sensitivity analysis of VS24 respiration tail truncation | **Item 6: Gate Closure Authorization (GATE-AUTH)** | **MAPPED** | Respiration channel artifact only. Cardiac radar displacement and ECG ground truth are completely unaffected. Accepted under gate closure. |

### Unmapped Issues Finding:
- **Zero Unmapped Issues:** Exactly **0** of the 7 pending Phase 2A issues are unmapped. All 7 items are completely covered by Decisions D13, D14, D15, Label Spec Approval, Hardware Timing Acknowledgement, and Gate Closure Authorization.

---

## 3. Pipeline Runner Override Flag for `outputs/phase2a`

### 3.1 Override Flag Identification
In [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py):
- **Parameter Name:** `allow_phase2a_overwrite: bool = False`
- **Location:** Present in both `run_full_validation()` (line 85) and `run_sync_validation()` (line 253).

### 3.2 Guard Implementation
```python
if (out_resolved == phase2a_resolved or (out_resolved.name == "phase2a" and out_resolved.parent.name == "outputs")) and not allow_phase2a_overwrite:
    raise PermissionError(
        "Writing directly to immutable 'outputs/phase2a' is blocked by governance guard. "
        "Pass allow_phase2a_overwrite=True to override."
    )
```

### 3.3 Documentation & Test Coverage Status
- **Documentation:** **YES (Fully Documented)**. Documented in function docstrings (`runner.py:92`), exception strings (`runner.py:105,267`), [`pi_decision_recommendations.md:173`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_decision_recommendations.md#L173), and [`pi_signoff_intake_protocol.md:87`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md#L87).
- **Test Coverage:** **YES (Covered by Regression Tests)**. In [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py), `test_protected_phase2a_raises_permission_error` explicitly verifies that attempting to target `outputs/phase2a` raises `PermissionError` when `allow_phase2a_overwrite=False`. (Setting `allow_phase2a_overwrite=True` is deliberately omitted from tests to ensure automated test suites never overwrite live baseline files).

---

## 4. Regression Test for `--real` Mode Raising `GateBlockerError`

### 4.1 Identified Test
- **Test Function:** `test_fail_closed_real_data_gate_enforcement`
- **Test File:** [`tests/test_phase5_training.py:234-247`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_phase5_training.py#L234-L247)
- **Implementation:**
  ```python
  def test_fail_closed_real_data_gate_enforcement():
      """Verify that attempting real-data training aborts with GateBlockerError when gate is OPEN."""
      base_dir = Path(__file__).resolve().parents[1]
      is_approved, reason = verify_gate_approval_for_real_data(base_dir)

      # In current state, gate must NOT be approved
      assert not is_approved, "Expected gate approval to be FALSE in current codebase."

      cfg = TrainingConfig(mode="real", output_dir="outputs/phase5/blocked_run")
      trainer = KANTrainer(cfg, base_dir=base_dir)

      with pytest.raises(GateBlockerError, match="Real-data training BLOCKED"):
          trainer.execute_training()
  ```

### 4.2 CLI Behavior
When executed via the command line ([`src/kan/train_cli.py:149-151`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/train_cli.py#L149-L151)):
- Supplying `--real` while the gate is `OPEN` causes `execute_training()` to raise `GateBlockerError`.
- `train_cli.py` catches the error, outputs `Execution Terminated: Real-data training BLOCKED: ...` to `stderr`, and terminates with exit code `2`.

---

## 5. Live Preflight Terminal Verification

Executed command from repository root:
```powershell
python src/closure/phase2c_preflight.py
```

### Exact Terminal Output:
```
=================================================================
PHASE 2C PREFLIGHT VERIFICATION REPORT (2026-10-25T06:06:25.319516+00:00)
=================================================================
Gate Status:                 OPEN
Preflight Verdict:           NO-GO
Authorized for Phase 2C:     False
Summary:                     {'PASS': 10, 'FAIL': 6, 'WARN': 0}

--- DETAILED CHECK RESULTS ---
  [FAIL  ] [GOVERNANCE      ] GOV_DECISION_D13: Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  [FAIL  ] [GOVERNANCE      ] GOV_DECISION_D14: Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  [FAIL  ] [GOVERNANCE      ] GOV_DECISION_D15: Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  [FAIL  ] [GOVERNANCE      ] GOV_LABEL_SPEC_APPROVAL: label_spec_v1.json 'approved_by' field is empty or blank.
  [PASS  ] [GOVERNANCE      ] GOV_LABEL_SPEC_HASH: Canonical content SHA-256 matched: ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44
  [FAIL  ] [GOVERNANCE      ] GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT: PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  [PASS  ] [GOVERNANCE      ] GOV_PHASE2A_RECONCILIATION_ADDENDUM: Addendum present; tracks all 28 Phase 2A issues.
  [FAIL  ] [GOVERNANCE      ] GOV_PHASE2A_GATE_CLOSURE_AUTH: PI marked gate closure as NOT AUTHORIZED.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  [PASS  ] [LABEL_SPEC      ] LABEL_SPEC_INTEGRITY: Canonical hash matched (ae5c67808b9a...), window parameters and SQI validated.
  [PASS  ] [RECONCILIATION  ] PHASE2A_ADDENDUM_INTEGRITY: Addendum presents complete audit for all 28 issues (12 resolved, 9 documented limitations, 7 open).
  [PASS  ] [RECONCILIATION  ] PHASE2A_BASELINE_HASH: Phase 2A baseline hash verified bit-for-bit (6c4391bf1f8b...).
  [PASS  ] [SOURCE_DATA     ] SOURCE_DATASET_INVENTORY: Complete cohort verified: 48 radar recordings and 48 reference ECG MAT files.
  [PASS  ] [ISOLATION       ] OUTPUT_ISOLATION_RUN_002: Confirmed: outputs/supervised_dataset/run_002 does not exist (isolation preserved).
  [PASS  ] [ISOLATION       ] OUTPUT_ISOLATION_REAL_TRAINING: Confirmed: outputs/phase5/run_real_001 does not exist (training isolation preserved).
  [PASS  ] [WINDOWING       ] WINDOW_DENOMINATOR_CONSISTENCY: Denominator verified: exactly 1104 candidate windows across 48 recordings (1104 accepted under SQI).
  [PASS  ] [HARDWARE_LIMITATION] HARDWARE_TIMING_LIMITATION_GUARD: Hardware timing limitation UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 strictly documented in spec and intake protocol.
=================================================================

BLOCKERS (Gate remains OPEN, Phase 2C execution prohibited):
  - [GOV_DECISION_D13] Decision D13: Window-Level Maximum RR Gap Rule (3.0 s): Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  - [GOV_DECISION_D14] Decision D14: Minimum Valid Beats Per Recording (20 Beats): Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  - [GOV_DECISION_D15] Decision D15: Pipeline Runner Default output_dir Guard: Option selection is missing or placeholder.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  - [GOV_LABEL_SPEC_APPROVAL] Label Specification Approval Field (label_spec_v1.json): label_spec_v1.json 'approved_by' field is empty or blank.
  - [GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT] Mandatory Hardware Timing Limitation (UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0): PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
  - [GOV_PHASE2A_GATE_CLOSURE_AUTH] Phase 2A Gate Closure Authorization: PI marked gate closure as NOT AUTHORIZED.; PI Name is missing or placeholder.; PI Signature is missing or placeholder.; Date error: Date is empty or placeholder.
=================================================================
```
- **Exit Code:** `1`
- **Preflight Verdict:** `NO-GO`
- **Gate Status:** `OPEN`

---

## 6. Uncertainty Analysis & Safety Boundaries

1. **Format Uncertainty Regarding Consistency Audit Path:** The prompt query referenced `outputs/closure/step2b_consistency_audit.md`. The actual canonical location on disk is [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md). Preflight explicitly tracks this path under `outputs/phase2a/`.
2. **Canonical Hash Invariance Assurance:** In `label_spec_v1.json`, populating `"approved_by"` does not change the canonical SHA-256 (`ae5c6780...`) because canonical hashing deliberately excludes `"approved_by"` and `"spec_sha256"`.
3. **Immutability Assurance:** Zero baseline files, zero scientific thresholds, and zero gate validators were modified during this read-only audit.

---

## 7. Single Next Human Action Required

> [!IMPORTANT]
> **Complete the PI Sign-Off Intake Protocol Without Modifying Baseline Audit Files:**  
> Open [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) and fill in the required decision and signature blocks:
> - **Section 2.2 (lines 38–49):** Decision D13
> - **Section 3.2 (lines 67–78):** Decision D14
> - **Section 4.2 (lines 94–104):** Decision D15
> - **Section 5.2 (lines 123–133):** Label Specification Approval (and set `"approved_by"` in [`label_spec_v1.json:4`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L4))
> - **Section 6.2 (lines 146–152):** Hardware Timing Limitation Acknowledgement
> - **Section 7.3 (lines 174–181):** Phase 2A Gate Closure Authorization
> 
> *(Do not modify `step2b_consistency_audit.md`).*
> 
> Then execute:
> ```powershell
> python kan_radar_HR/src/closure/phase2c_preflight.py
> ```
> To verify that the preflight verdict transitions from `NO-GO` to `GO`.
