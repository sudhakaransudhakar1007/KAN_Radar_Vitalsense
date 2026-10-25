"""Append dated erratum to outputs/phase2a/step2b_consistency_audit.md per Stage 5B B7."""

from pathlib import Path


def main():
    audit_path = Path("outputs/phase2a/step2b_consistency_audit.md")
    content = audit_path.read_text(encoding="utf-8")

    erratum = """

---

## 23. Stage 5B Erratum & Status Harmonization Addendum (2026-10-19)

### 23.1 Erratum: Issue Register Status Counts & Individual Issue Classifications
In Section 22.2, the Phase 2A Finalization Gate was erroneously counted as one of the 13 OPEN issues ("and Phase 2A Finalization Gate"). The Finalization Gate is an overarching project governance boundary, not an individual issue row in the register. 

A strict programmatic audit of `outputs/phase2a/step2b_issue_register.csv` confirms exactly **28 issue rows** with the following authoritative breakdown:
- **OPEN:** **13** (ISS-07, ISS-08, ISS-09, ISS-10, ISS-12, ISS-15, ISS-17, ISS-21, ISS-22, ISS-23, ISS-24, ISS-25, ISS-26)
- **DOCUMENTED:** **11** (ISS-03, ISS-04, ISS-05, ISS-06, ISS-11, ISS-14, ISS-16, ISS-18, ISS-20, ISS-27, ISS-28)
- **CONFIRMED:** **2** (ISS-01, ISS-02)
- **RESOLVED:** **2** (ISS-13, ISS-19)
- **Total:** $13 + 11 + 2 + 2 = 28$ rows.

The following specific misclassifications in Section 22.2 are formally corrected:
1. **ISS-01 & ISS-02:** Correct status is **`CONFIRMED`** (not `DOCUMENTED`).
2. **ISS-11:** Correct status is **`DOCUMENTED`** (not `RESOLVED`).
3. **ISS-13:** Correct status is **`RESOLVED`** (not `OPEN`).
4. **ISS-14:** Correct status is **`DOCUMENTED`** (not `CONFIRMED`).
5. **ISS-15:** Correct status is **`OPEN`** (not `CONFIRMED`).
6. **ISS-17:** Correct status is **`OPEN`** (not `DOCUMENTED`).
7. **ISS-19:** Correct status is **`RESOLVED`**; ISS-20 is **`DOCUMENTED`** (corrected from composite "ISS-19/20").

### 23.2 Erratum: Causal Mechanism of Respiratory Lag Discrepancies
Section 22.3 is clarified to remove any implication that DC offset or product of means causally explains the 28 non-matching respiratory lags:
- While demeaning alters the argmax cross-correlation lag in 27 of 28 non-matching recordings, the causal physical/mathematical mechanism is **`NOT_ESTABLISHED`**.
- Statistical evaluation in Stage 2K (K3) established that the correlation between the DC product metric ($r_{\\text{dc}}$) and discrete lag shift is statistically non-significant ($\\rho = -0.1254, p = 0.3956$).
- The true underlying phenomenon is that the cross-correlation function sits on an extended, flat plateau spanning a median width of **95.0 ms** (range **34.5 ms to 1,594.0 ms** for $r \\ge r_{\\text{peak}} - 0.001$).
- Discrete lag alignment at 0.0 ms is an artifact of searching on a discrete 0.5 ms grid over this broad plateau and does **not** demonstrate physical sub-sample hardware clock synchronization. Hardware timing remains strictly **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**.

### 23.3 Comprehensive Status Table for Section 18.x Preprocessing Requirements
The following table documents the current implementation and wiring status of each preprocessing requirement specified in Section 18:

| Requirement Section | Specification Description | Current Status | Pipeline / Source File & Line | Unit Test Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Section 18.1** | Intact Signal Integrity across all 48 radar (40,000 samples @ 333.33 Hz) and 48 Mindray (60,000 samples @ 500 Hz) signals | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/phase1_audit/inspect_mat.py:42`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase1_audit/inspect_mat.py#L42); all 96 `.mat` files verified unmodified | `tests/test_mat_inspection.py` |
| **Section 18.2** | In-Memory Working Copies: all operations execute on `np.array(..., copy=True)` working arrays; raw disk files untouched | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/runner.py:112-140`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L112-L140); [`src/sync_validation/ecg_processor.py:22`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L22); [`src/sync_validation/respiratory_validator.py:25-26`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L25-L26) | `tests/test_stage2_closure.py` |
| **Section 18.3** | Dynamic Array Lengths: safe in-memory truncation to common minimum length; no hardcoded 30,720 sample counts | **`TEST_ONLY`** (standalone function) / **`WIRED`** (pipeline equivalent) | Standalone: [`src/sync_validation/respiratory_validator.py:65-94`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L65-L94); Pipeline: [`src/sync_validation/respiratory_validator.py:51-52`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L51-L52) (`resample_signals_to_2000hz`) | `tests/test_stage2_closure.py:test_truncate_respiration_dynamic_length` |
| **Section 18.4** | Single-Sample NaN Interpolation: linear interpolation restricted to isolated single NaNs; multi-sample gaps flagged and un-interpolated | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/ecg_processor.py:46-86`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L46-L86) (`clean_ecg_isolated_nans`), wired into `clean_ecg_nans` at line 98, called at [`src/sync_validation/runner.py:125`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L125) | `tests/test_stage2_closure.py:test_clean_ecg_nans_isolated_only` |
| **Section 18.5a** | 4x Zero-Padding: evaluating DTFT on denser frequency grid ($N_{\\text{fft}} = 4 \\times N_{\\text{win}}$) for spectral interpolation | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/cardiac_radar_validator.py:69-110`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L69-L110) (`estimate_window_hr_multi_estimator`), wired into `compute_window_level_hr_agreement` at line 170 | `tests/test_stage2_closure.py:test_estimate_window_hr_multi_estimator` |
| **Section 18.5b** | 3-Point Parabolic Peak Interpolation: continuous parabolic peak interpolation resolving discrete bin discretization | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/cardiac_radar_validator.py:33-66`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L33-L66) (`estimate_peak_frequency_parabolic`), wired into `compute_window_level_hr_agreement` at line 170 | `tests/test_stage2_closure.py:test_estimate_peak_frequency_parabolic` |
"""

    audit_path.write_text(content + erratum, encoding="utf-8")
    print("Successfully appended Section 23 Erratum to step2b_consistency_audit.md")


if __name__ == "__main__":
    main()
