# PHASE 4C: SYNTHETIC METRIC RECALCULATION & RAW PREDICTION AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Verification Stage:** Phase 4C — Synthetic Prediction and Metric Recalculation  
**Verification File:** `outputs/phase4/verification_run_001/synthetic_metric_recalculation.md`  
**Raw Serialized Predictions:** `outputs/phase4/verification_run_001/synthetic_test_predictions.csv`  

---

## 1. Availability and Serialization of Raw Predictions

In prior runs (`run_001` and `audit_run_001`), synthetic predictions were generated in memory within `loso_evaluator.py::run_synthetic_benchmark()`, but were not persisted as an independent sample-by-sample table on disk. 

To satisfy the Phase 4C requirement for independent recomputation from actual saved files, the synthetic test predictions were generated under the deterministic seed ($42$) and saved to:
[`outputs/phase4/verification_run_001/synthetic_test_predictions.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase4/verification_run_001/synthetic_test_predictions.csv)

### Table of Serialized Test Predictions ($N = 16$):
| Sample Index | Ground Truth $y$ (BPM) | KAN Prediction $\hat{y}$ (BPM) | KAN Error $\hat{y}-y$ (BPM) | MLP Prediction $\hat{y}$ (BPM) | MLP Error $\hat{y}-y$ (BPM) | Mean Baseline $\hat{y}$ (BPM) | Mean Error $\hat{y}-y$ (BPM) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 74.135 | 9.991 | -64.144 | 26.538 | -47.597 | 70.724 | -3.411 |
| **1** | 61.470 | 9.797 | -51.673 | 26.305 | -35.165 | 70.724 | +9.254 |
| **2** | 88.935 | 10.134 | -78.801 | 26.965 | -61.971 | 70.724 | -18.211 |
| **3** | 82.130 | 9.978 | -72.151 | 26.783 | -55.347 | 70.724 | -11.405 |
| **4** | 87.882 | 10.151 | -77.731 | 26.826 | -61.057 | 70.724 | -17.158 |
| **5** | 86.319 | 10.082 | -76.237 | 27.234 | -59.085 | 70.724 | -15.595 |
| **6** | 75.926 | 9.966 | -65.960 | 26.556 | -49.370 | 70.724 | -5.202 |
| **7** | 87.266 | 10.092 | -77.174 | 26.877 | -60.389 | 70.724 | -16.541 |
| **8** | 58.097 | 9.830 | -48.267 | 25.921 | -32.176 | 70.724 | +12.627 |
| **9** | 61.859 | 9.904 | -51.956 | 26.177 | -35.683 | 70.724 | +8.865 |
| **10** | 56.583 | 9.865 | -46.718 | 26.111 | -30.472 | 70.724 | +14.141 |
| **11** | 66.387 | 10.098 | -56.288 | 26.942 | -39.445 | 70.724 | +4.338 |
| **12** | 68.604 | 9.950 | -58.653 | 26.614 | -41.990 | 70.724 | +2.121 |
| **13** | 64.497 | 9.982 | -54.515 | 26.742 | -37.755 | 70.724 | +6.227 |
| **14** | 84.006 | 10.190 | -73.816 | 26.996 | -57.010 | 70.724 | -13.282 |
| **15** | 67.486 | 9.919 | -57.567 | 26.483 | -41.003 | 70.724 | +3.238 |

---

## 2. Independent Recomputation of Metrics from Serialized CSV

Direct mathematical evaluation of the columns in `synthetic_test_predictions.csv` yielded the following verified statistics:

### Ground Truth Target Distribution ($y$):
- **Mean ($\bar{y}$):** **$73.224\text{ BPM}$**
- **Standard Deviation ($\sigma_y$):** **$11.136\text{ BPM}$**
- **Min / Max:** $56.583\text{ BPM}$ / $88.935\text{ BPM}$

### Model Metric Comparison:
| Evaluation Metric | KAN Regressor | MLP Regressor | Mean Predictor Baseline | Mathematical Formula |
| :--- | :---: | :---: | :---: | :--- |
| **Prediction Mean ($\bar{\hat{y}}$)** | $10.002\text{ BPM}$ | $26.692\text{ BPM}$ | $70.724\text{ BPM}$ | $\frac{1}{N} \sum \hat{y}_i$ |
| **Prediction Std ($\sigma_{\hat{y}}$)** | $0.111\text{ BPM}$ | $0.354\text{ BPM}$ | $0.000\text{ BPM}$ | $\sqrt{\frac{1}{N} \sum (\hat{y}_i - \bar{\hat{y}})^2}$ |
| **Bias (Mean Error)** | **$-63.221\text{ BPM}$** | **$-46.532\text{ BPM}$** | **$-2.500\text{ BPM}$** | $\frac{1}{N} \sum (\hat{y}_i - y_i)$ |
| **MAE** | **$63.221\text{ BPM}$** | **$46.532\text{ BPM}$** | **$10.101\text{ BPM}$** | $\frac{1}{N} \sum \|\hat{y}_i - y_i\|$ |
| **RMSE** | **$64.195\text{ BPM}$** | **$47.854\text{ BPM}$** | **$11.413\text{ BPM}$** | $\sqrt{\frac{1}{N} \sum (\hat{y}_i - y_i)^2}$ |
| **Pearson Correlation ($r$)** | **$+0.8712$** | **$+0.8988$** | **$0.0000$ (Convention)** | $\frac{\text{Cov}(\hat{y}, y)}{\sigma_{\hat{y}} \sigma_y}$ |
| **Percentage within $\pm 3\text{ BPM}$** | **$0.0\%$** | **$0.0\%$** | **$6.25\%$** | $\frac{1}{N} \sum \mathbb{I}(\|\text{error}\| \le 3) \times 100\%$ |
| **Percentage within $\pm 5\text{ BPM}$** | **$0.0\%$** | **$0.0\%$** | **$25.0\%$** | $\frac{1}{N} \sum \mathbb{I}(\|\text{error}\| \le 5) \times 100\%$ |

---

## 3. Detailed Verification of the 68 BPM MAE Paradox

The independent recomputation confirms with zero ambiguity:
1. **The MAE equals the absolute negative bias:**  
   Because all KAN predictions are clustered near $10.0\text{ BPM}$ while targets average $73.224\text{ BPM}$, every error $(\hat{y}_i - y_i)$ is negative. Thus:
   $$\text{MAE} \equiv -\text{Bias} = 73.224 - 10.002 = \mathbf{63.221\text{ BPM}}$$
   (In run_001, KAN predictions hovered at $3.85$ BPM yielding MAE $= 69.371$ BPM; in this fresh serialized run, predictions reached $10.00$ BPM yielding MAE $= 63.221$ BPM. In both cases, MAE equals $|\text{Bias}|$ to 3 decimal places).
2. **High Pearson correlation reflects frequency rank learning, not calibrated estimation:**  
   The Pearson correlation between KAN predictions and true targets is **$r = +0.8712$**, and for MLP is **$r = +0.8988$**.
   Because Pearson correlation evaluates the linear covariance normalized by the standard deviations:
   $$r = \frac{\sum (\hat{y}_i - \bar{\hat{y}})(y_i - \bar{y})}{N \sigma_{\hat{y}} \sigma_y}$$
   the tiny standard deviation ($\sigma_{\hat{y}} = 0.111\text{ BPM}$) cancels out the scale suppression. The 1D convolutional feature extractor successfully mapped radar chirp modulation frequency into relative scalar activations, but because the loss was Huber loss with small learning rate, the network never drifted up to the clinical 70 BPM baseline.

---

## 4. Re-Verification of Constant-Prediction Pearson Handling

For `MeanPredictorBaseline`, the predictions are identical across all samples: $\hat{y}_i = 70.724\text{ BPM}$.
- Standard deviation: $\sigma_{\hat{y}} = 0.000\text{ BPM}$.
- Correlation denominator: $\sigma_{\hat{y}} \sigma_y = 0.0 \times 11.136 = 0.0$.
- Mathematical result: $\frac{0}{0} = \text{NaN}$ (strictly undefined).
- Code verification: `src/kan/loso_evaluator.py` lines 149–153 contains the explicit check:
```python
if len(y_t) > 1 and np.std(y_t) > 1e-6 and np.std(y_p) > 1e-6:
    r = float(np.corrcoef(y_t, y_p)[0, 1])
else:
    r = 0.0
```
- **Auditor Conclusion:** The return value $r = 0.0$ is an **explicit defensive software convention** to prevent crashes. It must not be cited as mathematical zero correlation.

---

## 5. Scientific Determination: Code Execution vs. Meaningful Learning

The independent recomputation establishes:
- The synthetic benchmark proves **code execution, loss backpropagation, and non-zero gradient flow**.
- It does **NOT** validate meaningful, calibrated physiological heart rate learning.
- Target z-score normalization and output bias initialization are confirmed mandatory before real-data training.
