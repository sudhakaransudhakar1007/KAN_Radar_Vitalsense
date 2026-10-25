"""Update ISS-23 evidence and recommended-action cells in outputs/phase2a/step2b_issue_register.csv."""

import csv
from pathlib import Path
import pandas as pd


def main():
    csv_path = Path("outputs/phase2a/step2b_issue_register.csv")

    # Read original
    df = pd.read_csv(csv_path)
    old_row = df[df["issue_id"] == "ISS-23"].to_dict(orient="records")[0]

    old_evidence = old_row["evidence"]
    old_action = old_row["recommended_action"]

    new_evidence = (
        "cardiac_surrogate_mae (src/sync_validation/cardiac_radar_validator.py:267) is non-deterministic between runs "
        "due to unseeded np.random.permutation (verified: differs on repeated in-memory runs across recordings). In contrast, "
        "compute_surrogate_respiratory_control (src/sync_validation/respiratory_validator.py:225) is fully deterministic "
        "(uses np.random.default_rng(42); verified identical on repeated runs); its divergence from outputs/phase2a arises from "
        "a historical method change from circular shifts to Fourier phase randomization (N=5) documented in Section 21.6."
    )
    new_action = (
        "Replace unseeded np.random.permutation in cardiac_surrogate_mae with a seeded generator "
        "(e.g. np.random.default_rng(seed)) to ensure run-to-run determinism; record and fix all PRNG seeds in the future "
        "prespecified N >= 1000 surrogate protocol."
    )

    df.loc[df["issue_id"] == "ISS-23", "evidence"] = new_evidence
    df.loc[df["issue_id"] == "ISS-23", "recommended_action"] = new_action

    # Save
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
    assert len(df_v) == 23, f"Expected 23 rows, got {len(df_v)}"
    print("pandas validation: PASS, shape:", df_v.shape)
    print("Status counts:\n", df_v["status"].value_counts().to_dict())

    print("\n=== ISS-23 OLD EVIDENCE ===")
    print(old_evidence)
    print("\n=== ISS-23 NEW EVIDENCE ===")
    print(df_v.loc[df_v["issue_id"] == "ISS-23", "evidence"].values[0])

    print("\n=== ISS-23 OLD RECOMMENDED ACTION ===")
    print(old_action)
    print("\n=== ISS-23 NEW RECOMMENDED ACTION ===")
    print(df_v.loc[df_v["issue_id"] == "ISS-23", "recommended_action"].values[0])


if __name__ == "__main__":
    main()
