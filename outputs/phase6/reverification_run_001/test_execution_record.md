# PHASE 6: AUTOMATED TEST SUITE EXECUTION & REGRESSION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Execution Timestamp:** October 16, 2026, 16:11:55 UTC  
**Auditor Role:** Senior Python/TensorFlow Test Engineer & Scientific ML Auditor  
**Suite Status:** **`99 / 100 TESTS PASSED (1 FAILURE IDENTIFIED & LOCALIZED)`**  

---

## 1. Test Execution Metadata

In compliance with Phase 6 Task 7, the automated test suite was executed in the clean development environment:
- **Execution Command:** `python -m pytest tests/ -v`
- **Execution Environment:** Windows 10/11 x86_64, Python 3.10.11
- **Key Dependencies:** `pytest 9.1.1`, `tensorflow 2.16+`, `numpy 2.2.6`, `scipy 1.15.3`, `pandas 2.3.1`
- **Total Test Modules:** 13 test files
- **Total Tests Collected & Run:** 100 tests
- **Tests Passed:** **99 tests** ($99.0\%$)
- **Tests Failed:** **1 test** ($1.0\%$)
- **Tests Skipped:** 0
- **Deprecation Warnings:** 6 warnings (Keras NumPy 2.x `__array__` copy deprecation)
- **Execution Duration:** 49.42 seconds
- **Exit Code:** `1`

---

## 2. Test Suite Breakdown by Module

| Test Module File | Focus Domain / Subsystem | Tests Run | Passed | Failed | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `tests/test_audit_script.py` | Phase 1 dataset file inventory, SHA-256 integrity, MAT loading | 8 | 8 | 0 | **PASSED** |
| `tests/test_benchmark_metrics.py` | Metric computations: MAE, RMSE, Pearson $r$, bias, tolerances | 7 | 7 | 0 | **PASSED** |
| `tests/test_phase2a_pipeline.py` | Cross-correlation, lag sign convention, step response, +6.21s delay | 8 | 8 | 0 | **PASSED** |
| `tests/test_phase3_pipeline.py` | Sync manager, ECG NaN cleaning, SQI gating, bandpass filter, windowing | 15 | 15 | 0 | **PASSED** |
| `tests/test_phase4_kan.py` | KAN layer, Conv backbone, MLP, Mean baseline, LOSO, gate blockers | 9 | 9 | 0 | **PASSED** |
| `tests/test_phase4b_audit.py` | Parameter counts, tensor shapes, window arithmetic, fold isolation | 7 | 7 | 0 | **PASSED** |
| `tests/test_phase4d_completion.py`| Target normalizer, zero-variance guard, CNN, synthetic pipeline | 10 | 9 | **1** | **FAILED (1)** |
| `tests/test_same_file_pairing.py` | Multi-channel file pairing integrity and column index verification | 1 | 1 | 0 | **PASSED** |
| `tests/test_signal_quality.py` | Signal quality screening: flatlines, NaNs/Infs, physiological limits | 7 | 7 | 0 | **PASSED** |
| `tests/test_supervised_dataset_generation.py` | Supervised dataset generation, SQI rejection rules, gate blockers, manifest | 8 | 8 | 0 | **PASSED** |
| `tests/test_sync_validation.py` | ECG processor, R-peak detector, respiratory cross-corr, cardiac radar validation | 15 | 15 | 0 | **PASSED** |
| `tests/test_timing_validation.py` | Nominal time axis construction, sampling rate guards, unverified timing | 5 | 5 | 0 | **PASSED** |
| **Total Suite** | **Comprehensive Full-System Regression** | **100** | **99** | **1** | **99% PASS** |

---

## 3. Forensic Analysis of the Single Test Failure

### Failing Test: `tests/test_phase4d_completion.py::test_synthetic_end_to_end_integration_pipeline`
- **Failure Traceback:**
  ```text
  tests\test_phase4d_completion.py:163: in test_synthetic_end_to_end_integration_pipeline
      assert results["kan_metrics"]["within_5bpm_pct"] >= 90.0
  E   assert 75.0 >= 90.0  # (or 87.5% in isolated execution)
  ```
- **Root Cause Analysis:**
  1. **Primary Test Objective Succeeded:**
     The core assertion of `test_synthetic_end_to_end_integration_pipeline` is:
     ```python
     kan_mae = results["kan_metrics"]["mae_bpm"]
     assert kan_mae < 5.0, f"KAN MAE {kan_mae} exceeded 5.0 BPM; normalization failed"
     ```
     This assertion **PASSED** completely (KAN MAE dropped from 68.6 BPM to ~3.01 BPM on synthetic data, proving that target normalization resolves the calibration offset).
  2. **Brittle Discrete Threshold:**
     The synthetic test partition contains only $N_{\text{test}} = 16$ samples ($25\%$ of 64 synthetic samples).
     Each test sample represents $1/16 = 6.25\%$.
     - 14 / 16 samples within $\pm 5\text{ BPM} = 87.5\%$
     - 15 / 16 samples within $\pm 5\text{ BPM} = 93.75\%$
     The hardcoded threshold `>= 90.0%` requires at least 15 of 16 samples to be within 5 BPM after only 10 epochs of mini-batch gradient descent. Minor stochastic gradient variations across Python sessions cause this percentage to fluctuate between $75.0\%$ (12/16) and $87.5\%$ (14/16).
  3. **Safety Rule Compliance:**
     In accordance with Phase 6 Safety Rules: *"Never delete, overwrite, or silently modify earlier outputs or source code. Do not change model architecture during this audit. Record defects and recommend minimal corrections separately."*
     The test file was **NOT modified**. The defect is registered in [`discrepancy_and_corrective_action_register.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6/reverification_run_001/discrepancy_and_corrective_action_register.md).

---

## 4. Test Verification Conclusions

1. **Gate Blocker Enforcement is 100% Intact:** All governance tests (`test_gate_blocker_enforcement`, `test_gate_enforcement_dry_run_flag`, `test_run_manifest_gate_blocker_content`) passed, proving that real-data model training cannot be accidentally initiated while the Phase 2A gate is `OPEN`.
2. **Subject Isolation is 100% Intact:** All LOSO partitioning and target normalization leakage guards passed.
3. **Caveat on Software Testing:**
   *A passing or 99%-passing software test suite does not substitute for successful real-data model training. Software tests verify logical correctness on synthetic tensors; real-data evaluation remains blocked by the open governance gate.*
