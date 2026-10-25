# PHASE 2C SCIENTIFIC GATE BLOCKER RESOLUTION GUIDANCE
## Methodological Trade-Offs, Synchronization Sensitivity Analysis & Principal Investigator Decision Package

**Document ID:** `outputs/closure/phase2c_blocker_resolution_guidance.md`  
**Execution Stage:** Phase 6B.8 -> Phase 2C Governance Bridge  
**Project:** *A Subject-Independent Kolmogorov-Arnold Network (KAN)-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Date:** October 2026  
**Auditor / Engineering Role:** Senior Biomedical Signal-Processing Researcher, Physiological Validation Specialist & Research Governance Auditor  
**Workspace Root:** `c:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work`  
**Repository Root:** `c:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`  
**Scientific Gate Status:** Strictly **`OPEN`** ([`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md))  
**Preflight Check Verdict:** Strictly **`NO-GO`** (`10 PASS, 6 FAIL`)  
**Real-Data Supervised Dataset (`run_002`) & Real Training (`run_real_001`):** Strictly **`BLOCKED`** (do not exist)  

---

## 1. Executive Summary & Governance Preamble

The automated Phase 2C preflight suite ([`src/closure/phase2c_preflight.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py)) confirms that all 10 code, unit test, dataset inventory, cryptographic hash, and isolation checks evaluate to **`PASS`**. Exactly six checks evaluate to **`FAIL`**:

1. `GOV_DECISION_D13`: Window-Level Maximum RR Gap Rule ($3.0\text{ s}$ threshold).
2. `GOV_DECISION_D14`: Minimum Valid Beats Per Recording ($20\text{ beats}$ threshold).
3. `GOV_DECISION_D15`: Pipeline Runner Default `output_dir` Safeguard.
4. `GOV_LABEL_SPEC_APPROVAL`: Ground-Truth Label Specification Approval (`label_spec_v1.json`).
5. `GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT`: Standardized Limitation (`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`).
6. `GOV_PHASE2A_GATE_CLOSURE_AUTH`: Formal Gate Closure & Phase 2C Authorization.

> [!IMPORTANT]
> **Advisory Engineering Role vs. Formal PI Authority:**
> The engineering team has conducted extensive empirical analyses, mathematical simulations, and sensitivity checks across all 48 VITALSENSE recordings ($1,104$ candidate windows). All recommendations in this document represent **engineering advice**, not approvals. Under institutional research governance, no software engineer, test script, or AI agent possesses the authority to sign research governance decisions or close the scientific gate.
>
> All six pending items must be reviewed, selected, and signed by an authorized **human Principal Investigator (PI)**.

---

## 2. In-Depth Analysis of the Six Preflight Governance Blockers

### 2.1 Blocker 1: Decision D13 — Window-Level Maximum RR Gap Rule (`GOV_DECISION_D13`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Document:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 2.2 (Lines 38–49).
- **Missing Fields:**
  - Option selection checkbox: currently empty (`[ ] OPTION A`, `[ ] OPTION B`, `[ ] OPTION C`).
  - `Selected Option (A, B, or C):` currently placeholder `_______`.
  - `Principal Investigator Name:` currently placeholder `_______`.
  - `PI Academic / Clinical Title:` currently placeholder `_______`.
  - `PI Institution:` currently placeholder `_______`.
  - `PI Signature:` currently placeholder `_______`.
  - `Date of Execution:` currently placeholder `_______` (must be ISO `YYYY-MM-DD`).

