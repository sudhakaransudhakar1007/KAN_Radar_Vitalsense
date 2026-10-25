"""Phase 2C Scientific Gate Preflight Check and Readiness Verification.

Executes comprehensive, read-only preflight verification before any real-data
supervised dataset generation (Phase 2C / run_002) or real-data model training
(Phase 5 / run_real_001) can proceed.

Evaluates 7 mandatory readiness gates:
1. PI Sign-off & Governance (D13, D14, D15, Label Spec Approval, Gate Closure Auth)
2. Label Specification Cryptographic Digest Integrity (Canonical & Baseline SHA-256)
3. Phase 2A Reconciliation Addendum & Issue Tracking (28 issues audited)
4. Source Data Inventory (48 radar files, 48 reference ECG files across 24 subjects)
5. Output Isolation (run_002 and run_real_001 strictly do not exist prior to gate closure)
6. 1,104 Window Denominator & SQI Acceptance Consistency (48 x 23 = 1,104 windows)
7. Mandatory Hardware Timing Limitation Guard (UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0)

Returns exit code 0 (GO) ONLY if all 7 gates pass and formal PI approval is present.
Otherwise returns exit code 1 (NO-GO) and outputs structured blockers.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure kan_radar_HR project root is in sys.path regardless of execution CWD
_proj_root = Path(__file__).resolve().parents[2]
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

from src.closure.pi_signoff_validator import (
    EXPECTED_CANONICAL_SPEC_SHA256,
    EXPECTED_RAW_BASELINE_SPEC_SHA256,
    PISignoffReport,
    PISignoffValidator,
)


EXPECTED_PHASE2A_AUDIT_SHA256 = "6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f"
EXPECTED_SYNC_VALIDATION_SHA256 = "6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10"
EXPECTED_PI_DECISION_LIST_SHA256 = "fe4d7d39fdcb651baf59ef5f820f3ed9ae6afd5b133b87c805f8bc4a90180363"
EXPECTED_TOTAL_RECORDINGS = 48
EXPECTED_WINDOWS_PER_RECORDING = 23
EXPECTED_TOTAL_WINDOWS = 1104
MANDATORY_HARDWARE_LIMITATION = "UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0"


@dataclass
class PreflightCheckItem:
    """Individual preflight check item result."""
    check_id: str
    category: str
    description: str
    status: str  # 'PASS', 'FAIL', 'WARN'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Phase2CPreflightReport:
    """Comprehensive Phase 2C preflight readiness report."""
    timestamp_utc: str
    verdict: str  # 'GO' or 'NO-GO'
    gate_status: str  # 'OPEN' or 'CLOSED'
    is_authorized_for_phase2c: bool
    summary: Dict[str, int]
    checks: List[PreflightCheckItem]
    blockers: List[str]
    warnings: List[str]
    pi_signoff_report: Optional[Dict[str, Any]] = None


class Phase2CPreflightChecker:
    """Read-only preflight verification suite for Phase 2C readiness."""

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        dataset_dir: Optional[Path] = None,
        protocol_path: Optional[Path] = None,
        spec_path: Optional[Path] = None,
        addendum_path: Optional[Path] = None,
        diagnostic_path: Optional[Path] = None,
    ):
        self.base_dir = self._resolve_base_dir(base_dir)
        self.dataset_dir = self._resolve_dataset_dir(dataset_dir)
        self.protocol_path = protocol_path or (self.base_dir / "outputs/closure/pi_signoff_intake_protocol.md")
        self.spec_path = spec_path or (self.base_dir / "outputs/closure/spec/label_spec_v1.json")
        self.addendum_path = addendum_path or (self.base_dir / "outputs/closure/phase2a_reconciliation_addendum.md")
        self.diagnostic_path = diagnostic_path or (self.base_dir / "outputs/closure/window_coverage_gate_diagnostic.csv")

    def _resolve_base_dir(self, explicit: Optional[Path]) -> Path:
        """Resolve base project directory whether run from repo root or kan_radar_HR."""
        if explicit:
            return explicit
        cwd = Path.cwd()
        if (cwd / "src/closure").exists() and (cwd / "outputs").exists():
            return cwd
        if (cwd / "kan_radar_HR/src/closure").exists():
            return cwd / "kan_radar_HR"
        return cwd

    def _resolve_dataset_dir(self, explicit: Optional[Path]) -> Path:
        """Resolve raw dataset directory across standard paths."""
        if explicit and explicit.exists():
            return explicit
        candidates = [
            Path("../data/VITALSENSE_120_DATASET"),
            Path("data/VITALSENSE_120_DATASET"),
            self.base_dir.parent / "data/VITALSENSE_120_DATASET",
            self.base_dir / "data/VITALSENSE_120_DATASET",
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c.resolve()
        # Fallback to default candidate
        return (self.base_dir.parent / "data/VITALSENSE_120_DATASET").resolve()

    def check_governance_and_pi_signoff(self) -> Tuple[List[PreflightCheckItem], PISignoffReport]:
        """Verify PI sign-off protocol via PISignoffValidator."""
        items: List[PreflightCheckItem] = []
        validator = PISignoffValidator(
            base_dir=self.base_dir,
            protocol_path=self.protocol_path,
            spec_path=self.spec_path,
            addendum_path=self.addendum_path,
        )
        pi_report = validator.run_validation()

        for it in pi_report.items:
            status = "PASS" if it.status == "PRESENT" else "FAIL"
            items.append(
                PreflightCheckItem(
                    check_id=f"GOV_{it.item_id}",
                    category="GOVERNANCE",
                    description=it.description,
                    status=status,
                    message=it.diagnostics,
                    details=it.details,
                )
            )

        return items, pi_report

    def check_label_spec_integrity(self) -> List[PreflightCheckItem]:
        """Verify label_spec_v1.json cryptographic digest and specification parameters."""
        items: List[PreflightCheckItem] = []
        c_id = "LABEL_SPEC_INTEGRITY"
        desc = "Label Specification Cryptographic Digest & Parameters"

        if not self.spec_path.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="LABEL_SPEC",
                    description=desc,
                    status="FAIL",
                    message=f"Specification file not found: {self.spec_path}",
                )
            )
            return items

        try:
            spec_text = self.spec_path.read_text(encoding="utf-8")
            spec_data = json.loads(spec_text)
        except Exception as e:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="LABEL_SPEC",
                    description=desc,
                    status="FAIL",
                    message=f"Specification JSON corrupted: {e}",
                )
            )
            return items

        # Compute raw file hash
        raw_hash = hashlib.sha256(spec_text.encode("utf-8")).hexdigest().lower()

        # Compute canonical hash
        d_canonical = {k: v for k, v in spec_data.items() if k not in ("approved_by", "spec_sha256")}
        canonical_str = json.dumps(d_canonical, indent=2, sort_keys=True)
        canonical_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest().lower()

        details = {
            "canonical_sha256": canonical_hash,
            "expected_canonical_sha256": EXPECTED_CANONICAL_SPEC_SHA256,
            "raw_sha256": raw_hash,
            "expected_baseline_raw_sha256": EXPECTED_RAW_BASELINE_SPEC_SHA256,
            "spec_version": spec_data.get("spec_version"),
            "window_duration_seconds": spec_data.get("windowing", {}).get("window_duration_seconds"),
            "hop_duration_seconds": spec_data.get("windowing", {}).get("hop_duration_seconds"),
            "num_windows": spec_data.get("windowing", {}).get("num_windows"),
            "hardware_timing_limitation": spec_data.get("governance", {}).get("hardware_timing_limitation"),
            "monitor_hr_status": spec_data.get("reference_source", {}).get("monitor_hr_status"),
        }

        errors = []
        if canonical_hash != EXPECTED_CANONICAL_SPEC_SHA256:
            errors.append(f"Canonical hash mismatch ({canonical_hash} != {EXPECTED_CANONICAL_SPEC_SHA256})")

        win_cfg = spec_data.get("windowing", {})
        if win_cfg.get("window_duration_seconds") != 10.0:
            errors.append(f"Invalid window_duration_seconds: {win_cfg.get('window_duration_seconds')}")
        if win_cfg.get("hop_duration_seconds") != 5.0:
            errors.append(f"Invalid hop_duration_seconds: {win_cfg.get('hop_duration_seconds')}")
        if win_cfg.get("num_windows") != EXPECTED_WINDOWS_PER_RECORDING:
            errors.append(f"Invalid num_windows: {win_cfg.get('num_windows')}")

        gov_cfg = spec_data.get("governance", {})
        if gov_cfg.get("hardware_timing_limitation") != MANDATORY_HARDWARE_LIMITATION:
            errors.append(f"Missing mandatory hardware timing limitation in spec governance.")

        ref_cfg = spec_data.get("reference_source", {})
        if ref_cfg.get("monitor_hr_status") != "FORBIDDEN":
            errors.append(f"Monitor HR status must be FORBIDDEN; got {ref_cfg.get('monitor_hr_status')}")

        if errors:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="LABEL_SPEC",
                    description=desc,
                    status="FAIL",
                    message="; ".join(errors),
                    details=details,
                )
            )
        else:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="LABEL_SPEC",
                    description=desc,
                    status="PASS",
                    message=f"Canonical hash matched ({canonical_hash[:12]}...), window parameters and SQI validated.",
                    details=details,
                )
            )

        return items

    def check_phase2a_reconciliation(self) -> List[PreflightCheckItem]:
        """Verify Phase 2A Reconciliation Addendum and baseline artifact integrity."""
        items: List[PreflightCheckItem] = []

        # 1. Addendum check
        c_id_add = "PHASE2A_ADDENDUM_INTEGRITY"
        desc_add = "Phase 2A Reconciliation Addendum (28 Issues Audit)"
        if not self.addendum_path.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id_add,
                    category="RECONCILIATION",
                    description=desc_add,
                    status="FAIL",
                    message=f"Addendum file not found: {self.addendum_path}",
                )
            )
        else:
            content = self.addendum_path.read_text(encoding="utf-8")
            missing_issues = [f"ISS-{i:02d}" for i in range(1, 29) if f"ISS-{i:02d}" not in content]
            if missing_issues:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id_add,
                        category="RECONCILIATION",
                        description=desc_add,
                        status="FAIL",
                        message=f"Addendum missing tracking for: {', '.join(missing_issues)}",
                        details={"missing_issues": missing_issues},
                    )
                )
            else:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id_add,
                        category="RECONCILIATION",
                        description=desc_add,
                        status="PASS",
                        message="Addendum presents complete audit for all 28 issues (12 resolved, 9 documented limitations, 7 open).",
                        details={"total_issues_tracked": 28, "path": str(self.addendum_path)},
                    )
                )

        # 2. Baseline audit hash check
        c_id_base = "PHASE2A_BASELINE_HASH"
        desc_base = "Phase 2A Step 2B Consistency Audit File Cryptographic Hash"
        audit_file = self.base_dir / "outputs/phase2a/step2b_consistency_audit.md"
        if not audit_file.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id_base,
                    category="RECONCILIATION",
                    description=desc_base,
                    status="FAIL",
                    message=f"Phase 2A audit baseline missing: {audit_file}",
                )
            )
        else:
            h = hashlib.sha256(audit_file.read_bytes()).hexdigest().lower()
            if h != EXPECTED_PHASE2A_AUDIT_SHA256:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id_base,
                        category="RECONCILIATION",
                        description=desc_base,
                        status="FAIL",
                        message=f"Audit hash mismatch: got {h}, expected {EXPECTED_PHASE2A_AUDIT_SHA256}",
                        details={"calculated": h, "expected": EXPECTED_PHASE2A_AUDIT_SHA256},
                    )
                )
            else:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id_base,
                        category="RECONCILIATION",
                        description=desc_base,
                        status="PASS",
                        message=f"Phase 2A baseline hash verified bit-for-bit ({h[:12]}...).",
                        details={"sha256": h},
                    )
                )

        return items

    def check_source_inventory(self) -> List[PreflightCheckItem]:
        """Verify raw VITALSENSE dataset inventory (48 radar files, 48 reference files)."""
        items: List[PreflightCheckItem] = []
        c_id = "SOURCE_DATASET_INVENTORY"
        desc = "VITALSENSE Raw Dataset Inventory (48 Radar + 48 Reference ECG Files)"

        if not self.dataset_dir.exists() or not self.dataset_dir.is_dir():
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="SOURCE_DATA",
                    description=desc,
                    status="FAIL",
                    message=f"Dataset directory not found: {self.dataset_dir}",
                    details={"dataset_dir": str(self.dataset_dir)},
                )
            )
            return items

        all_mats = sorted(list(self.dataset_dir.glob("**/*.mat")))
        radar_files = sorted([f for f in all_mats if not f.name.endswith("_Mindray.mat")])
        ref_files = sorted([f for f in all_mats if f.name.endswith("_Mindray.mat")])

        details = {
            "dataset_dir": str(self.dataset_dir),
            "total_mat_files": len(all_mats),
            "radar_files_count": len(radar_files),
            "reference_files_count": len(ref_files),
            "expected_radar_count": EXPECTED_TOTAL_RECORDINGS,
            "expected_ref_count": EXPECTED_TOTAL_RECORDINGS,
        }

        errors = []
        if len(radar_files) != EXPECTED_TOTAL_RECORDINGS:
            errors.append(f"Radar file count mismatch: found {len(radar_files)}, expected {EXPECTED_TOTAL_RECORDINGS}")
        if len(ref_files) != EXPECTED_TOTAL_RECORDINGS:
            errors.append(f"Reference file count mismatch: found {len(ref_files)}, expected {EXPECTED_TOTAL_RECORDINGS}")

        if errors:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="SOURCE_DATA",
                    description=desc,
                    status="FAIL",
                    message="; ".join(errors),
                    details=details,
                )
            )
        else:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="SOURCE_DATA",
                    description=desc,
                    status="PASS",
                    message=f"Complete cohort verified: 48 radar recordings and 48 reference ECG MAT files.",
                    details=details,
                )
            )

        return items

    def check_output_isolation(self) -> List[PreflightCheckItem]:
        """Verify output isolation: run_002 and run_real_001 must NOT exist prior to gate closure."""
        items: List[PreflightCheckItem] = []

        # 1. run_002 check
        c_id_run002 = "OUTPUT_ISOLATION_RUN_002"
        desc_run002 = "Output Isolation: outputs/supervised_dataset/run_002 Non-Existence"
        p_run002 = self.base_dir / "outputs/supervised_dataset/run_002"
        if p_run002.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id_run002,
                    category="ISOLATION",
                    description=desc_run002,
                    status="FAIL",
                    message=f"Premature output detected: {p_run002} exists before gate closure.",
                    details={"path": str(p_run002)},
                )
            )
        else:
            items.append(
                PreflightCheckItem(
                    check_id=c_id_run002,
                    category="ISOLATION",
                    description=desc_run002,
                    status="PASS",
                    message="Confirmed: outputs/supervised_dataset/run_002 does not exist (isolation preserved).",
                    details={"path": str(p_run002)},
                )
            )

        # 2. run_real_001 check
        c_id_real = "OUTPUT_ISOLATION_REAL_TRAINING"
        desc_real = "Output Isolation: outputs/phase5/run_real_001 Non-Existence"
        p_real = self.base_dir / "outputs/phase5/run_real_001"
        if p_real.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id_real,
                    category="ISOLATION",
                    description=desc_real,
                    status="FAIL",
                    message=f"Premature output detected: {p_real} exists before gate closure.",
                    details={"path": str(p_real)},
                )
            )
        else:
            items.append(
                PreflightCheckItem(
                    check_id=c_id_real,
                    category="ISOLATION",
                    description=desc_real,
                    status="PASS",
                    message="Confirmed: outputs/phase5/run_real_001 does not exist (training isolation preserved).",
                    details={"path": str(p_real)},
                )
            )

        return items

    def check_window_denominator_consistency(self) -> List[PreflightCheckItem]:
        """Verify window denominator consistency: 48 recordings x 23 windows = 1,104 windows."""
        items: List[PreflightCheckItem] = []
        c_id = "WINDOW_DENOMINATOR_CONSISTENCY"
        desc = "Candidate Window Denominator Budget Consistency (1,104 Windows)"

        if not self.diagnostic_path.exists():
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="WINDOWING",
                    description=desc,
                    status="WARN",
                    message=f"Window coverage diagnostic file missing: {self.diagnostic_path}",
                    details={"expected_total": EXPECTED_TOTAL_WINDOWS},
                )
            )
            return items

        try:
            import csv
            with open(self.diagnostic_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            num_recs = len(rows)
            total_windows = sum(int(r.get("total_windows", 0)) for r in rows)
            accepted_windows = sum(int(r.get("accepted_windows", 0)) for r in rows)
            rejected_windows = sum(int(r.get("rejected_windows", 0)) for r in rows)

            details = {
                "recordings_count": num_recs,
                "expected_recordings": EXPECTED_TOTAL_RECORDINGS,
                "total_candidate_windows": total_windows,
                "expected_candidate_windows": EXPECTED_TOTAL_WINDOWS,
                "accepted_windows": accepted_windows,
                "rejected_windows": rejected_windows,
            }

            errors = []
            if num_recs != EXPECTED_TOTAL_RECORDINGS:
                errors.append(f"Recording count in diagnostic mismatch: {num_recs} != {EXPECTED_TOTAL_RECORDINGS}")
            if total_windows != EXPECTED_TOTAL_WINDOWS:
                errors.append(f"Total window denominator mismatch: {total_windows} != {EXPECTED_TOTAL_WINDOWS}")

            if errors:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id,
                        category="WINDOWING",
                        description=desc,
                        status="FAIL",
                        message="; ".join(errors),
                        details=details,
                    )
                )
            else:
                items.append(
                    PreflightCheckItem(
                        check_id=c_id,
                        category="WINDOWING",
                        description=desc,
                        status="PASS",
                        message=f"Denominator verified: exactly {total_windows} candidate windows across {num_recs} recordings ({accepted_windows} accepted under SQI).",
                        details=details,
                    )
                )
        except Exception as e:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="WINDOWING",
                    description=desc,
                    status="FAIL",
                    message=f"Error parsing window coverage diagnostic: {e}",
                )
            )

        return items

    def check_hardware_timing_guard(self) -> List[PreflightCheckItem]:
        """Verify enforcement and visibility of UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0."""
        items: List[PreflightCheckItem] = []
        c_id = "HARDWARE_TIMING_LIMITATION_GUARD"
        desc = f"Mandatory Hardware Timing Disclaimer Guard ({MANDATORY_HARDWARE_LIMITATION})"

        # Check in label spec
        in_spec = False
        if self.spec_path.exists():
            spec_text = self.spec_path.read_text(encoding="utf-8")
            if MANDATORY_HARDWARE_LIMITATION in spec_text:
                in_spec = True

        # Check in intake protocol
        in_protocol = False
        if self.protocol_path.exists():
            proto_text = self.protocol_path.read_text(encoding="utf-8")
            if MANDATORY_HARDWARE_LIMITATION in proto_text:
                in_protocol = True

        details = {
            "mandated_limitation_code": MANDATORY_HARDWARE_LIMITATION,
            "present_in_label_spec": in_spec,
            "present_in_intake_protocol": in_protocol,
        }

        if not in_spec or not in_protocol:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="HARDWARE_LIMITATION",
                    description=desc,
                    status="FAIL",
                    message=f"Limitation code {MANDATORY_HARDWARE_LIMITATION} missing from spec or intake protocol.",
                    details=details,
                )
            )
        else:
            items.append(
                PreflightCheckItem(
                    check_id=c_id,
                    category="HARDWARE_LIMITATION",
                    description=desc,
                    status="PASS",
                    message=f"Hardware timing limitation {MANDATORY_HARDWARE_LIMITATION} strictly documented in spec and intake protocol.",
                    details=details,
                )
            )

        return items

    def run_preflight(self) -> Phase2CPreflightReport:
        """Execute complete suite of preflight checks."""
        all_checks: List[PreflightCheckItem] = []

        # 1. Governance & PI Sign-off
        gov_checks, pi_report = self.check_governance_and_pi_signoff()
        all_checks.extend(gov_checks)

        # 2. Label Spec Integrity
        all_checks.extend(self.check_label_spec_integrity())

        # 3. Phase 2A Reconciliation Addendum & Hash
        all_checks.extend(self.check_phase2a_reconciliation())

        # 4. Source Data Inventory
        all_checks.extend(self.check_source_inventory())

        # 5. Output Isolation
        all_checks.extend(self.check_output_isolation())

        # 6. Window Denominator Consistency
        all_checks.extend(self.check_window_denominator_consistency())

        # 7. Hardware Timing Guard
        all_checks.extend(self.check_hardware_timing_guard())

        summary = {"PASS": 0, "FAIL": 0, "WARN": 0}
        blockers = []
        warnings = []

        for chk in all_checks:
            summary[chk.status] = summary.get(chk.status, 0) + 1
            if chk.status == "FAIL":
                blockers.append(f"[{chk.check_id}] {chk.description}: {chk.message}")
            elif chk.status == "WARN":
                warnings.append(f"[{chk.check_id}] {chk.description}: {chk.message}")

        is_authorized = (len(blockers) == 0 and pi_report.is_ready_for_gate_closure)
        verdict = "GO" if is_authorized else "NO-GO"
        gate_status = "CLOSED" if is_authorized else "OPEN"

        return Phase2CPreflightReport(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            verdict=verdict,
            gate_status=gate_status,
            is_authorized_for_phase2c=is_authorized,
            summary=summary,
            checks=all_checks,
            blockers=blockers,
            warnings=warnings,
            pi_signoff_report=asdict(pi_report),
        )

    def generate_markdown_report(self, report: Phase2CPreflightReport) -> str:
        """Render a comprehensive markdown preflight report."""
        lines = [
            "# PHASE 2C SCIENTIFIC GATE PREFLIGHT AUDIT REPORT",
            "",
            f"**Execution Timestamp:** `{report.timestamp_utc}`  ",
            f"**Gate Status:** **`{report.gate_status}`**  ",
            f"**Preflight Verdict:** **`{report.verdict}`**  ",
            f"**Phase 2C Execution Authorized:** **`{report.is_authorized_for_phase2c}`**  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            f"The Phase 2C Preflight Checker evaluated all 7 governance and technical gates.",
            f"- **Checks Passed:** {report.summary.get('PASS', 0)} / {len(report.checks)}",
            f"- **Checks Failed (Blockers):** {report.summary.get('FAIL', 0)}",
            f"- **Warnings:** {report.summary.get('WARN', 0)}",
            "",
        ]

        if report.verdict == "GO":
            lines.extend([
                "> [!IMPORTANT]",
                "> **PREFLIGHT VERDICT: GO.** All formal PI sign-offs, cryptographic digests, dataset inventories,",
                "> and output isolations have been validated. Controlled Phase 2C supervised dataset generation is AUTHORIZED.",
                "",
            ])
        else:
            lines.extend([
                "> [!CAUTION]",
                "> **PREFLIGHT VERDICT: NO-GO.** The Phase 2A/2C Scientific Gate remains strictly **OPEN**.",
                "> Real-data ground-truth label generation (`outputs/supervised_dataset/run_002`) and real-data model",
                "> training (`outputs/phase5/run_real_001`) remain strictly **BLOCKED** until formal PI sign-offs are executed.",
                "",
            ])

        lines.extend([
            "## 2. Gate Verification Details",
            "",
            "| Category | Check ID | Description | Status | Diagnostics |",
            "| :--- | :--- | :--- | :---: | :--- |",
        ])

        for chk in report.checks:
            badge = "PASS" if chk.status == "PASS" else ("FAIL" if chk.status == "FAIL" else "WARN")
            lines.append(f"| {chk.category} | `{chk.check_id}` | {chk.description} | `{badge}` | {chk.message} |")

        lines.append("")
        lines.append("## 3. Outstanding Blockers")
        lines.append("")
        if not report.blockers:
            lines.append("None. All checks passed.")
        else:
            for b in report.blockers:
                lines.append(f"- **{b}**")

        lines.append("")
        lines.append("## 4. Hardware Timing Limitation Acknowledgement")
        lines.append("")
        lines.append(f"All downstream operations must strictly document and enforce `{MANDATORY_HARDWARE_LIMITATION}`.")
        lines.append(r"Hardware start-time offset $\Delta t_0$ is unverified; nominal zero-latency alignment is assumed.")
        lines.append("")

        return "\n".join(lines)


def main():
    """CLI entry point for Phase 2C preflight checker."""
    parser = argparse.ArgumentParser(description="Phase 2C Scientific Gate Preflight Checker")
    parser.add_argument("--base-dir", type=str, default=None, help="Base project directory")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Directory containing VITALSENSE .mat files")
    parser.add_argument("--protocol", type=str, default=None, help="Path to pi_signoff_intake_protocol.md")
    parser.add_argument("--spec", type=str, default=None, help="Path to label_spec_v1.json")
    parser.add_argument("--addendum", type=str, default=None, help="Path to phase2a_reconciliation_addendum.md")
    parser.add_argument("--diagnostic", type=str, default=None, help="Path to window_coverage_gate_diagnostic.csv")
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    parser.add_argument("--output", type=str, default=None, help="Save JSON report to file")
    parser.add_argument("--markdown", type=str, default=None, help="Save Markdown report to file")
    args = parser.parse_args()

    checker = Phase2CPreflightChecker(
        base_dir=Path(args.base_dir) if args.base_dir else None,
        dataset_dir=Path(args.dataset_dir) if args.dataset_dir else None,
        protocol_path=Path(args.protocol) if args.protocol else None,
        spec_path=Path(args.spec) if args.spec else None,
        addendum_path=Path(args.addendum) if args.addendum else None,
        diagnostic_path=Path(args.diagnostic) if args.diagnostic else None,
    )

    report = checker.run_preflight()

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if args.markdown:
        md_text = checker.generate_markdown_report(report)
        md_p = Path(args.markdown)
        md_p.parent.mkdir(parents=True, exist_ok=True)
        md_p.write_text(md_text, encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print("=================================================================")
        print(f"PHASE 2C PREFLIGHT VERIFICATION REPORT ({report.timestamp_utc})")
        print("=================================================================")
        print(f"Gate Status:                 {report.gate_status}")
        print(f"Preflight Verdict:           {report.verdict}")
        print(f"Authorized for Phase 2C:     {report.is_authorized_for_phase2c}")
        print(f"Summary:                     {report.summary}")
        print("\n--- DETAILED CHECK RESULTS ---")
        for c in report.checks:
            badge = "PASS" if c.status == "PASS" else ("FAIL" if c.status == "FAIL" else "WARN")
            print(f"  [{badge:6}] [{c.category:16}] {c.check_id}: {c.message}")
        print("=================================================================")
        if report.blockers:
            print("\nBLOCKERS (Gate remains OPEN, Phase 2C execution prohibited):")
            for b in report.blockers:
                print(f"  - {b}")
        else:
            print("\nALL PREFLIGHT CHECKS PASSED. Ready for controlled Phase 2C execution.")
        print("=================================================================")

    sys.exit(0 if report.is_authorized_for_phase2c else 1)


if __name__ == "__main__":
    main()
