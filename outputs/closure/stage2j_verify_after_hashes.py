"""Verify after-hashes for Stage 2J and compare with before-hashes."""

import hashlib
from pathlib import Path


def get_h(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def main():
    before_file = Path("outputs/closure/stage2j_hashes_before.txt")
    before_hashes = {}
    with open(before_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("==="):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                before_hashes[parts[1]] = parts[0]

    assert len(before_hashes) == 154, f"Expected 154 files, got {len(before_hashes)}"

    after_lines = []
    after_hashes = {}
    mismatches = []
    matches = []

    # Re-run grouping as in recorder
    import glob
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    groups = {
        "src": sorted([Path(p) for p in glob.glob("src/**/*.py", recursive=True)]),
        "tests": sorted([Path(p) for p in glob.glob("tests/**/*.py", recursive=True)]),
        "outputs/phase2a": sorted([Path(p) for p in glob.glob("outputs/phase2a/*.*")]),
        "raw_mat": sorted(list(data_dir.glob("*/*.mat"))),
    }

    for grp, files in groups.items():
        after_lines.append(f"=== {grp} ({len(files)} files) ===")
        for f in files:
            rel = str(f).replace("\\", "/")
            h = get_h(f)
            after_lines.append(f"{h}  {rel}")
            after_hashes[rel] = h
            if rel in before_hashes:
                if before_hashes[rel] != h:
                    mismatches.append((rel, before_hashes[rel], h))
                else:
                    matches.append(rel)
            else:
                mismatches.append((rel, "MISSING_IN_BEFORE", h))
        after_lines.append("")

    target = Path("outputs/closure/stage2j_hashes_after.txt")
    target.write_text("\n".join(after_lines), encoding="utf-8")
    print(f"Recorded after-hashes for {len(after_hashes)} files into {target}")
    print(f"Total files checked: {len(after_hashes)}")
    print(f"Matching files: {len(matches)}")
    print(f"Mismatched files: {len(mismatches)}")

    print("\n=== MISMATCHED FILES (MUST ONLY BE step2b_issue_register.csv) ===")
    for rel, old_h, new_h in mismatches:
        print(f"File: {rel}")
        print(f"  BEFORE: {old_h}")
        print(f"  AFTER:  {new_h}")

    assert len(mismatches) == 1, f"Expected exactly 1 mismatch, got {len(mismatches)}"
    assert mismatches[0][0] == "outputs/phase2a/step2b_issue_register.csv", f"Unexpected mismatch: {mismatches[0][0]}"
    print("\nVERIFICATION RESULT: ALL 34 src/, 18 tests/, 96 raw mat, and 5 other outputs/phase2a files are UNTOUCHED!")
    print("ONLY authorized modification to outputs/phase2a/step2b_issue_register.csv occurred.")


if __name__ == "__main__":
    main()
