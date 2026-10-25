# VITALSENSE Dataset Audit — Comprehensive Phase 1 Audit Report

## 1. Executive Summary & Readiness Assessment
- **Overall Dataset Status:** **PHASE 1 COMPLETE — SCIENTIFICALLY AUDITED**
- **Phase 2 Readiness Decision:** **BLOCKED_PENDING_SYNCHRONIZATION_ALIGNMENT**
- **Core Scientific Finding:** The VITALSENSE dataset is physically intact, complete across 24 subjects, and accurately documented in terms of signal types (VitalSig in mm, Radar.fs in Hz). However, because radar and reference monitors were acquired on separate systems without a shared hardware trigger clock in the MAT files, **window-level temporal synchronization remains UNVERIFIED**. Supervised model training in Phase 2 must NOT proceed until a synchronization validation script confirms sub-second alignment.

---

## 2. Evidence Categorization (Strict Scientific Classification)

### 2.1 Verified Facts
1. **Dataset Integrity & File Counts:** Exactly 24 subject directories (`VS01` to `VS24`) containing 96 total `.mat` files (48 radar files and 48 Mindray reference files). Combined file size is exactly 30.90 MB (32,404,660 bytes). All 96 files have verified SHA-256 checksums and load successfully via `scipy.io.loadmat`.
2. **Radar Signal Meaning & Sampling Rate:** `VitalSig` is verified as chest displacement measured in **millimeters (mm)**. `Radar.fs` is verified as $333.3333333333333\text{ Hz}$ ($T_{frame} = 0.003\text{ s}$). Every radar file contains exactly 40,000 samples ($120.0\text{ s}$).
3. **Reference Multimodal Signals:** Every Mindray file contains:
   - `HR`: 120 points, dtype `uint8`, unit `beats per minute` (observed range: [47, 86] bpm across all subjects).
   - `ecg_lead2`: 60,000 samples @ $500\text{ Hz}$ ($120.0\text{ s}$), dtype `float64`, unit `mV`.
   - `pleth`: 7,200 samples @ $60\text{ Hz}$ ($120.0\text{ s}$), dtype `float64`, unit `%`.
   - `respiration`: 30,720 samples @ $256\text{ Hz}$ ($120.0\text{ s}$) for 47 files; 30,600 samples ($119.53\text{ s}$) for `VS24_Resting_Mindray.mat`.
4. **Signal Cleanliness:** 0 NaNs and 0 infinite values across all 48 radar signals and all 48 reference signals. 0 constant or near-constant radar signals. 0 zero-HR dropouts.
5. **Radar Parameters Discrepancy:** The initial hypothesis of a filesystem folder named `Radar Parameters` is **REFUTED**. `Radar Parameters` is Sheet 2 of `Subject Information.xlsx`.

### 2.2 Probable Interpretations
1. **Radar/Reference Pairing:** All 48 pairs are classified as **`PROBABLE_MATCH`**. Radar files and reference files match on subject folder and filename condition (`Resting` / `Apnea`). However, because Mindray files contain no internal session acquisition ID or timestamp header, pairing cannot be classified as `VERIFIED_MATCH`.
2. **Reference HR Update Interval:** The 120 points over 120 seconds probable rate is 1 sample per second ($1\text{ Hz}$ nominal).

### 2.3 Unverified Assumptions
1. **Hardware Clock Synchronization:** While nominal durations equal 120.0s, no microsecond-level hardware trigger clock, shared time vector, or common pulse exists in the MAT files. Synchronization status is **`UNVERIFIED_TIMING`**.
2. **HR Temporal Interpretation:** Whether each `HR` integer value represents an instantaneous beat-to-beat estimate, a 1-second rolling average, or monitor display refresh is **`UNVERIFIED_TEMPORAL_INTERPRETATION`**.

### 2.4 Failed Checks
- **0 File Corruption Failures:** No files failed to read or compute checksums.
- **0 Numerical Failures:** No NaNs, infinite values, or flatline signals detected.

### 2.5 Quality Warnings
- **`VS24_Resting_Mindray.mat`:** Respiration sample count is 30,600 ($119.53\text{ s}$), 120 samples shorter than nominal 120.0s.

