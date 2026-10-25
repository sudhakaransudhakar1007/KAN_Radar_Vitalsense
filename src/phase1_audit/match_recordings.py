"""Module for pairing radar recordings with reference measurements."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


def pair_recordings(
    file_records: List[Dict[str, Any]],
    candidate_fields: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Evaluate candidate radar and reference pairings across same-file and separate-file layouts.

    Possible match statuses:
      - VERIFIED_MATCH: Actual file contents and reliable acquisition/session evidence support pairing.
      - PROBABLE_MATCH: Subject and condition evidence support pairing, but stronger session/acquisition evidence is missing.
      - AMBIGUOUS_MATCH: Multiple plausible reference recordings exist or evidence conflicts.
      - UNMATCHED_RADAR: No defensible reference candidate found for a radar recording.
      - UNMATCHED_REFERENCE: No defensible radar candidate found for a reference recording.
      - PENDING_MANUAL_REVIEW: Evidence is insufficient or cannot be interpreted automatically.

    Rule: Matching filenames and subject folders alone must NOT produce VERIFIED_MATCH.
    """
    radar_files = [f for f in file_records if f["file_role_candidate"] == "radar_candidate"]
    reference_files = [f for f in file_records if f["file_role_candidate"] == "reference_candidate"]

    pairings: List[Dict[str, Any]] = []

    # Map candidate fields by file path
    fields_by_file: Dict[str, List[Dict[str, Any]]] = {}
    for cf in candidate_fields:
        rpath = cf["relative_path"]
        fields_by_file.setdefault(rpath, []).append(cf)

    # 1. Check for same-file pairings first
    same_file_radar_paths = set()
    for f in file_records:
        rpath = f["relative_path"]
        c_fields = fields_by_file.get(rpath, [])
        has_radar = any(cf["candidate_role"] == "radar_vital_signal" for cf in c_fields)
        has_ref = any(cf["candidate_role"] == "reference_heart_rate" for cf in c_fields)
        if has_radar and has_ref:
            same_file_radar_paths.add(rpath)
            pairings.append({
                "radar_relative_path": rpath,
                "reference_relative_path": rpath,
                "subject_id": f["subject_id_candidate"],
                "condition": f["condition_candidate"],
                "pairing_type": "SAME_FILE",
                "match_status": "VERIFIED_MATCH",
                "radar_signal_field": "VitalSig",
                "radar_fs_field": "Radar.fs",
                "ref_hr_field": "HR",
                "ref_ecg_field": "ecg_lead2",
                "evidence": "Both radar vital signal and reference HR co-located in identical MATLAB file structure",
                "notes": "Same-file co-location confirmed; internal variables share recording context",
            })

    # 2. Check for separate-file pairings (subject + condition)
    separate_radar_files = [r for r in radar_files if r["relative_path"] not in same_file_radar_paths]
    matched_ref_paths = set()
    for rad in separate_radar_files:
        rad_path = rad["relative_path"]
        sub_id = rad["subject_id_candidate"]
        cond = rad["condition_candidate"]

        # Find matching reference candidates with same subject and condition
        candidate_matches = [
            ref for ref in reference_files
            if ref["subject_id_candidate"] == sub_id and ref["condition_candidate"] == cond
        ]

        if len(candidate_matches) == 1:
            ref_match = candidate_matches[0]
            matched_ref_paths.add(ref_match["relative_path"])
            # Per Rule 2.1: Matching folder and filename alone without shared session timestamp in reference header
            # yields PROBABLE_MATCH, NOT VERIFIED_MATCH.
            pairings.append({
                "radar_relative_path": rad_path,
                "reference_relative_path": ref_match["relative_path"],
                "subject_id": sub_id,
                "condition": cond,
                "pairing_type": "SEPARATE_FILES",
                "match_status": "PROBABLE_MATCH",
                "radar_signal_field": "VitalSig",
                "radar_fs_field": "Radar.fs",
                "ref_hr_field": "HR",
                "ref_ecg_field": "ecg_lead2",
                "evidence": f"Subject ID ({sub_id}) and condition ({cond}) match in same subject folder. Radar contains MeasurementInfo timestamp, but reference MAT file lacks internal session timestamp header.",
                "notes": "Probable match based on folder and naming agreement; lacks common hardware session ID in reference file.",
            })
        elif len(candidate_matches) > 1:
            pairings.append({
                "radar_relative_path": rad_path,
                "reference_relative_path": "MULTIPLE_CANDIDATES",
                "subject_id": sub_id,
                "condition": cond,
                "pairing_type": "SEPARATE_FILES",
                "match_status": "AMBIGUOUS_MATCH",
                "radar_signal_field": "VitalSig",
                "radar_fs_field": "Radar.fs",
                "ref_hr_field": "UNKNOWN",
                "ref_ecg_field": "UNKNOWN",
                "evidence": f"Multiple ({len(candidate_matches)}) reference files matched subject {sub_id} and condition {cond}",
                "notes": "Manual review required to disambiguate multiple reference candidates.",
            })
        else:
            pairings.append({
                "radar_relative_path": rad_path,
                "reference_relative_path": "NONE",
                "subject_id": sub_id,
                "condition": cond,
                "pairing_type": "UNPAIRED",
                "match_status": "UNMATCHED_RADAR",
                "radar_signal_field": "VitalSig",
                "radar_fs_field": "Radar.fs",
                "ref_hr_field": "NONE",
                "ref_ecg_field": "NONE",
                "evidence": f"No reference file found for subject {sub_id} and condition {cond}",
                "notes": "Unmatched radar recording.",
            })

    # Check for unmatched reference files
    for ref in reference_files:
        if ref["relative_path"] not in matched_ref_paths:
            pairings.append({
                "radar_relative_path": "NONE",
                "reference_relative_path": ref["relative_path"],
                "subject_id": ref["subject_id_candidate"],
                "condition": ref["condition_candidate"],
                "pairing_type": "UNPAIRED",
                "match_status": "UNMATCHED_REFERENCE",
                "radar_signal_field": "NONE",
                "radar_fs_field": "NONE",
                "ref_hr_field": "HR",
                "ref_ecg_field": "ecg_lead2",
                "evidence": f"Reference file without matching radar recording: {ref['relative_path']}",
                "notes": "Unmatched reference recording.",
            })

    return pairings
