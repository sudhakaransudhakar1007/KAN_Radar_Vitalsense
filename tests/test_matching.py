"""Unit tests for separate-file radar and reference matching and ambiguity handling."""

from __future__ import annotations

import pytest

from src.phase1_audit.match_recordings import pair_recordings


def test_separate_file_verified_pairing():
    """Test standard 1-to-1 matching between radar and reference files."""
    file_records = [
        {
            "relative_path": "VS01/VS01_Resting.mat",
            "subject_id_candidate": "VS01",
            "recording_id_candidate": "VS01_Resting",
            "condition_candidate": "Resting",
            "file_role_candidate": "radar_candidate",
        },
        {
            "relative_path": "VS01/VS01_Resting_Mindray.mat",
            "subject_id_candidate": "VS01",
            "recording_id_candidate": "VS01_Resting_Mindray",
            "condition_candidate": "Resting",
            "file_role_candidate": "reference_candidate",
        },
    ]
    candidate_fields = [
        {"relative_path": "VS01/VS01_Resting.mat", "candidate_role": "radar_vital_signal"},
        {"relative_path": "VS01/VS01_Resting_Mindray.mat", "candidate_role": "reference_heart_rate"},
    ]

    pairings = pair_recordings(file_records, candidate_fields)
    assert len(pairings) == 1
    pair = pairings[0]
    assert pair["pairing_type"] == "SEPARATE_FILES"
    assert pair["match_status"] == "PROBABLE_MATCH"
    assert pair["radar_relative_path"] == "VS01/VS01_Resting.mat"
    assert pair["reference_relative_path"] == "VS01/VS01_Resting_Mindray.mat"


def test_ambiguous_file_matching():
    """Test that multiple candidate reference files flag AMBIGUOUS_MATCH."""
    file_records = [
        {
            "relative_path": "VS02/VS02_Resting.mat",
            "subject_id_candidate": "VS02",
            "recording_id_candidate": "VS02_Resting",
            "condition_candidate": "Resting",
            "file_role_candidate": "radar_candidate",
        },
        {
            "relative_path": "VS02/VS02_Resting_Mindray1.mat",
            "subject_id_candidate": "VS02",
            "recording_id_candidate": "VS02_Resting_Mindray1",
            "condition_candidate": "Resting",
            "file_role_candidate": "reference_candidate",
        },
        {
            "relative_path": "VS02/VS02_Resting_Mindray2.mat",
            "subject_id_candidate": "VS02",
            "recording_id_candidate": "VS02_Resting_Mindray2",
            "condition_candidate": "Resting",
            "file_role_candidate": "reference_candidate",
        },
    ]
    candidate_fields = []

    pairings = pair_recordings(file_records, candidate_fields)
    ambig_pairs = [p for p in pairings if p["match_status"] == "AMBIGUOUS_MATCH"]
    assert len(ambig_pairs) == 1
    assert ambig_pairs[0]["subject_id"] == "VS02"


def test_unmatched_recordings():
    """Test unmatched radar and unmatched reference detection."""
    file_records = [
        {
            "relative_path": "VS03/VS03_Resting.mat",
            "subject_id_candidate": "VS03",
            "recording_id_candidate": "VS03_Resting",
            "condition_candidate": "Resting",
            "file_role_candidate": "radar_candidate",
        },
        {
            "relative_path": "VS04/VS04_Apnea_Mindray.mat",
            "subject_id_candidate": "VS04",
            "recording_id_candidate": "VS04_Apnea_Mindray",
            "condition_candidate": "Apnea",
            "file_role_candidate": "reference_candidate",
        },
    ]
    pairings = pair_recordings(file_records, [])
    unmatched_radar = [p for p in pairings if p["match_status"] == "UNMATCHED_RADAR"]
    unmatched_ref = [p for p in pairings if p["match_status"] == "UNMATCHED_REFERENCE"]
    assert len(unmatched_radar) == 1
    assert len(unmatched_ref) == 1
