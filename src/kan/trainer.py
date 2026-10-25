"""Subject-Independent KAN Training Orchestrator with Inner-Validation Checkpointing.

Enforces:
1. Fail-closed Phase 2A/2C gate blocker protection against unauthorized real-data training.
2. Isolated synthetic fixtures for synthetic-mode benchmarking (zero real data access).
3. Strict 3-way subject-independent partitioning (inner-train, inner-val, held-out test).
4. Feature scaling and target normalization fitted strictly on inner-train subjects.
5. Early stopping and best checkpoint selection evaluated strictly on inner-validation loss.
6. Metric calculation strictly in physical BPM units after inverse-transforming predictions.
7. Comprehensive provenance tracking (software versions, seeds, git state, split manifest).
"""

from __future__ import annotations

import csv
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Configure non-interactive tempdir for libraries
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import tensorflow as tf
from tensorflow import keras

from src.kan.feature_scaler import FeatureScaler
from src.kan.kan_layer import KANLayer
from src.kan.kan_model import (
    CNNRegressor,
    ConvFeatureExtractor,
    KANFeatureRegressor,
    KANRegressor,
    MLPRegressor,
    MeanPredictorBaseline,
)
from src.kan.loso_evaluator import GateBlockerError
from src.kan.normalization import TargetNormalizer


@dataclass
class TrainingConfig:
    """Configuration record for reproducible KAN training."""
    run_id: str = "run_synthetic_001"
    mode: str = "synthetic"  # "synthetic" or "real"
    seed: int = 42
    epochs: int = 15
    batch_size: int = 16
    learning_rate: float = 0.005
    weight_decay: float = 1e-4
    patience: int = 5
    model_type: str = "kan"  # "kan", "mlp", "cnn", "mean"
    latent_dim: int = 16
    hidden_dim: int = 8
    grid_size: int = 5
    spline_order: int = 3
    grid_range: Tuple[float, float] = (-1.0, 1.0)
    feature_scaling: str = "standard"  # "standard", "minmax", "none"
    target_normalization: bool = True
    val_subjects_count: int = 2
    synthetic_subjects_count: int = 8
    synthetic_windows_per_subject: int = 10
    output_dir: str = "outputs/phase5/run_synthetic_001"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["grid_range"] = list(self.grid_range)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TrainingConfig:
        d = dict(data)
        if "grid_range" in d and isinstance(d["grid_range"], list):
            d["grid_range"] = tuple(d["grid_range"])
        return cls(**d)

    def save_json(self, filepath: Union[str, Path]) -> Path:
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return p

    @classmethod
    def load_json(cls, filepath: Union[str, Path]) -> TrainingConfig:
        p = Path(filepath)
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8")))


@dataclass
class FoldSplit:
    """Subject partition record for a single LOSO cross-validation fold."""
    fold: int
    test_subject: str
    val_subjects: List[str]
    train_subjects: List[str]
    train_samples: int = 0
    val_samples: int = 0
    test_samples: int = 0
    subject_leakage_detected: bool = False


@dataclass
class FoldMetrics:
    """Biomedical evaluation metrics on held-out test fold."""
    fold: int
    test_subject: str
    mae_bpm: float
    rmse_bpm: float
    bias_bpm: float
    pearson_r: float
    within_3bpm_pct: float
    within_5bpm_pct: float
    best_epoch: int
    best_val_loss: float


