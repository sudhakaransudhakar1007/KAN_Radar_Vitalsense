# PHASE 5: CHECKPOINT MANIFEST & OUTPUT ARTIFACT INVENTORY

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  

---

## 1. Executive Summary

In strict compliance with Phase 5 execution rules, no model checkpoints, training logs, or prediction CSVs were fabricated. Because the Phase 2A Finalization Gate remains officially **`OPEN`** and explicit user training authorization has not been granted, real-data model training was withheld.

Consequently, **0 model checkpoints** were exported to disk. All planned empirical training output files are formally cataloged below as **NOT GENERATED**.

---

## 2. Checkpoint Inventory

| Checkpoint Path | Model Type | Fold Index | Status | Reason / Justification |
| :--- | :--- | :---: | :---: | :--- |
| `checkpoints/kan_fold_*.pt` | `KANRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/mlp_fold_*.pt` | `MLPRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/cnn_fold_*.pt` | `CNNRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/mean_fold_*.pt` | `MeanPredictorBaseline` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |

**Total Checkpoints Generated:** `0`

---

## 3. Real-Data Training Outputs Status

In compliance with the project rule *"Never fabricate timestamps, synchronization, HR labels, missing values, metrics, or plots. Only create files that contain actual executed results. Clearly mark unavailable outputs as not generated"*:

| Planned Output File / Artifact | Planned Content | Actual Status | Justification |
| :--- | :--- | :---: | :--- |
| `outputs/phase5/run_001/fold_metrics.csv` | 24-fold test metrics for all models | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_001/per_subject_metrics.csv` | Subject-level MAE, RMSE, Pearson $r$ | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_001/heldout_predictions.csv` | 1,029 window predictions vs true HR | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_001/training_history/` | Epoch loss curves per fold | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_001/plots/bland_altman/` | Agreement plots vs ECG reference | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_001/plots/correlation/` | Regression scatter plots | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |

---

## 4. Phase 5 Non-Training Deliverables (Successfully Generated)

The following non-training audit artifacts and verification reports were generated based on actual inspections, test runs, and CPU benchmarks:

1. `outputs/phase5/run_001/gate_and_authorization_check.md`: Official Phase 2A gate status inspection and enforcement action.
2. `outputs/phase5/run_001/dataset_and_label_validation.md`: Non-training verification of 1,029 accepted windows, 27 rejections, SQI, and monitor HR delay (+6.21s).
3. `outputs/phase5/run_001/loso_integrity_report.md`: Non-training audit of 24 LOSO folds, 0% leakage, and coupled-condition holding.
4. `outputs/phase5/run_001/training_configuration.md`: Standardized hyperparameters, loss function, and early stopping rules.
5. `outputs/phase5/run_001/latency_and_model_size.md`: Empirical CPU latency and parameter count benchmark (KAN: 4,720 params, 2.368 ms).
6. `outputs/phase5/run_001/checkpoint_manifest.md`: Explicit catalog of generated vs ungenerated artifacts (this document).
7. `outputs/phase5/run_001/limitations_and_error_log.md`: Formal log of experimental constraints and unverified timing.
8. `outputs/phase5/run_001/test_execution_record.md`: Complete automated test suite execution report (100/100 passing).
9. `outputs/phase5/run_001/phase5_training_report.md`: Comprehensive executive report of Phase 5 findings.
10. `outputs/phase5/run_001/final_verdict.md`: Formal scientific sign-off with `BLOCKED` verdict.
