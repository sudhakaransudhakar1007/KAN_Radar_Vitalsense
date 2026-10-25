# VITALSENSE Dataset Audit — Stage A Summary Report

## 1. Execution Context
- **Working Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **Dataset Root:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\data\VITALSENSE_120_DATASET`
- **Docs Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\data\VITALSENSE_120_DATASET`
- **Output Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR\outputs\phase1_audit`
- **Dataset Accessible:** YES

## 2. File and Structure Inventory
- **Discovered `.mat` Files:** 96
- **Total Dataset Size:** 30.9 MB (32404660 bytes)
- **Candidate Subject Folders:** 24 (`VS01` to `VS24`)
- **Loader Used:** `scipy.io.loadmat` for all 96 files (0 HDF5 files)
- **Distinct Top-Level MATLAB Structures:**
  1. **Radar Signal Files (48 files):** `MeasurementInfo`, `Radar`, `T_frame`, `VitalSig`
  2. **Mindray Reference Files (48 files):** `BPD`, `BPM`, `BPS`, `Fs_ecg`, `Fs_pleth`, `Fs_resp`, `HR`, `RR`, `ecg_lead2`, `ecg_lead3`, `ecg_leadv1`, `pleth`, `respiration`

## 3. Candidate Field Findings
- **`VitalSig` (Radar Vital Signal):**
  - Shape: `(40000,)`, Dtype: `float64`
  - Documented meaning: Chest displacement vital signal in **millimeters (mm)** (verified in `Subject Information.xlsx`)
- **`Radar.fs` & `T_frame` (Sampling Rate & Interval):**
  - Value: `Radar.fs = 333.3333333333333 Hz`, `T_frame = 0.003 s` (verified in `Subject Information.xlsx`)
  - Calculated Duration: `40000 / 333.3333... = 120.0 seconds` (2 minutes)
- **`HR` (Reference Heart Rate):**
  - Shape: `(120,)`, Dtype: `uint8`, Unit: `beats per minute` (verified in `Subject Information.xlsx`)
  - Nominal Duration: `120 samples @ 1 Hz = 120.0 seconds`
- **Reference Waveforms:**
  - `ecg_lead2`: shape `(60000,)`, `Fs_ecg = 500 Hz` (120 seconds)
  - `pleth`: shape `(7200,)`, `Fs_pleth = 60 Hz` (120 seconds)
  - `respiration`: shape `(30720,)` (VS01-VS23) / `(30600,)` (VS24), `Fs_resp = 256 Hz` (~120 seconds)

## 4. Comparison with Supplied Dataset Hypotheses
| Hypothesis | Hypothesized | Observed | Status |
| :--- | :--- | :--- | :--- |
| Subject Count | ~24 subjects | Exactly 24 subject folders (`VS01`-`VS24`) | **VERIFIED** |
| Scenarios | Resting & Apnea | Both Resting & Apnea present for all 24 subjects | **VERIFIED** |
| Recording Duration | ~4 min per subject | 2 min Resting + 2 min Apnea = 4 min | **VERIFIED** |
| Combined File Size | ~31 MB | 30.90 MB (32,404,660 bytes) | **VERIFIED** |
| Radar Parameters | Folder named `Radar Parameters` | **NO folder exists**; it is a worksheet tab in `Subject Information.xlsx` | **DISCREPANCY (REFUTED)** |
| Radar Field `VitalSig` | Candidate radar field | Present in all 48 radar files; unit `mm` | **VERIFIED** |
| Sampling Rate `Radar.fs` | Candidate sampling rate | Present in all 48 radar files; 333.33 Hz | **VERIFIED** |
| Reference Device `Mindray` | Candidate reference | 48 files named `*_Mindray.mat` | **VERIFIED** |
| Temporal Synchronization | Believed synchronized | Separate files; equal duration (120s), but clock sync unverified | **UNVERIFIED** |

## 5. Critical Discrepancies and Unresolved Issues
1. **Radar Parameters is a Sheet, not a Folder:** The hypothesis assumed a directory named `Radar Parameters`. In reality, it is Sheet 2 inside `Subject Information.xlsx`.
2. **Separate-File Arrangement:** Radar signals (`VSxx_Resting.mat`) and Reference signals (`VSxx_Resting_Mindray.mat`) are stored in separate files, NOT co-located in the same file.
3. **Hardware Synchronization Unverified:** While durations match nominally (120 s), no shared hardware timestamp clock is present in the `.mat` files to verify sub-second alignment.
