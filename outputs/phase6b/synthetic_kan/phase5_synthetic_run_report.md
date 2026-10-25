# PHASE 5: KAN SYNTHETIC TRAINING BENCHMARK REPORT

**Benchmark Label:** `SYNTHETIC_BENCHMARK` (NO REAL DATA WAS ACCESSED OR USED)  
**Run ID:** `synthetic_kan`  
**Execution Timestamp:** `2026-10-21T10:54:31.185395+00:00`  
**Model Architecture:** `KAN` (B-spline KAN Layer)  
**Runtime Feature Dimension:** `3333`  
**Folds Evaluated:** `8`  

---

## 1. Multi-Fold Evaluation Summary

- **Mean MAE:** 2.592 +/- 2.85 BPM
- **Mean RMSE:** 2.928 BPM
- **Mean Bias:** -0.761 BPM
- **Mean Pearson r:** 0.8606
- **Within +/- 3 BPM:** 70.0%
- **Within +/- 5 BPM:** 82.5%

## 2. Hard Gate Compliance Notice
Real-data training remains officially **BLOCKED** because the Phase 2A Finalization Gate is OPEN. This run operated exclusively on isolated synthetic fixtures to verify gradient updates, checkpointing, and leakage-free normalization.
