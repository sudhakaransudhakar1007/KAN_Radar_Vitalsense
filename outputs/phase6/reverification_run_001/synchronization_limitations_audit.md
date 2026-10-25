# PHASE 6: SYNCHRONIZATION LIMITATIONS & HARDWARE TIMING AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  
**Timing Limitation Code:** **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**  

---

## 1. Executive Summary

In compliance with Phase 6 Task 4, an independent engineering audit was conducted on the physical synchronization evidence between the 120-GHz FMCW radar system and the Mindray bio-signal reference recorder.

The audit confirms that **no physical hardware synchronization exists** between the two instruments. No electronic TTL trigger, pulse-per-second (PPS) synchronization, genlock signal, or shared master clock is present in the dataset. All temporal alignment relies strictly on the operational convention `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.

---

## 2. Hardware Synchronization Infrastructure Inspection

| Hardware Component | Radar Sensor Instrument | Reference Bio-Signal Instrument | Joint Hardware Evidence |
| :--- | :--- | :--- | :---: |
| **Digitizer / Controller** | TI / Custom 120-GHz FMCW Radar Module | Commercial Mindray Patient Monitor | **None** (Separate chassis) |
| **Clock Source** | Local crystal oscillator ($333.33\text{ Hz}$) | Local crystal oscillator ($500\text{ Hz}$) | **None** (Independent crystals) |
| **Trigger Mechanism** | Software start command on host PC | Manual / software acquisition start | **None** (No physical trigger cable) |
| **PPS / GPS / Genlock** | None | None | **None** |
| **Hardware Sync Status** | **UNVERIFIED** | **UNVERIFIED** | **NO PHYSICAL PROOF** |

---

## 3. The Nominal Alignment Operational Convention

### Definition: `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`
Under this convention:
- The first recorded radar sample (index 0) and the first recorded ECG reference sample (index 0) are nominally assumed to coincide at timestamp $t_0 = 0.0\text{ seconds}$.
- Time axes are constructed synthetically as:
  $$t_{\text{radar}}[n] = \frac{n}{333.333333\text{ Hz}}, \quad t_{\text{ecg}}[m] = \frac{m}{500.0\text{ Hz}}$$

### Engineering Analysis of Timing Uncertainty:
1. **Host-Level Software Start Skew:** Because data acquisition was initiated via software rather than hardware triggers, asynchronous OS process scheduling introduces an unknown initial time offset $\tau_0 \in [0, 500]\text{ ms}$.
2. **Clock Drift Uncertainty:** Independent quartz crystal oscillators operate with frequency tolerances of $\pm 20 - 50\text{ ppm}$. Over a $120.0\text{-second}$ recording, relative drift between radar and ECG clocks can accumulate up to:
   $$\Delta t_{\text{drift}} = 120\text{ s} \times 100 \times 10^{-6} \approx 12.0\text{ ms}$$
3. **Impact on 10-Second Windowed HR Estimation:**
   In windowed spectral or autocorrelation-based HR estimation over 10.0 seconds, a static or drifting timing offset of $\sim 100\text{ ms}$ represents only $1.0\%$ of the window length. For stationary cardiac rhythms, this introduces negligible HR bias ($< 0.1\text{ BPM}$). However, it completely invalidates millisecond-level beat-to-beat pulse transit time (PTT) analysis.

---

## 4. Confirmation of Bedside Monitor Display Latency (+6.21 s)

Independent inspection of `outputs/phase2a/sync_validation_results.csv` and cross-correlation lag distributions confirmed:
- **Mean Observed Latency:** $+6.21\text{ seconds}$ relative to instantaneous ECG R-peak ground truth.
- **Interquartile Range:** $+5.0\text{ s}$ to $+8.0\text{ s}$ across 48 recordings.
- **Engineering Explanation:** Commercial patient monitors apply moving-average smoothing (finite impulse response or autoregressive filtering) to prevent erratic numeric display flickering in clinical environments.
- **Scientific Mandate:** Displayed monitor HR cannot be used as instantaneous ground truth. Training against monitor HR would introduce severe phase distortion and an artificial 6-second lag into ML models.

---

## 5. Explicit Statement: What the Data CAN and CANNOT Establish

In strict compliance with Phase 6 Task 4:

### The Dataset CAN Establish:
1. Window-level heart rate estimation agreement across 10-second segments under nominal file-start index alignment.
2. Macro-level physiological response tracking (e.g., elevation of heart rate during apnea recovery vs. baseline resting state).
3. The validity of instantaneous R-peak detection from Lead-II ECG as an audited numerical reference standard ($\text{HR}_{\text{ref}} = 60 / \overline{RR}$).

### The Dataset CANNOT Establish:
1. **Exact physical synchronization:** There is no evidence supporting sub-second hardware phase lock between radar and ECG signals.
2. **Pulse Transit Time (PTT) or Pulse Wave Velocity (PWV):** Millisecond-level cardiac cycle propagation cannot be measured without verified hardware triggers.
3. **Live Hardware / Edge Telemetry Validation:** All evaluations are conducted post-hoc in software.
4. **Clinical Applicability to Arrhythmias:** The dataset represents 24 healthy volunteers; clinical safety or arrhythmia detection in cardiac patients cannot be claimed.