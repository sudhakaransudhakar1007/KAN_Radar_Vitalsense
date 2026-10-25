# PHASE 7: GOVERNANCE GATE STATUS & INVESTIGATOR DECISION CHECKLIST

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  
**Official Gate Status:** **`FINALIZATION GATE OPEN — TRAINING BLOCKED`**  

---

## 1. Official Phase 2A Gate State Inspection

Programmatic and documentary inspection confirms that the Phase 2A Finalization Gate remains officially **`OPEN`**:
- Source document: `outputs/phase2a/step2b_consistency_audit.md` (lines 9–16).
- Official Verdict: `PHASE 2A — STEP 2B STATUS: RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION.`
- Persistent ML Tensor Export: `BLOCKED / WITHHELD`.
- Real-Data Model Fitting: `UNAUTHORIZED`.

In accordance with strict research integrity rules, the AI assistant cannot unilaterally close this gate.

---

## 2. Granular Multi-Dimensional Readiness Assessment

To prevent collapsing distinct scientific boundaries into a misleading generic "ready" status, the readiness of each subsystem is evaluated independently:

| Engineering / Research Subsystem | Detailed Readiness Status | Evidentiary Basis & Current Condition |
| :--- | :---: | :--- |
| **1. Dataset-Audit Readiness** | **`READY`** | 24 subjects, 48 recording pairs, 100% paired, sampling rates verified (`Radar.fs` = 333.33 Hz, `Fs_ecg` = 500 Hz). |
| **2. Label-Generation Readiness** | **`READY`** | 1,029 accepted windows, SQI thresholds (coverage $\ge 85\%$, gap $\le 3\text{s}$), Pan-Tompkins R-peak detector verified. |
| **3. Scientific Synchronization** | **`UNVERIFIED`** | Physical synchronization unproven. Operates strictly under `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. |
| **4. Software-Test Readiness** | **`READY`** | 100 / 100 automated unit and integration tests passing cleanly across 13 test files. |
| **5. Supervised Tensor Export** | **`BLOCKED`** | Blocked by Phase 2A gate; dry-run manifests generated, binary persistent arrays withheld. |
| **6. Real-Data Model Training** | **`BLOCKED`** | Blocked by Phase 2A gate; 0 real-data checkpoints created; no model fitting performed. |
| **7. Independent Evaluation** | **`BLOCKED`** | 24-fold LOSO partitions verified with 0% leakage, but held-out execution withheld until training authorization. |
| **8. Clinical Interpretation** | **`NOT READY`** | Dataset limited to 24 healthy volunteers in sitting positions. Clinical diagnostic claims prohibited. |

---

## 3. Missing Gate Closure Evidence & Prerequisite Checklist

Before the Phase 2A Finalization Gate can be legally and scientifically closed, the following prerequisites must be documented:

1. **Formal Gate Closure Addendum:** An auditable investigator statement formally closing Phase 2A Step 2B.
2. **Explicit Decision on Hardware Timing Limitations:** Investigator sign-off accepting `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` as an exploratory research limitation for 10-second windowed average HR estimation.
3. **Formal Disqualification of Bedside Monitor HR:** Explicit acknowledgment that the displayed bedside monitor HR (+6.21s latency) cannot be used as ground truth.
4. **Explicit Authorization for Tensor Export and Real-Data Training:** Formal investigator sign-off permitting the creation of persistent supervised ML tensors and real-data 24-fold LOSO model fitting.

---

## 4. Investigator Decision Checklist

The principal investigator must review the evidence and execute one of the following decisions:

### Pathway A: Conditional Authorization for Exploratory Research
If the investigator determines that nominal start-time alignment is scientifically sufficient for 10-second windowed average HR estimation under the approved institutional protocol:
> *"I approve the formal closure of the Phase 2A Finalization Gate under the documented UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 operational convention and the permanent disqualification of bedside monitor HR. I authorize the export of persistent supervised ML training tensors and the execution of real-data 24-fold LOSO model training and evaluation for KAN, CNN, MLP, and baseline models."*

### Pathway B: Halt for Additional Hardware Evidence
If the research protocol requires verified micro-Doppler phase synchronization:
> *"Real-data training remains BLOCKED. Additional physical hardware trigger or shared-clock acquisition evidence is required before supervised dataset generation may proceed."*
