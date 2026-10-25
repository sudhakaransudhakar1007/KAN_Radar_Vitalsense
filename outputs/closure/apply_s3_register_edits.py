"""Script to apply S3 register edits to outputs/phase2a/step2b_issue_register.csv."""

import csv
from pathlib import Path
import pandas as pd


def main():
    csv_path = Path("outputs/phase2a/step2b_issue_register.csv")
    df = pd.read_csv(csv_path)

    # 1. Capture old cells for ISS-16 and ISS-18
    old_cells = {}
    for i in ["ISS-16", "ISS-18"]:
        old_cells[i] = df[df["issue_id"] == i].iloc[0].to_dict()

    # 2. Update ISS-16
    df.loc[df["issue_id"] == "ISS-16", "evidence"] = (
        "Headline claimed 'WINDOW-LEVEL ALIGNMENT ADEQUATE FOR 10 s WINDOWS' before defining prespecified adequacy criteria "
        "or verifying test-set generalization."
    )
    df.loc[df["issue_id"] == "ISS-16", "scientific_risk"] = (
        "Prematurely endorses window-level alignment as adequately validated, risking unverified supervised training."
    )

    # 3. Update ISS-18
    df.loc[df["issue_id"] == "ISS-18", "evidence"] = (
        "Thresholds for respiratory correlation (r >= 0.40) and cardiac window agreement (MAE < 5.0 bpm) were implemented "
        "in runner.py without prespecified protocol or validated justification."
    )
    df.loc[df["issue_id"] == "ISS-18", "scientific_risk"] = (
        "Thresholds are not prespecified in any available document; provenance NOT_VERIFIABLE; risk confirmation bias "
        "and lack independent prior justification."
    )
    df.loc[df["issue_id"] == "ISS-18", "recommended_action"] = (
        "Formally label the 5.0 bpm and 0.40 correlation thresholds as UNVERIFIED_PROVENANCE in audit documentation "
        "until an independent validated reference is provided."
    )

    # 4. Add ISS-24 .. ISS-28
    new_rows = [
        {
            "issue_id": "ISS-24",
            "severity": "High",
            "file_or_function": "src/phase3/ecg_reference.py:102,116",
            "evidence": "Phase 3 ecg_reference.py:102,116 rejects any recording with a boundary NaN (VS10_Resting, 22 windows), while the Stage 2 cleaning handles it (156 beats, tested in K1).",
            "scientific_risk": "Rejection of viable recordings due to boundary NaNs artificially reduces training dataset size and creates discrepancy with sync_validation.",
            "recommended_action": "Adopt Stage 2 clean_ecg_nans boundary handling across Phase 3 upon investigator approval.",
            "status": "OPEN",
        },
        {
            "issue_id": "ISS-25",
            "severity": "Medium",
            "file_or_function": "src/phase3/supervised_dataset_generator.py:220-227, 291",
            "evidence": "Phase 3 integer-hop accumulation start += 1667 drops the 23rd window (7 samples short); time-based starts give 23 (J3).",
            "scientific_risk": "Discretization drift excludes 48 viable 10-second windows (4.98 seconds per recording) from supervised dataset.",
            "recommended_action": "Replace integer-hop accumulation with round-based time formula start_k = int(round(k * 5.0 * fs)) pending PI decision D1.",
            "status": "OPEN",
        },
        {
            "issue_id": "ISS-26",
            "severity": "High",
            "file_or_function": "src/phase3/ecg_reference.py; src/sync_validation/ecg_processor.py",
            "evidence": "two ECG label pipelines with different detector, RR range and coverage threshold (per S1 numbers).",
            "scientific_risk": "Discrepant peak detection logic (e.g. VS19 polarity difference) and aggregation definitions produce inconsistent ground-truth HR targets.",
            "recommended_action": "Harmonize on a single canonical ECG detector and window aggregation definition pending PI decision D7.",
            "status": "OPEN",
        },
        {
            "issue_id": "ISS-27",
            "severity": "Medium",
            "file_or_function": "outputs/supervised_dataset/run_001/",
            "evidence": "run_001 label manifests exist, generated 2026-10-15 before the gate decision, status UNAPPROVED, SUPERSEDED (see run_001_status_note.md).",
            "scientific_risk": "Premature use of unapproved, superseded manifests would violate gate governance and propagate pre-Stage-2 discrepancies.",
            "recommended_action": "Retain run_001 manifests as read-only diagnostic records; require explicit PI sign-off on decision D3 before regenerating.",
            "status": "DOCUMENTED",
        },
        {
            "issue_id": "ISS-28",
            "severity": "Medium",
            "file_or_function": "src/sync_validation/respiratory_validator.py:157-160",
            "evidence": "respiratory cross-correlation lag is method-sensitive; plateau width median 95 ms (34.5 ms to 1,594 ms) in K3; the DC-product hypothesis was not supported (rho = -0.1254, p = 0.3956); mechanism NOT_ESTABLISHED.",
            "scientific_risk": "Over-interpreting discrete lag peaks risks unverified claims of physical hardware synchronization.",
            "recommended_action": "Document lag plateau width and classify hardware timing as UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0 per PI decision D4 and D5.",
            "status": "DOCUMENTED",
        },
    ]

    for nr in new_rows:
        if nr["issue_id"] not in df["issue_id"].values:
            df = pd.concat([df, pd.DataFrame([nr])], ignore_index=True)

    df.to_csv(csv_path, index=False, quoting=csv.QUOTE_MINIMAL)

    # Validate with strict csv.reader
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, strict=True)
        rows = list(reader)
    print("Strict csv.reader validation: PASS, total rows (inc header):", len(rows))
    for idx, r in enumerate(rows):
        assert len(r) == 7, f"Row {idx} has {len(r)} columns instead of 7"

    # Validate with pandas
    df_v = pd.read_csv(csv_path)
    assert len(df_v) == 28, f"Expected 28 rows, got {len(df_v)}"
    print("pandas validation: PASS, shape:", df_v.shape)
    print("\nStatus counts:\n", df_v["status"].value_counts().to_dict())

    # Print old -> new cells
    print("\n=== OLD -> NEW CELLS ===")
    for i in ["ISS-16", "ISS-18"]:
        new_row = df_v[df_v["issue_id"] == i].iloc[0].to_dict()
        print(f"[{i}] evidence:")
        print(f"  OLD: {old_cells[i]['evidence']}")
        print(f"  NEW: {new_row['evidence']}")
        print(f"[{i}] scientific_risk:")
        print(f"  OLD: {old_cells[i]['scientific_risk']}")
        print(f"  NEW: {new_row['scientific_risk']}")
        if old_cells[i]["recommended_action"] != new_row["recommended_action"]:
            print(f"[{i}] recommended_action:")
            print(f"  OLD: {old_cells[i]['recommended_action']}")
            print(f"  NEW: {new_row['recommended_action']}")
        print()

    print("=== NEW ROWS (ISS-24..ISS-28) ===")
    for nr in new_rows:
        row = df_v[df_v["issue_id"] == nr["issue_id"]].iloc[0]
        print(f"[{row['issue_id']}] {row['severity']} | {row['status']} | {row['file_or_function']}")
        print(f"  evidence: {row['evidence']}")


if __name__ == "__main__":
    main()
