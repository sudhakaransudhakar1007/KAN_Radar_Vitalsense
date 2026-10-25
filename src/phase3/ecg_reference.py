"""ECG reference validation, missing sample interpolation, R-peak detection, and SQI diagnostics.

Strict non-destructive in-memory processing. If formal SQI approval is absent,
diagnostics are generated and label eligibility is marked strictly NOT_APPROVED.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.signal as signal

from src.sync_validation.ecg_processor import (
    clean_ecg_isolated_nans,
    clean_ecg_nans as sync_clean_ecg_nans,
    detect_r_peaks as sync_detect_r_peaks,
)


def clean_ecg_nans(
    ecg_raw: np.ndarray,
    only_isolated: bool = True,
    fill_boundary: bool = True,
) -> Tuple[np.ndarray, int, List[int]]:
    """Clean isolated delimiter NaNs in an in-memory copy of ecg_lead2 using canonical sync_validation method."""
    clean_arr, total_nans, isolated_idx = sync_clean_ecg_nans(ecg_raw, only_isolated=only_isolated)
    if not fill_boundary and len(ecg_raw) > 0:
        if np.isnan(ecg_raw[0]):
            clean_arr[0] = np.nan
        if np.isnan(ecg_raw[-1]):
            clean_arr[-1] = np.nan
    return clean_arr, total_nans, isolated_idx


def detect_r_peaks(
    ecg_clean: np.ndarray,
    fs: float = 500.0,
    min_bpm: float = 35.0,
    max_bpm: float = 185.0,
) -> Dict[str, Any]:
    """Detect ECG R-peaks using canonical sync_validation detector with abs refinement."""
    return sync_detect_r_peaks(ecg_clean, fs=fs, min_bpm=min_bpm, max_bpm=max_bpm)


@dataclass
class ECGMissingSampleAnalysis:
    """Missing sample structure and NaN pattern analysis."""
    total_samples: int
    nan_count: int
    nan_indices: List[int]
    is_periodic_single_nan: bool
    multi_sample_gap_count: int
    leading_trailing_nans: bool
    interpolation_eligible: bool
    cleaned_ecg_in_memory: Optional[np.ndarray] = None


@dataclass
class RPeakQCResult:
    """R-peak detection validation and RR-interval statistics."""
    detector_name: str
    detected_peak_count: int
    peak_indices: np.ndarray
    peak_times_s: np.ndarray
    rr_intervals_s: np.ndarray
    valid_rr_mask: np.ndarray
    valid_rr_count: int
    rejected_rr_count: int
    mean_hr_bpm: float
    min_hr_bpm: float
    max_hr_bpm: float
    duplicate_peak_count: int
    non_monotonic_count: int


@dataclass
class SQIDiagnosticResult:
    """Multi-parameter Signal Quality Index (SQI) diagnostic result."""
    subject_id: str
    condition: str
    recording_duration_s: float
    valid_rr_coverage_pct: float
    max_rr_gap_s: float
    detected_peak_count: int
    valid_rr_count: int
    rejected_rr_fraction: float
    nan_fraction: float
    proposed_sqi_pass: bool  # Evaluated against (>85% coverage, <3s gap)
    official_label_eligibility: str  # Strictly 'NOT_APPROVED' pending formal protocol sign-off
    rejection_reasons: List[str] = field(default_factory=list)
    amplitude_stability: str = "NOT_ASSESSED"
    official_sqi_verdict: str = "SQI_PARTIAL"


class ECGReferenceValidator:
    """Production ECG quality validator and Pan-Tompkins QRS detector."""

    def __init__(
        self,
        fs_ecg: float = 500.0,
        min_bpm: float = 35.0,
        max_bpm: float = 185.0,
        sqi_coverage_thresh: float = 85.0,
        sqi_max_gap_thresh_s: float = 3.0,
    ):
        self.fs = fs_ecg
        self.min_rr_s = 60.0 / max_bpm   # ~0.324s
        self.max_rr_s = 60.0 / min_bpm   # ~1.714s
        self.sqi_coverage_thresh = sqi_coverage_thresh
        self.sqi_max_gap_thresh_s = sqi_max_gap_thresh_s

    def analyze_missing_samples(self, raw_ecg: np.ndarray) -> ECGMissingSampleAnalysis:
        """Inspect NaN pattern and perform single-sample in-memory linear interpolation."""
        ecg = np.array(raw_ecg, copy=True, dtype=np.float64).flatten()
        n = len(ecg)
        nan_mask = np.isnan(ecg)
        nan_indices = np.where(nan_mask)[0].tolist()
        nan_count = len(nan_indices)

        if nan_count == 0:
            return ECGMissingSampleAnalysis(
                total_samples=n,
                nan_count=0,
                nan_indices=[],
                is_periodic_single_nan=False,
                multi_sample_gap_count=0,
                leading_trailing_nans=False,
                interpolation_eligible=True,
                cleaned_ecg_in_memory=ecg,
            )

        # Check for leading or trailing NaNs
        leading_trailing = bool(nan_mask[0] or nan_mask[-1])

        # Check for consecutive NaNs (multi-sample gaps)
        diffs = np.diff(nan_indices) if len(nan_indices) > 1 else np.array([999])
        multi_sample_gaps = int(np.sum(diffs == 1))

        # Check periodic spacing (~500 samples in Mindray)
        is_periodic = False
        if len(diffs) >= 5:
            median_spacing = float(np.median(diffs))
            if 490 <= median_spacing <= 510 and multi_sample_gaps == 0 and not leading_trailing:
                is_periodic = True

        # Interpolation eligibility: only isolated internal single NaNs are interpolated
        eligible = (multi_sample_gaps == 0) and (not leading_trailing)

        cleaned_ecg = None
        if eligible:
            cleaned_ecg = np.array(ecg, copy=True)
            valid_idx = np.where(~nan_mask)[0]
            cleaned_ecg[nan_indices] = np.interp(nan_indices, valid_idx, ecg[valid_idx])

        return ECGMissingSampleAnalysis(
            total_samples=n,
            nan_count=nan_count,
            nan_indices=nan_indices,
            is_periodic_single_nan=is_periodic,
            multi_sample_gap_count=multi_sample_gaps,
            leading_trailing_nans=leading_trailing,
            interpolation_eligible=eligible,
            cleaned_ecg_in_memory=cleaned_ecg,
        )

    def detect_r_peaks_pan_tompkins(self, ecg_signal: np.ndarray) -> RPeakQCResult:
        """Execute standardized Pan-Tompkins algorithm on clean in-memory ECG."""
        x = np.array(ecg_signal, dtype=np.float64).flatten()
        n = len(x)

        if np.any(np.isnan(x)):
            raise ValueError("ECG signal contains NaNs; missing sample handling must be performed first.")

        # 1. Bandpass filter 5 - 15 Hz
        nyq = self.fs / 2.0
        low = 5.0 / nyq
        high = 15.0 / nyq
        b, a = signal.butter(2, [low, high], btype="bandpass")
        filtered = signal.filtfilt(b, a, x)

        # 2. Derivative filter [-1, -2, 0, 2, 1] / 8
        h_der = np.array([-1.0, -2.0, 0.0, 2.0, 1.0]) / 8.0
        diff = signal.convolve(filtered, h_der, mode="same")

        # 3. Squaring
        squared = diff ** 2

        # 4. Moving window integration (~150 ms)
        win_size = int(0.150 * self.fs)
        integrated = np.convolve(squared, np.ones(win_size) / win_size, mode="same")

        # 5. Peak picking on integrated signal with refractory period (~250 ms)
        min_distance = int(0.250 * self.fs)
        # Adaptive thresholding: 35% of 90th percentile to avoid outlier bias
        thresh = 0.35 * float(np.percentile(integrated, 90))
        peaks_int, _ = signal.find_peaks(integrated, distance=min_distance, height=thresh)

        # 6. Search back in bandpass-filtered ECG around integrated peak for true local maximum
        search_radius = int(0.100 * self.fs)  # +/- 100 ms
        r_peaks = []
        for p in peaks_int:
            start = max(0, p - search_radius)
            end = min(n, p + search_radius + 1)
            local_peak = start + int(np.argmax(filtered[start:end]))
            if local_peak not in r_peaks:
                r_peaks.append(local_peak)

        r_peaks = np.array(sorted(r_peaks), dtype=np.int64)
        peak_times = r_peaks / self.fs

        # 7. RR interval analysis
        rr_intervals = np.diff(peak_times) if len(peak_times) > 1 else np.array([])
        valid_rr_mask = (rr_intervals >= self.min_rr_s) & (rr_intervals <= self.max_rr_s)

        valid_rr = rr_intervals[valid_rr_mask]
        valid_rr_count = int(np.sum(valid_rr_mask))
        rej_rr_count = len(rr_intervals) - valid_rr_count

        mean_hr = float(np.mean(60.0 / valid_rr)) if len(valid_rr) > 0 else 0.0
        min_hr = float(np.min(60.0 / valid_rr)) if len(valid_rr) > 0 else 0.0
        max_hr = float(np.max(60.0 / valid_rr)) if len(valid_rr) > 0 else 0.0

        # Monotonicity & duplicates check
        non_mono = int(np.sum(np.diff(r_peaks) <= 0))
        dups = len(r_peaks) - len(np.unique(r_peaks))

        return RPeakQCResult(
            detector_name="Pan-Tompkins_5-15Hz",
            detected_peak_count=len(r_peaks),
            peak_indices=r_peaks,
            peak_times_s=peak_times,
            rr_intervals_s=rr_intervals,
            valid_rr_mask=valid_rr_mask,
            valid_rr_count=valid_rr_count,
            rejected_rr_count=rej_rr_count,
            mean_hr_bpm=round(mean_hr, 2),
            min_hr_bpm=round(min_hr, 2),
            max_hr_bpm=round(max_hr, 2),
            duplicate_peak_count=dups,
            non_monotonic_count=non_mono,
        )

    def evaluate_sqi(
        self,
        subject_id: str,
        condition: str,
        total_duration_s: float,
        nan_count: int,
        rpeak_res: RPeakQCResult,
    ) -> SQIDiagnosticResult:
        """Compute multi-parameter Signal Quality Index diagnostics."""
        rejection_reasons = []

        # Coverage: sum of valid RR intervals
        valid_rr = rpeak_res.rr_intervals_s[rpeak_res.valid_rr_mask] if len(rpeak_res.rr_intervals_s) > 0 else np.array([])
        valid_time_s = float(np.sum(valid_rr)) if len(valid_rr) > 0 else 0.0
        coverage_pct = round((valid_time_s / total_duration_s) * 100.0, 2) if total_duration_s > 0 else 0.0

        # Max gap: longest interval between consecutive R-peaks (or start to first peak, or last peak to end)
        if len(rpeak_res.peak_times_s) > 1:
            gaps = [rpeak_res.peak_times_s[0]]  # start gap
            gaps.extend(rpeak_res.rr_intervals_s.tolist())
            gaps.append(max(0.0, total_duration_s - rpeak_res.peak_times_s[-1]))
            max_gap_s = round(float(np.max(gaps)), 3)
        else:
            max_gap_s = total_duration_s

        # Rejection fraction
        total_rr = len(rpeak_res.rr_intervals_s)
        rej_frac = round(rpeak_res.rejected_rr_count / total_rr, 4) if total_rr > 0 else 1.0
        nan_frac = round(nan_count / (total_duration_s * self.fs), 6)

        # Proposed SQI thresholds (>85% coverage, <3.0s max gap)
        proposed_pass = True
        if coverage_pct < self.sqi_coverage_thresh:
            proposed_pass = False
            rejection_reasons.append(f"RR coverage {coverage_pct:.1f}% below {self.sqi_coverage_thresh}% threshold")
        if max_gap_s > self.sqi_max_gap_thresh_s:
            proposed_pass = False
            rejection_reasons.append(f"Max RR gap {max_gap_s:.2f}s exceeds {self.sqi_max_gap_thresh_s:.1f}s threshold")
        if rpeak_res.valid_rr_count < 20:
            proposed_pass = False
            rejection_reasons.append(f"Valid beat count {rpeak_res.valid_rr_count} too low for 120s recording")

        # Official label eligibility remains NOT_APPROVED per Section 4 mandate
        official_eligibility = "NOT_APPROVED_PENDING_PROTOCOL_SIGN_OFF"
        # Official SQI verdict per D9: SQI_PARTIAL (never PASS), amplitude stability NOT_ASSESSED
        official_sqi_verdict = "SQI_PARTIAL" if proposed_pass else "SQI_FAIL"

        return SQIDiagnosticResult(
            subject_id=subject_id,
            condition=condition,
            recording_duration_s=round(total_duration_s, 2),
            valid_rr_coverage_pct=coverage_pct,
            max_rr_gap_s=max_gap_s,
            detected_peak_count=rpeak_res.detected_peak_count,
            valid_rr_count=rpeak_res.valid_rr_count,
            rejected_rr_fraction=rej_frac,
            nan_fraction=nan_frac,
            proposed_sqi_pass=proposed_pass,
            official_label_eligibility=official_eligibility,
            rejection_reasons=rejection_reasons,
            amplitude_stability="NOT_ASSESSED",
            official_sqi_verdict=official_sqi_verdict,
        )

    # Legacy aliases and canonical methods
    analyze_missing_samples_legacy = analyze_missing_samples
    detect_r_peaks_pan_tompkins_legacy = detect_r_peaks_pan_tompkins

    def clean_ecg_nans(
        self,
        ecg_raw: np.ndarray,
        only_isolated: bool = True,
        fill_boundary: bool = True,
    ) -> Tuple[np.ndarray, int, List[int]]:
        """Instance method wrapping canonical sync_validation clean_ecg_nans."""
        return clean_ecg_nans(ecg_raw, only_isolated=only_isolated, fill_boundary=fill_boundary)

    def detect_r_peaks(
        self,
        ecg_clean: np.ndarray,
        min_bpm: Optional[float] = None,
        max_bpm: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Instance method wrapping canonical sync_validation detect_r_peaks."""
        return detect_r_peaks(
            ecg_clean,
            fs=self.fs,
            min_bpm=min_bpm or (60.0 / self.max_rr_s),
            max_bpm=max_bpm or (60.0 / self.min_rr_s),
        )
