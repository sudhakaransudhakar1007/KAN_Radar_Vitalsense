"""Unit tests for candidate-field identification and documentation linking."""

from __future__ import annotations

from pathlib import Path
import pytest

from src.phase1_audit.identify_fields import (
    identify_candidate_fields,
    parse_subject_info_excel,
)


def test_candidate_field_identification_matching():
    """Test candidate field mapping for known radar and reference variables."""
    structures = [
        {"variable_path": "VitalSig", "shape_as_read": "(40000,)", "dtype_as_read": "float64", "relative_path": "VS01/VS01_Resting.mat"},
        {"variable_path": "Radar.fs", "shape_as_read": "()", "dtype_as_read": "float", "relative_path": "VS01/VS01_Resting.mat"},
        {"variable_path": "HR", "shape_as_read": "(120,)", "dtype_as_read": "uint8", "relative_path": "VS01/VS01_Resting_Mindray.mat"},
        {"variable_path": "ecg_lead2", "shape_as_read": "(60000,)", "dtype_as_read": "float64", "relative_path": "VS01/VS01_Resting_Mindray.mat"},
    ]

    doc_evidence = {
        "xlsx_info": {
            "radar_parameters": {
                "VitalSig": {"full_name": "Vital signal", "unit": "mm"},
                "Radar.fs": {"full_name": "Sampling frequency", "unit": "Hz"},
            },
            "reference_parameters": {
                "HR": {"full_name": "Heart Rate", "unit": "beats per minute"},
                "ecg_lead2": {"full_name": "ECG Lead II", "unit": "mV"},
            },
        }
    }

    candidates = identify_candidate_fields(structures, doc_evidence)
    assert len(candidates) == 4

    roles = [c["candidate_role"] for c in candidates]
    assert "radar_vital_signal" in roles
    assert "radar_sampling_frequency" in roles
    assert "reference_heart_rate" in roles
    assert "reference_ecg" in roles

    # Check evidence was linked from docs
    vs_cand = next(c for c in candidates if c["variable_path"] == "VitalSig")
    assert "mm" in vs_cand["evidence"]
    assert vs_cand["verification_status"] == "VERIFIED"


def test_missing_vitalsig_and_radar_fs():
    """Test handling of structures lacking VitalSig or Radar.fs."""
    structures = [
        {"variable_path": "UnknownSignal", "shape_as_read": "(100,)", "dtype_as_read": "float64", "relative_path": "unknown.mat"},
    ]
    candidates = identify_candidate_fields(structures)
    assert len(candidates) == 0


def test_unverified_field_when_not_in_docs():
    """Test that candidate without documentation is flagged UNVERIFIED."""
    structures = [
        {"variable_path": "VitalSig", "shape_as_read": "(40000,)", "dtype_as_read": "float64", "relative_path": "test.mat"},
    ]
    # No documentation passed
    candidates = identify_candidate_fields(structures, doc_evidence=None)
    assert len(candidates) == 1
    assert candidates[0]["verification_status"] == "UNVERIFIED"
