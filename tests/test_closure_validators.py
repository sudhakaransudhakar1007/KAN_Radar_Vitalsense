"""Automated Unit & Integration Tests for PI Sign-Off Validator and Phase 2C Preflight.

Tests comprehensive positive, negative, and edge-case behaviors:
1. Current repository real-file audit (verifies fail-closed pending status).
2. Field-level parsing (placeholders, ISO dates, decision extraction).
3. Cryptographic digest verification and canonical hash tampering detection.
4. Issue tracking completeness in Phase 2A addendum.
5. Source dataset inventory verification (48 radar + 48 ref = 96 files).
6. Output isolation verification (run_002 and run_real_001 non-existence).
7. Window denominator consistency (1,104 candidate windows).
8. Synthetic end-to-end fixture for fully authorized gate closure (GO condition).
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import pytest

from src.closure.pi_signoff_validator import (
    EXPECTED_CANONICAL_SPEC_SHA256,
    EXPECTED_RAW_BASELINE_SPEC_SHA256,
    PISignoffValidator,
    is_placeholder_or_empty,
    validate_iso_date,
)
from src.closure.phase2c_preflight import (
    EXPECTED_TOTAL_RECORDINGS,
    EXPECTED_TOTAL_WINDOWS,
    MANDATORY_HARDWARE_LIMITATION,
    Phase2CPreflightChecker,
)


# =====================================================================
# 1. Helper Fixtures & Mock Generators
# =====================================================================

def make_mock_protocol_text(
    d13_opt="OPTION A",
    d13_name="Dr. Eleanor Vance",
    d13_sig="E. Vance, MD PhD",
    d13_date="2026-10-22",
    d14_opt="OPTION A",
    d14_name="Dr. Eleanor Vance",
    d14_sig="E. Vance, MD PhD",
    d14_date="2026-10-22",
    d15_opt="OPTION A",
    d15_name="Dr. Eleanor Vance",
    d15_sig="E. Vance, MD PhD",
    d15_date="2026-10-22",
    hw_name="Dr. Eleanor Vance",
    hw_sig="E. Vance, MD PhD",
    hw_date="2026-10-22",
    gate_opt="AUTHORIZED",
    gate_name="Dr. Eleanor Vance",
    gate_sig="E. Vance, MD PhD",
    gate_date="2026-10-22",
) -> str:
    """Generate synthetic signed intake protocol text for testing."""
    return f"""# PRINCIPAL INVESTIGATOR (PI) SIGN-OFF INTAKE PROTOCOL

## 2. Decision D13: Window-Level Maximum RR Gap Rule (3.0 s Threshold)
Selected Option (A, B, or C): {d13_opt}
Principal Investigator Name:  {d13_name}
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               National Research Center
PI Signature:                 {d13_sig}
Date of Execution:            {d13_date}

---

## 3. Decision D14: Minimum Valid Beats Per Recording (20 Beats Threshold)
Selected Option (A, B, or C): {d14_opt}
Principal Investigator Name:  {d14_name}
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               National Research Center
PI Signature:                 {d14_sig}
Date of Execution:            {d14_date}

---

## 4. Decision D15: Pipeline Runner Default output_dir Guard
Selected Option (A or B):     {d15_opt}
Principal Investigator Name:  {d15_name}
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Institution:               National Research Center
PI Signature:                 {d15_sig}
Date of Execution:            {d15_date}

---

## 5. Formal Approval of Ground-Truth Label Specification v1.0.0
Approval Determination:       APPROVED
Approved By (PI Full Name):   {d13_name}
PI Signature:                 {d13_sig}
Date of Approval:             {d13_date}

---

## 6. Mandatory Hardware Timing Limitation Acknowledgement
Limitation Code: UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0
Acknowledged By (PI Name):    {hw_name}
PI Signature:                 {hw_sig}
Date of Acknowledgement:      {hw_date}

---

