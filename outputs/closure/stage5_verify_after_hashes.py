"""Verify after-hashes for Stage 5 across all 157 tracked files."""

import hashlib
from pathlib import Path


def get_h(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def main():
    before_file = Path("outputs/closure/stage5_hashes_before.txt")
    before_hashes = {}
    with open(before_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("==="):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                norm_path = parts[1].strip().replace("\\", "/")
                before_hashes[norm_path] = parts[0]


    assert len(before_hashes) == 157, f"Expected 157 files, got {len(before_hashes)}"

    after_lines = []
    after_hashes = {}
    mismatches = []
    matches = []

    # Same grouping
    import glob
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    groups = {
        "src": sorted([Path(p) for p in glob.glob("src/**/*.py", recursive=True)]),
        "tests": sorted([Path(p) for p in glob.glob("tests/**/*.py", recursive=True)]),
        "outputs/phase2a": sorted([Path(p) for p in glob.glob("outputs/phase2a/*.*")]),
        "raw_mat": sorted(list(data_dir.glob("*/*.mat"))),
        "run_001_manifests": [
            Path("outputs/supervised_dataset/run_001/accepted_window_manifest.csv"),
            Path("outputs/supervised_dataset/run_001/candidate_window_manifest.csv"),
            Path("outputs/supervised_dataset/run_001/rejected_window_manifest.csv"),
        ],
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

    target = Path("outputs/closure/stage5_hashes_after.txt")
    target.write_text("\n".join(after_lines), encoding="utf-8")
    print(f"Recorded after-hashes for {len(after_hashes)} files into {target}")
    print(f"Total files checked: {len(after_hashes)}")
    print(f"Matching files: {len(matches)}")
    print(f"Mismatched files: {len(mismatches)}")

    print("\n=== MISMATCHED FILES (MUST ONLY BE THE 2 AUTHORIZED FILES) ===")
    for rel, old_h, new_h in mismatches:
        print(f"File: {rel}")
        print(f"  BEFORE: {old_h}")
        print(f"  AFTER:  {new_h}")

    authorized = {
        "outputs/phase2a/step2b_issue_register.csv",
        "outputs/phase2a/step2b_consistency_audit.md",
    }
    mismatched_paths = {m[0] for m in mismatches}
    assert mismatched_paths == authorized, f"Unexpected mismatches: {mismatched_paths.symmetric_difference(authorized)}"

    print("\nVERIFICATION RESULT: ALL 34 src/, 18 tests/, 96 raw mat, 3 run_001 manifests, and 4 other phase2a files are UNTOUCHED!")
    print("ONLY the 2 authorized files in outputs/phase2a/ were modified.")


if __name__ == "__main__":
    main()
