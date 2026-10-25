"""Regenerate outputs/closure/gate_checklist.csv for Stage 5B per B3 and B6."""

import csv
from pathlib import Path


def main():
    checklist_path = Path("outputs/closure/gate_checklist.csv")

    rows = [
        {
            "boundary": "preprocessing",
            "current_status": "CONDITIONALLY_VERIFIED",
            "evidence_exists": (
                "All 96 raw MAT files 100% verified unmodified; in-memory working copies wired; "
                "single-sample NaN interpolation guarded and tested (5,629 isolated NaNs, 0 multi-sample gaps); "
                "4x zero-padding and 3-point parabolic peak interpolation implemented and tested in test_stage2_closure.py."
            ),
            "what_is_still_required": (
                "Formal PI sign-off on Section 18.x closure and adoption of Stage 2 clean_ecg_nans boundary handling in Phase 3 (Decision D6)."
            ),
            "who_decides": "Principal Investigator",
        },
        {
            "boundary": "label_generation",
            "current_status": "NOT_YET_APPROVED",
            "evidence_exists": (
                "Mindray monitor HR permanently disqualified (+6 to +7s latency); reference HR derived strictly from ECG R-peaks at nominal t0=0s zero shift; "
                "run_001 manifests cataloged and designated SUPERSEDED_UNAPPROVED."
            ),
            "what_is_still_required": (
                "Formal resolution of PI decisions D1 (23 vs 22 windows), D2a/b (label source & harmonic vs arithmetic HR), "
                "D6 (VS10_Resting inclusion), and D7 (canonical ECG detector); approval of formal gate closure."
            ),
            "who_decides": "Principal Investigator",
        },
        {
            "boundary": "hardware_clock_synchronization",
            "current_status": "UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0",
            "evidence_exists": (
                "No trigger, timestamp or clock information was found in the .mat files or the authors' script; "
                "the relation of the start times is unknown; nominal t0 = 0 is an assumption."
            ),
            "what_is_still_required": (
                "Formal adoption and sign-off on UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 limitation across all dataset documentation and scientific publications (Decision D4)."
            ),
            "who_decides": "Principal Investigator",
        },
        {
            "boundary": "respiratory_alignment",
            "current_status": "CONSISTENT_NOT_PROVEN",
            "evidence_exists": (
                "Replication of authors' method achieves 48/48 exact match; demeaning changes the argmax lag in 27 of 28 recordings; "
                "mechanism NOT_ESTABLISHED (K3: rho = -0.1254, p = 0.3956; plateau median 95 ms); "
                "tail truncation on VS24 (-3.0 ms) consistent with dataset range (-30 to +30 ms)."
            ),
            "what_is_still_required": (
                "Formal PI sign-off on respiratory reporting methodology (Decision D5) and prespecified N>=1000 surrogate null distribution."
            ),
            "who_decides": "Principal Investigator",
        },
        {
            "boundary": "10s_window_adequacy",
            "current_status": "NOT_YET_SUPPORTED",
            "evidence_exists": (
                "Continuous window coverage gate (>80% valid RR duration) implemented and tested; "
                "diagnostic baselines established on existing labels (LOSO constant-mean MAE 5.82 bpm; zero-shift radar spectral parabolic MAE 2.69 bpm)."
            ),
            "what_is_still_required": (
                "Formal approval of recording-level SQI gate (including validated amplitude stability threshold) and window-level coverage threshold (Decision D7)."
            ),
            "who_decides": "Principal Investigator",
        },
    ]

    fieldnames = [
        "boundary",
        "current_status",
        "evidence_exists",
        "what_is_still_required",
        "who_decides",
    ]

    with open(checklist_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Overwrote {checklist_path} with {len(rows)} updated rows.")


if __name__ == "__main__":
    main()
