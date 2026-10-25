"""Phase 2A Synchronization Validation Package."""

from .ecg_processor import (
    clean_ecg_nans,
    detect_r_peaks,
    derive_1hz_ecg_hr,
    scan_monitor_hr_lag,
)
from .respiratory_validator import (
    resample_signals_to_2000hz,
    compute_respiratory_xcorr,
    compute_surrogate_respiratory_control,
)
from .cardiac_radar_validator import (
    extract_radar_cardiac_signal,
    compute_window_level_hr_agreement,
    synthetic_known_offset_test,
)

__all__ = [
    "clean_ecg_nans",
    "detect_r_peaks",
    "derive_1hz_ecg_hr",
    "scan_monitor_hr_lag",
    "resample_signals_to_2000hz",
    "compute_respiratory_xcorr",
    "compute_surrogate_respiratory_control",
    "extract_radar_cardiac_signal",
    "compute_window_level_hr_agreement",
    "synthetic_known_offset_test",
]
