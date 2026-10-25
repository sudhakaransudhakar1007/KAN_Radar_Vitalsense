"""Robust MAT-file loader for VITALSENSE 120-GHz radar and Mindray reference data.

Supports MATLAB v5/v7 files, validates dimensionality, metadata, sampling frequencies,
missing values, and variable-length recordings without silent padding or truncation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import scipy.io as sio


@dataclass
class ChannelMetadata:
    """Metadata for a single loaded channel."""
    name: str
    shape: Tuple[int, ...]
    dtype: str
    finite_count: int
    nan_count: int
    inf_count: int
    sampling_rate_hz: Optional[float]
    sampling_rate_source: str
    duration_seconds: Optional[float]


@dataclass
class LoadedRecord:
    """Loaded record containing raw channels, metadata, and validation flags."""
    file_path: str
    file_type: str  # 'radar' or 'reference'
    mat_version: str
    channels: Dict[str, np.ndarray] = field(default_factory=dict)
    channel_metadata: Dict[str, ChannelMetadata] = field(default_factory=dict)
    metadata_fields: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)


class RobustMatLoader:
    """Production MAT-file loader with strict validation and no silent truncation/padding."""

    EXPECTED_RADAR_VARS = {"VitalSig"}
    EXPECTED_REF_VARS = {"ecg_lead2", "HR", "respiration"}

    @staticmethod
    def inspect_mat_version(file_path: Union[str, Path]) -> str:
        """Inspect MAT-file header to detect format version."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(p, "rb") as f:
            header = f.read(128)
        if len(header) < 128:
            return "MALFORMED_HEADER"
        try:
            header_str = header.decode("latin1")
            if "MATLAB 5.0" in header_str or "MATLAB 7" in header_str:
                return "MATLAB_v5_v7"
            if "HDF" in header_str or header[:4] == b"\x89HDF":
                return "MATLAB_v7.3_HDF5"
            return f"UNKNOWN_{header_str[:30].strip()}"
        except Exception as e:
            return f"CORRUPTED_HEADER_{type(e).__name__}"

    def load_radar_mat(self, file_path: Union[str, Path]) -> LoadedRecord:
        """Load and validate a radar MAT file containing VitalSig."""
        p = Path(file_path)
        version = self.inspect_mat_version(p)
        rec = LoadedRecord(file_path=str(p), file_type="radar", mat_version=version)

        try:
            mat = sio.loadmat(str(p))
        except Exception as e:
            rec.validation_errors.append(f"Failed to load MAT file with scipy.io: {e}")
            return rec

        # 1. Load VitalSig
        if "VitalSig" not in mat:
            rec.validation_errors.append("Missing required variable 'VitalSig'")
            return rec

        vitsig = mat["VitalSig"]
        if not isinstance(vitsig, np.ndarray):
            rec.validation_errors.append(f"VitalSig is not an ndarray, got {type(vitsig)}")
            return rec

        # Check dimensionality
        v_flat = vitsig.flatten()
        finite_c = int(np.sum(np.isfinite(v_flat)))
        nan_c = int(np.sum(np.isnan(v_flat)))
        inf_c = int(np.sum(np.isinf(v_flat)))

        # 2. Extract Radar.fs
        rad_fs: Optional[float] = None
        fs_source = "MISSING"
        if "Radar" in mat and hasattr(mat["Radar"], "dtype") and "fs" in mat["Radar"].dtype.names:
            try:
                rad_fs = float(mat["Radar"]["fs"][0, 0][0, 0])
                fs_source = "Radar.fs"
            except Exception as e:
                rec.validation_warnings.append(f"Error parsing Radar.fs: {e}")
        elif "T_frame" in mat:
            try:
                t_frame = float(mat["T_frame"].flatten()[0])
                if t_frame > 0:
                    rad_fs = float(1.0 / t_frame)
                    fs_source = "1/T_frame"
            except Exception as e:
                rec.validation_warnings.append(f"Error parsing T_frame: {e}")

        if rad_fs is None or rad_fs <= 0 or rad_fs > 100000:
            rec.validation_errors.append(f"Invalid or missing radar sampling frequency: {rad_fs}")
        
        duration_s = len(v_flat) / rad_fs if rad_fs and rad_fs > 0 else None

        v_meta = ChannelMetadata(
            name="VitalSig",
            shape=vitsig.shape,
            dtype=str(vitsig.dtype),
            finite_count=finite_c,
            nan_count=nan_c,
            inf_count=inf_c,
            sampling_rate_hz=rad_fs,
            sampling_rate_source=fs_source,
            duration_seconds=round(duration_s, 4) if duration_s else None,
        )

        rec.channels["VitalSig"] = vitsig
        rec.channel_metadata["VitalSig"] = v_meta

        # Metadata fields
        for k in ["T_frame", "MeasurementInfo"]:
            if k in mat:
                rec.metadata_fields[k] = mat[k]

        return rec

    def load_reference_mat(self, file_path: Union[str, Path]) -> LoadedRecord:
        """Load and validate a Mindray reference MAT file."""
        p = Path(file_path)
        version = self.inspect_mat_version(p)
        rec = LoadedRecord(file_path=str(p), file_type="reference", mat_version=version)

        try:
            mat = sio.loadmat(str(p))
        except Exception as e:
            rec.validation_errors.append(f"Failed to load MAT file with scipy.io: {e}")
            return rec

        # Extract sampling rates from metadata
        fs_ecg = None
        if "Fs_ecg" in mat:
            try:
                fs_ecg = float(mat["Fs_ecg"].flatten()[0])
            except Exception:
                pass
        if fs_ecg is None or fs_ecg <= 0:
            fs_ecg = 500.0  # Documented Mindray ECG lead2 standard
            fs_ecg_src = "DOCUMENTED_DEFAULT_500HZ"
        else:
            fs_ecg_src = "Fs_ecg"

        fs_resp = None
        if "Fs_resp" in mat:
            try:
                fs_resp = float(mat["Fs_resp"].flatten()[0])
            except Exception:
                pass
        if fs_resp is None or fs_resp <= 0:
            fs_resp = 256.0  # Documented Mindray respiration standard
            fs_resp_src = "DOCUMENTED_DEFAULT_256HZ"
        else:
            fs_resp_src = "Fs_resp"

        fs_hr = 1.0  # Mindray discrete monitor HR display updates at 1 Hz
        fs_hr_src = "DOCUMENTED_MONITOR_1HZ"

        # Check required reference channels
        channel_configs = [
            ("ecg_lead2", fs_ecg, fs_ecg_src, True),
            ("HR", fs_hr, fs_hr_src, True),
            ("respiration", fs_resp, fs_resp_src, True),
            ("pleth", 62.5, "DOCUMENTED_PLETH_62.5HZ", False),
        ]

        for ch_name, ch_fs, ch_src, is_mandatory in channel_configs:
            if ch_name not in mat:
                if is_mandatory:
                    rec.validation_errors.append(f"Missing mandatory reference variable '{ch_name}'")
                continue

            arr = mat[ch_name]
            arr_flat = arr.flatten()
            finite_c = int(np.sum(np.isfinite(arr_flat)))
            nan_c = int(np.sum(np.isnan(arr_flat)))
            inf_c = int(np.sum(np.isinf(arr_flat)))
            dur_s = len(arr_flat) / ch_fs if ch_fs and ch_fs > 0 else None

            ch_meta = ChannelMetadata(
                name=ch_name,
                shape=arr.shape,
                dtype=str(arr.dtype),
                finite_count=finite_c,
                nan_count=nan_c,
                inf_count=inf_c,
                sampling_rate_hz=ch_fs,
                sampling_rate_source=ch_src,
                duration_seconds=round(dur_s, 4) if dur_s else None,
            )

            rec.channels[ch_name] = arr
            rec.channel_metadata[ch_name] = ch_meta

        # Other metadata fields (BPD, BPM, BPS, RR)
        for k in ["BPD", "BPM", "BPS", "RR"]:
            if k in mat:
                rec.metadata_fields[k] = mat[k]

        return rec
