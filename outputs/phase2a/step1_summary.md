# PHASE 2A — STEP 1 SUMMARY REPORT: SYNCHRONIZATION VALIDATION & PREPROCESSING PREPARATION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 2A — Step 1: Pre-Implementation Audit & Technical Validation Inspection  
**Report File:** `outputs/phase2a/step1_summary.md`  
**Date of Audit:** October 2026  
**Auditor Role:** Senior Python Developer & Biomedical Signal-Processing Researcher  
**Status:** **STEP 1 COMPLETE — AWAITING USER APPROVAL PRIOR TO STEP 2**

---

## 1. Project Root Verification & Working Directory Confirmation

- **Expected Project Root:** `kan_radar_HR/`
- **Parent Workspace Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work`
- **Active Working Directory Confirmed:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **Execution Action:** Verified that commands are executed directly within `kan_radar_HR/`. No secondary project or duplicate repository was created.

---

## 2. Existing Project & Dataset Directory Structure

### 2.1 Project Directory (`kan_radar_HR/`)
```
kan_radar_HR/
├── configs/
│   └── audit_config.yaml
├── docs/
├── outputs/
│   ├── phase1_audit/
│   │   ├── audit_summary.md
│   │   ├── candidate_fields.csv
│   │   ├── correction_log.md
│   │   ├── data_quality_report.csv
│   │   ├── file_inventory.csv
│   │   ├── mat_structure_inventory.csv
│   │   ├── phase1_audit.log
│   │   ├── phase1_summary.json
│   │   ├── radar_reference_pairing.csv
│   │   ├── radar_signal_inventory.csv
│   │   ├── reference_inventory.csv
│   │   ├── stage_a_summary.json
│   │   ├── stage_a_summary.md
│   │   ├── subject_recording_inventory.csv
│   │   └── synchronization_audit.csv
│   └── phase2a/
│       └── step1_summary.md (this document)
├── src/
│   ├── audit/
│   └── utils/
├── tests/
│   ├── test_candidate_fields.py
│   ├── test_file_discovery.py
│   ├── test_mat_inspection.py
│   ├── test_matching.py
│   ├── test_same_file_pairing.py
│   ├── test_signal_quality.py
│   └── test_timing_validation.py
├── pytest.ini
├── README.md
└── requirements.txt
```

### 2.2 Dataset Directory (`data/VITALSENSE_120_DATASET/`)
```
data/VITALSENSE_120_DATASET/
├── VS01/ ... VS24/ (24 subject directories)
│   ├── VSxx_Resting.mat           (Radar chest displacement, 40,000 samples @ 333.33 Hz)
│   ├── VSxx_Resting_Mindray.mat   (Reference ECG, HR, Pleth, Resp, 120s duration)
│   ├── VSxx_Apnea.mat             (Radar chest displacement during breath-hold)
│   └── VSxx_Apnea_Mindray.mat     (Reference physiological signals during breath-hold)
├── MANIFEST.TXT                   (6,385 bytes, file inventory list)
├── README.txt                     (8,486 bytes, dataset documentation)
└── Subject Information.xlsx       (35,069 bytes, demographic & signal definitions)
```

---

## 3. Phase 1 Artifact Availability & Test Suite Status

All 15 required Phase 1 audit artifacts are present, verified, and consistent:
1. `file_inventory.csv` (96 MAT files verified across 24 subjects; SHA-256 hashes generated; 30.90 MB total).
2. `mat_structure_inventory.csv` (Complete variable, field, dtype, and shape inventory).
3. `candidate_fields.csv` (Exact field path and dimension mapping for all MAT variables).
4. `radar_signal_inventory.csv` (Confirms `VitalSig` 40,000 samples @ 333.3333 Hz across 48 radar files).
5. `reference_inventory.csv` (Confirms `HR`, `ecg_lead2`, `respiration`, `pleth` across 48 reference files).
6. `radar_reference_pairing.csv` (All 48 pairs categorized as `PROBABLE_MATCH` based on subject/condition alignment).
7. `synchronization_audit.csv` (All 48 pairs categorized as `UNVERIFIED_TIMING`).
8. `data_quality_report.csv` (816 executed checks: 767 passed, 1 warning for VS24 resting respiration duration, 0 failed, 48 unverified timing checks).
9. `subject_recording_inventory.csv` (All 4 distinct subject counts confirmed at exactly 24).
10. `stage_a_summary.json` & `stage_a_summary.md` (Stage A metadata inventory summary).
11. `phase1_summary.json` & `audit_summary.md` (Stage B synthesis and readiness blocker verdict).
12. `correction_log.md` & `phase1_audit.log` (Audit execution log and pairing correction documentation).

**Automated Test Suite Status:**
- Pytest suite executed across 7 test modules: **32 passed in 12.28s (100% pass rate)**.
- Validates file integrity, candidate fields, MAT parsing, pairing rules, signal quality, and timing checks.

---

## 4. Dataset Documentation Findings

Comprehensive inspection of `README.txt`, `MANIFEST.TXT`, and `Subject Information.xlsx` revealed:

### 4.1 `README.txt`
- **Experimental Setup:** Custom noncommercial 120-GHz FMCW radar developed by CommSensLab-UPC. Operates within the ISM band, delivering millimeter-level displacement sensitivity.
- **Protocol:** 24 healthy subjects recruited under clinical supervision. Each subject underwent two 120-second scenarios:
  1. *Resting:* Normal spontaneous breathing and resting heart activity.
  2. *Apnea:* Voluntary breath-holding to eliminate respiratory thoracic movement.
- **Data Acquisition:** Radar beat signals digitized via high-speed digitizer controlled by a C++ executable. Reference signals simultaneously recorded by a Mindray patient monitor.
- **Reference Code Citation (Line 230):** Mentions technical validation scripts located at the UPC repository `https://github.com/Rc-W024/VS_DATASET`:
  - `TechValidation.m`: Script for synchronization validation and cross-correlation analysis.
  - `VS_separation.m`: Breathing and cardiac signal separation validation.
  - `PlotVS.m`: Multi-modal visualization tool.
  - `Test_speaker.m`: Radar micro-motion displacement extraction validation on a loudspeaker.

