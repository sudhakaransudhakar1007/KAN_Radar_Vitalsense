# PHASE 7: AUTOMATED TEST SUITE EXECUTION & REGRESSION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Execution Timestamp:** October 17, 2026, 02:58:57 UTC  
**Auditor Role:** Senior Python/ML Engineer, Independent Code Auditor & Test Specialist  
**Execution Status:** **`100 / 100 TESTS PASSED (100% CLEAN REGRESSION RATE)`**  

---

## 1. Test Execution Metadata & Environment

In compliance with Phase 7 Task B and Section 13, the automated test suite was executed in full:
- **Execution Command:** `python -m pytest tests/ -v`
- **Execution Runtime:** Windows 10/11 x86_64, Python 3.10.11 (MSC v.1929 64 bit)
- **Key Framework Versions:**
  - `pytest 9.1.1`, `pluggy 1.6.0`
  - `tensorflow 2.16+`, `keras 3.x`
  - `torch 2.x`
  - `numpy 2.2.6`, `scipy 1.15.3`, `pandas 2.3.1`
- **Total Tests Collected & Run:** 100 tests
- **Tests Passed:** **100 tests** ($100.0\%$)
- **Tests Failed:** **0 tests** ($0.0\%$)
- **Tests Skipped:** 0 tests
- **Deprecation Warnings:** 6 warnings (Keras NumPy 2.x `__array__` copy keyword deprecation; non-breaking)
- **Execution Duration:** 54.76 seconds
- **Exit Code:** `0`

---

## 2. Module-by-Module Test Results Breakdown

| Test Module File | Focus Domain / Subsystem Verified | Tests Run | Passed | Failed | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `tests/test_audit_script.py` | Phase 1 raw MAT file inventory, SHA-256 integrity, MAT loading | 8 | 8 | 0 | **PASSED** |
| `tests/test_benchmark_metrics.py` | Metric calculations: MAE, RMSE, Pearson $r$, bias, error tolerances | 7 | 7 | 0 | **PASSED** |
| `tests/test_phase2a_pipeline.py` | Cross-correlation, lag sign convention, step response, +6.21s delay | 8 | 8 | 0 | **PASSED** |
| `tests/test_phase3_pipeline.py` | Sync manager, ECG NaN cleaning, SQI gating, bandpass filter, windowing | 15 | 15 | 0 | **PASSED** |
| `tests/test_phase4_kan.py` | KAN layer, Conv backbone, MLP, Mean baseline, LOSO, gate blockers | 9 | 9 | 0 | **PASSED** |
| `tests/test_phase4b_audit.py` | Model parameter counts, tensor shapes, window arithmetic, fold isolation | 7 | 7 | 0 | **PASSED** |
| `tests/test_phase4d_completion.py`| Target normalizer, zero-variance guard, CNN, synthetic pipeline | 10 | 10 | 0 | **PASSED** |
| `tests/test_same_file_pairing.py` | Multi-channel file pairing integrity and column index verification | 1 | 1 | 0 | **PASSED** |
| `tests/test_signal_quality.py` | Signal quality screening: flatlines, NaNs/Infs, physiological limits | 7 | 7 | 0 | **PASSED** |
| `tests/test_supervised_dataset_generation.py` | Supervised dataset generation, SQI rejection rules, gate blockers, manifest | 8 | 8 | 0 | **PASSED** |
| `tests/test_sync_validation.py` | ECG processor, R-peak detector, respiratory cross-corr, cardiac radar validation | 15 | 15 | 0 | **PASSED** |
| `tests/test_timing_validation.py` | Nominal time axis construction, sampling rate guards, unverified timing | 5 | 5 | 0 | **PASSED** |
| **Total Test Suite** | **Comprehensive Full-System Regression** | **100** | **100** | **0** | **100% PASS** |

---

## 3. Explicit Separation of Test Evidence

1. **Tests Actually Executed in Phase 7:**
   - Isolated execution of `test_phase4d_completion.py` (50.43s, 9 passed).
   - Full suite execution of all 100 tests across 13 test files (54.76s, 100 passed, exit code 0).
2. **Prior Phase 6 Historical Test Record:**
   - Phase 6 reported 99 passed, 1 failed (exit code 1).
   - The failure was investigated, resolved under Task B without threshold weakening, and re-verified.
3. **Important Scientific Caveat:**
   *Passing all 100 automated unit and integration tests does not constitute proof that real-data model training has occurred or that the framework achieves clinical validity. Software tests verify architectural correctness, gradient flow, mathematical formulas, and data isolation on synthetic tensors. Real-data training remains strictly blocked by the open governance gate.*
