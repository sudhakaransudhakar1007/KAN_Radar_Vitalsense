"""CLI entry point for reproducible KAN training and synthetic benchmarking."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure kan_radar_HR root is in sys.path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.kan.trainer import KANTrainer, TrainingConfig


def build_arg_parser() -> argparse.ArgumentParser:
    """Constructs command line argument parser for KAN training."""
    parser = argparse.ArgumentParser(
        description="Reproducible KAN regression training for radar heart-rate estimation."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to training configuration JSON file.",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Unique run identifier (e.g. run_synthetic_001).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Target directory for run outputs and checkpoints.",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        default=True,
        help="Run exclusively on isolated synthetic fixtures (default).",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        default=False,
        help="Attempt training on real data (requires closed Phase 2A/2C gate).",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override training epochs per fold.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override batch size.",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="Override learning rate.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override random seed for reproducibility.",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["kan", "mlp", "cnn", "mean"],
        default=None,
        help="Model architecture: 'kan', 'mlp', 'cnn', or 'mean'.",
    )
    parser.add_argument(
        "--max-folds",
        type=int,
        default=None,
        help="Maximum number of folds to train (default: all).",
    )
    return parser


def main(args: Optional[list] = None) -> int:
    """CLI execution entry point."""
    parser = build_arg_parser()
    parsed = parser.parse_args(args)

    # Load base config if provided
    if parsed.config:
        cfg_path = Path(parsed.config)
        if not cfg_path.exists():
            print(f"ERROR: Configuration file not found: {cfg_path}", file=sys.stderr)
            return 1
        config = TrainingConfig.load_json(cfg_path)
    else:
        config = TrainingConfig()

    # Apply command-line overrides
    if parsed.run_id:
        config.run_id = parsed.run_id
    if parsed.output_dir:
        config.output_dir = parsed.output_dir
    if parsed.real:
        config.mode = "real"
    elif parsed.synthetic:
        config.mode = "synthetic"
    if parsed.epochs is not None:
        config.epochs = parsed.epochs
    if parsed.batch_size is not None:
        config.batch_size = parsed.batch_size
    if parsed.learning_rate is not None:
        config.learning_rate = parsed.learning_rate
    if parsed.seed is not None:
        config.seed = parsed.seed
    if parsed.model_type is not None:
        config.model_type = parsed.model_type

    print("================================================================")
    print("PHASE 5: KAN REGRESSION TRAINING PIPELINE")
    print(f"Run ID:        {config.run_id}")
    print(f"Mode:          {config.mode.upper()}")
    print(f"Model:         {config.model_type.upper()}")
    print(f"Seed:          {config.seed}")
    print(f"Epochs:        {config.epochs} (Batch Size: {config.batch_size})")
    print(f"Output Dir:    {config.output_dir}")
    print("================================================================")

    trainer = KANTrainer(config=config, base_dir=repo_root)
    try:
        results = trainer.execute_training(max_folds=parsed.max_folds)
        print("\n--- Training Completed Successfully ---")
        print(f"Folds Evaluated:       {results['folds_evaluated']}")
        print(f"Mean Test MAE:         {results['mean_mae_bpm']:.2f} +/- {results['std_mae_bpm']:.2f} BPM")
        print(f"Mean Test RMSE:        {results['mean_rmse_bpm']:.2f} BPM")
        print(f"Mean Pearson r:        {results['mean_pearson_r']:.4f}")
        print(f"Within +/- 3 BPM:      {results['overall_within_3bpm_pct']:.1f}%")
        print(f"Within +/- 5 BPM:      {results['overall_within_5bpm_pct']:.1f}%")
        print(f"Artifacts Saved to:    {config.output_dir}")
        return 0
    except Exception as e:
        print(f"\nExecution Terminated: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
