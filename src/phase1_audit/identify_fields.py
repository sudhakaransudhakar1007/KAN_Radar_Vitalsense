"""Candidate-field identification and documentation evidence extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
import zipfile


def parse_subject_info_excel(xlsx_path: Path) -> Dict[str, Any]:
    """Parse sheets and parameters from Subject Information.xlsx using built-in zipfile/ET."""
    xlsx_path = Path(xlsx_path).resolve()
    if not xlsx_path.exists() or not xlsx_path.is_file():
        return {"exists": False, "error": f"File not found: {xlsx_path}"}

    results: Dict[str, Any] = {
        "exists": True,
        "sheets": {},
        "radar_parameters": {},
        "reference_parameters": {},
        "subject_count_in_sheet": 0,
    }

    try:
        with zipfile.ZipFile(xlsx_path, "r") as z:
            # 1. Read shared strings
            shared_strings: List[str] = []
            if "xl/sharedStrings.xml" in z.namelist():
                ss_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in ss_tree.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                    t = si.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                    shared_strings.append(t.text if t is not None and t.text else "")

            # 2. Read sheet names mapping
            sheet_map: Dict[str, str] = {}
            if "xl/workbook.xml" in z.namelist():
                wb_tree = ET.fromstring(z.read("xl/workbook.xml"))
                for sheet_elem in wb_tree.findall(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheets/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"
                ):
                    s_name = sheet_elem.attrib.get("name", "")
                    s_id = sheet_elem.attrib.get("sheetId", "")
                    sheet_map[s_name] = f"xl/worksheets/sheet{s_id}.xml"

            results["sheet_names"] = list(sheet_map.keys())

            def extract_sheet_rows(sheet_xml_path: str) -> List[List[str]]:
                if sheet_xml_path not in z.namelist():
                    return []
                sheet_tree = ET.fromstring(z.read(sheet_xml_path))
                rows_data: List[List[str]] = []
                for row_elem in sheet_tree.findall(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"
                ):
                    row_vals: List[str] = []
                    for c_elem in row_elem.findall(
                        "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"
                    ):
                        t_attr = c_elem.attrib.get("t")
                        v_elem = c_elem.find(
                            "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v"
                        )
                        val_str = v_elem.text if v_elem is not None and v_elem.text else ""
                        if t_attr == "s" and val_str.isdigit():
                            idx = int(val_str)
                            val_str = shared_strings[idx] if idx < len(shared_strings) else val_str
                        row_vals.append(val_str)
                    if any(row_vals):
                        rows_data.append(row_vals)
                return rows_data

            # Radar Parameters sheet
            if "Radar Parameters" in sheet_map:
                rows = extract_sheet_rows(sheet_map["Radar Parameters"])
                for r in rows[1:]:  # skip header
                    if len(r) >= 3:
                        abbr, full_name, unit = r[0].strip(), r[1].strip(), r[2].strip()
                        results["radar_parameters"][abbr] = {"full_name": full_name, "unit": unit}

            # Reference Parameters sheet
            if "Reference Parameters" in sheet_map:
                rows = extract_sheet_rows(sheet_map["Reference Parameters"])
                for r in rows[1:]:
                    if len(r) >= 3:
                        abbr, full_name, unit = r[0].strip(), r[1].strip(), r[2].strip()
                        results["reference_parameters"][abbr] = {
                            "full_name": full_name,
                            "unit": unit,
                        }

            # Subject Info sheet
            if "Subject Info" in sheet_map:
                rows = extract_sheet_rows(sheet_map["Subject Info"])
                sub_count = 0
                for r in rows[1:]:
                    if r and r[0].startswith("VS"):
                        sub_count += 1
                results["subject_count_in_sheet"] = sub_count

    except Exception as exc:
        results["error"] = f"Failed to parse xlsx: {type(exc).__name__}: {exc}"

    return results


def inspect_dataset_docs(docs_dir: Path) -> Dict[str, Any]:
    """Inspect README.txt, MANIFEST.TXT, and Subject Information.xlsx in docs_dir."""
    docs_dir = Path(docs_dir).resolve()
    doc_summary: Dict[str, Any] = {
        "docs_dir": str(docs_dir),
        "exists": docs_dir.exists(),
        "readme_found": False,
        "manifest_found": False,
        "xlsx_found": False,
        "definitions": {},
    }

    readme_path = docs_dir / "README.txt"
    if readme_path.exists():
        doc_summary["readme_found"] = True
        try:
            readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
            doc_summary["readme_bytes"] = len(readme_text)
            doc_summary["readme_lines"] = len(readme_text.splitlines())
            # Check for key keywords
            doc_summary["mentions_vitalsig"] = "VitalSig" in readme_text
            doc_summary["mentions_mindray"] = "Mindray" in readme_text
            doc_summary["mentions_120ghz"] = "120 GHz" in readme_text or "120-GHz" in readme_text
        except Exception as exc:
            doc_summary["readme_error"] = str(exc)

    manifest_path = docs_dir / "MANIFEST.TXT"
    if manifest_path.exists():
        doc_summary["manifest_found"] = True
        try:
            m_lines = manifest_path.read_text(encoding="utf-8", errors="replace").splitlines()
            doc_summary["manifest_file_count"] = len([ln for ln in m_lines if ln.strip()])
        except Exception as exc:
            doc_summary["manifest_error"] = str(exc)

    xlsx_path = docs_dir / "Subject Information.xlsx"
    if xlsx_path.exists():
        doc_summary["xlsx_found"] = True
        doc_summary["xlsx_info"] = parse_subject_info_excel(xlsx_path)

    return doc_summary


# Known candidate field roles mapping
CANDIDATE_FIELD_ROLES: Dict[str, Dict[str, str]] = {
    "vitalsig": {
        "role": "radar_vital_signal",
        "expected_unit": "mm",
        "semantic_desc": "Radar chest displacement vital signal (in mm)",
    },
    "radar.fs": {
        "role": "radar_sampling_frequency",
        "expected_unit": "Hz",
        "semantic_desc": "Radar sampling frequency (in Hz)",
    },
    "t_frame": {
        "role": "radar_sampling_interval",
        "expected_unit": "s",
        "semantic_desc": "Radar frame sampling interval (in s)",
    },
    "radar.t_frame": {
        "role": "radar_time_vector",
        "expected_unit": "s",
        "semantic_desc": "Radar time vector/series (in s)",
    },
    "hr": {
        "role": "reference_heart_rate",
        "expected_unit": "beats per minute",
        "semantic_desc": "Reference Heart Rate (in bpm)",
    },
    "rr": {
        "role": "reference_respiratory_rate",
        "expected_unit": "breaths per minute",
        "semantic_desc": "Reference Respiratory Rate (in breaths/min)",
    },
    "ecg_lead2": {
        "role": "reference_ecg",
        "expected_unit": "mV",
        "semantic_desc": "Reference ECG Lead II signal (in mV)",
    },
    "ecg_lead3": {
        "role": "reference_ecg",
        "expected_unit": "mV",
        "semantic_desc": "Reference ECG Lead III signal (in mV)",
    },
    "ecg_leadv1": {
        "role": "reference_ecg",
        "expected_unit": "mV",
        "semantic_desc": "Reference ECG Lead V1 signal (in mV)",
    },
    "respiration": {
        "role": "reference_respiration",
        "expected_unit": "unitless",
        "semantic_desc": "Reference respiratory signal (unitless)",
    },
    "pleth": {
        "role": "reference_ppg",
        "expected_unit": "%",
        "semantic_desc": "Reference PPG plethysmography signal (%)",
    },
    "fs_ecg": {
        "role": "reference_ecg_sampling_frequency",
        "expected_unit": "Hz",
        "semantic_desc": "ECG sampling frequency (in Hz)",
    },
    "fs_resp": {
        "role": "reference_resp_sampling_frequency",
        "expected_unit": "Hz",
        "semantic_desc": "Respiration sampling frequency (in Hz)",
    },
    "fs_pleth": {
        "role": "reference_ppg_sampling_frequency",
        "expected_unit": "Hz",
        "semantic_desc": "PPG sampling frequency (in Hz)",
    },
    "bps": {
        "role": "reference_bp_systolic",
        "expected_unit": "mmHg",
        "semantic_desc": "Systolic blood pressure (mmHg)",
    },
    "bpm": {
        "role": "reference_bp_mean",
        "expected_unit": "mmHg",
        "semantic_desc": "Mean blood pressure (mmHg)",
    },
    "bpd": {
        "role": "reference_bp_diastolic",
        "expected_unit": "mmHg",
        "semantic_desc": "Diastolic blood pressure (mmHg)",
    },
    "measurementinfo": {
        "role": "acquisition_metadata",
        "expected_unit": "text/metadata",
        "semantic_desc": "Acquisition metadata (Subject, timestamp, scenario)",
    },
}


def identify_candidate_fields(
    structure_records: List[Dict[str, Any]],
    doc_evidence: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Scan inspected structure records and identify candidate fields with documentation evidence."""
    candidate_records: List[Dict[str, Any]] = []

    # Prepare lookup of documented definitions
    doc_radar_params = {}
    doc_ref_params = {}
    if doc_evidence and doc_evidence.get("xlsx_info"):
        doc_radar_params = doc_evidence["xlsx_info"].get("radar_parameters", {})
        doc_ref_params = doc_evidence["xlsx_info"].get("reference_parameters", {})

    for rec in structure_records:
        var_path = rec["variable_path"]
        var_path_lower = var_path.lower()
        parts = var_path.split(".")
        parent_struct = ".".join(parts[:-1]) if len(parts) > 1 else "ROOT"
        leaf_name = parts[-1]
        leaf_lower = leaf_name.lower()

        # Check against candidate mapping
        matched_candidate = None
        matched_key = None
        if var_path_lower in CANDIDATE_FIELD_ROLES:
            matched_candidate = CANDIDATE_FIELD_ROLES[var_path_lower]
            matched_key = var_path
        elif leaf_lower in CANDIDATE_FIELD_ROLES:
            matched_candidate = CANDIDATE_FIELD_ROLES[leaf_lower]
            matched_key = leaf_name

        if matched_candidate:
            evidence_notes = []
            verif_status = "VERIFIED"

            # Check if documented in Radar Parameters or Reference Parameters
            doc_entry = doc_radar_params.get(matched_key) or doc_ref_params.get(matched_key)
            if not doc_entry:
                # Case insensitive search in doc entries
                for k, v in {**doc_radar_params, **doc_ref_params}.items():
                    if k.lower() == leaf_lower or k.lower() == var_path_lower:
                        doc_entry = v
                        break

            if doc_entry:
                evidence_notes.append(
                    f"Documented in Subject Information.xlsx: Full name='{doc_entry.get('full_name')}', Unit='{doc_entry.get('unit')}'"
                )
                verif_status = "VERIFIED"
            else:
                evidence_notes.append("Field observed in MATLAB structure; not explicitly defined in Excel sheets")
                verif_status = "UNVERIFIED"

            candidate_records.append({
                "relative_path": rec.get("relative_path", ""),
                "variable_path": var_path,
                "shape_as_read": rec.get("shape_as_read", ""),
                "dtype_as_read": rec.get("dtype_as_read", ""),
                "parent_structure": parent_struct,
                "candidate_role": matched_candidate["role"],
                "evidence": "; ".join(evidence_notes),
                "verification_status": verif_status,
                "notes": matched_candidate["semantic_desc"],
            })

    return candidate_records
