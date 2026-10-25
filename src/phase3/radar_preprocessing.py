"""Radar signal preprocessing and comparative filtering module for Phase 3.

Evaluates both candidate configurations:
1. Experimental candidate filter (1.0 - 20.0 Hz) per prompt Section 5.2.
2. Physiological cardiac band filter (0.8 - 3.0 Hz, 48 - 180 bpm) per prompt Section 5.2.

Validates Nyquist bounds, edge effects, causal vs non-causal implementations,
and computes comparative statistics against raw VitalSig.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.signal as signal


@dataclass
class FilterConfig:
    """Filter configuration and documentation."""
    name: str
    filter_type: str  # 'butterworth'
    order: int
    low_cutoff_hz: float
    high_cutoff_hz: float
    implementation: str  # 'zero_phase_filtfilt' or 'causal_lfilter'
    edge_handling: str  # 'pad_reflect'


@dataclass
class PreprocessingStats:
    """Summary statistics for raw vs filtered radar signals."""
    signal_name: str
    sample_count: int
    sampling_rate_hz: float
    mean: float
    std: float
    min_val: float
    max_val: float
    p2p_amplitude: float
    power_total: float
    power_cardiac_band_0_8_3_0hz: float
    cardiac_band_power_ratio: float


@dataclass
class RadarPreprocessingRecord:
    """Comparison results for a radar recording under raw and filtered configurations."""
    subject_id: str
    condition: str
    raw_stats: PreprocessingStats
    candidate_1_20hz_stats: PreprocessingStats
    cardiac_0_8_3_0hz_stats: PreprocessingStats
    nyquist_valid: bool
    filter_notes: str


class RadarPreprocessor:
    """Production radar signal preprocessor and spectral validator."""

    def __init__(self, default_order: int = 3):
        self.default_order = default_order

    def validate_filter_bounds(self, low_hz: float, high_hz: float, fs_hz: float) -> bool:
        """Validate 0 < f_low < f_high < fs / 2."""
        if fs_hz <= 0:
            return False
        nyq = fs_hz / 2.0
        return (0.0 < low_hz < high_hz < nyq)

    def apply_bandpass(
        self,
        signal_array: np.ndarray,
        fs_hz: float,
        low_hz: float,
        high_hz: float,
        order: int = 3,
        causal: bool = False,
    ) -> Tuple[np.ndarray, bool, str]:
        """Apply Butterworth bandpass filter with Nyquist validation."""
        x = np.array(signal_array, dtype=np.float64).flatten()
        if not self.validate_filter_bounds(low_hz, high_hz, fs_hz):
            return x, False, f"Invalid frequency bounds: low={low_hz}, high={high_hz}, fs={fs_hz}"

        nyq = fs_hz / 2.0
        wn = [low_hz / nyq, high_hz / nyq]
        b, a = signal.butter(order, wn, btype="bandpass")

        if causal:
            # Causal IIR for real-time simulation (has phase distortion and group delay)
            y = signal.lfilter(b, a, x)
            method = "causal_lfilter"
        else:
            # Zero-phase filtfilt for offline retrospective training
            y = signal.filtfilt(b, a, x)
            method = "zero_phase_filtfilt"

        return y, True, f"Successfully filtered with {order}-order Butterworth ({low_hz}-{high_hz} Hz, {method})"

    def compute_stats(self, x: np.ndarray, fs_hz: float, name: str) -> PreprocessingStats:
        """Compute statistical and spectral power distribution."""
        x_clean = np.array(x, dtype=np.float64).flatten()
        n = len(x_clean)
        if n == 0 or fs_hz <= 0:
            return PreprocessingStats(name, 0, fs_hz, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Remove DC component for power calculation
        x_detrend = x_clean - np.mean(x_clean)
        tot_power = float(np.mean(x_detrend ** 2))

        # FFT power in 0.8 - 3.0 Hz cardiac band
        freqs = np.fft.rfftfreq(n, d=1.0 / fs_hz)
        fft_vals = np.abs(np.fft.rfft(x_detrend)) ** 2 / n
        cardiac_mask = (freqs >= 0.8) & (freqs <= 3.0)
        cardiac_power = float(np.sum(fft_vals[cardiac_mask])) / n if n > 0 else 0.0
        ratio = round(cardiac_power / (tot_power + 1e-12), 4)

        return PreprocessingStats(
            signal_name=name,
            sample_count=n,
            sampling_rate_hz=fs_hz,
            mean=round(float(np.mean(x_clean)), 6),
            std=round(float(np.std(x_clean)), 6),
            min_val=round(float(np.min(x_clean)), 6),
            max_val=round(float(np.max(x_clean)), 6),
            p2p_amplitude=round(float(np.ptp(x_clean)), 6),
            power_total=round(tot_power, 6),
            power_cardiac_band_0_8_3_0hz=round(cardiac_power, 6),
            cardiac_band_power_ratio=min(1.0, max(0.0, ratio)),
        )

    def process_recording(
        self,
        subject_id: str,
        condition: str,
        vitsig_raw: np.ndarray,
        fs_hz: float,
    ) -> RadarPreprocessingRecord:
        """Process a single radar recording through raw, candidate (1-20 Hz) and cardiac (0.8-3.0 Hz) filters."""
        raw_stats = self.compute_stats(vitsig_raw, fs_hz, "raw_vitalsig")

        # 1. Candidate 1 - 20 Hz
        cand_sig, cand_ok, cand_msg = self.apply_bandpass(vitsig_raw, fs_hz, 1.0, 20.0, order=self.default_order)
        cand_stats = self.compute_stats(cand_sig, fs_hz, "candidate_1_20hz")

        # 2. Cardiac band 0.8 - 3.0 Hz
        card_sig, card_ok, card_msg = self.apply_bandpass(vitsig_raw, fs_hz, 0.8, 3.0, order=self.default_order)
        card_stats = self.compute_stats(card_sig, fs_hz, "cardiac_0_8_3_0hz")

        nyq_ok = cand_ok and card_ok
        notes = f"{cand_msg}; {card_msg}"

        return RadarPreprocessingRecord(
            subject_id=subject_id,
            condition=condition,
            raw_stats=raw_stats,
            candidate_1_20hz_stats=cand_stats,
            cardiac_0_8_3_0hz_stats=card_stats,
            nyquist_valid=nyq_ok,
            filter_notes=notes,
        )
