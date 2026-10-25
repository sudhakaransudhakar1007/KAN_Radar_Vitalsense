# Recorded Radar Data Demo Simulation — Implementation Plan

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 8 — Recorded Radar Data Demo Simulation  
**Document Path:** `outputs/demo_simulation/run_001/demo_implementation_plan.md`  
**Date:** October 2026  
**Auditor & Deployment Role:** Senior Python Engineer, ML Deployment Engineer, Biomedical Signal-Processing Specialist, & Frontend Developer  

---

## 1. Executive Summary & Objective

The objective of Phase 8 is to implement a reproducible, local **Recorded Radar Data — Streaming Simulation Demo** for the existing KAN heart-rate estimation research project.

The simulation demonstrates the end-to-end data processing workflow:
$$\mathbf{Recorded\ Radar\ Signal} \longrightarrow \mathbf{Streaming\ Buffer} \longrightarrow \mathbf{Rolling\ Window\ (10s)} \longrightarrow \mathbf{Validated\ Preprocessing} \longrightarrow \mathbf{Model\ Inference\ (if\ available)} \longrightarrow \mathbf{Live\ Dashboard\ Update}$$

### Mandatory Honesty & Governance Boundaries:
1. **Simulation Scope:** This is a software replay of recorded VITALSENSE radar signals, **not a live hardware system**. Physical 120-GHz radar transceivers are not connected.
2. **Zero Fabrication:** The system will **never** generate mock, random, or synthetic BPM numbers. Predictions are displayed **only** when a verified, compatible model checkpoint is loaded and executed.
3. **Model Availability Truth:** Because the Phase 2A Finalization Gate remains officially `OPEN` and real-data training was never executed, **zero trained model checkpoints exist in the repository**. The application launches honestly in **Mode A: Visualization Only — Model Unavailable**.
4. **Governance Invariance:** Phase 2A gate remains strictly `OPEN`. Zero real-data training, zero supervised tensor persistence, and zero modifications to historical research outputs (`outputs/phase1-7b/`) will occur.

---

## 2. Phase 0 Baseline Inventory & Stack Selection

| Component | Repository State | Selected Demo Implementation |
| :--- | :--- | :--- |
| **Frontend Stack** | None existed (0 web files) | Interactive HTML5 Canvas/SVG, modern CSS grid, and responsive JavaScript SPA |
| **Backend Stack** | None existed; Flask 3.1.3 installed | Lightweight Flask REST API backend (`src/demo/app.py`) |
| **Data Ingestion** | `src.phase3.mat_loader.RobustMatLoader` | Reused directly; loads `VitalSig` and extracts `Radar.fs` |
| **Authoritative Windowing** | 10.0s duration, 5.0s hop (Phase 7B verified) | 10.0s window ($3,333\text{ samples}$), 5.0s stride ($1,667\text{ samples}$), 22 complete windows |
| **Signal Preprocessing** | `src.phase3.radar_preprocessing.RadarPreprocessor` | Butterworth $0.8 - 3.0\text{ Hz}$ bandpass filter |
| **Model Architectures** | `src.kan.kan_model` (KAN, CNN, MLP, Mean) | `KANRegressor` ($4,720$ params), `CNNRegressor` ($3,377$), `MLPRegressor` ($3,505$) |
| **Model Checkpoints** | None found ($0$ checkpoints) | **Mode A (Visualization Only)** active; inference safely disabled |
| **Governance Status** | `outputs/phase2a/step2b_consistency_audit.md` | Gate is **`OPEN`**; real-data training remains blocked |

---

## 3. System Architecture & Component Design

### 3.1 Simulation Engine (`src/demo/simulation_engine.py`)
- **State Machine:** States: `READY`, `RUNNING`, `PAUSED`, `COMPLETED`, `ERROR`.
- **Clock Independence:** The simulation maintains its own internal virtual clock (`current_sample_idx`, `elapsed_sim_time_s`), decoupled from operating system wall-clock time for deterministic reproducibility.
- **Buffer & Rolling Window Management:**
  - Ingests continuous radar array ($40,000$ samples for 120s recording at $333.3333\text{ Hz}$).
  - Accumulates incoming samples into a streaming buffer.
  - Slices complete 10-second windows ($3,333$ samples). Rejects incomplete windows.
  - Hops forward by 5.0 seconds ($1,667$ samples) per step.
  - Emits window events with exact indices, start/end timestamps, sample counts, and signal slices.

