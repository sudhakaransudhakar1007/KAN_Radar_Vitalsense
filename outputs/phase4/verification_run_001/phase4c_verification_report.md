# PHASE 4C: INDEPENDENT VERIFICATION OF PHASE 4B FINDINGS

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 4C — Independent Forensic Verification & Evidence Audit  
**Verification Run Directory:** `outputs/phase4/verification_run_001/`  
**Execution Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  
**Verification Verdict:** **VERIFICATION PASSED — READY FOR FORMAL GATE REVIEW**  

---

## 1. Executive Summary & Purpose

Phase 4C provides a strict, evidence-based independent verification of the Phase 4B findings. The mandate requires confirming every reported metric, architecture parameter, dataset arithmetic quantity, LOSO fold split, and synchronization status directly from workspace source files and execution traces without relying on prior assistant claims.

### Key Verification Results:
1. **Synthetic Metric Recalculation:**
   - Saved test predictions were serialized to disk at `outputs/phase4/verification_run_001/synthetic_test_predictions.csv`.
   - Independent recomputation confirmed that the high-correlation ($r > 0.85$) vs. high-MAE ($\approx 65 - 69$ BPM) paradox is mathematically real: KAN predictions hover around $7.25 - 9.99$ BPM against true targets averaging $73.22$ BPM due to unnormalized targets, Huber loss clipping ($\pm 1.0$), and near-zero weight initialization.
   - The bias is negative and equals the MAE ($\text{MAE} \equiv |\text{Bias}|$).
   - Constant prediction Pearson correlation is mathematically undefined ($\frac{0}{0}$); the codebase implements an explicit fallback guard returning $r = 0.0$ when $\sigma_{\hat{y}} \le 10^{-6}$.
2. **Model Architecture Re-Verification:**
   - Full layer-by-layer forward pass verified runtime tensor shapes:
     $\text{Input } (2, 3333, 1) \to \text{Conv1 } (2, 834, 8) \to \text{Pool1 } (2, 417, 8) \to \text{Conv2 } (2, 105, 16) \to \text{Pool2 } (2, 52, 16) \to \text{Conv3 } (2, 26, 16) \to \text{GAP } (2, 16) \to \text{KAN1 } (2, 8) \to \text{KAN2 } (2, 1) \to \text{Squeeze } (2,)$.
   - Trainable parameters verified: `KANRegressor` = **4,720**, `MLPRegressor` = **3,505**, `MeanPredictorBaseline` = **0**.
   - Verified that `KANLayer` implements the authentic recursive Cox-de Boor B-spline algorithm ($k=3, G=5$) with trainable 3D tensor spline weights, base linear weights, and scale factors. It is not an MLP substitute.
3. **Dataset Window Arithmetic & Manifest Re-Verification:**
   - Exact sampling rate is $1000/3 = 333.333333$ Hz.
   - 10.0-second window corresponds to 3,333 samples ($9.9990$ s actual duration).
   - 5.0-second stride corresponds to 1,667 samples ($5.0010$ s actual duration).
   - 22 windows span samples $0$ to $38,340$, leaving a trailing tail of 1,660 samples ($4.9800$ s).
   - Exactly **1,029 unique valid windows** exist in `outputs/supervised_dataset/run_001/accepted_window_manifest.csv` with zero duplicate keys.
4. **LOSO Fold Isolation Re-Verification:**
   - All 24 folds ($VS01$ through $VS24$) in `outputs/phase4/run_001/fold_split_manifest.csv` have **0.0% cross-subject leakage**.
   - Sum of test windows across 24 folds equals exactly 1,029 windows.
5. **Phase 2A Synchronization Readiness:**
   - Physical hardware clock synchronization is **`UNVERIFIED`** (0 of 96 MAT files contain trigger channels).
   - Alignment is based strictly on the user-approved operational modeling assumption of nominal $t_0 = 0.0$ s.
   - The commercial monitor's displayed `HR` array is permanently disqualified due to verified $+6.21$ s latency.
   - Ground truth construction derives strictly from instantaneous ECG R-peaks via harmonic mean ($60 / \text{mean}(RR)$).
6. **Automated Test Suite Status:**
   - Fresh execution of the entire repository test suite confirmed **91 / 91 tests passing (100%)** with 0 failures and 0 regressions.

---

## 2. Inventory of Verification Artifacts in this Run
- `phase4c_verification_report.md`: Executive summary and cross-reference table.
- `synthetic_metric_recalculation.md`: Detailed mathematical recalculation of benchmark metrics.
- `synthetic_test_predictions.csv`: Serialized table of true targets and model predictions across 16 test samples.
- `architecture_reverification.md`: Line-by-line inspection of KAN spline mathematics and tensor dimensions.
- `manifest_and_loso_reverification.md`: Verification of 1,029 accepted windows and 24 LOSO partitions.
- `ground_truth_and_sync_review.md`: Complete audit of ECG R-peak extraction, harmonic HR derivation, and sync boundaries.
- `test_execution_record.md`: Verbatim log of 91/91 test pass.
- `error_log.md`: Status of tracked issues and mitigation registry.
- `final_verdict.md`: Formal justification of final verdict.
