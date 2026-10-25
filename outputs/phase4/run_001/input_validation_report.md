# PHASE 4: INPUT DATASET & PREREQUISITE VALIDATION REPORT

**Run ID:** `run_001`  
**Timestamp (UTC):** 2026-10-15T15:46:21.345336+00:00  
**Dataset Source:** `outputs/supervised_dataset/run_001/accepted_window_manifest.csv`  

## 1. Input Audit Summary
- **Total Accepted Windows:** 1029
- **Total Subjects Evaluated:** 24 (VS01 through VS24)
- **Candidate Pairs:** 48 pairs (24 Resting, 24 Apnea)
- **Input Radar Window Dimensions:** 10.0 seconds @ 333.3333 Hz = 3,333 samples per window
- **Primary Radar Preprocessing Filter:** Butterworth bandpass 0.8–3.0 Hz, zero-phase (order 3)
- **Reference HR Ground Truth Derivation:** Harmonic mean of valid ECG R-peak intervals ($60 / \text{mean}(RR)$)
- **SQI Criteria Applied:** Valid RR coverage > 85%, Maximum RR gap < 3.0 s, physiological range [35, 185] bpm

## 2. Gate Verification & Real-Data Training Authorization
- **Phase 2A Finalization Gate Status:** `OPEN`
- **Training Authorization Granted:** `False`
- **Execution Mode:** Model architecture definition, LOSO fold partitioning, synthetic convergence verification, and deliverable compilation.
- **Enforcement Status:** Persistent real-data supervised model training is **`BLOCKED`** in accordance with Mandatory Execution Rule 4.
