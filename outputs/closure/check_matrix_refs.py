"""Verify code_ref and test_ref in issue_closure_matrix.csv."""

import re
from pathlib import Path
import pandas as pd


def check_ref(ref_str):
    if pd.isna(ref_str) or str(ref_str).strip() in ["NOT_APPLICABLE", "NA", ""]:
        return True, "N/A"
    parts = [p.strip() for p in str(ref_str).split(";")]
    results = []
    for part in parts:
        m = re.match(r"^([^:]+)(?::(.*))?$", part)
        if not m:
            results.append((False, f"Malformed: {part}"))
            continue
        filepath = m.group(1).strip()
        linespec = m.group(2).strip() if m.group(2) else None

        p = Path(filepath)
        if not p.exists():
            results.append((False, f"File not found: {filepath}"))
            continue

        if linespec:
            if p.is_file():
                content = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                m_num = re.match(r"^(\d+)(?:-(\d+))?$", linespec)
                if m_num:
                    l1 = int(m_num.group(1))
                    l2 = int(m_num.group(2)) if m_num.group(2) else l1
                    if 1 <= l1 <= len(content) and 1 <= l2 <= len(content):
                        # Also check if line is not empty
                        snippet = content[l1 - 1 : l2]
                        results.append((True, f"Lines {l1}-{l2} exist ({len(content)} total)"))
                    else:
                        results.append((False, f"Lines {l1}-{l2} out of range (1..{len(content)})"))
                else:
                    results.append((True, f"Spec: {linespec}"))
            else:
                results.append((True, "Directory exists"))
        else:
            results.append((True, "File exists"))

    all_pass = all(r[0] for r in results)
    detail = "; ".join(r[1] for r in results)
    return all_pass, detail


def main():
    df = pd.read_csv("outputs/closure/issue_closure_matrix.csv")
    print(f"Loaded {len(df)} rows from matrix.")
    print(f"{'Issue':<8} | {'Code Ref OK':<12} | {'Test Ref OK':<12} | {'Code Ref':<55} | {'Test Ref':<35}")
    print("-" * 135)
    for idx, row in df.iterrows():
        c_ok, c_msg = check_ref(row["code_ref"])
        t_ok, t_msg = check_ref(row["test_ref"])
        c_status = "PASS" if c_ok else "FAIL"
        t_status = "PASS" if t_ok else "FAIL"
        print(f"{row['issue_id']:<8} | {c_status:<12} | {t_status:<12} | {str(row['code_ref']):<55} | {str(row['test_ref']):<35}")
        if not c_ok:
            print(f"   -> Code error: {c_msg}")
        if not t_ok:
            print(f"   -> Test error: {t_msg}")


if __name__ == "__main__":
    main()
