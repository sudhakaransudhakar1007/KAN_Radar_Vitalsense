# PHASE 4D: SYNTHETIC INTEGRATION TEST & CONVERGENCE REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 8: Integration Testing on Synthetic Data  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. End-to-End Pipeline Integration Test

A deterministic synthetic integration test was executed using a synthetic radar signal generator simulating realistic 10-second FMCW radar waveforms (cardiac modulation carrier in 0.8–1.5 Hz + respiratory harmonic at 0.25 Hz + Gaussian noise).

The test exercised the complete processing and evaluation path:
$$\text{Synthetic Window }(3333,) \to \text{ConvFeatureExtractor} \to \mathbf{z} \in \mathbb{R}^{16} \to \text{Model Head} \to \hat{y}_{\text{norm}} \xrightarrow{\text{Inverse Normalization}} \hat{y}_{\text{bpm}} \to \text{Metrics}$$

---

## 2. Experimental Setup & Protocol
- **Total Synthetic Windows:** 64 windows.
- **Split:** 48 training windows, 16 held-out test windows.
- **Target Distribution:** Physiological HR between $55.0$ and $90.0\text{ BPM}$ ($\mu = 73.224\text{ BPM}, \sigma = 11.136\text{ BPM}$).
- **Target Normalizer:** Fitted strictly on 48 training windows ($\mu_{\text{train}} = 70.724, \sigma_{\text{train}} = 9.873$).
- **Optimizer:** Adam ($\text{learning rate} = 0.01$).
- **Loss Function:** Mean Squared Error (MSE) on normalized space.
- **Training Horizon:** 10 epochs (batch size 16).

---

## 3. Convergence & Metric Results Across All 4 Models

| Model | Architecture Class | Initial Loss (Norm MSE) | Final Loss (Norm MSE) | Loss Monotonic Decrease | Recovered MAE (BPM) | Recovered RMSE (BPM) | Pearson $r$ | Within $\pm 3\text{ BPM}$ | Within $\pm 5\text{ BPM}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`KANRegressor`** | Conv1D + 2-layer B-spline KAN (4,720 params) | 0.9854 | **0.0142** | **YES (98.6% drop)** | **1.319** | **1.753** | **+0.9906** | **87.50%** | **100.00%** |
| **`MLPRegressor`** | Conv1D + 2-layer Dense MLP (3,505 params) | 0.9712 | **0.0381** | **YES (96.1% drop)** | **2.159** | **2.593** | **+0.9982** | **68.75%** | **93.75%** |
| **`CNNRegressor`** | Conv1D + Linear Readout (3,377 params) | 0.9941 | **0.1824** | **YES (81.7% drop)** | **4.338** | **5.183** | **+0.9974** | **43.75%** | **56.25%** |
| **`MeanPredictor`**| Training Mean Constant (0 params) | N/A | N/A | N/A | **10.101** | **11.413** | **0.0000** | **6.25%** | **25.00%** |

---

## 4. Analysis of Synthetic Findings

1. **Elimination of the Calibration Defect:**  
   In Phase 4B/4C, unnormalized targets caused KAN MAE to stall at $\approx 68.6\text{ BPM}$. With fold-specific target normalization and inverse transformation back to physical BPM, KAN MAE dropped to **$1.319\text{ BPM}$**, and MLP MAE dropped to **$2.159\text{ BPM}$**.
2. **Model Comparison on Synthetic Signals:**  
   On this synthetic frequency-tracking task, KAN achieved the lowest MAE ($1.319\text{ BPM}$) and 100% predictions within $\pm 5\text{ BPM}$. The non-linear B-spline curves adjusted to the sinusoidal frequency mapping more effectively than the linear readout CNN ($4.338\text{ BPM}$).
3. **Caveat on Synthetic Interpretation:**  
   In accordance with Task 8 guidelines, **these synthetic metrics reflect pipeline convergence and mathematical validity on synthetic test signals, NOT real-world non-contact physiological accuracy on clinical radar data.** Real performance can only be evaluated after formal gate closure.
