"""
Stage 7A E4: Spec and decision status note generation.
Author: Antigravity Assistant (Stage 7A)
"""
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
spec_path = repo_root / "outputs/closure/spec/label_spec_v1.json"
note_path = repo_root / "outputs/closure/spec_status_note.md"

def main():
    print("=== E4. Spec and Decision Status Audit ===")
    print(f"Reading spec from: {spec_path}")
    
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)
        
    governance_status = spec_data.get("governance", {}).get("status", "")
    approved_by = spec_data.get("approved_by", "")
    
    print(f"governance.status: '{governance_status}' (file:line: outputs/closure/spec/label_spec_v1.json:7)")
    print(f"approved_by:       '{approved_by}' (file:line: outputs/closure/spec/label_spec_v1.json:4)")
    
    note_content = f"""# Label Specification Status Note

**Target File:** `outputs/closure/spec/label_spec_v1.json`  
**Current Governance Status:** `{governance_status}`  
**Approved By Field:** `{approved_by}`  
**Actual Working Status:** `DRAFT_UNAPPROVED`

---

## Status Assessment

The label specification in `outputs/closure/spec/label_spec_v1.json` is **DRAFT_UNAPPROVED**.

It remains unapproved and frozen pre-training pending:
1. Investigator decisions on pending items **D13**, **D14**, and **D15** in `outputs/closure/pi_decision_list.md`.
2. Formal investigator review and approval of the proposed correction in `outputs/closure/d7a_wording_proposal.md` (correcting median bandpass vs. raw amplitudes for Decision D7a).
3. Resolution of the specification discrepancy identified in Stage 7A E3: `label_spec_v1.json` references `src.sync_validation.ecg_processor.clean_ecg_nans` with options `{{'only_isolated': True, 'fill_boundary': True}}`, whereas `fill_boundary` is implemented exclusively in `src.phase3.ecg_reference.clean_ecg_nans`.

**Constraint:** The file `outputs/closure/spec/label_spec_v1.json` must NOT be edited until formal investigator decisions are executed and recorded.
"""
    note_path.write_text(note_content.strip() + "\n", encoding="utf-8")
    print(f"\nWrote status note to: {note_path} ({note_path.stat().st_size} bytes)")
    print("Content preview:")
    for line in note_content.strip().splitlines()[:15]:
        print(f"  {line}")

if __name__ == "__main__":
    main()
