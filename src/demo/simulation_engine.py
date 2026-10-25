"""Deterministic Recorded Radar Replay and Rolling Window Simulation Engine.

Workflow:
Recorded radar signal -> Simulated streaming buffer -> Rolling window (10s) ->
Validated preprocessing -> Model inference (if available) -> Live-style updates.

Clock independence:
Maintains an internal virtual simulation clock decoupled from OS wall-clock time
for fully reproducible positioning and testing.
"""

from __future__ import annotations

import csv
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from src.demo.model_loader import ModelInferenceResult, SafeModelInferenceEngine
from src.phase3.mat_loader import LoadedRecord, RobustMatLoader
from src.phase3.radar_preprocessing import RadarPreprocessor


@dataclass
class WindowHistoryRecord:
    """Historical audit record for a single processed rolling window."""
    window_index: int
    start_time_s: float
    end_time_s: float
    start_sample_idx: int
    end_sample_idx: int
    sample_count: int
    processing_status: str  # 'PROCESSED', 'INCOMPLETE_WINDOW', 'INVALID_SIGNAL', 'MODEL_UNAVAILABLE'
    prediction_bpm: Optional[float]
    inference_latency_ms: float
    provenance_note: str
    error_reason: str


@dataclass
class SimulationSnapshot:
    """Complete serialized state snapshot for UI and API consumers."""
    session_id: str
    recording_id: str
    file_path: str
    playback_state: str  # 'READY', 'RUNNING', 'PAUSED', 'COMPLETED', 'ERROR'
    simulation_speed: float
    elapsed_sim_time_s: float
    current_sample_idx: int
    current_window_idx: int
    total_samples: int
    total_duration_s: float
    sampling_rate_hz: float
    window_duration_s: float
    hop_duration_s: float
    window_samples: int
    hop_samples: int
    total_windows: int
    signal_quality_status: str
    model_name: str
    operating_mode: str
    model_status_reason: str
    latest_prediction_bpm: Optional[float]
    latest_latency_ms: float
    processed_window_count: int
    error_message: str
    model_state: str = "MODEL_UNAVAILABLE"
    data_mode: str = "RECORDED_RADAR_PLAYBACK"


