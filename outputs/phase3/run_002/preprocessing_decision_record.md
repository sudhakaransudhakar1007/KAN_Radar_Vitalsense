# Phase 3 Radar Preprocessing Decision Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_002`  
**Execution Date:** October 15, 2026  
**Status:** `USER_APPROVED_EVIDENCE_BASED`  

---

## 1. Summary of Comparative Filter Evaluation

The Phase 3 preflight evaluated two candidate bandpass filter configurations against unfiltered raw `VitalSig` (phase-demodulated chest-wall displacement signal, $f_s = 333.3333\text{ Hz}$, Nyquist frequency = $166.6667\text{ Hz}$) across all 48 radar recordings:

1. **Raw VitalSig (Baseline):** Unfiltered continuous thoracic surface displacement capturing macro-respiratory motion, micro-ballistocardiographic vibration, and low-frequency postural drift.
2. **Candidate 1.0–20.0 Hz Filter:** 3rd-order zero-phase Butterworth bandpass filter. Captures broadband respiratory harmonics, high-frequency chest wall tremors, and cardiac motion.
3. **Cardiac 0.8–3.0 Hz Filter:** 3rd-order zero-phase Butterworth bandpass filter (corresponding to physiological cardiac rates of 48 to 180 bpm). Designed to isolate the primary fundamental cardiac ballistocardiogram displacement.

---

## 2. Empirical Quantitative Comparison Across All 48 Recordings

| Metric | Raw VitalSig | Candidate 1.0–20.0 Hz Bandpass | Cardiac 0.8–3.0 Hz Bandpass |
| :--- | :---: | :---: | :---: |
| **Mean Cardiac Band Power Ratio (0.8–3.0 Hz)** | **0.0060 (0.60%)** | **0.3911 (39.11%)** | **0.4843 (48.43%)** |
| **Mean Peak-to-Peak Amplitude** | 7.0725 | 0.7979 | 0.8346 |
| **Mean Standard Deviation** | 1.1842 | 0.0891 | 0.0934 |
| **Phase Distortion** | N/A | Zero (filtfilt) | Zero (filtfilt) |
| **Nyquist Bound Compliance** | Valid | Valid ($20.0 < 166.67\text{ Hz}$) | Valid ($3.0 < 166.67\text{ Hz}$) |

---

## 3. Approved Decision & Scientific Boundaries

- **Approved Primary Preprocessing Filter:** **Cardiac 0.8–3.0 Hz Bandpass Filter** (3rd-order zero-phase Butterworth).
- **Approval Justification:** User-approved based on empirical evidence showing an 80-fold increase in relative cardiac spectral power concentration (from 0.60% in raw `VitalSig` to 48.43% in the filtered signal), effectively suppressing out-of-band respiratory baseline wander without introducing phase distortion.
- **Mandatory Scientific Boundary:**
  - Cardiac-band power concentration is **strictly distinguished from downstream heart-rate estimation accuracy**.
  - **No claim is made** that the 0.8–3.0 Hz filter improves KAN, MLP, or CNN prediction accuracy or reduces Mean Absolute Error (MAE) in the absence of empirical downstream model training and validation evidence.
