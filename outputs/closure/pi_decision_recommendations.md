# PRINCIPAL INVESTIGATOR (PI) DECISION RECOMMENDATIONS & SCIENTIFIC TRADE-OFF ANALYSIS

**Document ID:** `outputs/closure/pi_decision_recommendations.md`  
**Execution Stage:** Phase 6B.8 — Implementation and Closure Readiness  
**Project:** *A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Engineering Role:** Senior Biomedical Signal-Processing Researcher, Test Engineer & Research Governance Auditor  
**Governance Status:** **`PENDING FORMAL PI REVIEW & EXECUTION`**  
**Scientific Gate Status:** Strictly **`OPEN`** ([`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md))  
**Supervised Label Generation & Real Training:** Strictly **`BLOCKED`**  

---

## Executive Summary & Governance Preamble

This document provides the formal scientific trade-off analysis, empirical evidence base, and technical recommendations for the six governance decisions required to transition the Phase 2A/2C Scientific Gate from **`OPEN`** to **`CLOSED`**.

### Strict Governance Boundary:
> [!IMPORTANT]
> **Engineering recommendations are NOT approvals.** Under institutional research integrity standards, no machine learning engineer, auditor, or automated script may sign these decisions or alter gate authorization flags. All six sign-off fields must be executed by an authorized Principal Investigator (PI) using the formal intake protocol:
> [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md).

Until formal execution is complete, the repository enforces a strict, fail-closed barrier:
1. `outputs/supervised_dataset/run_002` strictly does NOT exist.
2. `outputs/phase5/run_real_001` strictly does NOT exist.
3. Preflight check ([`src/closure/phase2c_preflight.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py)) returns exit code 1 (`NO-GO`), with 10 passing structural checks and 6 failing governance sign-off checks.

---

## Summary Matrix of Required PI Decisions

| Decision ID | Target Artifact / Section | Core Subject | Engineering Recommendation | Empirical Impact on Dataset Yield |
| :--- | :--- | :--- | :--- | :--- |
| **D13** | `pi_signoff_intake_protocol.md:Sec 2` | Window-Level Max RR Gap ($\ge 3.0\text{ s}$) | **Option A (Retain $3.0\text{ s}$)** | $0/1,104$ windows rejected ($100.00\%$ yield retained) |
| **D14** | `pi_signoff_intake_protocol.md:Sec 3` | Min Valid Beats Per Recording ($\ge 20$) | **Option A (Retain $\ge 20\text{ beats}$)** | $0/48$ recordings rejected ($100.00\%$ yield retained) |
| **D15** | `pi_signoff_intake_protocol.md:Sec 4` | Pipeline Runner Output Directory Guard | **Option A (Approve programmatic guard)** | Prevents baseline corruption of `outputs/phase2a` |
| **SPEC-v1** | `label_spec_v1.json` & Protocol Sec 5 | Ground-Truth Label Spec (`ae5c6780...`) | **APPROVE Specification v1.0.0** | Establishes frozen, canonical ground-truth labels |
| **HW-SYNC** | `pi_signoff_intake_protocol.md:Sec 6` | Hardware Timing Limitation Acknowledgement | **CONFIRM Limitation Acknowledged** | Enforces `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` |
| **GATE-AUTH**| `pi_signoff_intake_protocol.md:Sec 7` | Phase 2A Closure & Phase 2C Authorization | **AUTHORIZE Gate Transition** | Authorizes controlled generation of `run_002` |

---

## 1. Decision D13: Window-Level Maximum RR Gap Rule

### 1.1 Context & Problem Formulation
In [`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98) and [`outputs/closure/spec/label_spec_v1.json:56`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json#L56), a window-level Signal Quality Index (SQI) check rejects candidate 10-second windows if any RR interval falling within the window exceeds $3.0\text{ s}$.

The decision facing the PI is whether to retain this quality gate, drop it in favor of cumulative duration coverage alone, or revise the threshold.

### 1.2 Empirical Evidence Base
A comprehensive diagnostic scan was executed across all 48 VITALSENSE recordings and all 1,104 candidate windows ($24\text{ subjects} \times 2\text{ conditions} \times 23\text{ windows}$), documented in [`outputs/closure/window_coverage_gate_diagnostic.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_coverage_gate_diagnostic.csv):
- **Maximum Observed RR Gap in Cohort:** **$1.2920\text{ s}$** (observed in subject `VS02_Apnea`).
- **Distribution of Window Maximum RR Intervals:**
  - 50th percentile (median): $0.852\text{ s}$ ($\sim 70.4\text{ BPM}$)
  - 95th percentile: $1.110\text{ s}$ ($\sim 54.1\text{ BPM}$)
  - 99th percentile: $1.214\text{ s}$ ($\sim 49.4\text{ BPM}$)
  - Maximum observed: $1.292\text{ s}$ ($\sim 46.4\text{ BPM}$)
