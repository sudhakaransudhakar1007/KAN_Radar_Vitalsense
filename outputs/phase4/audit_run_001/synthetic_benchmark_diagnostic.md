# PHASE 4B: SYNTHETIC BENCHMARK DIAGNOSTIC & NUMERICAL AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Audit Stage:** Phase 4B — Targeted Benchmark Diagnostic  
**Audit File:** `outputs/phase4/audit_run_001/synthetic_benchmark_diagnostic.md`  

---

## 1. Problem Statement: The High-Correlation vs. High-MAE Paradox

In the Phase 4 initial synthetic benchmark run (`outputs/phase4/run_001/baseline_comparison_report.md`), the evaluation metrics showed:
- **MLP Regressor:** $\text{MAE} = 50.572\text{ to } 67.727\text{ BPM}$, $\text{Pearson } r = 0.9188\text{ to } 0.9328$.
- **KAN Regressor:** $\text{MAE} = 68.600\text{ to } 68.924\text{ BPM}$, $\text{Pearson } r = -0.7632\text{ to } 0.8370$.
- **Mean Predictor Baseline:** $\text{MAE} = 10.101\text{ BPM}$, $\text{Pearson } r = 0.0$.

At first glance, an MAE of $\approx 68\text{ BPM}$ alongside a Pearson correlation of $r > 0.85$ appears paradoxical. In clinical and machine learning audits, such a pattern warrants immediate investigation to distinguish mathematical artifacts from software defects.

---

## 2. Independent Empirical Diagnostic Results

An independent scratch re-execution of the synthetic training loop with seed 42 yielded the following exact values:

### A. Ground Truth Target Statistics:
- **Sample Count:** 16 test windows (derived from 64 total synthetic samples).
- **Target Range:** $[56.58, 88.94]\text{ BPM}$.
- **Target Mean ($\mu_y$):** $73.224\text{ BPM}$.
- **Target Standard Deviation ($\sigma_y$):** $11.136\text{ BPM}$.

### B. Model Predictions After 5 Epochs:
- **KAN Predictions:**
  - Range: $[3.784, 3.902]\text{ BPM}$
  - Mean ($\mu_{\hat{y}}$): **$3.853\text{ BPM}$**
  - Standard Deviation ($\sigma_{\hat{y}}$): **$0.0386\text{ BPM}$**
- **MLP Predictions:**
  - Range: $[17.528, 18.081]\text{ BPM}$
  - Mean ($\mu_{\hat{y}}$): **$17.882\text{ BPM}$**
  - Standard Deviation ($\sigma_{\hat{y}}$): **$0.1513\text{ BPM}$**

### C. Bias, Error, and Metric Breakdown:
| Metric | KAN Regressor | MLP Regressor | Mean Predictor Baseline | Formula / Definition |
| :--- | :--- | :--- | :--- | :--- |
| **Prediction Mean** | $3.853\text{ BPM}$ | $17.882\text{ BPM}$ | $70.724\text{ BPM}$ | $\bar{\hat{y}} = \frac{1}{N} \sum \hat{y}_i$ |
| **Target Mean** | $73.224\text{ BPM}$ | $73.224\text{ BPM}$ | $73.224\text{ BPM}$ | $\bar{y} = \frac{1}{N} \sum y_i$ |
| **Bias (Mean Error)** | **$-69.371\text{ BPM}$** | **$-55.342\text{ BPM}$** | **$-2.500\text{ BPM}$** | $\text{Bias} = \frac{1}{N} \sum (\hat{y}_i - y_i)$ |
| **MAE** | **$69.371\text{ BPM}$** | **$55.342\text{ BPM}$** | **$10.101\text{ BPM}$** | $\text{MAE} = \frac{1}{N} \sum \|\hat{y}_i - y_i\|$ |
| **RMSE** | **$69.818\text{ BPM}$** | **$56.402\text{ BPM}$** | **$11.413\text{ BPM}$** | $\text{RMSE} = \sqrt{\frac{1}{N} \sum (\hat{y}_i - y_i)^2}$ |
| **Pearson $r$** | **$-0.7632$ / $+0.8370$** | **$+0.9328$** | **$0.0000$ (Convention)** | $r = \frac{\sum (\hat{y}_i - \bar{\hat{y}})(y_i - \bar{y})}{\sqrt{\sum (\hat{y}_i - \bar{\hat{y}})^2 \sum (y_i - \bar{y})^2}}$ |
| **$\pm 3\text{ BPM}$ Pct** | **$0.0\%$** | **$0.0\%$** | **$6.25\%$** | $\frac{1}{N} \sum \mathbb{I}(\|\hat{y}_i - y_i\| \le 3) \times 100\%$ |
| **$\pm 5\text{ BPM}$ Pct** | **$0.0\%$** | **$0.0\%$** | **$25.0\%$** | $\frac{1}{N} \sum \mathbb{I}(\|\hat{y}_i - y_i\| \le 5) \times 100\%$ |

---

## 3. Mathematical Explanation of the Paradox

