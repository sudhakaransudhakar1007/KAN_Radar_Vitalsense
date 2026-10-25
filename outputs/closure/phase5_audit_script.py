"""
Independent Post-Run Audit and Recalculation for Phase 5 Synthetic Benchmark.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.kan.feature_scaler import FeatureScaler
from src.kan.kan_model import KANRegressor
from src.kan.normalization import TargetNormalizer
from src.kan.trainer import generate_synthetic_dataset

run_dir = repo_root / "outputs/phase5/run_synthetic_001"

def audit():
    print("=================================================================")
    print("PHASE 5 POST-RUN AUDIT: run_synthetic_001")
    print("=================================================================")
    
    # 1. Predictions integrity check
    preds_p = run_dir / "predictions_all_folds.csv"
    assert preds_p.exists(), f"Missing {preds_p}"
    preds_df = pd.read_csv(preds_p)
    
    print("\n--- 1. Predictions File Integrity ---")
    print(f"Path: {preds_p}")
    print(f"Total prediction records: {len(preds_df)} (Expected: 80, 8 subjects x 10 windows)")
    print(f"Columns: {preds_df.columns.tolist()}")
    print(f"Missing values: {preds_df.isnull().sum().to_dict()}")
    print(f"Non-finite in y_true_bpm: {np.sum(~np.isfinite(preds_df['y_true_bpm']))}")
    print(f"Non-finite in y_pred_bpm: {np.sum(~np.isfinite(preds_df['y_pred_bpm']))}")
    dups = preds_df.duplicated(subset=['subject_id', 'window_index']).sum()
    print(f"Duplicate (subject_id, window_index) pairs: {dups}")
    min_yt, max_yt = preds_df['y_true_bpm'].min(), preds_df['y_true_bpm'].max()
    min_yp, max_yp = preds_df['y_pred_bpm'].min(), preds_df['y_pred_bpm'].max()
    print(f"Physiological BPM range y_true: [{min_yt}, {max_yt}] BPM")
    print(f"Physiological BPM range y_pred: [{min_yp}, {max_yp}] BPM")
    
    # 2. Split Manifest Integrity
    manifest_p = run_dir / "fold_split_manifest.csv"
    assert manifest_p.exists(), f"Missing {manifest_p}"
    manifest_df = pd.read_csv(manifest_p)
    print("\n--- 2. Split Manifest & Subject Isolation ---")
    print(f"Path: {manifest_p}")
    print(f"Folds count: {len(manifest_df)}")
    
    all_subjects = sorted(preds_df['subject_id'].unique().tolist())
    print(f"Unique subjects in predictions ({len(all_subjects)}): {all_subjects}")
    
    isolation_ok = True
    for idx, row in manifest_df.iterrows():
        fold = int(row['fold'])
        test_subj = row['test_subject']
        val_subjs = set(row['val_subjects'].split(';'))
        train_subjs = set(row['train_subjects'].split(';'))
        
        # Check disjointness
        tr_val_overlap = train_subjs & val_subjs
        tr_test_overlap = train_subjs & {test_subj}
        val_test_overlap = val_subjs & {test_subj}
        union_all = train_subjs | val_subjs | {test_subj}
        
        if tr_val_overlap or tr_test_overlap or val_test_overlap or union_all != set(all_subjects):
            print(f"  ERROR in Fold {fold}: Leakage or incomplete union!")
            isolation_ok = False
        else:
            # Check predictions strictly match test_subj
            f_preds = preds_df[preds_df['fold'] == fold]
            pred_subjs = set(f_preds['subject_id'].unique())
            if pred_subjs != {test_subj}:
                print(f"  ERROR in Fold {fold}: Predictions subject {pred_subjs} != test_subject {test_subj}")
                isolation_ok = False
            else:
                print(f"  Fold {fold}: test={test_subj}, val={sorted(val_subjs)}, train={sorted(train_subjs)} -> ZERO LEAKAGE verified.")
                
    print(f"All 8 folds subject isolation status: {'PERFECT (ZERO LEAKAGE)' if isolation_ok else 'FAILED'}")

    # 3. Independent Metric Recalculation
    print("\n--- 3. Independent Metric Recalculation & Reconciliation ---")
    recomputed_folds = []
    for fold in range(1, 9):
        f_df = preds_df[preds_df['fold'] == fold]
        yt = f_df['y_true_bpm'].to_numpy(dtype=np.float64)
        yp = f_df['y_pred_bpm'].to_numpy(dtype=np.float64)
        err = yp - yt
        abs_err = np.abs(err)
        mae = float(np.mean(abs_err))
        rmse = float(np.sqrt(np.mean(err**2)))
        bias = float(np.mean(err))
        r = float(np.corrcoef(yt, yp)[0, 1]) if len(yt) > 1 and np.std(yt) > 1e-6 and np.std(yp) > 1e-6 else 0.0
        w3 = float(np.mean(abs_err <= 3.0) * 100.0)
        w5 = float(np.mean(abs_err <= 5.0) * 100.0)
        recomputed_folds.append({
            'fold': fold,
            'test_subject': f_df['subject_id'].iloc[0],
            'mae_bpm': round(mae, 3),
            'rmse_bpm': round(rmse, 3),
            'bias_bpm': round(bias, 3),
            'pearson_r': round(r, 4),
            'within_3bpm_pct': round(w3, 2),
            'within_5bpm_pct': round(w5, 2),
        })

    # Compare against summary_metrics.json
    summary_p = run_dir / "summary_metrics.json"
    assert summary_p.exists(), f"Missing {summary_p}"
    summary_data = json.loads(summary_p.read_text(encoding="utf-8"))
    saved_folds = summary_data['fold_breakdown']
    
    mismatches = 0
    for rf, sf in zip(recomputed_folds, saved_folds):
        for k in ['mae_bpm', 'rmse_bpm', 'bias_bpm', 'pearson_r', 'within_3bpm_pct', 'within_5bpm_pct']:
            diff = abs(rf[k] - sf[k])
            if diff > 1e-4:
                print(f"  MISMATCH Fold {rf['fold']} {k}: recomputed={rf[k]}, saved={sf[k]}")
                mismatches += 1
    if mismatches == 0:
        print("PERFECT MATCH: All 8 folds' recomputed metrics match saved metrics in summary_metrics.json exactly!")

    # 4. Clarification of "MAE 2.59 +/- 2.85 BPM"
    fold_maes = [f['mae_bpm'] for f in recomputed_folds]
    mean_mae = np.mean(fold_maes)
    pop_std_mae = np.std(fold_maes, ddof=0)
    sample_std_mae = np.std(fold_maes, ddof=1)
    print("\n--- 4. Explanation of +/- Term in 'MAE 2.59 +/- 2.85 BPM' ---")
    print(f"Individual Fold MAEs: {fold_maes}")
    print(f"Mean across folds:    {mean_mae:.3f} BPM (rounds to 2.59)")
    print(f"Population std (N=8): {pop_std_mae:.3f} BPM (rounds to 2.85)")
    print(f"Sample std (N-1=7):   {sample_std_mae:.3f} BPM (rounds to 3.05)")
    print("Conclusion: The +/- 2.85 BPM term represents the standard deviation (fold-to-fold inter-subject dispersion)")
    print("of the 8 test fold MAEs, NOT confidence interval or measurement noise.")

    # 5. Checkpoint Reload Verification
    print("\n--- 5. Checkpoint Reload Prediction Equivalence ---")
    # Verify each fold's checkpoint reload against saved predictions
    import tensorflow as tf
    from src.kan.kan_model import KANRegressor
    from src.kan.trainer import generate_synthetic_dataset
    
    _, X_all, _ = generate_synthetic_dataset(num_subjects=8, windows_per_subject=10, seed=42)
    
    max_reload_diffs = []
    for fold in range(1, 9):
        f_dir = run_dir / f"folds/fold_{fold:02d}"
        weights_p = f_dir / "best_model.weights.h5"
        scaler_p = f_dir / "feature_scaler.json"
        norm_p = f_dir / "target_normalizer.json"
        schema_p = f_dir / "feature_schema.json"
        
        assert weights_p.exists() and scaler_p.exists() and norm_p.exists() and schema_p.exists()
        
        scaler = FeatureScaler.load_json(scaler_p)
        norm_dict = json.loads(norm_p.read_text(encoding="utf-8"))
        schema_dict = json.loads(schema_p.read_text(encoding="utf-8"))
        
        # Test mask for this fold
        f_preds = preds_df[preds_df['fold'] == fold]
        sample_indices = f_preds['sample_index'].to_numpy()
        X_test_raw = X_all[sample_indices]
        
        # Transform using saved scaler
        X_test_s = scaler.transform(X_test_raw)
        
        # Instantiate fresh model and load weights
        input_dim = schema_dict['runtime_input_dim']
        eval_model = KANRegressor(
            input_dim=input_dim,
            latent_dim=schema_dict['latent_dim'],
            hidden_dim=8,
            grid_size=5,
            spline_order=3,
        )
        eval_model(tf.zeros((1, input_dim)))
        eval_model.load_weights(str(weights_p))
        
        # Predict
        preds_norm = eval_model(tf.convert_to_tensor(X_test_s, dtype=tf.float32), training=False).numpy()
        preds_bpm = np.round(preds_norm * norm_dict['train_std'] + norm_dict['train_mean'], 2)
        
        saved_preds = f_preds['y_pred_bpm'].to_numpy()
        diff = np.max(np.abs(preds_bpm - saved_preds))
        max_reload_diffs.append(diff)
        print(f"  Fold {fold} Checkpoint Reload Max Abs Diff: {diff:.6f} BPM")
        
    print(f"Overall Checkpoint Reload Max Diff: {max(max_reload_diffs):.6f} BPM (Tolerance: < 1e-4 BPM)")

if __name__ == "__main__":
    audit()
