# PRINCIPAL INVESTIGATOR (PI) SIGN-OFF INTAKE PROTOCOL

**Document ID:** `outputs/closure/pi_signoff_intake_protocol.md`  
**Execution Stage:** Phase 6B.7 — PI Sign-Off Intake, Gate Closure Re-Verification & Controlled Phase 2C Authorization  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date of Intake Protocol Generation:** October 2026  
**Auditor / Engineering Role:** Senior Biomedical Signal-Processing Researcher, Test Engineer & Research Governance Auditor  
**Governance Status:** **`PENDING FORMAL PI REVIEW & EXECUTION`**  
**Scientific Gate Status:** Strictly **`OPEN`** (`outputs/phase2a/step2b_consistency_audit.md`)  
**Supervised Label Generation & Real Training:** Strictly **`BLOCKED`**  

---

## 1. Governance Preamble & Instructions for the Principal Investigator

This document serves as the formal, auditable intake protocol for Principal Investigator (PI) review, decision selection, and official sign-off.

### Mandatory Governance Rules:
1. **Technical Recommendations are NOT Approvals:** The technical and engineering team has conducted extensive empirical recomputations across all 48 recordings ($1,104$ candidate windows) and presented evidence-based recommendations. However, recommendations do not constitute formal approval.
2. **Explicit PI Signature Required:** Under project research integrity standards, no real-data ground-truth labels may be generated (`run_002`), and no real VITALSENSE radar signals may be used for model training until this document is formally executed by the Principal Investigator.
3. **No Automated Gate Closure:** The Phase 2A/2C Scientific Gate remains **`OPEN`** until the PI signs each section below and formally authorizes gate closure.

---

## 2. Decision D13: Window-Level Maximum RR Gap Rule (3.0 s Threshold)

### 2.1 Technical Background & Context
- **Issue:** Whether to retain the window-level quality rule rejecting windows where the maximum RR interval is $\ge 3.0\text{ s}$ ([`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98)), drop the rule, or alter the threshold.
- **Empirical Evidence:**
  - Evaluated across all 48 recordings and all 1,104 candidate windows in the VITALSENSE dataset.
  - The maximum observed window RR interval in the entire cohort is **$1.2920\text{ s}$** (observed in `VS02_Apnea`).
  - Exactly **0 of 1,104 windows** ($0.00\%$) exceed the $3.0\text{ s}$ threshold.
  - Applying the $3.0\text{ s}$ rule results in **zero yield loss** ($100.00\%$ retention, $1,104 / 1,104$ windows accepted).
- **Engineering Recommendation:** **Option A (Retain $3.0\text{ s}$ threshold).** Ensures mathematical consistency with recording-level SQI ($\max(\text{RR gap}) < 3.0\text{ s}$) and guards against localized pause episodes without dropping any real data.

### 2.2 Formal PI Decision & Sign-Off Block for D13

```
[ ] OPTION A: RETAIN window-level maximum RR gap threshold at 3.0 s (Ensures consistency with recording-level SQI).
[ ] OPTION B: DROP window-level max-gap rule (Rely exclusively on cumulative valid RR duration coverage >= 80%).
[ ] OPTION C: REVISE window-level max-gap threshold to an alternative physiological limit (e.g. 4.0 s).

Selected Option (A, B, or C): ___________________________
Principal Investigator Name:  ___________________________
PI Academic / Clinical Title: ___________________________
PI Institution:               ___________________________
PI Signature:                 ___________________________
Date of Execution:            ___________________________
```

---

## 3. Decision D14: Minimum Valid Beats Per Recording (20 Beats Threshold)

### 3.1 Technical Background & Context
- **Issue:** Whether to retain the recording-level SQI requirement of at least 20 valid RR beats ([`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283)), drop the rule, or adjust the beat threshold.
- **Empirical Evidence:**
  - Evaluated across all 48 recordings ($60,000\text{ samples}$ @ $500\text{ Hz} = 120\text{ s}$ per recording).
  - Empirical beat count distribution: Minimum = **99 beats** (in `VS10_Resting`), Maximum = **157 beats** (in `VS14_Apnea`), Mean = **$129.2 \pm 14.8$ beats**, Median = **130.5 beats**.
  - A threshold of 20 beats rejects **0 of 48 recordings** ($0.0\%$ rejection rate).
  - An alternative threshold of 30 beats also rejects **0 of 48 recordings** ($0.0\%$ rejection rate).
  - For a 120-second recording with $\ge 85\%$ coverage ($102\text{ s}$) at the minimum physiological rate ($35\text{ BPM}$), the theoretical floor is $\approx 59.5\text{ beats}$.
