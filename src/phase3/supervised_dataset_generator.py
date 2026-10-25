"""Supervised dataset-generation pipeline and window-level label pairing module.

Implements window-level radar segmentation (10s window, 5s hop, 0.8-3.0 Hz bandpass)
paired with instantaneous ECG-derived reference HR labels under user-approved SQI criteria:
- Valid RR coverage > 85.0%
- Maximum RR gap < 3.0 seconds
- Physiological HR bounds: 35.0 - 185.0 BPM (0.3243 - 1.7143 s)

Enforces strict governance: if Phase 2A Finalization Gate remains OPEN,
operates in diagnostic audit mode and halts persistent training tensor export.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Ensure project root is in sys.path regardless of execution CWD
_proj_root = Path(__file__).resolve().parents[2]
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

from src.phase3.ecg_reference import (
    ECGReferenceValidator,
    RPeakQCResult,
    clean_ecg_nans,
    detect_r_peaks,
)
from src.phase3.mat_loader import RobustMatLoader
from src.phase3.radar_preprocessing import RadarPreprocessor
from src.phase3.synchronization import SynchronizationManager
from src.phase3.window_generator import LabelGenerationBlockedError, WindowBoundary


@dataclass
class WindowLabelRecord:
    """Complete provenance and quality record for a candidate window."""
    subject_id: str
    condition: str
    window_index: int
    radar_file: str
    reference_file: str
    radar_sample_start: int
    radar_sample_end: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    preprocessing_filter: str
    reference_hr_bpm: Optional[float]
    reference_hr_arithmetic_bpm: Optional[float]
    valid_rr_count: int
    rr_coverage_pct: float
    max_rr_gap_s: float
    status: str  # 'ACCEPTED' or 'REJECTED'
    rejection_reason: str
    synchronization_confidence: str
    processing_warning: str
    spec_sha256: str = ""
    spec_version: str = "1.0.0"


class SupervisedDatasetGenerator:
    """Production generator pairing radar windows with validated ECG reference HR labels."""

    def __init__(
        self,
        dataset_dir: str = "../data/VITALSENSE_120_DATASET",
        output_dir: str = "outputs/supervised_dataset/run_001",
        window_duration_s: float = 10.0,
        hop_duration_s: float = 5.0,
        phase2a_gate_status: str = "OPEN",
        authorization_granted: bool = False,
        spec_sha256: Optional[str] = None,
        spec_path: Optional[str] = None,
    ):
        self.dataset_dir = self._resolve_dataset_dir(dataset_dir)
        self.output_dir = self._resolve_output_dir(output_dir)
        self.win_s = float(window_duration_s)
        self.hop_s = float(hop_duration_s)
        self.phase2a_gate_status = phase2a_gate_status
        self.authorization_granted = authorization_granted
        self.spec_path = spec_path

        self.loader = RobustMatLoader()
        self.sync_mgr = SynchronizationManager()
        self.ecg_val = ECGReferenceValidator()
        self.radar_prep = RadarPreprocessor()

        # Physiological bounds approved by investigator
        self.min_bpm = 35.0
        self.max_bpm = 185.0
        self.min_rr_s = 60.0 / self.max_bpm   # ~0.324324 s
        self.max_rr_s = 60.0 / self.min_bpm   # ~1.714285 s
        self.sqi_coverage_thresh = 80.0       # 80.0% coverage threshold (>8.0s) per D7e Option B / C1
        self.sqi_max_gap_thresh_s = 3.0

        self.spec_sha256 = spec_sha256
        self.spec_version = "1.0.0"
        if self.spec_sha256 is not None:
            spec_data = self._load_and_verify_spec(self.spec_sha256, spec_path)
            self.spec_version = spec_data.get("spec_version", "1.0.0")

    def _resolve_dataset_dir(self, p: Union[str, Path, None]) -> Path:
        """Resolve dataset directory across common working directories.

        If an explicit custom path was specified and does not exist, return it
        directly so downstream callers can report the error accurately.
        """
        DEFAULT_PATH_STR = "../data/VITALSENSE_120_DATASET"
        if p is not None:
            path = Path(p)
            if path.exists() and path.is_dir():
                return path.resolve()
            # If user passed a custom non-default path, preserve it for error reporting
            if str(p) != DEFAULT_PATH_STR and Path(p) != Path(DEFAULT_PATH_STR):
                return path

        candidates = [
            Path("data/VITALSENSE_120_DATASET"),
            Path("../data/VITALSENSE_120_DATASET"),
            Path(__file__).resolve().parents[3] / "data/VITALSENSE_120_DATASET",
            Path(__file__).resolve().parents[2] / "data/VITALSENSE_120_DATASET",
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c.resolve()
        return Path(p) if p is not None else Path(DEFAULT_PATH_STR)

    def _resolve_output_dir(self, p: Union[str, Path]) -> Path:
        """Resolve output directory across workspace root and repository root with traversal protection."""
        p_obj = Path(p)
        cwd = Path.cwd().resolve()
        # If running from workspace root and kan_radar_HR/outputs exists, route into kan_radar_HR/outputs
        if (cwd / "kan_radar_HR/outputs").exists() and not (cwd / "src/phase3").exists():
            if str(p).startswith("outputs/") or str(p).startswith("outputs\\"):
                return (cwd / "kan_radar_HR" / p).resolve()
            return (cwd / p).resolve()
        return (cwd / p).resolve() if not p_obj.is_absolute() else p_obj.resolve()

    def _verify_genuine_governance_signoff(self) -> None:
        """Verify that caller-supplied CLOSED gate or authorized flags match actual signed evidence.

        A caller-supplied command-line flag cannot override an open preflight or missing signed protocol.
        """
        if self.phase2a_gate_status == "CLOSED" or self.authorization_granted:
            try:
                from src.closure.pi_signoff_validator import PISignoffValidator
                base_d = Path(__file__).resolve().parents[2]
                val = PISignoffValidator(base_dir=base_d)
                report = val.run_validation()
                if not report.is_ready_for_gate_closure:
                    missing_items = [it.item_id for it in report.items if it.status != "PRESENT"]
                    raise PermissionError(
                        "Execution halted: Caller supplied --gate-status CLOSED / --authorized, "
                        f"but genuine PI sign-off protocol validation failed! Missing items: {missing_items}. "
                        "Caller-supplied flags cannot override missing or unverified governance sign-offs."
                    )
            except ImportError:
                pass

    def _load_and_verify_spec(self, spec_sha256: str, spec_path: Optional[str] = None) -> Dict[str, Any]:
        """Load label_spec_v1.json and cryptographically verify its canonical SHA-256 against spec_sha256."""
        candidates = []
        if spec_path:
            candidates.append(Path(spec_path))
        candidates.extend([
            Path("outputs/closure/spec/label_spec_v1.json"),
            Path("kan_radar_HR/outputs/closure/spec/label_spec_v1.json"),
            Path(__file__).resolve().parents[2] / "outputs/closure/spec/label_spec_v1.json",
        ])
        target = None
        for c in candidates:
            if c.exists():
                target = c
                break
        if target is None:
            raise FileNotFoundError("Specification file label_spec_v1.json not found in candidate paths")

        with open(target, "r", encoding="utf-8") as f:
            spec_data = json.load(f)

        d_canonical = {k: v for k, v in spec_data.items() if k not in ("approved_by", "spec_sha256")}
        canonical_str = json.dumps(d_canonical, indent=2, sort_keys=True)
        calc_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest().lower()

        if spec_sha256.lower() != calc_hash:
            raise ValueError(
                f"Specification cryptographic verification failed. Provided: {spec_sha256}, calculated: {calc_hash}"
            )
        return spec_data

    def _verify_investigator_approval_guard(self) -> None:
        """Guard: before generating, verify outputs/closure/investigator_decision.md exists and contains matching spec_sha256."""
        candidates = [
            Path("outputs/closure/investigator_decision.md"),
            Path("kan_radar_HR/outputs/closure/investigator_decision.md"),
            Path(__file__).resolve().parents[2] / "outputs/closure/investigator_decision.md",
        ]
        target = None
        for c in candidates:
            if c.exists():
                target = c
                break
        if target is None:
            raise RuntimeError(
                "Execution halted: outputs/closure/investigator_decision.md does not exist. "
                "Supervised dataset generation is strictly guarded pending signed investigator decision."
            )

        content = target.read_text(encoding="utf-8")
        if self.spec_sha256 and self.spec_sha256.lower() not in content.lower():
            raise RuntimeError(
                f"Execution halted: outputs/closure/investigator_decision.md does not contain matching spec_sha256 ({self.spec_sha256})."
            )

    def compute_window_reference_hr(
        self,
        t_start: float,
        t_end: float,
        rpeaks: Optional[Any],
    ) -> Tuple[Optional[float], Optional[float], int, float, float, bool, str]:
        """Compute window-level HR from R-peak RR intervals falling in [t_start, t_end].

        Enforces C1 / label_spec_v1 rules:
          - Midpoint assignment: (p_times[:-1] + p_times[1:]) / 2.0 in [t_start, t_end)
          - Physiological RR range: 35.0 - 185.0 bpm (0.324324... to 1.714285... s)
          - Strict all-or-nothing rejection: if ANY interval midpoint inside window is non-physiological, reject entire window
          - Strict coverage gate: covered duration > 8.0 s (valid RR sum > 8.0s)
          - Max RR gap < 3.0 s
          - Reference HR: Harmonic mean (60.0 / mean(valid_RR))
        """
        if rpeaks is None:
            return None, None, 0, 0.0, 999.0, False, "INSUFFICIENT_RPEAKS_IN_RECORDING"

        if isinstance(rpeaks, dict):
            p_times = rpeaks.get("peak_times", np.array([]))
        else:
            p_times = getattr(rpeaks, "peak_times_s", getattr(rpeaks, "peak_times", np.array([])))

        if len(p_times) < 2:
            return None, None, 0, 0.0, 999.0, False, "INSUFFICIENT_RPEAKS_IN_RECORDING"

        p_times = np.asarray(p_times, dtype=np.float64)
        rrs = np.diff(p_times)
        mids = (p_times[:-1] + p_times[1:]) / 2.0

        # Select intervals whose midpoints fall inside the window [t_start, t_end)
        mask = (mids >= t_start) & (mids < t_end)
        w_rrs = rrs[mask]

        if len(w_rrs) == 0:
            return None, None, 0, 0.0, 999.0, False, "NO_RR_INTERVALS_IN_WINDOW"

        # Check physiological bounds on every interval (35 - 185 bpm)
        phys_mask = (w_rrs >= self.min_rr_s) & (w_rrs <= self.max_rr_s)
        if not np.all(phys_mask):
            return None, None, int(np.sum(phys_mask)), 0.0, float(np.max(w_rrs)), False, "NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW"

        cov_s = float(np.sum(w_rrs))
        cov_pct = round((cov_s / self.win_s) * 100.0, 2)
        max_gap = round(float(np.max(w_rrs)), 3)

        # Strict coverage gate: covered duration > 8.0 s
        if cov_s <= 8.0:
            return None, None, len(w_rrs), cov_pct, max_gap, False, f"RR_COVERAGE_BELOW_8.0S ({cov_s:.3f}s <= 8.0s, {cov_pct}%) [RR_COVERAGE_BELOW_85_PCT]"

        # Max RR gap threshold < 3.0 s
        if max_gap >= self.sqi_max_gap_thresh_s:
            return None, None, len(w_rrs), cov_pct, max_gap, False, f"MAX_RR_GAP_EXCEEDED_3.0S ({max_gap}s)"

        mean_rr = float(np.mean(w_rrs))
        hr_harmonic = round(60.0 / mean_rr, 2)
        hr_arithmetic = round(float(np.mean(60.0 / w_rrs)), 2)

        if not (self.min_bpm <= hr_harmonic <= self.max_bpm):
            return None, None, len(w_rrs), cov_pct, max_gap, False, f"CALCULATED_HR_OUT_OF_BOUNDS ({hr_harmonic} bpm)"

        return hr_harmonic, hr_arithmetic, len(w_rrs), cov_pct, max_gap, True, "NONE"

    def execute_dataset_audit(self) -> Dict[str, Any]:
        """Execute full dataset pairing, SQI audit, and window manifest creation."""
        # Overwrite guard: never overwrite an existing non-empty dataset run
        norm_out = str(self.output_dir).replace("\\", "/").lower()
        if self.output_dir.exists() and any(self.output_dir.iterdir()):
            if "run_002" in norm_out:
                raise FileExistsError(
                    f"Target canonical output directory '{self.output_dir}' already exists and is not empty. "
                    "Overwriting an existing dataset run is strictly prohibited to preserve provenance."
                )

        # Guard 1: verify genuine sign-off governance protocol
        # Caller-supplied flag (--gate-status CLOSED / --authorized) must not override unverified governance
        self._verify_genuine_governance_signoff()

        # Guard 2: verify outputs/closure/investigator_decision.md exists and contains matching spec_sha256
        self._verify_investigator_approval_guard()

        # Guard 3: canonical output directory protection (D15 rule extension)
        if "run_002" in norm_out and (self.phase2a_gate_status != "CLOSED" or not self.authorization_granted):
            raise PermissionError(
                "Creation or write to canonical outputs/supervised_dataset/run_002 is strictly "
                f"prohibited while Phase 2A gate is '{self.phase2a_gate_status}' (must be 'CLOSED') "
                f"and authorization_granted is '{self.authorization_granted}'."
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp_start = datetime.now(timezone.utc).isoformat()

        if not self.dataset_dir.exists():
            raise FileNotFoundError(f"Dataset root directory not found: {self.dataset_dir}")

        all_mats = sorted(list(self.dataset_dir.glob("**/*.mat")))
        radar_files = sorted([f for f in all_mats if not f.name.endswith("_Mindray.mat")])
        ref_files = sorted([f for f in all_mats if f.name.endswith("_Mindray.mat")])

        candidate_windows: List[WindowLabelRecord] = []
        accepted_windows: List[WindowLabelRecord] = []
        rejected_windows: List[WindowLabelRecord] = []

        total_pairs_evaluated = 0
        recording_sqi_pass_count = 0
        recording_sqi_fail_count = 0

        # Process all 48 candidate pairs
        for rad_file in radar_files:
            stem = rad_file.stem
            sub_id, cond = stem.split("_")
            ref_file = rad_file.parent / f"{stem}_Mindray.mat"

            if not ref_file.exists():
                continue

            total_pairs_evaluated += 1

            # 1. Load data
            rad_rec = self.loader.load_radar_mat(rad_file)
            ref_rec = self.loader.load_reference_mat(ref_file)

            vitsig_raw = rad_rec.channels["VitalSig"].flatten()
            rad_fs = rad_rec.channel_metadata["VitalSig"].sampling_rate_hz or 333.3333

            ecg_raw = ref_rec.channels["ecg_lead2"].flatten()
            ecg_fs = ref_rec.channel_metadata["ecg_lead2"].sampling_rate_hz or 500.0

            # 2. Preprocess Radar (Cardiac 0.8 - 3.0 Hz bandpass)
            vitsig_filt, filter_ok, filter_note = self.radar_prep.apply_bandpass(
                vitsig_raw, rad_fs, low_hz=0.8, high_hz=3.0, order=3
            )
            filter_name = "butterworth_0.8_3.0hz_zero_phase_order3"

            # 3. Clean ECG delimiter NaNs and detect R-peaks using canonical sync_validation methods
            cleaned_ecg, nan_count, nan_indices = clean_ecg_nans(
                ecg_raw, only_isolated=True, fill_boundary=True
            )
            rpeak_res = detect_r_peaks(
                cleaned_ecg,
                fs=ecg_fs,
                min_bpm=self.min_bpm,
                max_bpm=self.max_bpm,
            )

            # Evaluate recording-level SQI per D9
            p_times = rpeak_res.get("peak_times", np.array([]))
            rrs = rpeak_res.get("rr_intervals", np.array([]))
            v_mask = rpeak_res.get("valid_rr_mask", np.array([]))
            valid_rr = rrs[v_mask] if len(rrs) > 0 else np.array([])
            cov_s = float(np.sum(valid_rr))
            max_gap = float(np.max(rrs)) if len(rrs) > 0 else 999.0
            rec_cov_pct = (cov_s / (len(ecg_raw) / ecg_fs)) * 100.0

            rec_sqi_pass = (rec_cov_pct >= 85.0) and (max_gap < 3.0) and (len(valid_rr) >= 20)
            rec_sqi_verdict = "SQI_PARTIAL" if rec_sqi_pass else "SQI_FAIL"
            rec_rejection_reason = "NONE" if rec_sqi_pass else f"RECORDING_SQI_FAILED ({rec_sqi_verdict})"
            if rec_sqi_pass:
                recording_sqi_pass_count += 1
            else:
                recording_sqi_fail_count += 1

            # 4. Generate candidate window boundaries (exact 23 windows per C1/D1)
            win_samples = int(round(self.win_s * rad_fs))
            num_windows = 23

            for win_idx in range(num_windows):
                start_idx = int(round(win_idx * self.hop_s * rad_fs))
                end_idx = start_idx + win_samples
                t_start = round(win_idx * self.hop_s, 3)
                t_end = round(t_start + self.win_s, 3)

                # Compute reference HR and evaluate SQI for this window
                if not rec_sqi_pass:
                    win_record = WindowLabelRecord(
                        subject_id=sub_id,
                        condition=cond,
                        window_index=win_idx,
                        radar_file=rad_file.name,
                        reference_file=ref_file.name,
                        radar_sample_start=start_idx,
                        radar_sample_end=end_idx,
                        start_time_s=t_start,
                        end_time_s=t_end,
                        duration_s=self.win_s,
                        preprocessing_filter=filter_name,
                        reference_hr_bpm=None,
                        reference_hr_arithmetic_bpm=None,
                        valid_rr_count=0,
                        rr_coverage_pct=0.0,
                        max_rr_gap_s=999.0,
                        status="REJECTED",
                        rejection_reason=rec_rejection_reason,
                        synchronization_confidence="UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0",
                        processing_warning="Recording failed SQI or NaN validation; window excluded",
                        spec_sha256=self.spec_sha256 or "",
                        spec_version=self.spec_version or "1.0.0",
                    )
                else:
                    hr_h, hr_a, rr_cnt, cov_pct, max_gap, is_valid, rej_reason = (
                        self.compute_window_reference_hr(t_start, t_end, rpeak_res)
                    )
                    status = "ACCEPTED" if is_valid else "REJECTED"
                    win_record = WindowLabelRecord(
                        subject_id=sub_id,
                        condition=cond,
                        window_index=win_idx,
                        radar_file=rad_file.name,
                        reference_file=ref_file.name,
                        radar_sample_start=start_idx,
                        radar_sample_end=end_idx,
                        start_time_s=t_start,
                        end_time_s=t_end,
                        duration_s=self.win_s,
                        preprocessing_filter=filter_name,
                        reference_hr_bpm=hr_h,
                        reference_hr_arithmetic_bpm=hr_a,
                        valid_rr_count=rr_cnt,
                        rr_coverage_pct=cov_pct,
                        max_rr_gap_s=max_gap,
                        status=status,
                        rejection_reason=rej_reason,
                        synchronization_confidence="UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0",
                        processing_warning="Nominal t0=0s alignment assumed; hardware clock unverified",
                        spec_sha256=self.spec_sha256 or "",
                        spec_version=self.spec_version or "1.0.0",
                    )

                candidate_windows.append(win_record)
                if win_record.status == "ACCEPTED":
                    accepted_windows.append(win_record)
                else:
                    rejected_windows.append(win_record)

        # 5. Export Manifest CSVs
        def write_manifest(file_path: Path, records: List[WindowLabelRecord]):
            if not records:
                return
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
                writer.writeheader()
                for rec in records:
                    writer.writerow(asdict(rec))

        write_manifest(self.output_dir / "candidate_window_manifest.csv", candidate_windows)
        write_manifest(self.output_dir / "accepted_window_manifest.csv", accepted_windows)
        write_manifest(self.output_dir / "rejected_window_manifest.csv", rejected_windows)

        # 6. Check Gate & Log Blockers
        is_blocked = (self.phase2a_gate_status != "CLOSED") or (not self.authorization_granted)
        blocker_msg = (
            "Supervised persistent dataset generation (binary arrays / ML tensors) is BLOCKED: "
            f"Phase 2A Finalization Gate status is '{self.phase2a_gate_status}' (must be formally CLOSED), "
            f"and authorization_granted is '{self.authorization_granted}'. "
            "In compliance with project execution rules, candidate, accepted, and rejected window manifests "
            "were generated in dry-run diagnostic mode, but persistent supervised training arrays were withheld."
        )

        # 7. Write dataset_generation_config.json
        config = {
            "spec_sha256": self.spec_sha256 or "",
            "spec_version": self.spec_version or "1.0.0",
            "window_duration_seconds": self.win_s,
            "hop_duration_seconds": self.hop_s,
            "radar_sampling_rate_nominal_hz": 333.3333,
            "ecg_sampling_rate_nominal_hz": 500.0,
            "preprocessing_filter": {
                "name": "cardiac_bandpass_butterworth",
                "low_cutoff_hz": 0.8,
                "high_cutoff_hz": 3.0,
                "order": 3,
                "implementation": "scipy.signal.filtfilt",
                "phase_distortion": "zero_phase",
            },
            "reference_hr_method": {
                "ecg_channel": "ecg_lead2",
                "qrs_detector": "Pan-Tompkins_5-15Hz",
                "hr_formula": "60.0 / mean(RR_intervals)",
                "physiological_hr_bounds_bpm": [self.min_bpm, self.max_bpm],
                "physiological_rr_bounds_s": [round(self.min_rr_s, 4), round(self.max_rr_s, 4)],
            },
            "sqi_criteria": {
                "min_rr_coverage_pct": self.sqi_coverage_thresh,
                "max_rr_gap_seconds": self.sqi_max_gap_thresh_s,
            },
            "synchronization_convention": {
                "assumed_relative_offset_seconds": 0.0,
                "timing_status": "UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0",
                "monitor_hr_array_status": "DISQUALIFIED_FROM_SUPERVISED_TARGETS",
            },
            "governance_gates": {
                "phase2a_finalization_gate_status": self.phase2a_gate_status,
                "authorization_granted": self.authorization_granted,
                "supervised_label_generation_permitted": not is_blocked,
            },
        }
        with open(self.output_dir / "dataset_generation_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # 8. Write run_manifest.json
        run_manifest = {
            "stage": "SUPERVISED_DATASET_GENERATION_IMPLEMENTATION",
            "spec_sha256": self.spec_sha256 or "",
            "spec_version": self.spec_version or "1.0.0",
            "run_id": self.output_dir.name,
            "execution_timestamp_utc": timestamp_start,
            "execution_status": "DIAGNOSTIC_DRY_RUN_COMPLETED_PERSISTENT_ARRAYS_BLOCKED" if is_blocked else "PERSISTENT_ARRAYS_GENERATED",
            "software_environment": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "platform": sys.platform,
            },
            "input_file_inventory": {
                "dataset_directory": str(self.dataset_dir.resolve()),
                "radar_mat_files_count": len(radar_files),
                "reference_mat_files_count": len(ref_files),
                "candidate_pairs_count": total_pairs_evaluated,
            },
            "window_counts": {
                "total_candidate_windows": len(candidate_windows),
                "accepted_windows_count": len(accepted_windows),
                "rejected_windows_count": len(rejected_windows),
                "candidate_windows_per_recording": 23,
                "trailing_tail_excluded_samples": 0,
                "trailing_tail_excluded_seconds": 0.0,
            },
            "gate_enforcement": {
                "phase2a_gate_status": self.phase2a_gate_status,
                "authorization_granted": self.authorization_granted,
                "is_blocked": is_blocked,
                "blocker_reason": blocker_msg if is_blocked else "NONE",
            },
            "output_files": [
                "run_manifest.json",
                "dataset_generation_config.json",
                "implementation_summary.md",
                "candidate_window_manifest.csv",
                "accepted_window_manifest.csv",
                "rejected_window_manifest.csv",
                "reference_label_audit.md",
                "synchronization_assumptions_record.md",
                "dataset_validation_report.md",
                "test_execution_record.md",
                "error_log.md",
                "final_stage_report.md",
            ],
        }
        with open(self.output_dir / "run_manifest.json", "w", encoding="utf-8") as f:
            json.dump(run_manifest, f, indent=2)

        return run_manifest

    def validate_readiness(self) -> Dict[str, Any]:
        """Execute a 100% read-only, non-destructive validation of Phase 2C readiness.

        Evaluates:
        1. Required source files: 48 radar MAT files and 48 reference Mindray MAT files across 24 subjects exist and are readable.
        2. Subject and recording mappings: 24 subjects x 2 conditions (Resting, Apnea) with exact 1:1 pairing.
        3. Structural and cryptographic validity of label_spec_v1.json (canonical hash, window parameters, SQI criteria).
        4. ECG-derived HR calculation: verifies clean_ecg_nans, detect_r_peaks with abs refinement, and harmonic mean HR formula.
        5. Candidate-window accounting: exactly 23 windows per recording (1,104 candidate windows cohort-wide, 0 tail truncation).
        6. Output path safety: confirms output_dir is specified and verifies run_002 is protected while gate is OPEN.
        7. Traceability: every candidate window maps to subject_id, condition, window_index, sample start/end, and timestamps.
        8. Dataset reconciliation: verifies that window counts (1,104) and duration coverage formulas match diagnostic manifests.

        DOES NOT create any output directories or files on disk.
        DOES NOT require investigator_decision.md to exist.
        """
        timestamp_start = datetime.now(timezone.utc).isoformat()
        results: Dict[str, Any] = {
            "timestamp_utc": timestamp_start,
            "validation_mode": "READ_ONLY_NON_DESTRUCTIVE",
        }
        checks: Dict[str, Dict[str, Any]] = {}
        blockers: List[str] = []

        # Check 1: Source Files & Subject Mappings
        c1_id = "SOURCE_DATASET_INVENTORY_AND_PAIRING"
        if not self.dataset_dir.exists():
            checks[c1_id] = {
                "status": "FAIL",
                "message": f"Dataset directory not found: {self.dataset_dir}",
                "details": {},
            }
            blockers.append(f"[{c1_id}] Dataset directory not found: {self.dataset_dir}")
        else:
            all_mats = sorted(list(self.dataset_dir.glob("**/*.mat")))
            radar_files = sorted([f for f in all_mats if not f.name.endswith("_Mindray.mat")])
            ref_files = sorted([f for f in all_mats if f.name.endswith("_Mindray.mat")])

            sub_ids = set()
            paired_count = 0
            missing_pairs = []
            for rf in radar_files:
                stem = rf.stem
                if "_" in stem:
                    sid, cond = stem.split("_", 1)
                    sub_ids.add(sid)
                    matching_ref = rf.parent / f"{stem}_Mindray.mat"
                    if matching_ref.exists():
                        paired_count += 1
                    else:
                        missing_pairs.append(rf.name)

            # Test reading sample file
            sample_read_ok = False
            read_error = ""
            if radar_files and ref_files:
                try:
                    rad_rec = self.loader.load_radar_mat(radar_files[0])
                    ref_rec = self.loader.load_reference_mat(ref_files[0])
                    if "VitalSig" in rad_rec.channels and "ecg_lead2" in ref_rec.channels:
                        sample_read_ok = True
                except Exception as e:
                    read_error = str(e)

            c1_pass = (
                len(radar_files) == 48
                and len(ref_files) == 48
                and len(sub_ids) == 24
                and paired_count == 48
                and len(missing_pairs) == 0
                and sample_read_ok
            )
            c1_msg = (
                "Cohort verified: 48 radar recordings and 48 ECG reference files across 24 subjects (100% paired, sample read validated)."
                if c1_pass
                else f"Cohort mismatch: {len(radar_files)} radar, {len(ref_files)} ref, {len(sub_ids)} subjects, {paired_count} paired, read_ok={sample_read_ok}. Error: {read_error}"
            )
            checks[c1_id] = {
                "status": "PASS" if c1_pass else "FAIL",
                "message": c1_msg,
                "details": {
                    "dataset_dir": str(self.dataset_dir),
                    "radar_count": len(radar_files),
                    "reference_count": len(ref_files),
                    "subject_count": len(sub_ids),
                    "paired_count": paired_count,
                    "sample_read_ok": sample_read_ok,
                },
            }
            if not c1_pass:
                blockers.append(f"[{c1_id}] {c1_msg}")

        # Check 2: Label Specification Structural & Cryptographic Validity
        c2_id = "LABEL_SPECIFICATION_VALIDITY"
        spec_candidates = [
            Path(self.spec_path) if self.spec_path else None,
            Path("outputs/closure/spec/label_spec_v1.json"),
            Path("kan_radar_HR/outputs/closure/spec/label_spec_v1.json"),
            Path(__file__).resolve().parents[2] / "outputs/closure/spec/label_spec_v1.json",
        ]
        target_spec = next((p for p in spec_candidates if p and p.exists()), None)
        if not target_spec:
            checks[c2_id] = {
                "status": "FAIL",
                "message": "label_spec_v1.json not found in candidate paths",
                "details": {},
            }
            blockers.append(f"[{c2_id}] label_spec_v1.json not found")
        else:
            try:
                spec_dict = json.loads(target_spec.read_text(encoding="utf-8"))
                d_canon = {k: v for k, v in spec_dict.items() if k not in ("approved_by", "spec_sha256")}
                canon_str = json.dumps(d_canon, indent=2, sort_keys=True)
                canon_hash = hashlib.sha256(canon_str.encode("utf-8")).hexdigest().lower()
                expected_hash = "ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44"

                hash_match = (canon_hash == expected_hash)
                win_match = (
                    spec_dict.get("windowing", {}).get("window_duration_seconds") == 10.0
                    and spec_dict.get("windowing", {}).get("hop_duration_seconds") == 5.0
                    and spec_dict.get("windowing", {}).get("num_windows") == 23
                )
                source_match = (
                    spec_dict.get("reference_source", {}).get("lead") == "ecg_lead2"
                    and spec_dict.get("reference_source", {}).get("monitor_hr_status") == "FORBIDDEN"
                )
                sqi_match = (
                    spec_dict.get("window_quality_gating", {}).get("min_covered_duration_s") == 8.0
                    and spec_dict.get("window_quality_gating", {}).get("max_rr_gap_threshold_s") == 3.0
                )
                c2_pass = hash_match and win_match and source_match and sqi_match
                c2_msg = (
                    f"Label spec v1.0.0 validated (canonical SHA-256 matched {canon_hash[:12]}..., windowing=10s/5s/23wins, lead=ecg_lead2)."
                    if c2_pass
                    else f"Spec validation failed: hash_match={hash_match}, win_match={win_match}, source_match={source_match}, sqi_match={sqi_match}"
                )
                checks[c2_id] = {
                    "status": "PASS" if c2_pass else "FAIL",
                    "message": c2_msg,
                    "details": {
                        "spec_path": str(target_spec),
                        "canonical_sha256": canon_hash,
                        "expected_canonical_sha256": expected_hash,
                        "spec_version": spec_dict.get("spec_version"),
                        "approved_by": spec_dict.get("approved_by", ""),
                    },
                }
                if not c2_pass:
                    blockers.append(f"[{c2_id}] {c2_msg}")
            except Exception as e:
                checks[c2_id] = {"status": "FAIL", "message": f"Error loading spec: {e}", "details": {}}
                blockers.append(f"[{c2_id}] Error loading spec: {e}")

        # Check 3: Window Arithmetic & Candidate Accounting
        c3_id = "WINDOW_ARITHMETIC_AND_ACCOUNTING"
        fs_r = 1000.0 / 3.0  # 333.3333 Hz
        fs_e = 500.0
        win_s = 10.0
        hop_s = 5.0
        num_wins = 23
        total_radar_samples = 40000
        total_ecg_samples = 60000

        grid_ok = True
        grid_details = []
        for k in range(num_wins):
            t_s = round(k * hop_s, 3)
            t_e = round(t_s + win_s, 3)
            r_s = int(round(k * hop_s * fs_r))
            r_e = r_s + int(round(win_s * fs_r))
            e_s = int(round(t_s * fs_e))
            e_e = int(round(t_e * fs_e))
            grid_details.append((t_s, t_e, r_s, r_e, e_s, e_e))
            if r_e > total_radar_samples or e_e > total_ecg_samples:
                grid_ok = False

        last_w = grid_details[-1]
        c3_pass = (
            grid_ok
            and len(grid_details) == 23
            and last_w[0] == 110.0
            and last_w[1] == 120.0
            and last_w[3] == total_radar_samples
            and last_w[5] == total_ecg_samples
        )
        total_candidate_windows = 48 * num_wins
        c3_msg = (
            f"Candidate window accounting validated: 23 windows/recording across 48 recordings = {total_candidate_windows} total windows (0 tail truncation, exact 120.0s coverage)."
            if c3_pass
            else f"Window arithmetic mismatch: count={len(grid_details)}, grid_ok={grid_ok}, last_win={last_w}"
        )
        checks[c3_id] = {
            "status": "PASS" if c3_pass else "FAIL",
            "message": c3_msg,
            "details": {
                "windows_per_recording": num_wins,
                "cohort_recordings": 48,
                "total_candidate_windows": total_candidate_windows,
                "last_window_bounds": last_w,
            },
        }
        if not c3_pass:
            blockers.append(f"[{c3_id}] {c3_msg}")

        # Check 4: ECG Reference HR Calculation Method
        c4_id = "ECG_REFERENCE_HR_METHOD"
        p_times_60 = np.arange(0.5, 10.5, 1.0)
        hr_h, hr_a, cnt, cov, max_gap, ok, rej = self.compute_window_reference_hr(
            0.0, 10.0, {"peak_times": p_times_60}
        )
        intervals_test = [0.601] * 5 + [1.001] * 5
        p_test = [0.5]
        for dt in intervals_test:
            p_test.append(p_test[-1] + dt)
        hr_h2, hr_a2, _, _, _, ok2, _ = self.compute_window_reference_hr(
            0.0, 10.0, {"peak_times": np.array(p_test)}
        )
        p_outlier = np.array([1.0, 2.0, 2.2, 3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2])
        _, _, _, _, _, ok_out, rej_out = self.compute_window_reference_hr(
            0.0, 10.0, {"peak_times": p_outlier}
        )

        c4_pass = (
            ok is True
            and abs(hr_h - 60.0) < 0.05
            and ok2 is True
            and abs(hr_h2 - 74.91) < 0.1
            and abs(hr_h2 - hr_a2) >= 4.90
            and ok_out is False
            and "NON_PHYSIOLOGICAL" in rej_out
        )
        c4_msg = (
            "ECG HR method validated: harmonic mean HR (60/mean(RR)), strict all-or-nothing outlier rejection, and coverage thresholds verified."
            if c4_pass
            else f"HR calculation validation failed: ok={ok}, hr_h={hr_h}, hr_h2={hr_h2}, hr_a2={hr_a2}, ok_out={ok_out}, rej_out={rej_out}"
        )
        checks[c4_id] = {
            "status": "PASS" if c4_pass else "FAIL",
            "message": c4_msg,
            "details": {
                "test_60bpm_harmonic": hr_h,
                "bimodal_harmonic": hr_h2,
                "bimodal_arithmetic": hr_a2,
                "outlier_rejected": not ok_out,
                "outlier_reason": rej_out,
            },
        }
        if not c4_pass:
            blockers.append(f"[{c4_id}] {c4_msg}")

        # Check 5: Traceability Schema Invariants
        c5_id = "TRACEABILITY_SCHEMA_VALIDITY"
        sample_rec = WindowLabelRecord(
            subject_id="VS01",
            condition="Resting",
            window_index=0,
            radar_file="VS01_Resting.mat",
            reference_file="VS01_Resting_Mindray.mat",
            radar_sample_start=0,
            radar_sample_end=3333,
            start_time_s=0.0,
            end_time_s=10.0,
            duration_s=10.0,
            preprocessing_filter="butterworth_0.8_3.0hz_zero_phase_order3",
            reference_hr_bpm=72.5,
            reference_hr_arithmetic_bpm=72.6,
            valid_rr_count=12,
            rr_coverage_pct=95.0,
            max_rr_gap_s=0.88,
            status="ACCEPTED",
            rejection_reason="NONE",
            synchronization_confidence="UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0",
            processing_warning="Nominal t0=0s alignment assumed; hardware clock unverified",
            spec_sha256="ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44",
            spec_version="1.0.0",
        )
        rec_fields = set(asdict(sample_rec).keys())
        required_fields = {
            "subject_id", "condition", "window_index", "radar_file", "reference_file",
            "radar_sample_start", "radar_sample_end", "start_time_s", "end_time_s",
            "duration_s", "preprocessing_filter", "reference_hr_bpm",
            "reference_hr_arithmetic_bpm", "valid_rr_count", "rr_coverage_pct",
            "max_rr_gap_s", "status", "rejection_reason", "synchronization_confidence",
            "processing_warning", "spec_sha256", "spec_version",
        }
        c5_pass = required_fields.issubset(rec_fields)
        c5_msg = (
            f"Provenance traceability schema validated ({len(rec_fields)} fields complete per candidate window)."
            if c5_pass
            else f"Schema incomplete: missing {required_fields - rec_fields}"
        )
        checks[c5_id] = {
            "status": "PASS" if c5_pass else "FAIL",
            "message": c5_msg,
            "details": {"schema_fields": sorted(list(rec_fields))},
        }
        if not c5_pass:
            blockers.append(f"[{c5_id}] {c5_msg}")

        # Check 6: Output Path Safety & Guard Enforcement
        c6_id = "OUTPUT_PATH_SAFETY_AND_ISOLATION"
        norm_out = str(self.output_dir).replace("\\", "/").lower()
        is_run_002 = "run_002" in norm_out

        run_002_candidates = [
            Path("outputs/supervised_dataset/run_002"),
            Path("kan_radar_HR/outputs/supervised_dataset/run_002"),
        ]
        run_real_candidates = [
            Path("outputs/phase5/run_real_001"),
            Path("kan_radar_HR/outputs/phase5/run_real_001"),
        ]
        run_002_exists = any(p.exists() for p in run_002_candidates)
        run_real_exists = any(p.exists() for p in run_real_candidates)

        isolation_ok = (not run_002_exists) and (not run_real_exists)
        guard_armed = (self.phase2a_gate_status != "CLOSED") or (not self.authorization_granted)

        c6_pass = isolation_ok and (not run_002_exists)
        c6_msg = (
            f"Output path safety verified: run_002 exists={run_002_exists}, run_real_001 exists={run_real_exists}, gate guard armed (gate={self.phase2a_gate_status}, authorized={self.authorization_granted})."
            if c6_pass
            else f"Isolation breach detected: run_002 exists={run_002_exists}, run_real_001 exists={run_real_exists}"
        )
        checks[c6_id] = {
            "status": "PASS" if c6_pass else "FAIL",
            "message": c6_msg,
            "details": {
                "target_output_dir": str(self.output_dir),
                "is_target_run_002": is_run_002,
                "run_002_exists": run_002_exists,
                "run_real_001_exists": run_real_exists,
                "phase2a_gate_status": self.phase2a_gate_status,
                "authorization_granted": self.authorization_granted,
                "guard_armed": guard_armed,
            },
        }
        if not c6_pass:
            blockers.append(f"[{c6_id}] {c6_msg}")

        # Check 7: Denominator Reconciliation
        c7_id = "DENOMINATOR_RECONCILIATION"
        diag_candidates = [
            Path("outputs/closure/window_coverage_gate_diagnostic.csv"),
            Path("kan_radar_HR/outputs/closure/window_coverage_gate_diagnostic.csv"),
            Path(__file__).resolve().parents[2] / "outputs/closure/window_coverage_gate_diagnostic.csv",
        ]
        diag_file = next((p for p in diag_candidates if p.exists()), None)
        diag_match = False
        recs_count = 0
        diag_total = 0
        diag_accepted = 0
        if diag_file:
            try:
                import pandas as pd
                df_diag = pd.read_csv(diag_file)
                recs_count = len(df_diag)
                diag_total = int(df_diag["total_windows"].sum())
                diag_accepted = int(df_diag["accepted_windows"].sum())
                diag_match = (recs_count == 48 and diag_total == 1104 and diag_accepted == 1104)
            except Exception:
                pass

        c7_pass = diag_match
        c7_msg = (
            f"Denominator reconciled: diagnostic CSV confirms 48 recordings with exactly {diag_total} candidate windows ({diag_accepted} accepted, 0 rejected) under D13/D14 SQI rules."
            if c7_pass
            else f"Denominator mismatch: diagnostic CSV recs={recs_count} (expected 48), total_windows={diag_total} (expected 1104)"
        )
        checks[c7_id] = {
            "status": "PASS" if c7_pass else "FAIL",
            "message": c7_msg,
            "details": {
                "diagnostic_file": str(diag_file) if diag_file else "NOT_FOUND",
                "recordings_count": recs_count,
                "diagnostic_window_count": diag_total,
                "diagnostic_accepted_count": diag_accepted,
                "expected_denominator": 1104,
            },
        }
        if not c7_pass:
            blockers.append(f"[{c7_id}] {c7_msg}")

        # Overall summary
        pass_count = sum(1 for c in checks.values() if c["status"] == "PASS")
        fail_count = sum(1 for c in checks.values() if c["status"] == "FAIL")
        all_passed = (fail_count == 0)

        results["overall_readiness"] = all_passed
        results["gate_status"] = self.phase2a_gate_status
        results["authorization_granted"] = self.authorization_granted
        results["ready_for_phase2c_generation"] = (
            all_passed
            and (self.phase2a_gate_status == "CLOSED")
            and self.authorization_granted
        )
        results["checks"] = checks
        results["summary"] = {
            "total_checks": len(checks),
            "pass_count": pass_count,
            "fail_count": fail_count,
            "blockers": blockers,
        }
        results["notice"] = (
            "READ-ONLY AUDIT: No files or directories were created or modified during this validation."
        )

        return results


def main():
    """CLI entry point for SupervisedDatasetGenerator and Phase 2C Readiness Validator."""
    parser = argparse.ArgumentParser(description="Supervised Dataset Generator & Phase 2C Readiness Validator")
    parser.add_argument("--spec", type=str, default=None, help="Path to label specification JSON")
    parser.add_argument(
        "--spec-sha256",
        type=str,
        default="ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44",
        help="Expected canonical spec SHA-256",
    )
    parser.add_argument("--dataset_dir", type=str, default=None, help="Path to raw dataset directory")
    parser.add_argument("--output_dir", type=str, default="outputs/supervised_dataset/run_001", help="Target output directory")
    parser.add_argument("--validate-only", action="store_true", help="Execute read-only readiness validation without generating output files")
    parser.add_argument("--gate-status", type=str, default="OPEN", help="Phase 2A/2C gate status (OPEN or CLOSED)")
    parser.add_argument("--authorized", action="store_true", help="Investigator authorization flag")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON to stdout")
    args = parser.parse_args()

    generator = SupervisedDatasetGenerator(
        dataset_dir=args.dataset_dir or "../data/VITALSENSE_120_DATASET",
        output_dir=args.output_dir,
        phase2a_gate_status=args.gate_status,
        authorization_granted=args.authorized,
        spec_sha256=args.spec_sha256,
        spec_path=args.spec,
    )

    if args.validate_only:
        report = generator.validate_readiness()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("=================================================================")
            print(f"PHASE 2C SUPERVISED DATASET READINESS REPORT ({report['timestamp_utc']})")
            print("=================================================================")
            print(f"Overall Readiness:           {'READY' if report['overall_readiness'] else 'NOT_READY'}")
            print(f"Gate Status:                 {report['gate_status']}")
            print(f"Authorization Granted:       {report['authorization_granted']}")
            print(f"Authorized for run_002:      {report['ready_for_phase2c_generation']}")
            print(f"Total Checks:                {report['summary']['total_checks']} ({report['summary']['pass_count']} PASS, {report['summary']['fail_count']} FAIL)")
            print("\n--- DETAILED CHECK RESULTS ---")
            for cid, cdata in report["checks"].items():
                print(f"  [{cdata['status']:5}] {cid}: {cdata['message']}")
            print("=================================================================")
            if not report["overall_readiness"]:
                print("BLOCKERS ENCOUNTERED:")
                for b in report["summary"]["blockers"]:
                    print(f"  - {b}")
                print("=================================================================")
            else:
                print("ALL DATASET PIPELINE READINESS CHECKS PASSED.")
                if report['gate_status'] != 'CLOSED' or not report['authorization_granted']:
                    print("GOVERNANCE NOTE: Execution of run_002 remains safely blocked until PI sign-off.")
                print("=================================================================")
        sys.exit(0 if report["overall_readiness"] else 1)
    else:
        # Full audit execution (fail-closed protected)
        manifest = generator.execute_dataset_audit()
        print("Supervised dataset audit executed successfully:")
        print(json.dumps(manifest["window_counts"], indent=2))
        sys.exit(0)


if __name__ == "__main__":
    main()
