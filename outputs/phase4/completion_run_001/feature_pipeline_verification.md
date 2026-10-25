# PHASE 4D: FEATURE EXTRACTION PIPELINE & KAN INTERFACE VERIFICATION

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 6: Feature Pipeline Verification  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. Feature Representation & Dimensionality Management

Connecting a 10-second raw radar window ($N = 3,333\text{ samples}$) directly into a Kolmogorov-Arnold Network causes catastrophic parameter explosion:
$$\text{Parameters}_{\text{Direct KAN}} = 3333 \times 16 \times (5 + 3) = 426,624\text{ spline parameters}$$
With only 1,029 accepted windows in the dataset, direct spline mapping would severely overfit. 

To resolve this, the architecture utilizes a compact 1D convolutional feature extractor (`ConvFeatureExtractor`) that maps the 3,333-sample waveform into a 16-dimensional physiological latent vector $\mathbf{z} \in \mathbb{R}^{16}$.

### Feature Names and Ordering:
The 16 latent cardiac features are formally exposed via `extractor.feature_names`:
- `cardiac_latent_feat_00` through `cardiac_latent_feat_15`.

---

## 2. Verification of the Dual KAN Interface

The KAN model implementation supports two complementary operational interfaces:

### Interface 1: End-to-End Radar Input Mode (`KANRegressor`)
- **Input Shape:** $(B, 3333)$ or $(B, 3333, 1)$.
- **Execution Flow:** Raw radar window $\to$ `ConvFeatureExtractor` $\to$ latent vector $\mathbf{z} \in \mathbb{R}^{16} \to$ `KANFeatureRegressor` $\to$ scalar prediction $\hat{y}$.
- **Use Case:** End-to-end backpropagation where convolutional filters and spline functions are optimized jointly.

### Interface 2: Compact Feature Vector Mode (`KANFeatureRegressor`)
- **Input Shape:** $(B, 16)$.
- **Execution Flow:** Directly consumes the 16 latent cardiac features without passing through the convolutional layers:
  $$\mathbf{z} \in \mathbb{R}^{16} \xrightarrow{\text{KANLayer}(16 \to 8)} \mathbf{h} \in \mathbb{R}^8 \xrightarrow{\text{KANLayer}(8 \to 1)} \hat{y} \in \mathbb{R}$$
- **Use Case:** Modular feature inspection, spline visualization, interpretability analysis, and decoupling feature extraction from regression.

Both interfaces were verified via automated unit tests in `tests/test_phase4d_completion.py`.

---

## 3. Data Integrity & Leakage Verification

### A. Finite-Value Handling:
- In `src/kan/kan_model.py` (line 58), `tf.debugging.check_numerics` explicitly asserts that the input tensor contains no NaNs or Infs prior to convolution.
- In `KANFeatureRegressor` (line 104), a secondary `tf.debugging.check_numerics` ensures latent features are strictly finite before spline basis evaluation.

### B. Decoupling from ECG Ground Truth:
- The input to `ConvFeatureExtractor` is strictly the non-contact radar Doppler array `VitalSig` filtered in the 0.8–3.0 Hz bandpass.
- **Zero ECG features** enter the radar input pipeline. ECG R-peak timestamps and RR intervals are used exclusively as reference target labels ($y$) during supervised loss calculation.

### C. Training-Fold-Only Feature Processing:
- Feature extraction weights are optimized strictly on the 23 training subjects in each LOSO fold.
- No global feature selection or dimensionality reduction (e.g., PCA, mutual information) is performed across the entire dataset.
- Held-out test fold performance is never consulted during feature extraction or representation learning.
