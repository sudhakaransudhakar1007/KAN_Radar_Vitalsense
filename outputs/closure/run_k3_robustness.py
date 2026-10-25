"""Script to evaluate K3: Respiratory robustness outside src."""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio
from scipy import signal
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(".").resolve()))
from src.sync_validation.respiratory_validator import resample_signals_to_2000hz


def main():
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    # Load authors replicated lags and pipeline lags
    df_authors = pd.read_csv("outputs/closure/authors_method_lags.csv")
    df_v2 = pd.read_csv("outputs/closure/v2/sync_validation_results.csv")

    authors_map = dict(zip(df_authors["recording_id"], df_authors["lag_ms"]))
    pipeline_map = dict(
        zip(df_v2["subject_id"] + "_" + df_v2["condition"], df_v2["respiratory_lag_ms"])
    )

    all_mats = sorted(list(data_dir.glob("*/*_Mindray.mat")))
    records = []

    for m_path in all_mats:
        rec_id = m_path.stem.replace("_Mindray", "")
        sub, cond = rec_id.split("_")
        r_path = m_path.parent / f"{rec_id}.mat"

        m_mat = sio.loadmat(m_path)
        r_mat = sio.loadmat(r_path)

        resp_raw = m_mat["respiration"].flatten()
        vitsig_raw = r_mat["VitalSig"].flatten()

        # Resample to 2000 Hz and truncate to common length (pipeline method)
        v_2000, r_2000 = resample_signals_to_2000hz(vitsig_raw, 333.3333333333333, resp_raw, 256.0)

        mu_radar = float(np.mean(v_2000))
        sigma_radar = float(np.std(v_2000))
        mu_resp = float(np.mean(r_2000))
        sigma_resp = float(np.std(r_2000))

        r_dc = (mu_resp * mu_radar) / (sigma_resp * sigma_radar)

        lag_raw = authors_map[rec_id]
        lag_dem = pipeline_map[rec_id]
        lag_diff = lag_raw - lag_dem

        # Compute demeaned normalized cross-correlation
        vn = (v_2000 - mu_radar) / sigma_radar
        rn = (r_2000 - mu_resp) / sigma_resp
        n = len(vn)

        # Full correlation
        # Authors correlate xcorr(r, v), so lag > 0 means radar lags respiration
        c = signal.correlate(rn, vn, mode="full") / n
        lags_samples = signal.correlation_lags(len(rn), len(vn), mode="full")
        lags_ms = lags_samples * (1000.0 / 2000.0)

        # Restrict to search bound [-30s, +30s]
        mask_30s = (lags_ms >= -30000.0) & (lags_ms <= 30000.0)
        c_sub = c[mask_30s]
        lags_sub = lags_ms[mask_30s]

        # In pipeline, abs_corr or positive peak
        # In runner: abs_corr is evaluated, let's look at the absolute peak
        peak_idx = np.argmax(np.abs(c_sub))
        peak_corr = float(np.abs(c_sub[peak_idx]))
        peak_lag = float(lags_sub[peak_idx])

        # Correlation at lag 0
        idx_0 = np.where(lags_sub == 0.0)[0][0]
        corr_0 = float(np.abs(c_sub[idx_0]))

        # Correlation at +/- 0.5 ms (-1 sample, +1 sample)
        idx_minus1 = np.where(lags_sub == -0.5)[0][0]
        idx_plus1 = np.where(lags_sub == 0.5)[0][0]
        corr_minus05 = float(np.abs(c_sub[idx_minus1]))
        corr_plus05 = float(np.abs(c_sub[idx_plus1]))

        # Lag range where demeaned correlation >= peak - 0.001
        thresh = peak_corr - 0.001
        flat_mask = np.abs(c_sub) >= thresh
        flat_lags = lags_sub[flat_mask]
        lag_min_flat = float(np.min(flat_lags))
        lag_max_flat = float(np.max(flat_lags))
        flat_width_ms = lag_max_flat - lag_min_flat

        is_strict_local_max_at_0 = bool(corr_0 > corr_minus05 and corr_0 > corr_plus05)

        records.append({
            "recording": rec_id,
            "scenario": cond,
            "mu_radar": mu_radar,
            "sigma_radar": sigma_radar,
            "mu_resp": mu_resp,
            "sigma_resp": sigma_resp,
            "r_dc": r_dc,
            "lag_raw_ms": lag_raw,
            "lag_dem_ms": lag_dem,
            "lag_diff_ms": lag_diff,
            "peak_corr": round(peak_corr, 4),
            "corr_0": round(corr_0, 4),
            "corr_minus05": round(corr_minus05, 4),
            "corr_plus05": round(corr_plus05, 4),
            "lag_min_flat_ms": lag_min_flat,
            "lag_max_flat_ms": lag_max_flat,
            "flat_width_ms": flat_width_ms,
            "is_strict_local_max_at_0": is_strict_local_max_at_0,
        })

    df = pd.DataFrame(records)
    out_csv = Path("outputs/closure/respiratory_robustness_k3.csv")
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} rows to {out_csv}")

    # Spearman correlation
    rho, pval = spearmanr(df["lag_diff_ms"], df["r_dc"])
    print(f"\nSpearman correlation between (lag_raw - lag_dem) and r_dc: rho = {rho:.4f}, p = {pval:.4e}")

    # Print summary table
    print("\nSummary metrics (all 48 recordings):")
    print(f"r_dc: mean={df['r_dc'].mean():.2f}, std={df['r_dc'].std():.2f}, min={df['r_dc'].min():.2f}, max={df['r_dc'].max():.2f}")
    print(f"Flat width (corr >= peak - 0.001): mean={df['flat_width_ms'].mean():.1f} ms, median={df['flat_width_ms'].median():.1f} ms, min={df['flat_width_ms'].min():.1f} ms, max={df['flat_width_ms'].max():.1f} ms")

    # List recordings with pipeline lag exactly 0.0 ms
    zero_recs = df[df["lag_dem_ms"] == 0.0]
    print(f"\nRecordings with pipeline lag exactly 0.0 ms (N = {len(zero_recs)}):")
    for _, r in zero_recs.iterrows():
        print(f"  {r['recording']:15s} | peak={r['peak_corr']:.4f} | corr(-0.5)={r['corr_minus05']:.4f} | corr(0)={r['corr_0']:.4f} | corr(+0.5)={r['corr_plus05']:.4f} | strict_max={r['is_strict_local_max_at_0']} | flat_range=[{r['lag_min_flat_ms']:.1f}, {r['lag_max_flat_ms']:.1f}] ms (w={r['flat_width_ms']:.1f} ms)")


if __name__ == "__main__":
    main()
