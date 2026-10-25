# PHASE 5: PHASE 2A GATE DECISION & AUTHORIZATION STATUS

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  
**Gate Status:** **`FINALIZATION GATE OPEN — REAL-DATA MODEL TRAINING BLOCKED`**  

---

## 1. Phase 2A Finalization Gate Inspection

In compliance with Phase 5 Task 2, the primary governance source documents were examined:

### Source Document: `outputs/phase2a/step2b_consistency_audit.md`
- **Official Stage Verdict (Line 9):**
  > `PHASE 2A — STEP 2B STATUS: RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION.`
- **Supervised-Label Generation Status (Line 12):**
  > `NOT YET APPROVED`
- **Hardware Clock Synchronization Status (Line 13):**
  > `UNVERIFIED`
- **10-Second Window-Alignment Adequacy (Line 15):**
  > `NOT YET SUPPORTED without its evidence gate`
- **Scientific Headline (Line 16):**
  > `"EMPIRICAL RESTING CARDIAC-BAND AGREEMENT OBSERVED FOR 10 s WINDOWS AT ZERO SHIFT (MAE = 2.97 BPM); SUPERVISED LABEL GENERATION NOT YET APPROVED; HARDWARE CLOCK UNVERIFIED"`

---

## 2. Hardware Synchronization Status & Operational Convention

### Known Scientific Limitation: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`
- **Physical Assessment:** There is no shared electronic master clock, no TTL pulse trigger, and no genlock synchronization between the 120-GHz FMCW radar digitizer and the Mindray ECG bio-signal recorder.
- **Clock Drift:** Radar operates at nominal $f_s \approx 333.333\text{ Hz}$ while ECG operates at $f_{s,\text{ECG}} = 1,000\text{ Hz}$. Independent oscillator crystal drift (typically $\pm 20 - 50\text{ ppm}$) precludes microsecond-level phase lock.
- **Scientific Decision:** Hardware clock synchronization remains **`UNVERIFIED`**. No claim of verified physical synchronization can be made.
- **Operational Convention:** Window boundaries are constructed assuming recording file start samples correspond to nominal $t_0 = 0.0\text{ s}$. For 10.0-second windowed average HR estimation, this assumption introduces negligible error ($< 0.1\text{ BPM}$) during stationary periods, but must remain documented as a scientific limitation.

---

## 3. Disqualification of Bedside Monitor Displayed HR

Phase 2A cross-correlation lag scans and step-response audits revealed a critical data characteristic:
- **Mean Observed Latency:** $+6.21\text{ seconds}$ relative to instantaneous ECG R-peak ground truth (median: $+7.0\text{ s}$, mode: $+7.0\text{ s}$, with 40/48 recordings falling in $[+4\text{ s}, +10\text{ s}]$).
- **Cause:** Proprietary moving-average smoothing filter on commercial bedside monitor hardware.
- **Governance Rule:** The commercial bedside monitor displayed HR stream is **permanently disqualified** from serving as ground truth reference labels. Supervised models trained against the monitor HR would inherit severe phase distortion and artificial label latency.

---

## 4. Evaluation of User Authorization & Gate Blocker Enforcement

- **Mandatory Rule:**
  > *"Check whether explicit real-data training authorization and any required gate closure are documented. If authorization is missing or the gate is still OPEN, do not start or resume real-data model fitting. Audit existing outputs, complete non-training checks, and report the exact blocker... Do not close the gate automatically."*
- **Audit Findings:**
  1. The user has not submitted an explicit statement closing the Phase 2A Finalization Gate.
  2. The user has not explicitly authorized the export of persistent supervised ML tensors or the execution of real-data model fitting on disk.
  3. The AI assistant cannot unilaterally or automatically close a governance gate.
- **Enforcement Decision:**
  - Real-data model fitting for KAN, CNN, MLP, and baseline models is strictly **`BLOCKED`**.
  - All non-training checks (dataset validation, LOSO split audit, feature pipeline audit, model latency benchmarking, and test suite execution) were completed in full.
  - Zero real-data checkpoints or prediction files were fabricated.