def set_deterministic_seeds(seed: int) -> None:
    """Set seeds across Python, NumPy, and TensorFlow for reproducible training."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    try:
        keras.utils.set_random_seed(seed)
    except Exception:
        pass


def verify_gate_approval_for_real_data(base_dir: Path) -> Tuple[bool, str]:
    """Fail-closed multi-artifact verification for Phase 2A and Phase 2C approvals.

    A markdown status string alone is NOT sufficient. Requires:
    1. Phase 2A audit closed and training permitted.
    2. Phase 2A checklist fully closed without pending or partial items.
    3. Label spec approved with valid investigator signature.
    4. Label status note confirming active approval (not draft).
    5. Formal signed investigator decision file present on disk.

    Returns:
        (is_approved, reason)
    """
    audit_file = base_dir / "outputs" / "phase2a" / "step2b_consistency_audit.md"
    checklist_file = base_dir / "outputs" / "closure" / "gate_checklist.csv"
    spec_file = base_dir / "outputs" / "closure" / "spec" / "label_spec_v1.json"
    spec_note_file = base_dir / "outputs" / "closure" / "spec_status_note.md"
    pi_decision_file = base_dir / "outputs" / "closure" / "investigator_decision.md"

    # 1. Audit file check
    if not audit_file.exists():
        return False, f"Phase 2A audit artifact missing: {audit_file}"
    audit_text = audit_file.read_text(encoding="utf-8")
    if "FINALIZATION GATE CLOSED" not in audit_text or "SUPERVISED TRAINING PERMITTED" not in audit_text:
        return False, "Phase 2A Finalization Gate remains OPEN in step2b_consistency_audit.md."
    if "FINALIZATION GATE: OPEN" in audit_text or "RECONCILIATION PARTIAL" in audit_text:
        return False, "Phase 2A audit text explicitly contains OPEN/PARTIAL status."

    # 2. Checklist check
    if not checklist_file.exists():
        return False, f"Gate checklist artifact missing: {checklist_file}"
    checklist_text = checklist_file.read_text(encoding="utf-8")
    for blocked_kw in ["NOT_YET_APPROVED", "OPEN", "UNVERIFIED", "NOT_YET_SUPPORTED"]:
        if blocked_kw in checklist_text:
            return False, f"Gate checklist contains unresolved blocker status '{blocked_kw}'."

    # 3. Spec approval check
    if not spec_file.exists():
        return False, f"Label specification missing: {spec_file}"
    try:
        spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Label specification is invalid JSON: {e}"
    if not spec_data.get("approved_by"):
        return False, "Label specification approved_by field is empty (unapproved draft)."
    if spec_data.get("governance", {}).get("status") != "APPROVED":
        return False, f"Label spec status is '{spec_data.get('governance', {}).get('status')}', expected 'APPROVED'."

    # 4. Spec status note check
    if spec_note_file.exists():
        note_text = spec_note_file.read_text(encoding="utf-8")
        if "DRAFT_UNAPPROVED" in note_text:
            return False, "Spec status note certifies label_spec_v1.json as DRAFT_UNAPPROVED."

    # 5. Formal investigator decision file
    if not pi_decision_file.exists():
        return False, f"Formal investigator authorization file missing: {pi_decision_file}"

    return True, "All Phase 2A and Phase 2C scientific approvals are formally verified and closed."


def generate_synthetic_dataset(
    num_subjects: int = 8,
    windows_per_subject: int = 10,
    window_len: int = 3333,
    fs: float = 333.3333,
    seed: int = 42,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Generates isolated synthetic multi-subject radar vital-sign windows and HR labels.

    Does NOT access or read raw data or real labels.
    All outputs are explicitly flagged as SYNTHETIC_BENCHMARK.
    """
    rng = np.random.RandomState(seed)
    total_samples = num_subjects * windows_per_subject
    t = np.arange(window_len) / fs

    records = []
    X_windows = np.zeros((total_samples, window_len), dtype=np.float32)
    y_bpm = np.zeros(total_samples, dtype=np.float32)

    sample_idx = 0
    for s_idx in range(1, num_subjects + 1):
        subj_id = f"SYNTH_S{s_idx:02d}"
        base_hr = rng.uniform(58.0, 85.0)

        for w_idx in range(windows_per_subject):
            cond = "Resting" if w_idx % 2 == 0 else "Apnea"
            hr = float(np.clip(base_hr + rng.normal(0.0, 2.5), 45.0, 120.0))
            f_cardiac = hr / 60.0
            f_resp = 0.22 if cond == "Resting" else 0.05

            # Synthesize physiological radar chest displacement
            cardiac_signal = 0.7 * np.sin(2.0 * np.pi * f_cardiac * t) + 0.25 * np.sin(4.0 * np.pi * f_cardiac * t)
            resp_signal = (0.5 if cond == "Resting" else 0.08) * np.sin(2.0 * np.pi * f_resp * t)
            noise = rng.normal(0.0, 0.08, size=window_len)

            X_windows[sample_idx] = (cardiac_signal + resp_signal + noise).astype(np.float32)
            y_bpm[sample_idx] = round(hr, 2)

            records.append({
                "sample_index": sample_idx,
                "subject_id": subj_id,
                "condition": cond,
                "window_index": w_idx,
                "reference_hr_bpm": round(hr, 2),
                "is_synthetic": True,
                "benchmark_label": "SYNTHETIC_BENCHMARK",
            })
            sample_idx += 1

    manifest_df = pd.DataFrame(records)
    return manifest_df, X_windows, y_bpm