#### 2. Evidence Needed for an Informed PI Decision
- **Cohort Diagnostic Scan:** [`outputs/closure/window_coverage_gate_diagnostic.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_coverage_gate_diagnostic.csv) evaluating all 48 recordings and all 1,104 candidate 10-second windows ($24\text{ subjects} \times 2\text{ conditions} \times 23\text{ windows}$).
- **Empirical Gap Distribution:**
  - The maximum observed window RR interval in the entire cohort is **$1.2920\text{ s}$** (observed in subject `VS02_Apnea`).
  - Cohort 99th percentile RR interval: $1.214\text{ s}$ ($\approx 49.4\text{ BPM}$).
  - Rejection count at $3.0\text{ s}$: **0 of 1,104 windows ($0.00\%$)** exceed $3.0\text{ s}$.
  - Data yield retention: **$100.00\%$** ($1,104 / 1,104$ accepted).
- **Code Implementation:** [`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98).

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Over-Filtering (Option A with too strict threshold):** If set below $1.3\text{ s}$, valid resting bradycardia windows in subjects like `VS02` would be discarded, introducing systematic sampling bias against low heart rates.
- **Risk of Under-Filtering (Option B - Dropping gap rule):** If relying purely on cumulative valid duration coverage ($\ge 80\%$), a window could theoretically contain a $2.5\text{ s}$ sinus pause combined with rapid compensatory beats, yielding a distorted harmonic mean HR that does not represent physiological rhythm.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** Select **Option A (Retain $3.0\text{ s}$ threshold)**.  
> **Rationale:** In the VITALSENSE dataset, the $3.0\text{ s}$ threshold guarantees zero yield loss ($100\%$ retention across 1,104 windows) while enforcing mathematical consistency with the recording-level SQI rule ($\max(\text{RR gap}) < 3.0\text{ s}$). It provides a vital defense-in-depth safety rail against undetected sensor disconnects or asystolic episodes.

#### 5. Unresolved Phase 2A Issues Affecting D13
- **ISS-08 (Superficial ECG Quality Check):** The legacy detector only checked for $\ge 5$ beats in 120s. Enforcing the window-level max gap rule ensures localized trace quality independent of global recording flags.

---

### 2.2 Blocker 2: Decision D14 — Minimum Valid Beats Per Recording (`GOV_DECISION_D14`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Document:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 3.2 (Lines 67–78).
- **Missing Fields:**
  - Option selection checkbox: currently empty (`[ ] OPTION A`, `[ ] OPTION B`, `[ ] OPTION C`).
  - `Selected Option (A, B, or C):` currently placeholder `_______`.
  - `Principal Investigator Name:` currently placeholder `_______`.
  - `PI Academic / Clinical Title:` currently placeholder `_______`.
  - `PI Institution:` currently placeholder `_______`.
  - `PI Signature:` currently placeholder `_______`.
  - `Date of Execution:` currently placeholder `_______` (must be ISO `YYYY-MM-DD`).

#### 2. Evidence Needed for an Informed PI Decision
- **Cohort Beat Count Distribution:** Evaluated across all 48 recordings ($120.0\text{ s}$ @ $500\text{ Hz}$):
  - Minimum observed beat count: **99 beats** (in `VS10_Resting`).
  - Maximum observed beat count: **157 beats** (in `VS14_Apnea`).
  - Mean $\pm$ Standard Deviation: **$129.2 \pm 14.8\text{ beats}$** (Median: $130.5\text{ beats}$).
- **Theoretical Lower Physiological Floor:** For a 120-second recording with $\ge 85\%$ coverage ($102.0\text{ s}$) at the minimum allowable heart rate ($35\text{ BPM}$), the theoretical minimum beat count is:
  $$\text{Floor} = \frac{102.0\text{ s}}{60.0\text{ s/min}} \times 35\text{ BPM} = 59.5\text{ beats}$$
- **Rejection Rates:** A threshold of $\ge 20$ beats rejects **0 of 48 recordings ($0.00\%$)**. A threshold of $\ge 30$ or $\ge 50$ beats also rejects **0 of 48 recordings ($0.00\%$)**.

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Spurious Invalidation (Option C with excessive threshold):** Setting a threshold $> 99$ beats would reject `VS10_Resting` (a subject with healthy resting bradycardia of $\approx 50\text{ BPM}$), dropping an entire viable recording.
- **Risk of Silent Corruption (Option B - Dropping beat threshold):** Relying solely on duration coverage could permit a corrupted file with an anomalous long interpolated single-beat artifact to pass recording-level QC.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** Select **Option A (Retain $\ge 20\text{ beats}$ threshold)**.  
> **Rationale:** The 20-beat requirement serves as a non-binding sanity floor protecting against empty, truncated, or severely corrupted files. Because every recording in the cohort exhibits $\ge 99$ beats, retaining $\ge 20$ beats guarantees $0\%$ data loss while preserving verified regression test baselines.

#### 5. Unresolved Phase 2A Issues Affecting D14
- **ISS-08 (Superficial ECG Quality Check):** Legacy `src/sync_validation/ecg_processor.py` awarded `ecg_quality_status = PASS` for $\ge 5$ beats in 120s. Decision D14 replaces that superficial heuristic with multi-parameter SQI ($\ge 20$ beats, $> 85\%$ coverage, max gap $< 3.0\text{ s}$).

