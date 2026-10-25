"""Automated tests for D15 pipeline runner output directory safeguard.

Tests that omitting output_dir raises ValueError, specifying outputs/phase2a raises
PermissionError unless explicitly overridden, and isolated output directories are permitted,
while strictly preserving audited outputs/phase2a baseline files.
"""

import hashlib
from pathlib import Path
import pytest

from src.sync_validation.runner import run_full_validation, run_sync_validation


@pytest.fixture
def phase2a_integrity():
    """Verify outputs/phase2a files remain strictly bit-for-bit unchanged."""
    p2a_csv = Path("outputs/phase2a/sync_validation_results.csv")
    p2a_audit = Path("outputs/phase2a/step2b_consistency_audit.md")
    
    h_csv_before = hashlib.sha256(p2a_csv.read_bytes()).hexdigest() if p2a_csv.exists() else None
    h_audit_before = hashlib.sha256(p2a_audit.read_bytes()).hexdigest() if p2a_audit.exists() else None
    
    yield
    
    if h_csv_before:
        h_csv_after = hashlib.sha256(p2a_csv.read_bytes()).hexdigest()
        assert h_csv_after == h_csv_before, "CRITICAL: outputs/phase2a/sync_validation_results.csv was modified!"
    if h_audit_before:
        h_audit_after = hashlib.sha256(p2a_audit.read_bytes()).hexdigest()
        assert h_audit_after == h_audit_before, "CRITICAL: outputs/phase2a/step2b_consistency_audit.md was modified!"


def test_missing_output_dir_raises_value_error(phase2a_integrity):
    """Test that omitting output_dir in run_sync_validation raises ValueError."""
    with pytest.raises(ValueError, match="output_dir must be explicitly specified"):
        run_sync_validation(output_dir=None)

    with pytest.raises(ValueError, match="output_dir must be explicitly specified"):
        run_full_validation(dataset_dir=Path("nonexistent"), output_dir=None)


def test_protected_phase2a_raises_permission_error(phase2a_integrity):
    """Test that directing output to outputs/phase2a raises PermissionError by default."""
    target_dir = Path("outputs/phase2a")
    with pytest.raises(PermissionError, match="immutable 'outputs/phase2a' is blocked by governance guard"):
        run_sync_validation(output_dir=target_dir)

    with pytest.raises(PermissionError, match="immutable 'outputs/phase2a' is blocked by governance guard"):
        run_sync_validation(output_dir="outputs/phase2a")

    with pytest.raises(PermissionError, match="immutable 'outputs/phase2a' is blocked by governance guard"):
        run_full_validation(dataset_dir=Path("nonexistent"), output_dir=target_dir)


def test_safe_isolated_output_dir_accepted(tmp_path, phase2a_integrity):
    """Test that a distinct isolated output directory is permitted without raising early guard errors."""
    iso_dir = tmp_path / "isolated_output"
    # When passing a nonexistent dataset_dir, it will pass the guard and proceed to dataset scanning
    # (or raise FileNotFoundError / complete empty scan), proving the guard did not block valid isolated paths.
    dummy_data = tmp_path / "mock_dataset"
    dummy_data.mkdir()
    df, stats = run_full_validation(dataset_dir=dummy_data, output_dir=iso_dir)
    assert iso_dir.exists()
    assert len(df) == 0  # No .mat files in dummy_data, clean empty run
