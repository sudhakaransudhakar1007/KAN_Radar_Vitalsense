"""
Script to apply R7 and R9 edits to outputs/closure/pi_decision_list.md.
Author: Antigravity Assistant (Stage 6C)
"""
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]

def main():
    target_path = repo_root / "outputs/closure/pi_decision_list.md"
    backup_path = repo_root / "outputs/closure/pi_decision_list_before_6c.md"
    
    assert backup_path.exists(), f"Backup file {backup_path} does not exist!"
    
    orig_text = backup_path.read_text(encoding="utf-8")
    
    # 1. D2b Empirical Numbers
    old_d2b = "- **Empirical Numbers:** Across all 1,029 accepted windows in the dataset, the mean absolute difference between harmonic and arithmetic definitions is $0.0527\\text{ bpm}$ (maximum absolute difference: $0.82\\text{ bpm}$)."
    new_d2b = "- **Empirical Numbers:** Across all 1,029 accepted windows in the dataset (manifest `outputs/supervised_dataset/run_001/accepted_window_manifest.csv`), the mean absolute difference between harmonic and arithmetic definitions is $0.1474\\text{ bpm}$ (maximum absolute difference: $2.9400\\text{ bpm}$ in `VS15_Resting` window 18). In-memory recomputation across all 1,104 continuous-time candidate windows yields mean absolute difference $0.1441\\text{ bpm}$ and maximum absolute difference $2.9400\\text{ bpm}$ (also in `VS15_Resting` window 18). (Evidence: `outputs/closure/stage6c_r1_analysis.py`)."
    assert old_d2b in orig_text, "D2b target not found in original text"

    # 2. D5 Consequences
    old_d5 = "- **Consequences:** Option A prevents misleading claims of sub-sample or microsecond physical synchronization and accurately reflects physiological signal uncertainty. Option B perpetuates uncorrected baseline wander artifacts."
    new_d5 = "- **Consequences:** Option A prevents misleading claims of sub-sample or microsecond physical synchronization and accurately reflects physiological signal uncertainty. Under Option B, the discrete argmax lag shift between demeaned and raw cross-correlation has no verified physical mechanism (the DC-product hypothesis is not supported: Spearman rho = -0.1254, p = 0.3956; physical mechanism NOT_ESTABLISHED per Stage 2K K3 in `outputs/closure/respiratory_robustness_k3.csv`)."
    assert old_d5 in orig_text, "D5 target not found in original text"

    # 3. D7a Empirical Numbers
    old_d7a = "- **Empirical Numbers (from B5a):** Evaluated across all 48 recordings. On 46 recordings with standard positive polarity, both detectors yield identical peak timestamps ($100\\%$ match within $20\\text{ ms}$). On `VS19` (both Apnea and Resting), Lead II exhibits inverted negative QRS polarity: Option B locks onto a minor positive side-lobe (+224.9/+231.8 raw amplitude), while Option A correctly identifies the true deep negative QRS deflection (-349.4/-358.5 bandpassed, -820 raw amplitude), resolving a $\\approx 44\\text{ ms}$ fiducial shift."
    new_d7a = "- **Empirical Numbers (from B5a):** Evaluated across all 48 recordings. On 44 recordings, both detectors yield identical peak timestamps ($100\\%$ match within $20\\text{ ms}$). On `VS16` (both Apnea and Resting), the legacy detector detects an extra false peak producing non-physiological $RR < 0.343\\text{ s}$ ($0.270\\text{ s}$ and $0.274\\text{ s}$). On `VS19` (both Apnea and Resting), Lead II exhibits inverted negative QRS polarity: Option B locks onto a minor positive side-lobe (+224.9/+231.8 raw amplitude), while Option A correctly identifies the true deep negative QRS deflection (-349.4/-358.5 bandpassed, -820 raw amplitude), resolving an empirical $44.0\\text{ ms}$ fiducial shift ($0\\%$ match within $20\\text{ ms}$). (Evidence: `outputs/closure/stage6c_r4_audit.py:127-195`)."
    assert old_d7a in orig_text, "D7a target not found in original text"

    # 4. D7c Empirical Numbers
    old_d7c = "- **Empirical Numbers (from B5b):** S1 reported 48 windows ($4.57\\%$) with $|\\Delta HR| > 1.0\\text{ bpm}$ between Phase 3 and `sync_validation` because Phase 3 used midpoint while `sync_validation` used second peak. Counterfactual harmonization in B5b proves that aligning this rule drops windows with $|\\Delta HR| > 1.0\\text{ bpm}$ from 48 down to just 4 ($0.38\\%$), and mean absolute difference drops from $0.2715\\text{ bpm}$ to $0.0225\\text{ bpm}$."
    new_d7c = "- **Empirical Numbers (from B5b):** S1 reported 48 windows with $|\\Delta HR| > 1.0\\text{ bpm}$ between Phase 3 and `sync_validation` because Phase 3 used midpoint while `sync_validation` used second peak (representing $4.57\\%$ of 1,051 valid paired windows in `s1_window_hr_comparison.csv`, $4.55\\%$ of 1,056 `run_001` candidate windows, or $4.35\\%$ of 1,104 continuous-time candidate windows). Counterfactual harmonization in B5b proves that aligning this rule drops windows with $|\\Delta HR| > 1.0\\text{ bpm}$ from 48 down to just 4 ($0.38\\%$), and mean absolute difference drops from $0.2715\\text{ bpm}$ to $0.0225\\text{ bpm}$. (Evidence: `outputs/closure/stage6c_r2_analysis.py`)."
    assert old_d7c in orig_text, "D7c target not found in original text"

    # Apply R7 edits
    text = orig_text
    text = text.replace(old_d2b, new_d2b)
    text = text.replace(old_d5, new_d5)
    text = text.replace(old_d7a, new_d7a)
    text = text.replace(old_d7c, new_d7c)

    # R9 Append new undecided items at the end
    r9_append = """

---

## Decision D10: Window-Level Maximum RR Gap Rule (3.0 s)
- **Context & Question:** Whether to retain the window-level rule rejecting windows with maximum RR gap $\\ge 3.0\\text{ s}$ (`supervised_dataset_generator.py:98,213`), drop the rule, or change the threshold.
- **Options:**
  - **Option A:** Keep the window-level max-gap threshold at $3.0\\text{ s}$ (strict consistency with recording-level SQI gap rule).
  - **Option B:** Drop the window-level max-gap threshold and rely exclusively on cumulative valid RR duration coverage ($\\ge 80\\%$).
  - **Option C:** Change the window-level max-gap threshold to a prespecified physiological limit (e.g., $4.0\\text{ s}$).
- **Consequences:** Option A guards against undetected beat dropouts or bradycardia episodes distorting window harmonic mean HR. Option B avoids redundant filtering when coverage is already high. Option C provides intermediate filtering.
- **Evidence File:** [`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98), [`outputs/closure/spec_gap_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec_gap_register.csv).
- **Decision: ____________________**

---

## Decision D11: Minimum Valid Beats Per Recording (20 Beats)
- **Context & Question:** Whether to retain the recording-level SQI requirement of at least 20 valid RR beats (`ecg_reference.py:283`), drop the rule, or adjust the beat threshold.
- **Options:**
  - **Option A:** Keep the minimum valid beat threshold of 20 beats per 120 s recording.
  - **Option B:** Drop the beat count threshold and rely exclusively on cumulative valid RR coverage $> 85\\%$ of 120 s.
  - **Option C:** Increase or decrease the minimum beat threshold.
- **Consequences:** Option A ensures adequate sample size for recording-level SQI evaluation. Option B simplifies rules by tying gating strictly to time duration.
- **Evidence File:** [`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283), [`outputs/closure/spec_gap_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec_gap_register.csv).
- **Decision: ____________________**

---

## Decision D12: Pipeline Runner Default `output_dir` Guard
- **Context & Question:** Whether to apply the proposed code patch in `outputs/closure/proposed_runner_guard.diff` requiring explicit `output_dir` in `src/sync_validation/runner.py`, or maintain operational documentation only.
- **Options:**
  - **Option A:** Apply the code patch in `proposed_runner_guard.diff` so that omitting `output_dir` raises `ValueError` and writing to `outputs/phase2a` requires an explicit override flag.
  - **Option B:** Maintain operational documentation only (`runner_output_dir_rule.md`) without modifying `src/sync_validation/runner.py`.
- **Consequences:** Option A provides hard programmatic protection against accidental overwrites of `outputs/phase2a/`. Option B preserves existing code signatures at the cost of requiring procedural developer compliance.
- **Evidence File:** [`outputs/closure/proposed_runner_guard.diff`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/proposed_runner_guard.diff), [`outputs/closure/runner_output_dir_rule.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/runner_output_dir_rule.md).
- **Decision: ____________________**
"""
    # Strip any trailing whitespace from text before appending
    text = text.rstrip() + r9_append + "\n"
    
    target_path.write_text(text, encoding="utf-8")
    print(f"Successfully updated {target_path} ({len(text)} chars)")
    
    # Verify Decision lines side by side
    orig_dec_lines = [l.strip() for l in orig_text.splitlines() if "Decision:" in l]
    new_dec_lines = [l.strip() for l in text.splitlines() if "Decision:" in l]
    
    print("\n=== Decision Lines Verification ===")
    print(f"Original decision count: {len(orig_dec_lines)}")
    print(f"Updated decision count:  {len(new_dec_lines)}")
    
    all_matched = True
    for i, orig_d in enumerate(orig_dec_lines):
        new_d = new_dec_lines[i]
        matched = (orig_d == new_d)
        if not matched:
            all_matched = False
        print(f"Line {i+1}: {'PASS' if matched else 'FAIL'} | Orig: '{orig_d}' | New: '{new_d}'")
        
    print("\nNewly Appended Decisions (Blank):")
    for i in range(len(orig_dec_lines), len(new_dec_lines)):
        print(f"Appended Decision {i+1}: '{new_dec_lines[i]}'")
        
    print(f"\nOverall byte-identical match on original decisions: {'PASS' if all_matched else 'FAIL'}")

if __name__ == "__main__":
    main()
