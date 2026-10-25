"""Privacy-preserving file discovery and inventory module for VITALSENSE audit."""

from __future__ import annotations

import datetime
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple


def compute_sha256(file_path: Path) -> Tuple[str, str | None]:
    """Compute SHA-256 checksum for a file in a streaming manner.

    Returns:
        Tuple of (sha256_hex_or_failure_string, error_message_if_any).
    """
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest(), None
    except Exception as exc:
        return f"HASH_FAILED:{type(exc).__name__}", str(exc)


def infer_candidates_from_path(
    rel_path: Path,
) -> Tuple[str, str, str, str]:
    """Extract candidate subject ID, recording ID, condition, and role from path.

    Returns:
        (subject_id_candidate, recording_id_candidate, condition_candidate, file_role_candidate)
    """
    filename = rel_path.name
    stem = rel_path.stem
    parent_name = rel_path.parent.name if rel_path.parent != Path(".") else ""

    # Subject ID candidate
    subject_id = "UNKNOWN"
    if parent_name and (parent_name.startswith("VS") or parent_name.startswith("sub")):
        subject_id = parent_name
    elif stem.startswith("VS") or stem.startswith("sub"):
        parts = stem.split("_")
        if parts:
            subject_id = parts[0]

    # Condition candidate
    stem_lower = stem.lower()
    if "resting" in stem_lower:
        condition = "Resting"
    elif "apnea" in stem_lower:
        condition = "Apnea"
    else:
        condition = "UNKNOWN"

    # Candidate file role
    if "mindray" in stem_lower:
        role = "reference_candidate"
    elif rel_path.suffix.lower() == ".mat":
        role = "radar_candidate"
    elif rel_path.suffix.lower() in [".txt", ".xlsx", ".csv", ".md"]:
        role = "documentation"
    else:
        role = "other"

    # Recording ID candidate
    recording_id = stem

    return subject_id, recording_id, condition, role


def discover_mat_files(dataset_root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Recursively discover .mat files and metadata in dataset_root.

    Returns:
        A tuple of (file_records, summary_stats).
    """
    dataset_root = Path(dataset_root).resolve()
    if not dataset_root.exists() or not dataset_root.is_dir():
        return [], {
            "dataset_root": str(dataset_root),
            "exists": False,
            "total_mat_files": 0,
            "total_bytes": 0,
            "subject_folder_count": 0,
            "folders": [],
            "error": f"Dataset root does not exist or is not a directory: {dataset_root}",
        }

    # Identify candidate subject folders
    candidate_subject_folders = sorted(
        [
            d.name
            for d in dataset_root.iterdir()
            if d.is_dir() and (d.name.startswith("VS") or d.name.startswith("sub"))
        ]
    )

    all_mat_files = sorted(
        list(dataset_root.rglob("*.mat")),
        key=lambda p: p.relative_to(dataset_root).as_posix(),
    )

    file_records: List[Dict[str, Any]] = []
    total_bytes = 0

    for file_path in all_mat_files:
        rel_path = file_path.relative_to(dataset_root)
        file_size = file_path.stat().st_size
        total_bytes += file_size

        try:
            mtime = datetime.datetime.fromtimestamp(
                file_path.stat().st_mtime, tz=datetime.timezone.utc
            ).isoformat()
        except Exception:
            mtime = "UNKNOWN"

        sha256_val, hash_err = compute_sha256(file_path)
        subject_id, recording_id, condition, role = infer_candidates_from_path(rel_path)

        notes = []
        if hash_err:
            notes.append(f"Hash calculation error: {hash_err}")

        record = {
            "relative_path": rel_path.as_posix(),
            "filename": file_path.name,
            "extension": file_path.suffix,
            "file_size_bytes": file_size,
            "sha256": sha256_val,
            "modification_time": mtime,
            "subject_id_candidate": subject_id,
            "recording_id_candidate": recording_id,
            "condition_candidate": condition,
            "file_role_candidate": role,
            "loader_used": "NOT_INSPECTED",
            "read_status": "PENDING_INSPECTION",
            "notes": "; ".join(notes) if notes else "NONE",
        }
        file_records.append(record)

    summary = {
        "dataset_root": str(dataset_root),
        "exists": True,
        "total_mat_files": len(file_records),
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / (1024 * 1024), 2),
        "subject_folder_count": len(candidate_subject_folders),
        "candidate_subject_folders": candidate_subject_folders,
    }

    return file_records, summary
