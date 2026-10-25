# KNOWN LIMITATIONS & SCIENTIFIC SCOPE CONSTRAINTS
## Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals

**Document Generated:** 2026-10-25  
**Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Report Output Path:** [`outputs/project_status/known_limitations.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/project_status/known_limitations.md)  

---

## 1. Hardware Synchronization Constraints

1. **Absence of Shared Clock / Trigger:**
   The VITALSENSE experimental setup utilized an autonomous 120-GHz FMCW radar digitizer and an independent Mindray BeneView T8 clinical patient monitor. There was no shared master clock, hardware TTL trigger, or PPS pulse cable.
2. **Timing Uncertainty Envelope:**
   The composite temporal uncertainty envelope between radar displacement and ECG traces is estimated at **$\pm 100\text{--}300\text{ ms}$** (upper bound **$\pm 500\text{ ms}$**), arising from physiological pulse transit time ($100\text{--}250\text{ ms}$), respiratory cross-correlation plateau ambiguity ($95\text{ ms}$ median), and software recording startup delays ($200\text{--}500\text{ ms}$).
3. **Mandatory Provenance Citation:**
   All ground-truth labels and derived outputs must carry the mandatory limitation label:  
   `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`

---

## 2. Physiological & Clinical Scope Boundaries

1. **Window-Level Cadence vs. Beat-to-Beat Tracking:**
   - **Supported Scope:** Estimating average heart rate over 10.0-second observation windows (aggregating 8–16 cardiac cycles).
   - **Excluded Scope:** Beat-to-beat pulse transit time (PTT) estimation, microsecond pulse wave velocity (PWV) tracking, and sub-second arrhythmia localization. The $\pm 200\text{ ms}$ synchronization uncertainty invalidates beat-to-beat PTT tracking.
2. **Cohort Demographics & Clinical Generalizability:**
   - The VITALSENSE cohort comprises 24 healthy adult volunteers seated quietly in laboratory conditions.
   - The dataset does not evaluate patients with arrhythmias (e.g. atrial fibrillation, frequent premature ventricular contractions), heart failure, pacemakers, or severe tachycardia ($> 185\text{ BPM}$).
   - This framework is **not clinical software** and has not been cleared as a medical diagnostic device.

---

## 3. Physical Sensing & Environmental Limitations

1. **Vulnerability to Macroscopic Motion:**
   The radar detects sub-millimeter chest displacement induced by cardiac apex thrust and arterial pulsation. Macroscopic torso movement, coughing, deep sighing, or limb movement produces phase wrapping and signal clipping that swamps the micro-motion signal.
2. **Offline Software Simulation Notice:**
   The interactive dashboard serves as an offline software replay of pre-recorded data. It does not interface with live radar hardware, and successful dashboard loading does not demonstrate physical live-radar capability.

---

## 4. Dataset-Specific Anomalies

1. **`VS24_Resting_Mindray.mat` Truncation:**
   The respiration reference channel in `VS24_Resting` contains 30,600 samples instead of 30,720 (480 ms short) and uses float codes. This anomaly is restricted to the respiration channel; the ECG Lead II signal contains the full 60,000 intact samples.
2. **Boundary Delimiter NaNs:**
   Minor isolated delimiter NaNs present in Mindray files are cleaned using guarded linear interpolation without introducing boundary distortion.