def build_loso_splits_with_inner_val(
    manifest_df: pd.DataFrame,
    val_subjects_count: int = 2,
    seed: int = 42,
) -> List[FoldSplit]:
    """Builds strict 3-way subject-independent LOSO splits with inner validation."""
    subjects = sorted(manifest_df["subject_id"].unique().tolist())
    num_subjs = len(subjects)
    if num_subjs < 3:
        raise ValueError(f"Need at least 3 subjects for train/val/test splits, got {num_subjs}")

    effective_val_count = min(val_subjects_count, num_subjs - 2)
    effective_val_count = max(1, effective_val_count)

    splits: List[FoldSplit] = []
    for fold_idx, test_subj in enumerate(subjects, start=1):
        candidate_pool = [s for s in subjects if s != test_subj]
        
        # Deterministic rotation for inner validation subjects
        val_subjs = [
            candidate_pool[(fold_idx - 1 + i) % len(candidate_pool)]
            for i in range(effective_val_count)
        ]
        train_subjs = [s for s in candidate_pool if s not in val_subjs]

        # Assert strict subject disjointness
        s_train = set(train_subjs)
        s_val = set(val_subjs)
        s_test = {test_subj}

        leakage = bool((s_train & s_val) or (s_train & s_test) or (s_val & s_test))
        if leakage:
            raise RuntimeError(
                f"Subject leakage detected in fold {fold_idx}: "
                f"train={s_train}, val={s_val}, test={s_test}"
            )

        n_train = int(manifest_df["subject_id"].isin(s_train).sum())
        n_val = int(manifest_df["subject_id"].isin(s_val).sum())
        n_test = int(manifest_df["subject_id"].isin(s_test).sum())

        splits.append(
            FoldSplit(
                fold=fold_idx,
                test_subject=test_subj,
                val_subjects=sorted(val_subjs),
                train_subjects=sorted(train_subjs),
                train_samples=n_train,
                val_samples=n_val,
                test_samples=n_test,
                subject_leakage_detected=leakage,
            )
        )

    return splits