### 4.2 `MANIFEST.TXT`
- Authoritative manifest enumerating exactly 96 `.mat` files across folders `VS01` through `VS24`, plus `README.txt`, `Subject Information.xlsx`. Verified 100% match with filesystem inventory.

### 4.3 `Subject Information.xlsx`
- **Sheet 1 (`Subject Info`):** 24 subjects (13 Male, 11 Female). Age range: 20–55 years. Height, weight, and BMI cataloged.
- **Sheet 2 (`Radar Parameters`):**
  - `VitalSig`: Vital signal, unit **`mm`** (chest displacement).
  - `T_frame`: Sampling interval, unit **`s`** ($0.003\text{ s}$).
  - `Radar.fs`: Sampling frequency, unit **`Hz`** ($333.3333\text{ Hz}$).
  - `Radar.t_frame`: Time series vector, unit **`s`**.
- **Sheet 3 (`Reference Parameters`):**
  - `HR`: Heart Rate, unit **`beats per minute`** (`bpm`), dtype `uint8`, 120 samples.
  - `ecg_lead2`: ECG Lead II, unit **`mV`**, 60,000 samples @ $500\text{ Hz}$ (`Fs_ecg`).
  - `ecg_lead3`, `ecg_leadv1`: Auxiliary ECG channels, unit **`mV`** @ $500\text{ Hz}$.
  - `respiration`: Respiratory signal, unitless, 30,720 samples @ $256\text{ Hz}$ (or nominal `Fs_resp = 62.5 Hz`).
  - `pleth`: Photoplethysmography (PPG), unit **`%`**, 7,200 samples @ $60\text{ Hz}$ (or nominal `Fs_pleth = 125 Hz`).
  - `BPS`, `BPM`, `BPD`: Blood pressure metrics, unit **`mmHg`**.

---

## 5. `TechValidation.m` Findings, Analysis, and Critical Limitations

### 5.1 Availability & Location
- **Local Filesystem:** Not included in the downloaded dataset directory `data/VITALSENSE_120_DATASET/`.
- **Source Repository:** Fetched and inspected directly from the authors' public GitHub repository:  
  `https://raw.githubusercontent.com/Rc-W024/VS_DATASET/main/TechValidation.m`
- **Execution State:** **INSPECTED AS READ-ONLY SOURCE CODE. NOT EXECUTED. NOT MODIFIED.**

### 5.2 Algorithm & Logic in `TechValidation.m`
1. **Inputs:** Loads paired files `VSxx_<Scenario>.mat` and `VSxx_<Scenario>_Mindray.mat`.
2. **Signal Extraction:**
   - Radar: `vitalsig = radarData.VitalSig; Radar.fs = radarData.Radar.fs;`
   - Reference: `respiration = refData.respiration; Fs_resp = refData.Fs_resp;`
3. **Resampling:** Both signals are resampled to $2000\text{ Hz}$ ($0.5\text{ ms}$ sample interval):
   - Reference: `respiration_re = resample(respiration, 2000, refData.Fs_resp);`
   - Radar: `[P, Q] = rat(2000 / Radar.fs); vitsig_re = resample(vitalsig, P, Q);`
