"""
R3 Audit Script: Project-wide search for specific patterns and provenance verification.
Author: Antigravity Assistant (Stage 6C)
"""
import os
import re
from pathlib import Path

def main():
    script_path = Path(__file__).resolve()
    # kan_radar_HR directory
    repo_root = script_path.parents[2]
    # Workspace root (contains data/, kan_radar_HR/, integrity_baseline_2026-10-15.txt)
    workspace_root = repo_root.parent
    
    extensions = ('.md', '.py', '.csv', '.json', '.txt', '.yaml', '.log')
    patterns_b2 = [r'HoldingBreath', r'Talking', r'Walking']
    regex_b2 = re.compile('|'.join(patterns_b2), re.IGNORECASE)
    
    extra_patterns = [
        '0.237',
        '1.760',
        '84%',
        'VS11',
        'VS04_Holding',
        'transient sinus arrhythmia'
    ]
    
    output_lines = []
    output_lines.append("=== STAGE 6C R3 SEARCH RESULTS ===")
    output_lines.append(f"Script: {script_path}")
    output_lines.append(f"Workspace root: {workspace_root}")
    output_lines.append(f"Regex B2: {regex_b2.pattern}")
    output_lines.append(f"Extensions searched: {extensions}")
    output_lines.append("")
    
    # 1. Search whole project excluding raw data for B2 patterns
    files_searched_b2 = 0
    hits_b2 = []
    
    # Search from workspace_root
    for root, dirs, files in os.walk(workspace_root):
        # Exclude raw data, .git, and gemini logs
        if any(ex in root for ex in ['data', '.git', '.system_generated', '__pycache__', '.pytest_cache']):
            continue
        for f in files:
            if f.endswith(extensions):
                p = Path(root) / f
                # Skip the search script itself and its output
                if p.name in ['stage6c_r3_search.py', 'stage6c_r3_output.txt']:
                    continue
                files_searched_b2 += 1
                try:
                    # Try utf-8 first, fallback to utf-16 or ignore
                    try:
                        content = p.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            content = p.read_text(encoding='utf-16')
                        except Exception:
                            content = p.read_text(encoding='utf-8', errors='ignore')
                    for i, line in enumerate(content.splitlines()):
                        if regex_b2.search(line):
                            rel_p = str(p.relative_to(workspace_root)).replace('\\', '/')
                            hits_b2.append((rel_p, i + 1, line.strip()))
                except Exception as e:
                    pass
    
    output_lines.append("=== 1. B2 Pattern Search (Whole Project excluding raw data) ===")
    output_lines.append(f"Total files searched: {files_searched_b2}")
    output_lines.append(f"Total matches found: {len(hits_b2)}")
    if hits_b2:
        for p, line_no, text in hits_b2:
            output_lines.append(f"  {p}:{line_no}: {text[:100]}")
    else:
        output_lines.append("  NONE (0 matches)")
    output_lines.append("")
    
    # 2. Search outputs/closure, src, tests for extra strings
    target_dirs = [
        repo_root / "outputs/closure",
        repo_root / "src",
        repo_root / "tests"
    ]
    extra_hits = {pat: [] for pat in extra_patterns}
    extra_files_count = 0
    
    for t_dir in target_dirs:
        for root, dirs, files in os.walk(t_dir):
            if any(ex in root for ex in ['__pycache__', '.pytest_cache']):
                continue
            for f in files:
                if f.endswith(extensions):
                    p = Path(root) / f
                    if p.name in ['stage6c_r3_search.py', 'stage6c_r3_output.txt']:
                        continue
                    extra_files_count += 1
                    try:
                        try:
                            content = p.read_text(encoding='utf-8')
                        except UnicodeDecodeError:
                            content = p.read_text(encoding='utf-8', errors='ignore')
                        for i, line in enumerate(content.splitlines()):
                            for pat in extra_patterns:
                                if pat in line:
                                    rel_p = str(p.relative_to(workspace_root)).replace('\\', '/')
                                    extra_hits[pat].append((rel_p, i + 1, line.strip()))
                    except Exception:
                        pass
                        
    output_lines.append("=== 2. Extra Strings Search (outputs/closure, src, tests) ===")
    output_lines.append(f"Total files searched in target dirs: {extra_files_count}")
    for pat, matches in extra_hits.items():
        output_lines.append(f"\nPattern '{pat}': {len(matches)} match(es)")
        for p, line_no, text in matches:
            output_lines.append(f"  {p}:{line_no}: {text[:120]}")
            
    out_file = repo_root / "outputs/closure/stage6c_r3_output.txt"
    out_file.write_text("\n".join(output_lines), encoding='utf-8')
    print(f"Written {len(output_lines)} lines to {out_file}")

if __name__ == "__main__":
    main()
