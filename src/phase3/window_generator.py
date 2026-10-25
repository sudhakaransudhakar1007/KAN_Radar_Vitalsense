"""Window generation and candidate segmentation module for Phase 3.

Strictly conditioned on authorization gate. If supervised label generation is not
authorized, stops execution before writing window manifests or label arrays,
reporting the exact blocking conditions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class LabelGenerationBlockedError(PermissionError):
    """Raised when supervised label generation is attempted while authorization gate is open."""
    pass


@dataclass
class WindowBoundary:
    """Calculated start/end times and sample indices for a candidate window."""
    window_index: int
    start_time_s: float
    end_time_s: float
    radar_sample_start: int
    radar_sample_end: int
    sample_count: int
    is_complete: bool


@dataclass
class WindowCandidateMetadata:
    """Diagnostic window metadata record (without unapproved supervised labels)."""
    subject_id: str
    recording_id: str
    condition: str
    window_index: int
    start_time_s: float
    end_time_s: float
    radar_sample_start: int
    radar_sample_end: int
    radar_sampling_rate_hz: float
    reference_source: str
    reference_coverage: float
    quality_status: str
    label_bpm: Optional[float]
    rejection_reason: Optional[str]


class WindowGenerator:
    """Production sliding window generator with strict gate enforcement and tail accounting."""

    def __init__(
        self,
        window_duration_s: float = 10.0,
        hop_duration_s: float = 5.0,
        authorization_granted: bool = False,
    ):
        self.win_s = window_duration_s
        self.hop_s = hop_duration_s
        self.authorization_granted = authorization_granted

    def compute_window_boundaries(
        self,
        total_samples: int,
        fs_hz: float,
    ) -> Tuple[List[WindowBoundary], int, float]:
        """Compute window boundaries and account for partial trailing tails without silent padding.

        Returns:
            boundaries: List of complete WindowBoundary objects.
            tail_samples: Number of excluded trailing samples.
            tail_duration_s: Duration of excluded trailing samples in seconds.
        """
        if fs_hz <= 0:
            raise ValueError(f"Sampling frequency must be positive, got {fs_hz}")

        win_samples = int(round(self.win_s * fs_hz))
        hop_samples = int(round(self.hop_s * fs_hz))

        boundaries = []
        start_idx = 0
        win_idx = 0

        while start_idx + win_samples <= total_samples:
            end_idx = start_idx + win_samples
            start_t = win_idx * self.hop_s
            end_t = start_t + self.win_s

            boundaries.append(
                WindowBoundary(
                    window_index=win_idx,
                    start_time_s=round(start_t, 3),
                    end_time_s=round(end_t, 3),
                    radar_sample_start=start_idx,
                    radar_sample_end=end_idx,
                    sample_count=win_samples,
                    is_complete=True,
                )
            )
            win_idx += 1
            start_idx += hop_samples

        # Trailing tail calculation
        last_processed_sample = (start_idx - hop_samples + win_samples) if win_idx > 0 else 0
        tail_samples = max(0, total_samples - last_processed_sample)
        tail_duration_s = round(tail_samples / fs_hz, 4)

        return boundaries, tail_samples, tail_duration_s

    def execute_supervised_generation(self) -> None:
        """Enforces mandatory approval gate before generating supervised window dataset."""
        if not self.authorization_granted:
            raise LabelGenerationBlockedError(
                "Supervised HR-label generation is BLOCKED: Phase 2A Finalization Gate remains OPEN, "
                "and formal clinical SQI ground-truth label approval has not been granted by user."
            )
