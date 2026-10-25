# PHASE 5: CHECKPOINT MANIFEST & UNGENERATED ARTIFACT REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  

---

## 1. Executive Summary

In strict compliance with Phase 5 Task 11 and Task 13 mandatory execution rules:
> *"Do not create fake files or empty results merely to satisfy this list. Clearly mark outputs that were not generated and explain why."*

Because the Phase 2A Finalization Gate remains officially **`OPEN`** and explicit user training authorization has not been granted, real-data model fitting was withheld.

Consequently, **0 model checkpoints** were exported to disk, and all empirical real-data training artifact files are formally registered below as **NOT GENERATED**.

---

## 2. Checkpoint Inventory

| Checkpoint Path | Architecture | Fold Index | Status | Justification / Reason |
| :--- | :--- | :---: | :---: | :--- |
| `checkpoints/kan_fold_*.keras` | `KANRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/cnn_fold_*.keras` | `CNNRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/mlp_fold_*.keras` | `MLPRegressor` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `checkpoints/mean_fold_*.json` | `MeanPredictorBaseline` | Folds 1–24 | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |

**Total Model Checkpoints Generated:** `0`

---

## 3. Real-Data Training Outputs Register (Not Generated)

| Planned Output File / Artifact | Planned Description | Actual Status | Justification / Reason |
| :--- | :--- | :---: | :--- |
| `outputs/phase5/run_002/fold_metrics.csv` | 24-fold test metrics for all models | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_002/per_subject_metrics.csv` | Subject-level MAE, RMSE, Pearson $r$ | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_002/heldout_predictions.csv` | 1,029 window predictions vs true HR | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_002/training_history/` | Loss and metric curves per epoch | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |
| `outputs/phase5/run_002/checkpoints/` | Saved weights for top models | **NOT GENERATED** | Real-data training blocked by Phase 2A Gate |

**Anti-Fabrication Certification:** Zero metrics, predictions, or training loss logs were fabricated or populated with synthetic numbers to simulate real-data training.

---

## 4. Phase 5 `run_002` Executed Deliverables

The following 12 non-training audit reports and verification deliverables were generated from actual repository inspection, code review, test suite execution, and CPU latency benchmarks:

1. `outputs/phase5/run_002/existing_run_audit.md`: Line-by-line inspection of source modules, prior run inventory, and run_001 audit.
2. `outputs/phase5/run_002/gate_and_authorization_status.md`: Audit of Phase 2A gate status (`OPEN`), missing authorization, and timing assumptions.
3. `outputs/phase5/run_002/dataset_validation_report.md`: Verification of 24 subjects, 48 pairs, 1,029 accepted windows, 27 rejections, and monitor HR delay (+6.21s).
4. `outputs/phase5/run_002/loso_integrity_report.md`: Verification of 24 LOSO folds, coupled condition holding, and 0% subject leakage.
5. `outputs/phase5/run_002/training_configuration.md`: Specifications for KAN, CNN, MLP, Mean baseline, feature pipeline, and optimizer.
6. `outputs/phase5/run_002/checkpoint_manifest.md`: Register of 0 checkpoints and ungenerated real-data training outputs (this document).
7. `outputs/phase5/run_002/model_size_and_latency.md`: Trainable parameter counts, float32 model footprint, and CPU latency benchmarks.
8. `outputs/phase5/run_002/baseline_comparison_report.md`: Architectural comparison and formal audit of the classical autocorrelation gap.
9. `outputs/phase5/run_002/test_execution_record.md`: Complete automated test execution record (100/100 tests passing across 13 modules).
10. `outputs/phase5/run_002/limitations_and_error_log.md`: Formal registry of scientific limitations, timing assumptions, and blockers.
11. `outputs/phase5/run_002/phase5_completion_report.md`: Comprehensive executive report synthesizing all Phase 5 findings.
12. `outputs/phase5/run_002/final_verdict.md`: Formal scientific sign-off with `BLOCKED — PHASE 2A GATE OPEN OR AUTHORIZATION MISSING`.
