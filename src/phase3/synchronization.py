"""Synchronization and reference-time mapping module for Phase 3.

Adheres to strict evidence hierarchy:
1. Verified timestamps or physical sync markers (ABSENT in VITALSENSE).
2. Documented acquisition timing conventions supported by metadata.
3. Explicitly labeled UNVERIFIED timing assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class TimeAxis:
    """Explicit sample time axis for a discrete physiological/radar channel."""
    channel_name: str
    sample_count: int
    sampling_rate_hz: float
    t0_seconds: float
    time_array: np.ndarray
    timing_confidence: str  # 'VERIFIED_HARDWARE', 'DOCUMENTED_NOMINAL', 'UNVERIFIED_ASSUMPTION'
    timing_notes: str


@dataclass
class SynchronizationRecord:
    """Synchronization assessment for a radar-reference recording pair."""
    subject_id: str
    condition: str
    radar_file: str
    reference_file: str
    hardware_clock_status: str  # 'UNVERIFIED'
    hardware_clock_evidence: str
    relative_alignment_assumption: str
    cross_device_offset_s: float
    offset_provenance: str
    radar_duration_s: float
    ecg_duration_s: float
    respiration_duration_s: float
    monitor_hr_duration_s: float
    duration_mismatch_s: float
    synchronization_confidence: str
    blocker_description: str


class SynchronizationManager:
    """Builds explicit time axes and conducts non-destructive synchronization audits."""

    @staticmethod
    def build_time_axis(
        channel_name: str,
        sample_count: int,
        fs_hz: float,
        t0_s: float = 0.0,
        confidence: str = "DOCUMENTED_NOMINAL",
        notes: str = "Nominal uniform sampling grid; hardware clock unverified",
    ) -> TimeAxis:
        """Construct explicit sample-time axis: t_n = t0 + n / fs."""
        if fs_hz <= 0:
            raise ValueError(f"Sampling frequency must be positive, got {fs_hz}")
        if sample_count <= 0:
            raise ValueError(f"Sample count must be positive, got {sample_count}")

        time_array = t0_s + np.arange(sample_count, dtype=np.float64) / fs_hz
        return TimeAxis(
            channel_name=channel_name,
            sample_count=sample_count,
            sampling_rate_hz=fs_hz,
            t0_seconds=t0_s,
            time_array=time_array,
            timing_confidence=confidence,
            timing_notes=notes,
        )

    @classmethod
    def evaluate_pair_synchronization(
        cls,
        subject_id: str,
        condition: str,
        radar_file: str,
        reference_file: str,
        radar_len: int,
        radar_fs: float,
        ecg_len: int,
        ecg_fs: float,
        resp_len: int,
        resp_fs: float,
        mon_hr_len: int,
        mon_hr_fs: float,
    ) -> SynchronizationRecord:
        """Evaluate timing relationship and duration consistency for a pair."""
        rad_dur = radar_len / radar_fs
        ecg_dur = ecg_len / ecg_fs
        resp_dur = resp_len / resp_fs
        mon_dur = mon_hr_len / mon_hr_fs

        # Check maximum duration mismatch between radar and ECG
        dur_mismatch = abs(rad_dur - ecg_dur)

        # Hardware trigger / clock check
        hw_status = "UNVERIFIED"
        hw_evidence = "MAT headers lack PPS pulse, common digitizer clock, or shared hardware trigger"
        rel_assumption = "Nominal concurrent recording start assumed (t0 = 0.0 s for both devices)"
        offset_s = 0.0
        offset_prov = "PRESPECIFIED_ZERO_OFFSET_ASSUMPTION"
        sync_conf = "UNVERIFIED_HARDWARE_TIMING"
        blocker = "Sub-second physical synchronization cannot be verified without hardware clock"

        return SynchronizationRecord(
            subject_id=subject_id,
            condition=condition,
            radar_file=radar_file,
            reference_file=reference_file,
            hardware_clock_status=hw_status,
            hardware_clock_evidence=hw_evidence,
            relative_alignment_assumption=rel_assumption,
            cross_device_offset_s=offset_s,
            offset_provenance=offset_prov,
            radar_duration_s=round(rad_dur, 4),
            ecg_duration_s=round(ecg_dur, 4),
            respiration_duration_s=round(resp_dur, 4),
            monitor_hr_duration_s=round(mon_dur, 4),
            duration_mismatch_s=round(dur_mismatch, 4),
            synchronization_confidence=sync_conf,
            blocker_description=blocker,
        )
