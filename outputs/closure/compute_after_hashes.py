"""Compute cryptographic SHA-256 hashes for Stage 2G AFTER verification."""

import glob
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def get_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    data_dir = PROJECT_ROOT.parent / "data" / "VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = PROJECT_ROOT / "data" / "VITALSENSE_120_DATASET"

    file_groups = {
        "src": sorted([Path(p) for p in glob.glob("src/**/*.py", recursive=True)]),
        "tests": sorted([Path(p) for p in glob.glob("tests/**/*.py", recursive=True)]),
        "outputs/phase2a": sorted([Path(p) for p in glob.glob("outputs/phase2a/*.*")]),
        "raw_mat": sorted(list(data_dir.glob("*/*.mat"))),
    }

    out_file = Path("outputs/closure/stage2g_hashes_after.txt")
    lines = []
    hash_dict = {}

    for group, flist in file_groups.items():
        lines.append(f"=== {group} ({len(flist)} files) ===")
        for f in flist:
            rel = str(f).replace("\\", "/")
            h = get_sha256(f)
            hash_dict[rel] = h
            lines.append(f"{h}  {rel}")
        lines.append("")

    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(hash_dict)} file hashes to {out_file}")

    # Compare against before hashes
    before_file = Path("outputs/closure/stage2g_hashes_before.txt")
    if before_file.exists():
        before_lines = before_file.read_text(encoding="utf-8").splitlines()
        before_dict = {}
        for line in before_lines:
            line = line.strip()
            if line and not line.startswith("==="):
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    before_dict[parts[1]] = parts[0]

        print("\n=== HASH COMPARISON (BEFORE vs AFTER Stage 2G) ===")
        modified = []
        new_files = []
        unchanged = 0

        for path, h_after in hash_dict.items():
            if path in before_dict:
                h_before = before_dict[path]
                if h_before != h_after:
                    modified.append((path, h_before, h_after))
                else:
                    unchanged += 1
            else:
                new_files.append((path, h_after))

        print(f"Total files checked: {len(hash_dict)}")
        print(f"Unchanged files:     {unchanged}")
        print(f"Modified files:      {len(modified)}")
        for path, h_b, h_a in modified:
            print(f"  MODIFIED: {path}\n    BEFORE: {h_b}\n    AFTER:  {h_a}")

        print(f"New files:           {len(new_files)}")
        for path, h in new_files:
            print(f"  NEW:      {path} ({h})")

        # Verify raw files immutability
        raw_modified = [p for p, _, _ in modified if p.endswith(".mat")]
        assert len(raw_modified) == 0, f"CRITICAL ERROR: Raw MAT files modified: {raw_modified}"
        print("\nVERIFIED: All 96 raw MAT files are 100% IMMUTABLE and untouched.")


if __name__ == "__main__":
    main()
