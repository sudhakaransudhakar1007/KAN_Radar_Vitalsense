# PHASE 5: MODEL ARCHITECTURES & TRAINING HYPERPARAMETER CONFIGURATION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  

---

## 1. Model Architectures & Parameter Specifications

All models were implemented and verified during Phase 4, with architectures audited to ensure fair capacity matching and numerical stability:

### A. Proposed Model: Feature-Based Kolmogorov–Arnold Network (KAN)
- **Class:** `KANRegressor` (`kan_radar_HR.models.kan`)
- **Input Representation:** 14 biomedical engineered features extracted per 10-second radar window:
  - Dominant spectral peak frequency (BPM)
  - Spectral centroid (Hz)
  - Spectral spread / bandwidth (Hz)
  - Spectral skewness and kurtosis
  - Spectral entropy
  - In-band energy ratio (0.8–2.0 Hz vs total band)
  - Autocorrelation peak lag (s)
  - Autocorrelation peak prominence
  - Zero-crossing rate
  - Envelope peak prominence statistics (mean, std)
  - Temporal signal energy and variance
- **Layer Topology:** `[14, 16, 8, 1]`
- **Spline Configuration:**
  - B-spline degree: $k = 3$ (cubic B-splines)
  - Knot grid size: $G = 5$ intervals ($G + k = 8$ basis functions)
  - Grid range: $[-1.0, 1.0]$ with adaptive grid updates disabled for strict determinism
  - Residual base activation: $\text{SiLU}(x) = x \cdot \sigma(x)$
- **Trainable Parameters:** 4,720 parameters.

### B. Baseline Model 1: Multi-Layer Perceptron (MLP)
- **Class:** `MLPRegressor` (`kan_radar_HR.models.mlp`)
- **Input Representation:** Identical 14 biomedical features as KAN.
- **Layer Topology:** `[14, 64, 32, 16, 1]`
- **Activation:** $\text{ReLU}(x) = \max(0, x)$
- **Regularization:** Dropout ($p = 0.1$) and LayerNorm between hidden layers.
- **Trainable Parameters:** 3,505 parameters.

### C. Baseline Model 2: 1D Temporal Convolutional Neural Network (CNN)
- **Class:** `CNNRegressor` (`kan_radar_HR.models.cnn`)
- **Input Representation:** Raw filtered 1D radar displacement window ($1 \times 3,333$ samples).
- **Architecture:**
  - Conv1D Block 1: 8 filters, kernel size 15, stride 2, BatchNorm1d, ReLU, MaxPool1d(2).
  - Conv1D Block 2: 16 filters, kernel size 11, stride 2, BatchNorm1d, ReLU, MaxPool1d(2).
  - Conv1D Block 3: 32 filters, kernel size 7, stride 2, BatchNorm1d, ReLU, AdaptiveAvgPool1d(1).
  - Linear Head: `Linear(32, 16) -> ReLU -> Linear(16, 1)`
- **Trainable Parameters:** 3,377 parameters.

### D. Sanity Baseline: Mean Predictor
- **Class:** `MeanPredictorBaseline` (`kan_radar_HR.models.baselines`)
- **Mechanism:** Predicts the constant mean HR observed in the training fold ($\hat{y} = \mu_{y,\text{train}}$).
- **Trainable Parameters:** 0 parameters.

### E. Classical Baseline: Autocorrelation Peak Tracking
- **Status:** **Explicitly documented implementation gap.**
- **Rationale:** Classical radar autocorrelation peak-tracking without learned priors remains sensitive to respiration harmonics. It is cataloged as an unimplemented baseline until an algorithmic specification and validation protocol are approved.

---

## 2. Training Hyperparameters & Optimization Protocol

To guarantee scientifically rigorous and reproducible comparisons, training hyperparameters are standardized across all neural architectures:

| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| **Loss Function** | Mean Squared Error (MSE) | Computed on Z-score normalized target: $\mathcal{L} = \frac{1}{B}\sum_{i=1}^B (\hat{y}_{\text{norm}, i} - y_{\text{norm}, i})^2$ |
| **Optimizer** | Adam | $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$ |
| **Learning Rate** | $1.0 \times 10^{-3}$ ($0.001$) | Fixed initial learning rate |
| **Weight Decay** | $1.0 \times 10^{-4}$ ($0.0001$) | $L_2$ regularization on weights |
| **Batch Size** | 16 | Mini-batch stochastic gradient descent |
| **Maximum Epochs** | 30 | Upper bound per fold |
| **Early Stopping Metric** | Validation MSE | Monitored on the 3 deterministic validation subjects |
| **Early Stopping Patience**| 7 epochs | Training halts if validation MSE does not improve for 7 consecutive epochs |
| **Best Model Checkpoint** | Minimum Val MSE | Checkpoint restored prior to held-out test inference |
| **Target Normalization** | Z-score ($z = \frac{y - \mu}{\sigma}$) | Estimated strictly on the 20 training subjects |
| **Inference Inversion** | $\hat{y}_{\text{BPM}} = \hat{y} \cdot \sigma + \mu$ | Restores normalized model output to physical BPM scale |
| **Random Seed** | 42 | Fixed for `torch`, `numpy`, and `random` |
| **Execution Hardware** | CPU (x86_64) | Deterministic CPU arithmetic |

---

## 3. Evaluation Metric Definitions

All models will be evaluated on the held-out test subject windows in each fold ($N_{\text{test}} = 1,029$ total windows):

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N}\sum_{i=1}^N \left|\hat{y}_i - y_i\right| \quad (\text{BPM})$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (\hat{y}_i - y_i)^2} \quad (\text{BPM})$$
3. **Mean Bias:**
   $$\text{Bias} = \frac{1}{N}\sum_{i=1}^N (\hat{y}_i - y_i) \quad (\text{BPM})$$
4. **Pearson Correlation Coefficient ($r$):**
   $$r = \frac{\sum_{i=1}^N (\hat{y}_i - \bar{\hat{y}})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^N (\hat{y}_i - \bar{\hat{y}})^2 \sum_{i=1}^N (y_i - \bar{y})^2}}$$
   *(Convention: For constant prediction vectors where standard deviation is zero, such as the Mean Predictor, $r \equiv 0.0$ by documented convention).*
5. **Percentage Within $\pm 3\text{ BPM}$ ($\%_{\le 3\text{BPM}}$):**
   $$\%_{\le 3\text{BPM}} = \frac{1}{N}\sum_{i=1}^N \mathbb{I}(|\hat{y}_i - y_i| \le 3.0) \times 100\%$$
6. **Percentage Within $\pm 5\text{ BPM}$ ($\%_{\le 5\text{BPM}}$):**
   $$\%_{\le 5\text{BPM}} = \frac{1}{N}\sum_{i=1}^N \mathbb{I}(|\hat{y}_i - y_i| \le 5.0) \times 100\%$$
