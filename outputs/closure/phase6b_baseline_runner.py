"""
Phase 6B: Fair synthetic baseline comparison orchestrator.
Trains and evaluates KAN, MLP, CNN, and MeanPredictorBaseline on identical synthetic LOSO folds.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.kan.evaluator import ModelEvaluator
from src.kan.trainer import KANTrainer, TrainingConfig, generate_synthetic_dataset


def run_fair_comparison():
    print("=================================================================")
    print("PHASE 6B: FAIR SYNTHETIC BASELINE COMPARISON")
    print("=================================================================")

    base_out = repo_root / "outputs" / "phase6b"
    base_out.mkdir(parents=True, exist_ok=True)

    # 1. Generate identical synthetic dataset once
    seed = 42
    num_subjects = 8
    windows_per_subject = 10
    print(f"Generating synthetic dataset: {num_subjects} subjects, {windows_per_subject} windows/subj, seed={seed}...")
    manifest_df, X_all, y_all = generate_synthetic_dataset(
        num_subjects=num_subjects,
        windows_per_subject=windows_per_subject,
        seed=seed,
    )

    models_to_run = ["kan", "mlp", "cnn", "mean"]
    model_predictions = {}
    model_configs = {}

    for m_type in models_to_run:
        print(f"\n>>> Running Model: {m_type.upper()} <<<")
        run_id = f"synthetic_{m_type}"
        out_dir = base_out / run_id

        cfg = TrainingConfig(
            run_id=run_id,
            mode="synthetic",
            model_type=m_type,
            seed=seed,
            epochs=15,
            batch_size=16,
            learning_rate=0.005,
            output_dir=f"outputs/phase6b/{run_id}",
        )
        model_configs[m_type] = cfg

        trainer = KANTrainer(config=cfg, base_dir=repo_root)
        results = trainer.execute_training(
            custom_manifest=manifest_df,
            custom_X=X_all,
            custom_y=y_all,
        )

        preds_p = out_dir / "predictions_all_folds.csv"
        assert preds_p.exists(), f"Predictions file not generated for {m_type}: {preds_p}"
        preds_df = pd.read_csv(preds_p)
        model_predictions[m_type] = preds_df
        print(f"Model {m_type.upper()} completed: Macro MAE = {results['mean_mae_bpm']:.3f} +/- {results['std_mae_bpm']:.3f} BPM")

    # 2. Comprehensive Per-Subject and Pooled Analysis
    print("\n--- Detailed Multi-Model Evaluation ---")
    subjects = sorted(manifest_df["subject_id"].unique().tolist())
    
    per_subject_rows = []
    pooled_rows = []
    
    y_true_all = model_predictions["kan"]["y_true_bpm"].to_numpy()

    for m_type in models_to_run:
        df_m = model_predictions[m_type]
        yp_all = df_m["y_pred_bpm"].to_numpy()
        
        # Pooled metrics
        pooled_m = ModelEvaluator.compute_detailed_metrics(y_true_all, yp_all)
        pooled_rows.append({
            "model": m_type.upper(),
            "mae_bpm": pooled_m.mae_bpm,
            "rmse_bpm": pooled_m.rmse_bpm,
            "bias_bpm": pooled_m.bias_bpm,
            "medae_bpm": pooled_m.medae_bpm,
            "max_error_bpm": pooled_m.max_error_bpm,
            "pearson_r": pooled_m.pearson_r,
            "spearman_rho": pooled_m.spearman_rho,
            "within_3bpm_pct": pooled_m.within_3bpm_pct,
            "within_5bpm_pct": pooled_m.within_5bpm_pct,
            "within_10bpm_pct": pooled_m.within_10bpm_pct,
            "bland_altman_lower_loa": pooled_m.bland_altman_lower_loa,
            "bland_altman_upper_loa": pooled_m.bland_altman_upper_loa,
        })
        
        # Per subject metrics
        for s in subjects:
            sub_m = df_m[df_m["subject_id"] == s]
            s_yt = sub_m["y_true_bpm"].to_numpy()
            s_yp = sub_m["y_pred_bpm"].to_numpy()
            sub_metric = ModelEvaluator.compute_detailed_metrics(s_yt, s_yp)
            per_subject_rows.append({
                "model": m_type.upper(),
                "subject_id": s,
                "mae_bpm": sub_metric.mae_bpm,
                "rmse_bpm": sub_metric.rmse_bpm,
                "bias_bpm": sub_metric.bias_bpm,
                "medae_bpm": sub_metric.medae_bpm,
                "max_error_bpm": sub_metric.max_error_bpm,
                "pearson_r": sub_metric.pearson_r,
                "within_3bpm_pct": sub_metric.within_3bpm_pct,
                "within_5bpm_pct": sub_metric.within_5bpm_pct,
                "within_10bpm_pct": sub_metric.within_10bpm_pct,
            })

    pooled_df = pd.DataFrame(pooled_rows)
    per_subj_df = pd.DataFrame(per_subject_rows)

    pooled_df.to_csv(base_out / "pooled_comparison.csv", index=False)
    per_subj_df.to_csv(base_out / "per_subject_comparison.csv", index=False)

    # 3. Statistical Significance Comparisons (Subject-level and Window-level)
    print("\n--- Statistical Significance Comparisons (KAN vs Baselines) ---")
    kan_preds = model_predictions["kan"]["y_pred_bpm"].to_numpy()
    
    # Subject-level MAE vectors (N=8)
    kan_sub_maes = np.array([
        per_subj_df[(per_subj_df["model"] == "KAN") & (per_subj_df["subject_id"] == s)]["mae_bpm"].iloc[0]
        for s in subjects
    ])

    stat_comparisons = {}

    for baseline in ["mlp", "cnn", "mean"]:
        base_name = baseline.upper()
        b_preds = model_predictions[baseline]["y_pred_bpm"].to_numpy()
        b_sub_maes = np.array([
            per_subj_df[(per_subj_df["model"] == base_name) & (per_subj_df["subject_id"] == s)]["mae_bpm"].iloc[0]
            for s in subjects
        ])

        # Window-level (N=80)
        win_comp = ModelEvaluator.compare_models(
            preds_model_a=kan_preds,
            preds_model_b=b_preds,
            y_true=y_true_all,
            model_a_name="KAN",
            model_b_name=base_name,
        )

        # Subject-level (N=8)
        diff_sub = kan_sub_maes - b_sub_maes
        if np.allclose(kan_sub_maes, b_sub_maes):
            t_stat_s, t_pval_s = 0.0, 1.0
            w_stat_s, w_pval_s = 0.0, 1.0
        else:
            t_res_s = stats.ttest_rel(kan_sub_maes, b_sub_maes)
            t_stat_s = 0.0 if np.isnan(t_res_s.statistic) else float(t_res_s.statistic)
            t_pval_s = 1.0 if np.isnan(t_res_s.pvalue) else float(t_res_s.pvalue)
            try:
                w_res_s = stats.wilcoxon(kan_sub_maes, b_sub_maes)
                w_stat_s = 0.0 if np.isnan(w_res_s.statistic) else float(w_res_s.statistic)
                w_pval_s = 1.0 if np.isnan(w_res_s.pvalue) else float(w_res_s.pvalue)
            except Exception:
                w_stat_s, w_pval_s = 0.0, 1.0

        stat_comparisons[f"KAN_vs_{base_name}"] = {
            "comparison": f"KAN vs {base_name}",
            "subject_level_n8": {
                "mean_mae_kan": round(float(np.mean(kan_sub_maes)), 3),
                "mean_mae_baseline": round(float(np.mean(b_sub_maes)), 3),
                "mae_difference": round(float(np.mean(kan_sub_maes) - np.mean(b_sub_maes)), 3),
                "paired_ttest": {
                    "t_statistic": round(t_stat_s, 4),
                    "p_value": round(t_pval_s, 6),
                    "significant_at_05": bool(t_pval_s < 0.05),
                },
                "wilcoxon_test": {
                    "statistic": round(w_stat_s, 4),
                    "p_value": round(w_pval_s, 6),
                    "significant_at_05": bool(w_pval_s < 0.05),
                },
            },
            "window_level_n80_pseudoreplicated": win_comp,
        }

    (base_out / "statistical_tests.json").write_text(json.dumps(stat_comparisons, indent=2), encoding="utf-8")

    summary_comparison = {
        "benchmark_label": "SYNTHETIC_BENCHMARK",
        "dataset_seed": seed,
        "subjects_count": num_subjects,
        "windows_per_subject": windows_per_subject,
        "models_evaluated": [m.upper() for m in models_to_run],
        "pooled_metrics": pooled_rows,
        "statistical_comparisons": stat_comparisons,
    }
    (base_out / "baseline_comparison_summary.json").write_text(json.dumps(summary_comparison, indent=2), encoding="utf-8")

    print("\n=================================================================")
    print("PHASE 6B FAIR COMPARISON COMPLETE")
    print(f"Artifacts saved in: {base_out}")
    print("=================================================================")
    print("\nPooled Metrics Summary:")
    print(pooled_df[["model", "mae_bpm", "rmse_bpm", "bias_bpm", "medae_bpm", "within_3bpm_pct", "within_5bpm_pct", "within_10bpm_pct"]].to_string(index=False))


if __name__ == "__main__":
    run_fair_comparison()
