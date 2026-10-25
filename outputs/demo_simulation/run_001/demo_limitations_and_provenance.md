# PHASE 8 DEMO LIMITATIONS, PROVENANCE, AND REGULATORY DISCLAIMERS

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 8 — Recorded Radar Data Streaming Simulation  
**Document:** System Limitations, Provenance, and Research Governance Disclaimers  
**Run Directory:** `outputs/demo_simulation/run_001/`  
**Execution Date:** 2026-10-18  

---

## 1. Scope & Primary Provenance Distinction

The software provided in Phase 8 is a **deterministic recorded-data playback simulation**. It is strictly designed to replay recorded `.mat` files from the VITALSENSE 120-GHz radar dataset to illustrate the end-to-end signal streaming, windowing, and inference architecture.

### Primary Distinctions:
1. **No Live Radar Hardware Attached:** The system does not interface with a physical Infineon/Texas Instruments 120-GHz FMCW radar transceiver, USB serial bus, or SPI raw ADC capture board.
2. **Software Virtual Clock:** Playback time is driven by a software timer advancing through pre-recorded sample arrays.
3. **No Clinical Status:** This software is an academic engineering prototype and is neither certified nor suitable for clinical diagnosis, patient monitoring, or therapeutic decision-making.

---

## 2. Hardware Timing & Synchronization Limitations

### 2.1 The `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` Status
As established in Phase 2A, Phase 3, and Phase 7 audits:
- The VITALSENSE dataset recordings lack microsecond-accurate hardware trigger timestamps between the radar sensor and the Mindray ECG reference device.
- The radar start time is recorded under the nominal convention:
  $$t_0 = 0.0\text{ s at index } 0$$
- This assumption is designated across the codebase as `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.
- The streaming simulation replicates this nominal timeline for visualization. It does not resolve historical hardware clock drift, sensor startup latency, or physiological pulse transit time (PTT) between thoracic radar displacement and the ECG R-peak.

---

## 3. Signal Processing & Causal Filter Limitations

### 3.1 Non-Causal Zero-Phase Bandpass Filtering
- **Implementation:** The demo applies a 3rd-order Butterworth bandpass filter ($0.8\text{--}3.0\text{ Hz}$) using `scipy.signal.filtfilt`.
- **Limitation:** `filtfilt` operates forward and backward across the signal array, which eliminates nonlinear phase distortion but is **strictly non-causal** (it uses future samples).
- **Live Hardware Translation:** In a true physical deployment with live hardware streaming, filtering must be performed causally (forward-only IIR or linear-phase FIR with group delay compensation). Causal filtering will introduce a small phase lag not present in this pre-filtered replay demonstration.

### 3.2 Rolling Window Latency
- The system segments data into 10.0-second rolling windows with a 5.0-second hop.
- An inherent latency of 10.0 seconds is required before the first window ($k=0$) can be formed and evaluated. Subsequent updates occur at 5.0-second intervals.

---

## 4. Model Inference Limitations & Mode A Governance

### 4.1 Absence of Trained Checkpoints (Mode A Active)
- **Status:** The Phase 2A Finalization Gate (`outputs/phase2a/step2b_consistency_audit.md`) remains officially **`OPEN`** (`RECONCILIATION PARTIAL — FINALIZATION GATE NOT YET APPROVED`).
- **Research Integrity Rule:** Under mandatory research integrity rules, real-data model training on VITALSENSE recordings cannot proceed without explicit authorization from the human principal investigator.
- **Consequence:** Zero trained model checkpoints exist in the repository. The application operates in **Mode A: Visualization Only**.
- **User-Facing Behavior:** The user interface explicitly displays `HR PREDICTION: NOT AVAILABLE` and `MODEL UNAVAILABLE (MODE A)`. The application strictly refuses to synthesize random BPM numbers (e.g. 72 BPM) or pass off mock heuristics as measured radar estimates.

### 4.2 Transition to Mode B
When real-data training is authorized and completed in a future phase:
- The pre-built `SafeModelInferenceEngine` will load the authorized `.keras` / `.h5` checkpoint.
- The UI will seamlessly transition to displaying real-time BPM estimates, confidence bounds, and KAN feature representations.

---

## 5. Summary of Regulatory & Ethical Disclaimers

The following disclosures are embedded permanently within the demo UI, REST API metadata, and exported session logs:

1. **Academic Demonstration Only:** Created solely for evaluating algorithmic workflows and user interface responsiveness.
2. **Not a Medical Device:** Has not received regulatory clearance (e.g., FDA 510(k), CE mark, or MHRA approval).
3. **No Diagnostic Reliability:** Heart rate displays must not be used to detect arrhythmias, tachycardia, bradycardia, or apnea in clinical contexts.
4. **Reproducibility Guarantee:** All session parameters, window indices, and data paths are logged to deterministic JSON/CSV files in `outputs/demo_simulation/run_001/`.
