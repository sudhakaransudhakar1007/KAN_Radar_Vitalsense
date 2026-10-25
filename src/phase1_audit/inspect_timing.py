"""Timing and synchronization audit module."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def compute_duration_seconds(
    shape: Tuple[int, ...],
    fs: float,
    verified_time_axis: Optional[int] = None,
) -> Tuple[Optional[float], str, str]:
    """Compute duration strictly per Final Patch 3 rule.

    DURATION: Only when both are verified, duration_seconds = n_samples / fs_hz,
    where n_samples is taken along the axis verified as time. Check that fs is finite and > 0.
    If the time axis is uncertain, report both candidate axes, mark POSSIBLY_TRANSPOSED, do not pick one.

    Returns:
        (duration_seconds_or_none, orientation_status, notes)
    """
    if not np.isfinite(fs) or fs <= 0:
        return None, "INVALID_FS", f"fs={fs} is not finite and positive"

    if len(shape) == 1:
        # 1D vector: axis 0 is the single sample axis
        duration = float(shape[0]) / float(fs)
        return round(duration, 4), "CONFIRMED_1D", f"{shape[0]} samples at {fs} Hz = {duration:.4f} s"

    if len(shape) == 2:
        if verified_time_axis is not None and verified_time_axis in (0, 1):
            n_samples = shape[verified_time_axis]
            duration = float(n_samples) / float(fs)
            return round(duration, 4), "VERIFIED_AXIS", f"Axis {verified_time_axis} ({n_samples} samples) at {fs} Hz = {duration:.4f} s"

        # Uncertain 2D axis: do NOT pick one, report POSSIBLY_TRANSPOSED
        cand_0 = float(shape[0]) / float(fs)
        cand_1 = float(shape[1]) / float(fs)
        return None, "POSSIBLY_TRANSPOSED", f"Time axis uncertain: shape={shape}. Axis 0 -> {cand_0:.4f} s, Axis 1 -> {cand_1:.4f} s"

    return None, "POSSIBLY_TRANSPOSED", f"Multidimensional shape={shape}; time axis unverified"


def audit_synchronization_pair(
    radar_info: Dict[str, Any],
    reference_info: Dict[str, Any],
) -> Dict[str, Any]:
    """Audit timing and synchronization for a candidate radar-reference pair per Section 5."""
    sub_id = radar_info.get("subject_id", reference_info.get("subject_id", "UNKNOWN"))
    cond = radar_info.get("condition", reference_info.get("condition", "UNKNOWN"))

    rad_fs = float(radar_info.get("fs", 333.3333333333333))
    rad_shape = radar_info.get("shape", (40000,))
    rad_samples = rad_shape[0] if len(rad_shape) > 0 else 0

    ref_fs_ecg = float(reference_info.get("fs_ecg", 500))
    ref_ecg_shape = reference_info.get("ecg_shape", (60000,))
    ref_ecg_samples = ref_ecg_shape[0] if len(ref_ecg_shape) > 0 else 0

    ref_hr_shape = reference_info.get("hr_shape", (120,))
    ref_hr_samples = ref_hr_shape[0] if len(ref_hr_shape) > 0 else 0

    # Compute durations
    rad_dur, _, _ = compute_duration_seconds(rad_shape, rad_fs)
    ecg_dur, _, _ = compute_duration_seconds(ref_ecg_shape, ref_fs_ecg)

    # Descriptive comparison only; equal duration does NOT prove synchronization
    duration_match = bool(rad_dur is not None and ecg_dur is not None and rad_dur == ecg_dur)

    # Trigger / timestamp evidence
    timestamp_trigger_evidence = (
        "Radar MAT file contains MeasurementInfo with date-time string (e.g. '2025-03-10_12-05-36'); "
        "Mindray reference MAT file contains no internal hardware clock, start time, or trigger pulse marker."
    )

    # HR temporal interpretation (Rule 2.3)
    hr_temporal_interpretation = (
        "UNVERIFIED_TEMPORAL_INTERPRETATION: 120 points observed over nominal 120s duration. "
        "Documentation does not verify whether points represent instantaneous beat-to-beat rate, "
        "rolling 1-second averages, or monitor display refresh intervals."
    )

    # Timing and synchronization status (Rule 2.2)
    sync_status = "UNVERIFIED_TIMING"
    missing_timing_metadata = "Shared hardware clock timestamps, common trigger event pulse, or documented offset"

    evidence = (
        f"Radar: {rad_samples} samples @ {rad_fs:.4f} Hz -> {rad_dur}s. "
        f"Reference ECG: {ref_ecg_samples} samples @ {ref_fs_ecg:.1f} Hz -> {ecg_dur}s. "
        f"Reference HR: {ref_hr_samples} samples. "
        "Nominal durations match (120.0s), but independent clock verification is absent."
    )

    notes = (
        "Timing alignment cannot be verified from MAT file headers alone. "
        "Equal durations and folder-matching do NOT establish sub-second temporal synchronization. "
        "Independent hardware clock synchronization or shared trigger pulse is undocumented. "
        "Window-level alignment for supervised training is unverified."
    )

    return {
        "radar_relative_path": radar_info.get("relative_path", ""),
        "reference_relative_path": reference_info.get("relative_path", ""),
        "subject_id": sub_id,
        "condition": cond,
        "radar_sample_count": rad_samples,
        "radar_fs_hz": round(rad_fs, 4),
        "radar_duration_seconds": rad_dur,
        "ref_ecg_sample_count": ref_ecg_samples,
        "ref_ecg_fs_hz": round(ref_fs_ecg, 1),
        "ref_ecg_duration_seconds": ecg_dur,
        "ref_hr_sample_count": ref_hr_samples,
        "hr_temporal_interpretation": hr_temporal_interpretation,
        "timestamp_trigger_evidence": timestamp_trigger_evidence,
        "duration_match": duration_match,
        "synchronization_status": sync_status,
        "missing_timing_metadata": missing_timing_metadata,
        "evidence": evidence,
        "notes": notes,
    }
