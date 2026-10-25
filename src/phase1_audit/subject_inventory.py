"""Subject and recording inventory module."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple


def compile_subject_inventory(
    candidate_subject_folders: List[str],
    file_records: List[Dict[str, Any]],
    pairings: List[Dict[str, Any]],
    radar_inventory: List[Dict[str, Any]],
    ref_inventory: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Compile subject-level recording inventory and compute four distinct aggregate counts.

    The four required aggregate counts:
      1. Number of subject folders found
      2. Number of subjects with at least one readable radar recording
      3. Number of subjects with usable reference candidate (usability criteria: readable HR array, 120 samples, 0 NaNs)
      4. Number of subjects potentially eligible for later analysis (provisional; subject to unresolved synchronization)
    """
    all_subjects = sorted(list(set(
        candidate_subject_folders +
        [f["subject_id_candidate"] for f in file_records if f["subject_id_candidate"] != "UNKNOWN"]
    )))

    subject_rows: List[Dict[str, Any]] = []

    subjects_with_readable_radar = set()
    subjects_with_usable_ref = set()
    subjects_potentially_eligible = set()

    for sub_id in all_subjects:
        has_folder = sub_id in candidate_subject_folders

        sub_radar = [r for r in radar_inventory if r["subject_id_candidate"] == sub_id]
        sub_ref = [r for r in ref_inventory if r["subject_id_candidate"] == sub_id]
        sub_pairs = [p for p in pairings if p["subject_id"] == sub_id]

        radar_count = len(sub_radar)
        ref_count = len(sub_ref)

        # Count conditions strictly
        apnea_count = sum(1 for r in sub_radar if "apnea" in r.get("recording_id_candidate", "").lower())
        resting_count = sum(1 for r in sub_radar if "resting" in r.get("recording_id_candidate", "").lower())

        same_file_count = sum(1 for p in sub_pairs if p.get("pairing_type") == "SAME_FILE")
        separate_file_count = sum(1 for p in sub_pairs if p.get("pairing_type") == "SEPARATE_FILES")
        ambig_count = sum(1 for p in sub_pairs if p.get("match_status") == "AMBIGUOUS_MATCH")

        # Readable radar data
        readable_radar = any(r.get("status") in ("PASS", "WARNING") for r in sub_radar)
        if readable_radar:
            subjects_with_readable_radar.add(sub_id)

        # Usable reference data
        usable_ref = any(r.get("verification_status") in ("VERIFIED", "VERIFIED_WITH_WARNINGS") for r in sub_ref)
        if usable_ref:
            subjects_with_usable_ref.add(sub_id)

        # Potentially eligible (PROVISIONAL: has readable radar AND candidate reference)
        is_prov_eligible = bool(readable_radar and usable_ref)
        if is_prov_eligible:
            subjects_potentially_eligible.add(sub_id)

        unverified_sync = len(sub_pairs)  # All are UNVERIFIED_TIMING
        quality_warnings = sum(1 for r in sub_radar if r.get("status") == "WARNING") + \
                           sum(1 for r in sub_ref if r.get("verification_status") == "VERIFIED_WITH_WARNINGS")

        notes = []
        if not has_folder:
            notes.append("No dedicated subject folder found")
        if quality_warnings > 0:
            notes.append(f"{quality_warnings} quality warnings")
        notes.append("Timing synchronization with radar is UNVERIFIED; manual alignment review required")

        row = {
            "subject_id": sub_id,
            "evidence": f"Subject folder '{sub_id}' in dataset root with {len(sub_radar) + len(sub_ref)} MAT files",
            "folder_found": has_folder,
            "radar_recordings_count": radar_count,
            "reference_recordings_count": ref_count,
            "apnea_count": apnea_count,
            "resting_count": resting_count,
            "same_file_pairings_count": same_file_count,
            "separate_file_pairings_count": separate_file_count,
            "pairing_ambiguities_count": ambig_count,
            "unreadable_count": sum(1 for r in sub_radar if r.get("status") == "FAIL"),
            "missing_radar_count": 0 if radar_count > 0 else 1,
            "missing_reference_count": 0 if ref_count > 0 else 1,
            "synchronization_status": "UNVERIFIED_TIMING",
            "data_quality_flags_count": quality_warnings,
            "manual_review_required": True,  # True because synchronization is unverified
            "provisional_readiness_status": "PROVISIONALLY_ELIGIBLE_PENDING_SYNC" if is_prov_eligible else "INELIGIBLE",
            "notes": "; ".join(notes),
        }
        subject_rows.append(row)

    aggregate_counts = {
        "count_1_subject_folders_found": len(candidate_subject_folders),
        "count_2_subjects_with_readable_radar": len(subjects_with_readable_radar),
        "count_3_subjects_with_usable_reference": len(subjects_with_usable_ref),
        "count_4_subjects_potentially_eligible_provisional": len(subjects_potentially_eligible),
        "total_candidate_subjects": len(all_subjects),
    }

    return subject_rows, aggregate_counts
