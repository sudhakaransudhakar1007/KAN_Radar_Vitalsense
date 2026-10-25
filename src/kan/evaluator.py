"""Phase 6 Evaluation Framework for Heart-Rate Estimation Models.

Computes:
1. Standard biomedical metrics: MAE, RMSE, Bias, Pearson r, Spearman rho, MedAE.
2. Clinical tolerance limits: Within +/- 3 BPM %, +/- 5 BPM %, +/- 10 BPM %.
3. Bland-Altman agreement analysis (Mean difference, LoA: bias +/- 1.96 * SD).
4. Statistical significance tests between comparative models (paired t-test, Wilcoxon).
5. Structured report generation with SYNTHETIC_BENCHMARK provenance.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class DetailedMetrics:
    """Comprehensive biomedical heart-rate evaluation metrics."""
    sample_count: int
    mae_bpm: float
    rmse_bpm: float
    bias_bpm: float
    medae_bpm: float
    std_error_bpm: float
    max_error_bpm: float
    pearson_r: float
    pearson_pvalue: float
    spearman_rho: float
    spearman_pvalue: float
    within_3bpm_pct: float
    within_5bpm_pct: float
    within_10bpm_pct: float
    bland_altman_lower_loa: float
    bland_altman_upper_loa: float


class ModelEvaluator:
    """Evaluates heart-rate predictions and performs multi-model comparisons."""

    @staticmethod
    def compute_detailed_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> DetailedMetrics:
        """Computes comprehensive evaluation metrics on physical BPM heart rates."""
        yt = np.asarray(y_true, dtype=np.float64).flatten()
        yp = np.asarray(y_pred, dtype=np.float64).flatten()

        if len(yt) != len(yp):
            raise ValueError(f"Length mismatch: len(y_true)={len(yt)} vs len(y_pred)={len(yp)}")
        if len(yt) == 0:
            raise ValueError("Cannot compute metrics on empty arrays.")
        if np.any(~np.isfinite(yt)) or np.any(~np.isfinite(yp)):
            raise ValueError("Arrays contain non-finite values (NaN or Inf).")

        n = len(yt)
        errors = yp - yt
        abs_errors = np.abs(errors)

        mae = float(np.mean(abs_errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        bias = float(np.mean(errors))
        medae = float(np.median(abs_errors))
        std_err = float(np.std(errors, ddof=1)) if n > 1 else 0.0
        max_err = float(np.max(abs_errors))

        # Correlation
        if n > 2 and np.std(yt) > 1e-6 and np.std(yp) > 1e-6:
            r, p_val = stats.pearsonr(yt, yp)
            rho, s_val = stats.spearmanr(yt, yp)
            r = 0.0 if np.isnan(r) else float(r)
            p_val = 1.0 if np.isnan(p_val) else float(p_val)
            rho = 0.0 if np.isnan(rho) else float(rho)
            s_val = 1.0 if np.isnan(s_val) else float(s_val)
        else:
            r, p_val, rho, s_val = 0.0, 1.0, 0.0, 1.0

        w3 = float(np.mean(abs_errors <= 3.0) * 100.0)
        w5 = float(np.mean(abs_errors <= 5.0) * 100.0)
        w10 = float(np.mean(abs_errors <= 10.0) * 100.0)

        # Bland-Altman Limits of Agreement (95% CI)
        lower_loa = bias - 1.96 * std_err
        upper_loa = bias + 1.96 * std_err

        return DetailedMetrics(
            sample_count=n,
            mae_bpm=round(mae, 3),
            rmse_bpm=round(rmse, 3),
            bias_bpm=round(bias, 3),
            medae_bpm=round(medae, 3),
            std_error_bpm=round(std_err, 3),
            max_error_bpm=round(max_err, 3),
            pearson_r=round(r, 4),
            pearson_pvalue=round(p_val, 6),
            spearman_rho=round(rho, 4),
            spearman_pvalue=round(s_val, 6),
            within_3bpm_pct=round(w3, 2),
            within_5bpm_pct=round(w5, 2),
            within_10bpm_pct=round(w10, 2),
            bland_altman_lower_loa=round(lower_loa, 3),
            bland_altman_upper_loa=round(upper_loa, 3),
        )

    @classmethod
    def evaluate_predictions_file(
        cls,
        predictions_csv_path: Union[str, Path],
    ) -> Dict[str, Any]:
        """Evaluates an existing predictions CSV containing true and predicted BPMs."""
        p = Path(predictions_csv_path)
        if not p.exists():
            raise FileNotFoundError(f"Predictions file not found: {p}")

        df = pd.read_csv(p)
        required_cols = {"subject_id", "y_true_bpm", "y_pred_bpm"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Predictions CSV missing columns: {missing}")

        # Overall pooled metrics
        pooled_metrics = cls.compute_detailed_metrics(
            df["y_true_bpm"].to_numpy(),
            df["y_pred_bpm"].to_numpy(),
        )

        # Per-subject breakdown
        subject_breakdown = {}
        subjects = sorted(df["subject_id"].unique().tolist())
        for s in subjects:
            sub_df = df[df["subject_id"] == s]
            s_metrics = cls.compute_detailed_metrics(
                sub_df["y_true_bpm"].to_numpy(),
                sub_df["y_pred_bpm"].to_numpy(),
            )
            subject_breakdown[s] = asdict(s_metrics)

        # Macro-averaged summary across subjects
        subj_maes = [m["mae_bpm"] for m in subject_breakdown.values()]
        macro_mae = float(np.mean(subj_maes))
        macro_std_mae = float(np.std(subj_maes, ddof=1)) if len(subj_maes) > 1 else 0.0

        return {
            "predictions_source": str(p),
            "benchmark_status": "SYNTHETIC_BENCHMARK" if "SYNTHETIC" in p.name.upper() or "synthetic" in str(p) else "UNVERIFIED",
            "total_windows": len(df),
            "total_subjects": len(subjects),
            "macro_averaged": {
                "mean_mae_bpm": round(macro_mae, 3),
                "std_mae_bpm": round(macro_std_mae, 3),
            },
            "pooled_metrics": asdict(pooled_metrics),
            "subject_breakdown": subject_breakdown,
        }

    @staticmethod
    def compare_models(
        preds_model_a: np.ndarray,
        preds_model_b: np.ndarray,
        y_true: np.ndarray,
        model_a_name: str = "Model_A",
        model_b_name: str = "Model_B",
    ) -> Dict[str, Any]:
        """Performs paired statistical significance tests between two model predictions."""
        err_a = np.abs(np.asarray(preds_model_a) - np.asarray(y_true))
        err_b = np.abs(np.asarray(preds_model_b) - np.asarray(y_true))

        # Paired comparisons
        if len(err_a) < 2 or np.allclose(err_a, err_b):
            t_stat, t_pval = 0.0, 1.0
            w_stat, w_pval = 0.0, 1.0
        else:
            t_res = stats.ttest_rel(err_a, err_b)
            t_stat = 0.0 if np.isnan(t_res.statistic) else float(t_res.statistic)
            t_pval = 1.0 if np.isnan(t_res.pvalue) else float(t_res.pvalue)
            try:
                w_res = stats.wilcoxon(err_a, err_b)
                w_stat = 0.0 if np.isnan(w_res.statistic) else float(w_res.statistic)
                w_pval = 1.0 if np.isnan(w_res.pvalue) else float(w_res.pvalue)
            except Exception:
                w_stat, w_pval = 0.0, 1.0

        return {
            "comparison": f"{model_a_name} vs {model_b_name}",
            "sample_count": len(err_a),
            "mae_model_a": round(float(np.mean(err_a)), 3),
            "mae_model_b": round(float(np.mean(err_b)), 3),
            "mae_difference": round(float(np.mean(err_a) - np.mean(err_b)), 3),
            "paired_ttest": {
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(t_pval), 6),
                "significant_at_05": bool(t_pval < 0.05),
            },
            "wilcoxon_test": {
                "statistic": round(float(w_stat), 4),
                "p_value": round(float(w_pval), 6),
                "significant_at_05": bool(w_pval < 0.05),
            },
        }
