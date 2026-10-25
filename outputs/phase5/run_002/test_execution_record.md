# PHASE 5: AUTOMATED TEST SUITE EXECUTION & VERIFICATION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Execution Timestamp:** October 16, 2026, 09:34:27 UTC  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Python Test Engineer  
**Suite Status:** **100 / 100 TESTS PASSED (100% SUCCESS RATE)**  

---

## 1. Test Execution Summary

The entire automated test suite for the project was executed in the clean development environment:
- **Test Command:** `python -m pytest tests/ -v`
- **Execution Runtime:** Python 3.10.11, PyTorch 2.x, TensorFlow 2.x / Keras, NumPy 2.2.6, Pytest 8.x
- **Total Test Modules:** 13 test files
- **Total Tests Collected & Run:** 100 tests
- **Passed Tests:** 100
- **Failed / Errored Tests:** 0
- **Skipped Tests:** 0
- **Execution Duration:** 26.47 seconds
- **Exit Code:** `0`

> **Scientific Caveat (Task 12):** *A passing software test suite does not substitute for successful real-data training or evaluation. The test suite verifies software logic, mathematical correctness, data isolation, and governance guards. Real-data model training remains blocked pending explicit user gate authorization.*

---

## 2. Test Suite Breakdown by Functional Area

| Test Module File | Domain / Functional Area Verified | Tests | Status |
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
| **Total** | **Full System Integration & Architectural Readiness** | **100** | **ALL PASSED** |

---

## 3. Specific Subsystem Verifications

1. **Gate Enforcement (`test_gate_blocker_enforcement`, `test_gate_enforcement_dry_run_flag`):**
   Verified that attempting to export persistent supervised training arrays or train real-data models while Phase 2A gate is `OPEN` raises `PermissionError` / `GateBlockerError`.
2. **Subject-Wise Isolation (`test_loso_fold_partitioning_leakage_free`, `test_all_24_loso_folds_isolation`):**
   Verified that in every one of the 24 evaluation folds:
   - Held-out test subjects never appear in training or validation sets.
   - Resting and Apnea recordings are held out together.
   - Every subject appears in the held-out test position exactly once.
3. **Target Normalization Boundaries (`test_target_normalizer_training_only_fit`, `test_target_normalizer_leakage_guards`):**
   Verified that normalization parameters are fitted strictly on training targets, and that calling `transform()` or `inverse_transform()` on an unfitted instance raises `RuntimeError`.
4. **Architectural Capacity Verification (`test_model_parameter_counts`, `test_cnn_regressor_forward_and_params`):**
   Verified exact trainable parameter counts:
   - `KANRegressor`: 4,720 parameters.
   - `MLPRegressor`: 3,505 parameters.
   - `CNNRegressor`: 3,377 parameters.
   - `MeanPredictorBaseline`: 0 parameters.
5. **Constant Prediction Handling (`test_constant_prediction_pearson_fallback`):**
   Verified that constant prediction vectors produce $r = 0.0$ without zero-division or NaN crashes.