class KANTrainer:
    """Trainer orchestrating reproducible LOSO cross-validation for KAN and comparative baselines."""

    def __init__(
        self,
        config: TrainingConfig,
        base_dir: Optional[Path] = None,
    ):
        self.config = config
        self.base_dir = base_dir or Path(__file__).resolve().parents[2]
        self.output_dir = self.base_dir / config.output_dir

    def _collect_run_metadata(self) -> Dict[str, Any]:
        """Collects environment, git, and execution provenance metadata."""
        git_commit = "UNKNOWN"
        git_dirty = False
        git_status_detail = "UNCHECKED"

        git_bin = shutil.which("git")
        has_git_dir = (self.base_dir / ".git").exists() or (self.base_dir.parent / ".git").exists()

        if git_bin is None:
            git_commit = "GIT_EXECUTABLE_NOT_FOUND"
            git_status_detail = "git executable is not installed or not present on system PATH"
        elif not has_git_dir:
            git_commit = "NOT_A_GIT_REPOSITORY"
            git_status_detail = "No .git directory found at repository root"
        else:
            try:
                r = subprocess.run(
                    [git_bin, "rev-parse", "HEAD"],
                    cwd=str(self.base_dir),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if r.returncode == 0:
                    git_commit = r.stdout.strip()
                    git_status_detail = "OK"
                else:
                    git_commit = "UNKNOWN_GIT_ERROR"
                    git_status_detail = r.stderr.strip() or f"git exit code {r.returncode}"
                r_diff = subprocess.run(
                    [git_bin, "status", "--porcelain"],
                    cwd=str(self.base_dir),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                git_dirty = bool(r_diff.stdout.strip())
            except Exception as e:
                git_commit = "GIT_EXECUTION_EXCEPTION"
                git_status_detail = str(e)

        return {
            "run_id": self.config.run_id,
            "mode": self.config.mode,
            "benchmark_type": "SYNTHETIC_BENCHMARK" if self.config.mode == "synthetic" else "REAL_DATA",
            "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "tensorflow_version": tf.__version__,
            "keras_version": keras.__version__,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "git_status_detail": git_status_detail,
            "random_seeds": {
                "configured_seed": self.config.seed,
                "pythonhashseed": os.environ.get("PYTHONHASHSEED", str(self.config.seed)),
            },
            "scientific_gate_status": "OPEN_TRAINING_BLOCKED" if self.config.mode == "real" else "BYPASS_SYNTHETIC_FIXTURE_ONLY",
        }

    def _instantiate_model(self, runtime_input_dim: int) -> keras.Model:
        """Instantiate framework-verified model using validated runtime dimensions."""
        if runtime_input_dim <= 0:
            raise ValueError(f"Invalid runtime_input_dim: {runtime_input_dim}")

        m_type = self.config.model_type.lower()
        if m_type == "kan":
            return KANRegressor(
                input_dim=runtime_input_dim,
                latent_dim=self.config.latent_dim,
                hidden_dim=self.config.hidden_dim,
                grid_size=self.config.grid_size,
                spline_order=self.config.spline_order,
            )
        elif m_type == "mlp":
            return MLPRegressor(
                input_dim=runtime_input_dim,
                latent_dim=self.config.latent_dim,
                hidden_dim=self.config.hidden_dim,
            )
        elif m_type == "cnn":
            return CNNRegressor(
                input_dim=runtime_input_dim,
                latent_dim=self.config.latent_dim,
            )
        else:
            raise ValueError(f"Unsupported model_type: '{self.config.model_type}'")

    @staticmethod
    def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute biomedical evaluation metrics strictly in physical BPM units."""
        yt = np.asarray(y_true, dtype=np.float64).flatten()
        yp = np.asarray(y_pred, dtype=np.float64).flatten()
        err = yp - yt
        abs_err = np.abs(err)

        mae = float(np.mean(abs_err))
        rmse = float(np.sqrt(np.mean(err ** 2)))
        bias = float(np.mean(err))

        if len(yt) > 1 and np.std(yt) > 1e-6 and np.std(yp) > 1e-6:
            r = float(np.corrcoef(yt, yp)[0, 1])
            if np.isnan(r):
                r = 0.0
        else:
            r = 0.0

        w3 = float(np.mean(abs_err <= 3.0) * 100.0)
        w5 = float(np.mean(abs_err <= 5.0) * 100.0)

        return {
            "mae_bpm": round(mae, 3),
            "rmse_bpm": round(rmse, 3),
            "bias_bpm": round(bias, 3),
            "pearson_r": round(r, 4),
            "within_3bpm_pct": round(w3, 2),
            "within_5bpm_pct": round(w5, 2),
        }

    def execute_training(
        self,
        custom_manifest: Optional[pd.DataFrame] = None,
        custom_X: Optional[np.ndarray] = None,
        custom_y: Optional[np.ndarray] = None,
        max_folds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Executes complete subject-independent training pipeline with fold logs and checkpoints."""
        # 1. Enforce fail-closed gate checks before accessing any real data
        if self.config.mode == "real":
            is_approved, reason = verify_gate_approval_for_real_data(self.base_dir)
            if not is_approved:
                raise GateBlockerError(f"Real-data training BLOCKED: {reason}")
            raise NotImplementedError("Real-data dataset loading is not permitted while Phase 2A is OPEN.")

        # 2. Setup output directory cleanly
        self.output_dir.mkdir(parents=True, exist_ok=True)
        set_deterministic_seeds(self.config.seed)

        # 3. Load or generate data
        if custom_manifest is not None and custom_X is not None and custom_y is not None:
            manifest_df = custom_manifest.copy()
            X_all = np.asarray(custom_X, dtype=np.float32)
            y_all = np.asarray(custom_y, dtype=np.float32)
        else:
            manifest_df, X_all, y_all = generate_synthetic_dataset(
                num_subjects=self.config.synthetic_subjects_count,
                windows_per_subject=self.config.synthetic_windows_per_subject,
                seed=self.config.seed,
            )

        # Validate input dimensions and finite numbers
        if X_all.ndim != 2:
            raise ValueError(f"Input feature tensor must be 2D, got shape {X_all.shape}")
        if np.any(~np.isfinite(X_all)):
            raise ValueError("Input feature tensor contains NaN or Inf.")
        if np.any(~np.isfinite(y_all)):
            raise ValueError("Target HR labels contain NaN or Inf.")

        runtime_input_dim = X_all.shape[1]

        # 4. Generate deterministic LOSO splits
        splits = build_loso_splits_with_inner_val(
            manifest_df,
            val_subjects_count=self.config.val_subjects_count,
            seed=self.config.seed,
        )
        if max_folds is not None:
            splits = splits[:max_folds]

        # Save split manifest
        split_records = []
        for s in splits:
            split_records.append({
                "fold": s.fold,
                "test_subject": s.test_subject,
                "val_subjects": ";".join(s.val_subjects),
                "train_subjects": ";".join(s.train_subjects),
                "train_samples": s.train_samples,
                "val_samples": s.val_samples,
                "test_samples": s.test_samples,
                "subject_leakage_detected": s.subject_leakage_detected,
            })
        split_df = pd.DataFrame(split_records)
        split_df.to_csv(self.output_dir / "fold_split_manifest.csv", index=False)

        # Save metadata and config
        metadata = self._collect_run_metadata()
        (self.output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self.config.save_json(self.output_dir / "training_config.json")

        # 5. Train each fold
        fold_results: List[FoldMetrics] = []
        all_test_predictions = []

        folds_dir = self.output_dir / "folds"
        folds_dir.mkdir(parents=True, exist_ok=True)

        for split in splits:
            fold_dir = folds_dir / f"fold_{split.fold:02d}"
            fold_dir.mkdir(parents=True, exist_ok=True)

            train_mask = manifest_df["subject_id"].isin(split.train_subjects).to_numpy()
            val_mask = manifest_df["subject_id"].isin(split.val_subjects).to_numpy()
            test_mask = (manifest_df["subject_id"] == split.test_subject).to_numpy()

            X_tr, y_tr = X_all[train_mask], y_all[train_mask]
            X_va, y_va = X_all[val_mask], y_all[val_mask]
            X_te, y_te = X_all[test_mask], y_all[test_mask]

            # Fit FeatureScaler strictly on inner-train
            scaler = FeatureScaler(scaling_type=self.config.feature_scaling)
            X_tr_s = scaler.fit_transform(X_tr)
            X_va_s = scaler.transform(X_va)
            X_te_s = scaler.transform(X_te)
            scaler.save_json(fold_dir / "feature_scaler.json")

            # Fit TargetNormalizer strictly on inner-train
            target_norm = TargetNormalizer()
            y_tr_n = target_norm.fit_transform(y_tr)
            y_va_n = target_norm.transform(y_va)
            y_te_n = target_norm.transform(y_te)
            (fold_dir / "target_normalizer.json").write_text(
                json.dumps({
                    "train_mean": target_norm.train_mean,
                    "train_std": target_norm.train_std,
                    "sample_count": target_norm.sample_count,
                    "is_fitted": target_norm.is_fitted,
                }, indent=2),
                encoding="utf-8",
            )

            # Save feature schema
            (fold_dir / "feature_schema.json").write_text(
                json.dumps({
                    "runtime_input_dim": runtime_input_dim,
                    "latent_dim": self.config.latent_dim,
                    "scaling_type": self.config.feature_scaling,
                    "temporal_length_samples": runtime_input_dim,
                }, indent=2),
                encoding="utf-8",
            )

            # Baseline vs Neural Models
            if self.config.model_type.lower() == "mean":
                mean_model = MeanPredictorBaseline()
                mean_model.fit(y_tr)
                test_preds_bpm = mean_model.predict(X_te)
                test_metrics = self._compute_metrics(y_te, test_preds_bpm)
                fold_metric = FoldMetrics(
                    fold=split.fold,
                    test_subject=split.test_subject,
                    mae_bpm=test_metrics["mae_bpm"],
                    rmse_bpm=test_metrics["rmse_bpm"],
                    bias_bpm=test_metrics["bias_bpm"],
                    pearson_r=test_metrics["pearson_r"],
                    within_3bpm_pct=test_metrics["within_3bpm_pct"],
                    within_5bpm_pct=test_metrics["within_5bpm_pct"],
                    best_epoch=1,
                    best_val_loss=0.0,
                )
                fold_results.append(fold_metric)

                # Record per-sample test predictions for baseline
                test_sub_df = manifest_df[test_mask].copy()
                test_sub_df["fold"] = split.fold
                test_sub_df["y_true_bpm"] = y_te
                test_sub_df["y_pred_bpm"] = np.round(test_preds_bpm, 2)
                test_sub_df["error_bpm"] = np.round(test_preds_bpm - y_te, 2)
                test_sub_df["abs_error_bpm"] = np.round(np.abs(test_preds_bpm - y_te), 2)
                test_sub_df.to_csv(fold_dir / "predictions_test.csv", index=False)
                all_test_predictions.append(test_sub_df)
                continue

            # Instantiate model
            model = self._instantiate_model(runtime_input_dim)
            optimizer = keras.optimizers.Adam(learning_rate=self.config.learning_rate)
            loss_fn = keras.losses.MeanSquaredError()

            best_val_loss = float("inf")
            best_epoch = 0
            best_weights_path = fold_dir / "best_model.weights.h5"
            history = {"epoch": [], "train_loss": [], "val_loss": [], "val_mae_bpm": []}
            patience_counter = 0

            # Training loop with validation-only early stopping
            for ep in range(1, self.config.epochs + 1):
                # Mini-batch training
                indices = np.arange(len(X_tr_s))
                np.random.shuffle(indices)
                batch_losses = []

                for start_i in range(0, len(indices), self.config.batch_size):
                    batch_idx = indices[start_i:start_i + self.config.batch_size]
                    xb = tf.convert_to_tensor(X_tr_s[batch_idx], dtype=tf.float32)
                    yb = tf.convert_to_tensor(y_tr_n[batch_idx], dtype=tf.float32)

                    with tf.GradientTape() as tape:
                        preds = model(xb, training=True)
                        loss = loss_fn(yb, preds)
                    grads = tape.gradient(loss, model.trainable_variables)
                    optimizer.apply_gradients(zip(grads, model.trainable_variables))
                    batch_losses.append(float(loss.numpy()))

                train_loss = float(np.mean(batch_losses))

                # Validation step (strictly inner validation subjects)
                val_xb = tf.convert_to_tensor(X_va_s, dtype=tf.float32)
                val_preds_norm = model(val_xb, training=False).numpy()
                val_loss = float(loss_fn(y_va_n, val_preds_norm).numpy())

                val_preds_bpm = target_norm.inverse_transform(val_preds_norm)
                val_mae = float(np.mean(np.abs(val_preds_bpm - y_va)))

                history["epoch"].append(ep)
                history["train_loss"].append(round(train_loss, 6))
                history["val_loss"].append(round(val_loss, 6))
                history["val_mae_bpm"].append(round(val_mae, 3))

                # Checkpoint saving on best inner validation loss
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_epoch = ep
                    model.save_weights(str(best_weights_path))
                    patience_counter = 0
                else:
                    patience_counter += 1
                    if patience_counter >= self.config.patience:
                        break

            # Save training history
            (fold_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
            pd.DataFrame(history).to_csv(fold_dir / "history.csv", index=False)

            # Evaluate best checkpoint on held-out test fold
            eval_model = self._instantiate_model(runtime_input_dim)
            eval_model(tf.zeros((1, runtime_input_dim)))
            eval_model.load_weights(str(best_weights_path))

            test_xb = tf.convert_to_tensor(X_te_s, dtype=tf.float32)
            test_preds_norm = eval_model(test_xb, training=False).numpy()
            test_preds_bpm = target_norm.inverse_transform(test_preds_norm)

            test_metrics = self._compute_metrics(y_te, test_preds_bpm)
            fold_metric = FoldMetrics(
                fold=split.fold,
                test_subject=split.test_subject,
                mae_bpm=test_metrics["mae_bpm"],
                rmse_bpm=test_metrics["rmse_bpm"],
                bias_bpm=test_metrics["bias_bpm"],
                pearson_r=test_metrics["pearson_r"],
                within_3bpm_pct=test_metrics["within_3bpm_pct"],
                within_5bpm_pct=test_metrics["within_5bpm_pct"],
                best_epoch=best_epoch,
                best_val_loss=round(best_val_loss, 6),
            )
            fold_results.append(fold_metric)

            # Record per-sample test predictions
            test_sub_df = manifest_df[test_mask].copy()
            test_sub_df["fold"] = split.fold
            test_sub_df["y_true_bpm"] = y_te
            test_sub_df["y_pred_bpm"] = np.round(test_preds_bpm, 2)
            test_sub_df["error_bpm"] = np.round(test_preds_bpm - y_te, 2)
            test_sub_df["abs_error_bpm"] = np.round(np.abs(test_preds_bpm - y_te), 2)
            test_sub_df.to_csv(fold_dir / "predictions_test.csv", index=False)
            all_test_predictions.append(test_sub_df)

        # 6. Aggregate results across folds
        pred_all_df = pd.concat(all_test_predictions, ignore_index=True) if all_test_predictions else pd.DataFrame()
        pred_all_df.to_csv(self.output_dir / "predictions_all_folds.csv", index=False)

        summary_metrics = {
            "run_id": self.config.run_id,
            "benchmark_status": "SYNTHETIC_BENCHMARK",
            "folds_evaluated": len(fold_results),
            "mean_mae_bpm": round(float(np.mean([m.mae_bpm for m in fold_results])), 3),
            "std_mae_bpm": round(float(np.std([m.mae_bpm for m in fold_results])), 3),
            "mean_rmse_bpm": round(float(np.mean([m.rmse_bpm for m in fold_results])), 3),
            "mean_bias_bpm": round(float(np.mean([m.bias_bpm for m in fold_results])), 3),
            "mean_pearson_r": round(float(np.mean([m.pearson_r for m in fold_results])), 4),
            "overall_within_3bpm_pct": round(float(np.mean([m.within_3bpm_pct for m in fold_results])), 2),
            "overall_within_5bpm_pct": round(float(np.mean([m.within_5bpm_pct for m in fold_results])), 2),
            "fold_breakdown": [asdict(m) for m in fold_results],
        }
        (self.output_dir / "summary_metrics.json").write_text(json.dumps(summary_metrics, indent=2), encoding="utf-8")

        # 7. Write completion report
        report_text = f"""# PHASE 5: KAN SYNTHETIC TRAINING BENCHMARK REPORT

**Benchmark Label:** `SYNTHETIC_BENCHMARK` (NO REAL DATA WAS ACCESSED OR USED)  
**Run ID:** `{self.config.run_id}`  
**Execution Timestamp:** `{metadata['execution_timestamp_utc']}`  
**Model Architecture:** `{self.config.model_type.upper()}` (B-spline KAN Layer)  
**Runtime Feature Dimension:** `{runtime_input_dim}`  
**Folds Evaluated:** `{len(fold_results)}`  

---

## 1. Multi-Fold Evaluation Summary

- **Mean MAE:** {summary_metrics['mean_mae_bpm']} +/- {summary_metrics['std_mae_bpm']} BPM
- **Mean RMSE:** {summary_metrics['mean_rmse_bpm']} BPM
- **Mean Bias:** {summary_metrics['mean_bias_bpm']} BPM
- **Mean Pearson r:** {summary_metrics['mean_pearson_r']}
- **Within +/- 3 BPM:** {summary_metrics['overall_within_3bpm_pct']}%
- **Within +/- 5 BPM:** {summary_metrics['overall_within_5bpm_pct']}%

## 2. Hard Gate Compliance Notice
Real-data training remains officially **BLOCKED** because the Phase 2A Finalization Gate is OPEN. This run operated exclusively on isolated synthetic fixtures to verify gradient updates, checkpointing, and leakage-free normalization.
"""
        (self.output_dir / "phase5_synthetic_run_report.md").write_text(report_text, encoding="utf-8")

        return summary_metrics
