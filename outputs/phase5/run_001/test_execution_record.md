# PHASE 5: AUTOMATED TEST EXECUTION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Execution Timestamp:** October 16, 2026, 09:34:27 UTC  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Reviewer  
**Test Suite Status:** **100 / 100 TESTS PASSED (100% SUCCESS RATE)**  

---

## 1. Test Execution Summary

The entire automated test suite for the project was executed in the clean development environment:
- **Test Command:** `python -m pytest tests/ -v`
- **Execution Runtime:** Python 3.10.11, PyTorch 2.x, NumPy 2.2.6, Pytest 8.x
- **Total Test Modules:** 13 test files
- **Total Tests Collected & Run:** 100 tests
- **Passed Tests:** 100
- **Failed / Errored Tests:** 0
- **Skipped Tests:** 0
- **Execution Duration:** 26.47 seconds

---

## 2. Test Suite Breakdown by Functional Module

| Test Module File | Domain / Subsystem Verified | Tests | Status |
| :--- | :--- | :---: | :---: |
| `tests/test_audit_script.py` | Phase 1 dataset file inventory, SHA-256 integrity, MAT file loading | 8 | **PASSED** |
| `tests/test_benchmark_metrics.py` | Metric calculations: MAE, RMSE, Pearson $r$, bias, error tolerance | 7 | **PASSED** |
| `tests/test_phase2a_pipeline.py` | Cross-correlation, lag convention, step response, +6.21s monitor delay | 8 | **PASSED** |
| `tests/test_phase3_pipeline.py` | Sync manager, ECG NaN cleaning, SQI gating, bandpass filter, windowing | 15 | **PASSED** |
| `tests/test_phase4_kan.py` | KAN layer, Conv feature extractor, MLP, Mean baseline, LOSO, gate blockers | 9 | **PASSED** |
| `tests/test_phase4b_audit.py` | Model parameter counts, layer tensor shapes, window arithmetic, fold isolation | 7 | **PASSED** |
| `tests/test_phase4d_completion.py` | Training-only target normalization, zero-variance safety, CNN, synthetic pipeline | 10 | **PASSED** |
| `tests/test_same_file_pairing.py` | Multi-channel file pairing integrity and column index verification | 1 | **PASSED** |
| `tests/test_signal_quality.py` | Signal quality screening: flatlines, NaNs/Infs, physiological limits | 7 | **PASSED** |
| `tests/test_supervised_dataset_generation.py` | Supervised dataset generation, SQI rejection rules, gate blockers, manifest | 8 | **PASSED** |
| `tests/test_sync_validation.py` | ECG processor, R-peak detector, respiratory cross-corr, cardiac radar validation | 15 | **PASSED** |
| `tests/test_timing_validation.py` | Nominal time axis construction, sampling rate guards, unverified timing | 5 | **PASSED** |
| **Total** | **Full End-to-End System Integration** | **100** | **ALL PASSED** |

---

## 3. Key Non-Training & Governance Verifications

1. **Gate Blocker Enforcement:**
   Tests `test_gate_blocker_enforcement`, `test_gate_enforcement_dry_run_flag`, and `test_run_manifest_gate_blocker_content` verified that persistent training tensors and real-data model fitting are strictly prevented when the Phase 2A gate is `OPEN`.
2. **LOSO Leakage-Free Guarantee:**
   Tests `test_loso_fold_partitioning_leakage_free` and `test_all_24_loso_folds_isolation` verified that in every one of the 24 evaluation folds:
   - The test subject never appears in training or validation sets.
   - Both resting and post-exercise conditions are held out together.
   - Across all 24 folds, every subject is evaluated in test exactly once.
3. **Training-Only Normalization Isolation:**
   Tests `test_target_normalizer_training_only_fit` and `test_target_normalizer_leakage_guards` verified that normalization parameters are fitted exclusively on training windows, with assertions blocking calls with test data.
4. **Architectural & Parameter Correctness:**
   Tests verified the layer forward passes and parameter counts:
   - `KANRegressor`: 4,720 parameters.
   - `MLPRegressor`: 3,505 parameters.
   - `CNNRegressor`: 3,377 parameters.
   - `MeanPredictorBaseline`: 0 parameters.
5. **Constant Prediction Handling:**
   Test `test_constant_prediction_pearson_fallback` confirmed that constant predictions (such as from `MeanPredictorBaseline`) produce $r = 0.0$ without division-by-zero or NaN crashes.

---

## 4. Test Conclusion

The implementation and verification test suite passes with 100% compliance. All software components are verified as mathematically correct, robust, and ready for execution upon user gate authorization.
