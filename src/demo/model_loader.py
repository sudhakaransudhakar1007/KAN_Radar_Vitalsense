"""Safe Model Loader and Inference Engine for Demo Simulation.

Enforces strict research integrity:
1. Validates model checkpoint existence, architecture match, and weight compatibility.
2. If no valid checkpoint is found, operates in Mode A (Visualization Only - Model Unavailable).
3. Never fabricates random or synthetic HR predictions.
4. Executes pure evaluation inference without weight updates or training.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf

from src.kan.kan_model import (
    CNNRegressor,
    ConvFeatureExtractor,
    KANFeatureRegressor,
    KANRegressor,
    MeanPredictorBaseline,
    MLPRegressor,
)
from src.kan.normalization import TargetNormalizer


def check_scientific_gate_status(base_dir: Optional[Path] = None) -> Tuple[bool, str]:
    """Inspects Phase 2A and Phase 3 gate status on disk.

    Returns:
        (is_open, explanation)
    """
    root = base_dir or Path(__file__).resolve().parents[2]
    p2a_audit = root / "outputs" / "phase2a" / "step2b_consistency_audit.md"
    if p2a_audit.exists():
        content = p2a_audit.read_text(encoding="utf-8", errors="ignore")
        if "FINALIZATION GATE CLOSED" not in content or "RECONCILIATION PARTIAL" in content:
            return True, "Phase 2A gate is OPEN (outputs/phase2a/step2b_consistency_audit.md)"

    p3_approval = root / "outputs" / "phase3" / "run_002" / "approval_record.json"
    if p3_approval.exists():
        try:
            d = json.loads(p3_approval.read_text(encoding="utf-8"))
            if d.get("governance_stop_condition", {}).get("phase2a_finalization_gate") == "OPEN":
                return True, "Phase 2A gate is OPEN (outputs/phase3/run_002/approval_record.json)"
        except Exception:
            pass

    return False, "Gate closed"


def is_synthetic_checkpoint(checkpoint_path: Path) -> Tuple[bool, str]:
    """Inspects checkpoint path and neighboring metadata to determine if it is synthetic."""
    p_str = str(checkpoint_path).lower().replace("\\", "/")
    if "synthetic" in p_str:
        return True, "Checkpoint path contains 'synthetic'"

    curr = checkpoint_path.parent
    for _ in range(4):
        if curr == curr.parent:
            break
        cfg_file = curr / "training_config.json"
        if cfg_file.exists():
            try:
                cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
                if cfg.get("mode") == "synthetic":
                    return True, f"training_config.json in {curr.name} has mode='synthetic'"
            except Exception:
                pass
        meta_file = curr / "run_metadata.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if meta.get("mode") == "synthetic" or meta.get("benchmark_type") == "SYNTHETIC_BENCHMARK":
                    return True, f"run_metadata.json in {curr.name} has mode='synthetic'"
            except Exception:
                pass
        curr = curr.parent

    return False, "No synthetic metadata detected"


@dataclass
class ModelInferenceResult:
    """Record of a single window model inference attempt."""
    window_index: int
    start_time_s: float
    end_time_s: float
    model_name: str
    status: str  # 'SUCCESS', 'MODEL_UNAVAILABLE', 'SYNTHETIC_DEMO_ONLY', 'REAL_MODEL_BLOCKED_BY_APPROVAL_GATE', 'INVALID_INPUT', 'INFERENCE_ERROR'
    prediction_bpm: Optional[float]
    raw_normalized_output: Optional[float]
    latency_ms: float
    error_message: str
    provenance_note: str


@dataclass
class ModelCompatibilityStatus:
    """Metadata regarding model and checkpoint verification."""
    model_name: str
    is_available: bool
    operating_mode: str  # 'SAVED_MODEL_INFERENCE' or 'VISUALIZATION_ONLY'
    checkpoint_path: Optional[str]
    input_shape: Tuple[int, ...]
    parameters_count: int
    normalization_available: bool
    status_reason: str
    model_state: str = "MODEL_UNAVAILABLE"  # 'MODEL_UNAVAILABLE', 'SYNTHETIC_DEMO_ONLY', 'REAL_MODEL_BLOCKED_BY_APPROVAL_GATE', 'REAL_MODEL_READY'
    data_mode: str = "RECORDED_RADAR_PLAYBACK"


class SafeModelInferenceEngine:
    """Safe evaluation-only inference engine with strict checkpoint guards."""

    def __init__(
        self,
        model_name: str = "KANRegressor",
        checkpoint_path: Optional[Union[str, Path]] = None,
        normalizer_stats: Optional[Dict[str, float]] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ):
        self.model_name = model_name
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.normalizer = TargetNormalizer()
        self.base_dir = Path(base_dir) if base_dir else None
        self.model: Optional[tf.keras.Model] = None
        self.is_compatible: bool = False
        self.model_state: str = "MODEL_UNAVAILABLE"
        self.data_mode: str = "RECORDED_RADAR_PLAYBACK"
        self.status_reason: str = "Uninitialized"

        # Initialize normalizer if statistics provided
        if normalizer_stats and "train_mean" in normalizer_stats and "train_std" in normalizer_stats:
            self.normalizer.train_mean = float(normalizer_stats["train_mean"])
            self.normalizer.train_std = float(normalizer_stats["train_std"])
            self.normalizer.is_fitted = True

        self._verify_and_load_checkpoint()

    def _verify_and_load_checkpoint(self) -> None:
        """Inspects and verifies model checkpoint without fitting or training."""
        if self.checkpoint_path is None or not self.checkpoint_path.exists():
            self.model_state = "MODEL_UNAVAILABLE"
            self.is_compatible = False
            self.model = None
            self.status_reason = (
                f"No verified trained checkpoint found for {self.model_name}. "
                "Phase 2A Finalization Gate remains OPEN; real-data training was not executed. "
                "Operating strictly in Visualization Only mode."
            )
            return

        # Check if checkpoint is synthetic
        is_synth, synth_reason = is_synthetic_checkpoint(self.checkpoint_path)
        if is_synth:
            self.model_state = "SYNTHETIC_DEMO_ONLY"
            self.is_compatible = False
            self.model = None
            self.status_reason = (
                f"Synthetic benchmark checkpoint detected ({synth_reason}). "
                "Synthetic models must NEVER be presented as approved real-data models or used to predict on real radar data. "
                "Heart-rate predictions are strictly suppressed to uphold research integrity."
            )
            return

        # Check scientific gate status for real checkpoints
        gate_open, gate_reason = check_scientific_gate_status(base_dir=self.base_dir)
        if gate_open:
            self.model_state = "REAL_MODEL_BLOCKED_BY_APPROVAL_GATE"
            self.is_compatible = False
            self.model = None
            self.status_reason = (
                f"Real-model checkpoint supplied, but Phase 2A/2C Finalization Gate remains OPEN ({gate_reason}). "
                "Real-data model inference is legally and scientifically blocked pending formal PI gate closure."
            )
            return

        try:
            # Instantiate architecture based on model_name
            if self.model_name == "KANRegressor":
                model_inst = KANRegressor(input_dim=3333, latent_dim=16, hidden_dim=8)
            elif self.model_name == "CNNRegressor":
                model_inst = CNNRegressor(input_dim=3333, latent_dim=16)
            elif self.model_name == "MLPRegressor":
                model_inst = MLPRegressor(input_dim=3333, latent_dim=16, hidden_dim=8)
            else:
                self.model_state = "MODEL_UNAVAILABLE"
                self.is_compatible = False
                self.status_reason = f"Unsupported model architecture: {self.model_name}"
                return

            # Build model with expected input shape
            dummy_input = tf.zeros((1, 3333), dtype=tf.float32)
            _ = model_inst(dummy_input)

            # Attempt weight loading
            model_inst.load_weights(str(self.checkpoint_path))

            # Verify normalizer is fitted
            if not self.normalizer.is_fitted:
                self.model_state = "MODEL_UNAVAILABLE"
                self.is_compatible = False
                self.status_reason = "Checkpoint loaded but target normalization parameters are missing."
                return

            self.model = model_inst
            self.is_compatible = True
            self.model_state = "REAL_MODEL_READY"
            self.status_reason = f"Valid real model checkpoint verified and loaded from {self.checkpoint_path.name}."

        except Exception as e:
            self.model_state = "MODEL_UNAVAILABLE"
            self.is_compatible = False
            self.model = None
            self.status_reason = f"Checkpoint verification failed: {str(e)}"

    def get_compatibility_status(self) -> ModelCompatibilityStatus:
        """Returns structured compatibility status for UI and logs."""
        mode = "SAVED_MODEL_INFERENCE" if self.is_compatible else "VISUALIZATION_ONLY"
        param_count = 0
        if self.model is not None:
            param_count = sum(v.numpy().size for v in self.model.trainable_variables)
        elif self.model_name == "KANRegressor":
            param_count = 4720
        elif self.model_name == "CNNRegressor":
            param_count = 3377
        elif self.model_name == "MLPRegressor":
            param_count = 3505

        return ModelCompatibilityStatus(
            model_name=self.model_name,
            is_available=self.is_compatible,
            operating_mode=mode,
            checkpoint_path=str(self.checkpoint_path) if self.checkpoint_path else None,
            input_shape=(1, 3333),
            parameters_count=param_count,
            normalization_available=self.normalizer.is_fitted,
            status_reason=self.status_reason,
            model_state=self.model_state,
            data_mode=self.data_mode,
        )

    def predict_window(
        self,
        window_signal: np.ndarray,
        window_index: int,
        start_time_s: float,
        end_time_s: float,
    ) -> ModelInferenceResult:
        """Runs evaluation-only inference on a single 10-second radar window."""
        t0 = time.perf_counter()

        # If model is unavailable or not permitted, return honest status immediately
        if not self.is_compatible or self.model is None:
            return ModelInferenceResult(
                window_index=window_index,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                model_name=self.model_name,
                status=self.model_state,
                prediction_bpm=None,
                raw_normalized_output=None,
                latency_ms=0.0,
                error_message=self.status_reason,
                provenance_note=f"VISUALIZATION_ONLY: Prediction suppressed ({self.model_state})",
            )

        # Validate input signal dimensions
        arr = np.array(window_signal, dtype=np.float32).flatten()
        if len(arr) != 3333:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return ModelInferenceResult(
                window_index=window_index,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                model_name=self.model_name,
                status="INVALID_INPUT",
                prediction_bpm=None,
                raw_normalized_output=None,
                latency_ms=round(latency_ms, 2),
                error_message=f"Expected 3333 samples, got {len(arr)}",
                provenance_note="REJECTED_WINDOW: Incomplete sample count",
            )

        if not np.all(np.isfinite(arr)):
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return ModelInferenceResult(
                window_index=window_index,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                model_name=self.model_name,
                status="INVALID_INPUT",
                prediction_bpm=None,
                raw_normalized_output=None,
                latency_ms=round(latency_ms, 2),
                error_message="Window contains non-finite values (NaN or Inf)",
                provenance_note="REJECTED_WINDOW: Non-finite values detected",
            )

        try:
            # Prepare tensor without gradients
            input_tensor = tf.convert_to_tensor(arr.reshape(1, 3333), dtype=tf.float32)
            raw_out = self.model(input_tensor, training=False)
            norm_val = float(raw_out.numpy().flatten()[0])

            # Invert target normalization to get physical BPM
            pred_bpm = float(self.normalizer.inverse_transform(np.array([norm_val]))[0])
            latency_ms = (time.perf_counter() - t0) * 1000.0

            # Physiological sanity check
            if not (30.0 <= pred_bpm <= 220.0):
                return ModelInferenceResult(
                    window_index=window_index,
                    start_time_s=start_time_s,
                    end_time_s=end_time_s,
                    model_name=self.model_name,
                    status="INFERENCE_ERROR",
                    prediction_bpm=None,
                    raw_normalized_output=norm_val,
                    latency_ms=round(latency_ms, 2),
                    error_message=f"Model output {pred_bpm:.2f} BPM is outside physiological contract (30-220 BPM)",
                    provenance_note="OUT_OF_CONTRACT: Output rejected by physiological safety guard",
                )

            return ModelInferenceResult(
                window_index=window_index,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                model_name=self.model_name,
                status="SUCCESS",
                prediction_bpm=round(pred_bpm, 2),
                raw_normalized_output=round(norm_val, 4),
                latency_ms=round(latency_ms, 2),
                error_message="",
                provenance_note="GENUINE_MODEL_PREDICTION",
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return ModelInferenceResult(
                window_index=window_index,
                start_time_s=start_time_s,
                end_time_s=end_time_s,
                model_name=self.model_name,
                status="INFERENCE_ERROR",
                prediction_bpm=None,
                raw_normalized_output=None,
                latency_ms=round(latency_ms, 2),
                error_message=f"Inference exception: {str(e)}",
                provenance_note="EXCEPTION_DURING_INFERENCE",
            )