- **Engineering Recommendation:** **Option A (Retain 20 beats threshold).** Serves as a non-binding, uncostly defense-in-depth lower invariant protecting against truncated or heavily corrupted recording files.

### 3.2 Formal PI Decision & Sign-Off Block for D14

```
[ ] OPTION A: RETAIN minimum valid beat threshold of >= 20 beats per 120 s recording.
[ ] OPTION B: DROP beat count threshold (Rely strictly on duration coverage > 85% of recording).
[ ] OPTION C: REVISE beat count threshold to an alternative count (e.g. 30 beats).

Selected Option (A, B, or C): ___________________________
Principal Investigator Name:  ___________________________
PI Academic / Clinical Title: ___________________________
PI Institution:               ___________________________
PI Signature:                 ___________________________
Date of Execution:            ___________________________
```

---

## 4. Decision D15: Pipeline Runner Default `output_dir` Safeguard

### 4.1 Technical Background & Context
- **Issue:** Whether to enforce code safeguards requiring an explicit `output_dir` in [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py) to prevent accidental overwrites of the audited Phase 2A baseline, or rely strictly on operational documentation.
- **Implementation & Testing Evidence:**
  - Implemented in `src/sync_validation/runner.py`: omitting `output_dir` raises `ValueError`; directing to `outputs/phase2a` without `allow_phase2a_overwrite=True` raises `PermissionError`.
  - Automated tests in [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) passed ($3/3$).
  - Phase 2A audited baseline files verified strictly bit-for-bit unchanged (`step2b_consistency_audit.md` SHA-256: `6c4391bf...`, `sync_validation_results.csv` SHA-256: `6f4fda36...`).
- **Engineering Recommendation:** **Option A (Approve programmatic code safeguard).** Enforces hard technical boundaries against accidental baseline corruption.

### 4.2 Formal PI Decision & Sign-Off Block for D15

```
[ ] OPTION A: APPROVE programmatic code safeguard in src/sync_validation/runner.py (Requires explicit output_dir; blocks unauthorized overwrite of outputs/phase2a/).
[ ] OPTION B: REJECT code safeguard and revert to procedural documentation only.

Selected Option (A or B):     ___________________________
Principal Investigator Name:  ___________________________
PI Academic / Clinical Title: ___________________________
PI Institution:               ___________________________
PI Signature:                 ___________________________
Date of Execution:            ___________________________
```

---

## 5. Formal Approval of Ground-Truth Label Specification (`label_spec_v1.json`)

### 5.1 Technical Background & Specification Hash
- **Specification Path:** [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json)
- **Canonical SHA-256 Digest:** `a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8`
- **Core Specification Invariants:**
  1. Windowing: 10.0 s duration, 5.0 s hop, continuous temporal formula $t_{\text{start}} = \text{round}(k \times 5.0, 3)$ yielding exactly 23 windows per recording (1,104 candidate windows).
  2. Reference Source: Lead II (`ecg_lead2`). Commercial monitor `HR` array strictly excluded (due to $+6.21\text{ s}$ systematic latency).
  3. Preprocessing: Delimiter NaN interpolation (`clean_ecg_nans`) with `only_isolated: true, fill_boundary: true`.
  4. Detection: Pan-Tompkins with absolute fiducial refinement $\text{argmax}(|\text{filtered}|)$ resolving inverted lead morphology (`VS19`).
  5. Label Formula: Harmonic mean $\text{HR} = 60.0 / \text{mean}(w\_rrs)$ of all valid intervals whose midpoints fall in $[t_{\text{start}}, t_{\text{end}})$.
  6. Quality Gating: Strict all-or-nothing outlier rejection (35–185 BPM), covered duration $> 8.0\text{ s}$, max RR gap $< 3.0\text{ s}$.

