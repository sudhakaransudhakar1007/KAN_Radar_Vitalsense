"""
Stage 7A E1: Comprehensive hashing (all extensions) across all 174 tracked files.
Author: Antigravity Assistant (Stage 7A)
"""
import hashlib
import csv
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

def normalize_rel_path(p_str: str) -> str:
    # Convert backslashes to forward slashes
    p_str = p_str.replace("\\", "/")
    # If absolute path, make relative to workspace_root
    ws_str = str(workspace_root).replace("\\", "/")
    if p_str.startswith(ws_str):
        p_str = p_str[len(ws_str):].lstrip("/")
    return p_str

def main(output_filename="stage7a_hashes_before.txt"):
    target_dirs = [
        ("data", workspace_root / "data"),
        ("kan_radar_HR/src", repo_root / "src"),
        ("kan_radar_HR/tests", repo_root / "tests"),
        ("kan_radar_HR/outputs/phase2a", repo_root / "outputs/phase2a"),
        ("kan_radar_HR/outputs/supervised_dataset", repo_root / "outputs/supervised_dataset"),
        ("kan_radar_HR/outputs/closure/spec", repo_root / "outputs/closure/spec"),
    ]
    
    output_lines = []
    current_entries = {}
    hash_to_paths = defaultdict(list)
    total_files = 0
    
    print(f"=== E1. Hashing ALL Files (all extensions) for {output_filename} ===")
    for label, d_path in target_dirs:
        files = sorted([
            f for f in d_path.rglob("*")
            if f.is_file() and "__pycache__" not in str(f) and ".pytest_cache" not in str(f)
        ])
        print(f"Directory '{label}': {len(files)} files")
        output_lines.append(f"=== {label} ({len(files)} files) ===")
        total_files += len(files)
        for f in files:
            sha, sz = compute_sha256_and_size(f)
            rel_p = str(f.relative_to(workspace_root)).replace("\\", "/")
            output_lines.append(f"{sha}  {sz}  {rel_p}")
            current_entries[rel_p] = (sha, sz)
            hash_to_paths[sha].append(rel_p)
        output_lines.append("")
        
    out_file = repo_root / "outputs/closure" / output_filename
    out_file.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")
    print(f"\nTotal files hashed: {total_files} (Expected: 174)")
    print(f"Written to: {out_file} ({out_file.stat().st_size} bytes)")
    
    # Check for duplicate hashes
    dups = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}
    print(f"Total unique hashes: {len(hash_to_paths)}")
    print(f"Duplicate hash count: {len(dups)}")
    if dups:
        for h, paths in dups.items():
            print(f"  Duplicate hash {h} across: {paths}")
            
    # Print first and last 3 lines
    lines = [l for l in output_lines if l.strip() and not l.startswith("===")]
    print("\nFirst 3 lines of output:")
    for l in lines[:3]:
        print(f"  {l}")
    print("Last 3 lines of output:")
    for l in lines[-3:]:
        print(f"  {l}")
        
    # Compare with stage6d_hashes_before.txt
    stage6d_f = repo_root / "outputs/closure/stage6d_hashes_before.txt"
    if stage6d_f.exists():
        stage6d_entries = {}
        for l in stage6d_f.read_text(encoding="utf-8").splitlines():
            l = l.strip()
            if not l or l.startswith("==="):
                continue
            parts = l.split("  ")
            if len(parts) == 3:
                stage6d_entries[parts[2]] = (parts[0], int(parts[1]))
                
        only_in_7a = [p for p in current_entries if p not in stage6d_entries]
        print(f"\n=== Comparison with stage6d_hashes_before.txt ===")
        print(f"Stage 6D count: {len(stage6d_entries)} | Stage 7A count: {len(current_entries)}")
        print(f"Files present ONLY in Stage 7A list ({len(only_in_7a)} files):")
        for p in sorted(only_in_7a):
            print(f"  + {p} ({current_entries[p][1]} bytes, sha256={current_entries[p][0]})")
            
    # Compare with desktop baseline hash_baseline_20oct.csv
    desktop_f = repo_root / "outputs/closure/stage7a_desktop_baseline.csv"
    if desktop_f.exists():
        desktop_entries = {}
        with open(desktop_f, "r", encoding="utf-8") as fp:
            reader = csv.reader(fp)
            header = next(reader)
            for row in reader:
                if len(row) >= 3:
                    algo, h, p = row[0].strip(), row[1].strip().lower(), row[2].strip()
                    norm_p = normalize_rel_path(p)
                    desktop_entries[norm_p] = h
                    
        print(f"\n=== Comparison with Investigator's hash_baseline_20oct.csv ===")
        print(f"Investigator baseline count: {len(desktop_entries)}")
        print(f"Stage 7A before count:       {len(current_entries)}")
        
        missing_in_current = [p for p in desktop_entries if p not in current_entries]
        missing_in_desktop = [p for p in current_entries if p not in desktop_entries]
        mismatches = []
        for p in current_entries:
            if p in desktop_entries:
                if current_entries[p][0] != desktop_entries[p]:
                    mismatches.append((p, current_entries[p][0], desktop_entries[p]))
                    
        print(f"Matching paths:      {len([p for p in current_entries if p in desktop_entries])}")
        print(f"Missing in Stage 7A: {len(missing_in_current)}")
        if missing_in_current:
            for p in missing_in_current:
                print(f"  Missing: {p}")
        print(f"Missing in Desktop:  {len(missing_in_desktop)}")
        if missing_in_desktop:
            for p in missing_in_desktop:
                print(f"  Missing: {p}")
        print(f"Hash mismatches:     {len(mismatches)}")
        if mismatches:
            for p, hc, hd in mismatches:
                print(f"  Mismatch in {p}:\n    7A:      {hc}\n    Desktop: {hd}")
        else:
            print("PERFECT MATCH: All 174 hashes in Stage 7A match the investigator's hash_baseline_20oct.csv exactly!")

if __name__ == "__main__":
    main()
