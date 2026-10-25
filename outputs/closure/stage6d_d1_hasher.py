"""
Stage 6D Hasher: Hashes all tracked files including all 12 run_001 files.
Author: Antigravity Assistant (Stage 6D)
"""
import hashlib
import os
from pathlib import Path
from collections import defaultdict

repo_root = Path(__file__).resolve().parents[2]
workspace_root = repo_root.parent

def compute_sha256_and_size(filepath: Path):
    h = hashlib.sha256()
    size = filepath.stat().st_size
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower(), size

def main(output_filename="stage6d_hashes_before.txt"):
    categories = {}
    
    # 1. data/ (raw .mat)
    data_dir = workspace_root / "data/VITALSENSE_120_DATASET"
    if not data_dir.exists():
        data_dir = repo_root / "data/VITALSENSE_120_DATASET"
    raw_files = sorted(list(data_dir.glob("*/*.mat")))
    categories["data (raw .mat)"] = raw_files
    
    # 2. src/
    src_files = sorted([f for f in (repo_root / "src").rglob("*.py") if "__pycache__" not in str(f)])
    categories["src"] = src_files
    
    # 3. tests/
    test_files = sorted([f for f in (repo_root / "tests").rglob("*.py") if "__pycache__" not in str(f)])
    categories["tests"] = test_files
    
    # 4. outputs/phase2a/
    phase2a_files = sorted([f for f in (repo_root / "outputs/phase2a").glob("*.*") if f.is_file()])
    categories["outputs/phase2a"] = phase2a_files
    
    # 5. outputs/supervised_dataset/ (all 12 files of run_001)
    run001_dir = repo_root / "outputs/supervised_dataset/run_001"
    run001_files = sorted([f for f in run001_dir.glob("*.*") if f.is_file()])
    categories["outputs/supervised_dataset/run_001"] = run001_files
    
    # 6. outputs/closure/spec/
    spec_dir = repo_root / "outputs/closure/spec"
    spec_files = sorted([f for f in spec_dir.glob("*.*") if f.is_file() and "__pycache__" not in str(f)])
    categories["outputs/closure/spec"] = spec_files
    
    output_lines = []
    all_entries = []
    hash_to_paths = defaultdict(list)
    
    total_files = 0
    print(f"=== Hashing Summary for {output_filename} ===")
    for cat, files in categories.items():
        print(f"Category '{cat}': {len(files)} files")
        output_lines.append(f"=== {cat} ({len(files)} files) ===")
        total_files += len(files)
        for f in files:
            sha, sz = compute_sha256_and_size(f)
            rel_p = str(f.relative_to(workspace_root)).replace("\\", "/")
            output_lines.append(f"{sha}  {sz}  {rel_p}")
            all_entries.append((sha, sz, rel_p))
            hash_to_paths[sha].append(rel_p)
        output_lines.append("")
        
    out_path = repo_root / "outputs/closure" / output_filename
    out_path.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Total files hashed: {total_files}")
    print(f"Output written to: {out_path} ({out_path.stat().st_size} bytes)")
    
    # Check for duplicates
    dups = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}
    print(f"Total unique hashes: {len(hash_to_paths)}")
    print(f"Duplicate hash count: {len(dups)}")
    if dups:
        for h, paths in dups.items():
            print(f"Duplicate hash {h} shared by {len(paths)} files:")
            for p in paths:
                print(f"  {p}")
    else:
        print("No duplicate hashes found.")

if __name__ == "__main__":
    main()
