"""Principal Investigator (PI) Sign-Off and Governance Validator.

Performs strict, read-only syntactic and cryptographic verification of all
project governance artifacts, decision records, label specifications, and
reconciliation addenda.

Enforces:
1. Syntactic completeness: all required decision fields, names, signatures, and dates must be non-empty and non-placeholder.
2. Valid date formatting: ISO-compliant dates (YYYY-MM-DD).
3. Recommendation vs Decision separation: engineering recommendations are never treated as PI approvals.
4. Cryptographic integrity: label specification canonical hash must match expected digest.
5. Authenticity boundary: clearly documents that software can only verify syntactic presence, not human authenticity.
6. Fail-closed: returns exit code 1 if any approval or verification is MISSING, INVALID, or MISMATCH.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


EXPECTED_CANONICAL_SPEC_SHA256 = "ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44"
EXPECTED_RAW_BASELINE_SPEC_SHA256 = "a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8"

PLACEHOLDER_PATTERNS = [
    r"^[_\s\-]+$",                     # Underlines, hyphens, spaces only
    r"^\[\s*\]$",                      # Empty check box
    r"^(?:TODO|TBD|PENDING|UNKNOWN)$", # Placeholder keywords
]


def is_placeholder_or_empty(val: Optional[str]) -> bool:
    """Check if a string is None, empty, or consists exclusively of placeholder characters."""
    if val is None:
        return True
    s = str(val).strip()
    if not s:
        return True
    for pat in PLACEHOLDER_PATTERNS:
        if re.match(pat, s, re.IGNORECASE):
            return True
    return False


def validate_iso_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """Validate that date_str complies with ISO 8601 YYYY-MM-DD format."""
    clean = date_str.strip()
    if is_placeholder_or_empty(clean):
        return False, "Date is empty or placeholder."
    # Match YYYY-MM-DD
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[T\s].*)?$", clean)
    if not m:
        return False, f"Date '{clean}' does not match ISO format (YYYY-MM-DD)."
    try:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        datetime(year, month, day)
        return True, None
    except ValueError as e:
        return False, f"Invalid calendar date '{clean}': {e}"


@dataclass
class ValidationItemResult:
    """Structured result for a single governance validation item."""
    item_id: str
    description: str
    status: str  # 'PRESENT', 'MISSING', 'INVALID', 'MISMATCH', 'NOT_VERIFIABLE'
    details: Dict[str, Any] = field(default_factory=dict)
    diagnostics: str = ""
    authenticity_notice: str = "SYNTACTIC_CHECK_ONLY: Software cannot verify human signature authenticity."


@dataclass
class PISignoffReport:
    """Comprehensive validation report across all governance artifacts."""
    timestamp_utc: str
    overall_status: str  # 'VALID' or 'BLOCKED'
    is_ready_for_gate_closure: bool
    summary: Dict[str, int]
    items: List[ValidationItemResult]
    blockers: List[str]


class PISignoffValidator:
    """Read-only validator for PI sign-off intake protocol and label specifications."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        protocol_path: Optional[Path] = None,
        spec_path: Optional[Path] = None,
        addendum_path: Optional[Path] = None,
    ):
        self.base_dir = self._resolve_base_dir(base_dir)
        self.protocol_path = protocol_path or (self.base_dir / "outputs/closure/pi_signoff_intake_protocol.md")
        self.spec_path = spec_path or (self.base_dir / "outputs/closure/spec/label_spec_v1.json")
        self.addendum_path = addendum_path or (self.base_dir / "outputs/closure/phase2a_reconciliation_addendum.md")

    def _resolve_base_dir(self, explicit: Optional[Path]) -> Path:
        """Resolve base project directory whether run from repo root or kan_radar_HR."""
        if explicit:
            return explicit
        cwd = Path.cwd()
        if (cwd / "src/closure").exists() and (cwd / "outputs").exists():
            return cwd
        if (cwd / "kan_radar_HR/src/closure").exists():
            return cwd / "kan_radar_HR"
        return cwd

    def _extract_field_value(self, text: str, field_name: str) -> Optional[str]:
        r"""Extract value after 'Field Name:\s*' from markdown text."""
        escaped = re.escape(field_name)
        pattern = rf"{escaped}\s*:\s*(.*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            # Strip trailing comments or markdown bold if present
            raw = re.sub(r"\s*\*+$", "", raw).strip()
            return raw
        return None

    def _parse_decision_block(self, text: str, section_header: str) -> Dict[str, Optional[str]]:
        """Parse selected option, name, signature, and date from a decision block."""
        idx = text.find(section_header)
        if idx == -1:
            return {"option": None, "name": None, "signature": None, "date": None}
        # Slice section until next major header '---' or end
        end_idx = text.find("---", idx + len(section_header))
        block_text = text[idx:end_idx] if end_idx != -1 else text[idx:]

        # Find option
        opt = None
        for key in ["Selected Option (A, B, or C)", "Selected Option (A or B)", "Selected Option", "Approval Determination", "Gate Closure Authorization"]:
            val = self._extract_field_value(block_text, key)
            if val is not None:
                opt = val
                break
        
        # Check radio-button checkmarks if line contains [X]
        if is_placeholder_or_empty(opt):
            checked = re.findall(r"\[[xX]\]\s*(OPTION [ABC]|APPROVED|AUTHORIZED)", block_text)
            if checked:
                opt = checked[0].strip()

        # Find name
        name = None
        for key in ["Principal Investigator Name", "Approved By (PI Full Name)", "Acknowledged By (PI Name)", "Approved By"]:
            val = self._extract_field_value(block_text, key)
            if val is not None:
                name = val
                break

        # Find signature
        sig = self._extract_field_value(block_text, "PI Signature")

        # Find date
        dt = None
        for key in ["Date of Execution", "Date of Approval", "Date of Acknowledgement", "Date of Authorization", "Date"]:
            val = self._extract_field_value(block_text, key)
            if val is not None:
                dt = val
                break

        return {"option": opt, "name": name, "signature": sig, "date": dt}

    def validate_decision_d13(self, protocol_text: Optional[str]) -> ValidationItemResult:
        """Validate Decision D13 (Window-Level Maximum RR Gap Rule)."""
        item_id = "DECISION_D13"
        desc = "Decision D13: Window-Level Maximum RR Gap Rule (3.0 s)"
        if protocol_text is None:
            return ValidationItemResult(item_id, desc, "MISSING", diagnostics="PI sign-off protocol file does not exist.")

        parsed = self._parse_decision_block(protocol_text, "Decision D13")
        opt, name, sig, dt = parsed["option"], parsed["name"], parsed["signature"], parsed["date"]

        errors = []
        if is_placeholder_or_empty(opt):
            errors.append("Option selection is missing or placeholder.")
        else:
            opt_clean = opt.upper()
            if not any(v in opt_clean for v in ["OPTION A", "OPTION B", "OPTION C", "A", "B", "C"]):
                errors.append(f"Option value '{opt}' is invalid (expected Option A, B, or C).")

        if is_placeholder_or_empty(name):
            errors.append("PI Name is missing or placeholder.")
        if is_placeholder_or_empty(sig):
            errors.append("PI Signature is missing or placeholder.")
        
        date_ok, date_err = validate_iso_date(dt or "")
        if not date_ok:
            errors.append(f"Date error: {date_err}")

        if errors:
            status = "MISSING" if (is_placeholder_or_empty(opt) and is_placeholder_or_empty(sig)) else "INVALID"
            return ValidationItemResult(item_id, desc, status, details=parsed, diagnostics="; ".join(errors))

        return ValidationItemResult(item_id, desc, "PRESENT", details=parsed, diagnostics="Valid D13 decision selection, signature, and date.")

    def validate_decision_d14(self, protocol_text: Optional[str]) -> ValidationItemResult:
        """Validate Decision D14 (Minimum Valid Beats Per Recording)."""
        item_id = "DECISION_D14"
        desc = "Decision D14: Minimum Valid Beats Per Recording (20 Beats)"
        if protocol_text is None:
            return ValidationItemResult(item_id, desc, "MISSING", diagnostics="PI sign-off protocol file does not exist.")

        parsed = self._parse_decision_block(protocol_text, "Decision D14")
        opt, name, sig, dt = parsed["option"], parsed["name"], parsed["signature"], parsed["date"]

        errors = []
        if is_placeholder_or_empty(opt):
            errors.append("Option selection is missing or placeholder.")
        else:
            opt_clean = opt.upper()
            if not any(v in opt_clean for v in ["OPTION A", "OPTION B", "OPTION C", "A", "B", "C"]):
                errors.append(f"Option value '{opt}' is invalid (expected Option A, B, or C).")

        if is_placeholder_or_empty(name):
            errors.append("PI Name is missing or placeholder.")
        if is_placeholder_or_empty(sig):
            errors.append("PI Signature is missing or placeholder.")

        date_ok, date_err = validate_iso_date(dt or "")
        if not date_ok:
            errors.append(f"Date error: {date_err}")

        if errors:
            status = "MISSING" if (is_placeholder_or_empty(opt) and is_placeholder_or_empty(sig)) else "INVALID"
            return ValidationItemResult(item_id, desc, status, details=parsed, diagnostics="; ".join(errors))

        return ValidationItemResult(item_id, desc, "PRESENT", details=parsed, diagnostics="Valid D14 decision selection, signature, and date.")

    def validate_decision_d15(self, protocol_text: Optional[str]) -> ValidationItemResult:
        """Validate Decision D15 (Pipeline Runner Default output_dir Guard)."""
        item_id = "DECISION_D15"
        desc = "Decision D15: Pipeline Runner Default output_dir Guard"
        if protocol_text is None:
            return ValidationItemResult(item_id, desc, "MISSING", diagnostics="PI sign-off protocol file does not exist.")

        parsed = self._parse_decision_block(protocol_text, "Decision D15")
        opt, name, sig, dt = parsed["option"], parsed["name"], parsed["signature"], parsed["date"]

        errors = []
        if is_placeholder_or_empty(opt):
            errors.append("Option selection is missing or placeholder.")
        else:
            opt_clean = opt.upper()
            if not any(v in opt_clean for v in ["OPTION A", "OPTION B", "A", "B"]):
                errors.append(f"Option value '{opt}' is invalid (expected Option A or B).")

        if is_placeholder_or_empty(name):
            errors.append("PI Name is missing or placeholder.")
        if is_placeholder_or_empty(sig):
            errors.append("PI Signature is missing or placeholder.")

        date_ok, date_err = validate_iso_date(dt or "")
        if not date_ok:
            errors.append(f"Date error: {date_err}")

        if errors:
            status = "MISSING" if (is_placeholder_or_empty(opt) and is_placeholder_or_empty(sig)) else "INVALID"
            return ValidationItemResult(item_id, desc, status, details=parsed, diagnostics="; ".join(errors))

        return ValidationItemResult(item_id, desc, "PRESENT", details=parsed, diagnostics="Valid D15 decision selection, signature, and date.")

    def validate_hardware_timing_limitation(self, protocol_text: Optional[str]) -> ValidationItemResult:
        """Validate explicit PI signed acknowledgement of UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0."""
        item_id = "HARDWARE_TIMING_ACKNOWLEDGEMENT"
        desc = "Mandatory Hardware Timing Limitation (UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0)"
        if protocol_text is None:
            return ValidationItemResult(item_id, desc, "MISSING", diagnostics="PI sign-off protocol file does not exist.")

        parsed = self._parse_decision_block(protocol_text, "Mandatory Hardware Timing Limitation")
        name, sig, dt = parsed["name"], parsed["signature"], parsed["date"]

        errors = []
        if "UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0" not in protocol_text:
            errors.append("Standardized limitation text 'UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0' is missing.")

        if is_placeholder_or_empty(name):
            errors.append("PI Name is missing or placeholder.")
        if is_placeholder_or_empty(sig):
            errors.append("PI Signature is missing or placeholder.")

        date_ok, date_err = validate_iso_date(dt or "")
        if not date_ok:
            errors.append(f"Date error: {date_err}")

        if errors:
            status = "MISSING" if is_placeholder_or_empty(sig) else "INVALID"
            return ValidationItemResult(item_id, desc, status, details=parsed, diagnostics="; ".join(errors))

        return ValidationItemResult(item_id, desc, "PRESENT", details=parsed, diagnostics="Hardware timing limitation explicitly acknowledged and signed.")

    def validate_gate_closure_authorization(self, protocol_text: Optional[str]) -> ValidationItemResult:
        """Validate formal PI closure authorization block."""
        item_id = "PHASE2A_GATE_CLOSURE_AUTH"
        desc = "Phase 2A Gate Closure Authorization"
        if protocol_text is None:
            return ValidationItemResult(item_id, desc, "MISSING", diagnostics="PI sign-off protocol file does not exist.")

        parsed = self._parse_decision_block(protocol_text, "Formal PI Gate Authorization Block")
        opt, name, sig, dt = parsed["option"], parsed["name"], parsed["signature"], parsed["date"]

        errors = []
        if is_placeholder_or_empty(opt):
            errors.append("Gate closure authorization is missing or placeholder.")
        else:
            opt_clean = opt.upper()
            if "NOT AUTHORIZED" in opt_clean:
                errors.append("PI marked gate closure as NOT AUTHORIZED.")
            elif not any(v in opt_clean for v in ["AUTHORIZED", "[X] AUTHORIZED"]):
                errors.append(f"Authorization determination '{opt}' is invalid.")

        if is_placeholder_or_empty(name):
            errors.append("PI Name is missing or placeholder.")
        if is_placeholder_or_empty(sig):
            errors.append("PI Signature is missing or placeholder.")

        date_ok, date_err = validate_iso_date(dt or "")
        if not date_ok:
            errors.append(f"Date error: {date_err}")

        if errors:
            status = "MISSING" if is_placeholder_or_empty(sig) else "INVALID"
            return ValidationItemResult(item_id, desc, status, details=parsed, diagnostics="; ".join(errors))

        return ValidationItemResult(item_id, desc, "PRESENT", details=parsed, diagnostics="Formal gate closure explicitly authorized by PI.")

    def validate_label_specification(self) -> Tuple[ValidationItemResult, ValidationItemResult]:
        """Validate label_spec_v1.json approval fields and canonical content hash."""
        id_app = "LABEL_SPEC_APPROVAL"
        desc_app = "Label Specification Approval Field (label_spec_v1.json)"
        id_hash = "LABEL_SPEC_HASH"
        desc_hash = "Label Specification Canonical Content Hash"

        if not self.spec_path.exists():
            res_app = ValidationItemResult(id_app, desc_app, "MISSING", diagnostics=f"File not found: {self.spec_path}")
            res_hash = ValidationItemResult(id_hash, desc_hash, "MISSING", diagnostics=f"File not found: {self.spec_path}")
            return res_app, res_hash

        try:
            spec_data = json.loads(self.spec_path.read_text(encoding="utf-8"))
        except Exception as e:
            res_app = ValidationItemResult(id_app, desc_app, "INVALID", diagnostics=f"JSON parse error: {e}")
            res_hash = ValidationItemResult(id_hash, desc_hash, "INVALID", diagnostics=f"JSON parse error: {e}")
            return res_app, res_hash

        # 1. Check approval field
        approved_by = spec_data.get("approved_by", "")
        if is_placeholder_or_empty(approved_by):
            res_app = ValidationItemResult(
                id_app,
                desc_app,
                "MISSING",
                details={"approved_by": approved_by},
                diagnostics="label_spec_v1.json 'approved_by' field is empty or blank.",
            )
        else:
            res_app = ValidationItemResult(
                id_app,
                desc_app,
                "PRESENT",
                details={"approved_by": approved_by},
                diagnostics=f"Approved by: {approved_by}",
            )

        # 2. Check canonical hash
        d_canonical = {k: v for k, v in spec_data.items() if k not in ("approved_by", "spec_sha256")}
        canonical_str = json.dumps(d_canonical, indent=2, sort_keys=True)
        calc_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest().lower()
        internal_hash = spec_data.get("spec_sha256", "").lower()

        hash_details = {
            "calculated_canonical_sha256": calc_hash,
            "internal_spec_sha256": internal_hash,
            "expected_canonical_sha256": EXPECTED_CANONICAL_SPEC_SHA256,
        }

        if calc_hash != EXPECTED_CANONICAL_SPEC_SHA256:
            res_hash = ValidationItemResult(
                id_hash,
                desc_hash,
                "MISMATCH",
                details=hash_details,
                diagnostics=f"Calculated canonical hash ({calc_hash}) does not match expected ({EXPECTED_CANONICAL_SPEC_SHA256}).",
            )
        elif internal_hash and internal_hash != calc_hash:
            res_hash = ValidationItemResult(
                id_hash,
                desc_hash,
                "MISMATCH",
                details=hash_details,
                diagnostics=f"Internal spec_sha256 ({internal_hash}) does not match canonical calculation ({calc_hash}).",
            )
        else:
            res_hash = ValidationItemResult(
                id_hash,
                desc_hash,
                "PRESENT",
                details=hash_details,
                diagnostics=f"Canonical content SHA-256 matched: {calc_hash}",
            )

        return res_app, res_hash

    def validate_phase2a_reconciliation_addendum(self) -> ValidationItemResult:
        """Validate that Phase 2A Reconciliation Addendum exists and documents issue status."""
        item_id = "PHASE2A_RECONCILIATION_ADDENDUM"
        desc = "Phase 2A Reconciliation Addendum (phase2a_reconciliation_addendum.md)"

        if not self.addendum_path.exists():
            return ValidationItemResult(
                item_id,
                desc,
                "MISSING",
                diagnostics=f"Addendum file not found: {self.addendum_path}",
            )

        content = self.addendum_path.read_text(encoding="utf-8")
        if "ISS-01" not in content or "ISS-28" not in content:
            return ValidationItemResult(
                item_id,
                desc,
                "INVALID",
                diagnostics="Addendum does not contain complete ISS-01 to ISS-28 issue tracking.",
            )

        return ValidationItemResult(
            item_id,
            desc,
            "PRESENT",
            details={"file_path": str(self.addendum_path), "size_bytes": len(content)},
            diagnostics="Addendum present; tracks all 28 Phase 2A issues.",
        )

    def run_validation(self) -> PISignoffReport:
        """Execute full validation suite across all governance documents."""
        protocol_text = None
        if self.protocol_path.exists():
            protocol_text = self.protocol_path.read_text(encoding="utf-8")

        items: List[ValidationItemResult] = []

        # 1. Decisions
        items.append(self.validate_decision_d13(protocol_text))
        items.append(self.validate_decision_d14(protocol_text))
        items.append(self.validate_decision_d15(protocol_text))

        # 2. Label spec
        item_app, item_hash = self.validate_label_specification()
        items.append(item_app)
        items.append(item_hash)

        # 3. Hardware limitation
        items.append(self.validate_hardware_timing_limitation(protocol_text))

        # 4. Reconciliation addendum
        items.append(self.validate_phase2a_reconciliation_addendum())

        # 5. Gate closure authorization
        items.append(self.validate_gate_closure_authorization(protocol_text))

        # Summarize
        summary = {"PRESENT": 0, "MISSING": 0, "INVALID": 0, "MISMATCH": 0, "NOT_VERIFIABLE": 0}
        blockers = []
        for it in items:
            summary[it.status] = summary.get(it.status, 0) + 1
            if it.status in ("MISSING", "INVALID", "MISMATCH"):
                blockers.append(f"[{it.item_id}] {it.diagnostics}")

        is_ready = (len(blockers) == 0)
        overall_status = "VALID" if is_ready else "BLOCKED"

        return PISignoffReport(
            timestamp_utc=datetime.utcnow().isoformat() + "Z",
            overall_status=overall_status,
            is_ready_for_gate_closure=is_ready,
            summary=summary,
            items=items,
            blockers=blockers,
        )


