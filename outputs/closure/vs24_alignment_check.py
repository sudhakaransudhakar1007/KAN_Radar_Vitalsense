"""VS24_Resting alignment diagnostic: Head vs Tail truncation analysis."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scipy.io as sio
import numpy as np
from src.sync_validation.respiratory_validator import resample_signals_to_2000hz, compute_respiratory_xcorr


def run():
    data_dir = PROJECT_ROOT.parent / "data" / "VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = PROJECT_ROOT / "data" / "VITALSENSE_120_DATASET"

    rad_mat = sio.loadmat(str(data_dir / "VS24" / "VS24_Resting.mat"))
    ref_mat = sio.loadmat(str(data_dir / "VS24" / "VS24_Resting_Mindray.mat"))

    vitsig = rad_mat["VitalSig"].flatten()
    rad_fs = float(rad_mat["Radar"]["fs"][0, 0][0, 0])

    resp_raw = ref_mat["respiration"].flatten()
    ref_fs_resp = float(ref_mat["Fs_resp"][0, 0]) if "Fs_resp" in ref_mat else 256.0

    print(f"VitalSig length: {len(vitsig)}, fs: {rad_fs} Hz (duration: {len(vitsig)/rad_fs:.4f} s)")
    print(f"Respiration length: {len(resp_raw)}, fs: {ref_fs_resp} Hz (duration: {len(resp_raw)/ref_fs_resp:.4f} s)")
    diff_s = (len(vitsig) / rad_fs) - (len(resp_raw) / ref_fs_resp)
    print(f"Duration difference: {diff_s:.5f} s (missing 120 samples at 256 Hz = {120/256.0:.5f} s)")

    # 1. Standard (tail truncation: both resampled to 2000 Hz and truncated at tail to matching length)
    v_2000_tail, r_2000_tail = resample_signals_to_2000hz(vitsig, rad_fs, resp_raw, ref_fs_resp)
    res_tail = compute_respiratory_xcorr(v_2000_tail, r_2000_tail, max_lag_sec=30.0)

    print("\n=== 1. STANDARD ASSUMPTION: TAIL TRUNCATION ===")
    print(f"Resampled length: {len(v_2000_tail)} samples ({len(v_2000_tail)/2000.0:.4f} s)")
    print(f"Best lag: {res_tail['pos_lag_ms']} ms")
    print(f"Correlation: {res_tail['pos_corr']:.4f}")
    print(f"Polarity: {res_tail['polarity']}")

    # 2. Head truncation: assume missing 120 samples occurred at the beginning (lead-in) of respiration.
    # If respiration started 0.46875s late, the first valid sample of respiration corresponds to radar time t = 0.46875s.
    # Therefore, to align HEADs, we discard the first 0.46875s of radar VitalSig:
    n_rad_head = int(round((120.0 / ref_fs_resp) * rad_fs))
    vitsig_head_aligned = vitsig[n_rad_head:]
    v_2000_head, r_2000_head = resample_signals_to_2000hz(vitsig_head_aligned, rad_fs, resp_raw, ref_fs_resp)
    res_head = compute_respiratory_xcorr(v_2000_head, r_2000_head, max_lag_sec=30.0)

    print("\n=== 2. HYPOTHETICAL ASSUMPTION: HEAD TRUNCATION (Radar trimmed at head by 120/256s) ===")
    print(f"Trimmed VitalSig head samples: {n_rad_head} ({n_rad_head/rad_fs:.5f} s)")
    print(f"Resampled length: {len(v_2000_head)} samples ({len(v_2000_head)/2000.0:.4f} s)")
    print(f"Best lag: {res_head['pos_lag_ms']} ms")
    print(f"Correlation: {res_head['pos_corr']:.4f}")
    print(f"Polarity: {res_head['polarity']}")

    # 3. Discard 120 samples from respiration head directly vs full radar
    # If radar started at t=0 and respiration was clipped at head by another 120 samples:
    resp_head_cut = resp_raw[120:]
    v_2000_h3, r_2000_h3 = resample_signals_to_2000hz(vitsig, rad_fs, resp_head_cut, ref_fs_resp)
    res_h3 = compute_respiratory_xcorr(v_2000_h3, r_2000_h3, max_lag_sec=30.0)

    print("\n=== 3. ALTERNATIVE: RESPIRATION TRIMMED AT HEAD (Extra 120 samples removed from resp head) ===")
    print(f"Best lag: {res_h3['pos_lag_ms']} ms")
    print(f"Correlation: {res_h3['pos_corr']:.4f}")

    # Comparison & Delta
    delta_lag = res_head['pos_lag_ms'] - res_tail['pos_lag_ms']
    print("\n=== COMPARISON SUMMARY ===")
    print(f"Tail truncation lag: {res_tail['pos_lag_ms']:.1f} ms, corr: {res_tail['pos_corr']:.4f}")
    print(f"Head truncation lag: {res_head['pos_lag_ms']:.1f} ms, corr: {res_head['pos_corr']:.4f}")
    print(f"Lag shift: {delta_lag:.1f} ms ({delta_lag/1000.0:.4f} s)")
    print(f"Correlation change: {res_head['pos_corr'] - res_tail['pos_corr']:+.4f}")


if __name__ == "__main__":
    run()
