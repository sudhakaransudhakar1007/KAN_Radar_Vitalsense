"""Automated Tests for Phase 2C Readiness Validation & Supervised Dataset Safety Guards.

Verifies:
1. SupervisedDatasetGenerator.validate_readiness() passes all 7 readiness checks in read-only mode.
2. validate_readiness() is strictly non-destructive (creates zero output files or directories).
3. outputs/supervised_dataset/run_002 strictly does not exist before and after validation.
4. Output directory protection blocks unauthorized writes targeting run_002.
5. Subprocess CLI --validate-only returns exit code 0.
6. Subprocess CLI without --validate-only halts with fail-closed guard error.
7. Candidate window accounting accurately reconciles 1,104 windows across 48 recordings.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import pytest

from src.phase3.supervised_dataset_generator import SupervisedDatasetGenerator


# ==============================================================================
# 1. Non-Destructive Readiness Validation Tests
# ==============================================================================

def test_validate_readiness_all_checks_pass():
    """Verify that validate_readiness evaluates all 7 checks to PASS while keeping gate OPEN."""
    gen = SupervisedDatasetGenerator(
        output_dir="outputs/supervised_dataset/run_002",
        phase2a_gate_status="OPEN",
        authorization_granted=False,
    )
    report = gen.validate_readiness()

    assert report["overall_readiness"] is True
    assert report["gate_status"] == "OPEN"
    assert report["authorization_granted"] is False
    assert report["ready_for_phase2c_generation"] is False
    assert report["summary"]["total_checks"] == 7
    assert report["summary"]["pass_count"] == 7
    assert report["summary"]["fail_count"] == 0
    assert len(report["summary"]["blockers"]) == 0

    # Verify individual check IDs
    expected_checks = [
        "SOURCE_DATASET_INVENTORY_AND_PAIRING",
        "LABEL_SPECIFICATION_VALIDITY",
        "WINDOW_ARITHMETIC_AND_ACCOUNTING",
        "ECG_REFERENCE_HR_METHOD",
        "TRACEABILITY_SCHEMA_VALIDITY",
        "OUTPUT_PATH_SAFETY_AND_ISOLATION",
        "DENOMINATOR_RECONCILIATION",
    ]
    for cid in expected_checks:
        assert cid in report["checks"], f"Missing check {cid}"
        assert report["checks"][cid]["status"] == "PASS", f"Check {cid} failed: {report['checks'][cid]['message']}"


def test_validate_readiness_is_completely_non_destructive():
    """Verify that validate_readiness makes zero disk modifications and never creates run_002."""
    target_p = Path("outputs/supervised_dataset/run_002")
    assert not target_p.exists(), "Pre-condition: run_002 must not exist"

    gen = SupervisedDatasetGenerator(
        output_dir=str(target_p),
        phase2a_gate_status="OPEN",
        authorization_granted=False,
    )
    report = gen.validate_readiness()

    assert not target_p.exists(), "Post-condition: run_002 must strictly not exist after validate_readiness()"
    assert "READ-ONLY AUDIT" in report["notice"]


def test_validate_readiness_detects_missing_dataset(tmp_path):
    """Verify that validate_readiness reports FAIL when dataset_dir does not exist."""
    fake_data = tmp_path / "nonexistent_dataset"
    gen = SupervisedDatasetGenerator(dataset_dir=str(fake_data))
    report = gen.validate_readiness()

    assert report["overall_readiness"] is False
    assert report["checks"]["SOURCE_DATASET_INVENTORY_AND_PAIRING"]["status"] == "FAIL"
    assert "Dataset directory not found" in report["checks"]["SOURCE_DATASET_INVENTORY_AND_PAIRING"]["message"]


def test_validate_readiness_detects_corrupted_spec(tmp_path):
    """Verify that validate_readiness reports FAIL when label spec is corrupted or missing."""
    bad_spec = tmp_path / "corrupted_spec.json"
    bad_spec.write_text(json.dumps({"invalid": "spec"}), encoding="utf-8")

    gen = SupervisedDatasetGenerator(spec_path=str(bad_spec))
    report = gen.validate_readiness()

    assert report["overall_readiness"] is False
    assert report["checks"]["LABEL_SPECIFICATION_VALIDITY"]["status"] == "FAIL"


# ==============================================================================
# 2. Safety Guard & Output Protection Tests
# ==============================================================================

def test_execute_audit_blocks_unauthorized_run_002(tmp_path):
    """Verify that execute_dataset_audit halts before writing to run_002 while gate is OPEN."""
    target_p = Path("outputs/supervised_dataset/run_002")
    assert not target_p.exists()

    gen = SupervisedDatasetGenerator(
        output_dir=str(target_p),
        phase2a_gate_status="OPEN",
        authorization_granted=False,
    )

    with pytest.raises((RuntimeError, PermissionError)):
        gen.execute_dataset_audit()

    assert not target_p.exists(), "run_002 must not exist after blocked audit call"


def test_output_dir_guard_blocks_run_002_even_if_investigator_decision_exists(tmp_path, monkeypatch):
    """Verify defense-in-depth: run_002 is blocked even if investigator_decision.md exists when gate is OPEN."""
    target_p = Path("outputs/supervised_dataset/run_002")
    assert not target_p.exists()

    gen = SupervisedDatasetGenerator(
        output_dir=str(target_p),
        phase2a_gate_status="OPEN",
        authorization_granted=False,
    )

    # Mock investigator approval guard to pass
    monkeypatch.setattr(gen, "_verify_investigator_approval_guard", lambda: None)

    with pytest.raises(PermissionError, match="Creation or write to canonical outputs/supervised_dataset/run_002 is strictly prohibited"):
        gen.execute_dataset_audit()

    assert not target_p.exists()


# ==============================================================================
# 3. CLI Subprocess Invocation Tests
# ==============================================================================

SCRIPT_PATH = str(Path(__file__).resolve().parents[1] / "src/phase3/supervised_dataset_generator.py")


def test_cli_validate_only_returns_exit_0():
    """Verify that running the script with --validate-only exits with 0 and prints readiness report."""
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--validate-only",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI --validate-only failed with stderr: {res.stderr}"

    data = json.loads(res.stdout)
    assert data["overall_readiness"] is True
    assert data["summary"]["pass_count"] == 7
    assert data["summary"]["fail_count"] == 0


def test_cli_unauthorized_audit_halts_with_error():
    """Verify that running the script without --validate-only halts with exit code 1."""
    cmd = [
        sys.executable,
        SCRIPT_PATH,
        "--output_dir",
        "outputs/supervised_dataset/run_002",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0
    assert "RuntimeError" in res.stderr or "PermissionError" in res.stderr


# ==============================================================================
# 4. Scope Separation, Overwrite Guard & Mathematical HR Tests
# ==============================================================================

def test_output_dir_resolution_and_overwrite_guard(tmp_path, monkeypatch):
    """Verify _resolve_output_dir and non-empty run_002 overwrite protection."""
    gen = SupervisedDatasetGenerator(
        output_dir="outputs/supervised_dataset/run_002",
        phase2a_gate_status="CLOSED",
        authorization_granted=True,
    )
    # Output dir resolved
    assert "run_002" in str(gen.output_dir)

    # Simulate existing non-empty run_002 dir
    fake_run002 = tmp_path / "run_002"
    fake_run002.mkdir()
    (fake_run002 / "dummy_manifest.csv").write_text("dummy", encoding="utf-8")

    gen_existing = SupervisedDatasetGenerator(
        output_dir=str(fake_run002),
        phase2a_gate_status="CLOSED",
        authorization_granted=True,
    )
    monkeypatch.setattr(gen_existing, "_verify_investigator_approval_guard", lambda: None)

    with pytest.raises(FileExistsError, match="Overwriting an existing dataset run is strictly prohibited"):
        gen_existing.execute_dataset_audit()


def test_harmonic_mean_hr_mathematical_precision():
    """Verify that window HR formula calculates exact harmonic mean (60 / mean(RR))."""
    import numpy as np

    gen = SupervisedDatasetGenerator()

    # Create artificial synthetic peaks in [0, 10s]: 10 beats with variable RR
    # RR intervals: 0.8s, 0.9s, 1.0s, 0.9s, 1.0s, 0.8s, 0.9s, 1.0s, 0.8s (sum = 8.1s)
    rrs = np.array([0.8, 0.9, 1.0, 0.9, 1.0, 0.8, 0.9, 1.0, 0.8])
    peak_times = np.concatenate([[0.5], 0.5 + np.cumsum(rrs)])

    rpeaks = {"peak_times": peak_times}
    hr_h, hr_a, rr_cnt, cov_pct, max_gap, is_valid, rej_reason = gen.compute_window_reference_hr(
        0.0, 10.0, rpeaks
    )

    assert is_valid is True
    assert rr_cnt == len(rrs)
    assert rej_reason == "NONE"

    # Mathematical identity check
    expected_mean_rr = float(np.mean(rrs))
    expected_harmonic = round(60.0 / expected_mean_rr, 2)
    expected_arithmetic = round(float(np.mean(60.0 / rrs)), 2)

    assert hr_h == expected_harmonic
    assert hr_a == expected_arithmetic

    # By Jensen's inequality: Arithmetic mean >= Harmonic mean
    assert hr_a >= hr_h


def test_sqi_scope_separation_recording_vs_window():
    """Verify scope separation: recording-level rule (>=20 beats) vs window-level rule (>8.0s / >=5 intervals)."""
    import numpy as np

    gen = SupervisedDatasetGenerator()

    # 1. Window with only 4 intervals at maximum physiological RR (1.71s):
    # Total coverage = 4 * 1.71s = 6.84s <= 8.0s -> Window REJECTED for insufficient coverage
    rrs_4 = np.array([1.71, 1.71, 1.71, 1.71])
    p_times_4 = np.concatenate([[0.5], 0.5 + np.cumsum(rrs_4)])
    _, _, _, _, _, is_valid_4, rej_4 = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times_4})
    assert is_valid_4 is False
    assert "RR_COVERAGE_BELOW_8.0S" in rej_4

    # 2. Window with 5 intervals at 1.71s:
    # Total coverage = 5 * 1.71s = 8.55s > 8.0s -> Window ACCEPTED
    rrs_5 = np.array([1.71, 1.71, 1.71, 1.71, 1.71])
    p_times_5 = np.concatenate([[0.5], 0.5 + np.cumsum(rrs_5)])
    _, _, _, _, _, is_valid_5, rej_5 = gen.compute_window_reference_hr(0.0, 10.0, {"peak_times": p_times_5})
    assert is_valid_5 is True
    assert rej_5 == "NONE"


def test_caller_flags_cannot_override_unverified_signoff(tmp_path):
    """Verify Phase 6 requirement: caller-supplied flags (--gate-status CLOSED / --authorized)
    cannot override unverified governance sign-offs when PI sign-off protocol is incomplete."""
    target_out = tmp_path / "test_unauthorized_closed_flag"
    gen = SupervisedDatasetGenerator(
        output_dir=str(target_out),
        phase2a_gate_status="CLOSED",
        authorization_granted=True,
    )
    with pytest.raises(PermissionError, match="Caller supplied --gate-status CLOSED / --authorized, but genuine PI sign-off protocol validation failed"):
        gen._verify_genuine_governance_signoff()


def test_investigator_decision_template_is_unapproved():
    """Verify that investigator_decision_template.md is present as an unsigned draft template."""
    candidates = [
        Path("outputs/closure/investigator_decision_template.md"),
        Path("kan_radar_HR/outputs/closure/investigator_decision_template.md"),
    ]
    tmpl_path = next((p for p in candidates if p.exists()), None)
    assert tmpl_path is not None, "investigator_decision_template.md must exist"
    content = tmpl_path.read_text(encoding="utf-8")
    assert "DRAFT TEMPLATE ONLY" in content
    assert "[PENDING]" in content


