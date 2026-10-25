"""
Subject-level detailed investigation for SYNTH_S02 and SYNTH_S08.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

repo_root = Path(__file__).resolve().parents[2]
run_dir = repo_root / "outputs/phase5/run_synthetic_001"

def main():
    preds_df = pd.read_csv(run_dir / "predictions_all_folds.csv")
    manifest_df = pd.read_csv(run_dir / "fold_split_manifest.csv")
    
    print("=================================================================")
    print("TASK 3: SUBJECT-LEVEL INVESTIGATION (SYNTH_S02 & SYNTH_S08)")
    print("=================================================================")
    
    for subj in sorted(preds_df["subject_id"].unique()):
        s_df = preds_df[preds_df["subject_id"] == subj]
        yt = s_df["y_true_bpm"].to_numpy()
        yp = s_df["y_pred_bpm"].to_numpy()
        err = yp - yt
        abs_err = np.abs(err)
        fold = s_df["fold"].iloc[0]
        
        # Load fold normalizer
        norm_p = run_dir / f"folds/fold_{fold:02d}/target_normalizer.json"
        norm_data = json.loads(norm_p.read_text(encoding="utf-8"))
        train_mean = norm_data["train_mean"]
        train_std = norm_data["train_std"]
        
        print(f"\nSubject: {subj} (Fold {fold})")
        print(f"  True HR:       Mean={yt.mean():.2f} BPM, Range=[{yt.min():.2f}, {yt.max():.2f}], Std={yt.std():.2f} BPM")
        print(f"  Predicted HR:  Mean={yp.mean():.2f} BPM, Range=[{yp.min():.2f}, {yp.max():.2f}], Std={yp.std():.2f} BPM")
        print(f"  Signed Errors: Mean(Bias)={err.mean():.3f} BPM, Min={err.min():.2f}, Max={err.max():.2f}")
        print(f"  MAE:           {abs_err.mean():.3f} BPM")
        print(f"  Training Fold: Mean={train_mean:.2f} BPM, Std={train_std:.2f} BPM")
        print(f"  Target Offset: Subject Mean - Train Mean = {yt.mean() - train_mean:+.2f} BPM")
        
    print("\n--- Summary of Outlier Subjects ---")
    print("SYNTH_S02:")
    s2 = preds_df[preds_df["subject_id"] == "SYNTH_S02"]
    print(f"  All signed errors are NEGATIVE: min={s2['error_bpm'].min()}, max={s2['error_bpm'].max()}")
    print(f"  Mean bias: {s2['error_bpm'].mean():.3f} BPM")
    print(f"  True mean: {s2['y_true_bpm'].mean():.2f} BPM vs Train mean: 70.36 BPM (Offset: +18.42 BPM)")
    
    print("\nSYNTH_S08:")
    s8 = preds_df[preds_df["subject_id"] == "SYNTH_S08"]
    print(f"  All signed errors are POSITIVE: min={s8['error_bpm'].min()}, max={s8['error_bpm'].max()}")
    print(f"  Mean bias: {s8['error_bpm'].mean():.3f} BPM")
    print(f"  True mean: {s8['y_true_bpm'].mean():.2f} BPM vs Train mean: 75.34 BPM (Offset: -18.73 BPM)")

if __name__ == "__main__":
    main()