4. **Cross-Correlation:**
   - Computes full cross-correlation: `[c, lags] = xcorr(respiration_re, vitsig_re);`
   - Peak lag detection: `lag_max = lags(find(c == max(c)));`
   - Millisecond lag: `lag_ms = lag_max * 0.5;`
5. **Reported Author Findings:**
   - Author script computes mean time lags across 24 subjects on the order of a few milliseconds (Resting: mean lag ~few ms; Apnea: mean lag ~few ms; spread within approximately $[-40\text{ ms}, +30\text{ ms}]$).

### 5.3 Critical Assumptions & Scientific Limitations for Heart-Rate Modeling
While `TechValidation.m` provides valuable evidence of gross acquisition synchronization, it exhibits several critical scientific limitations that directly impact Phase 2 KAN model development:

1. **Respiratory-Domain Only (Zero Validation of Cardiac Signals):**  
   The script correlates `respiration` (reference) with `VitalSig` (radar chest displacement). It does **not** evaluate synchronization against `ecg_lead2` or the cardiac ballistocardiogram (BCG) components.
2. **Apnea Scenario Paradox:**  
   During voluntary apnea, chest breathing excursions are suspended. The author script still attempts to cross-correlate `respiration` against `VitalSig` during apnea. In apnea, the reference respiratory signal is near-flat or drifting noise, which makes cross-correlation peak identification ambiguous or susceptible to spurious low-frequency baseline drifts.
3. **Complete Omission of Reference Heart Rate (`HR`):**  
   `TechValidation.m` does **not** examine or synchronize the 120-sample `HR` vector. It provides zero evidence regarding whether `HR[k]` corresponds to second $k$, or whether the Mindray monitor incorporates internal filtering/averaging latency (e.g., 5–10 s sliding window).
4. **Ignored ECG Ground Truth:**  
   The dataset provides high-fidelity 500 Hz Lead II ECG (`ecg_lead2`), which represents the physiological gold standard for cardiac activity. `TechValidation.m` completely ignores the ECG signal.
5. **Peak Polarity Assumption:**  
   The script uses `find(c == max(c))`, assuming strictly positive correlation. In radar displacement sensing, whether chest inhalation causes positive or negative displacement depends on radar antenna orientation and phase unwrapping conventions. A sign inversion could result in false lag estimation.

---

## 6. Verified vs. Unverified Metadata Inventory

| Item | Classification | Source of Evidence | Scientific Caveat / Note |
| :--- | :--- | :--- | :--- |
| **Radar Signal Meaning** | **VERIFIED** | `Subject Information.xlsx`, Sheet 2 (`VitalSig` = `mm`) | Chest surface displacement in millimeters |
| **Radar Sampling Rate** | **VERIFIED** | MAT file `Radar.fs = 333.3333 Hz`, `T_frame = 0.003 s` | Exactly 40,000 samples = 120.0 seconds |
| **Reference ECG Rate** | **VERIFIED** | MAT file `Fs_ecg = 500 Hz`, 60,000 samples | Lead II ECG across all 48 reference files |
| **Reference HR Format** | **VERIFIED** | MAT file `HR` (120 elements, uint8, bpm) | Present in all 48 reference files, no NaNs |
| **Cohort Demographics** | **VERIFIED** | `Subject Information.xlsx`, Sheet 1 | 24 subjects (13 M, 11 F), age 20–55 |
| **Radar/Ref Pairing** | **PROBABLE_MATCH** | Subject folder and scenario filename agreement | Separate MAT files; no internal session UID header |
| **Hardware Trigger Sync** | **UNVERIFIED** | MAT headers lack shared timestamp/clock pulses | Distinct digitizer and monitor hardware clocks |
| **Gross Time Alignment** | **SUPPORTED_BY_CODE** | `TechValidation.m` cross-correlation (~few ms lag) | Respiration-based only; script not yet executed locally |
| **HR Latency / Aggregation** | **UNVERIFIED** | Mindray monitor specifications not in dataset | Unclear if `HR` is instantaneous vs rolling average |
| **Radar Cardiac vs ECG Sync** | **UNVERIFIED** | No prior analysis in audit or author code | Must be evaluated via BCG / R-peak cross-analysis |

---

## 7. Synchronization Blocker Assessment

