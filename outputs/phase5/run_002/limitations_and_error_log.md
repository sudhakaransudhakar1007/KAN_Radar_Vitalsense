# PHASE 5: SCIENTIFIC LIMITATIONS, EXPERIMENTAL CONSTRAINTS & AUDIT ERROR LOG

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

This document formalizes all scientific limitations, experimental constraints, hardware gaps, and governance blockers identified during the Phase 5 audit. In adherence to strict scientific reporting rules (Task 14), these items are documented without mitigation or omission.

---

## 2. Mandatory Scientific Reporting Rules & Prohibited Claims (Task 14)

In compliance with Phase 5 Task 14, the following explicit scientific boundaries are maintained across all reports and publications:

1. **Hardware Timing Assumption:**
   # `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`
   - *Physical reality:* No common hardware clock, electronic trigger signal, or genlock synchronization exists between the FMCW radar digitizer and the ECG recorder.
   - *Operational convention:* Data streams are aligned assuming their recording file start indices correspond to nominal $t=0.0\text{ s}$.
   - *Prohibited claim:* **Do not claim that physical synchronization has been proven.**
2. **Clinical Applicability:**
   - *Cohort demographics:* The VITALSENSE dataset comprises 24 healthy adult volunteers recorded under controlled sitting conditions (resting and breath-hold recovery).
   - *Prohibited claim:* **Do not claim that clinical validity has been established, or that arrhythmia classification was performed.**
3. **Model Superiority:**
   - *Evaluation status:* While synthetic gradient convergence and architectural capacity have been verified, real-data 24-fold LOSO model training has not yet executed due to the open governance gate.
   - *Prohibited claim:* **Do not claim that the proposed KAN model is superior to CNN, MLP, or classical baselines without valid held-out real-data empirical evidence.**
4. **Hardware Performance:**
   - *Measurement context:* Parameter counts and inference latencies were benchmarked on a standard x86_64 CPU workstation using single-window batches ($B=1$).
   - *Prohibited claim:* **Do not claim live embedded-hardware or edge-ASIC performance was measured.**

---

## 3. Registered Scientific Limitations

### A. Displayed Bedside Monitor HR Disqualification
- **Observation:** The commercial Mindray bedside monitor displayed HR array exhibits a systematic $+6.21\text{ s}$ latency relative to instantaneous ECG R-peak ground truth.
- **Scientific Impact:** The monitor HR is permanently disqualified as ground truth reference labels. Only instantaneous R-peak derived heart rate ($\text{HR}_{\text{ref}} = 60 / \overline{RR}$) from audited ECG Lead-II is scientifically valid.

### B. Classical Autocorrelation Implementation Gap
- **Observation:** Classical autocorrelation peak tracking lacks an approved, validated mathematical specification for respiration harmonic rejection.
- **Scientific Impact:** Classical autocorrelation is cataloged as **`NOT IMPLEMENTED`** rather than evaluated with an arbitrary, ad-hoc heuristic that would artificially bias comparison.

### C. Governance Blocker: Phase 2A Finalization Gate OPEN
- **Observation:** In `outputs/phase2a/step2b_consistency_audit.md`, the Phase 2A Finalization Gate status is officially **`OPEN`**.
- **Scientific Impact:** Supervised persistent dataset generation (binary arrays / ML tensors) and real-data model fitting remain strictly blocked until explicit user sign-off.

---

## 4. Phase 5 Execution Error & Exception Log

| Timestamp (UTC) | Category | Subsystem | Description | Resolution / Status |
| :--- | :--- | :--- | :--- | :--- |
| `2026-10-16 10:05` | Governance | Phase 2A Gate | Gate status confirmed `OPEN` in `outputs/phase2a/step2b_consistency_audit.md`. | Enforced real-data training block. |
| `2026-10-16 10:08` | Authorization | User Directive | User prompt provided Phase 5 instructions subject to gate closure, without explicit closure statement. | Blocked real-data training; completed non-training checks only. |
| `2026-10-16 10:12` | Dataset | SQI Screening | 27 of 1,056 candidate windows disqualified by SQI screening ($< 85\%$ RR coverage or $> 3.0\text{ s}$ gap). | Excluded from training set; logged in `rejected_window_manifest.csv`. |
| `2026-10-16 10:15` | Baseline Model | Autocorrelation | Classical autocorrelation lacks validated algorithmic specification. | Documented as explicit baseline implementation gap. |
| `2026-10-16 10:18` | Artifact Audit | Training Outputs | No checkpoints or prediction CSVs generated due to gate block. | Formally registered as NOT GENERATED in `checkpoint_manifest.md`. |
