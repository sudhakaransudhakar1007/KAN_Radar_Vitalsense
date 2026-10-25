"""Phase 6B Artifact and Reproducibility Validator.

Verifies the integrity, presence, schema, subject isolation, and metadata
completeness of synthetic benchmark experiment runs without modifying or retraining them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


class ArtifactValidationError(Exception):
    """Raised when an expected artifact fails presence, schema, or integrity checks."""
    pass


def validate_synthetic_run_artifacts(
    base_dir: Path,
    expected_models: List[str] = None,
    expected_subjects: int = 8,
    expected_windows_per_subject: int = 10,
) -> Dict[str, Any]:
    """Inspects and validates synthetic benchmark artifacts on disk.

    Args:
        base_dir: Path to directory containing benchmark outputs (e.g., outputs/phase6b).
        expected_models: List of model identifiers expected (default: ['kan', 'mlp', 'cnn', 'mean']).
        expected_subjects: Number of unique held-out subjects expected (default: 8).
        expected_windows_per_subject: Number of windows per subject expected (default: 10).

    Returns:
        Validation report dictionary with status, audited files, and findings.
    """
    if expected_models is None:
        expected_models = ["kan", "mlp", "cnn", "mean"]

    total_expected_windows = expected_subjects * expected_windows_per_subject
    report: Dict[str, Any] = {
        "base_dir": str(base_dir),
        "status": "PASS",
        "models_validated": [],
        "errors": [],
        "warnings": [],
        "files_checked": [],
    }

    def record_file(p: Path) -> Path:
        report["files_checked"].append(str(p.resolve()))
        return p

    def record_error(msg: str) -> None:
        report["status"] = "FAIL"
        report["errors"].append(msg)

    # 1. Root comparison artifacts
    root_artifacts = [
        "pooled_comparison.csv",
        "per_subject_comparison.csv",
        "baseline_comparison_summary.json",
        "statistical_tests.json",
    ]
    for art in root_artifacts:
        art_path = base_dir / art
        if not art_path.exists():
            record_error(f"Missing root comparison artifact: {art_path}")
        else:
            record_file(art_path)

    # Validate pooled_comparison.csv
    pooled_csv_path = base_dir / "pooled_comparison.csv"
    if pooled_csv_path.exists():
        try:
            df_pooled = pd.read_csv(pooled_csv_path)
            expected_cols = {
                "model", "mae_bpm", "rmse_bpm", "bias_bpm", "medae_bpm",
                "within_3bpm_pct", "within_5bpm_pct", "within_10bpm_pct"
            }
            if not expected_cols.issubset(set(df_pooled.columns)):
                record_error(f"pooled_comparison.csv missing expected columns: {expected_cols - set(df_pooled.columns)}")
            if len(df_pooled) != len(expected_models):
                record_error(f"pooled_comparison.csv row count {len(df_pooled)} != expected {len(expected_models)}")
        except Exception as e:
            record_error(f"Failed to read pooled_comparison.csv: {e}")

    # Validate per_subject_comparison.csv
    subj_csv_path = base_dir / "per_subject_comparison.csv"
    if subj_csv_path.exists():
        try:
            df_subj = pd.read_csv(subj_csv_path)
            expected_subj_rows = len(expected_models) * expected_subjects
            if len(df_subj) != expected_subj_rows:
                record_error(f"per_subject_comparison.csv row count {len(df_subj)} != expected {expected_subj_rows}")
        except Exception as e:
            record_error(f"Failed to read per_subject_comparison.csv: {e}")

    # 2. Per-model artifacts
    for m in expected_models:
        model_dir = base_dir / f"synthetic_{m}"
        if not model_dir.exists():
            record_error(f"Missing model directory: {model_dir}")
            continue

        model_report = {"model": m, "folds_verified": 0, "status": "PASS"}

        # training_config.json
        cfg_p = model_dir / "training_config.json"
        if not cfg_p.exists():
            record_error(f"Missing training_config.json for {m}")
        else:
            record_file(cfg_p)
            try:
                cfg_data = json.loads(cfg_p.read_text(encoding="utf-8"))
                for req_key in ["run_id", "mode", "seed", "epochs", "batch_size", "model_type"]:
                    if req_key not in cfg_data:
                        record_error(f"{m} training_config.json missing required key: {req_key}")
                if cfg_data.get("mode") != "synthetic":
                    record_error(f"{m} training_config.json mode is not 'synthetic': {cfg_data.get('mode')}")
            except Exception as e:
                record_error(f"Failed parsing {cfg_p}: {e}")

        # run_metadata.json
        meta_p = model_dir / "run_metadata.json"
        if not meta_p.exists():
            record_error(f"Missing run_metadata.json for {m}")
        else:
            record_file(meta_p)
            try:
                meta_data = json.loads(meta_p.read_text(encoding="utf-8"))
                for req_key in ["run_id", "benchmark_type", "execution_timestamp_utc", "python_version", "random_seeds"]:
                    if req_key not in meta_data:
                        record_error(f"{m} run_metadata.json missing required key: {req_key}")
            except Exception as e:
                record_error(f"Failed parsing {meta_p}: {e}")

        # fold_split_manifest.csv (1 row per fold = expected_subjects rows)
        manifest_p = model_dir / "fold_split_manifest.csv"
        if not manifest_p.exists():
            record_error(f"Missing fold_split_manifest.csv for {m}")
        else:
            record_file(manifest_p)
            try:
                man_df = pd.read_csv(manifest_p)
                if len(man_df) != expected_subjects:
                    record_error(f"{m} fold split manifest row count {len(man_df)} != expected {expected_subjects}")
                if "subject_leakage_detected" in man_df.columns:
                    if man_df["subject_leakage_detected"].any():
                        record_error(f"{m} fold split manifest detected subject leakage!")
            except Exception as e:
                record_error(f"Failed parsing {manifest_p}: {e}")

        # predictions_all_folds.csv
        preds_all_p = model_dir / "predictions_all_folds.csv"
        if not preds_all_p.exists():
            record_error(f"Missing predictions_all_folds.csv for {m}")
        else:
            record_file(preds_all_p)
            try:
                p_df = pd.read_csv(preds_all_p)
                if len(p_df) != total_expected_windows:
                    record_error(f"{m} predictions count {len(p_df)} != {total_expected_windows}")
                if p_df.isna().sum().sum() > 0:
                    record_error(f"{m} predictions contain NaN values")
                if p_df.duplicated(subset=["subject_id", "window_index", "condition"]).sum() > 0:
                    record_error(f"{m} predictions contain duplicate window entries")
            except Exception as e:
                record_error(f"Failed parsing {preds_all_p}: {e}")

        # Folds 1..8
        folds_dir = model_dir / "folds"
        if not folds_dir.exists():
            record_error(f"Missing folds directory for {m}: {folds_dir}")
        else:
            for f_idx in range(1, expected_subjects + 1):
                f_name = f"fold_{f_idx:02d}"
                f_path = folds_dir / f_name
                if not f_path.exists():
                    record_error(f"Missing fold directory: {f_path}")
                    continue

                # predictions_test.csv
                f_pred = f_path / "predictions_test.csv"
                if not f_pred.exists():
                    record_error(f"Missing predictions_test.csv in {f_name} for {m}")
                else:
                    record_file(f_pred)
                    try:
                        f_df = pd.read_csv(f_pred)
                        if len(f_df) != expected_windows_per_subject:
                            record_error(f"{m} {f_name} test predictions count {len(f_df)} != {expected_windows_per_subject}")
                    except Exception as e:
                        record_error(f"Failed parsing {f_pred}: {e}")

                # feature_scaler.json
                f_scaler = f_path / "feature_scaler.json"
                if not f_scaler.exists():
                    record_error(f"Missing feature_scaler.json in {f_name} for {m}")
                else:
                    record_file(f_scaler)
                    try:
                        sc_data = json.loads(f_scaler.read_text(encoding="utf-8"))
                        if not sc_data.get("is_fitted", False):
                            record_error(f"{m} {f_name} feature_scaler is not marked as fitted")
                    except Exception as e:
                        record_error(f"Failed parsing {f_scaler}: {e}")

                # target_normalizer.json
                f_norm = f_path / "target_normalizer.json"
                if not f_norm.exists():
                    record_error(f"Missing target_normalizer.json in {f_name} for {m}")
                else:
                    record_file(f_norm)
                    try:
                        norm_data = json.loads(f_norm.read_text(encoding="utf-8"))
                        if not norm_data.get("is_fitted", False):
                            record_error(f"{m} {f_name} target_normalizer is not marked as fitted")
                    except Exception as e:
                        record_error(f"Failed parsing {f_norm}: {e}")

                # best_model.weights.h5 (for parametric models)
                if m in ("kan", "mlp", "cnn"):
                    f_weights = f_path / "best_model.weights.h5"
                    if not f_weights.exists():
                        record_error(f"Missing weights checkpoint in {f_name} for {m}: {f_weights}")
                    else:
                        record_file(f_weights)

                model_report["folds_verified"] += 1

        report["models_validated"].append(model_report)

    return report


def main() -> int:
    """CLI entrypoint for artifact validation."""
    parser = argparse.ArgumentParser(description="Validate Phase 6B synthetic benchmark artifacts on disk.")
    parser.add_argument(
        "--run-dir",
        type=str,
        default="outputs/phase6b",
        help="Path to phase 6b benchmark directory (default: outputs/phase6b)",
    )
    args = parser.parse_args()

    run_path = Path(args.run_dir)
    print(f"=== Validating Phase 6B Artifacts in: {run_path.resolve()} ===")

    if not run_path.exists():
        print(f"ERROR: Run directory does not exist: {run_path}")
        return 1

    report = validate_synthetic_run_artifacts(run_path)
    print(f"Files checked: {len(report['files_checked'])}")
    print(f"Models checked: {len(report['models_validated'])}")

    for m_rep in report["models_validated"]:
        print(f"  Model {m_rep['model'].upper()}: {m_rep['folds_verified']} folds verified")

    if report["status"] == "PASS":
        print("\n>>> ARTIFACT VALIDATION RESULT: PASS (All expected files and schemas verified) <<<")
        return 0
    else:
        print("\n>>> ARTIFACT VALIDATION RESULT: FAIL <<<")
        print(f"Encountered {len(report['errors'])} error(s):")
        for err in report["errors"]:
            print(f"  - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