| Blocker ID | Description | Severity | Impact on KAN Model | Resolution Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **BLK-SYNC-01** | **No Shared Hardware Clock:** Separate acquisition hardware (digitizer vs Mindray) without unified clock channel in MAT files. | **CRITICAL** | Windows extracted from radar cannot be assumed to have identical sub-second timestamps to reference channels. | Validate time lag using cross-correlation before windowing. |
| **BLK-SYNC-02** | **Monitor HR Latency Unknown:** The 120-sample `HR` array may reflect an internal moving average (e.g., 5–10 s delay) rather than instantaneous heart rate. | **CRITICAL** | Supervised KAN labels derived directly from `HR` could have systematic temporal lag, degrading training loss and phase alignment. | Extract gold-standard beat-to-beat HR directly from `ecg_lead2` R-peaks (Pan-Tompkins algorithm) and compare with `HR`. |
| **BLK-SYNC-03** | **Apnea Respiration Decoupling:** `TechValidation.m` correlates respiration, but in Apnea, respiratory motion is near-zero. | **HIGH** | Respiration cross-correlation cannot reliably validate Apnea recordings. | Evaluate cardiac-band radar BCG vs ECG R-peak timing during Apnea. |
| **BLK-SYNC-04** | **VS24 Respiration Truncation:** `VS24_Resting_Mindray.mat` respiration has 30,600 samples (119.53s) instead of 30,720 samples (120.0s). | **LOW** | Minor edge truncation; ECG (60,000) and HR (120) remain complete. | Trim trailing 0.47s or exclude respiratory tail for VS24. |

---

## 8. Preprocessing Prerequisites Prior to Phase 2 Pipeline Implementation

Before any window slicing, filtering, feature extraction, or KAN model training can proceed, the following scientific steps must be prepared:

1. **Python-Native Synchronization Validator:**  
   Implement a clean, reproducible Python module that replicates the cross-correlation methodology of `TechValidation.m` on all 48 pairs to empirically verify the empirical time lag distribution on the local dataset.
2. **ECG R-Peak Ground Truth Pipeline:**  
   Implement Pan-Tompkins / QRS detection on `ecg_lead2` ($500\text{ Hz}$) to compute exact RR intervals and true continuous instantaneous heart rate $HR_{\text{ecg}}(t)$. Compare $HR_{\text{ecg}}(t)$ with the Mindray `HR` array to quantify monitor filter latency.
3. **Dual-Band Radar Decomposition:**  
   Implement bandpass filtering on `VitalSig` ($fs = 333.3333\text{ Hz}$):
   - Respiratory band: $0.1 - 0.5\text{ Hz}$ ($6 - 30\text{ breaths/min}$)
   - Cardiac band: $0.8 - 3.0\text{ Hz}$ ($48 - 180\text{ bpm}$)
4. **Windowing & Label Assignment Specifications:**  
   Define window duration (e.g., 5 s, 10 s, or 15 s) and stride, with rigorous label assignment rules tied to the aligned ground-truth HR.

---

## 9. Missing Information & Unresolved Questions

1. **Mindray Manufacturer Proprietary Filter:** The exact mathematical transfer function / window length used by the Mindray monitor to compute the scalar integer `HR` value is undocumented in the dataset.
2. **Local Inclusion of Author Validation Scripts:** `TechValidation.m` and `VS_separation.m` were not packaged in the distributed zip archive and exist only on GitHub.
3. **Absolute Start Time Synchronization:** Did the operator press "Start" simultaneously on both machines via software trigger, or was there human trigger latency? (Author reported lags of $[-40\text{ ms}, +30\text{ ms}]$ suggest automated or tight manual trigger, which must be verified).

---

## 10. Recommended Next Steps (Step 2 Planning)

Following user review and explicit approval of this Step 1 summary:

1. **Develop Synchronization Validation Script (`src/preprocessing/sync_validator.py`):**
   - Implement respiration-based cross-correlation following author specifications.
   - Run across all 48 pairs and export `outputs/phase2a/sync_validation_results.csv`.
2. **Develop ECG R-Peak Reference Extractor (`src/preprocessing/ecg_extractor.py`):**
   - Detect QRS complexes from `ecg_lead2`.
   - Calculate instantaneous HR and evaluate cross-correlation between radar BCG and ECG R-peaks.
3. **Formulate Subject Splitting Strategy:**
   - Define subject-independent cross-validation folds (e.g., 5-fold cross-subject split across the 24 subjects, preventing data leakage).
4. **Prepare Preprocessing Pipeline Specification:**
   - Document formal filter specifications, window sizes, and normalization procedures.

---

## 11. Scientific Safety & Compliance Statement

- **No Dataset Modification:** Original files in `data/VITALSENSE_120_DATASET/` were strictly preserved; no files were modified, moved, renamed, or deleted.
- **No Data Fabrication:** All metrics, sampling rates, sample counts, and script behaviors were extracted directly from verified physical files and authentic author source code.
- **No Model Training Executed:** Zero models, training loops, neural networks, or feature matrices were generated or executed during Step 1.
- **Strict Phase Gating:** Phase 2A Step 1 is hereby concluded. Progression to Step 2 remains blocked pending explicit user authorization.

---
`PHASE 2A STEP 1 COMPLETE — WAITING FOR USER REVIEW`
