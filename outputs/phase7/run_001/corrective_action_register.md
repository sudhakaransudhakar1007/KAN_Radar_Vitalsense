# PHASE 7: CORRECTIVE ACTION & DEFECT RESOLUTION REGISTER

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Python/ML Engineer, Independent Code Auditor & Reproducibility Specialist  

---

## 1. Executive Summary

In compliance with Phase 7 Section 13, all engineering defects, narrative reporting discrepancies, test regressions, baseline gaps, and governance blockers identified across Phases 2A through 7 are cataloged in this register.

Each entry documents the root cause, severity, concrete evidence, assigned owner role, corrective action taken or proposed, acceptance criteria, and whether the issue blocks the commencement of the real-data 24-fold LOSO training experiment.

---

## 2. Master Defect & Corrective Action Entries

### Entry 01: Inverted Condition Distribution of Disqualified Windows in Narrative Text
- **Defect Description:** Phase 5 text stated that all 27 rejections occurred during Apnea sessions and that all Resting windows passed. In reality, 25 rejections occurred in `Resting` and 2 in `Apnea`.
- **Severity:** Low (Narrative discrepancy; total accepted window count of 1,029 was unaffected).
- **Concrete Evidence:** Programmatic inspection of `rejected_window_manifest.csv`: 22 boundary NaN / delimiter errors in resting files, 4 non-physiological RR intervals, 1 coverage $< 85\%$.
- **Owner Role:** Senior Biomedical Signal Processing Engineer & Data Quality Auditor.
- **Corrective Action Taken:** Reconciled and documented in [`dataset_reconciliation_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7/run_001/dataset_reconciliation_report.md).
- **Acceptance Criteria:** Candidate ($1,056$) = Accepted ($1,029$) + Disqualified ($27$). Resting accepted ($503$), Apnea accepted ($526$). Reconciled with $100\%$ precision.
- **Blocks Next Phase:** **NO**.

---

### Entry 02: Misstated Reference ECG Sampling Rate in Prior Documentation
- **Defect Description:** Prior Phase 5 narrative text casually stated that ECG was sampled at $1,000\text{ Hz}$ ($10,000\text{ samples}$ per window).
- **Severity:** Moderate (Documentation error).
- **Concrete Evidence:** Raw MAT inspection of `VS01_Resting_Mindray.mat`: metadata variable `Fs_ecg` is $500\text{ Hz}$, array shape $(60000, 1)$ across $120.0\text{ s}$ ($5,000\text{ samples}$ per 10s window).
- **Owner Role:** Biomedical Signal Processing Researcher.
- **Corrective Action Taken:** Corrected in Phase 6 and Phase 7 documentation. Verified that loader code (`mat_loader.py`) dynamically reads true $500\text{ Hz}$ from metadata.
- **Acceptance Criteria:** Documentation accurately matches physical MAT metadata.
- **Blocks Next Phase:** **NO**.

---

### Entry 03: Synthetic Pipeline Test Regression in `test_phase4d_completion.py`
- **Defect Description:** Test `test_synthetic_end_to_end_integration_pipeline` failed on `assert within_5bpm_pct >= 90.0` (observed: $87.5\%$ at 10 epochs).
- **Severity:** Moderate (Caused test suite exit code 1 in Phase 6).
- **Concrete Evidence:** Test log traceback from Phase 6; empirical ablation in Phase 7 Task B showing 30 gradient steps was slightly under-converged for seed 42 ($14/16 = 87.5\%$), whereas 45 steps (15 epochs) achieves $100.0\%$ within 5 BPM and MAE $0.51\text{ BPM}$.
- **Owner Role:** Senior Python/ML Test Engineer.
- **Corrective Action Taken:** In strict adherence to Rule 7, the threshold was NOT weakened. The training epoch budget in `test_phase4d_completion.py` line 155 was adjusted from `epochs=10` to `epochs=15` (the smallest necessary change to permit convergence).
- **Acceptance Criteria:** Full automated test suite passes **100 / 100 tests cleanly** in 54.76 seconds.
- **Blocks Next Phase:** **RESOLVED (NO)**.

---

### Entry 04: Classical Autocorrelation Baseline Implementation Gap
- **Defect Description:** Classical autocorrelation baseline listed as a required comparison method, but zero implementation existed in `src/`.
- **Severity:** Moderate (Comparative scope gap).
- **Concrete Evidence:** File search confirmed no autocorrelation script in `src/`. Mathematical analysis proved unassisted autocorrelation fails due to breathing harmonic collisions.
- **Owner Role:** Signal Processing Engineer & Scientific Reproducibility Auditor.
- **Corrective Action Taken:** Formalized complete 10-point algorithmic proposal in [`autocorrelation_specification_proposal.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7/run_001/autocorrelation_specification_proposal.md) with explicit investigator decision checkpoints.
- **Acceptance Criteria:** Formal investigator sign-off on harmonic suppression and fallback protocol prior to coding.
- **Blocks Next Phase:** **NO** (Neural baseline training can proceed independently upon gate closure).

---

### Entry 05: Phase 2A Finalization Gate Remains Officially `OPEN`
- **Defect Description:** Supervised persistent tensor export and real-data model training are legally and scientifically blocked because the Phase 2A Finalization Gate is `OPEN`.
- **Severity:** **CRITICAL (GOVERNANCE BLOCKER)**.
- **Concrete Evidence:** `outputs/phase2a/step2b_consistency_audit.md` lines 9–16; `outputs/supervised_dataset/run_001/run_manifest.json` line 29.
- **Owner Role:** Principal Investigator / Human Researcher.
- **Required Action:** The human investigator must review [`governance_gate_status.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7/run_001/governance_gate_status.md) and issue an explicit formal decision closing the gate under `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` and authorizing real-data training.
- **Acceptance Criteria:** Documented investigator approval recorded in repository.
- **Blocks Next Phase:** **`YES — MANDATORY EXPERIMENT BLOCKER`**.
