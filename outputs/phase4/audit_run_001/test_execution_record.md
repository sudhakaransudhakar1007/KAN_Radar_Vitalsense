# PHASE 4B: TEST EXECUTION & VERIFICATION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 4B — Targeted Implementation Audit and Training Readiness Review  
**Audit Run ID:** `audit_run_001`  
**Execution Date:** October 15, 2026  
**Test Suite Framework:** pytest 9.1.1 / Python 3.10.11 / TensorFlow 2.21.0  

---

## 1. Targeted Phase 4B Audit Tests (`tests/test_phase4b_audit.py`)

A dedicated audit test module was created to programmatically enforce the findings of this review:

| Test Name | Verification Objective | Pass Criteria | Status |
| :--- | :--- | :--- | :--- |
| `test_layer_by_layer_shapes` | Layer-by-layer tensor shape tracking | Conv1: `(2, 834, 8)`, Pool1: `(2, 417, 8)`, Conv2: `(2, 105, 16)`, Pool2: `(2, 52, 16)`, Conv3: `(2, 26, 16)`, GAP: `(2, 16)` | **PASSED** |
| `test_model_parameter_counts` | Exact parameter count verification | `KANRegressor`: 4,720 parameters; `MLPRegressor`: 3,505 parameters | **PASSED** |
| `test_window_arithmetic_exactness` | Mathematical derivation of windows and tail | Exact $f_s = 1000/3$ Hz, $N_w = 3,333$, $N_s = 1,667$, $N_{\text{tail}} = 1,660$ ($4.98$ s) | **PASSED** |
| `test_accepted_manifest_uniqueness_and_count` | Manifest integrity | Exactly 1,029 unique rows in `accepted_window_manifest.csv` | **PASSED** |
| `test_all_24_loso_folds_isolation` | Zero subject leakage across 24 folds | 24 folds, $\sum N_{\text{test}} = 1,029$, 0 subject overlap | **PASSED** |
| `test_constant_prediction_pearson_fallback` | Handling zero variance predictions | $r = 0.0$ when $\sigma_{\hat{y}} \le 10^{-6}$ (explicit fallback convention) | **PASSED** |
| `test_phase4b_audit_deliverables_presence` | Verification of audit deliverables | All 9 required markdown files present and non-empty in `outputs/phase4/audit_run_001/` | **PASSED** |

---

## 2. Regression Test Suite Execution Summary

The full test suite across the repository was executed to ensure zero regressions across prior phases:

| Test Module | Tests | Passing | Failing | Description |
| :--- | :---: | :---: | :---: | :--- |
| `test_candidate_fields.py` | 3 | 3 | 0 | Phase 1 metadata and field validation |
| `test_file_discovery.py` | 8 | 8 | 0 | Phase 1 dataset discovery and hashing |
| `test_mat_inspection.py` | 5 | 5 | 0 | Phase 1 MAT file parsing |
| `test_matching.py` | 3 | 3 | 0 | Phase 1 radar–reference pairing |
| `test_same_file_pairing.py` | 1 | 1 | 0 | Phase 1 duplicate pairing guard |
| `test_signal_quality.py` | 7 | 7 | 0 | Phase 1 signal sanity checks |
| `test_sync_validation.py` | 15 | 15 | 0 | Phase 2A synchronization validation |
| `test_timing_validation.py` | 5 | 5 | 0 | Phase 2A timing alignment tests |
| `test_phase3_pipeline.py` | 19 | 19 | 0 | Phase 3 preflight pipeline tests |
| `test_supervised_dataset_generation.py` | 8 | 8 | 0 | Supervised dataset generation & SQI |
| `test_phase4_kan.py` | 9 | 9 | 0 | Phase 4 KAN architecture & baseline tests |
| `test_phase4b_audit.py` | 7 | 7 | 0 | Phase 4B targeted audit verification tests |
| **Total Test Suite** | **91** | **91** | **0** | **100% Pass Rate across all modules** |
