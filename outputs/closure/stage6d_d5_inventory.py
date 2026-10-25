"""
Stage 6D D5: Generate outputs/closure/run_001_inventory.csv.
Author: Antigravity Assistant (Stage 6D)
"""
import hashlib
import csv
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
workspace_root = repo_root.parent

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def main():
    run001_dir = repo_root / "outputs/supervised_dataset/run_001"
    files = sorted(list(run001_dir.glob("*.*")))
    
    three_manifests = {
        "accepted_window_manifest.csv",
        "candidate_window_manifest.csv",
        "rejected_window_manifest.csv"
    }
    
    rows = []
    not_covered = []
    
    for f in files:
        sha = compute_sha256(f)
        size = f.stat().st_size
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
        rel_path = str(f.relative_to(workspace_root)).replace("\\", "/")
        is_covered = f.name in three_manifests
        if not is_covered:
            not_covered.append(f.name)
            
        rows.append({
            "filename": f.name,
            "path": rel_path,
            "size_bytes": size,
            "mtime_utc": mtime,
            "sha256": sha,
            "covered_by_3_manifests": "YES" if is_covered else "NO"
        })
        
    out_csv = repo_root / "outputs/closure/run_001_inventory.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["filename", "path", "size_bytes", "mtime_utc", "sha256", "covered_by_3_manifests"])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Written {len(rows)} files to {out_csv}")
    print(f"Files in run_001: {len(rows)}")
    print(f"Covered by 3 manifests: {len(rows) - len(not_covered)}")
    print(f"NOT covered by 3 manifests ({len(not_covered)} files):")
    for fn in not_covered:
        print(f"  - {fn}")

if __name__ == "__main__":
    main()