## 7. Formal PI Gate Authorization Block
Phase 2A Gate Closure Determination: [X] {gate_opt}
Principal Investigator Name:  {gate_name}
PI Academic / Clinical Title: Professor of Biomedical Engineering
PI Signature:                 {gate_sig}
Date of Authorization:        {gate_date}
"""


# =====================================================================
# 2. Field-Level Validation Tests
# =====================================================================

def test_is_placeholder_or_empty():
    """Verify robust rejection of placeholders and acceptance of valid content."""
    assert is_placeholder_or_empty(None) is True
    assert is_placeholder_or_empty("") is True
    assert is_placeholder_or_empty("   ") is True
    assert is_placeholder_or_empty("_______") is True
    assert is_placeholder_or_empty("---") is True
    assert is_placeholder_or_empty("[ ]") is True
    assert is_placeholder_or_empty("[   ]") is True
    assert is_placeholder_or_empty("TODO") is True
    assert is_placeholder_or_empty("TBD") is True
    assert is_placeholder_or_empty("PENDING") is True
    assert is_placeholder_or_empty("unknown") is True

    # Valid values must return False
    assert is_placeholder_or_empty("OPTION A") is False
    assert is_placeholder_or_empty("Dr. Alice Smith") is False
    assert is_placeholder_or_empty("2026-10-22") is False


def test_validate_iso_date():
    """Verify ISO 8601 date parsing and error reporting."""
    ok, err = validate_iso_date("2026-10-22")
    assert ok is True
    assert err is None

    ok, err = validate_iso_date("2026-02-28")
    assert ok is True

    # Non-leap year February 29
    ok, err = validate_iso_date("2025-02-29")
    assert ok is False
    assert "Invalid calendar date" in err

    # Bad formats
    ok, err = validate_iso_date("22-10-2026")
    assert ok is False
    ok, err = validate_iso_date("October 22, 2026")
    assert ok is False
    ok, err = validate_iso_date("_______")
    assert ok is False


# =====================================================================
# 3. PI Sign-Off Validator Real-Repository & Edge Cases
# =====================================================================

def test_pi_validator_on_real_repo_files():
    """Verify validator on real repository files correctly enforces fail-closed state."""
    validator = PISignoffValidator()
    report = validator.run_validation()

    # The gate MUST be blocked and not ready
    assert report.overall_status == "BLOCKED"
    assert report.is_ready_for_gate_closure is False

    # Check summary counts
    assert report.summary["PRESENT"] >= 2  # Canonical spec hash and addendum are present
    assert report.summary["MISSING"] >= 4  # D13, D14, D15, Label Spec Approval, HW Timing, etc.
    assert len(report.blockers) >= 4

    # Ensure authenticity notice is present on items
    for item in report.items:
        assert "SYNTACTIC_CHECK_ONLY" in item.authenticity_notice


def test_pi_validator_detects_hash_tampering(tmp_path):
    """Verify that any modification to label spec content causes a MISMATCH."""
    real_spec = Path("outputs/closure/spec/label_spec_v1.json")
    if not real_spec.exists():
        real_spec = Path("kan_radar_HR/outputs/closure/spec/label_spec_v1.json")

    spec_data = json.loads(real_spec.read_text(encoding="utf-8"))
    # Tamper with window duration
    spec_data["windowing"]["window_duration_seconds"] = 12.0

    tampered_spec_file = tmp_path / "label_spec_v1.json"
    tampered_spec_file.write_text(json.dumps(spec_data, indent=2), encoding="utf-8")

    validator = PISignoffValidator(spec_path=tampered_spec_file)
    _, item_hash = validator.validate_label_specification()

    assert item_hash.status == "MISMATCH"
    assert "does not match expected" in item_hash.diagnostics


def test_pi_validator_detects_missing_addendum(tmp_path):
    """Verify validator flags missing or incomplete reconciliation addendum."""
    missing_path = tmp_path / "nonexistent_addendum.md"
    validator = PISignoffValidator(addendum_path=missing_path)
    res = validator.validate_phase2a_reconciliation_addendum()
    assert res.status == "MISSING"

    # Incomplete addendum
    incomplete_path = tmp_path / "incomplete_addendum.md"
    incomplete_path.write_text("Only ISS-01 is documented.", encoding="utf-8")
    validator_inc = PISignoffValidator(addendum_path=incomplete_path)
    res_inc = validator_inc.validate_phase2a_reconciliation_addendum()
    assert res_inc.status == "INVALID"


def test_pi_validator_detects_invalid_decision_option():
    """Verify validator flags invalid decision options (e.g. OPTION Z)."""
    validator = PISignoffValidator()
    text = make_mock_protocol_text(d13_opt="OPTION Z")
    res = validator.validate_decision_d13(text)
    assert res.status == "INVALID"
    assert "Option value 'OPTION Z' is invalid" in res.diagnostics


def test_pi_validator_fully_approved_synthetic_fixture(tmp_path):
    """Verify validator passes completely (VALID) when all required fields are populated."""
    # 1. Create valid mock protocol
    mock_protocol_path = tmp_path / "pi_signoff_intake_protocol.md"
    mock_protocol_path.write_text(make_mock_protocol_text(), encoding="utf-8")

    # 2. Create valid mock spec with approved_by populated
    real_spec = Path("outputs/closure/spec/label_spec_v1.json")
    if not real_spec.exists():
        real_spec = Path("kan_radar_HR/outputs/closure/spec/label_spec_v1.json")
    spec_data = json.loads(real_spec.read_text(encoding="utf-8"))
    spec_data["approved_by"] = "Dr. Eleanor Vance"
    mock_spec_path = tmp_path / "label_spec_v1.json"
    mock_spec_path.write_text(json.dumps(spec_data, indent=2), encoding="utf-8")

    # 3. Create mock addendum covering ISS-01 to ISS-28
    mock_addendum_path = tmp_path / "phase2a_reconciliation_addendum.md"
    addendum_content = "Tracking issues:\n" + "\n".join(f"- ISS-{i:02d}: AUDITED" for i in range(1, 29))
    mock_addendum_path.write_text(addendum_content, encoding="utf-8")

    validator = PISignoffValidator(
        protocol_path=mock_protocol_path,
        spec_path=mock_spec_path,
        addendum_path=mock_addendum_path,
    )
    report = validator.run_validation()

    assert report.overall_status == "VALID"
    assert report.is_ready_for_gate_closure is True
    assert len(report.blockers) == 0
    assert report.summary["PRESENT"] == 8
    assert report.summary["MISSING"] == 0
    assert report.summary["INVALID"] == 0
    assert report.summary["MISMATCH"] == 0


# =====================================================================
# 4. Phase 2C Preflight Checker Tests
# =====================================================================

def test_preflight_on_real_repo_files():
    """Verify preflight on real repository returns NO-GO and gate status OPEN."""
    checker = Phase2CPreflightChecker()
    report = checker.run_preflight()

    assert report.verdict == "NO-GO"
    assert report.gate_status == "OPEN"
    assert report.is_authorized_for_phase2c is False
    assert len(report.blockers) >= 4

    # Confirm key passing checks
    pass_ids = [c.check_id for c in report.checks if c.status == "PASS"]
    assert "LABEL_SPEC_INTEGRITY" in pass_ids
    assert "PHASE2A_ADDENDUM_INTEGRITY" in pass_ids
    assert "PHASE2A_BASELINE_HASH" in pass_ids
    assert "SOURCE_DATASET_INVENTORY" in pass_ids
    assert "OUTPUT_ISOLATION_RUN_002" in pass_ids
    assert "OUTPUT_ISOLATION_REAL_TRAINING" in pass_ids
    assert "WINDOW_DENOMINATOR_CONSISTENCY" in pass_ids
    assert "HARDWARE_TIMING_LIMITATION_GUARD" in pass_ids


def test_preflight_verifies_source_inventory():
    """Verify checker accurately inspects 48 radar + 48 reference files."""
    checker = Phase2CPreflightChecker()
    items = checker.check_source_inventory()
    assert len(items) == 1
    item = items[0]
    assert item.status == "PASS"
    assert item.details["radar_files_count"] == EXPECTED_TOTAL_RECORDINGS
    assert item.details["reference_files_count"] == EXPECTED_TOTAL_RECORDINGS
    assert item.details["total_mat_files"] == 96


def test_preflight_detects_premature_output_isolation_breach(tmp_path):
    """Verify preflight fails immediately if run_002 or run_real_001 exists."""
    fake_base = tmp_path / "mock_project"
    fake_base.mkdir()
    (fake_base / "outputs/supervised_dataset/run_002").mkdir(parents=True)

    checker = Phase2CPreflightChecker(base_dir=fake_base)
    items = checker.check_output_isolation()

    # run_002 check must fail
    run002_item = next(it for it in items if it.check_id == "OUTPUT_ISOLATION_RUN_002")
    assert run002_item.status == "FAIL"
    assert "Premature output detected" in run002_item.message


def test_preflight_verifies_window_denominator(tmp_path):
    """Verify window denominator consistency logic for valid and corrupted counts."""
    valid_diag = tmp_path / "valid_diag.csv"
    # Create CSV with 48 recordings, each 23 windows
    rows = ["subject_id,condition,total_windows,accepted_windows,rejected_windows,pass_rate,rejection_reasons"]
    for i in range(1, 25):
        s_id = f"VS{i:02d}"
        rows.append(f"{s_id},Apnea,23,23,0,1.0,NONE")
        rows.append(f"{s_id},Resting,23,23,0,1.0,NONE")
    valid_diag.write_text("\n".join(rows), encoding="utf-8")

    checker = Phase2CPreflightChecker(diagnostic_path=valid_diag)
    items = checker.check_window_denominator_consistency()
    assert items[0].status == "PASS"
    assert items[0].details["total_candidate_windows"] == EXPECTED_TOTAL_WINDOWS

    # Corrupt count
    bad_diag = tmp_path / "bad_diag.csv"
    bad_diag.write_text(
        "subject_id,condition,total_windows,accepted_windows,rejected_windows,pass_rate,rejection_reasons\n"
        "VS01,Apnea,10,10,0,1.0,NONE\n",
        encoding="utf-8",
    )
    checker_bad = Phase2CPreflightChecker(diagnostic_path=bad_diag)
    items_bad = checker_bad.check_window_denominator_consistency()
    assert items_bad[0].status == "FAIL"
    assert "denominator mismatch" in items_bad[0].message


def test_preflight_end_to_end_authorized_fixture(tmp_path):
    """Verify preflight returns GO and gate status CLOSED in a fully approved mock setup."""
    fake_base = tmp_path / "mock_project"
    fake_base.mkdir()

    # 1. Approved protocol
    p_proto = fake_base / "outputs/closure/pi_signoff_intake_protocol.md"
    p_proto.parent.mkdir(parents=True)
    p_proto.write_text(make_mock_protocol_text(), encoding="utf-8")

    # 2. Approved spec
    real_spec = Path("outputs/closure/spec/label_spec_v1.json")
    if not real_spec.exists():
        real_spec = Path("kan_radar_HR/outputs/closure/spec/label_spec_v1.json")
    spec_data = json.loads(real_spec.read_text(encoding="utf-8"))
    spec_data["approved_by"] = "Dr. Eleanor Vance"
    p_spec = fake_base / "outputs/closure/spec/label_spec_v1.json"
    p_spec.parent.mkdir(parents=True)
    p_spec.write_text(json.dumps(spec_data, indent=2), encoding="utf-8")

    # 3. Addendum
    p_add = fake_base / "outputs/closure/phase2a_reconciliation_addendum.md"
    add_lines = "Tracking:\n" + "\n".join(f"- ISS-{i:02d}: AUDITED" for i in range(1, 29))
    p_add.write_text(add_lines, encoding="utf-8")

    # 4. Phase 2A audit copy
    real_audit = Path("outputs/phase2a/step2b_consistency_audit.md")
    if not real_audit.exists():
        real_audit = Path("kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md")
    p_audit = fake_base / "outputs/phase2a/step2b_consistency_audit.md"
    p_audit.parent.mkdir(parents=True)
    p_audit.write_bytes(real_audit.read_bytes())

    # 5. Diagnostic with 1,104 windows
    p_diag = fake_base / "outputs/closure/window_coverage_gate_diagnostic.csv"
    diag_rows = ["subject_id,condition,total_windows,accepted_windows,rejected_windows,pass_rate,rejection_reasons"]
    for i in range(1, 25):
        s_id = f"VS{i:02d}"
        diag_rows.append(f"{s_id},Apnea,23,23,0,1.0,NONE")
        diag_rows.append(f"{s_id},Resting,23,23,0,1.0,NONE")
    p_diag.write_text("\n".join(diag_rows), encoding="utf-8")

    # 6. Mock dataset with 48 radar and 48 Mindray files
    p_data = tmp_path / "mock_dataset"
    p_data.mkdir()
    for i in range(1, 25):
        s_id = f"VS{i:02d}"
        (p_data / f"{s_id}_Apnea.mat").touch()
        (p_data / f"{s_id}_Apnea_Mindray.mat").touch()
        (p_data / f"{s_id}_Resting.mat").touch()
        (p_data / f"{s_id}_Resting_Mindray.mat").touch()

    checker = Phase2CPreflightChecker(
        base_dir=fake_base,
        dataset_dir=p_data,
        protocol_path=p_proto,
        spec_path=p_spec,
        addendum_path=p_add,
        diagnostic_path=p_diag,
    )
    report = checker.run_preflight()

    # Preflight MUST return GO
    assert report.verdict == "GO"
    assert report.gate_status == "CLOSED"
    assert report.is_authorized_for_phase2c is True
    assert len(report.blockers) == 0
    assert report.summary["FAIL"] == 0

    # Test Markdown rendering
    md = checker.generate_markdown_report(report)
    assert "PREFLIGHT VERDICT: GO" in md
    assert "PHASE 2C SCIENTIFIC GATE PREFLIGHT AUDIT REPORT" in md
