"""
Stage 6D D2: Decision list numbering and baseline recomputed value update.
Author: Antigravity Assistant (Stage 6D)
"""
import hashlib
import shutil
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

def main():
    dec_file = repo_root / "outputs/closure/pi_decision_list.md"
    backup_file = repo_root / "outputs/closure/pi_decision_list_before_6d.md"
    
    # 1. Copy unchanged to pi_decision_list_before_6d.md
    shutil.copy2(dec_file, backup_file)
    sha_backup = compute_sha256(backup_file)
    print(f"Copied unchanged {dec_file.name} to {backup_file.name}")
    print(f"SHA-256 of {backup_file.name}: {sha_backup} ({backup_file.stat().st_size} bytes)")
    
    orig_text = dec_file.read_text(encoding="utf-8")
    
    # 2. In original D10 baseline block, replace 2.69 bpm with 2.8977 bpm citing stage6c_r6_compute.py
    old_d10_opt = 'Options: A) Descriptive only: report radar-vs-ECG window MAE with confidence intervals and the baselines (LOSO constant-mean 5.82 bpm; zero-shift spectral parabolic 2.69 bpm), no numeric gate. B) Prespecify a numeric MAE gate now, before any training result is seen.'
    new_d10_opt = 'Options: A) Descriptive only: report radar-vs-ECG window MAE with confidence intervals and the baselines (LOSO constant-mean 5.82 bpm; zero-shift spectral parabolic 2.8977 bpm [recomputed in outputs/closure/stage6c_r6_compute.py]), no numeric gate. B) Prespecify a numeric MAE gate now, before any training result is seen.'
    assert old_d10_opt in orig_text, "Original D10 options line not found!"
    
    # 3. Rename appended D10, D11, D12 to D13, D14, D15
    old_h_d10 = "## Decision D10: Window-Level Maximum RR Gap Rule (3.0 s)"
    new_h_d13 = "## Decision D13: Window-Level Maximum RR Gap Rule (3.0 s)"
    assert old_h_d10 in orig_text, "Appended D10 header not found!"
    
    old_h_d11 = "## Decision D11: Minimum Valid Beats Per Recording (20 Beats)"
    new_h_d14 = "## Decision D14: Minimum Valid Beats Per Recording (20 Beats)"
    assert old_h_d11 in orig_text, "Appended D11 header not found!"
    
    old_h_d12 = "## Decision D12: Pipeline Runner Default `output_dir` Guard"
    new_h_d15 = "## Decision D15: Pipeline Runner Default `output_dir` Guard"
    assert old_h_d12 in orig_text, "Appended D12 header not found!"
    
    updated_text = orig_text.replace(old_d10_opt, new_d10_opt)
    updated_text = updated_text.replace(old_h_d10, new_h_d13)
    updated_text = updated_text.replace(old_h_d11, new_h_d14)
    updated_text = updated_text.replace(old_h_d12, new_h_d15)
    
    dec_file.write_text(updated_text, encoding="utf-8")
    print(f"Updated {dec_file.name} successfully.")
    
    # 4. Verify Decision lines byte-identical before and after
    orig_dec_lines = [l.strip() for l in orig_text.splitlines() if "Decision:" in l]
    new_dec_lines = [l.strip() for l in updated_text.splitlines() if "Decision:" in l]
    
    print("\n=== Verification of 'Decision:' Lines ===")
    assert len(orig_dec_lines) == len(new_dec_lines), f"Count mismatch: {len(orig_dec_lines)} vs {len(new_dec_lines)}"
    all_matched = True
    for i, (od, nd) in enumerate(zip(orig_dec_lines, new_dec_lines)):
        match = (od == nd)
        if not match:
            all_matched = False
        print(f"Line {i+1}: {'PASS' if match else 'FAIL'} | '{od}' == '{nd}'")
    print(f"All Decision lines byte-identical: {'PASS' if all_matched else 'FAIL'}")
    
    # 5. Check and update runner_output_dir_rule.md if it cites D10-D12
    rule_file = repo_root / "outputs/closure/runner_output_dir_rule.md"
    rule_text = rule_file.read_text(encoding="utf-8")
    if "Decision D12" in rule_text:
        print("\n=== Updating runner_output_dir_rule.md ===")
        print("Before line:")
        for l in rule_text.splitlines():
            if "Decision D12" in l:
                print(f"  {l}")
        new_rule_text = rule_text.replace("Decision D12", "Decision D15")
        rule_file.write_text(new_rule_text, encoding="utf-8")
        print("After line:")
        for l in new_rule_text.splitlines():
            if "Decision D15" in l:
                print(f"  {l}")
    else:
        print("\nrunner_output_dir_rule.md does not cite D10-D12; left unchanged.")

if __name__ == "__main__":
    main()