- **Rejection Statistics at $3.0\text{ s}$:** Exactly **0 out of 1,104 windows** ($0.00\%$) exceed $3.0\text{ s}$.
- **Dataset Yield:** Retention is **$100.00\%$** ($1,104 / 1,104$ candidate windows accepted).

### 1.3 Available Options & Trade-Off Analysis

```
+----------------------------------------------------------------------------------------------------+
| OPTION A (RECOMMENDED): RETAIN window-level maximum RR gap threshold at 3.0 s                      |
| - Mathematical Consistency: Perfectly harmonized with recording-level SQI (max RR gap < 3.0 s).    |
| - Safety: Guards against unflagged sinus arrest, sensor lead detachment, or ectopic pauses.        |
| - Empirical Yield Cost: 0% data loss (all 1,104 windows retained).                                 |
+----------------------------------------------------------------------------------------------------+
| OPTION B: DROP window-level max-gap rule (Rely exclusively on duration coverage >= 8.0 s)         |
| - Vulnerability: Could permit windows with severe localized pauses (e.g. 2.0 s pause + rapid beats) |
|   as long as valid beat durations sum to >= 8.0 s.                                                 |
| - Scientific Benefit: None in VITALSENSE, because no windows are rejected under Option A.          |
+----------------------------------------------------------------------------------------------------+
| OPTION C: REVISE threshold to an alternative limit (e.g. 4.0 s)                                   |
| - Overly Permissive: In a 10.0 s window, a 4.0 s gap represents 40% of the window duration.        |
| - Scientific Benefit: Redundant, as cohort maximum is 1.292 s.                                     |
+----------------------------------------------------------------------------------------------------+
```

### 1.4 Engineering Recommendation
**Option A (Retain $3.0\text{ s}$ threshold).** It provides rigorous defense-in-depth against cardiac pause artifacts with zero empirical data loss in the target cohort.

### 1.5 Required Action by PI in `pi_signoff_intake_protocol.md` (Lines 38–49)
```markdown
[X] OPTION A: RETAIN window-level maximum RR gap threshold at 3.0 s (Ensures consistency with recording-level SQI).
[ ] OPTION B: DROP window-level max-gap rule (Rely exclusively on cumulative valid RR duration coverage >= 80%).
[ ] OPTION C: REVISE window-level max-gap threshold to an alternative physiological limit (e.g. 4.0 s).

Selected Option (A, B, or C): Option A
Principal Investigator Name:  <Full Name of Authorized PI>
PI Academic / Clinical Title: <Academic Title / Department>
PI Institution:               <University / Research Hospital>
PI Signature:                 <Digital or Typed Signature>
Date of Execution:            <YYYY-MM-DD>
```

---

## 2. Decision D14: Minimum Valid Beats Per Recording

