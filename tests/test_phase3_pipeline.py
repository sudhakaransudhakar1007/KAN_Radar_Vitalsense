"""Comprehensive test suite for Phase 3 pipeline components.

Tests:
1. RobustMatLoader: format detection, channel extraction, metadata tracking, and error handling.
2. SynchronizationManager: time-axis construction (t_n = t_0 + n/f_s), hardware clock UNVERIFIED marking.
3. ECGReferenceValidator: NaN pattern detection, linear interpolation, Pan-Tompkins QRS detection, SQI diagnostics.
4. RadarPreprocessor: Nyquist validation, bandpass filtering, power spectral ratio computation.
5. WindowGenerator: 10s/5s sliding window boundary calculation, tail accounting, LabelGenerationBlockedError enforcement.
6. Phase 3 Pipeline Outputs: verification of all 11 output files and 6 diagnostic plots in outputs/phase3/run_001.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import scipy.io as sio

from src.phase3.ecg_reference import ECGReferenceValidator
from src.phase3.mat_loader import RobustMatLoader
from src.phase3.radar_preprocessing import RadarPreprocessor
from src.phase3.synchronization import SynchronizationManager
from src.phase3.window_generator import WindowGenerator, LabelGenerationBlockedError


# ==============================================================================
# 1. RobustMatLoader Tests
# ==============================================================================

def test_mat_loader_file_not_found():
    loader = RobustMatLoader()
    with pytest.raises(FileNotFoundError):
        loader.inspect_mat_version("non_existent_file.mat")


def test_mat_loader_mock_radar(tmp_path):
    loader = RobustMatLoader()
    mat_file = tmp_path / "mock_radar.mat"

    # Create mock radar MAT file
    fake_vitsig = np.sin(np.linspace(0, 10, 1000)).reshape(-1, 1)
    sio.savemat(str(mat_file), {"VitalSig": fake_vitsig, "Radar": {"fs": 333.3333}})

    rec = loader.load_radar_mat(mat_file)
    assert rec.file_type == "radar"
    assert rec.mat_version == "MATLAB_v5_v7"
    assert "VitalSig" in rec.channels
    assert rec.channel_metadata["VitalSig"].sampling_rate_hz == pytest.approx(333.3333, rel=1e-3)
    assert rec.channel_metadata["VitalSig"].finite_count == 1000
    assert rec.channel_metadata["VitalSig"].nan_count == 0
    assert len(rec.validation_errors) == 0


def test_mat_loader_missing_required_variable(tmp_path):
    loader = RobustMatLoader()
    mat_file = tmp_path / "empty_radar.mat"
    sio.savemat(str(mat_file), {"unrelated_var": np.zeros(10)})

    rec = loader.load_radar_mat(mat_file)
    assert len(rec.validation_errors) > 0
    assert "Missing required variable 'VitalSig'" in rec.validation_errors[0]


def test_mat_loader_mock_reference(tmp_path):
    loader = RobustMatLoader()
    mat_file = tmp_path / "mock_Mindray.mat"

    fake_ecg = np.zeros(500)
    fake_ecg[100] = np.nan  # 1 isolated delimiter NaN
    fake_hr = np.ones(10) * 75.0
    fake_resp = np.zeros(256)

    sio.savemat(
        str(mat_file),
        {
            "ecg_lead2": fake_ecg,
            "HR": fake_hr,
            "respiration": fake_resp,
            "param": {"Fs_ecg": 500.0, "Fs_resp": 256.0},
        },
    )

    rec = loader.load_reference_mat(mat_file)
    assert rec.file_type == "reference"
    assert "ecg_lead2" in rec.channels
    assert "HR" in rec.channels
    assert "respiration" in rec.channels
    assert rec.channel_metadata["ecg_lead2"].nan_count == 1
    assert rec.channel_metadata["ecg_lead2"].finite_count == 499
    assert rec.channel_metadata["ecg_lead2"].sampling_rate_hz == 500.0


# ==============================================================================
# 2. SynchronizationManager Tests
# ==============================================================================

def test_sync_manager_time_axis_construction():
    sync = SynchronizationManager()
    fs = 100.0
    n = 500
    axis = sync.build_time_axis(
        channel_name="test_channel",
        sample_count=n,
        fs_hz=fs,
        t0_s=0.0,
    )

    assert axis.channel_name == "test_channel"
    assert axis.sample_count == n
    assert axis.sampling_rate_hz == fs
    assert len(axis.time_array) == n
    assert axis.time_array[0] == 0.0
    assert axis.time_array[1] == pytest.approx(1.0 / fs)
    assert axis.time_array[-1] == pytest.approx((n - 1) / fs)


def test_sync_manager_invalid_frequency_or_samples():
    sync = SynchronizationManager()
    with pytest.raises(ValueError):
        sync.build_time_axis("ch", sample_count=100, fs_hz=0.0)
    with pytest.raises(ValueError):
        sync.build_time_axis("ch", sample_count=0, fs_hz=100.0)


def test_sync_manager_unverified_hardware_status():
    sync = SynchronizationManager()
    rec = sync.evaluate_pair_synchronization(
        subject_id="VS01",
        condition="Resting",
        radar_file="VS01_Resting.mat",
        reference_file="VS01_Resting_Mindray.mat",
        radar_len=40000,
        radar_fs=333.3333,
        ecg_len=60000,
        ecg_fs=500.0,
        resp_len=30720,
        resp_fs=256.0,
        mon_hr_len=120,
        mon_hr_fs=1.0,
    )

    assert rec.hardware_clock_status == "UNVERIFIED"
    assert rec.synchronization_confidence == "UNVERIFIED_HARDWARE_TIMING"
    assert rec.cross_device_offset_s == 0.0
    assert rec.radar_duration_s == pytest.approx(120.0, rel=1e-3)
    assert rec.ecg_duration_s == pytest.approx(120.0, rel=1e-3)


# ==============================================================================
# 3. ECGReferenceValidator Tests
# ==============================================================================

def test_ecg_nan_analysis_zero_nans():
    val = ECGReferenceValidator()
    ecg = np.random.randn(1000)
    analysis = val.analyze_missing_samples(ecg)

    assert analysis.nan_count == 0
    assert analysis.interpolation_eligible is True
    assert analysis.cleaned_ecg_in_memory is not None
    assert np.array_equal(analysis.cleaned_ecg_in_memory, ecg)


def test_ecg_nan_linear_interpolation():
    val = ECGReferenceValidator()
    ecg = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
    analysis = val.analyze_missing_samples(ecg)

    assert analysis.nan_count == 1
    assert analysis.multi_sample_gap_count == 0
    assert analysis.interpolation_eligible is True
    assert analysis.cleaned_ecg_in_memory is not None
    # Check that NaN at index 2 is interpolated to exactly 3.0
    assert analysis.cleaned_ecg_in_memory[2] == pytest.approx(3.0)


def test_ecg_periodic_nans_detection():
    val = ECGReferenceValidator()
    # Create signal with periodic delimiter NaNs every 500 samples
    ecg = np.ones(3500)
    for idx in range(500, 3500, 500):
        ecg[idx] = np.nan
    analysis = val.analyze_missing_samples(ecg)

    assert analysis.nan_count == 6
    assert analysis.is_periodic_single_nan is True
    assert analysis.multi_sample_gap_count == 0
    assert analysis.interpolation_eligible is True


def test_ecg_nan_multi_sample_gap():
    val = ECGReferenceValidator()
    ecg = np.array([1.0, np.nan, np.nan, 4.0, 5.0])
    analysis = val.analyze_missing_samples(ecg)

    assert analysis.nan_count == 2
    assert analysis.multi_sample_gap_count == 1
    assert analysis.is_periodic_single_nan is False
    assert analysis.interpolation_eligible is False
    assert analysis.cleaned_ecg_in_memory is None


def test_ecg_pan_tompkins_qrs_detection():
    val = ECGReferenceValidator(fs_ecg=500.0)
    fs = 500.0
    duration_s = 10.0
    t = np.arange(int(duration_s * fs)) / fs
    ecg = np.zeros_like(t)

    # Inject sharp R-peaks at 1.0s intervals (60 BPM)
    for peak_t in np.arange(1.0, duration_s - 0.5, 1.0):
        idx = int(peak_t * fs)
        ecg[idx - 5 : idx + 5] = 2.0 * np.exp(-0.5 * ((np.arange(-5, 5)) / 1.5) ** 2)

    res = val.detect_r_peaks_pan_tompkins(ecg)
    assert res.detected_peak_count >= 8
    assert res.valid_rr_count >= 7
    assert res.mean_hr_bpm == pytest.approx(60.0, abs=3.0)
    assert res.duplicate_peak_count == 0


def test_ecg_sqi_evaluation_not_approved_guard():
    val = ECGReferenceValidator()
    fs = 500.0
    ecg = np.zeros(int(120.0 * fs))
    # Inject regular peaks
    for t_peak in np.arange(1.0, 119.0, 0.8):  # 75 BPM
        idx = int(t_peak * fs)
        ecg[idx - 5 : idx + 5] = 2.0 * np.exp(-0.5 * ((np.arange(-5, 5)) / 1.5) ** 2)

    rpeak_res = val.detect_r_peaks_pan_tompkins(ecg)
    sqi_res = val.evaluate_sqi(
        subject_id="VS01",
        condition="Resting",
        total_duration_s=120.0,
        nan_count=120,
        rpeak_res=rpeak_res,
    )

    assert sqi_res.proposed_sqi_pass is True
    # Mandatory guard: official eligibility remains NOT_APPROVED pending protocol sign-off
    assert sqi_res.official_label_eligibility == "NOT_APPROVED_PENDING_PROTOCOL_SIGN_OFF"


# ==============================================================================
# 4. RadarPreprocessor Tests
# ==============================================================================

def test_radar_nyquist_validation():
    prep = RadarPreprocessor()
    # High cutoff >= Nyquist should fail
    filtered, valid, note = prep.apply_bandpass(
        np.ones(100),
        30.0,  # Nyquist = 15 Hz
        1.0,
        20.0,  # > 15 Hz
    )
    assert valid is False
    assert "Invalid frequency bounds" in note
    assert np.array_equal(filtered, np.ones(100))


def test_radar_bandpass_filtering():
    prep = RadarPreprocessor()
    fs = 333.3333
    t = np.arange(int(10.0 * fs)) / fs
    # Low frequency 0.2 Hz (respiration), Cardiac frequency 1.5 Hz (90 bpm), High frequency 35 Hz (noise)
    sig = (
        5.0 * np.sin(2 * np.pi * 0.2 * t)
        + 1.0 * np.sin(2 * np.pi * 1.5 * t)
        + 0.5 * np.sin(2 * np.pi * 35.0 * t)
    )

    # Cardiac bandpass: 0.8 to 3.0 Hz
    filtered, valid, note = prep.apply_bandpass(sig, fs, 0.8, 3.0)
    assert valid is True
    assert len(filtered) == len(sig)

    # Respiratory drift and high frequency noise should be attenuated
    stats_raw = prep.compute_stats(sig, fs, "raw")
    stats_filt = prep.compute_stats(filtered, fs, "cardiac_filt")
    assert stats_filt.cardiac_band_power_ratio > stats_raw.cardiac_band_power_ratio


# ==============================================================================
# 5. WindowGenerator Tests
# ==============================================================================

def test_window_boundary_computation():
    gen = WindowGenerator(window_duration_s=10.0, hop_duration_s=5.0)
    fs = 333.3333
    total_samples = 40000  # 120 seconds
    boundaries, tail_samples, tail_dur = gen.compute_window_boundaries(total_samples, fs)

    # With 120s (40000 samps at 333.3333 Hz), 10s window (3333 samps), 5s hop (1667 samps):
    # Fits exactly 22 windows (indices 0 to 21), with 1660 excluded tail samples (4.98s)
    assert len(boundaries) == 22
    assert boundaries[0].start_time_s == 0.0
    assert boundaries[0].end_time_s == 10.0
    assert boundaries[0].radar_sample_start == 0
    assert boundaries[0].radar_sample_end == 3333
    assert boundaries[-1].window_index == 21
    assert tail_samples == 1660
    assert tail_dur == 4.98


def test_window_generator_blocked_error_enforcement():
    gen = WindowGenerator(authorization_granted=False)
    with pytest.raises(LabelGenerationBlockedError) as exc_info:
        gen.execute_supervised_generation()
    assert "Supervised HR-label generation is BLOCKED" in str(exc_info.value)


# ==============================================================================
# 6. Pipeline Artifact Verification Tests (outputs/phase3/run_001)
# ==============================================================================

def test_phase3_artifacts_exist():
    base = Path("outputs/phase3/run_001")
    assert base.exists(), "Phase 3 run_001 directory does not exist"

    required_files = [
        "run_manifest.json",
        "synchronization_manifest.csv",
        "synchronization_audit.md",
        "ecg_quality_manifest.csv",
        "rpeak_detection_summary.csv",
        "ecg_quality_report.md",
        "radar_preprocessing_manifest.csv",
        "preprocessing_comparison.csv",
        "preprocessing_report.md",
        "window_segmentation_diagnostics.csv",
        "phase3_report.md",
    ]

    for fname in required_files:
        p = base / fname
        assert p.exists(), f"Missing required file: {fname}"
        assert p.stat().st_size > 0, f"File is empty: {fname}"

    # Check diagnostic plots
    plots_dir = base / "plots"
    assert plots_dir.exists(), "plots directory does not exist"
    plot_files = [
        "plot1_plot2_radar_preprocessing.png",
        "plot3_ecg_rpeaks.png",
        "plot4_ecg_quality_sqi_summary.png",
        "plot5_window_counts.png",
        "plot6_reference_hr_gate_status.png",
        "plot7_time_alignment_diagram.png",
    ]
    for pfile in plot_files:
        ppath = plots_dir / pfile
        assert ppath.exists(), f"Missing plot: {pfile}"
        assert ppath.stat().st_size > 0, f"Plot file is empty: {pfile}"


def test_run_manifest_content():
    manifest_path = Path("outputs/phase3/run_001/run_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["run_id"] == "run_001"
    assert manifest["total_candidate_pairs"] == 48
    assert manifest["total_radar_files_evaluated"] == 48
    assert manifest["total_reference_files_evaluated"] == 48
    assert manifest["phase2a_finalization_gate_status"] == "OPEN"
    assert manifest["supervised_hr_label_generation_status"] == "NOT_YET_APPROVED_HALTED"
    assert "Supervised HR-label generation is BLOCKED" in manifest["blocker_reason"]