### 5.2 Formal PI Approval Block for `label_spec_v1.json`

```
[ ] APPROVED: I hereby approve outputs/closure/spec/label_spec_v1.json (SHA-256: a0f7a85e...) as the frozen, canonical reference label specification for the project.
[ ] REJECTED: Revisions required prior to approval.

Approval Determination:       ___________________________
Approved By (PI Full Name):   ___________________________
PI Academic / Clinical Title: ___________________________
PI Institution:               ___________________________
PI Signature:                 ___________________________
Date of Approval:             ___________________________
```

---

## 6. Mandatory Hardware Timing Limitation Acknowledgement

### 6.1 Statement of Physical Acquisition Limitation
Byte-level audit of all 96 MAT files in the VITALSENSE dataset confirmed the complete absence of pulse-per-second (PPS) hardware lines, external TTL trigger timestamps, or shared digitizer clocks. 

Nominal alignment at $T_0 = 0.0\text{ s}$ is an operational computational assumption, not a verified physical hardware clock synchronization. Physiological pulse transit time (PTT, $\sim 100\text{--}250\text{ ms}$), physical pulse wave propagation, and manual recording startup latencies cannot be disentangled without external physical triggers.

### 6.2 Formal PI Limitation Acknowledgement Block

```
I formally acknowledge and confirm that hardware clock synchronization between the 120-GHz FMCW radar and the reference ECG digitizer is unverified. I mandate that all future publications, project documentation, model cards, and benchmark tables must explicitly cite the standardized limitation: 'UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0'.

Acknowledged By (PI Name):    ___________________________
PI Signature:                 ___________________________
Date of Acknowledgement:      ___________________________
```

---

## 7. Phase 2A Gate Reconciliation Status & Outstanding Closure Evidence

### 7.1 Status of Phase 2A Consistency Audit
The baseline audit in [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md) currently documents:
`Audit Status: PHASE 2A – STEP 2B STATUS: RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION.`

### 7.2 Checklist of Required Closure Evidence:
1. **[X] Harmonization of Preprocessing:** `clean_ecg_nans` harmonized across `src.sync_validation` and `src.phase3` to support `fill_boundary: bool = True`.
2. **[X] Parabolic Peak Interpolation & Zero-Padding:** 4x zero-padding and 3-point parabolic peak interpolation implemented and verified in `tests/test_stage2_closure.py`.
3. **[X] Discrepancy Reporting:** Resolved contradictions regarding surrogate correlations (true max: 0.8123, mean: 0.5077) and negative polarity subject IDs (`VS09`, `VS20`).
4. **[X] Immutability of Phase 2A Baseline:** Programmatic guard implemented and verified; original audit files verified bit-for-bit unchanged.
5. **[ ] Formal PI Sign-Off of Decisions D13, D14, D15:** PENDING (Sections 2, 3, 4 above).
6. **[ ] Formal PI Approval of `label_spec_v1.json`:** PENDING (Section 5 above).
7. **[ ] Formal PI Limitation Acknowledgement:** PENDING (Section 6 above).
8. **[ ] Execution of Phase 2A Formal Closure Addendum:** To be executed only after Items 5, 6, and 7 are signed.

### 7.3 Formal PI Gate Authorization Block

```
I hereby confirm that upon execution of Sections 2 through 6 above, the Phase 2A/2C Scientific Gate is authorized to transition from OPEN to CLOSED. I authorize the engineering team to generate the canonical Phase 2C supervised dataset ('run_002') in strict accordance with label_spec_v1.json.

Gate Closure Authorization:   [ ] AUTHORIZED    [ ] NOT AUTHORIZED
Principal Investigator Name:  ___________________________
PI Signature:                 ___________________________
Date:                         ___________________________
```