### 2.1 Context & Problem Formulation
In [`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283), recording-level Signal Quality Indexing requires that a 120-second reference ECG recording contain at least 20 valid RR beats.

The decision facing the PI is whether to retain this invariant, drop it, or adjust the beat threshold.

### 2.2 Empirical Evidence Base
Analysis of all 48 VITALSENSE ECG recordings ($60,000\text{ samples}$ @ $500\text{ Hz} = 120.0\text{ s}$):
- **Beat Count Distribution Across 48 Recordings:**
  - Minimum: **99 beats** (in `VS10_Resting`)
  - Maximum: **157 beats** (in `VS14_Apnea`)
  - Mean $\pm$ SD: **$129.2 \pm 14.8\text{ beats}$**
  - Median: **130.5 beats**
- **Theoretical Lower Physiological Bound:**
  - Minimum physiological heart rate limit is $35\text{ BPM}$.
  - Minimum valid ECG duration coverage is $85\%$ ($102.0\text{ s}$).
  - Theoretical minimum beats in $102\text{ s}$ at $35\text{ BPM}$ is $(102 / 60) \times 35 \approx 59.5\text{ beats}$.
- **Empirical Rejection Statistics:**
  - Threshold $\ge 20$ beats rejects **0 of 48 recordings** ($0.0\%$).
  - Threshold $\ge 30$ beats rejects **0 of 48 recordings** ($0.0\%$).
  - Threshold $\ge 50$ beats rejects **0 of 48 recordings** ($0.0\%$).

### 2.3 Available Options & Trade-Off Analysis

```
+----------------------------------------------------------------------------------------------------+
| OPTION A (RECOMMENDED): RETAIN minimum valid beat threshold of >= 20 beats per 120 s recording     |
| - Scientific Basis: Acts as a non-binding sanity floor protecting against truncated, silent, or    |
|   catastrophically corrupted MAT files.                                                            |
| - Empirical Yield Cost: 0% data loss (all 48 recordings exceed threshold with >= 99 beats).        |
| - Backward Compatibility: Fully aligned with existing regression tests and Phase 2A audit.         |
+----------------------------------------------------------------------------------------------------+
| OPTION B: DROP beat count threshold (Rely strictly on duration coverage > 85% of recording)       |
| - Vulnerability: Removes an explicit beat floor; relies purely on duration coverage calculations,  |
|   which could theoretically pass an anomalous single-beat file if duration logic failed.          |
+----------------------------------------------------------------------------------------------------+
| OPTION C: REVISE beat count threshold to an alternative count (e.g. 30 or 50 beats)               |
| - Physiological Realism: 50 beats is closer to the theoretical 35 BPM floor (59.5 beats).          |
| - Practical Consequence: In VITALSENSE, because min is 99 beats, 30 or 50 produces identical yield |
|   (48/48 accepted), but requires updating historical test baselines.                               |
+----------------------------------------------------------------------------------------------------+
```

### 2.4 Engineering Recommendation
**Option A (Retain $\ge 20$ beats threshold).** It guarantees defense-in-depth against data corruption without altering verified baselines or sacrificing any recording yield.

### 2.5 Required Action by PI in `pi_signoff_intake_protocol.md` (Lines 67–78)
```markdown
[X] OPTION A: RETAIN minimum valid beat threshold of >= 20 beats per 120 s recording.
[ ] OPTION B: DROP beat count threshold (Rely strictly on duration coverage > 85% of recording).
[ ] OPTION C: REVISE beat count threshold to an alternative count (e.g. 30 beats).

Selected Option (A, B, or C): Option A
Principal Investigator Name:  <Full Name of Authorized PI>
PI Academic / Clinical Title: <Academic Title / Department>
PI Institution:               <University / Research Hospital>
PI Signature:                 <Digital or Typed Signature>
Date of Execution:            <YYYY-MM-DD>
```

---

## 3. Decision D15: Pipeline Runner Default `output_dir` Safeguard

### 3.1 Context & Problem Formulation
In Phase 2A synchronization validation ([`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py)), legacy invocations could inadvertently write output files directly into the audited baseline directory (`outputs/phase2a`), risking silent corruption of audited baselines.

The decision facing the PI is whether to approve a programmatic code safeguard requiring explicit output directory specification and blocking unauthorized baseline overwriting, or revert to procedural documentation only.

### 3.2 Implementation & Verification Evidence
A programmatic safeguard was implemented in `src/sync_validation/runner.py`:
1. If `output_dir` is omitted or set to `None`, the runner raises `ValueError: output_dir must be explicitly specified`.
2. If `output_dir` resolves to `outputs/phase2a` and `allow_phase2a_overwrite` is not explicitly set to `True`, the runner raises `PermissionError: Overwriting outputs/phase2a is prohibited to protect audited baseline files`.
3. Automated unit tests in [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) test and pass all boundary conditions (3/3 passed).
4. Bit-for-bit SHA-256 hashes of audited baseline files remain confirmed identical:
   - `outputs/phase2a/step2b_consistency_audit.md`: `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f`
   - `outputs/phase2a/sync_validation_results.csv`: `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10`

### 3.3 Available Options & Trade-Off Analysis

```
+----------------------------------------------------------------------------------------------------+
| OPTION A (RECOMMENDED): APPROVE programmatic code safeguard in src/sync_validation/runner.py       |
| - Research Integrity: Mathematically and programmatically guarantees that audited historical      |
|   validation results cannot be destroyed by accidental CLI runs or automated scripts.             |
| - Safety: Enforces explicit intent when generating new validation runs.                            |
+----------------------------------------------------------------------------------------------------+
| OPTION B: REJECT code safeguard and revert to procedural documentation only                        |
| - Vulnerability: Leaves audited baseline data vulnerable to silent overwrite during routine testing|
|   or retraining cycles. High risk of non-reproducibility.                                          |
+----------------------------------------------------------------------------------------------------+
```

