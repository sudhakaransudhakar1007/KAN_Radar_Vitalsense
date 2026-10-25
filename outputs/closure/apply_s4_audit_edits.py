"""Apply S4 audit edits to outputs/phase2a/step2b_consistency_audit.md."""

from datetime import datetime, timezone
from pathlib import Path


def main():
    audit_path = Path("outputs/phase2a/step2b_consistency_audit.md")
    content = audit_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    print(f"Initial lines: {len(lines)}")

    old_lines = {}
    # Line numbers to update (1-indexed)
    # 36, 96, 367, 579, 845
    target_indices = [35, 95, 366, 578, 844]
    for idx in target_indices:
        old_lines[idx + 1] = lines[idx]

    # 1. Update line 36
    assert "clinical clean-trace quality" in lines[35], f"Line 36 mismatch: {lines[35]}"
    lines[35] = lines[35].replace("clinical clean-trace quality", "validated clean-trace quality")

    # 2. Update line 96
    assert "Clinical Ground Truth Validity" in lines[95], f"Line 96 mismatch: {lines[95]}"
    lines[95] = lines[95].replace("Clinical Ground Truth Validity", "Ground Truth Validity").replace(
        "clinical trace quality", "validated trace quality"
    )

    # 3. Update line 367
    assert "clinical adequacy gate" in lines[366], f"Line 367 mismatch: {lines[366]}"
    lines[366] = lines[366].replace("clinical adequacy gate", "prespecified adequacy gate")

    # 4. Update line 579
    assert "clinically defensible" in lines[578], f"Line 579 mismatch: {lines[578]}"
    lines[578] = lines[578].replace("clinically defensible", "validated")

    # 5. Update line 845
    assert "CLINICAL SQI & ADEQUACY GATES" in lines[844], f"Line 845 mismatch: {lines[844]}"
    lines[844] = lines[844].replace("CLINICAL SQI & ADEQUACY GATES", "SQI & ADEQUACY GATES")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    section_22 = """

---

## 22. Stage 5 Closure Package Addendum & Status Re-Audit (DATE_PLACEHOLDER)

### 22.1 Status of Preprocessing Requirements from Stale Sections 18.x
A comprehensive code-level audit of the requirements outlined in Section 18 confirms their current implementation and pipeline status:
1. **Section 18.2 — In-Memory Working Copies:**
   - **Status:** **`WIRED`** / **`IMPLEMENTED_AND_TESTED`**
   - *Evidence:* Sourced in [`src/sync_validation/runner.py:112-140`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L112-L140). All operations execute on arrays allocated via `np.array(..., copy=True)`. All 96 raw `.mat` files are cryptographically verified to have remained 100% untouched across all stages.
2. **Section 18.3 — Dynamic Array Lengths:**
   - **Status:** **`TEST_ONLY`** (standalone function) / **`WIRED`** (pipeline equivalent)
   - *Evidence:* Standalone utility `truncate_respiration_dynamic_length_in_memory` is implemented in [`src/sync_validation/respiratory_validator.py:65-94`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L65-L94) and verified by unit tests in `tests/test_stage2_closure.py`. In the active pipeline (`runner.py:135`), length equalization is achieved in-memory via `resample_signals_to_2000hz` ([`respiratory_validator.py:51-52`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L51-L52)).
3. **Section 18.4 — Single-Sample NaN Interpolation:**
   - **Status:** **`WIRED`** / **`IMPLEMENTED_AND_TESTED`**
   - *Evidence:* Guarded interpolation is implemented in `clean_ecg_isolated_nans` ([`src/sync_validation/ecg_processor.py:46-86`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L46-L86)) and wired directly into `clean_ecg_nans` at line 98, invoked at `runner.py:125`. Evaluated across all 48 Mindray files: 5,629 isolated delimiter NaNs are cleanly interpolated; zero multi-sample gaps exist; one index-0 boundary NaN (`VS10_Resting`) is cleanly filled by nearest valid neighbor.
4. **Section 18.5 — 4x Zero-Padding & Parabolic Peak Interpolation:**
   - **Status:** **`WIRED`** / **`IMPLEMENTED_AND_TESTED`**
   - *Evidence:* 3-point parabolic peak interpolation is implemented in `estimate_peak_frequency_parabolic` ([`src/sync_validation/cardiac_radar_validator.py:33-66`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L33-L66)), and exact 4x zero-padding is implemented in `estimate_window_hr_multi_estimator` (lines 69-110). Both are wired into `compute_window_level_hr_agreement` at line 170.

### 22.2 Register Re-Audit & Current Status Counts
Following the addition of issues ISS-24 through ISS-28 and terminology corrections for ISS-16 and ISS-18, the issue register (`outputs/phase2a/step2b_issue_register.csv`) contains exactly **28 issues**:
- **OPEN:** **13** (ISS-07, ISS-08, ISS-09, ISS-10, ISS-12, ISS-13, ISS-21, ISS-22, ISS-23, ISS-24, ISS-25, ISS-26, and Phase 2A Finalization Gate)
- **DOCUMENTED:** **11** (ISS-01, ISS-02, ISS-03, ISS-04, ISS-05, ISS-06, ISS-16, ISS-17, ISS-18, ISS-27, ISS-28)
- **CONFIRMED:** **2** (ISS-14, ISS-15)
- **RESOLVED:** **2** (ISS-11, ISS-19/20)

### 22.3 Respiratory Cross-Correlation Robustness & Boundary Findings (Stage 2K)
Analysis of demeaned normalized respiratory cross-correlation across all 48 recordings reveals that the correlation peak sits on an extended plateau:
- The lag range where correlation remains within 0.001 of the maximum spans a median width of **95.0 ms** (mean: **129.0 ms**, range: **34.5 ms to 1,594.0 ms**).
- For the 15 recordings where pipeline demeaned lag evaluates to exactly 0.0 ms, correlation at lag 0 is strictly greater than at +/- 0.5 ms, but the plateau width spans tens to hundreds of milliseconds due to the slow breathing cycle (0.2 - 0.33 Hz).
- The hypothesis that lag shifts between raw and demeaned signals are explained by the product of means (r_dc) was not supported (rho = -0.1254, p = 0.3956).
- **Conclusion:** Discrete alignment at 0.0 ms is a numerical artifact of searching on a 0.5 ms grid over a broad plateau and does **not** demonstrate physical sub-sample hardware clock synchronization. Hardware timing remains strictly **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**.

### 22.4 Supervised Label Provenance & `run_001` Status
1. **Manifest Existence & Label Presence:** Diagnostic manifests generated on 2026-10-15 under `outputs/supervised_dataset/run_001/` (`candidate_window_manifest.csv`, `accepted_window_manifest.csv`, `rejected_window_manifest.csv`) contain reference-HR target labels derived from ECG R-peaks at nominal zero shift.
2. **Current Governance Status:** Formally designated as **`UNAPPROVED`**, **`SUPERSEDED`**, and **`NOT FOR TRAINING`** pending formal PI decisions. Sourced with the legacy integer-hop 22-window rule and pre-Stage-2 ECG cleaning. Files are retained in-place and 100% unmodified.

### 22.5 Pending Investigator Decisions
Before Phase 2A can be closed and before supervised dataset generation or training can proceed, the Principal Investigator must formally resolve the 8 decisions documented in `outputs/closure/pi_decision_list.md`:
- **D1:** 23-window continuous-time formula (`1,104` candidate windows) vs. legacy 22-window integer hop (`1,056` windows).
- **D2:** Canonical label definition (Harmonic 60/mean(RR) vs. Arithmetic mean(60/RR)).
- **D3:** Status and disposition of `run_001` manifests.
- **D4:** Formal adoption of `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` limitation.
- **D5:** Respiratory cross-correlation reporting standards.
- **D6:** Inclusion of `VS10_Resting` under Stage 2 boundary-NaN cleaning.
- **D7:** Harmonization of ECG detector and RR coverage thresholds between Phase 3 and sync_validation.
- **D8:** Authorization to regenerate `outputs/phase2a/` official artifacts after seeding the cardiac surrogate.
""".replace("DATE_PLACEHOLDER", today_str)

    updated_content = "\n".join(lines) + section_22
    audit_path.write_text(updated_content, encoding="utf-8")
    print(f"Updated {audit_path}, new total lines: {len(updated_content.splitlines())}")

    print("\n=== OLD -> NEW LINES IN step2b_consistency_audit.md ===")
    for idx in target_indices:
        print(f"[Line {idx+1}]")
        print(f"  OLD: {old_lines[idx+1]}")
        print(f"  NEW: {lines[idx]}")


if __name__ == "__main__":
    main()
