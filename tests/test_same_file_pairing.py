"""Unit tests for same-file radar and reference co-location pairing."""

from __future__ import annotations

import pytest

from src.phase1_audit.match_recordings import pair_recordings


def test_same_file_pairing_detection():
    """Test that a file containing both radar signal and reference HR is paired as SAME_FILE."""
    file_records = [
        {
            "relative_path": "subject01/co_located.mat",
            "subject_id_candidate": "subject01",
            "recording_id_candidate": "co_located",
            "condition_candidate": "Resting",
            "file_role_candidate": "radar_candidate",
        }
    ]
    candidate_fields = [
        {
            "relative_path": "subject01/co_located.mat",
            "variable_path": "VitalSig",
            "candidate_role": "radar_vital_signal",
        },
        {
            "relative_path": "subject01/co_located.mat",
            "variable_path": "HR",
            "candidate_role": "reference_heart_rate",
        },
    ]

    pairings = pair_recordings(file_records, candidate_fields)
    assert len(pairings) == 1
    pair = pairings[0]
    assert pair["pairing_type"] == "SAME_FILE"
    assert pair["match_status"] == "VERIFIED_MATCH"
    assert pair["radar_relative_path"] == "subject01/co_located.mat"
    assert pair["reference_relative_path"] == "subject01/co_located.mat"
    assert pair["radar_signal_field"] == "VitalSig"
    assert pair["ref_hr_field"] == "HR"