### 3.4 Engineering Recommendation
**Option A (Approve programmatic safeguard).** Programmatic invariants are standard best practice in research MLOps to prevent baseline contamination.

### 3.5 Required Action by PI in `pi_signoff_intake_protocol.md` (Lines 94–104)
```markdown
[X] OPTION A: APPROVE programmatic code safeguard in src/sync_validation/runner.py (Requires explicit output_dir; blocks unauthorized overwrite of outputs/phase2a/).
[ ] OPTION B: REJECT code safeguard and revert to procedural documentation only.

Selected Option (A or B):     Option A
Principal Investigator Name:  <Full Name of Authorized PI>
PI Academic / Clinical Title: <Academic Title / Department>
PI Institution:               <University / Research Hospital>
PI Signature:                 <Digital or Typed Signature>
Date of Execution:            <YYYY-MM-DD>
```

---

## 4. Formal Approval of Ground-Truth Label Specification (`label_spec_v1.json`)

### 4.1 Context & Scientific Rationale
Before generating supervised training targets (`outputs/supervised_dataset/run_002`) for real radar signals, the ground-truth calculation methodology must be cryptographically frozen and approved to prevent data leakage or post-hoc label tuning.

[`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) defines the project's frozen ground-truth specification:
- **Canonical Content SHA-256 Digest:** `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`
- **Raw Unsigned File SHA-256 Digest:** `a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8`

### 4.2 Core Specification Invariants
1. **Windowing Grid:** Window duration $10.0\text{ s}$, hop $5.0\text{ s}$. Continuous temporal formula $t_{\text{start}} = \text{round}(k \times 5.0, 3)$ yielding exactly 23 windows per 120-second recording ($1,104$ candidate windows cohort-wide).
2. **Reference Signal:** Continuous ECG Lead II (`ecg_lead2`). Commercial monitor numeric `HR` array is strictly `FORBIDDEN` due to $+6.21\text{ s}$ systematic lag.
3. **Preprocessing:** Delimiter NaN interpolation (`clean_ecg_nans`) with `only_isolated: true, fill_boundary: true`.
4. **QRS Detection:** Pan-Tompkins with absolute peak refinement $\text{argmax}(|\text{filtered}|)$, resolving inverted lead morphology (e.g. `VS19`).
5. **Heart Rate Label Formulation:** Harmonic mean:
   $$\text{HR}_{\text{window}} = \frac{60.0}{\frac{1}{M}\sum_{i=1}^{M} \text{RR}_i}$$
   computed over all valid RR intervals whose midpoints fall in $[t_{\text{start}}, t_{\text{end}})$.
6. **Window Quality Gating (SQI):** Strict all-or-nothing physiological bounds ($35.0\text{--}185.0\text{ BPM}$), covered duration $> 8.0\text{ s}$, and maximum RR gap $< 3.0\text{ s}$.

### 4.3 Cryptographic Hash Invariance Under Signing
> [!NOTE]
> The canonical hash algorithm implemented in [`src/closure/pi_signoff_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/pi_signoff_validator.py#L375) explicitly excludes `"approved_by"` and `"spec_sha256"`:
> ```python
> d_canonical = {k: v for k, v in spec_data.items() if k not in ("approved_by", "spec_sha256")}
> canonical_str = json.dumps(d_canonical, indent=2, sort_keys=True)
> canonical_sha256 = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
> ```
> This deliberate architectural design ensures that when the PI signs their name into `"approved_by"` in `label_spec_v1.json`, the canonical digest remains bit-for-bit identical (`ae5c6780...`), preserving automated pipeline verification without hash mismatch.

### 4.4 Engineering Recommendation
**Approve `label_spec_v1.json` as the frozen, canonical ground-truth label specification.**

### 4.5 Required Action by PI
1. In `pi_signoff_intake_protocol.md` (Lines 123–133):
```markdown
[X] APPROVED: I hereby approve outputs/closure/spec/label_spec_v1.json (SHA-256: a0f7a85e...) as the frozen, canonical reference label specification for the project.
[ ] REJECTED: Revisions required prior to approval.

Approval Determination:       APPROVED
Approved By (PI Full Name):   <Full Name of Authorized PI>
PI Academic / Clinical Title: <Academic Title / Department>
PI Institution:               <University / Research Hospital>
PI Signature:                 <Digital or Typed Signature>
Date of Approval:             <YYYY-MM-DD>
```
2. In `outputs/closure/spec/label_spec_v1.json` (Line 4):
```json
  "approved_by": "<Full Name of Authorized PI>",
```

---

## 5. Mandatory Hardware Timing Limitation Acknowledgement

### 5.1 Context & Physical Acquisition Limitation
A rigorous, byte-level inspection of all 96 MAT files in `../data/VITALSENSE_120_DATASET` confirmed that the experimental recording apparatus did not include:
- Pulse-per-second (PPS) synchronization lines.
- External TTL hardware trigger timestamps.
- Common master digitizer clock across the 120-GHz radar and the Mindray ECG monitor.

Consequently:
- Nominal alignment at $T_0 = 0.0\text{ s}$ is an **operational computational convention**, not a verified hardware synchronization.
- Physiological Pulse Transit Time (PTT, $\sim 100\text{--}250\text{ ms}$), vascular pulse wave propagation velocity, and human operator startup latency cannot be resolved post-hoc.

### 5.2 Scientific Consequences & Governance Policy
To uphold scientific transparency and avoid fraudulent claims of microsecond-level hardware synchronization, all downstream research artifacts must carry the standardized disclaimer:
**`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**.

This disclaimer is already embedded into `label_spec_v1.json`, the web dashboard UI, and preflight check validators.

### 5.3 Engineering Recommendation
**Formally acknowledge and mandate `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` across all future project publications, benchmark tables, and model cards.**

### 5.4 Required Action by PI in `pi_signoff_intake_protocol.md` (Lines 146–152)
```markdown
I formally acknowledge and confirm that hardware clock synchronization between the 120-GHz FMCW radar and the reference ECG digitizer is unverified. I mandate that all future publications, project documentation, model cards, and benchmark tables must explicitly cite the standardized limitation: 'UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0'.

Acknowledged By (PI Name):    <Full Name of Authorized PI>
PI Signature:                 <Digital or Typed Signature>
Date of Acknowledgement:      <YYYY-MM-DD>
```

---

## 6. Phase 2A Gate Closure Authorization & Transition to Phase 2C

### 6.1 Context & Preflight Status
The Phase 2A consistency audit identified 28 issues:
- 12 verified and resolved in code and unit tests.
- 9 documented and accepted physical acquisition limitations.
- 7 pending formal PI decisions (D13, D14, D15, Label Spec, HW Timing, Gate Closure, Legacy Addendum).

Once Items 1 through 5 are formally signed by the PI, the scientific prerequisites for Phase 2A gate closure are fully satisfied.

### 6.2 Authorized Next Step: Phase 2C Dataset Generation
Upon PI authorization:
1. Scientific Gate status formally transitions from **`OPEN`** to **`CLOSED`**.
2. Preflight verification ([`src/closure/phase2c_preflight.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py)) will evaluate to **`GO`** (16 PASS, 0 FAIL).
3. The engineering team is authorized to execute:
   ```powershell
   python kan_radar_HR/src/phase3/supervised_dataset_generator.py `
     --spec kan_radar_HR/outputs/closure/spec/label_spec_v1.json `
     --output_dir kan_radar_HR/outputs/supervised_dataset/run_002
   ```
   generating exactly 1,104 supervised windows across 48 recordings without human intervention.

### 6.3 Required Action by PI in `pi_signoff_intake_protocol.md` (Lines 174–181)
```markdown
I hereby confirm that upon execution of Sections 2 through 6 above, the Phase 2A/2C Scientific Gate is authorized to transition from OPEN to CLOSED. I authorize the engineering team to generate the canonical Phase 2C supervised dataset ('run_002') in strict accordance with label_spec_v1.json.

Gate Closure Authorization:   [X] AUTHORIZED    [ ] NOT AUTHORIZED
Principal Investigator Name:  <Full Name of Authorized PI>
PI Signature:                 <Digital or Typed Signature>
Date:                         <YYYY-MM-DD>
```

---

## Governance Integrity Certification

This recommendation document has been prepared under strict research-governance compliance. All code guards remain fail-closed, no real-data labels have been generated, and all decision sign-off blocks remain unexecuted pending the Principal Investigator's personal review and signature.
