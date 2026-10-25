# Supervised Dataset Generation: Implementation Summary

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Supervised Dataset Generation Implementation & Quality Audit  
**Run ID:** `run_001`  
**Output Directory:** `outputs/supervised_dataset/run_001`  
**Execution Timestamp:** 2026-10-15T15:13:00Z  
**Implementation Status:** `DIAGNOSTIC_DRY_RUN_COMPLETED_PERSISTENT_ARRAYS_BLOCKED`  

---

## 1. Overview & Reusable Architectural Components

This stage implements the end-to-end dataset-generation pipeline pairing continuous 120-GHz radar signals with instantaneous ECG-derived reference HR labels under the user-approved SQI criteria.

### Reusable Pipeline Components:
1. **`RobustMatLoader` ([`src/phase3/mat_loader.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/mat_loader.py)):**
   - Validates MATLAB v5/v7 binary formatting across all 96 MAT files.
   - Extracts continuous thoracic displacement `VitalSig` ($f_s = 333.3333\text{ Hz}$) and Lead II ECG `ecg_lead2` ($f_s = 500.0\text{ Hz}$).
   - Enforces zero silent truncation and zero silent zero-padding.
2. **`RadarPreprocessor` ([`src/phase3/radar_preprocessing.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/radar_preprocessing.py)):**
   - Implements the user-approved primary filter: 3rd-order zero-phase Butterworth bandpass filter spanning **0.8 to 3.0 Hz** (48 to 180 bpm).
   - Applied continuously to each 120-second recording prior to window segmentation, preventing edge-filter transients.
3. **`ECGReferenceValidator` ([`src/phase3/ecg_reference.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py)):**
   - In-memory linear interpolation of isolated periodic delimiter NaNs (119–120 NaNs/recording in 47 files).
   - Standardized Pan-Tompkins QRS detection (5–15 Hz bandpass, differentiation, squaring, 150 ms moving integration).
   - Enforces physiological HR bounds ($35.0 \le \text{BPM} \le 185.0$, corresponding to $0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$).
4. **`SupervisedDatasetGenerator` ([`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py)):**
   - Orchestrates window slicing ($10.0\text{ s}$ duration, $5.0\text{ s}$ hop), window-level SQI evaluation, label derivation, provenance tracking, and gate enforcement.

---

## 2. Sliding Window Segmentation Architecture

- **Radar Sampling Rate:** $f_s = 333.3333\text{ Hz}$ ($40,000\text{ samples} / 120.000\text{ s}$).
- **Window Length:** $L = \text{round}(10.0 \times 333.3333) = 3333\text{ samples}$ ($10.0\text{ seconds}$).
- **Hop Length:** $H = \text{round}(5.0 \times 333.3333) = 1667\text{ samples}$ ($5.0\text{ seconds}$, 50% overlap).
- **Window Count:** Exactly **22 complete windows** per 120-second recording (sample start indices $k \cdot 1667$ for $k=0, \dots, 21$).
- **Excluded Trailing Tail:** Exactly **1,660 samples ($4.9800\text{ seconds}$)** per recording.
- **Total Dataset Candidate Windows:** $22 \times 48 = 1056\text{ candidate windows}$.

---

## 3. Window-Level Reference HR Label Calculation

For each candidate window $k$ spanning the nominal time interval $[t_{start}, t_{end}] = [k \cdot 5.0, k \cdot 5.0 + 10.0)\text{ seconds}$:
1. All RR intervals whose midpoints $m_i = (t_i + t_{i+1}) / 2$ fall within $[t_{start}, t_{end}]$ are identified.
2. The window is evaluated against the user-approved SQI criteria:
   - Valid RR coverage: $\ge 85.0\%$ of $10.0\text{ s}$ window.
   - Maximum RR interval gap: $< 3.0\text{ seconds}$.
   - All RR intervals within physiological limits: $0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$.
3. If valid, the reference ground-truth heart rate is computed using the standard harmonic mean formula:
   $$HR_{\text{ref}}(k) = \frac{60.0}{\frac{1}{N_{rr, k}} \sum_{i \in I_k} RR_i} \quad (\text{BPM})$$
   alongside the arithmetic mean of instantaneous rates $\frac{1}{N_{rr, k}} \sum_{i \in I_k} \frac{60.0}{RR_i}$.

---

## 4. Aggregate Window Acceptance & Rejection Summary

Across the full dataset of 1,056 candidate windows:
- **Accepted Windows:** **1,029 windows (97.44%)** across 47 recordings.
- **Rejected Windows:** **27 windows (2.56%)** across 3 subjects / 4 recordings.
- **Excluded Files / Windows:**
  - `VS10_Resting`: All 22 windows rejected (`ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`) due to a delimiter NaN at sample index `0`.
  - `VS03_Resting`: Window 0 rejected (`RR_COVERAGE_BELOW_85_PCT`, 84.96% coverage).
  - `VS16_Apnea`: Windows 4 and 5 rejected (`NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`).
  - `VS16_Resting`: Windows 0 and 1 rejected (`NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`).

---

## 5. Gate Enforcement & Blocker Status

In strict adherence to Mandatory Rule 4 and Rule 5:
- **Phase 2A Finalization Gate Status:** **`OPEN`** (`step2b_consistency_audit.md`).
- **Supervised Dataset Extraction Status:** **`BLOCKED BY PHASE 2A GATE`**.
- The pipeline successfully generated all diagnostic manifests (`candidate_window_manifest.csv`, `accepted_window_manifest.csv`, `rejected_window_manifest.csv`), but **persistent binary arrays (`X_radar.npy`, `y_hr.npy`) were withheld** from disk pending formal closure of the Phase 2A gate.
