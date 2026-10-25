# PHASE 4: FINAL KAN MODEL IMPLEMENTATION & SUBJECT-INDEPENDENT EVALUATION REPORT

**Project:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4 — KAN Model Development and Subject-Independent Evaluation  
**Status:** **INFRASTRUCTURE COMPLETE — REAL-DATA TRAINING BLOCKED BY PHASE 2A GATE**  
**Execution Timestamp (UTC):** 2026-10-15T15:46:21.345336+00:00  

---

## Executive Summary

Phase 4 successfully implemented the complete, mathematically authentic Kolmogorov-Arnold Network (KAN) regression framework, comparative baselines (MLP and Mean Predictor), 24-fold Leave-One-Subject-Out (LOSO) cross-validation pipeline, and evaluation metric engine.

In strict compliance with **Mandatory Execution Rule 4**, persistent supervised model training against real VITALSENSE radar signals was **`BLOCKED`** because the Phase 2A Finalization Gate remains officially **`OPEN`** (`outputs/phase2a/step2b_consistency_audit.md`). All training loops, loss functions, backpropagation mechanics, and metric calculations were verified via an end-to-end synthetic benchmark.

---

## 1. KAN Model Implementation
- **Spline Implementation:** Full Cox-de Boor recursive algorithm for cubic B-splines ($k=3$) with a trainable uniform knot vector grid ($G=5$), trainable spline coefficients, residual linear base weights, and scaling factors.
- **Dimensionality Management:** A 3-block 1D convolutional feature extractor reduces 3,333 input samples to 16 latent representations, restricting total model parameters to 4,720.

## 2. Comparative Baselines
- **`MLPRegressor`:** Identical 1D Conv feature extractor with a 2-layer Dense network (3,505 parameters).
- **`MeanPredictorBaseline`:** Non-parametric empirical mean estimator.

## 3. LOSO Partitioning & Leakage Verification
- **Total Folds:** 24 folds ($VS01$ through $VS24$).
- **Subject Overlap:** Verified **0% leakage** across all 24 folds.
- **Distribution:** 1,029 total accepted windows partitioned across folds (average ~43 test windows per subject).

## 4. Synthetic Verification Results
- **KAN Loss Convergence:** Monotonically decreased from 70.0128 to 66.5966.
- **Gradient Backpropagation:** Verified non-zero gradients on all trainable KAN parameters.
