"""Record baseline SHA-256 hashes before Stage 2HI execution."""

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
    for grp, files in groups.items():
        out_lines.append(f"=== {grp} ({len(files)} files) ===")
        for f in files:
            rel = str(f).replace("\\", "/")
            h = get_h(f)
            out_lines.append(f"{h}  {rel}")
        out_lines.append("")

    target = Path("outputs/closure/stage2hi_hashes_before.txt")
    target.write_text("\n".join(out_lines), encoding="utf-8")
    total_count = sum(len(f) for f in groups.values())
    print(f"Recorded before-hashes for {total_count} files into {target}")
    print(f"src files: {len(groups['src'])}")
    print(f"tests files: {len(groups['tests'])}")
    print(f"outputs/phase2a files: {len(groups['outputs/phase2a'])}")
    print(f"raw mat files: {len(groups['raw_mat'])}")


if __name__ == "__main__":
    main()
