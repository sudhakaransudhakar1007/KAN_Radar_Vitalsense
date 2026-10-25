"""Unit tests for signal quality checks and subject aggregate counts."""

from __future__ import annotations

import numpy as np
import pytest

from src.phase1_audit.subject_inventory import compile_subject_inventory
from src.phase1_audit.validate_data import (
    validate_radar_signal,
    validate_reference_signal,
)


def test_empty_signal_detection():
    """Test detection of empty array."""
    empty_arr = np.array([])
    rec, findings = validate_radar_signal(empty_arr, 333.33, "rad.mat", "VS01", "rec1")
    assert rec["status"] == "FAIL"
    assert any(f["check_performed"] == "empty_check" for f in findings)


def test_nan_and_inf_detection():
    """Test detection of NaN, +Inf, and -Inf."""
    bad_arr = np.array([1.0, np.nan, np.inf, -np.inf, 2.0])
    rec, findings = validate_radar_signal(bad_arr, 333.33, "rad.mat", "VS01", "rec1")
    assert rec["nan_count"] == 1
    assert rec["posinf_count"] == 1
    assert rec["neginf_count"] == 1
    assert rec["status"] == "FAIL"
    checks = [f["check_performed"] for f in findings]
    assert "nan_check" in checks
    assert "infinity_check" in checks


def test_constant_signal_detection():
    """Test detection of completely flat / constant signal."""
    const_arr = np.ones(100) * 5.0
    rec, findings = validate_radar_signal(const_arr, 333.33, "rad.mat", "VS01", "rec1")
    assert rec["constant_flag"] == "CONSTANT"
    assert any(f["check_performed"] == "constant_signal_check" for f in findings)


def test_near_constant_signal_detection():
    """Test detection of near-constant signal below threshold."""
    near_const_arr = np.ones(100) + np.random.randn(100) * 1e-8
    rec, findings = validate_radar_signal(
        near_const_arr, 333.33, "rad.mat", "VS01", "rec1", near_constant_threshold=1e-6
    )
    assert rec["constant_flag"] == "NEAR_CONSTANT"
    assert any(f["check_performed"] == "near_constant_check" for f in findings)


def test_non_numeric_signal_detection():
    """Test detection of non-numeric signal."""
    rec, findings = validate_radar_signal("not_an_array", 333.33, "rad.mat", "VS01", "rec1")
    assert rec["status"] == "FAIL_NON_ARRAY"
    assert any(f["check_performed"] == "array_type" for f in findings)


def test_reference_hr_bounds_and_zeros():
    """Test zero HR readings and physiological bounds checking."""
    hr_arr = np.array([72, 75, 0, 0, 240, 70], dtype=np.uint8)
    rec, findings = validate_reference_signal(hr_arr, "ref.mat", "VS01", "rec1")
    assert rec["missing_or_invalid_count"] >= 2  # 2 zeros
    assert rec["verification_status"] == "VERIFIED_WITH_WARNINGS"
    checks = [f["check_performed"] for f in findings]
    assert "zero_hr_dropout_check" in checks
    assert "physiological_bounds_hr" in checks


def test_subject_inventory_four_separate_counts():
    """Test Section 14 rule: Four distinct aggregate counts must not be conflated."""
    candidate_folders = ["VS01", "VS02", "VS03"]
    file_records = [
        {"subject_id_candidate": "VS01"},
        {"subject_id_candidate": "VS02"},
        {"subject_id_candidate": "VS03"},
    ]
    pairings = [
        {"subject_id": "VS01", "match_status": "VERIFIED_MATCH", "pairing_type": "SEPARATE_FILES"},
        {"subject_id": "VS02", "match_status": "VERIFIED_MATCH", "pairing_type": "SEPARATE_FILES"},
    ]
    # VS01 has radar and ref
    # VS02 has radar only
    # VS03 has unreadable radar
    radar_inventory = [
        {"subject_id_candidate": "VS01", "status": "PASS"},
        {"subject_id_candidate": "VS02", "status": "PASS"},
        {"subject_id_candidate": "VS03", "status": "FAIL"},
    ]
    ref_inventory = [
        {"subject_id_candidate": "VS01", "verification_status": "VERIFIED"},
    ]

    rows, agg = compile_subject_inventory(
        candidate_folders,
        file_records,
        pairings,
        radar_inventory,
        ref_inventory,
    )

    # Count 1: Subject folders found = 3
    assert agg["count_1_subject_folders_found"] == 3
    # Count 2: Readable radar data = 2 (VS01, VS02)
    assert agg["count_2_subjects_with_readable_radar"] == 2
    # Count 3: Usable reference data = 1 (VS01)
    assert agg["count_3_subjects_with_usable_reference"] == 1
    # Count 4: Potentially eligible = 1 (VS01 only has both)
    assert agg["count_4_subjects_potentially_eligible_provisional"] == 1
