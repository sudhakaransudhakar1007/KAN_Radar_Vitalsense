"""
R2 Analysis Script: Percentage Verification for |dHR| > 1.0 bpm.
Author: Antigravity Assistant (Stage 6C)
"""
import sys
from pathlib import Path
import pandas as pd

repo_root = Path(__file__).resolve().parents[2]

def main():
    s1_csv = repo_root / "outputs/closure/s1_window_hr_comparison.csv"
    assert s1_csv.exists(), f"Missing {s1_csv}"
    
    df = pd.read_csv(s1_csv)
    total_rows = len(df)
    
    print(f"Columns in {s1_csv.name}: {list(df.columns)}")
    print(f"Total rows in {s1_csv.name}: {total_rows}")
    
    # Check valid rows
    valid_df = df.dropna(subset=['p3_hr_harmonic', 'sync_hr'])
    n_valid = len(valid_df)
    print(f"Valid paired rows: {n_valid}")
    
    diffs = (valid_df['p3_hr_harmonic'] - valid_df['sync_hr']).abs()
    gt_1 = (diffs > 1.0).sum()
    print(f"Count with |dHR| > 1.0 bpm: {gt_1}")
    
    pct_valid = (gt_1 / n_valid) * 100.0
    pct_1056 = (gt_1 / 1056.0) * 100.0
    pct_1104 = (gt_1 / 1104.0) * 100.0
    
    print(f"48 / 1,051 (valid pairs in S1) = {pct_valid:.5f}% -> rounded: {pct_valid:.2f}%")
    print(f"48 / 1,056 (run_001 total candidate windows) = {pct_1056:.5f}% -> rounded: {pct_1056:.2f}%")
    print(f"48 / 1,104 (continuous-time candidate windows 48*23) = {pct_1104:.5f}% -> rounded: {pct_1104:.2f}%")
    
    # Find script that computed this
    scripts = ["run_s1_s2.py", "run_b5_analysis.py"]
    for s in scripts:
        sp = repo_root / "outputs/closure" / s
        if sp.exists():
            lines = sp.read_text(encoding='utf-8').splitlines()
            for i, l in enumerate(lines):
                if any(k in l for k in ["> 1.0", "gt_1", "1051", "4.57", "s1_window_hr_comparison"]):
                    print(f"Hit in {s}:{i+1}: {l.strip()}")

if __name__ == "__main__":
    main()
