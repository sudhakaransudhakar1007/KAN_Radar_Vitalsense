# VITALSENSE 120-GHz Radar Recorded Data Streaming Demo

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 8 — Recorded Radar Data Streaming Simulation  
**Implementation Directory:** `src/demo/`  
**Run Artifacts:** `outputs/demo_simulation/run_001/`  

---

## 1. Overview & Objective

This module provides a reproducible, interactive simulation environment that replays recorded 120-GHz FMCW radar signals from the VITALSENSE dataset as if samples were arriving from a continuous real-time stream:

$$\mathbf{Recorded\ Radar\ MAT} \longrightarrow \mathbf{Streaming\ Buffer} \longrightarrow \mathbf{Rolling\ Window\ (10s)} \longrightarrow \mathbf{Validated\ Preprocessing} \longrightarrow \mathbf{Safe\ Inference\ Engine} \longrightarrow \mathbf{Web\ Dashboard}$$

### Mandatory Research Integrity Disclosures
- **Software Replay Only:** Replays pre-recorded data from the VITALSENSE study. It does **not** interface with physical 120-GHz hardware.
- **Phase 2A Gate Open:** The governance gate remains strictly `OPEN` (`outputs/phase2a/step2b_consistency_audit.md`). No real-data model training or supervised tensor export has taken place.
- **Operating Mode A (Visualization Only):** Because no trained model checkpoints exist in the repository, heart rate estimates are displayed as `NOT AVAILABLE`. Random or synthetic BPM values are **never** fabricated.
- **Academic Research Prototype:** Not an FDA/CE cleared medical device; not intended for clinical diagnostic use.

---

## 2. Quick Start Guide

### Prerequisites
The demo utilizes the existing project environment (Python 3.10+):
```powershell
pip install -r requirements.txt
```
*(Flask 3.1+, NumPy, SciPy, and TensorFlow/Keras are the core dependencies).*

### Option 1: Launch Interactive Web Dashboard
Run the Flask server:
```powershell
python -m src.demo.app
```
Then open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

### Option 2: Run Headless CLI Simulation
Replay any recording directly in your PowerShell terminal:
```powershell
# Replay 10 windows of subject VS01 resting recording with live progress:
python -m src.demo.cli --recording VS01_Resting --max-windows 10

# Single-step mode with prompt between windows:
python -m src.demo.cli --recording VS02_Apnea --step-by-step
```
Session metadata and window-level CSV logs are automatically exported to `outputs/demo_simulation/run_001/`.

---

## 3. Web Dashboard Features

The web interface is implemented in pure HTML5, CSS3, and vanilla JavaScript (no external CDN dependencies required):

1. **Governance & Hardware Banners:**
   - Prominently displays the `RECORDED DATA — SIMULATION` disclaimer and the `Phase 2A Gate: OPEN` status badge.
2. **Recording Selector:**
   - Dropdown menu dynamically populated with all **48 recordings** across the **24 VITALSENSE subjects** (both `Resting` and `Apnea` conditions).
3. **Playback Control Bar:**
   - `Start`: Initiates continuous playback driven by the background virtual clock.
   - `Pause` / `Resume`: Halts and resumes streaming at the current sample index.
   - `Reset`: Returns simulation pointers to sample 0, clearing active window history.
   - `Step Window`: Advances exactly one complete 10-second window ($3,333$ samples).
   - `Speed Selector`: Switch between $0.5\times$, $1.0\times$ (real-time nominal), and $2.0\times$ playback rates.
4. **Dual Synchronized Real-Time Canvases:**
   - **Radar Waveform Canvas:** Visualizes raw radar displacement alongside the 3rd-order Butterworth bandpass-filtered signal ($0.8\text{--}3.0\text{ Hz}$). A semi-transparent cursor highlights the active 10-second window.
   - **Heart Rate Trajectory Canvas:** Displays the temporal evolution of HR predictions (prominently watermarked with `MODEL UNAVAILABLE (MODE A)`).
5. **Metric Summary Cards:**
   - Instant readout of current window index, elapsed virtual time, signal quality index (SQI), and active HR estimate.
6. **Session Window Audit Table:**
   - Tabular record of every processed window showing start/end sample indices, exact time ranges, signal quality flags, and model inference status.
7. **Session Export:**
   - One-click `Export Session Data` button flushes full session metadata (`.json`) and window-level audit rows (`.csv`) to disk.

---

## 4. Signal Processing & Windowing Specifications

- **Radar Sampling Frequency:** $f_s = 333.3333\text{ Hz}$ ($T_{\text{frame}} = 0.003\text{ s}$).
- **Window Length:** $T_{\text{win}} = 10.0\text{ s} \longrightarrow 3,333\text{ samples}$.
- **Hop Length:** $T_{\text{hop}} = 5.0\text{ s} \longrightarrow 1,667\text{ samples}$.
- **Complete Windows per Recording:** Exactly 22 complete windows per 120-second recording ($40,000$ samples).
- **Trailing Tail:** $1,660$ samples ($4.98\text{ s}$) at the end of each recording are preserved without zero-padding or silent truncation.
- **Bandpass Filter:** 3rd-order Butterworth zero-phase bandpass filter ($0.8\text{--}3.0\text{ Hz}$, equivalent to $48\text{--}180\text{ BPM}$).

---

## 5. Verification & Automated Tests

To run the automated Phase 8 test suite:
```powershell
pytest tests/test_demo_simulation.py -v
```
To run the complete repository regression test suite (112 tests across all phases):
```powershell
pytest tests/ -v
```

---

## 6. Directory Structure

```
kan_radar_HR/
├── src/
│   └── demo/
│       ├── __init__.py               # Package marker
│       ├── app.py                    # Flask REST application & playback worker
│       ├── cli.py                    # Terminal headless runner
│       ├── model_loader.py           # SafeModelInferenceEngine & zero-fabrication guard
│       ├── simulation_engine.py      # RadarSimulationEngine & rolling buffer FSM
│       ├── static/
│       │   ├── app.css               # Scientific dark-theme styling
│       │   └── app.js                # Frontend streaming & canvas rendering
│       └── templates/
│           └── index.html            # Main dashboard SPA template
├── tests/
│   └── test_demo_simulation.py       # 12 comprehensive automated unit tests
├── outputs/
│   └── demo_simulation/
│       └── run_001/                  # Deliverables, manifests, and session exports
└── DEMO_README.md                    # This document
```
