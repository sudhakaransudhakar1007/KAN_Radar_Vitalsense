import pandas as pd

df_authors = pd.read_csv("outputs/closure/authors_method_lags.csv")
df_v2 = pd.read_csv("outputs/closure/v2/sync_validation_results.csv")
df_p2a = pd.read_csv("outputs/phase2a/sync_validation_results.csv")

df_authors["key"] = df_authors["recording_id"]
df_v2["key"] = df_v2["subject_id"] + "_" + df_v2["condition"]
df_p2a["key"] = df_p2a["subject_id"] + "_" + df_p2a["condition"]

m = df_authors.merge(df_p2a[["key", "respiratory_lag_ms"]], on="key").merge(
    df_v2[["key", "respiratory_lag_ms"]], on="key", suffixes=("_p2a", "_v2")
)
m["diff"] = m["respiratory_lag_ms_v2"] - m["lag_ms"]
m = m.sort_values("key")

print("| recording | authors_lag_ms | pipeline_phase2a_ms | pipeline_v2_ms | diff_ms |")
print("| :--- | :--- | :--- | :--- | :--- |")
for _, r in m.iterrows():
    print(
        f"| {r['key']} | {r['lag_ms']:.1f} | {r['respiratory_lag_ms_p2a']:.1f} | {r['respiratory_lag_ms_v2']:.1f} | {r['diff']:.1f} |"
    )

direct = (abs(m["respiratory_lag_ms_v2"] - m["lag_ms"]) <= 0.5).sum()
flipped = (abs(m["respiratory_lag_ms_v2"] - (-m["lag_ms"])) <= 0.5).sum()
print(f"\nDIRECT MATCHES (|pipeline - authors| <= 0.5 ms): {direct} / 48")
print(f"SIGN-FLIPPED MATCHES (|pipeline - (-authors)| <= 0.5 ms): {flipped} / 48")
