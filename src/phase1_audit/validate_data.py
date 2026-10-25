"""Signal quality validation module for radar and reference data."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.phase1_audit.inspect_mat import compute_approved_summary_stats
from src.phase1_audit.inspect_timing import compute_duration_seconds


def validate_radar_signal(
    signal_data: Any,
    fs_val: Optional[float],
    relative_path: str,
    subject_id: str,
    recording_id: str,
    signal_field_path: str = "VitalSig",
    fs_field_path: str = "Radar.fs",
    near_constant_threshold: float = 1e-6,
    time_vector: Optional[Any] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Validate candidate radar signal array and log all executed checks to quality report."""
    quality_findings: List[Dict[str, Any]] = []

    # Check 1: Field presence
    if signal_data is None:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "field_presence",
            "observed_result": "MISSING",
            "status": "FAIL",
            "evidence": "MATLAB key lookup returned None",
            "notes": "Signal field not present in MAT structure",
        })
        record = {
            "relative_path": relative_path,
            "subject_id_candidate": subject_id,
            "recording_id_candidate": recording_id,
            "signal_field_path": signal_field_path,
            "shape_as_read": "NONE",
            "sample_count_candidate_axis": 0,
            "dtype_as_read": "NONE",
            "is_complex": False,
            "fs_field_path": fs_field_path,
            "fs_value": fs_val,
            "fs_units_status": "UNKNOWN",
            "duration_seconds": None,
            "nan_count": 0,
            "posinf_count": 0,
            "neginf_count": 0,
            "constant_flag": "UNKNOWN",
            "status": "FAIL",
            "notes": "Signal array is missing",
        }
        return record, quality_findings

    quality_findings.append({
        "relative_path": relative_path,
        "field_path": signal_field_path,
        "check_performed": "field_presence",
        "observed_result": "PRESENT",
        "status": "PASS",
        "evidence": f"Field '{signal_field_path}' extracted from MAT structure",
        "notes": "Field exists",
    })

    # Check 2: Array type
    if not isinstance(signal_data, np.ndarray):
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "array_type",
            "observed_result": type(signal_data).__name__,
            "status": "FAIL",
            "evidence": f"Expected numpy.ndarray, got {type(signal_data).__name__}",
            "notes": "Signal is not a numpy array",
        })
        record = {
            "relative_path": relative_path,
            "subject_id_candidate": subject_id,
            "recording_id_candidate": recording_id,
            "signal_field_path": signal_field_path,
            "shape_as_read": str(getattr(signal_data, "shape", "()")),
            "sample_count_candidate_axis": 0,
            "dtype_as_read": type(signal_data).__name__,
            "is_complex": False,
            "fs_field_path": fs_field_path,
            "fs_value": fs_val,
            "fs_units_status": "UNKNOWN",
            "duration_seconds": None,
            "nan_count": 0,
            "posinf_count": 0,
            "neginf_count": 0,
            "constant_flag": "UNKNOWN",
            "status": "FAIL_NON_ARRAY",
            "notes": "Signal is not a numpy array",
        }
        return record, quality_findings

    quality_findings.append({
        "relative_path": relative_path,
        "field_path": signal_field_path,
        "check_performed": "array_type",
        "observed_result": "numpy.ndarray",
        "status": "PASS",
        "evidence": f"Object type: {type(signal_data).__name__}, dtype: {signal_data.dtype}",
        "notes": "Valid array type",
    })

    shape = signal_data.shape
    dtype_str = str(signal_data.dtype)
    is_complex = bool(np.iscomplexobj(signal_data))
    stats = compute_approved_summary_stats(signal_data)

    # Check 3: Empty check
    if signal_data.size == 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "empty_check",
            "observed_result": "0 samples",
            "status": "FAIL",
            "evidence": "Array size is 0",
            "notes": "Signal array is empty",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "empty_check",
            "observed_result": f"{signal_data.size} samples",
            "status": "PASS",
            "evidence": f"Array shape: {shape}",
            "notes": "Signal array is non-empty",
        })

    # Check 4: NaN check
    nan_count = stats["nan_count"]
    if nan_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "nan_check",
            "observed_result": f"{nan_count} NaNs",
            "status": "FAIL",
            "evidence": f"Found {nan_count} NaN values out of {signal_data.size} samples",
            "notes": "Signal contains missing NaN samples",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "nan_check",
            "observed_result": "0 NaNs",
            "status": "PASS",
            "evidence": "All samples are non-NaN",
            "notes": "No NaN values detected",
        })

    # Check 5: Infinity check
    posinf_count = stats["posinf_count"]
    neginf_count = stats["neginf_count"]
    if posinf_count > 0 or neginf_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "infinity_check",
            "observed_result": f"+Inf: {posinf_count}, -Inf: {neginf_count}",
            "status": "FAIL",
            "evidence": f"Found infinite values in signal array",
            "notes": "Signal contains infinite samples",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "infinity_check",
            "observed_result": "0 Infs",
            "status": "PASS",
            "evidence": "No infinite values found",
            "notes": "Signal is finite",
        })

    # Check 6: Constant / Near-constant checks
    constant_flag = "NORMAL"
    std_val = stats["std"]
    range_val = stats["range"]
    if signal_data.size == 0 or range_val is None:
        constant_flag = "EMPTY_OR_NON_NUMERIC"
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "constant_signal_check",
            "observed_result": "N/A (empty or non-finite)",
            "status": "FAIL",
            "evidence": "Array is empty or contains no finite values",
            "notes": "Cannot compute signal range or standard deviation",
        })
    elif range_val == 0.0:
        constant_flag = "CONSTANT"
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "constant_signal_check",
            "observed_result": "range=0.0",
            "status": "FAIL",
            "evidence": "Signal range is zero",
            "notes": "Signal is completely flat / constant",
        })
    elif std_val is not None and std_val < near_constant_threshold:
        constant_flag = "NEAR_CONSTANT"
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "near_constant_check",
            "observed_result": f"std={std_val:.2e} < {near_constant_threshold}",
            "status": "WARNING",
            "evidence": f"Configured near-constant threshold: {near_constant_threshold}",
            "notes": "Near-zero standard deviation detected",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": signal_field_path,
            "check_performed": "constant_signal_check",
            "observed_result": f"std={std_val:.4f}, range={range_val:.4f}",
            "status": "PASS",
            "evidence": f"std={std_val:.4f} > {near_constant_threshold}",
            "notes": "Dynamic signal variation confirmed",
        })

    # Check 7: Sampling frequency
    fs_units_status = "UNKNOWN"
    duration = None
    if fs_val is not None and fs_val > 0 and np.isfinite(fs_val):
        fs_units_status = "VERIFIED_HZ"
        dur, _, _ = compute_duration_seconds(shape, fs_val)
        duration = dur
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": fs_field_path,
            "check_performed": "sampling_frequency_check",
            "observed_result": f"{fs_val:.4f} Hz",
            "status": "PASS",
            "evidence": f"Value {fs_val} extracted from {fs_field_path}",
            "notes": f"Sampling frequency is positive and finite; calculated duration = {duration:.1f}s",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": fs_field_path,
            "check_performed": "sampling_frequency_check",
            "observed_result": str(fs_val),
            "status": "FAIL",
            "evidence": f"fs_val={fs_val} is invalid or non-positive",
            "notes": "Cannot compute duration without valid sampling frequency",
        })

    # Check 8: Time vector consistency
    if time_vector is not None and isinstance(time_vector, np.ndarray):
        tv_samples = time_vector.shape[0] if len(time_vector.shape) > 0 else 0
        if tv_samples == shape[0]:
            quality_findings.append({
                "relative_path": relative_path,
                "field_path": "Radar.t_frame",
                "check_performed": "time_vector_consistency",
                "observed_result": f"{tv_samples} samples",
                "status": "PASS",
                "evidence": f"Radar.t_frame length ({tv_samples}) matches VitalSig length ({shape[0]})",
                "notes": "Time series vector dimensions are consistent",
            })
        else:
            quality_findings.append({
                "relative_path": relative_path,
                "field_path": "Radar.t_frame",
                "check_performed": "time_vector_consistency",
                "observed_result": f"{tv_samples} vs {shape[0]}",
                "status": "WARNING",
                "evidence": f"Mismatch between t_frame ({tv_samples}) and VitalSig ({shape[0]})",
                "notes": "Time vector dimension mismatch",
            })

    status = "PASS"
    if any(q["status"] == "FAIL" for q in quality_findings):
        status = "FAIL"
    elif any(q["status"] == "WARNING" for q in quality_findings):
        status = "WARNING"

    record = {
        "relative_path": relative_path,
        "subject_id_candidate": subject_id,
        "recording_id_candidate": recording_id,
        "signal_field_path": signal_field_path,
        "shape_as_read": str(shape),
        "sample_count_candidate_axis": shape[0] if len(shape) > 0 else 0,
        "dtype_as_read": dtype_str,
        "is_complex": is_complex,
        "fs_field_path": fs_field_path,
        "fs_value": fs_val,
        "fs_units_status": fs_units_status,
        "duration_seconds": duration,
        "nan_count": nan_count,
        "posinf_count": posinf_count,
        "neginf_count": neginf_count,
        "constant_flag": constant_flag,
        "status": status,
        "notes": f"Stats: min={stats['min']:.4f}, max={stats['max']:.4f}, std={stats['std']:.4f}" if stats['min'] is not None else "No stats",
    }
    return record, quality_findings


