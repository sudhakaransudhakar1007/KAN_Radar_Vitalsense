"""
Stage 7A E5: phase2a inventory and project-wide search for missing files.
Author: Antigravity Assistant (Stage 7A)
"""
import hashlib
import csv
import re
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
workspace_root = repo_root.parent
phase2a_dir = repo_root / "outputs/phase2a"
inventory_csv_path = repo_root / "outputs/closure/phase2a_inventory.csv"

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def main():
    print("=== E5. Phase 2A Inventory & Project-Wide Search ===")
    
    # 1. Real files in outputs/phase2a
    real_files = sorted([f for f in phase2a_dir.iterdir() if f.is_file()])
    print(f"Discovered {len(real_files)} real files in {phase2a_dir}:")
    
    inventory_rows = []
    for f in real_files:
        sz = f.stat().st_size
        h = compute_sha256(f)
        inventory_rows.append({"name": f.name, "size": sz, "sha256": h})
        print(f"  - {f.name} ({sz} bytes, sha256={h[:16]}...)")
        
    with open(inventory_csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=["name", "size", "sha256"])
        writer.writeheader()
        writer.writerows(inventory_rows)
        
    print(f"\nWritten phase2a inventory to: {inventory_csv_path} ({inventory_csv_path.stat().st_size} bytes)")
    
    # 2. Project-wide search for the 3 target files
    target_names = [
        "step2b_gate_decision.md",
        "sync_status_inventory.csv",
        "sync_validation_summary.json"
    ]
    
    print("\n--- Physical File Existence Check ---")
    for target in target_names:
        matches = list(workspace_root.rglob(target))
        if matches:
            print(f"Target '{target}': FOUND ({len(matches)} occurrences):")
            for m in matches:
                print(f"  {m}")
        else:
            print(f"Target '{target}': NOT FOUND as physical file on disk anywhere in workspace.")
            
    print("\n--- Text Reference Search across Codebase ---")
    # Search all text files in repo for references to these target filenames
    text_extensions = {".py", ".md", ".txt", ".csv", ".json", ".html", ".js", ".css"}
    hits = {target: [] for target in target_names}
    
    for p in workspace_root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in text_extensions:
            continue
        # Skip git / pycache / pytest_cache
        if any(skip in p.parts for skip in [".git", "__pycache__", ".pytest_cache"]):
            continue
            
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        rel_p = str(p.relative_to(workspace_root)).replace("\\", "/")
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            line_no = idx + 1
            for target in target_names:
                if target in line:
                    hits[target].append((rel_p, line_no, line.strip()))
                    
    for target in target_names:
        target_hits = hits[target]
        print(f"\nReferences to '{target}' ({len(target_hits)} hits):")
        if target_hits:
            for rel_p, l_no, text in target_hits[:15]:  # show first 15 if many
                print(f"  {rel_p}:{l_no}: {text}")
            if len(target_hits) > 15:
                print(f"  ... and {len(target_hits) - 15} more references.")
        else:
            print("  No text references found.")

if __name__ == "__main__":
    main()
