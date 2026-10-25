# Mandatory Operational Rule: Pipeline Runner `output_dir` Specification

**Status:** MANDATORY GOVERNANCE DIRECTIVE  
**Date:** 2026-10-20  
**Target:** `src/sync_validation/runner.py`  

## 1. Problem Identification
In `src/sync_validation/runner.py:95-96` and `src/sync_validation/runner.py:244-245`, the pipeline functions `run_full_validation()` and `run_sync_validation_pipeline()` currently default `output_dir` to `Path("outputs/phase2a")` whenever `output_dir` is omitted (`None`).

Because `outputs/phase2a/` serves as the cryptographically frozen baseline of the Phase 2A audit, any unparameterized invocation of `runner.py` risks overwriting baseline artifacts (`sync_validation_results.csv`, `sync_validation_summary.json`).

## 2. Mandatory Operational Directive
Until the formal code modification proposed in [`proposed_runner_guard.diff`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/proposed_runner_guard.diff) is formally approved and applied under Decision D15:

1. **Explicit Directory Requirement:** Every script or diagnostic invocation of `run_full_validation()` or `run_sync_validation_pipeline()` **MUST** pass an explicit `output_dir` pointing to a subdirectory within `outputs/closure/` (e.g., `output_dir=Path("outputs/closure/v3")` or `output_dir=Path("outputs/closure/diagnostic_run")`).
2. **Strict Prohibition on Default Calls:** Invoking `run_sync_validation_pipeline()` or `run_full_validation()` without specifying `output_dir` is **STRICTLY PROHIBITED**.
3. **Immutability of `outputs/phase2a/`:** The gate for Phase 2A remains **OPEN**, and no script may write directly into `outputs/phase2a/`.