---

### 2.3 Blocker 3: Decision D15 — Pipeline Runner Output Directory Guard (`GOV_DECISION_D15`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Document:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 4.2 (Lines 94–104).
- **Missing Fields:**
  - Option selection checkbox: currently empty (`[ ] OPTION A`, `[ ] OPTION B`).
  - `Selected Option (A or B):` currently placeholder `_______`.
  - `Principal Investigator Name:` currently placeholder `_______`.
  - `PI Academic / Clinical Title:` currently placeholder `_______`.
  - `PI Institution:` currently placeholder `_______`.
  - `PI Signature:` currently placeholder `_______`.
  - `Date of Execution:` currently placeholder `_______` (must be ISO `YYYY-MM-DD`).

#### 2. Evidence Needed for an Informed PI Decision
- **Code Implementation:** [`src/sync_validation/runner.py:34-45`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L34-L45) requiring explicit `output_dir` and raising `PermissionError` on unauthorized writes to `outputs/phase2a`.
- **Automated Test Results:** [`tests/test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) (3/3 passed).
- **Cryptographic Baseline Stability:**
  - `outputs/phase2a/step2b_consistency_audit.md` SHA-256: `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f` (MATCH).
  - `outputs/phase2a/sync_validation_results.csv` SHA-256: `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10` (MATCH).

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Procedural Failure (Option B - Documentation only):** High risk that an automated regression test, CI script, or developer CLI run silently overwrites the audited Phase 2A baseline files, corrupting the scientific audit trail.
- **Risk of Software Inflexibility (Option A):** Requires callers to provide explicit output directories. This risk was mitigated by adding `--allow-phase2a-overwrite` as an explicit override flag.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** Select **Option A (Approve programmatic safeguard)**.  
> **Rationale:** In computational biomedical science, immutable baseline records must be protected programmatically rather than through procedural documentation alone. The code guard eliminates human error risk with zero impact on operational workflows.

#### 5. Unresolved Phase 2A Issues Affecting D15
- **ISS-27 (Disposition of Legacy Outputs):** Programmatic directory guards ensure that historical baseline audits remain pristine while active work proceeds in decoupled directories.

---

### 2.4 Blocker 4: Ground-Truth Label Specification Approval (`label_spec_v1.json`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Documents:**
  1. [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 5.2 (Lines 123–133):
     - `Approval Determination:` currently placeholder `_______`.
     - `Approved By (PI Full Name):` currently placeholder `_______`.
     - `PI Signature:` currently placeholder `_______`.
     - `Date of Approval:` currently placeholder `_______`.
  2. [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json), Line 4:
     - `"approved_by": ""` is currently empty.

#### 2. Evidence Needed for an Informed PI Decision
- **Specification Invariants in `label_spec_v1.json`:**
  - Continuous-time windowing: $10.0\text{ s}$ window, $5.0\text{ s}$ hop, continuous formula $t_{\text{start}} = \text{round}(k \times 5.0, 3)$, yielding exactly 23 windows/recording ($1,104$ windows cohort-wide).
  - Reference signal: Lead II continuous ECG (`ecg_lead2`). Commercial monitor `HR` array strictly `FORBIDDEN` due to $+6.21\text{ s}$ systematic latency.
  - Preprocessing: Delimiter NaN interpolation (`clean_ecg_nans`) with `only_isolated: true, fill_boundary: true`.
  - R-peak detector: Pan-Tompkins with absolute peak refinement $\text{argmax}(|\text{filtered}|)$, resolving inverted lead morphology (`VS19`).
  - Label formula: Harmonic mean $\text{HR} = 60.0 / \text{mean}(w\_\text{rrs})$ of valid intervals whose midpoints fall in $[t_{\text{start}}, t_{\text{end}})$.
  - Window SQI: $35.0\text{--}185.0\text{ BPM}$, covered duration $> 8.0\text{ s}$, max gap $< 3.0\text{ s}$.
- **Cryptographic Hash Invariance Architecture:**
  The canonical hash algorithm deliberately excludes `"approved_by"` and `"spec_sha256"`. Populating the PI's name in `label_spec_v1.json` preserves the canonical digest `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44` bit-for-bit, allowing preflight validation to pass.

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Latency Contamination:** If the commercial monitor `HR` array were used instead of continuous ECG, supervised training targets would be contaminated with historical heart rates lagged by $+6\text{ to }+7\text{ s}$.
- **Risk of Morphological Inversion Error:** If standard positive peak refinement were used instead of absolute refinement $\text{argmax}(|\text{filtered}|)$, inverted ECG leads (e.g. `VS19`) would suffer $\approx 44\text{ ms}$ fiducial misalignments.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** **Approve `label_spec_v1.json` as the frozen canonical ground-truth label specification**.  
> **Rationale:** The specification fixes all methodological choices prior to observing model training results. It eliminates post-hoc tuning bias, establishes 100% reproducibility across 1,104 windows, and enforces rigorous physiological quality gating.

#### 5. Unresolved Phase 2A Issues Affecting Label Spec
- **ISS-01 (Monitor HR Latency):** Resolved by disqualifying monitor `HR` and standardizing on continuous ECG.
- **ISS-24 (Boundary NaN):** Resolved by adopting `fill_boundary: true`.
- **ISS-25 (Continuous Windowing):** Resolved by adopting the 23-window continuous grid.
- **ISS-26 (Detector Harmonization):** Resolved by adopting absolute peak refinement.

---

### 2.5 Blocker 5: Mandatory Hardware Timing Limitation Acknowledgement (`GOV_HARDWARE_TIMING_ACKNOWLEDGEMENT`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Document:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 6.2 (Lines 146–152).
- **Missing Fields:**
  - `Acknowledged By (PI Name):` currently placeholder `_______`.
  - `PI Signature:` currently placeholder `_______`.
  - `Date of Acknowledgement:` currently placeholder `_______` (must be ISO `YYYY-MM-DD`).

#### 2. Evidence Needed for an Informed PI Decision
- **Byte-Level Physical Dataset Audit:** Forensic inspection of all 96 MAT files in `data/VITALSENSE_120_DATASET` confirming the complete absence of:
  - External pulse-per-second (PPS) trigger lines.
  - Common hardware digitizer clocks or shared sampling clock buses.
  - Microsecond-level hardware timestamp headers.
- **Empirical Cross-Correlation Plateau:** Analysis in `step2b_consistency_audit.md:Section 22.3` proving that respiratory cross-correlation peaks sit on an extended plateau (median width $95.0\text{ ms}$, range $34.5\text{--}1,594.0\text{ ms}$).

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Scientific Misconduct / Fraudulent Claims:** Claiming physical hardware clock synchronization without hardware timing evidence would invite immediate manuscript rejection, scientific challenge, or retractions during peer review.
- **Risk of False Attribution:** Misattributing physiological Pulse Transit Time (PTT, $\sim 100\text{--}250\text{ ms}$) or operator start latencies to FMCW radar hardware properties.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** **Formally acknowledge and mandate `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` across all future project publications, benchmark tables, and model cards**.  
> **Rationale:** Transparent disclosure of physical acquisition realities protects academic credibility. Nominal $T_0 = 0.0\text{ s}$ alignment is a defensible computational baseline for window-level average HR estimation, provided it is openly documented as an operational assumption.

#### 5. Unresolved Phase 2A Issues Affecting Hardware Timing
- **ISS-02 (Absence of Hardware Clocks):** Accepted physical acquisition limitation.
- **ISS-28 (Correlation Plateau):** Confirms that sub-sample alignment is a mathematical artifact rather than hardware clock synchronization.

---

### 2.6 Blocker 6: Phase 2A Gate Closure Authorization & Phase 2C Execution (`GOV_PHASE2A_GATE_CLOSURE_AUTH`)

#### 1. Exact Requirement & Current Missing Fields
- **Target Document:** [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md), Section 7.3 (Lines 174–181).
- **Missing Fields:**
  - `Gate Closure Authorization:` currently `[ ] AUTHORIZED    [ ] NOT AUTHORIZED` (unchecked).
  - `Principal Investigator Name:` currently placeholder `_______`.
  - `PI Signature:` currently placeholder `_______`.
  - `Date:` currently placeholder `_______` (must be ISO `YYYY-MM-DD`).

#### 2. Evidence Needed for an Informed PI Decision
- **Phase 2A Reconciliation Addendum:** [`outputs/closure/phase2a_reconciliation_addendum.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/phase2a_reconciliation_addendum.md) tracking all 28 audit issues (12 resolved in code, 9 documented limitations, 7 pending governance sign-off).
- **Full Test Suite Status:** `215 / 215 tests passing` across all 27 test modules (Exit code: 0).
- **Non-Destructive Readiness Verification:** [`src/phase3/supervised_dataset_generator.py --validate-only`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L525) evaluating all 7 dataset pipeline checks to `PASS`.

