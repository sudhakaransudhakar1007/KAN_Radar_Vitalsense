# PHASE 5: MODEL COMPLEXITY, TRAINABLE PARAMETERS & INFERENCE LATENCY

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

To assess edge-computing feasibility and hardware deployability for continuous non-contact physiological monitoring, an empirical benchmark of model capacity (parameter count, memory footprint) and single-window inference latency was performed on the host CPU.

All models exhibit ultra-compact architectures ($< 5,000$ trainable parameters) and sub-3 millisecond single-sample inference times. With a 5.0-second window stride ($\Delta t_{\text{stride}} = 5,000\text{ ms}$), the Real-Time Factor (RTF) for the proposed KAN framework is **$0.00047$**, consuming less than $0.05\%$ of available CPU budget per update.

---

## 2. Experimental Measurement Protocol

- **Hardware Platform:** Host CPU (Intel/AMD x86_64 architecture).
- **Execution Runtime:** Python 3.10.11, TensorFlow 2.x / Keras on single-thread/CPU execution.
- **Timing Protocol:**
  - Warmup: 50 untimed inference passes to prime instruction caches and runtime buffers.
  - Timed Runs: 200 consecutive single-window forward passes.
  - Measurement: High-resolution monotonic wall-clock timing via `time.perf_counter()`.
  - Input batch size: $B = 1$ (simulating live real-time single-window streaming).
- **Input Dimensions:**
  - Feature-based inputs (`KANFeatureRegressor`, `MLPRegressor` head): $1 \times 16$ latent float32 features.
  - End-to-end radar window inputs (`KANRegressor`, `CNNRegressor`, `MLPRegressor`): $1 \times 3,333$ filtered radar displacement samples.

---

## 3. Empirical Model Complexity & Latency Results

| Model Architecture | Input Modality | Trainable Parameters | Float32 Weight Memory | Mean CPU Latency (ms) | Peak Throughput (windows/s) | Real-Time Factor (RTF)* |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **KANRegressor** (Proposed) | Raw Radar (3,333) | **4,720** | **18.88 KB** | **2.368 ms** | 422.3 | $0.00047$ |
| **KANFeatureRegressor** | 16 Latent Features | **1,360** | **5.44 KB** | **1.142 ms** | 875.6 | $0.00023$ |
| **MLPRegressor** (Baseline) | Raw Radar (3,333) | **3,505** | **14.02 KB** | **1.360 ms** | 735.3 | $0.00027$ |
| **CNNRegressor** (Baseline) | Raw Radar (3,333) | **3,377** | **13.51 KB** | **1.123 ms** | 890.5 | $0.00022$ |
| **MeanPredictor** (Sanity) | Summary Statistic | **0** | **0.00 KB** | **0.002 ms** | >100,000 | $< 0.000001$ |
| **Classical Autocorrelation** | Temporal Signal | 0 | 0.00 KB | *Unimplemented* | *Unimplemented* | *N/A* |

*\*Real-Time Factor (RTF) is defined relative to the 5.0-second window stride: $\text{RTF} = \frac{\text{Latency (s)}}{5.0\text{ s}}$. An $\text{RTF} \ll 1.0$ indicates real-time capability with negligible processor overhead.*

---

## 4. Architectural Capacity Analysis

### A. Parameter Breakdown by Subsystem
1. **Shared Convolutional Feature Extractor (`ConvFeatureExtractor`):**
   - Conv1 (8 filters, $k=15$): $8 \times 15 \times 1 + 8 = 128$ weights.
   - Conv2 (16 filters, $k=11$): $16 \times 11 \times 8 + 16 = 1,424$ weights.
   - Conv3 (16 filters, $k=7$): $16 \times 7 \times 16 + 16 = 1,808$ weights.
   - Subtotal Backbone: **3,360 parameters**.
2. **KAN Regression Head (`KANFeatureRegressor`):**
   - Layer 1 (`KANLayer(16, 8)`):
     - `w_base`: $8 \times 16 = 128$
     - `w_spline`: $8 \times 16 = 128$
     - `spline_coeffs`: $8 \times 16 \times 8 = 1,024$
     - Subtotal: $1,280$
   - Layer 2 (`KANLayer(8, 1)`):
     - `w_base`: $1 \times 8 = 8$
     - `w_spline`: $1 \times 8 = 8$
     - `spline_coeffs`: $1 \times 8 \times 8 = 64$
     - Subtotal: $80$
   - Subtotal KAN Head: **1,360 parameters**.
3. **Total KANRegressor:** $3,360 + 1,360 =$ **4,720 parameters**.

### B. Computational Comparison
- The KAN regressor introduces a modest $34.6\%$ parameter increase over the MLP baseline ($4,720$ vs $3,505$) and $39.8\%$ over the CNN baseline ($4,720$ vs $3,377$).
- The CPU inference latency of KAN ($2.368\text{ ms}$) is $1.74\times$ that of MLP ($1.360\text{ ms}$), reflecting the piecewise evaluation of cubic B-spline polynomials. However, in absolute terms, $2.368\text{ ms}$ is imperceptible in real-time physiological monitoring, leaving $99.95\%$ of processor time available for display, wireless transmission, or multi-sensor processing.
