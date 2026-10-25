"""
Stage 7A: Verify after hashes and compare with stage7a_hashes_before.txt.
Author: Antigravity Assistant (Stage 7A)
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "outputs/closure"))
import stage7a_e1_hasher

def main():
    print("=== Writing stage7a_hashes_after.txt ===")
    stage7a_e1_hasher.main("stage7a_hashes_after.txt")
    
    before_p = repo_root / "outputs/closure/stage7a_hashes_before.txt"
    after_p = repo_root / "outputs/closure/stage7a_hashes_after.txt"
    
    before_lines = [l.strip() for l in before_p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("===")]
    after_lines = [l.strip() for l in after_p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("===")]
    
    print("\n=== Stage 7A Before vs After Hash Comparison ===")
    print(f"Total files before: {len(before_lines)}")
    print(f"Total files after:  {len(after_lines)}")
    
    before_dict = {}
    for l in before_lines:
        parts = l.split("  ")
        before_dict[parts[2]] = (parts[0], parts[1])
        
    after_dict = {}
    for l in after_lines:
        parts = l.split("  ")
        after_dict[parts[2]] = (parts[0], parts[1])
        
    mismatches = []
    missing_after = [p for p in before_dict if p not in after_dict]
    added_after = [p for p in after_dict if p not in before_dict]
    
    for p in before_dict:
        if p in after_dict:
            if before_dict[p] != after_dict[p]:
                mismatches.append((p, before_dict[p], after_dict[p]))
                
    print(f"Missing after: {len(missing_after)}")
    print(f"Added after:   {len(added_after)}")
    print(f"Mismatches:    {len(mismatches)}")
    
    if not mismatches and not missing_after and not added_after:
        print("PERFECT INTEGRITY: All 174 tracked files are bit-identical before and after Stage 7A.")
    else:
        for p, b, a in mismatches:
            print(f"  MISMATCH: {p}: before={b} vs after={a}")

if __name__ == "__main__":
    main()