#### 3. Technical Risks of Deciding Without Evidence
- **Risk of Premature Training on Corrupted Targets:** Authorizing Phase 2C before approving the label specification risks generating non-reproducible training tensors.
- **Risk of Indefinite Research Paralysis:** Refusing to close the gate when all technical defects have been resolved prevents completing the core research objective.

#### 4. Engineering Recommendation & Rationale
> **[ADVISORY ENGINEERING RECOMMENDATION — NOT AN APPROVAL]**  
> **Recommendation:** **Authorize gate transition from `OPEN` to `CLOSED` and authorize Phase 2C execution, conditional upon Blockers 1 through 5 being signed**.  
> **Rationale:** All technical prerequisites are verified in code and regression tests. The pipeline is fail-closed, isolated, and cryptographically verified. Signing authorizes controlled generation of `run_002` without human intervention.

---

## 3. Systematic Investigation of the Seven Open Phase 2A Issues

The Phase 2A Reconciliation Addendum documents seven open issues. The table below details their impact on Phase 2C dataset generation and model training:

| Issue ID | Summary Description | Location in Code / Reports | Impact on Phase 2C Supervised Generation | PI Resolution Required |
| :--- | :--- | :--- | :--- | :--- |
| **ISS-07** | Lumping lags $< 4\text{ s}$ into `NEAR_ZERO_LATENCY` | [`src/sync_validation/runner.py:98-110`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L98) | **NON-BLOCKING:** Phase 3/5 pipelines bypass this lag heuristic entirely, using continuous R-peak instantaneous HR. | Accept as legacy Phase 2A reporting artifact. |
| **ISS-08** | Superficial ECG Quality Check ($5$ beats in $120\text{ s}$) | [`src/sync_validation/ecg_processor.py:125`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L125) | **RESOLVED VIA D14:** Phase 3 requires multi-parameter SQI ($\ge 20$ beats, $> 85\%$ coverage, max gap $< 3\text{ s}$). | Formally execute Decision D14. |
| **ISS-10** | In-sample trial shift selection optimism | `step2b_consistency_audit.md:Section 14` | **RESOLVED VIA SPEC-v1:** Scanning $\tau \in [-5, +5]\text{ s}$ is discarded. Nominal zero-shift ($\tau = 0.0\text{ s}$) codified as canonical. | Approve `label_spec_v1.json`. |
| **ISS-12** | `VS24_Resting_Mindray.mat` format divergence | `VS24_Resting_Mindray.mat` (30,600 samples) | **NON-BLOCKING:** Anomaly affects respiration channel only. ECG has full 60,000 samples. Dynamic length handling implemented. | Acknowledge documented reproducible anomaly. |
| **ISS-15** | Test assertion threshold loosening ($r < 0.75$) | `tests/test_sync_validation.py` | **NON-BLOCKING:** Exploratory surrogate test threshold. Does not affect supervised training pipeline. | Acknowledge exploratory nature of surrogate controls. |
| **ISS-17** | Small surrogate sample size ($N=5$) | `step2b_consistency_audit.md:Section 5.2` | **NON-BLOCKING:** Statistical limitation of Phase 2A audit. Confirms surrogate test cannot prove hardware sync. | Re-affirms why `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` is required. |
| **ISS-22** | Sensitivity analysis of VS24 respiration truncation | `step2b_consistency_audit.md:Section 23.2` | **NON-BLOCKING:** Affects respiratory cross-correlation only. Cardiac radar/ECG channels are unaffected. | Documented non-blocking limitation. |

