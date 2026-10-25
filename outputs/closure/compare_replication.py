"""Compare replication results against published table and pipeline outputs."""

import pandas as pd
import numpy as np


def main():
    df_rep = pd.read_csv("outputs/closure/authors_method_lags.csv")
    df_pub = pd.read_csv("outputs/closure/authors_technical_validation_results.csv")
    df_p2a = pd.read_csv("outputs/phase2a/sync_validation_results.csv")
    df_v2 = pd.read_csv("outputs/closure/v2/sync_validation_results.csv")

    df_rep["subjectID"] = df_rep["recording_id"].apply(lambda x: x.split("_")[0])
    df_p2a["scenario"] = df_p2a["condition"]
    df_p2a["subjectID"] = df_p2a["subject_id"]
    df_v2["scenario"] = df_v2["condition"]
    df_v2["subjectID"] = df_v2["subject_id"]

    # Merge
    m = pd.merge(df_rep, df_pub, on=["subjectID", "scenario"], suffixes=("_rep", "_pub"))
    m = pd.merge(m, df_p2a[["subjectID", "scenario", "respiratory_lag_ms"]], on=["subjectID", "scenario"])
    m.rename(columns={"respiratory_lag_ms": "lag_ms_p2a"}, inplace=True)
    m = pd.merge(m, df_v2[["subjectID", "scenario", "respiratory_lag_ms"]], on=["subjectID", "scenario"])
    m.rename(columns={"respiratory_lag_ms": "lag_ms_v2"}, inplace=True)

    # 1. Compare Replication vs Published
    diff_pub = m["lag_ms"] - m["timeLag_ms"]
    abs_diff_pub = diff_pub.abs()
    count_close_pub = int((abs_diff_pub <= 0.5).sum())
    count_exact_pub = int((diff_pub == 0.0).sum())
    max_diff_pub = float(abs_diff_pub.max())

    print("=== 1. REPLICATION vs PUBLISHED ===")
    print(f"Total pairs compared: {len(m)}")
    print(f"Exact match (diff == 0.0 ms): {count_exact_pub} / {len(m)} ({count_exact_pub/len(m)*100:.1f}%)")
    print(f"Count with |diff| <= 0.5 ms:   {count_close_pub} / {len(m)} ({count_close_pub/len(m)*100:.1f}%)")
    print(f"Maximum absolute difference:  {max_diff_pub:.4f} ms")

    diff_pub_mask = abs_diff_pub > 0.0
    if diff_pub_mask.any():
        print(f"\nRecordings with non-zero difference ({diff_pub_mask.sum()} rows):")
        sub_df = m[diff_pub_mask][["recording_id", "scenario", "lag_ms", "timeLag_ms"]].copy()
        sub_df["diff_ms"] = sub_df["lag_ms"] - sub_df["timeLag_ms"]
        print(sub_df.to_string(index=False))
    else:
        print("\nAll 48 recordings match published values exactly (0.0 ms difference)!")

    # 2. Compare Replication vs Pipeline (outputs/phase2a and outputs/closure/v2)
    # Note: p2a and v2 respiratory_lag_ms are identical (verified in G8)
    assert (m["lag_ms_p2a"] == m["lag_ms_v2"]).all()
    diff_pipe = m["lag_ms"] - m["lag_ms_p2a"]
    abs_diff_pipe = diff_pipe.abs()
    count_close_pipe = int((abs_diff_pipe <= 0.5).sum())
    count_exact_pipe = int((diff_pipe == 0.0).sum())
    max_diff_pipe = float(abs_diff_pipe.max())

    print("\n=== 2. REPLICATION vs PIPELINE (sync_validation_results.csv) ===")
    print(f"Total pairs compared: {len(m)}")
    print(f"Exact match (diff == 0.0 ms): {count_exact_pipe} / {len(m)} ({count_exact_pipe/len(m)*100:.1f}%)")
    print(f"Count with |diff| <= 0.5 ms:   {count_close_pipe} / {len(m)} ({count_close_pipe/len(m)*100:.1f}%)")
    print(f"Maximum absolute difference:  {max_diff_pipe:.4f} ms")

    diff_pipe_mask = abs_diff_pipe > 0.5
    if diff_pipe_mask.any():
        print(f"\nRecordings differing from pipeline by > 0.5 ms ({diff_pipe_mask.sum()} rows):")
        sub_df2 = m[diff_pipe_mask][["recording_id", "scenario", "lag_ms", "lag_ms_p2a"]].copy()
        sub_df2["diff_ms"] = sub_df2["lag_ms"] - sub_df2["lag_ms_p2a"]
        print(sub_df2.to_string(index=False))
    else:
        print("\nZero recordings differ by > 0.5 ms from pipeline!")

    # Print summary table of all 48 rows
    print("\n=== COMPLETE 48-RECORDING 3-WAY COMPARISON TABLE ===")
    summary_cols = ["recording_id", "scenario", "timeLag_ms", "lag_ms", "lag_ms_p2a"]
    print(m[summary_cols].to_string(index=False))


if __name__ == "__main__":
    main()