### 2.6 Decisions Requiring Manual Review
1. Verification of radar-to-ECG alignment using the technical validation script (`TechValidation.m` referenced in `README.txt`) before window slicing.
2. Decision on whether to derive instantaneous heart-rate ground truth directly from `ecg_lead2` R-peaks (Pan-Tompkins algorithm) rather than relying on the quantized 1-Hz integer `HR` monitor array.

---

## 3. Detailed 12-Category Readiness Assessment

| Category | Status | Supporting Evidence | Unresolved Issue / Blocker | Next Required Action |
| :--- | :--- | :--- | :--- | :--- |
| **1. Dataset Access & Integrity** | **VERIFIED** | 96/96 files accessible, SHA-256 verified, total size 30.90 MB | None | None |
| **2. Recording Inventory** | **VERIFIED** | Exactly 24 subjects, 48 radar, 48 reference files | None | None |
| **3. Radar Signal Field & Meaning** | **VERIFIED** | `VitalSig` (40,000 samples, float64), documented as chest displacement in `mm` | None | None |
| **4. Sampling Frequency & Units** | **VERIFIED** | `Radar.fs = 333.3333 Hz`, `T_frame = 0.003 s`, unit `Hz` | None | None |
| **5. Reference HR Field & Semantics** | **PARTIALLY_VERIFIED** | `HR` present (120 samples, uint8, bpm), no NaNs/dropouts | Aggregation window (instantaneous vs rolling) unverified | Clarify with author script or derive HR from ECG |
| **6. ECG Availability & Quality** | **VERIFIED** | `ecg_lead2` present in all 48 files (60,000 samples @ 500 Hz, 120s) | None | High-quality gold standard for R-peak timing |
| **7. Pairing Evidence** | **PROBABLE_MATCH** | 48/48 pairs match by subject folder and condition | No session timestamp inside Mindray MAT header | Treat as probable; verify via cross-correlation in Phase 2 prep |
| **8. Synchronization Evidence** | **UNVERIFIED_TIMING** | Nominal 120s durations match across all pairs | No shared clock or trigger marker in MAT files | **BLOCKER:** Run synchronization script before window extraction |
| **9. Subject & Condition Completeness**| **VERIFIED** | All 24 subjects have both Resting (2 min) and Apnea (2 min) | None | Full balanced cohort available |
| **10. Signal Quality** | **VERIFIED_WITH_WARNINGS**| 0 NaNs, 0 Infs, dynamic range intact; VS24 resp warning | VS24 respiration has 30,600 samples | Safe for HR analysis (ECG and HR intact) |
| **11. Metadata Consistency** | **VERIFIED** | `Subject Information.xlsx` sheets match array shapes | Excel sheet layout differed from folder hypothesis | Hypotheses reconciled |
| **12. Documentation Completeness** | **VERIFIED** | `README.txt`, `MANIFEST.TXT`, and `Subject Information.xlsx` | GitHub validation scripts need inspection | Review referenced UPC MATLAB validation code |

---

## 4. Subject Recording Inventory Summary
- **Count 1 — Subject Folders Found:** **24** (`VS01` to `VS24`)
- **Count 2 — Subjects with Readable Radar Data:** **24**
- **Count 3 — Subjects with Usable Reference Candidate:** **24** (All have intact HR arrays and 500 Hz ECG)
- **Count 4 — Subjects Potentially Eligible (Provisional):** **24** (Provisional cohort; final eligibility subject to sub-second synchronization verification)

---

## 5. Phase 2 Readiness Decision
**VERDICT: BLOCKED_PENDING_SYNCHRONIZATION_ALIGNMENT**

### Justification:
Kolmogorov-Arnold Network (KAN) model training requires high-precision ground truth labels aligned with FMCW radar chest displacement windows. Because the radar digitizer and the Mindray physiological monitor ran independently without shared hardware clock timestamps in the MAT files, training labels cannot be assigned blindly. Sub-second cross-modal alignment between radar respiration/cardiac traces and Mindray ECG must be established algorithmically prior to training window generation.