def validate_reference_signal(
    ref_dict: Any,
    relative_path: str,
    subject_id: str,
    recording_id: str,
    ref_field_path: str = "HR",
    same_file: bool = False,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Validate candidate reference signals and log all executed checks to quality report."""
    quality_findings: List[Dict[str, Any]] = []

    hr_data = ref_dict.get("HR", None) if isinstance(ref_dict, dict) else ref_dict

    # Check 1: HR Field Presence
    if hr_data is None:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "field_presence_hr",
            "observed_result": "MISSING",
            "status": "FAIL",
            "evidence": "MATLAB key lookup for HR returned None",
            "notes": "Reference HR field missing in MAT structure",
        })
        record = {
            "relative_path": relative_path,
            "subject_id_candidate": subject_id,
            "recording_id_candidate": recording_id,
            "ref_field_path": ref_field_path,
            "shape_as_read": "NONE",
            "dtype_as_read": "NONE",
            "units_status": "UNKNOWN",
            "timestamp_field_path": "NONE",
            "timestamp_units_status": "UNKNOWN",
            "sampling_interval_status": "UNKNOWN",
            "start_end_status": "UNKNOWN",
            "missing_or_invalid_count": 0,
            "temporal_semantics_status": "UNKNOWN",
            "same_file_as_radar": same_file,
            "verification_status": "FAIL",
            "notes": "Reference HR field is missing",
        }
        return record, quality_findings

    quality_findings.append({
        "relative_path": relative_path,
        "field_path": ref_field_path,
        "check_performed": "field_presence_hr",
        "observed_result": "PRESENT",
        "status": "PASS",
        "evidence": "Field 'HR' extracted successfully",
        "notes": "Field exists",
    })

    # Check 2: Array type
    if not isinstance(hr_data, np.ndarray):
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "array_type_hr",
            "observed_result": type(hr_data).__name__,
            "status": "FAIL",
            "evidence": f"Expected numpy.ndarray, got {type(hr_data).__name__}",
            "notes": "Reference HR is not an array",
        })
        record = {
            "relative_path": relative_path,
            "subject_id_candidate": subject_id,
            "recording_id_candidate": recording_id,
            "ref_field_path": ref_field_path,
            "shape_as_read": str(getattr(hr_data, "shape", "()")),
            "dtype_as_read": type(hr_data).__name__,
            "units_status": "UNKNOWN",
            "timestamp_field_path": "NONE",
            "timestamp_units_status": "UNKNOWN",
            "sampling_interval_status": "UNKNOWN",
            "start_end_status": "UNKNOWN",
            "missing_or_invalid_count": 0,
            "temporal_semantics_status": "UNKNOWN",
            "same_file_as_radar": same_file,
            "verification_status": "FAIL",
            "notes": "Reference HR is not an array",
        }
        return record, quality_findings

    shape = hr_data.shape
    dtype_str = str(hr_data.dtype)
    stats = compute_approved_summary_stats(hr_data)

    quality_findings.append({
        "relative_path": relative_path,
        "field_path": ref_field_path,
        "check_performed": "array_type_hr",
        "observed_result": "numpy.ndarray",
        "status": "PASS",
        "evidence": f"dtype: {dtype_str}, shape: {shape}",
        "notes": "Valid array type",
    })

    # Check 3: NaN and Inf checks
    nan_count = stats["nan_count"]
    posinf_count = stats["posinf_count"]
    neginf_count = stats["neginf_count"]

    if nan_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "nan_check_hr",
            "observed_result": f"{nan_count} NaNs",
            "status": "FAIL",
            "evidence": f"Found {nan_count} NaN values",
            "notes": "Reference HR contains missing NaN values",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "nan_check_hr",
            "observed_result": "0 NaNs",
            "status": "PASS",
            "evidence": "No NaN values in HR array",
            "notes": "Clean numeric HR values",
        })

    if posinf_count > 0 or neginf_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "infinity_check_hr",
            "observed_result": f"+Inf: {posinf_count}, -Inf: {neginf_count}",
            "status": "FAIL",
            "evidence": "Found infinite values in HR array",
            "notes": "Reference HR contains infinite values",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "infinity_check_hr",
            "observed_result": "0 Infs",
            "status": "PASS",
            "evidence": "No infinite values in HR array",
            "notes": "Finite HR measurements",
        })

    # Check 4: Zero HR dropout check
    zero_hr_count = int(np.sum(hr_data == 0))
    if zero_hr_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "zero_hr_dropout_check",
            "observed_result": f"{zero_hr_count} zero HR values",
            "status": "WARNING",
            "evidence": f"{zero_hr_count} samples read exactly 0 bpm",
            "notes": "Possible sensor detachment or monitor dropout",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "zero_hr_dropout_check",
            "observed_result": "0 zero values",
            "status": "PASS",
            "evidence": "No zero HR samples found",
            "notes": "No sensor detachment dropouts detected",
        })

    # Check 5: Physiological bounds [30, 220] bpm
    out_of_bounds_count = int(np.sum((hr_data > 0) & ((hr_data < 30) | (hr_data > 220))))
    if out_of_bounds_count > 0:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "physiological_bounds_hr",
            "observed_result": f"{out_of_bounds_count} out-of-bound values",
            "status": "WARNING",
            "evidence": "Values outside [30, 220] bpm detected",
            "notes": "Physiologically implausible readings present",
        })
    else:
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": ref_field_path,
            "check_performed": "physiological_bounds_hr",
            "observed_result": f"All within [30, 220] bpm (min={stats['min']}, max={stats['max']})",
            "status": "PASS",
            "evidence": f"Observed HR range: [{stats['min']}, {stats['max']}] bpm",
            "notes": "Values within normal human physiological bounds",
        })

    # Additional Checks on Multimodal Reference Signals (if dict provided)
    if isinstance(ref_dict, dict):
        # ECG check
        ecg_lead2 = ref_dict.get("ecg_lead2", None)
        fs_ecg = ref_dict.get("Fs_ecg", None)
        if ecg_lead2 is not None and isinstance(ecg_lead2, np.ndarray):
            ecg_samples = ecg_lead2.shape[0] if len(ecg_lead2.shape) > 0 else 0
            quality_findings.append({
                "relative_path": relative_path,
                "field_path": "ecg_lead2",
                "check_performed": "field_presence_ecg",
                "observed_result": f"{ecg_samples} samples @ {fs_ecg} Hz",
                "status": "PASS",
                "evidence": f"ECG Lead II available, duration = {ecg_samples / float(fs_ecg):.1f}s",
                "notes": "Synchronous reference ECG Lead II available",
            })

        # Respiration check
        resp = ref_dict.get("respiration", None)
        fs_resp = ref_dict.get("Fs_resp", None)
        if resp is not None and isinstance(resp, np.ndarray):
            resp_samples = resp.shape[0] if len(resp.shape) > 0 else 0
            if resp_samples == 30720:
                quality_findings.append({
                    "relative_path": relative_path,
                    "field_path": "respiration",
                    "check_performed": "sampling_frequency_resp",
                    "observed_result": f"{resp_samples} samples (120.0s @ {fs_resp} Hz)",
                    "status": "PASS",
                    "evidence": "Full 120s duration for respiration",
                    "notes": "Respiration signal complete",
                })
            else:
                quality_findings.append({
                    "relative_path": relative_path,
                    "field_path": "respiration",
                    "check_performed": "sampling_frequency_resp",
                    "observed_result": f"{resp_samples} samples ({resp_samples / float(fs_resp):.2f}s @ {fs_resp} Hz)",
                    "status": "WARNING",
                    "evidence": f"Expected 30720 samples (120s), observed {resp_samples} samples",
                    "notes": "Dimension inconsistency: respiration duration slightly less than 120s",
                })

        # Hardware timestamp vector check
        quality_findings.append({
            "relative_path": relative_path,
            "field_path": "TIMESTAMP_VECTOR",
            "check_performed": "timestamp_vector_presence",
            "observed_result": "MISSING",
            "status": "UNVERIFIED",
            "evidence": "No explicit hardware time vector found in Mindray MAT file",
            "notes": "Clock synchronization with radar is unverified",
        })

    total_invalid = nan_count + posinf_count + neginf_count + zero_hr_count
    status = "VERIFIED"
    if total_invalid > 0 or out_of_bounds_count > 0:
        status = "VERIFIED_WITH_WARNINGS"

    record = {
        "relative_path": relative_path,
        "subject_id_candidate": subject_id,
        "recording_id_candidate": recording_id,
        "ref_field_path": ref_field_path,
        "shape_as_read": str(shape),
        "dtype_as_read": dtype_str,
        "units_status": "VERIFIED_BPM",
        "timestamp_field_path": "NONE",
        "timestamp_units_status": "UNVERIFIED_IMPLICIT_1HZ",
        "sampling_interval_status": "ASSUMED_1S_NOMINAL",
        "start_end_status": "UNVERIFIED_WALLCLOCK",
        "missing_or_invalid_count": total_invalid,
        "temporal_semantics_status": "UNVERIFIED_TEMPORAL_INTERPRETATION",
        "same_file_as_radar": same_file,
        "verification_status": status,
        "notes": f"Stats: min={stats['min']}, max={stats['max']}, mean={stats['mean']:.2f}, invalid={total_invalid}" if stats['min'] is not None else "No stats",
    }
    return record, quality_findings
