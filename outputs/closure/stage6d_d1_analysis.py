"""
Stage 6D D1(a) Analysis: Read stage6c_hashes_before.txt and stage6c_hashes_after.txt in slices.
Author: Antigravity Assistant (Stage 6D)
"""
from pathlib import Path
from collections import defaultdict

repo_root = Path(__file__).resolve().parents[2]

def read_in_slices(filepath: Path, slice_size: int = 80):
    total_bytes = filepath.stat().st_size
    lines = filepath.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    
    slices = []
    for start in range(0, total_lines, slice_size):
        end = min(start + slice_size, total_lines)
        slice_lines = lines[start:end]
        slices.append((start + 1, end, slice_lines))
    return total_bytes, total_lines, slices, lines

def analyze_file(filepath: Path):
    total_bytes, total_lines, slices, lines = read_in_slices(filepath)
    print(f"\n--- Analysis of {filepath.name} ---")
    print(f"Total size: {total_bytes} bytes | Total lines: {total_lines}")
    for start, end, s_lines in slices:
        print(f"  Read slice lines {start}-{end} ({len(s_lines)} lines)")
        
    has_dataset_summary = any("dataset_summary.json" in l for l in lines)
    has_candidate_manifest = any("candidate_window_manifest.csv" in l for l in lines)
    
    print(f"Contains 'dataset_summary.json': {has_dataset_summary}")
    print(f"Contains 'candidate_window_manifest.csv': {has_candidate_manifest}")
    
    # Check duplicate hashes
    hashes = defaultdict(list)
    for l in lines:
        l = l.strip()
        if not l or l.startswith("==="):
            continue
        parts = l.split("  ")
        if len(parts) == 2:
            h, p = parts
            hashes[h].append(p)
            
    dups = {h: p for h, p in hashes.items() if len(p) > 1}
    print(f"Total unique file entries: {sum(len(p) for p in hashes.values())}")
    print(f"Total unique hash values: {len(hashes)}")
    print(f"Duplicate hash count: {len(dups)}")
    if dups:
        for h, p in dups.items():
            print(f"  Duplicate hash {h} across: {p}")
            
    print(f"First 3 lines:")
    for l in lines[:3]:
        print(f"  {l}")
    print(f"Last 3 lines:")
    for l in lines[-3:]:
        print(f"  {l}")

def main():
    f_before = repo_root / "outputs/closure/stage6c_hashes_before.txt"
    f_after = repo_root / "outputs/closure/stage6c_hashes_after.txt"
    
    analyze_file(f_before)
    analyze_file(f_after)

if __name__ == "__main__":
    main()
