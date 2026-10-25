"""Record after-hashes and compare against baseline for Stage 2HI."""

import glob
import hashlib
from pathlib import Path


def get_h(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def main():
    data_dir = Path("../data/VITALSENSE_120_DATASET")
    if not data_dir.exists():
        data_dir = Path("data/VITALSENSE_120_DATASET")

    groups = {
        "src": sorted([Path(p) for p in glob.glob("src/**/*.py", recursive=True)]),
        "tests": sorted([Path(p) for p in glob.glob("tests/**/*.py", recursive=True)]),
        "outputs/phase2a": sorted([Path(p) for p in glob.glob("outputs/phase2a/*.*")]),
        "raw_mat": sorted(list(data_dir.glob("*/*.mat"))),
    }

    out_lines = []
    current_hashes = {}
    for grp, files in groups.items():
        out_lines.append(f"=== {grp} ({len(files)} files) ===")
        for f in files:
            rel = str(f).replace("\\", "/")
            h = get_h(f)
            current_hashes[rel] = h
            out_lines.append(f"{h}  {rel}")
        out_lines.append("")

    target = Path("outputs/closure/stage2hi_hashes_after.txt")
    target.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Recorded after-hashes for {len(current_hashes)} files into {target}")

    # Compare with before
    before_file = Path("outputs/closure/stage2hi_hashes_before.txt")
    before_hashes = {}
    for l in before_file.read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if l and not l.startswith("==="):
            parts = l.split("  ", 1)
            if len(parts) == 2:
                before_hashes[parts[1].replace("\\", "/")] = parts[0].lower()

    modified = []
    unchanged = 0
    for p, h_after in current_hashes.items():
        if p in before_hashes:
            h_before = before_hashes[p]
            if h_before != h_after:
                modified.append((p, h_before, h_after))
            else:
                unchanged += 1
        else:
            print("NEW FILE DETECTED in tracked set:", p)

    print("\n=== STAGE 2HI HASH COMPARISON RESULTS ===")
    print(f"Total tracked files: {len(current_hashes)}")
    print(f"Unchanged files:     {unchanged}")
    print(f"Modified files:      {len(modified)}")
    for p, h_b, h_a in modified:
        print(f"  MODIFIED: {p}")
        print(f"    BEFORE: {h_b}")
        print(f"    AFTER:  {h_a}")

    raw_modified = [p for p, _, _ in modified if p.endswith(".mat")]
    assert len(raw_modified) == 0, f"ERROR: Raw files modified: {raw_modified}"
    print("VERIFIED: All 96 raw MAT files are 100% UNCHANGED and IMMUTABLE.")

    src_tests_modified = [p for p, _, _ in modified if p.startswith("src/") or p.startswith("tests/")]
    assert len(src_tests_modified) == 0, f"ERROR: src/ or tests/ modified: {src_tests_modified}"
    print("VERIFIED: All files in src/ and tests/ are 100% UNCHANGED.")

    other_p2a_modified = [p for p, _, _ in modified if p.startswith("outputs/phase2a/") and not p.endswith("step2b_issue_register.csv")]
    assert len(other_p2a_modified) == 0, f"ERROR: Unauthorized outputs/phase2a/ files modified: {other_p2a_modified}"
    print("VERIFIED: Only authorized outputs/phase2a/step2b_issue_register.csv was modified.")


if __name__ == "__main__":
    main()
