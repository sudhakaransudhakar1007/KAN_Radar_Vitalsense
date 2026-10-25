# PHASE 4B: TARGETED IMPLEMENTATION AUDIT REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 4B — Targeted Implementation Audit and Training Readiness Review  
**Audit Run ID:** `audit_run_001`  
**Execution Date:** October 15, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer, Scientific ML Auditor, & Reproducibility Reviewer  
**Audit Status:** **AUDIT PASSED WITH DOCUMENTED LIMITATIONS — GATE DECISION REQUIRED**  

---

## 1. Executive Summary

This targeted audit performs an exhaustive, evidence-based code and mathematical review of the Phase 4 Kolmogorov-Arnold Network (KAN) regression pipeline, comparative baselines (MLP and non-parametric mean predictor), window generation arithmetic, Leave-One-Subject-Out (LOSO) isolation boundaries, and the synthetic benchmark execution.

### Key Audit Findings:
1. **Synthetic Benchmark Diagnostic (Confirmed Defect & Resolution Identified):**
   The synthetic benchmark produced an MAE of $\approx 68.6$ BPM for KAN and $\approx 50.6$ BPM for MLP despite high Pearson correlations ($r \approx 0.83 - 0.93$). The audit independently verified that this was caused by unnormalized target HRs ($55 - 90$ BPM) paired with standard near-zero weight initialization, Huber loss gradient clipping ($\pm 1.0$), and a short 5-epoch training horizon. The models only drifted upwards to $3.85$ BPM (KAN) and $17.88$ BPM (MLP), creating a massive $-69.37$ BPM bias that equals the MAE. The high correlation reflects scale-invariant frequency feature alignment, proving code execution and gradient flow, but **not** meaningful calibrated physiological learning.
2. **Model Architecture Verification (Verified Authentic KAN, Shape Discrepancy Resolved):**
   The KAN layer was verified to be a mathematically authentic, differentiable B-spline implementation using the recursive Cox-de Boor algorithm ($k=3$, $G=5$, 4,720 total parameters). It is **not** an MLP substitute. A minor discrepancy between informal code comments and actual layer shapes was reconciled: TensorFlow `"same"` padding with stride 4 produces $\lceil 3333/4 \rceil = 834$ (not 833), flowing into $417 \to 105 \to 52 \to 26 \to 16$ latent dimensions.
3. **Dataset Window Arithmetic (100% Mathematically Verified):**
   Exact sampling rate is $1000/3 = 333.333333$ Hz (yielding exactly 120.000000 s for 40,000 samples). 10.0-second windows correspond to 3,333 samples ($9.9990$ s actual duration); 5.0-second stride corresponds to 1,667 samples ($5.0010$ s actual duration). 22 windows span samples $0$ to $38,340$, leaving a trailing tail of 1,660 samples ($4.9800$ s). The accepted window manifest contains exactly **1,029 unique valid windows** across 48 recordings.
4. **LOSO Isolation (100% Verified, Zero Cross-Subject Leakage):**
   All 24 held-out folds ($VS01$ to $VS24$) were audited against the accepted window manifest. Zero subject leakage was verified ($0\%$). Both Resting and Apnea recordings of each subject are held out together. Four potential leakage risks (global normalization, test-fold hyperparameter tuning, cross-condition splitting, and edge effects) were evaluated with strict mitigation protocols.
5. **Scientific Readiness & Phase 2A Gate (Formally Blocked):**
   The Phase 2A Finalization Gate remains officially **`OPEN`**. Nominal $t_0 = 0.0$ s sample alignment is an operational modeling convention, not verified hardware synchronization. Supervised real-data training remains strictly **`BLOCKED`**.

---

## 2. Inventory of Audited Files
- `src/kan/kan_layer.py`: Authentic Cox-de Boor cubic B-spline KAN layer.
- `src/kan/kan_model.py`: `ConvFeatureExtractor`, `KANRegressor`, `MLPRegressor`, `MeanPredictorBaseline`.
- `src/kan/loso_evaluator.py`: 24-fold LOSO cross-validation partitioner, gate checker, synthetic benchmark runner.
- `outputs/supervised_dataset/run_001/accepted_window_manifest.csv`: 1,029 accepted windows.
- `outputs/phase4/run_001/fold_split_manifest.csv`: 24-fold partition manifest.
- `outputs/phase4/run_001/baseline_comparison_report.md`: Synthetic benchmark report.
- `outputs/phase2a/step2b_consistency_audit.md`: Phase 2A audit and gate record.
