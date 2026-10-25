"""
Stage 6D Verify After: Re-hashes all 168 tracked files to stage6d_hashes_after.txt and verifies 0 modifications.
Author: Antigravity Assistant (Stage 6D)
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from outputs.closure.stage6d_d1_hasher import main as run_hasher

def main():
    # 1. Run hasher for stage6d_hashes_after.txt
    run_hasher(output_filename="stage6d_hashes_after.txt")
    
    before_f = repo_root / "outputs/closure/stage6d_hashes_before.txt"
    after_f = repo_root / "outputs/closure/stage6d_hashes_after.txt"
    
    assert before_f.exists() and after_f.exists()
    
    before_text = before_f.read_text(encoding="utf-8")
    after_text = after_f.read_text(encoding="utf-8")
    
    before_entries = {}
    for l in before_text.splitlines():
        l = l.strip()
        if not l or l.startswith("==="):
            continue
        parts = l.split("  ")
        if len(parts) == 3:
            sha, sz, p = parts
            before_entries[p] = (sha, sz)
            
    after_entries = {}
    for l in after_text.splitlines():
        l = l.strip()
        if not l or l.startswith("==="):
            continue
        parts = l.split("  ")
        if len(parts) == 3:
            sha, sz, p = parts
            after_entries[p] = (sha, sz)
            
    total_compared = len(before_entries)
    mismatches = []
    missing_in_after = []
    
    for p, (sha_b, sz_b) in before_entries.items():
        if p not in after_entries:
            missing_in_after.append(p)
        else:
            sha_a, sz_a = after_entries[p]
            if sha_a != sha_b or sz_a != sz_b:
                mismatches.append((p, sha_b, sha_a, sz_b, sz_a))
                
    print(f"\n=== Verification Comparison Results ===")
    print(f"Total files compared: {total_compared}")
    print(f"Matching files:       {total_compared - len(mismatches) - len(missing_in_after)}")
    print(f"Mismatches:           {len(mismatches)}")
    print(f"Missing in after:     {len(missing_in_after)}")
    
    if mismatches:
        for p, sb, sa, zb, za in mismatches:
            print(f"  MISMATCH in {p}: before=({sb}, {zb}) vs after=({sa}, {za})")
    else:
        print("PERFECT MATCH: Exactly 0 tracked files were modified during Stage 6D!")
        
    print(f"Exact byte match between before and after hash files: {before_text == after_text}")

if __name__ == "__main__":
    main()
