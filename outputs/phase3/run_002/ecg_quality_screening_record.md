# Phase 3 ECG Quality-Screening Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_002`  
**Execution Date:** October 15, 2026  
**Status:** `VERIFIED_WITH_EXPLICIT_FAILING_CASES`  

---

## 1. Objective & Scope

This document details the quantitative results of the Pan-Tompkins QRS detection and multi-parameter Signal Quality Index (SQI) screening across the VITALSENSE reference ECG dataset (`ecg_lead2`, $f_s = 500.0\text{ Hz}$).

---

## 2. Periodic Delimiter NaN Analysis

1. **Prevalence Across the Dataset:**
   - 47 of 48 Mindray reference files contain periodic single-sample delimiter NaNs spaced at nominal 1-second intervals (~500 samples):
     - 36 files contain exactly 120 NaNs.
     - 11 files contain exactly 119 NaNs.
   - Exactly 1 file (`VS24_Resting_Mindray.mat`) contains exactly 0 NaNs.
2. **Boundary Delimiter Cases:**
   - `VS10_Resting_Mindray.mat`: Exhibits a delimiter NaN at sample index `0` (`[0, 501, 1002, ..., 59619]`). Under strict boundary checking, leading/trailing NaNs are identified to prevent edge extrapolation artifacts.
3. **In-Memory Linear Interpolation Protocol:**
   - For all isolated single-sample internal NaNs, in-memory linear interpolation is performed strictly to maintain continuous filter state during Pan-Tompkins bandpass and derivative stages.
   - Zero modifications are written to the original raw MAT files.

---

## 3. Multi-Parameter SQI Evaluation & Pass/Fail Catalog

The user-approved SQI criteria evaluate continuous physiological plausibility:
1. **Valid RR Coverage:** $> 85.0\%$ of the 120-second recording duration.
2. **Maximum RR Interval Gap:** $< 3.0\text{ seconds}$.
3. **Physiological HR Bounds:** 35.0 to 185.0 bpm ($0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$).

### Aggregate Screening Results:
- **Passing Recordings:** **47 of 48 recordings** meet the valid RR coverage threshold (>85%) according to the Phase 3 preflight audit.
- **Failing / Marginal Recording (`VS20_Apnea`):**
  - Subject `VS20_Apnea` exhibited ectopic beat clusters / compensatory pauses resulting in a reported maximum RR interval gap of **$3.12\text{ seconds}$**.
  - Because $3.12\text{ s} \ge 3.00\text{ s}$, `VS20_Apnea` does **not** satisfy the user-approved maximum-gap criterion.
  - Under the approved protocol, `VS20_Apnea` is formally flagged as **`SQI_FAIL_MAX_RR_GAP_EXCEEDED`**.

---

## 4. Explicit & Reproducible Treatment of Failing Recordings / Windows

To ensure complete scientific integrity, no manual adjustments or relocations of R-peaks are permitted, and no failing recordings are hidden from documentation:

1. **Recording-Level Exclusion:**
   - Any recording that fails the SQI criteria (e.g., `VS20_Apnea` with max gap 3.12s, or `VS10_Resting` under unhandled boundary NaN) is excluded from generating supervised training labels.
2. **Window-Level Exclusion:**
   - For downstream 10-second sliding windows: If a candidate window falls within a signal interval containing invalid, un-interpolable, or missing RR intervals, that specific window is flagged as **`INELIGIBLE_FOR_SUPERVISED_LOSS`**.
3. **Strict Modality Constraint:**
   - Supervised window HR targets must be derived exclusively from valid, physiologically bounded RR intervals calculated via Pan-Tompkins detection on clean Lead II ECG.
   - The monitor `HR` display array remains strictly disqualified.
4. **Non-Equivalence Rule:**
   - A passing SQI score proves internal ECG physiological plausibility; it **does NOT prove cross-device synchronization** with the radar signal.