### 1. Why is the MAE around 55 to 69 BPM?
Because the models were initialized with standard near-zero weights (Glorot uniform and $\mathcal{N}(0, 0.1)$), their initial predictions $\hat{y}_0$ were close to $0.0\text{ BPM}$.
During training:
- The Huber loss ($\delta = 1.0$) was applied directly to unnormalized physiological targets ($y \in [55, 90]\text{ BPM}$).
- For any prediction where $|y - \hat{y}| > 1.0$, the gradient of the Huber loss is clipped to exactly $\text{sign}(\hat{y} - y) = -1.0$.
- With learning rate $\eta = 0.005$, batch size 16, and only 3 updates per epoch across 5 epochs (15 gradient steps total), the maximum theoretical displacement the network could accumulate is:
$$\Delta \hat{y}_{\text{max}} \approx 15 \times 0.005 \times \text{gain} \approx 0.075 - 18\text{ BPM}$$
- Consequently:
  - The KAN regressor moved from $\approx 0\text{ BPM}$ to **$3.85\text{ BPM}$**.
  - The MLP regressor moved from $\approx 0\text{ BPM}$ to **$17.88\text{ BPM}$**.
- Since every prediction is strictly smaller than the minimum target ($3.85 < 56.58$), the absolute error $|\hat{y}_i - y_i|$ is identically $(y_i - \hat{y}_i)$. Therefore:
$$\text{MAE} \equiv |\text{Bias}| = 73.224 - 3.853 = \mathbf{69.371\text{ BPM}}$$

### 2. Why is Pearson Correlation High?
Pearson correlation is defined as:
$$r = \frac{\text{Cov}(\hat{y}, y)}{\sigma_{\hat{y}} \sigma_y}$$
A fundamental mathematical property of Pearson correlation is **scale and translation invariance**:
$$r(\alpha \hat{y} + \beta, y) = r(\hat{y}, y) \quad \forall \alpha > 0, \beta \in \mathbb{R}$$
Even though $\hat{y}$ only spans $[17.53, 18.08]\text{ BPM}$ ($\sigma_{\hat{y}} = 0.151\text{ BPM}$), the 1D convolutional feature extractor successfully learned an internal filter correlating with the cardiac Doppler carrier frequency. Higher cardiac frequencies produced slightly higher latent activations. Dividing by the tiny standard deviation $\sigma_{\hat{y}}$ scaled this monotonic ordering into a high correlation coefficient ($r = 0.9328$).
In short: **the network learned the relative ranking of frequencies, but never converged on the absolute DC scale of heart rate.**

---

## 4. Handling Constant Predictions (Mean Predictor Baseline)

For `MeanPredictorBaseline`, the model predicts the training set mean $\hat{y}_i = \bar{y}_{\text{train}} = 70.724\text{ BPM}$ for every test window.
- The variance of predictions is $\sigma_{\hat{y}}^2 = \frac{1}{N} \sum (\bar{y}_{\text{train}} - \bar{y}_{\text{train}})^2 = 0.0$.
- The denominator of Pearson's $r$ is:
$$\sigma_{\hat{y}} \sigma_y = 0 \times 11.136 = 0$$
- In pure mathematics, Pearson correlation for a constant vector is **undefined ($\frac{0}{0} = \text{NaN}$)**.
- In `src/kan/loso_evaluator.py` (lines 149–153), the code contains an explicit guard:
```python
if len(y_t) > 1 and np.std(y_t) > 1e-6 and np.std(y_p) > 1e-6:
    r = float(np.corrcoef(y_t, y_p)[0, 1])
else:
    r = 0.0
```
- **Auditor Assessment:** Setting $r = 0.0$ when $\sigma_{\hat{y}} \le 10^{-6}$ is a standard programmatic convention to prevent runtime exceptions. However, scientific reports must explicitly state: *"Pearson $r$ is undefined for a constant predictor; $r = 0.0$ is reported by programmatic convention."*

---

## 5. Audit Verdict on the Synthetic Benchmark

**Does the synthetic benchmark validate meaningful learning?**
**NO.** The synthetic benchmark validates **code execution, tensor shape consistency, and backward gradient flow only**. It proves:
1. The KAN layer does not crash during forward or backward passes.
2. Gradients are successfully propagated through the Cox-de Boor B-spline coefficients and linear base weights.
3. The evaluation metric functions compute without syntax errors.

It **does not** prove that the network has learned to estimate heart rate accurately.

### Mandatory Mitigations for Real-Data Supervised Training:
If and when the user authorizes real-data training, the following three architectural enhancements must be implemented:
1. **Target Normalization:** Transform target heart rates using z-score normalization ($z = \frac{y - \mu_{\text{train}}}{\sigma_{\text{train}}}$) or min-max scaling to $[0, 1]$.
2. **Output Layer Bias Initialization:** Initialize the final regression bias/spline offset to $\bar{y}_{\text{train}}$ ($\approx 70\text{ BPM}$) so training starts with zero initial bias.
3. **Loss Function Calibration:** Utilize Mean Squared Error (MSE) or adapt Huber delta $\delta$ to physiological scale, with sufficient training epochs ($\ge 30$) and early stopping.
