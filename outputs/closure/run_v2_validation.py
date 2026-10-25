"""Run sync validation into outputs/closure/v2/ and compare with outputs/phase2a/."""

import hashlib
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.sync_validation.runner import run_sync_validation


def main():
    phase2a_csv = Path("outputs/phase2a/sync_validation_results.csv")
    h_before = hashlib.sha256(phase2a_csv.read_bytes()).hexdigest()
    print("outputs/phase2a/sync_validation_results.csv SHA-256 BEFORE:", h_before)

    out_dir = Path("outputs/closure/v2")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Executing run_sync_validation with output_dir={out_dir}...")
    df_v2, summary_stats = run_sync_validation(output_dir=out_dir)

    v2_csv = out_dir / "sync_validation_results.csv"
    print(f"Generated {v2_csv} with {len(df_v2)} rows.")

    h_after = hashlib.sha256(phase2a_csv.read_bytes()).hexdigest()
    print("outputs/phase2a/sync_validation_results.csv SHA-256 AFTER:", h_after)
    assert h_before == h_after, "CRITICAL ERROR: outputs/phase2a/sync_validation_results.csv was modified!"
    print("VERIFIED: outputs/phase2a/sync_validation_results.csv was NOT touched.")

    # Detailed column-by-column comparison
    df_p2a = pd.read_csv(phase2a_csv)
    print("\n=== COLUMN-BY-COLUMN COMPARISON ===")
    identical_cols = []
    differing_cols = []

    for col in df_p2a.columns:
        if col not in df_v2.columns:
            differing_cols.append(col)
            print(f"Column '{col}' MISSING in v2!")
            continue

        s_p2a = df_p2a[col]
        s_v2 = df_v2[col]

        # Check equality with floating point tolerance where applicable
        if pd.api.types.is_float_dtype(s_p2a) and pd.api.types.is_float_dtype(s_v2):
            matches = (s_p2a == s_v2) | (s_p2a.isna() & s_v2.isna()) | (abs(s_p2a - s_v2) < 1e-6)
        else:
            matches = (s_p2a == s_v2) | (s_p2a.isna() & s_v2.isna())

        if matches.all():
            identical_cols.append(col)
        else:
            diff_count = (~matches).sum()
            differing_cols.append((col, diff_count))

    print(f"Identical columns ({len(identical_cols)}):", ", ".join(identical_cols))
    print(f"Differing columns ({len(differing_cols)}):", differing_cols)

    # Print exact differences for differing columns
    for item in differing_cols:
        col, count = item if isinstance(item, tuple) else (item, 0)
        print(f"\n--- Differences in column: {col} ({count} rows differing) ---")
        diff_mask = df_p2a[col] != df_v2[col]
        for idx in df_p2a[diff_mask].index:
            sub = df_p2a.loc[idx, "subject_id"]
            cond = df_p2a.loc[idx, "condition"]
            val_old = df_p2a.loc[idx, col]
            val_new = df_v2.loc[idx, col]
            print(f"Row {idx:2d} ({sub}_{cond}):\n  OLD: {val_old}\n  NEW: {val_new}")


if __name__ == "__main__":
    main()
