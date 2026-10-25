"""Unit tests for file discovery, hashing, and CLI gates."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import pytest

from src.phase1_audit.discover_files import (
    compute_sha256,
    discover_mat_files,
    infer_candidates_from_path,
)


def test_missing_dataset_root(tmp_path: Path):
    """Test behavior when dataset root does not exist."""
    non_existent = tmp_path / "does_not_exist"
    records, summary = discover_mat_files(non_existent)
    assert len(records) == 0
    assert summary["exists"] is False
    assert "error" in summary


def test_empty_dataset_root(tmp_path: Path):
    """Test discovery on an empty directory."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    records, summary = discover_mat_files(empty_dir)
    assert len(records) == 0
    assert summary["exists"] is True
    assert summary["total_mat_files"] == 0
    assert summary["subject_folder_count"] == 0


def test_sha256_computation(tmp_path: Path):
    """Test SHA-256 calculation on a known file."""
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"VITALSENSE_TEST_CONTENT")
    sha, err = compute_sha256(test_file)
    assert err is None
    # Pre-calculated sha256 for 'VITALSENSE_TEST_CONTENT'
    import hashlib
    expected = hashlib.sha256(b"VITALSENSE_TEST_CONTENT").hexdigest()
    assert sha == expected


def test_sha256_nonexistent_file(tmp_path: Path):
    """Test SHA-256 calculation on a missing file records error."""
    missing_file = tmp_path / "missing.bin"
    sha, err = compute_sha256(missing_file)
    assert sha.startswith("HASH_FAILED")
    assert err is not None


def test_infer_candidates_from_path():
    """Test candidate parsing for radar and reference files."""
    # Structured layout
    p1 = Path("VS01/VS01_Resting.mat")
    sub, rec, cond, role = infer_candidates_from_path(p1)
    assert sub == "VS01"
    assert rec == "VS01_Resting"
    assert cond == "Resting"
    assert role == "radar_candidate"

    # Reference file
    p2 = Path("VS01/VS01_Resting_Mindray.mat")
    sub, rec, cond, role = infer_candidates_from_path(p2)
    assert sub == "VS01"
    assert cond == "Resting"
    assert role == "reference_candidate"


def test_flat_layout_discovery(tmp_path: Path):
    """Test discovery with a flat layout (0 subject folders)."""
    dataset_dir = tmp_path / "flat_dataset"
    dataset_dir.mkdir()
    (dataset_dir / "VS01_Resting.mat").write_bytes(b"dummy_radar")
    (dataset_dir / "VS01_Resting_Mindray.mat").write_bytes(b"dummy_ref")

    records, summary = discover_mat_files(dataset_dir)
    assert len(records) == 2
    assert summary["subject_folder_count"] == 0
    # Subject inferred as candidate from filename
    assert records[0]["subject_id_candidate"] == "VS01"


def test_cli_stage_b_gate_refuses_without_stage_a(tmp_path: Path):
    """FINAL PATCH 1: Stage B must refuse if stage_a_summary.json is missing."""
    empty_out = tmp_path / "out"
    empty_out.mkdir()
    cmd = [
        sys.executable,
        "-m",
        "src.phase1_audit.run_audit",
        "--stage",
        "B",
        "--approve-stage-b",
        "--output-dir",
        str(empty_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0
    assert "Stage B execution refused" in (res.stdout + res.stderr)
    assert "Missing required Stage A summary file" in (res.stdout + res.stderr)


def test_cli_stage_b_gate_refuses_without_approval_flag(tmp_path: Path):
    """FINAL PATCH 1: Stage B must refuse if --approve-stage-b is not passed."""
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Create fake stage_a_summary.json
    (out_dir / "stage_a_summary.json").write_text(json.dumps({"stage": "A"}), encoding="utf-8")

    cmd = [
        sys.executable,
        "-m",
        "src.phase1_audit.run_audit",
        "--stage",
        "B",
        "--output-dir",
        str(out_dir),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0
    assert "Stage B execution refused" in (res.stdout + res.stderr)
    assert "--approve-stage-b" in (res.stdout + res.stderr)