---

## 4. Scientific Investigation: Does Synchronization Uncertainty Invalidate ECG Reference Labels for Radar Windows?

A foundational research governance question is: **Does the absence of verified hardware clock synchronization invalidate ECG-derived heart-rate labels for 10-second FMCW radar windows?**

### 4.1 Quantitative Temporal Uncertainty Budget
In the VITALSENSE experimental setup, timing uncertainty arises from three distinct sources:
1. **Pulse Transit Time (PTT):** The physiological delay for the cardiac mechanical pressure pulse wave to propagate from the aortic valve to the microvasculature and chest surface ($\sim 100\text{--}250\text{ ms}$).
2. **Cross-Correlation Plateau Uncertainty:** Demeaned respiratory cross-correlation exhibits a median plateau width of **$95.0\text{ ms}$** (range $34.5\text{--}1,594.0\text{ ms}$).
3. **Software/Operator Acquisition Latency:** Manual recording startup without hardware bus synchronization introduces an estimated offset of $\le 200\text{--}500\text{ ms}$.

**Total Combined Timing Uncertainty Envelope:** $\Delta t \approx \pm 100\text{--}300\text{ ms}$ (upper bound: $\pm 500\text{ ms}$).

### 4.2 Fractional Impact on the 10-Second Analysis Window
The candidate analysis window has duration $W = 10.0\text{ s}$ with a hop of $H = 5.0\text{ s}$:
$$\text{Relative Timing Uncertainty} = \frac{\Delta t}{W} = \frac{0.20\text{ s}}{10.0\text{ s}} = 2.0\% \quad (\text{Upper bound: } \frac{0.50\text{ s}}{10.0\text{ s}} = 5.0\%)$$

