# PHASE 4: BASELINE COMPARISON & SYNTHETIC BENCHMARK REPORT

## 1. Model Theoretical Comparison
| Model | Type | Trainable Params | Inductive Bias | Interpretability |
| :--- | :--- | :--- | :--- | :--- |
| **MeanPredictorBaseline** | Non-parametric | 0 | Stationary mean HR | None (constant) |
| **MLPRegressor** | Deep Linear/ReLU/SiLU | 3,505 | Global hyperplanes | Black-box weights |
| **KANRegressor** | B-Spline Kolmogorov-Arnold | 4,720 | Univariate spline basis | Inspectable 1D splines |

## 2. Synthetic Benchmark Verification Results
To rigorously verify model convergence and metric calculation without bypassing the Phase 2A Gate on real radar data, a 64-sample synthetic benchmark was executed end-to-end:
- **Synthetic Training Samples:** 48
- **Synthetic Testing Samples:** 16
- **KAN Initial Loss $\to$ Final Loss:** 70.0128 $\to$ 66.5966 (Monotonic decrease: `True`)
- **KAN Gradient Flow Verified:** `True` (All spline & linear weights receive non-zero gradients)
- **MLP Initial Loss $\to$ Final Loss:** 70.1922 $\to$ 67.0553

### Test Evaluation Metrics on Synthetic Cardiac Signals:
- **Mean Predictor Baseline:**
  - MAE: 10.101 bpm
  - RMSE: 11.413 bpm
  - Pearson $r$: 0.0
  - Within $\pm 3$ bpm: 6.25%
- **MLP Regressor Baseline:**
  - MAE: 67.727 bpm
  - RMSE: 68.624 bpm
  - Pearson $r$: 0.9188
  - Within $\pm 3$ bpm: 0.0%
- **KAN Regressor:**
  - MAE: 68.6 bpm
  - RMSE: 69.496 bpm
  - Pearson $r$: 0.837
  - Within $\pm 3$ bpm: 0.0%
