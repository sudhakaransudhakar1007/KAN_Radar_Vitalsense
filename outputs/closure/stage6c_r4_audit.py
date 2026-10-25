"""R4 Audit Script: Detailed dry-run rule verification, coverage distribution, VS16/VS19 analysis."""

import sys
from pathlib import Path
import numpy as np
import scipy.io as sio

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.phase3.ecg_reference import clean_ecg_nans, detect_r_peaks, ECGReferenceValidator
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator


def main():
    data_dir = Path("data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = repo_root / "data/VITALSENSE_120_DATASET"

    ref_files = sorted(list(data_dir.glob("*/*_Mindray.mat")))
    generator = SupervisedDatasetGenerator()
    val_legacy = ECGReferenceValidator()

    # (b) Coverage distribution across all 1104 windows
    all_coverages_s = []
    all_coverages_pct = []
    vs03_w0_cov = None

    # (c) Min/max RR and HR over all valid RR intervals
    scenario_stats = {
        "Resting": {"rrs": [], "hrs": []},
        "Apnea": {"rrs": [], "hrs": []},
    }
    vs16_stats = {
        "VS16_Apnea": {"rrs": [], "hrs": []},
        "VS16_Resting": {"rrs": [], "hrs": []},
    }

    for rf in ref_files:
        stem = rf.stem.replace("_Mindray", "")
        sub, cond = stem.split("_")
        mat = sio.loadmat(rf)
        ecg_raw = mat["ecg_lead2"].flatten()

        cleaned_ecg, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)
        rpeaks = detect_r_peaks(cleaned_ecg, fs=500.0, min_bpm=35.0, max_bpm=185.0)

        p_times = rpeaks["peak_times"]
        rrs = rpeaks["rr_intervals"]
        v_mask = rpeaks["valid_rr_mask"]
        valid_rrs = rrs[v_mask]
        valid_hrs = 60.0 / valid_rrs

        scenario_stats[cond]["rrs"].extend(valid_rrs.tolist())
        scenario_stats[cond]["hrs"].extend(valid_hrs.tolist())

        if stem in vs16_stats:
            vs16_stats[stem]["rrs"].extend(valid_rrs.tolist())
            vs16_stats[stem]["hrs"].extend(valid_hrs.tolist())

        # Window level
        for k in range(23):
            t_s = round(k * 5.0, 3)
            t_e = round(t_s + 10.0, 3)
            hr_h, hr_a, cnt, cov_pct, max_g, ok, rej = generator.compute_window_reference_hr(t_s, t_e, rpeaks)
            # Reconstruct cov_s
            cov_s = (cov_pct / 100.0) * 10.0
            all_coverages_s.append(cov_s)
            all_coverages_pct.append(cov_pct)

            if stem == "VS03_Resting" and k == 0:
                vs03_w0_cov = (cov_s, cov_pct, ok, rej)

    all_cov_s = np.array(all_coverages_s)
    all_cov_pct = np.array(all_coverages_pct)

    print("=== R4(b) Window RR Coverage Distribution (1,104 windows) ===")
    print(f"Min coverage: {np.min(all_cov_s):.4f} s ({np.min(all_cov_pct):.2f}%)")
    print(f"1st percentile coverage: {np.percentile(all_cov_s, 1):.4f} s ({np.percentile(all_cov_pct, 1):.2f}%)")
    print(f"5th percentile coverage: {np.percentile(all_cov_s, 5):.4f} s ({np.percentile(all_cov_pct, 5):.2f}%)")
    print(f"Count below 90% (<9.0s): {np.sum(all_cov_pct < 90.0)}")
    print(f"Count below 85% (<8.5s): {np.sum(all_cov_pct < 85.0)}")
    print(f"Count below 80% (<8.0s): {np.sum(all_cov_pct < 80.0)}")
    print(f"VS03_Resting window 0: cov_s={vs03_w0_cov[0]:.4f}s, cov_pct={vs03_w0_cov[1]:.2f}%, accepted={vs03_w0_cov[2]}, reason={vs03_w0_cov[3]}")

    print("\n=== R4(c) Physiological RR and HR Bounds ===")
    for sc, data in scenario_stats.items():
        rrs = np.array(data["rrs"])
        hrs = np.array(data["hrs"])
        print(f"Scenario {sc} ({len(rrs)} beats):")
        print(f"  RR range: [{np.min(rrs):.4f} s, {np.max(rrs):.4f} s]")
        print(f"  HR range: [{np.min(hrs):.2f} bpm, {np.max(hrs):.2f} bpm]")

    for st, data in vs16_stats.items():
        rrs = np.array(data["rrs"])
        hrs = np.array(data["hrs"])
        print(f"Recording {st} ({len(rrs)} beats):")
        print(f"  RR range: [{np.min(rrs):.4f} s, {np.max(rrs):.4f} s]")
        print(f"  HR range: [{np.min(hrs):.2f} bpm, {np.max(hrs):.2f} bpm]")

    # Check legacy detector vs canonical detector on VS16
    print("\n=== VS16 Legacy vs Canonical Detector Comparison ===")
    for st in ["VS16_Apnea", "VS16_Resting"]:
        sub, cond = st.split("_")
        rf = data_dir / sub / f"{st}_Mindray.mat"
        mat = sio.loadmat(rf)
        ecg_raw = mat["ecg_lead2"].flatten()
        cleaned_ecg, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)

        res_canon = detect_r_peaks(cleaned_ecg, fs=500.0, min_bpm=35.0, max_bpm=185.0)
        res_legacy = val_legacy.detect_r_peaks_pan_tompkins(cleaned_ecg)

        canon_rrs = res_canon["rr_intervals"]
        legacy_rrs = res_legacy.rr_intervals_s

        canon_lt_0343 = np.sum(canon_rrs < 0.343)
        legacy_lt_0343 = np.sum(legacy_rrs < 0.343)
        print(f"{st}:")
        print(f"  Canonical peaks: {len(res_canon['peaks'])}, RR < 0.343s count: {canon_lt_0343}")
        print(f"  Legacy peaks:    {len(res_legacy.peak_indices)}, RR < 0.343s count: {legacy_lt_0343}")
        if legacy_lt_0343 > 0:
            bad = legacy_rrs[legacy_rrs < 0.343]
            print(f"  Legacy RR < 0.343s values: {bad}")

    # (d) VS19 analysis and peak matching
    print("\n=== R4(d) VS19 Legacy vs Canonical Polarity Comparison ===")
    for st in ["VS19_Apnea", "VS19_Resting"]:
        sub, cond = st.split("_")
        rf = data_dir / sub / f"{st}_Mindray.mat"
        mat = sio.loadmat(rf)
        ecg_raw = mat["ecg_lead2"].flatten()
        cleaned_ecg, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)

        res_canon = detect_r_peaks(cleaned_ecg, fs=500.0, min_bpm=35.0, max_bpm=185.0)
        res_legacy = val_legacy.detect_r_peaks_pan_tompkins(cleaned_ecg)

        c_times = res_canon["peak_times"]
        l_times = res_legacy.peak_times_s

        # Match peaks within 20 ms
        matched_diffs_ms = []
        for ct in c_times:
            diffs = np.abs(l_times - ct)
            min_idx = np.argmin(diffs)
            if diffs[min_idx] <= 0.020:
                matched_diffs_ms.append(diffs[min_idx] * 1000.0)

        match_frac = len(matched_diffs_ms) / max(len(c_times), len(l_times))
        med_diff = np.median(matched_diffs_ms) if matched_diffs_ms else np.nan
        max_diff = np.max(matched_diffs_ms) if matched_diffs_ms else np.nan

        # Also find overall nearest difference (even if > 20ms)
        all_nearest_diffs_ms = [np.min(np.abs(l_times - ct)) * 1000.0 for ct in c_times]
        med_all_shift = np.median(all_nearest_diffs_ms)

        print(f"{st}:")
        print(f"  Canonical peaks: {len(c_times)}, Legacy peaks: {len(l_times)}")
        print(f"  Matched within 20ms: {len(matched_diffs_ms)} / {max(len(c_times), len(l_times))} ({match_frac*100:.1f}%)")
        print(f"  Median diff of matched: {med_diff:.2f} ms, Max diff of matched: {max_diff:.2f} ms")
        print(f"  Median timing shift to nearest peak: {med_all_shift:.2f} ms")

    # Overall dataset: check how many recordings give identical peak timestamps between detectors
    print("\n=== Dataset-wide Detector Timestamp Comparison (48 recordings) ===")
    identical_count = 0
    non_identical = []
    for rf in ref_files:
        stem = rf.stem.replace("_Mindray", "")
        mat = sio.loadmat(rf)
        ecg_raw = mat["ecg_lead2"].flatten()
        cleaned_ecg, _, _ = clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)

        res_c = detect_r_peaks(cleaned_ecg, fs=500.0, min_bpm=35.0, max_bpm=185.0)
        res_l = val_legacy.detect_r_peaks_pan_tompkins(cleaned_ecg)

        c_p = res_c["peaks"]
        l_p = res_l.peak_indices

        # Check if identical
        if len(c_p) == len(l_p) and np.array_equal(c_p, l_p):
            identical_count += 1
        else:
            # Check if all peaks match within 20 ms
            max_p_diff = 0.0
            if len(c_p) == len(l_p):
                max_samp_diff = np.max(np.abs(c_p - l_p))
                max_p_diff = max_samp_diff / 500.0 * 1000.0
            else:
                max_p_diff = 999.0
            non_identical.append((stem, len(c_p), len(l_p), max_p_diff))

    print(f"Recordings with exactly identical peak indices: {identical_count} / 48")
    print(f"Non-identical recordings count: {len(non_identical)}")
    for item in non_identical[:10]:
        print(f"  {item[0]}: canonical={item[1]}, legacy={item[2]}, max_diff_ms={item[3]:.1f}")


if __name__ == "__main__":
    main()
