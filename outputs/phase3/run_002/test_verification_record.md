# Phase 3 Test & Deliverable Verification Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_002`  
**Execution Timestamp:** 2026-10-15T10:39:19Z (Local: 16:09:19+05:30)  
**Status:** `VERIFIED_ALL_PASSING`  

---

## 1. Test Execution Command & Environment

The full automated regression test suite was executed without modification:

- **Execution Command:** `python -m pytest tests/ -v`
- **Working Directory:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **Python Runtime:** Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]
- **Operating System:** Windows (win32)
- **Pytest Version:** pytest 9.1.1 (pluggy 1.6.0)
- **Active Dependencies:** NumPy 2.2.6, SciPy 1.15.3, Pandas 2.3.1, Matplotlib 3.10.8, AnyIO 4.15.1, LangSmith 0.12.5

---

## 2. Test Execution Results

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR
configfile: pytest.ini
plugins: anyio-4.15.1, langsmith-0.12.5
collecting ... collected 67 items

tests/test_candidate_fields.py::test_candidate_field_identification_matching PASSED [  1%]
tests/test_candidate_fields.py::test_missing_vitalsig_and_radar_fs PASSED [  2%]
tests/test_candidate_fields.py::test_unverified_field_when_not_in_docs PASSED [  4%]
tests/test_file_discovery.py::test_missing_dataset_root PASSED           [  5%]
tests/test_file_discovery.py::test_empty_dataset_root PASSED             [  7%]
tests/test_file_discovery.py::test_sha256_computation PASSED             [  8%]
tests/test_file_discovery.py::test_sha256_nonexistent_file PASSED        [ 10%]
tests/test_file_discovery.py::test_infer_candidates_from_path PASSED     [ 11%]
tests/test_file_discovery.py::test_flat_layout_discovery PASSED          [ 13%]
tests/test_file_discovery.py::test_cli_stage_b_gate_refuses_without_stage_a PASSED [ 14%]
tests/test_file_discovery.py::test_cli_stage_b_gate_refuses_without_approval_flag PASSED [ 16%]
tests/test_mat_inspection.py::test_traditional_mat_inspection PASSED     [ 17%]
tests/test_mat_inspection.py::test_hdf5_mat_inspection PASSED            [ 19%]
tests/test_mat_inspection.py::test_hdf5_complex_compound_array PASSED    [ 20%]
tests/test_mat_inspection.py::test_orientation_status_flagging PASSED    [ 22%]
tests/test_mat_inspection.py::test_approved_summary_stats_no_raw_leak PASSED [ 23%]
tests/test_matching.py::test_separate_file_verified_pairing PASSED       [ 25%]
tests/test_matching.py::test_ambiguous_file_matching PASSED              [ 26%]
tests/test_matching.py::test_unmatched_recordings PASSED                 [ 28%]
tests/test_phase3_pipeline.py::test_mat_loader_file_not_found PASSED     [ 29%]
tests/test_phase3_pipeline.py::test_mat_loader_mock_radar PASSED         [ 31%]
tests/test_phase3_pipeline.py::test_mat_loader_missing_required_variable PASSED [ 32%]
tests/test_phase3_pipeline.py::test_mat_loader_mock_reference PASSED     [ 34%]
tests/test_phase3_pipeline.py::test_sync_manager_time_axis_construction PASSED [ 35%]
tests/test_phase3_pipeline.py::test_sync_manager_invalid_frequency_or_samples PASSED [ 37%]
tests/test_phase3_pipeline.py::test_sync_manager_unverified_hardware_status PASSED [ 38%]
tests/test_phase3_pipeline.py::test_ecg_nan_analysis_zero_nans PASSED    [ 40%]
tests/test_phase3_pipeline.py::test_ecg_nan_linear_interpolation PASSED  [ 41%]
tests/test_phase3_pipeline.py::test_ecg_periodic_nans_detection PASSED   [ 43%]
tests/test_phase3_pipeline.py::test_ecg_nan_multi_sample_gap PASSED      [ 44%]
tests/test_phase3_pipeline.py::test_ecg_pan_tompkins_qrs_detection PASSED [ 46%]
tests/test_phase3_pipeline.py::test_ecg_sqi_evaluation_not_approved_guard PASSED [ 47%]
tests/test_phase3_pipeline.py::test_radar_nyquist_validation PASSED      [ 49%]
tests/test_phase3_pipeline.py::test_radar_bandpass_filtering PASSED      [ 50%]
tests/test_phase3_pipeline.py::test_window_boundary_computation PASSED   [ 52%]
tests/test_phase3_pipeline.py::test_window_generator_blocked_error_enforcement PASSED [ 53%]
tests/test_phase3_pipeline.py::test_phase3_artifacts_exist PASSED        [ 55%]
tests/test_phase3_pipeline.py::test_run_manifest_content PASSED          [ 56%]
tests/test_same_file_pairing.py::test_same_file_pairing_detection PASSED [ 58%]
tests/test_signal_quality.py::test_empty_signal_detection PASSED         [ 59%]
tests/test_signal_quality.py::test_nan_and_inf_detection PASSED          [ 61%]
tests/test_signal_quality.py::test_constant_signal_detection PASSED      [ 62%]
tests/test_signal_quality.py::test_near_constant_signal_detection PASSED [ 64%]
tests/test_signal_quality.py::test_non_numeric_signal_detection PASSED   [ 65%]
tests/test_signal_quality.py::test_reference_hr_bounds_and_zeros PASSED  [ 67%]
tests/test_signal_quality.py::test_subject_inventory_four_separate_counts PASSED [ 68%]
tests/test_sync_validation.py::TestECGProcessor::test_clean_ecg_nans_isolated PASSED [ 70%]
tests/test_sync_validation.py::TestECGProcessor::test_clean_ecg_nans_no_nans PASSED [ 71%]
tests/test_sync_validation.py::TestECGProcessor::test_detect_r_peaks_synthetic PASSED [ 73%]
tests/test_sync_validation.py::TestECGProcessor::test_detect_r_peaks_insufficient_length PASSED [ 74%]
tests/test_sync_validation.py::TestECGProcessor::test_derive_1hz_ecg_hr PASSED [ 76%]
tests/test_sync_validation.py::TestECGProcessor::test_scan_monitor_hr_lag_sign_convention PASSED [ 77%]
tests/test_sync_validation.py::TestECGProcessor::test_scan_monitor_hr_lag_ambiguous PASSED [ 79%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_resample_signals_to_2000hz PASSED [ 80%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_resample_signals_truncated PASSED [ 82%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_compute_respiratory_xcorr_known_lag PASSED [ 83%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_compute_respiratory_xcorr_polarity_inversion PASSED [ 85%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_compute_respiratory_xcorr_low_variation PASSED [ 86%]
tests/test_sync_validation.py::TestRespiratoryValidator::test_compute_surrogate_respiratory_control PASSED [ 88%]
tests/test_sync_validation.py::TestCardiacRadarValidator::test_extract_radar_cardiac_signal PASSED [ 89%]
tests/test_sync_validation.py::TestCardiacRadarValidator::test_synthetic_known_offset PASSED [ 91%]
tests/test_sync_validation.py::TestCardiacRadarValidator::test_window_level_hr_agreement_synthetic PASSED [ 92%]
tests/test_timing_validation.py::test_duration_1d_array PASSED           [ 94%]
tests/test_timing_validation.py::test_duration_invalid_fs PASSED         [ 95%]
tests/test_timing_validation.py::test_duration_uncertain_2d_orientation PASSED [ 97%]
tests/test_timing_validation.py::test_duration_verified_2d_orientation PASSED [ 98%]
tests/test_timing_validation.py::test_synchronization_audit_unverified PASSED [100%]

============================= 67 passed in 6.21s ==============================
```

- **Total Tests Collected:** 67
- **Total Tests Passing:** 67 (100%)
- **Total Tests Failing:** 0 (0%)
- **Test Baseline:** 48 Phase 1 & 2 tests + 19 Phase 3 tests = 67 tests confirmed passing.

---

## 3. Physical Deliverable Inventory Verification

Every expected Phase 3 file was verified directly on the local filesystem:

| File / Artifact Path | Verification Status | Size (Bytes) | Observations |
| :--- | :---: | :---: | :--- |
| `src/phase3/__init__.py` | **VERIFIED** | 123 | Module namespace initialized. |
| `src/phase3/mat_loader.py` | **VERIFIED** | 8,141 | `RobustMatLoader` supporting v5/v7 MAT files. |
| `src/phase3/synchronization.py` | **VERIFIED** | 4,517 | `SynchronizationManager` with explicit time axes. |
| `src/phase3/ecg_reference.py` | **VERIFIED** | 10,670 | In-memory NaN interpolation, Pan-Tompkins QRS, SQI. |
| `src/phase3/radar_preprocessing.py` | **VERIFIED** | 5,893 | Filter design, Nyquist checking, spectral power ratios. |
| `src/phase3/window_generator.py` | **VERIFIED** | 3,975 | 10s/5s boundaries and blocker enforcement. |
| `src/phase3/runner.py` | **VERIFIED** | 21,022 | End-to-end execution orchestrator. |
| `tests/test_phase3_pipeline.py` | **VERIFIED** | 13,648 | 19 automated unit and regression tests. |
| `outputs/phase3/run_001/run_manifest.json` | **VERIFIED** | 947 | Preflight run manifest documenting blocker status. |
| `outputs/phase3/run_001/phase3_report.md` | **VERIFIED** | 18,137 | Comprehensive Phase 3 audit report (15 sections). |
| `outputs/phase3/run_001/synchronization_manifest.csv` | **VERIFIED** | 19,079 | 48 recording pair timing records. |
| `outputs/phase3/run_001/synchronization_audit.md` | **VERIFIED** | 1,196 | Audit notes on timing conventions and mismatches. |
| `outputs/phase3/run_001/ecg_quality_manifest.csv` | **VERIFIED** | 5,935 | 47 rows with SQI metrics. |
| `outputs/phase3/run_001/rpeak_detection_summary.csv` | **VERIFIED** | 3,192 | R-peak counts and HR statistics. |
| `outputs/phase3/run_001/ecg_quality_report.md` | **VERIFIED** | 682 | Summary of periodic NaNs and SQI screening. |
| `outputs/phase3/run_001/radar_preprocessing_manifest.csv`| **VERIFIED** | 10,063 | Radar sampling rate and Nyquist validation. |
| `outputs/phase3/run_001/preprocessing_comparison.csv` | **VERIFIED** | 4,355 | Spectral power comparisons across 3 filter states. |
| `outputs/phase3/run_001/preprocessing_report.md` | **VERIFIED** | 1,008 | Comparative evaluation of candidate filters. |
| `outputs/phase3/run_001/window_segmentation_diagnostics.csv`| **VERIFIED** | 3,736 | 22 windows per recording and tail exclusion metrics. |
| `outputs/phase3/run_001/plots/plot1_plot2_radar_preprocessing.png` | **VERIFIED** | 199,100 | Visual filter comparison waveform. |
| `outputs/phase3/run_001/plots/plot3_ecg_rpeaks.png` | **VERIFIED** | 100,464 | Cleaned ECG Lead II waveform with detected peaks. |
| `outputs/phase3/run_001/plots/plot4_ecg_quality_sqi_summary.png` | **VERIFIED** | 54,226 | Delimiter NaN and RR coverage distributions. |
| `outputs/phase3/run_001/plots/plot5_window_counts.png` | **VERIFIED** | 48,012 | Window count distribution by subject and condition. |
| `outputs/phase3/run_001/plots/plot6_reference_hr_gate_status.png` | **VERIFIED** | 32,431 | Gate blocker status banner. |
| `outputs/phase3/run_001/plots/plot7_time_alignment_diagram.png` | **VERIFIED** | 63,566 | Nominal zero-offset relative time diagram. |
