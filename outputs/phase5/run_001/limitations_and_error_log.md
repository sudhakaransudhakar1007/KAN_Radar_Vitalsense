# PHASE 5: LIMITATIONS, EXPERIMENTAL CONSTRAINTS & AUDIT LOG

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

This document registers all scientific limitations, experimental constraints, hardware gaps, and governance blockers identified during Phase 5. In accordance with strict reproducibility standards, these items are preserved without mitigation or omission.

---

## 2. Inventory of Scientific & Engineering Limitations

### A. Lack of Hardware Clock Synchronization (`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`)
- **Limitation:** The 120-GHz FMCW radar and the reference ECG bio-signal recorder operate on independent hardware clocks without shared electronic clock signals, TTL triggers, or genlock synchronization.
- **Operational Assumption:** Data streams are aligned by setting recording file start samples to nominal $t=0.0\text{ s}$.
- **Impact:** Sub-second phase alignment between radar micro-Doppler chest-wall displacement and ECG electrical R-peaks cannot be verified physically. However, for 10-second windowed average HR estimation, nominal alignment introduces negligible bias ($< 0.1\text{ BPM}$) provided sample clock drift remains small ($< 50\text{ ppm}$).

### B. Permanent Disqualification of Displayed Bedside Monitor HR
- **Limitation:** The commercial bedside monitor displays an HR value that lags instantaneous ECG R-peak ground truth by a mean of $+6.21\text{ seconds}$.
- **Root Cause:** Proprietary internal moving-average filtering and peak tracking algorithms implemented in commercial bedside firmware.
- **Scientific Decision:** Monitor HR is disqualified as ground truth. Only instantaneous RR-derived HR ($\text{HR} = 60 / \overline{RR}$) from audited ECG leads is scientifically defensible.

### C. Governance Blocker: Phase 2A Finalization Gate OPEN
- **Limitation:** The Phase 2A Finalization Gate remains officially **`OPEN`** (`outputs/phase2a/step2b_consistency_audit.md`).
- **Enforcement:** In strict compliance with Phase 5 Section 1, no persistent real-data training tensors were exported, and no models were fitted to real VITALSENSE data. Real-data training cannot proceed without explicit user gate closure and training authorization.

### D. Classical Autocorrelation Baseline Implementation Gap
- **Limitation:** Classical autocorrelation peak tracking remains cataloged as an unimplemented baseline.
- **Root Cause:** Unassisted autocorrelation on chest-wall displacement signals is highly susceptible to respiration harmonics (first and second breathing harmonics frequently overlap with cardiac fundamental frequencies during resting bradycardia or shallow breathing). Without an approved, validated harmonic-cancellation algorithm, reporting ad-hoc autocorrelation numbers would produce unscientific and artificially depressed baseline comparisons.

### E. Cohort Demographics & Generalizability
- **Limitation:** The VITALSENSE dataset comprises 24 healthy adult volunteers recorded under controlled sitting conditions (resting and immediately post-exercise).
- **Impact:** The generalizability of the trained KAN and baseline models to clinical populations (patients with arrhythmias, atrial fibrillation, congestive heart failure, severe dyspnea, or pediatric patients) and unconstrained ambulatory motion remains unproven.

### F. Bandpass Filtering Assumptions
- **Limitation:** The primary radar filter passband ($0.8 - 3.0\text{ Hz}$, $48 - 180\text{ BPM}$) was selected based on physiological plausibility and spectral inspections.
- **Status:** Whether this passband yields optimal estimation accuracy relative to narrower ($0.8 - 2.0\text{ Hz}$) or adaptive filtering remains an empirical question that must be tested during authorized model training.

---

## 3. Error & Exception Log

| Timestamp (UTC) | Category | Code / Subsystem | Description | Resolution / Status |
| :--- | :--- | :--- | :--- | :--- |
| `2026-10-16 09:20` | Governance | Phase 2A Gate | Gate status confirmed `OPEN` in `outputs/phase2a/step2b_consistency_audit.md`. | Enforced real-data training block. |
| `2026-10-16 09:21` | Authorization | User Directive | User prompt provided Phase 5 instructions subject to gate closure, without explicit closure statement. | Blocked real-data training; executed non-training checks only. |
| `2026-10-16 09:25` | Baseline Model | Autocorrelation | Classical autocorrelation lacks validated algorithmic specification. | Documented as explicit baseline implementation gap. |
| `2026-10-16 09:28` | Data Quality | Supervised Dataset | 27 of 1,056 candidate windows disqualified by SQI screening ($< 85\%$ RR coverage or $> 3.0\text{s}$ gap). | Excluded from training set; logged in `rejected_window_manifest.csv`. |
