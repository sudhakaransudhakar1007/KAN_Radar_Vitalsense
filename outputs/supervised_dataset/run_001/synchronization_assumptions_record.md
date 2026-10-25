# Supervised Dataset Synchronization Assumptions Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Supervised Dataset Generation Implementation  
**Run ID:** `run_001`  
**Execution Date:** October 15, 2026  
**Status:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`  

---

## 1. Physical Hardware Trigger & Timestamp Audit

An exhaustive forensic inspection of the 96 binary MAT files composing the VITALSENSE dataset established the following physical facts:

1. **Absence of Shared Clock & Trigger Channels:**
   - 0 of 48 radar MAT files contain trigger input channels, external sync markers, or hardware time-of-day clock signals.
   - 0 of 48 Mindray reference MAT files contain common-digitizer sync channels, TTL pulses, or Pulse-Per-Second (PPS) inputs.
   - The radar transceiver digitizer and the Mindray physiological monitor operated on independent, uncoupled internal quartz crystal oscillators.

2. **Nominal Zero-Offset Convention ($t_0 = 0.0\text{ s}$):**
   - The supervised window pairing establishes sample-to-sample alignment under the prespecified convention that the first recorded sample of `VitalSig` ($n=0$) and the first recorded sample of `ecg_lead2` ($m=0$) represent $t = 0.000\text{ seconds}$.
   - This convention is an **operational modeling assumption**, not measured or physical proof of zero-latency synchronization.
   - Formally, the confidence status for every paired window is cataloged as **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**.

---

## 2. Cross-Device Duration Matching & Observed Discrepancies

- **Nominal Duration Matching (47 of 48 Pairs):**
  - In 47 of 48 pairs, the nominal recorded durations match at exactly 120.0 seconds:
    - Radar `VitalSig`: 40,000 samples at $f_s = 333.3333\text{ Hz}$ ($40,000 / 333.3333 = 120.000\text{ s}$).
    - Mindray `ecg_lead2`: 60,000 samples at $f_s = 500.0\text{ Hz}$ ($60,000 / 500.0 = 120.000\text{ s}$).
    - Mindray `respiration`: 30,720 samples at $f_s = 256.0\text{ Hz}$ ($30,720 / 256.0 = 120.000\text{ s}$).
    - Mindray `HR`: 120 samples at $f_s = 1.0\text{ Hz}$ ($120 / 1.0 = 120.000\text{ s}$).

- **Empirical Discrepancy in `VS24_Resting`:**
  - `VS24_Resting_Mindray.mat` contains exactly 30,600 respiration samples (instead of 30,720 samples).
  - At the documented sampling rate of 256.0 Hz:
    $$T_{\text{resp}} = \frac{30,600}{256.0} = 119.53125\text{ seconds}$$
  - This represents a discrepancy of **0.46875 seconds** (120 respiration samples) shorter than the nominal 120.0 seconds.
  - The ECG Lead II array in `VS24_Resting_Mindray.mat` contains 60,000 samples ($120.000\text{ s}$), and radar contains 40,000 samples ($120.000\text{ s}$).

---

## 3. Disqualification of Monitor HR Display Array

- Cross-correlation and lag scan between the 120-point Mindray `HR` array and continuous instantaneous ECG-derived HR proved a systematic $+6.21\text{ s}$ average display latency (mode: $+7.0\text{ s}$).
- The monitor `HR` array is permanently disqualified from serving as supervised training targets for 10-second sliding windows.
- All window training targets are derived exclusively from validated instantaneous ECG R-peaks.

---

## 4. Prohibition of Post-Hoc Alignment Shifting

- No in-sample optimized temporal shifts ($\tau \in [-5, +5]\text{ s}$) are applied to the dataset windows.
- Prior Phase 2A diagnostic split testing demonstrated that in-sample lag optimization overfits training windows and degrades performance on held-out test windows.
- All window boundaries adhere strictly to the un-shifted nominal timeline.
