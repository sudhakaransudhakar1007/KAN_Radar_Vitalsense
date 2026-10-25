"""Replication of Authors' Technical Validation MATLAB script.

MATLAB Logic:
    respiration_re = resample(respiration, 2000, Fs_resp);
    [P,Q] = rat(2000/Radar.fs);
    vitsig_re = resample(VitalSig, P, Q);
    [c,lags] = xcorr(respiration_re, vitsig_re);
    lag_max = lags(find(c==max(c)));
    lag_ms = lag_max*0.5;

Note on parameters:
    Radar.fs = 333.3333333333333 Hz -> [P, Q] = rat(2000 / (1000/3)) = [6, 1].
    Fs_resp = 256.0 Hz -> resampled by 2000 / 256 = 125 / 16.
    Zero-padding: No truncation to minimum length is performed before xcorr;
    MATLAB xcorr pads the shorter signal (VS24_Resting respiration: 239,063 samples)
    with zeros at the end to match the longer signal (VitalSig: 240,000 samples).
    Cross-correlation is unnormalized raw sum of products.
"""

from fractions import Fraction
import glob
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import scipy.io as sio
import scipy.signal as signal

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_replication():
    data_dir = PROJECT_ROOT.parent / "data" / "VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = PROJECT_ROOT / "data" / "VITALSENSE_120_DATASET"

    # Discover candidate pairs
    rad_files = sorted(list(data_dir.glob("VS*/VS*.mat")))
    rad_files = [f for f in rad_files if not f.name.endswith("_Mindray.mat")]
    print(f"Discovered {len(rad_files)} radar recordings.")

    results = []

    for rad_path in rad_files:
        stem = rad_path.stem  # e.g. VS01_Resting
        sub_id, cond = stem.split("_")
        ref_path = rad_path.parent / f"{stem}_Mindray.mat"

        if not ref_path.exists():
            print(f"WARNING: Reference missing for {stem}")
            continue

        rad_mat = sio.loadmat(str(rad_path))
        ref_mat = sio.loadmat(str(ref_path))

        vitsig = rad_mat["VitalSig"].flatten()
        rad_fs = float(rad_mat["Radar"]["fs"][0, 0][0, 0])

        resp = ref_mat["respiration"].flatten()
        ref_fs_resp = float(ref_mat["Fs_resp"][0, 0]) if "Fs_resp" in ref_mat else 256.0

        # Rational resampling factors
        frac_radar = Fraction(2000.0 / rad_fs).limit_denominator(1000)
        p_rad, q_rad = frac_radar.numerator, frac_radar.denominator

        frac_resp = Fraction(2000.0 / ref_fs_resp).limit_denominator(1000)
        p_resp, q_resp = frac_resp.numerator, frac_resp.denominator

        # Resample signals to 2000 Hz
        vitsig_re = signal.resample_poly(vitsig, p_rad, q_rad)
        resp_re = signal.resample_poly(resp, p_resp, q_resp)

        # Full cross-correlation: [c, lags] = xcorr(respiration_re, vitsig_re)
        c = signal.correlate(resp_re, vitsig_re, mode="full")
        lags = signal.correlation_lags(len(resp_re), len(vitsig_re), mode="full")

        max_c = np.max(c)
        max_indices = np.where(c == max_c)[0]
        n_ties = len(max_indices)
        lag_max_samples = lags[max_indices]
        lag_ms = lag_max_samples * 0.5

        # Record primary lag (first if tie, as find() does in MATLAB)
        primary_lag_samples = int(lag_max_samples[0])
        primary_lag_ms = float(lag_ms[0])

        results.append({
            "recording_id": stem,
            "scenario": cond,
            "lag_samples": primary_lag_samples,
            "lag_ms": primary_lag_ms,
            "n_ties": n_ties,
            "resp_len_2000": len(resp_re),
            "radar_len_2000": len(vitsig_re),
        })

    df = pd.DataFrame(results)
    out_csv = Path("outputs/closure/authors_method_lags.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Saved replication results to {out_csv} ({len(df)} rows).")

    return df


if __name__ == "__main__":
    run_replication()
