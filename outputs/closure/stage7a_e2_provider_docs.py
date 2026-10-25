"""
Stage 7A E2: Provider Documents Analysis using standard library zipfile.
Author: Antigravity Assistant (Stage 7A)
"""
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
workspace_root = repo_root.parent

def analyze_text_file(filepath: Path, slice_size=80):
    total_bytes = filepath.stat().st_size
    text = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    total_lines = len(lines)
    
    print(f"\n==========================================")
    print(f"File: {filepath.name} ({total_bytes} bytes, {total_lines} lines)")
    print(f"==========================================")
    
    slices = []
    for start in range(0, total_lines, slice_size):
        end = min(start + slice_size, total_lines)
        slices.append((start + 1, end))
        print(f"Reading slice: lines {start+1} - {end} ({end - start} lines)")
        
    keywords = [
        "sync", "synchron", "trigger", "clock", "timestamp", "sampling",
        "offset", "delay", "latency", "mindray", "monitor", "exclusion",
        "quality", "known issue", "apnea", "respiration"
    ]
    pattern = re.compile(r"\b(" + "|".join(keywords) + r")\b", re.IGNORECASE)
    
    matching_lines = []
    for i, line in enumerate(lines):
        line_no = i + 1
        if pattern.search(line):
            matching_lines.append((line_no, line.strip()))
            
    print(f"\nLines matching keywords in {filepath.name} ({len(matching_lines)} matches):")
    for l_no, text_line in matching_lines:
        print(f"  {l_no:3d}: {text_line}")
        
    return text, lines

def parse_xlsx_sheets(filepath: Path):
    print(f"\n==========================================")
    print(f"File: {filepath.name} ({filepath.stat().st_size} bytes)")
    print(f"==========================================")
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    
    with zipfile.ZipFile(filepath, 'r') as z:
        # 1. Sheet names
        wb_xml = z.read('xl/workbook.xml')
        wb_root = ET.fromstring(wb_xml)
        sheets = [s.attrib['name'] for s in wb_root.iter(f'{ns}sheet')]
        print(f"Sheet names ({len(sheets)}): {sheets}")
        
        # 2. Shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml')
            ss_root = ET.fromstring(ss_xml)
            for si in ss_root.iter(f'{ns}si'):
                text = ''.join(t.text for t in si.iter(f'{ns}t') if t.text)
                shared_strings.append(text)
                
        # 3. For each sheet, parse rows
        for idx, sheet_name in enumerate(sheets):
            sheet_file = f'xl/worksheets/sheet{idx+1}.xml'
            if sheet_file not in z.namelist():
                continue
            s_xml = z.read(sheet_file)
            s_root = ET.fromstring(s_xml)
            
            rows = []
            for r in s_root.iter(f'{ns}row'):
                row_vals = []
                for c in r.iter(f'{ns}c'):
                    val = ""
                    t_attr = c.attrib.get('t')
                    v_elem = c.find(f'{ns}v')
                    if v_elem is not None and v_elem.text:
                        v_text = v_elem.text
                        if t_attr == 's' and v_text.isdigit():
                            s_idx = int(v_text)
                            val = shared_strings[s_idx] if s_idx < len(shared_strings) else v_text
                        else:
                            val = v_text
                    row_vals.append(val)
                rows.append(row_vals)
                
            print(f"\nSheet '{sheet_name}' (Total rows: {len(rows)}):")
            if rows:
                headers = rows[0]
                print(f"  Header row ({len(headers)} columns): {headers}")
                # Search all cells in this sheet for keywords
                sheet_text = " ".join(" ".join(r) for r in rows)
                for kw in ["exclusion", "quality", "note", "comment", "flag", "drop", "anomal", "issue", "clock", "sync", "trigger", "delay", "latency", "vs10", "vs24", "256", "333"]:
                    if kw in sheet_text.lower():
                        print(f"  * Keyword '{kw}' appears in sheet '{sheet_name}'")
                        for r_idx, r in enumerate(rows):
                            row_str = " | ".join(r)
                            if kw in row_str.lower():
                                print(f"    Row {r_idx+1}: {row_str}")

def main():
    data_dir = workspace_root / "data/VITALSENSE_120_DATASET"
    manifest_p = data_dir / "MANIFEST.TXT"
    readme_p = data_dir / "README.txt"
    excel_p = data_dir / "Subject Information.xlsx"
    
    analyze_text_file(manifest_p, slice_size=100)
    analyze_text_file(readme_p, slice_size=80)
    parse_xlsx_sheets(excel_p)

if __name__ == "__main__":
    main()