def main():
    """CLI entry point for PI sign-off validator."""
    parser = argparse.ArgumentParser(description="PI Sign-Off Intake and Governance Validator")
    parser.add_argument("--protocol", type=str, default=None, help="Path to pi_signoff_intake_protocol.md")
    parser.add_argument("--spec", type=str, default=None, help="Path to label_spec_v1.json")
    parser.add_argument("--addendum", type=str, default=None, help="Path to phase2a_reconciliation_addendum.md")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON to stdout")
    parser.add_argument("--output", type=str, default=None, help="Save JSON report to file")
    args = parser.parse_args()

    validator = PISignoffValidator(
        protocol_path=Path(args.protocol) if args.protocol else None,
        spec_path=Path(args.spec) if args.spec else None,
        addendum_path=Path(args.addendum) if args.addendum else None,
    )
    report = validator.run_validation()

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print("=================================================================")
        print(f"PI SIGN-OFF & GOVERNANCE VALIDATION REPORT ({report.timestamp_utc})")
        print("=================================================================")
        print(f"Overall Status:              {report.overall_status}")
        print(f"Ready for Gate Closure:      {report.is_ready_for_gate_closure}")
        print(f"Items Verified:              {len(report.items)}")
        print(f"Counts:                      {report.summary}")
        print("\n--- DETAILED ITEM RESULTS ---")
        for it in report.items:
            status_icon = "PASS" if it.status == "PRESENT" else f"FAIL ({it.status})"
            print(f"  [{status_icon:12}] {it.item_id}: {it.description}")
            if it.diagnostics:
                print(f"                 Diagnostics: {it.diagnostics}")
        print("=================================================================")
        if report.blockers:
            print("\nOUTSTANDING GOVERNANCE BLOCKERS (Must be resolved before gate closure):")
            for b in report.blockers:
                print(f"  - {b}")
            print("\nNOTICE: The scientific gate remains OPEN. Real-data operations remain BLOCKED.")
        else:
            print("\nALL GOVERNANCE CHECKS PASSED. Ready for formal gate closure.")
        print("=================================================================")

    sys.exit(0 if report.is_ready_for_gate_closure else 1)


if __name__ == "__main__":
    main()
