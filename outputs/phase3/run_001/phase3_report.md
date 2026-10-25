# Phase 3 Scientific Audit & Preflight Implementation Report

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_001`  
**Execution Timestamp:** `2026-10-15T09:24:57.618429+00:00`  
**Pipeline Author:** Senior Biomedical Signal Processing & Scientific ML Engineering Team  
**Execution Status:** `COMPLETED_PREFLIGHT_AND_AUDIT_LABEL_GENERATION_HALTED`  

---

## 1. Executive Summary & Approval Gate Status

Phase 3 established the non-destructive production data-loading, synchronization audit, ECG reference validation, radar preprocessing, and sliding-window segmentation infrastructure across all 48 candidate radar/reference recording pairs of the VITALSENSE dataset (subjects VS01–VS24, Resting and Apnea conditions).

### Mandatory Stop-Condition Compliance
In strict adherence to the project charter, Section 0 rules, and Section 6 stop conditions:
1. **The Phase 2A Finalization Gate remains OPEN.** The Phase 2A consistency audit concluded with `PHASE 2A — STEP 2B STATUS: RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION`.
2. **Supervised HR-label generation is NOT YET APPROVED.** No ground-truth label arrays or supervised window training sets were generated.
3. **Persistent window dataset generation is HALTED.** The `WindowGenerator` raised `LabelGenerationBlockedError`, logging active blockers in `run_manifest.json`.
4. **Zero Model Training:** No Kolmogorov-Arnold Networks (KAN), Multi-Layer Perceptrons (MLP), or Convolutional Neural Networks (CNN) were trained.
5. **Data Integrity:** All 96 raw MAT files and previous Phase 1/Phase 2 deliverables remain strictly untouched and bit-identical.

```
+-----------------------------------------------------------------------------------+
|                            PHASE 3 EXECUTION GATES                               |
+-----------------------------------------------------------------------------------+
|  1. Robust MAT Loading (v5/v7, no silent truncation/padding)  |  [PASSED]         |
|  2. Synchronization Audit (48 pairs, explicit time axes)      |  [PASSED]         |
|  3. ECG Reference In-Memory Interpolation & Pan-Tompkins QRS   |  [PASSED]         |
|  4. Multi-Parameter SQI Diagnostic Screening                  |  [PASSED]         |
|  5. Radar Preprocessing & Comparative Spectral Filter Audit   |  [PASSED]         |
|  6. Window Boundary Diagnostics (10s win, 5s hop, 22 win/rec) |  [PASSED]         |
|  7. Automated Regression Suite (67 tests, 100% pass rate)     |  [PASSED]         |
|  -------------------------------------------------------------------------------  |
|  8. Supervised Ground-Truth HR-Label Generation               |  [BLOCKED - GATE] |
|  9. Machine Learning Model Training (KAN / Baseline)          |  [BLOCKED - GATE] |
+-----------------------------------------------------------------------------------+
```

---

## 2. Raw Dataset Inventory & File Verification

The dataset directory `data/VITALSENSE_120_DATASET` was inspected using `RobustMatLoader`:
- **Total MAT Files Discovered:** Exactly 96 `.mat` files across 24 subject directories (`VS01` to `VS24`).
- **File Distribution:** 48 radar signal files (`<Subject>_<Condition>.mat`) and 48 Mindray reference files (`<Subject>_<Condition>_Mindray.mat`).
- **File Formats:** 100% of the 96 files conform to MATLAB v5.0 / v7.0 structured binary format.
- **Inventory Checksum Match:** Verified against `outputs/phase1_audit/file_inventory.csv` with zero byte-level discrepancies (composite dataset SHA-256: `a3fc618267c9fe10c55d045d909ec903d6d03cf1c33c3065b75883d6e5c5aa44`).
- **Missing Variables:** 0 files missing mandatory variables. Radar files contain `VitalSig` and `Radar.fs`; Mindray reference files contain `ecg_lead2`, `HR`, `respiration`, `param.Fs_ecg`, and `param.Fs_resp`.

---

## 3. Synchronization Audit & Evidence Hierarchy

All 48 candidate recording pairs were subjected to a rigorous synchronization audit. Findings are cataloged in `synchronization_manifest.csv` and summarized in `synchronization_audit.md`:

```
                           EVIDENCE HIERARCHY FOR SYNCHRONIZATION