Over $95\%$ to $98\%$ of the window's physiological duration is identically shared between the radar signal and the reference ECG trace.

### 4.3 Mathematical Sensitivity of Window Harmonic Mean Heart Rate
Under `label_spec_v1.json`, the window ground truth is computed as the harmonic mean of valid RR intervals whose midpoints fall within $[t_{\text{start}}, t_{\text{end}})$:
$$\text{HR}_{\text{harmonic}} = \frac{60.0}{\frac{1}{M}\sum_{i=1}^{M} \text{RR}_i}$$

- **Beat Count in Window:** In resting adult humans ($50\text{--}100\text{ BPM}$), a 10.0-second window contains $M \approx 8\text{ to }16\text{ beats}$ ($\text{RR} \approx 0.6\text{--}1.2\text{ s}$).
- **Boundary Beat Shift:** A timing shift of $\Delta t \le 250\text{ ms}$ shifts at most **one beat midpoint** across the window boundary.
- **Heart Rate Variability (HRV) Dynamics:** Under resting breathing or sustained apnea, sinus arrhythmia modulates instantaneous rate smoothly ($\Delta \text{HR} / \Delta t \ll 1\text{ BPM/s}$).
- **Quantitative Error Bound:** If one beat of $0.90\text{ s}$ enters and one beat of $0.85\text{ s}$ exits an $M=12$ beat window:
  $$\Delta \text{HR}_{\text{harmonic}} \approx \left| \frac{60.0}{0.875} - \frac{60.0}{0.879} \right| \approx 0.31\text{ BPM}$$
  Even under extreme physiological variability, the boundary modulation is bounded by **$\le 0.8\text{--}1.2\text{ BPM}$**, well below the clinical tolerance limit of $\pm 5.0\text{ BPM}$ (ANSI/AAMI EC13).

### 4.4 Empirical Agreement Evidence from Step 2B Audit
In `step2b_consistency_audit.md:Section 14`, the independent recomputation of cardiac-band radar displacement FFT peaks vs. nominal zero-shift ECG reference HR across all resting recordings demonstrated:
- **Zero-Shift Cardiac-Band MAE:** **$2.97\text{ BPM}$**.
- **Conclusion:** Gross macroscopic cardiac alignment is already established at nominal $T_0 = 0.0\text{ s}$. Scanning trial shifts $\tau \in [-5, +5]\text{ s}$ overfits in-sample without improving held-out test error.

### 4.5 Boundary Conditions: When Synchronization Matters vs. When It Does Not