### 3.2 Safe Model Loader & Compatibility Guard (`src/demo/model_loader.py`)
- Inspects checkpoint path, architecture configuration, expected input shape (`(B, 3333)` or `(B, 16)`), preprocessing parameters, and normalization statistics (`TargetNormalizer`).
- If checkpoint is missing, corrupted, or unverified:
  - Disables inference.
  - Sets model status to `MODEL UNAVAILABLE`.
  - Sets prediction status to `HR PREDICTION: NOT AVAILABLE`.
  - Logs exact reason.
- If compatible checkpoint is present:
  - Enables Mode B (Saved-Model Inference).
  - Executes non-gradient forward pass.
  - Applies inverse normalization to obtain physiological BPM.

### 3.3 Backend API (`src/demo/app.py`)
REST Endpoints:
- `GET /api/status`: Returns system mode, governance status, hardware disclaimer, model availability.
- `GET /api/recordings`: Lists available recorded radar files discovered in `data/VITALSENSE_120_DATASET`.
- `POST /api/select`: Loads selected recording, initializes buffer, validates signal metadata.
- `POST /api/control`: Handles `start`, `pause`, `resume`, `reset`, `step`, and speed selection (`0.5x`, `1.0x`, `2.0x`).
- `GET /api/state`: Returns current playback position, window index, buffer snapshot, and latest prediction status.
- `GET /api/history`: Returns table of all processed windows and audit records.

### 3.4 Frontend Research Dashboard (`src/demo/templates/index.html` & `src/demo/static/`)
- **Header:** Title, `RECORDED DATA — SIMULATION` badge, `MODEL UNAVAILABLE` badge, hardware disclaimer.
- **Summary Metric Cards:** Simulation State, Elapsed Time, Current Window, Sampling Rate, Signal Quality, Model Status, Latest HR Estimate, Processing Latency.
- **Main Radar Signal Chart:** Real-time rolling waveform display with highlighted 10-second active window boundaries.
- **Heart-Rate Estimate Chart:** Plots valid model predictions against simulation time; displays empty placeholder state when model is unavailable.
- **Window History Table:** Tabular log of window index, time interval, sample count, processing status, and prediction.
- **Control Panel:** Recording selector dropdown, Start, Pause, Resume, Reset, Step, and Speed selector buttons.

### 3.5 CLI Runner (`src/demo/cli.py`)
- Headless terminal command for running replay simulations, stepping through recordings, and generating verifiable session logs without launching a web browser.

---

## 4. Test Suite Strategy (`tests/test_demo_simulation.py`)

A comprehensive automated test suite will test all critical failure and operational modes:
1. **Data Ingestion Tests:** Valid MAT loading, missing `VitalSig`, invalid sampling rates, non-finite values.
2. **Deterministic Windowing Tests:** Exact 10.0s window length ($3,333$ samples), 5.0s hop ($1,667$ samples), 22 complete windows, trailing tail accounting, zero duplicate or skipped indices.
3. **Simulation Control Tests:** Start, pause, resume, reset, step, duplicate loop prevention, end-of-file halt.
4. **Model Safety Tests:** Missing checkpoint handling, invalid input rejection, inference exception handling, zero training/weight updates during demo inference.
5. **Research Integrity Tests:** Verification that no training functions are invoked, no supervised tensors are exported, no random numbers are generated as HR estimates, and the Phase 2A gate remains unchanged.

---

## 5. Required Deliverables Matrix

All deliverables will be created in `outputs/demo_simulation/run_001/`:
1. `demo_implementation_plan.md` (this file)
2. `demo_architecture.md`
3. `demo_data_and_window_validation.md`
4. `demo_model_inference_compatibility.md`
5. `demo_test_execution_record.md`
6. `demo_limitations_and_provenance.md`
7. `demo_manifest.json`

Plus repository files:
- `src/demo/simulation_engine.py`
- `src/demo/model_loader.py`
- `src/demo/app.py`
- `src/demo/cli.py`
- `src/demo/templates/index.html`
- `src/demo/static/app.js`
- `src/demo/static/app.css`
- `tests/test_demo_simulation.py`
- `DEMO_README.md`