Level 1: Hardware Sync Markers / PPS Triggers ─────────► ABSENT (0 of 96 files)
Level 2: Cross-Device Common Clock Reference ─────────► ABSENT (Unverified Clock Drift)
Level 3: Prespecified Nominal Alignment (t0 = 0.0 s) ─► ADOPTED WITH UNVERIFIED STATUS
```

1. **Hardware Synchronization Status:** `UNVERIFIED`. None of the files contain hardware trigger signals, PPS pulses, or shared clock timestamps.
2. **Relative Time Alignment:** Evaluated under the prespecified nominal zero-offset convention ($t_0 = 0.0\text{ s}$ for both devices).
3. **Cross-Device Duration Mismatches:**
   - 47 of 48 pairs exhibit matching 120.0-second nominal durations (40,000 radar samples at 333.3333 Hz vs 60,000 ECG samples at 500.0 Hz).
   - Exactly 1 pair (`VS24_Resting`) exhibits an empirical mismatch: Mindray reference duration is 120.0 seconds (60,000 ECG samples, 30,600 respiration samples), while respiration sample rate is documented as 256.0 Hz ($30600 / 256.0 = 119.53125\text{ s}$), leaving a 0.46875-second nominal mismatch.
4. **Sub-second Confidence:** Formally cataloged as `UNVERIFIED_HARDWARE_TIMING` across all 48 pairs.

---

## 4. Reference HR Modality Separation & Latency

Phase 3 implements strict architectural separation between reference modalities:
1. **Mindray Monitor Display HR (`HR` array, $f_s = 1.0\text{ Hz}$):**
   - Confirmed to exhibit a systematic $+6.0\text{ s}$ to $+7.0\text{ s}$ moving-average and display latency relative to instantaneous cardiac events.
   - **Disqualification Verdict:** Strictly disqualified from serving as supervised training labels for 10-second sliding windows. Using monitor HR introduces temporal label leakage and severe misalignments.
2. **Instantaneous ECG-Derived HR:**
   - Computed from Pan-Tompkins QRS detections on cleaned Lead II ECG ($f_s = 500.0\text{ Hz}$).
   - Serves as the candidate physiological ground truth, pending formal protocol sign-off.

---

## 5. ECG Quality, Delimiter NaNs & R-Peak Validation

### Periodic Delimiter NaN Analysis
- **Prevalence:** 47 of 48 Mindray files exhibit periodic single-sample NaNs in `ecg_lead2`:
  - 36 recordings contain exactly 120 NaNs (spaced at exactly 500 samples, or 1.000 s).
  - 11 recordings contain exactly 119 NaNs (periodic delimiters starting after index 0 or ending before final sample).
  - Exactly 1 recording (`VS24_Resting_Mindray.mat`) contains exactly 0 NaNs.
- **Pattern Verification:** 100% of the NaNs across all 47 files are isolated single-sample delimiters (`multi_sample_gaps == 0`, `leading_trailing_nans == False`).
- **In-Memory Interpolation:** Corrected strictly in-memory using linear interpolation between adjacent valid samples for QRS detection. Zero raw files were modified.

### Pan-Tompkins QRS Detection
- Bandpass filtering (5.0–15.0 Hz, 3rd-order Butterworth), 5-point derivative, squaring, and moving-window integration (150 ms window).
- Verified on all 48 recordings:
  - 0 duplicate peak indices detected.
  - 0 non-monotonic peak timestamp sequences.
  - Physiological heart-rate bounds enforced: 35.0 to 185.0 bpm.
  - Detection results cataloged in `rpeak_detection_summary.csv`.

---

## 6. Multi-Parameter SQI Diagnostic Results

Each ECG recording was evaluated against multi-parameter Signal Quality Index (SQI) criteria:
1. **Valid RR-interval coverage:** $\ge 85.0\%$ of the recording duration.
2. **Maximum RR-interval gap:** $< 3.0\text{ seconds}$.
3. **Physiological RR bounds:** $324\text{ ms} \le RR_i \le 1714\text{ ms}$ (35–185 bpm).

### Results Summary
- **Proposed SQI Pass Count:** **47 of 48 recordings (97.9%)** satisfied the criteria.
- **Marginal / Failed Recording:** `VS20_Apnea` exhibited ectopic beat clusters with a maximum RR gap of $3.12\text{ s}$, triggering SQI flag `MAX_RR_GAP_EXCEEDED_3.0S`.
- **Official Ground-Truth Eligibility:** Marked strictly as **`NOT_APPROVED_PENDING_PROTOCOL_SIGN_OFF`** across all 48 recordings.

---

## 7. Radar Preprocessing & Filter Characterization

The radar preprocessor evaluated two candidate filter topologies against raw `VitalSig` (continuous phase-demodulated displacement signal):
1. **Candidate 1.0–20.0 Hz Bandpass:** 3rd-order zero-phase Butterworth filter. Captures respiratory harmonics and broadband chest-wall vibration.
2. **Cardiac 0.8–3.0 Hz Bandpass:** 3rd-order zero-phase Butterworth filter (corresponding to 48–180 bpm). Isolates ballistocardiographic surface displacement.

### Quantitative Comparison (48 Recordings)

| Metric | Raw VitalSig | Candidate 1.0–20.0 Hz | Cardiac 0.8–3.0 Hz |
| :--- | :---: | :---: | :---: |
| **Mean Cardiac Band Power Ratio** | 0.0060 (0.6%) | 0.3911 (39.1%) | **0.4843 (48.4%)** |
| **Mean Peak-to-Peak Amplitude** | 7.0725 | 0.7979 | 0.8346 |
| **Standard Deviation** | 1.1842 | 0.0891 | 0.0934 |
| **Phase Distortion** | N/A | Zero (filtfilt) | Zero (filtfilt) |
| **Nyquist Bound Satisfaction** | Valid ($f_s = 333.33$) | Valid ($20 < 166.67$) | Valid ($3.0 < 166.67$) |

*Recommendation:* The 0.8–3.0 Hz cardiac bandpass filter yields superior cardiac power concentration (48.4% vs 39.1% and 0.6%), removing massive low-frequency respiratory drift while preserving cardiac ballistocardiographic morphology.

---

## 8. Sliding Window Segmentation Architecture & Tail Handling

The sliding-window segmentation scheme was validated across all 48 radar recordings:
- **Window Length:** 10.0 seconds ($L = \text{round}(10.0 \times 333.3333) = 3333\text{ samples}$).
- **Hop Size:** 5.0 seconds ($H = \text{round}(5.0 \times 333.3333) = 1667\text{ samples}$, 50% overlap).
- **Candidate Windows per 120s Recording:** Exactly **22 complete windows** per recording ($0\text{--}10\text{s}, 5\text{--}15\text{s}, \dots, 105\text{--}115\text{s}$, and $107.0\text{--}117.0\text{s}$).
- **Total Dataset Candidate Windows:** $22 \times 48 = 1056\text{ candidate windows}$.
- **Trailing Tail Accounting:**
  - Total samples: 40,000.
  - Samples covered by 22 windows: $0 \text{ to } (21 \times 1667 + 3333) = 38,340\text{ samples}$.
  - Excluded trailing tail: Exactly **1660 samples (4.98 seconds)** per recording.
  - Tail handling rule: Excluded without silent zero-padding or length distortion.

---

## 9. Blocker Analysis & Scientific Stop Conditions

Supervised window dataset generation and KAN model training are blocked by the following documented findings:

```
+-----------------------------------------------------------------------------------------+
|                               ACTIVE PROJECT BLOCKERS                                   |
+-----------------------------------------------------------------------------------------+
| BLK-01: Phase 2A Finalization Gate Open                                                 |
|         The Phase 2A audit concluded RECONCILIATION PARTIAL; formal closure is required.|
|                                                                                         |
| BLK-02: Unverified Hardware Clock Synchronization                                      |
|         Absence of hardware sync markers or PPS triggers introduces potential sub-second|
|         timing uncertainty across independent acquisition hardware clocks.              |
|                                                                                         |
| BLK-03: Monitor HR Latency Disqualification                                             |
|         Mindray monitor HR exhibits a +6s to +7s display lag, requiring formal protocol |
|         adoption of ECG-derived instantaneous HR.                                       |
|                                                                                         |
| BLK-04: Ground-Truth Label Approval Pending                                             |
|         Multi-parameter ECG SQI screening has passed diagnostics (97.9%), but user sign-|
|         off is required before generating persistent supervised dataset arrays.          |
+-----------------------------------------------------------------------------------------+
```

---

## 10. Hardware Trigger & Clock Drift Assessment

- **Trigger Channel Search:** Inspected all struct fields and channel names in all 96 MAT files. Confirmed: No auxiliary synchronization trigger channels, TTL pulses, or PPS markers exist.
- **Clock Drift Risk:** Radar and Mindray hardware operated on independent internal crystal oscillators. Over 120 seconds, standard commercial crystal tolerances ($\pm 20\text{ ppm}$) could induce up to $2.4\text{ ms}$ of clock drift—negligible for 10-second average HR estimation, but uncharacterized for microsecond phase alignment.

---

## 11. Respiration vs Cardiac Separation Evidence

Raw radar `VitalSig` is heavily dominated by large-amplitude chest-wall respiratory displacement ($>99\%$ of total spectral power), with cardiac ballistocardiographic displacements contributing less than $1\%$ of raw signal power. Filtering with a dedicated 0.8–3.0 Hz zero-phase bandpass filter increases the relative cardiac power concentration by a factor of 80x (from 0.0060 to 0.4843), confirming the necessity of rigorous physiological bandpass preprocessing prior to non-linear KAN feature extraction.

---

## 12. Risk Analysis for Downstream KAN Modeling

1. **Temporal Label Misalignment Risk:** If models are trained against nominal ECG labels without accounting for potential sync uncertainty, gradient updates may penalize correct predictions. 10-second average HR labels mitigate this risk significantly compared to instantaneous beat-to-beat tracking.
2. **Overfitting to Subject Ballistocardiogram Morphology:** Chest-wall morphology and radar reflectance vary widely across subjects. Training on random window splits will cause severe data leakage and inflated test performance.
3. **Nonlinear Spline Activation Collapse:** KAN B-spline activation functions require well-normalized inputs to prevent spline grid saturation. Filtered radar signals must undergo z-score normalization per window.

---

## 13. Evaluation Protocol & Split Integrity Guidelines

To guarantee true generalization and prevent subject leakage, the downstream KAN evaluation protocol must adhere to:
1. **Strict Subject-Level Cross-Validation:**
   - **Primary Protocol:** Leave-One-Subject-Out (LOSO) Cross-Validation across all 24 subjects (24 folds).
   - **Alternative Protocol:** Subject-stratified split (16 train subjects, 4 validation subjects, 4 test subjects).
2. **Prohibited Practices:**
   - Random shuffling of 10-second windows across train/val/test splits is strictly forbidden.
   - Normalization statistics must be calculated strictly per-window or derived exclusively from the training subject pool.

---

## 14. Comprehensive Artifact Register

All generated Phase 3 artifacts are stored in `outputs/phase3/run_001/`:

| Artifact Path | Format | Description |
| :--- | :---: | :--- |
| `run_manifest.json` | JSON | Run metadata, environment versions, gate statuses, blocker description |
| `synchronization_manifest.csv` | CSV | 48 recording pair synchronization parameters and timing confidence |
| `synchronization_audit.md` | MD | Audit report on timing conventions, clock status, and duration checks |
| `ecg_quality_manifest.csv` | CSV | ECG NaN patterns, interpolation eligibility, and SQI metrics |
| `rpeak_detection_summary.csv` | CSV | Pan-Tompkins R-peak detection statistics and HR summary |
| `ecg_quality_report.md` | MD | Summary report on delimiter NaNs and SQI diagnostic screening |
| `radar_preprocessing_manifest.csv` | CSV | Radar recording filter validation notes and Nyquist bounds |
| `preprocessing_comparison.csv` | CSV | Spectral power and amplitude comparison across 3 filter states |
| `preprocessing_report.md` | MD | Comparative evaluation of candidate 1–20 Hz vs cardiac 0.8–3.0 Hz |
| `window_segmentation_diagnostics.csv` | CSV | Diagnostic window counts (22/rec), tail exclusions, and blocker status |
| `plots/plot1_plot2_radar_preprocessing.png` | PNG | Visual comparison of raw vs candidate 1–20 Hz vs cardiac 0.8–3.0 Hz |
| `plots/plot3_ecg_rpeaks.png` | PNG | Cleaned ECG waveform with Pan-Tompkins detected R-peaks |
| `plots/plot4_ecg_quality_sqi_summary.png` | PNG | Distribution of delimiter NaNs and valid RR coverage percentages |
| `plots/plot5_window_counts.png` | PNG | Bar chart of candidate window counts by subject and condition |
| `plots/plot6_reference_hr_gate_status.png` | PNG | High-visibility warning banner documenting active blocker status |
| `plots/plot7_time_alignment_diagram.png` | PNG | Relative time-alignment diagram illustrating nominal zero-offset model |

---

## 15. Final Gate Verdict & Required User Action

```
+-----------------------------------------------------------------------------------+
|                        PHASE 3 FINAL GATE VERDICT                                 |
+-----------------------------------------------------------------------------------+
| PREFLIGHT PIPELINE STATUS:         SUCCESSFUL & REPRODUCIBLE                      |
| AUTOMATED TEST SUITE:              67 PASSED, 0 FAILED (100%)                     |
| SUPERVISED LABEL GENERATION:       HALTED (BLOCKERS ACTIVE)                       |
| KAN MODEL TRAINING:                NOT STARTED                                    |
+-----------------------------------------------------------------------------------+
```

### Required User Actions to Proceed:
1. **Formally Close Phase 2A Finalization Gate:** Review the Phase 2A consistency findings and confirm closure of the reconciliation gate.
2. **Authorize Supervised Ground-Truth Generation:** Approve the ECG-derived instantaneous reference HR and proposed SQI screening protocol (>85% coverage, <3s max gap) for generating supervised window labels.
3. **Approve Radar Filter Selection:** Confirm the recommended 0.8–3.0 Hz cardiac bandpass filter for downstream KAN window feature extraction.
