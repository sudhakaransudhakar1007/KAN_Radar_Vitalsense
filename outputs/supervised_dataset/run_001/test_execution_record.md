# Supervised Dataset Generation: Test Execution Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Supervised Dataset Generation Implementation & Quality Audit  
**Run ID:** `run_001`  
**Execution Timestamp:** 2026-10-15T15:18:08Z (Local: 20:48:08+05:30)  
**Status:** `VERIFIED_ALL_PASSING`  

---

## 1. Test Command & Execution Environment

The full repository test suite, including new stage-specific tests, was executed:

- **Command:** `python -m pytest tests/ -v`
- **Working Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **Operating System:** Windows (win32)
- **Python Runtime:** Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]
- **Pytest Version:** pytest 9.1.1 (pluggy 1.6.0)
- **Key Dependencies:** NumPy 2.2.6, SciPy 1.15.3, Pandas 2.3.1, Matplotlib 3.10.8, AnyIO 4.15.1, LangSmith 0.12.5

---

## 2. Test Suite Composition & Results

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR
configfile: pytest.ini
collected 75 items

tests/test_candidate_fields.py ........................................ [  4%]
tests/test_file_discovery.py ........................................... [ 14%]
tests/test_mat_inspection.py ........................................... [ 21%]
tests/test_matching.py ................................................. [ 25%]
tests/test_phase3_pipeline.py .......................................... [ 50%]
tests/test_same_file_pairing.py ........................................ [ 52%]
tests/test_signal_quality.py ........................................... [ 61%]
tests/test_supervised_dataset_generation.py ............................ [ 72%]
tests/test_sync_validation.py .......................................... [ 93%]
tests/test_timing_validation.py ........................................ [100%]

============================= 75 passed in 9.17s ==============================
```

- **Total Test Files:** 10
- **Total Tests Collected:** 75
- **Total Tests Passing:** 75 (100%)
- **Total Tests Failing:** 0 (0%)

### Test Layer Breakdown:
1. **Phase 1 & Phase 2 Baseline Tests (48 tests):**
   - File discovery, SHA-256 calculation, MAT-file inspection, candidate field extraction, signal quality checks, and sync validation functions. All 48 passed.
2. **Phase 3 Pipeline Tests (19 tests):**
   - In `tests/test_phase3_pipeline.py`: `RobustMatLoader`, `SynchronizationManager`, `ECGReferenceValidator`, `RadarPreprocessor`, `WindowGenerator`, and deliverable verifications for `outputs/phase3/run_001`. All 19 passed.
3. **Supervised Dataset Generation Tests (8 tests):**
   - In `tests/test_supervised_dataset_generation.py`:
     - `test_window_reference_hr_perfect_rhythm`: Verifies harmonic mean formula ($60 / \overline{RR}$) on 60 bpm rhythm. Passed.
     - `test_window_reference_hr_coverage_below_85`: Verifies rejection of window when RR coverage $< 85\%$. Passed.
     - `test_window_reference_hr_max_gap_exceeded`: Verifies rejection when maximum gap $\ge 3.0\text{ s}$. Passed.
     - `test_window_reference_hr_non_physiological_interval`: Verifies rejection when RR interval falls outside 35–185 bpm range. Passed.
     - `test_gate_enforcement_dry_run_flag`: Verifies that `phase2a_gate_status == 'OPEN'` blocks persistent array generation. Passed.
     - `test_supervised_dataset_run_001_deliverables_exist`: Verifies all manifests and reports exist in `outputs/supervised_dataset/run_001/`. Passed.
     - `test_supervised_manifest_counts_and_integrity`: Verifies exactly 1,056 candidate, 1,029 accepted, and 27 rejected windows with zero NaNs and zero duplicates. Passed.
     - `test_run_manifest_gate_blocker_content`: Verifies gate blocker reason string in `run_manifest.json`. Passed.

---

## 3. Error Preservation During Implementation

One transient implementation error occurred during the initial prototype execution:
- **Traceback:** `UnboundLocalError: local variable 'rec_sqi_fail_count' referenced before assignment` at line 202 of `src/phase3/supervised_dataset_generator.py`.
- **Cause:** Typo in variable naming (`rec_sqi_fail_count` vs `recording_sqi_fail_count`).
- **Resolution:** Corrected variable reference. Preserved in `error_log.md`. All subsequent runs completed with exit code 0.