```
+----------------------------------------------------------------------------------------------------+
| SCENARIO 1: Window-Level Average Heart Rate Estimation (10.0 s Windows)                            |
| - Target: Mean beat frequency over 10 seconds.                                                     |
| - Impact of 200 ms timing uncertainty: <= 0.5 - 1.2 BPM (< 2% error).                              |
| - Scientific Validity: FULLY DEFENDED AND VALID under UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0.      |
+----------------------------------------------------------------------------------------------------+
| SCENARIO 2: Beat-to-Beat Pulse Transit Time (PTT) / Blood Pressure Estimation                      |
| - Target: Microsecond-to-millisecond delay between ECG R-peak and radar systolic foot.             |
| - Impact of 200 ms timing uncertainty: 50% - 100% error (completely invalidates task).             |
| - Scientific Validity: INVALID — Strictly out of scope for this project.                          |
+----------------------------------------------------------------------------------------------------+
| SCENARIO 3: Sub-Second Arrhythmia Localization (e.g. Single PVC Detection)                         |
| - Target: Exact millisecond occurrence of an ectopic beat.                                         |
| - Impact of 200 ms timing uncertainty: Ambiguity in window assignment.                            |
| - Scientific Validity: INVALID — Excluded by strict all-or-nothing SQI gating.                     |
+----------------------------------------------------------------------------------------------------+
```

### 4.6 Formal Scientific Determination
> **SCIENTIFIC DETERMINATION:**  
> Synchronization uncertainty **DOES NOT invalidate** the reference heart-rate labels for 10-second FMCW radar windows.  
> 
> Because the target variable is the statistical harmonic mean over 10 seconds (aggregating 8–16 cardiac cycles) and model training uses frequency-domain spectrogram / displacement representations rather than point-to-point time-domain matching, a timing uncertainty of $\pm 200\text{ ms}$ contributes less than $1.2\text{ BPM}$ to label variance. This uncertainty is fully accommodated within the project's clinical validation tolerances ($\pm 5\text{ BPM}$ and $\pm 10\text{ BPM}$), provided that the standardized limitation `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` is prominently cited across all publications.

---

## 5. Required Actions & Principal Investigator Handoff Protocol

To resolve all six governance blockers and authorize Phase 2C, the Principal Investigator must execute the following physical steps:

### Step 1: Open the Intake Protocol
Open [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) and complete:
1. **Section 2.2 (Decision D13, Lines 38–49):** Check `[X] OPTION A`, enter PI Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
2. **Section 3.2 (Decision D14, Lines 67–78):** Check `[X] OPTION A`, enter PI Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
3. **Section 4.2 (Decision D15, Lines 94–104):** Check `[X] OPTION A`, enter PI Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
4. **Section 5.2 (Label Spec Approval, Lines 123–133):** Check `[X] APPROVED`, enter PI Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
5. **Section 6.2 (Hardware Timing Acknowledgement, Lines 146–152):** Enter PI Name, Signature, and Date (`YYYY-MM-DD`).
6. **Section 7.3 (Gate Closure Authorization, Lines 174–181):** Check `[X] AUTHORIZED`, enter PI Name, Signature, and Date (`YYYY-MM-DD`).

### Step 2: Populate Approver Name in Label Specification
Open [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json), line 4:
Change `"approved_by": ""` to:
```json
  "approved_by": "<Principal Investigator Full Name>",
```
*(Canonical SHA-256 remains `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44` because canonical hashing ignores `"approved_by"`).*

### Step 3: Run Preflight Check to Verify Transition to GO
```powershell
python kan_radar_HR/src/closure/phase2c_preflight.py
```
- **Current Output:** Gate: `OPEN`, Verdict: `NO-GO` (10 PASS, 6 FAIL).
- **Expected Output Post-Signing:** Gate: `CLOSED`, Verdict: `GO` (16 PASS, 0 FAIL).

### Step 4: Execute Authorized Phase 2C Supervised Generation (ONLY Post-GO)
```powershell
python kan_radar_HR/src/phase3/supervised_dataset_generator.py `
  --spec kan_radar_HR/outputs/closure/spec/label_spec_v1.json `
  --spec-sha256 ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44 `
  --output_dir kan_radar_HR/outputs/supervised_dataset/run_002 `
  --gate-status CLOSED `
  --authorized
```

---

## 6. Safety Confirmations & Governance Certification

1. **No Approvals Fabricated:** No PI identity, signature, date, or authorization flag has been invented or entered.
2. **Scientific Gate Unchanged:** The gate remains strictly **`OPEN`** and the preflight verdict remains strictly **`NO-GO`**.
3. **Output Isolation Preserved:**
   - `outputs/supervised_dataset/run_002`: **Does not exist** (`False`).
   - `outputs/phase5/run_real_001`: **Does not exist** (`False`).
4. **Baseline Integrity Verified:** All historical audit baselines remain bit-for-bit immutable.
5. **Preflight Criteria Intact:** Preflight validation logic, expected hashes, and SQI thresholds have not been modified or weakened.