class RadarSimulationEngine:
    """Production-grade deterministic streaming simulation engine."""

    def __init__(
        self,
        dataset_dir: Union[str, Path] = "../data/VITALSENSE_120_DATASET",
        window_duration_s: float = 10.0,
        hop_duration_s: float = 5.0,
        model_engine: Optional[SafeModelInferenceEngine] = None,
    ):
        self.dataset_dir = Path(dataset_dir)
        self.win_s = float(window_duration_s)
        self.hop_s = float(hop_duration_s)
        self.model_engine = model_engine or SafeModelInferenceEngine(model_name="KANRegressor")

        self.loader = RobustMatLoader()
        self.preprocessor = RadarPreprocessor()

        # Session tracking
        self.session_id = f"demo_sess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self.recording_id: str = "NONE"
        self.loaded_record: Optional[LoadedRecord] = None
        self.raw_signal: np.ndarray = np.array([], dtype=np.float64)
        self.filtered_signal: np.ndarray = np.array([], dtype=np.float64)
        self.fs_hz: float = 333.3333333333333

        # Window counts
        self.win_samples: int = int(round(self.win_s * self.fs_hz))
        self.hop_samples: int = int(round(self.hop_s * self.fs_hz))
        self.total_windows: int = 0

        # Simulation playback state
        self.playback_state: str = "READY"
        self.simulation_speed: float = 1.0
        self.current_sample_idx: int = 0
        self.current_window_idx: int = -1
        self.elapsed_sim_time_s: float = 0.0
        self.signal_quality_status: str = "NO_DATA"
        self.error_message: str = ""

        # History tracking
        self.window_history: List[WindowHistoryRecord] = []
        self.latest_prediction: Optional[ModelInferenceResult] = None

    def discover_recordings(self) -> List[Dict[str, Any]]:
        """Discovers all available radar recordings in dataset_dir."""
        results = []
        if not self.dataset_dir.exists():
            return results

        mats = sorted(list(self.dataset_dir.glob("**/*.mat")))
        radar_files = [f for f in mats if not f.name.endswith("_Mindray.mat")]

        for f in radar_files:
            stem = f.stem
            sub_id = stem.split("_")[0] if "_" in stem else "Unknown"
            cond = stem.split("_")[1] if "_" in stem else "Unknown"
            results.append({
                "recording_id": stem,
                "subject_id": sub_id,
                "condition": cond,
                "file_name": f.name,
                "file_path": str(f.resolve()),
                "file_size_bytes": f.stat().st_size,
            })
        return results

    def load_recording(self, file_path: Union[str, Path]) -> bool:
        """Loads a recorded radar file and validates its channels and metadata."""
        p = Path(file_path)
        if not p.exists():
            self.playback_state = "ERROR"
            self.error_message = f"File not found: {file_path}"
            return False

        rec = self.loader.load_radar_mat(p)
        if rec.validation_errors:
            self.playback_state = "ERROR"
            self.error_message = f"Validation failed: {'; '.join(rec.validation_errors)}"
            return False

        if "VitalSig" not in rec.channels:
            self.playback_state = "ERROR"
            self.error_message = "Missing required variable 'VitalSig'"
            return False

        raw = rec.channels["VitalSig"].flatten()
        if len(raw) == 0:
            self.playback_state = "ERROR"
            self.error_message = "VitalSig signal is empty (0 samples)"
            return False

        # Extract sampling rate
        meta = rec.channel_metadata.get("VitalSig")
        rad_fs = meta.sampling_rate_hz if meta and meta.sampling_rate_hz else 333.3333333333333

        self.loaded_record = rec
        self.recording_id = p.stem
        self.raw_signal = raw
        self.fs_hz = rad_fs

        # Calculate exact window and hop samples
        self.win_samples = int(round(self.win_s * self.fs_hz))
        self.hop_samples = int(round(self.hop_s * self.fs_hz))

        # Check total complete windows possible
        total_s = len(raw)
        self.total_windows = max(0, (total_s - self.win_samples) // self.hop_samples + 1)

        # Apply validated cardiac bandpass filter on full recording (0.8-3.0 Hz, zero-phase)
        filt, ok, note = self.preprocessor.apply_bandpass(
            raw, self.fs_hz, low_hz=0.8, high_hz=3.0, order=3, causal=False
        )
        self.filtered_signal = filt if ok else raw

        # Check signal finiteness
        if np.all(np.isfinite(raw)):
            self.signal_quality_status = "VALID_FINITE_SIGNAL"
        else:
            self.signal_quality_status = "NON_FINITE_SAMPLES_DETECTED"

        # Reset simulation state for new recording
        self.reset()
        self.playback_state = "READY"
        self.error_message = ""
        return True

    def start(self) -> None:
        """Starts continuous simulation playback."""
        if self.playback_state in ("READY", "PAUSED"):
            self.playback_state = "RUNNING"
        elif self.playback_state == "COMPLETED":
            # Restart from beginning
            self.reset()
            self.playback_state = "RUNNING"

    def pause(self) -> None:
        """Pauses simulation playback without losing state."""
        if self.playback_state == "RUNNING":
            self.playback_state = "PAUSED"

    def resume(self) -> None:
        """Resumes paused simulation."""
        if self.playback_state == "PAUSED":
            self.playback_state = "RUNNING"

    def reset(self) -> None:
        """Resets simulation clock and buffer position back to t=0."""
        self.current_sample_idx = 0
        self.current_window_idx = -1
        self.elapsed_sim_time_s = 0.0
        self.playback_state = "READY" if len(self.raw_signal) > 0 else "NO_DATA"
        self.window_history = []
        self.latest_prediction = None
        self.error_message = ""

    def step(self) -> Optional[WindowHistoryRecord]:
        """Advances simulation deterministically by exactly one window step."""
        if len(self.raw_signal) == 0:
            self.playback_state = "ERROR"
            self.error_message = "No recording loaded."
            return None

        # Next window index
        next_win_idx = self.current_window_idx + 1

        # Check if next window start index exceeds signal length
        start_sample = next_win_idx * self.hop_samples
        end_sample = start_sample + self.win_samples

        if end_sample > len(self.raw_signal):
            self.playback_state = "COMPLETED"
            return None

        # Extract current 10-second window
        window_raw = self.raw_signal[start_sample:end_sample]
        window_filt = self.filtered_signal[start_sample:end_sample]

        t_start = round(next_win_idx * self.hop_s, 3)
        t_end = round(t_start + self.win_s, 3)

        # Run safe inference
        inf_res = self.model_engine.predict_window(
            window_signal=window_filt,
            window_index=next_win_idx,
            start_time_s=t_start,
            end_time_s=t_end,
        )
        self.latest_prediction = inf_res

        # Record history
        record = WindowHistoryRecord(
            window_index=next_win_idx,
            start_time_s=t_start,
            end_time_s=t_end,
            start_sample_idx=start_sample,
            end_sample_idx=end_sample,
            sample_count=len(window_raw),
            processing_status=inf_res.status,
            prediction_bpm=inf_res.prediction_bpm,
            inference_latency_ms=inf_res.latency_ms,
            provenance_note=inf_res.provenance_note,
            error_reason=inf_res.error_message,
        )
        self.window_history.append(record)

        # Update simulation clock
        self.current_window_idx = next_win_idx
        self.current_sample_idx = end_sample
        self.elapsed_sim_time_s = t_end

        # If this was the last window, mark completed
        if (next_win_idx + 1) * self.hop_samples + self.win_samples > len(self.raw_signal):
            self.playback_state = "COMPLETED"

        return record

    def advance_time(self, delta_sim_seconds: float) -> List[WindowHistoryRecord]:
        """Advances internal virtual clock by delta_sim_seconds and processes completed windows."""
        if self.playback_state != "RUNNING" or len(self.raw_signal) == 0:
            return []

        target_time = self.elapsed_sim_time_s + delta_sim_seconds
        records = []

        # Process any window that finishes before or at target_time
        while self.playback_state == "RUNNING":
            next_win_idx = self.current_window_idx + 1
            next_win_end_t = (next_win_idx * self.hop_s) + self.win_s

            if next_win_end_t <= target_time:
                rec = self.step()
                if rec:
                    records.append(rec)
                else:
                    break
            else:
                self.elapsed_sim_time_s = round(target_time, 3)
                self.current_sample_idx = min(len(self.raw_signal), int(round(self.elapsed_sim_time_s * self.fs_hz)))
                break

        return records

    def get_snapshot(self) -> SimulationSnapshot:
        """Returns structured JSON-serializable snapshot of current state."""
        compat = self.model_engine.get_compatibility_status()
        tot_samples = len(self.raw_signal)
        tot_dur = tot_samples / self.fs_hz if self.fs_hz > 0 else 0.0

        latest_bpm = self.latest_prediction.prediction_bpm if self.latest_prediction else None
        latest_lat = self.latest_prediction.latency_ms if self.latest_prediction else 0.0

        return SimulationSnapshot(
            session_id=self.session_id,
            recording_id=self.recording_id,
            file_path=str(self.loaded_record.file_path) if self.loaded_record else "",
            playback_state=self.playback_state,
            simulation_speed=self.simulation_speed,
            elapsed_sim_time_s=round(self.elapsed_sim_time_s, 2),
            current_sample_idx=self.current_sample_idx,
            current_window_idx=self.current_window_idx,
            total_samples=tot_samples,
            total_duration_s=round(tot_dur, 2),
            sampling_rate_hz=round(self.fs_hz, 4),
            window_duration_s=self.win_s,
            hop_duration_s=self.hop_s,
            window_samples=self.win_samples,
            hop_samples=self.hop_samples,
            total_windows=self.total_windows,
            signal_quality_status=self.signal_quality_status,
            model_name=compat.model_name,
            operating_mode=compat.operating_mode,
            model_status_reason=compat.status_reason,
            latest_prediction_bpm=latest_bpm,
            latest_latency_ms=latest_lat,
            processed_window_count=len(self.window_history),
            error_message=self.error_message,
            model_state=compat.model_state,
            data_mode=compat.data_mode,
        )

    def get_waveform_display_data(self, max_points: int = 500) -> Dict[str, Any]:
        """Provides downsampled waveform points for smooth chart rendering."""
        if len(self.raw_signal) == 0:
            return {"times_s": [], "raw_radar": [], "filtered_radar": [], "window_bounds": None}

        # Visible range: current rolling window or last 15 seconds of buffer
        cur_end = max(self.win_samples, self.current_sample_idx)
        cur_start = max(0, cur_end - int(round(15.0 * self.fs_hz)))

        sub_raw = self.raw_signal[cur_start:cur_end]
        sub_filt = self.filtered_signal[cur_start:cur_end]
        sub_t = np.arange(cur_start, cur_end) / self.fs_hz

        # Downsample for responsive UI rendering
        step = max(1, len(sub_raw) // max_points)
        t_down = sub_t[::step].round(3).tolist()
        raw_down = sub_raw[::step].round(5).tolist()
        filt_down = sub_filt[::step].round(5).tolist()

        # Active window highlight boundaries
        win_bounds = None
        if self.current_window_idx >= 0:
            w_start_s = round(self.current_window_idx * self.hop_s, 3)
            w_end_s = round(w_start_s + self.win_s, 3)
            win_bounds = {"start_time_s": w_start_s, "end_time_s": w_end_s}

        return {
            "times_s": t_down,
            "raw_radar": raw_down,
            "filtered_radar": filt_down,
            "window_bounds": win_bounds,
        }

    def export_session_logs(self, output_dir: Union[str, Path]) -> Tuple[Path, Path]:
        """Exports session metadata and window history to JSON and CSV."""
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)

        meta_json_path = out_p / f"{self.session_id}_metadata.json"
        history_csv_path = out_p / f"{self.session_id}_history.csv"

        # 1. Write metadata JSON
        snap = asdict(self.get_snapshot())
        snap["exported_at_utc"] = datetime.now(timezone.utc).isoformat()
        snap["hardware_disclaimer"] = "RECORDED DATA SIMULATION — HARDWARE CLOCK UNVERIFIED — NOT CLINICAL SOFTWARE"

        with open(meta_json_path, "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)

        # 2. Write history CSV
        fieldnames = [
            "window_index",
            "start_time_s",
            "end_time_s",
            "start_sample_idx",
            "end_sample_idx",
            "sample_count",
            "processing_status",
            "prediction_bpm",
            "inference_latency_ms",
            "provenance_note",
            "error_reason",
        ]
        with open(history_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in self.window_history:
                writer.writerow(asdict(r))

        return meta_json_path, history_csv_path
