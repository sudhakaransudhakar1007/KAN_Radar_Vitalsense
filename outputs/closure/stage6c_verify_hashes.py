"""
Verification of tracked files hashes before vs after Stage 6C.
Author: Antigravity Assistant (Stage 6C)
"""
import hashlib
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
    before_file = repo_root / "outputs/closure/stage6c_hashes_before.txt"
    after_file = repo_root / "outputs/closure/stage6c_hashes_after.txt"
    
    assert before_file.exists(), "stage6c_hashes_before.txt not found!"
    
    before_hashes = {}
    with open(before_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("==="):
                continue
            parts = line.split("  ")
            if len(parts) == 2:
                h, p = parts
                before_hashes[p.strip()] = h.strip().lower()
                
    after_lines = []
    after_hashes = {}
    
    # 1. src
    after_lines.append(f"=== src ({len([k for k in before_hashes if k.startswith('kan_radar_HR/src/')])} files) ===")
    src_files = sorted(list((repo_root / "src").rglob("*.py")))
    for sf in src_files:
        rel = str(sf.relative_to(workspace_root)).replace("\\", "/")
        h = compute_sha256(sf)
        after_hashes[rel] = h
        after_lines.append(f"{h}  {rel}")
        
    # 2. tests
    after_lines.append(f"\n=== tests ({len([k for k in before_hashes if k.startswith('kan_radar_HR/tests/')])} files) ===")
    test_files = sorted(list((repo_root / "tests").rglob("*.py")))
    for tf in test_files:
        rel = str(tf.relative_to(workspace_root)).replace("\\", "/")
        h = compute_sha256(tf)
        after_hashes[rel] = h
        after_lines.append(f"{h}  {rel}")
        
    # 3. outputs/phase2a
    after_lines.append(f"\n=== outputs/phase2a ({len([k for k in before_hashes if k.startswith('kan_radar_HR/outputs/phase2a/')])} files) ===")
    phase2a_files = sorted(list((repo_root / "outputs/phase2a").glob("*.*")))
    for pf in phase2a_files:
        rel = str(pf.relative_to(workspace_root)).replace("\\", "/")
        h = compute_sha256(pf)
        after_hashes[rel] = h
        after_lines.append(f"{h}  {rel}")
        
    # 4. raw_mat
    raw_dir = workspace_root / "data/VITALSENSE_120_DATASET"
    if not raw_dir.exists():
        raw_dir = repo_root / "data/VITALSENSE_120_DATASET"
    raw_files = sorted(list(raw_dir.glob("*/*.mat")))
    after_lines.append(f"\n=== raw_mat ({len(raw_files)} files) ===")
    for rf in raw_files:
        rel = str(rf.relative_to(workspace_root)).replace("\\", "/")
        h = compute_sha256(rf)
        after_hashes[rel] = h
        after_lines.append(f"{h}  {rel}")
        
    # 5. run_001
    run001_dir = repo_root / "outputs/supervised_dataset/run_001"
    run001_files = sorted(list(run001_dir.glob("*.csv")))
    after_lines.append(f"\n=== run_001 ({len(run001_files)} files) ===")
    for rf in run001_files:
        rel = str(rf.relative_to(workspace_root)).replace("\\", "/")
        h = compute_sha256(rf)
        after_hashes[rel] = h
        after_lines.append(f"{h}  {rel}")
        
    # 6. spec
    spec_f = repo_root / "outputs/closure/spec/label_spec_v1.json"
    after_lines.append("\n=== spec (1 file) ===")
    rel = str(spec_f.relative_to(workspace_root)).replace("\\", "/")
    h = compute_sha256(spec_f)
    after_hashes[rel] = h
    after_lines.append(f"{h}  {rel}")
    
    after_file.write_text("\n".join(after_lines) + "\n", encoding="utf-8")
    print(f"Written {after_file} ({len(after_hashes)} tracked files).")
    
    # Compare
    mismatches = []
    missing_in_after = []
    for p, h_before in before_hashes.items():
        if p not in after_hashes:
            missing_in_after.append(p)
        elif after_hashes[p] != h_before:
            mismatches.append((p, h_before, after_hashes[p]))
            
    print(f"Comparison Result:")
    print(f"Total files compared: {len(before_hashes)}")
    print(f"Matching files:       {len(before_hashes) - len(mismatches) - len(missing_in_after)}")
    print(f"Mismatches:           {len(mismatches)}")
    print(f"Missing in after:     {len(missing_in_after)}")
    
    if mismatches:
        for p, hb, ha in mismatches:
            print(f"  MISMATCH: {p}\n    before: {hb}\n    after:  {ha}")
    else:
        print("PERFECT MATCH: Exactly 0 tracked files were modified during Stage 6C!")

if __name__ == "__main__":
    main()
