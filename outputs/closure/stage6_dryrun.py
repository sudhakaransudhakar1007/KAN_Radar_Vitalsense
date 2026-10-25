"""Stage 6 In-Memory Dry Run and Verification Script.

Processes all 48 recordings from the VITALSENSE dataset in memory:
- Strictly asserts exactly 48 radar and 48 Mindray files matching VSxx_Resting and VSxx_Apnea (VS01-VS24).
- Executes Stage 6 windowing and label logic (23 continuous-time windows per recording, midpoint rule, harmonic mean HR).
- Exports summary metrics to outputs/closure/stage6_dryrun_counts.csv without printing individual label values.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import numpy as np
import scipy.io as sio

# Ensure kan_radar_HR is in Python path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.phase3.ecg_reference import clean_ecg_nans, detect_r_peaks
from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator


def run_stage6_dryrun() -> None:
    # 1. Dataset Discovery and Assertions
    candidate_data_dirs = [
        Path("data/VITALSENSE_120_DATASET"),
        repo_root / "data/VITALSENSE_120_DATASET",
        repo_root.parent / "data/VITALSENSE_120_DATASET",
    ]
    data_dir = None
    for d in candidate_data_dirs:
        if d.exists():
            data_dir = d
            break
    assert data_dir is not None, "Dataset directory VITALSENSE_120_DATASET not found"

    all_mats = sorted(list(data_dir.glob("*/*.mat")))
    radar_files = sorted([f for f in all_mats if not f.name.endswith("_Mindray.mat")])
    ref_files = sorted([f for f in all_mats if f.name.endswith("_Mindray.mat")])

    assert len(radar_files) == 48, f"Expected exactly 48 radar files, found {len(radar_files)}"
    assert len(ref_files) == 48, f"Expected exactly 48 Mindray files, found {len(ref_files)}"

    name_pattern = re.compile(r"^VS(0[1-9]|1[0-9]|2[0-4])_(Resting|Apnea)$")
    for rf in radar_files:
        assert name_pattern.match(rf.stem), f"File {rf.name} does not match VSxx_Resting / VSxx_Apnea"

    for mf in ref_files:
        base = mf.stem.replace("_Mindray", "")
        assert name_pattern.match(base), f"File {mf.name} does not match VSxx_Resting_Mindray / VSxx_Apnea_Mindray"

    generator = SupervisedDatasetGenerator()

    min_rr_185 = 60.0 / 185.0   # ~0.324324 s
    max_rr_175 = 60.0 / 175.0   # ~0.342857 s

    rows = []
    max_inst_hr = -1.0
    max_inst_hr_rec = ""
    max_inst_hr_rr = 0.0

    rr_lt_0343_counts = {"Resting": 0, "Apnea": 0}

    # 2. Process all 48 pairs in memory
    for rad_f in radar_files:
        stem = rad_f.stem
        sub, cond = stem.split("_")
        ref_f = rad_f.parent / f"{stem}_Mindray.mat"
        assert ref_f.exists(), f"Missing Mindray file for {stem}"

        mat = sio.loadmat(ref_f)
        ecg_raw = mat["ecg_lead2"].flatten()
        ecg_fs = 500.0

        cleaned_ecg, nan_cnt, _ = clean_ecg_nans(ecg_raw, only_isolated=True, fill_boundary=True)
        rpeaks = detect_r_peaks(cleaned_ecg, fs=ecg_fs, min_bpm=35.0, max_bpm=185.0)

        p_times = rpeaks.get("peak_times", np.array([]))
        rrs = rpeaks.get("rr_intervals", np.array([]))
        v_mask = rpeaks.get("valid_rr_mask", np.array([]))
        valid_rr = rrs[v_mask] if len(rrs) > 0 else np.array([])

        cov_s = float(np.sum(valid_rr))
        max_gap = float(np.max(rrs)) if len(rrs) > 0 else 999.0
        rec_cov_pct = (cov_s / (len(ecg_raw) / ecg_fs)) * 100.0

        # Recording SQI verdict per D9 (amplitude stability NOT_ASSESSED -> SQI_PARTIAL, never PASS)
        sqi_eligible = (rec_cov_pct >= 85.0) and (max_gap < 3.0) and (len(valid_rr) >= 20)
        sqi_verdict = "SQI_PARTIAL" if sqi_eligible else "SQI_FAIL"

        # Count RR intervals in (0.3243s, 0.3429s] (175 - 185 bpm)
        n_rr_175_185 = int(np.sum((rrs > min_rr_185) & (rrs <= max_rr_175)))

        # Track max instantaneous HR over valid RR intervals
        if len(valid_rr) > 0:
            rec_inst_hrs = 60.0 / valid_rr
            top_hr_idx = int(np.argmax(rec_inst_hrs))
            top_hr = float(rec_inst_hrs[top_hr_idx])
            if top_hr > max_inst_hr:
                max_inst_hr = top_hr
                max_inst_hr_rec = stem
                max_inst_hr_rr = float(valid_rr[top_hr_idx])

        # Track RR intervals shorter than 0.343s (< 175 bpm)
        rr_lt_0343_counts[cond] += int(np.sum(rrs < 0.343))

        # 23 continuous-time windows
        accepted_cnt = 0
        rejected_cnt = 0
        rej_reasons = []

        for k in range(23):
            t_start = round(k * 5.0, 3)
            t_end = round(t_start + 10.0, 3)
            hr_h, hr_a, cnt, cov_pct, max_g, ok, rej = generator.compute_window_reference_hr(
                t_start, t_end, rpeaks
            )
            if ok:
                accepted_cnt += 1
            else:
                rejected_cnt += 1
                if rej not in rej_reasons:
                    rej_reasons.append(rej)

        rej_str = ";".join(rej_reasons) if rej_reasons else "NONE"

        rows.append({
            "recording": stem,
            "sqi_verdict": sqi_verdict,
            "candidate_windows": 23,
            "accepted": accepted_cnt,
            "rejected": rejected_cnt,
            "rejection_reasons": rej_str,
            "n_peaks": len(p_times),
            "n_valid_rr": int(np.sum(v_mask)),
            "n_rr_in_0.3243_to_0.3429_s": n_rr_175_185,
        })

    # 3. Export CSV
    out_dir = repo_root / "outputs/closure"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "stage6_dryrun_counts.csv"

    fieldnames = [
        "recording",
        "sqi_verdict",
        "candidate_windows",
        "accepted",
        "rejected",
        "rejection_reasons",
        "n_peaks",
        "n_valid_rr",
        "n_rr_in_0.3243_to_0.3429_s",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {out_csv} with {len(rows)} recording rows.")
    print(f"Max instantaneous HR: {max_inst_hr:.2f} bpm (RR = {max_inst_hr_rr:.4f} s) in {max_inst_hr_rec}")
    print(f"Count of RR intervals < 0.343 s: {rr_lt_0343_counts}")


if __name__ == "__main__":
    run_stage6_dryrun()
