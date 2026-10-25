# PRINCIPAL INVESTIGATOR (PI) REVIEW READINESS REPORT
## Formal Intake Package, Governance Checklist, Scientific Boundaries & Gate Closure Roadmap

**Project:** *A Subject-Independent Kolmogorov-Arnold Network (KAN)-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Repository Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Document ID:** `outputs/closure/pi_review_readiness_report.md`  
**Execution Stage:** Pre-Phase 2C Governance Gate Sign-Off Intake  
**Audit Date:** October 2026  
**Auditor Roles:** Senior Biomedical Signal-Processing Researcher, QA Engineer, Research Governance Reviewer  

---

## 1. Executive Summary & Purpose

This document establishes the formal readiness of the repository for Principal Investigator (PI) review. All software modules, synthetic benchmarks, dataset inventories, and defensive safeguards have been implemented and verified (207/207 tests passing). The technical engineering team has reached the maximum authorized pre-training boundary.

Transitioning the repository to **Phase 2C (Supervised Ground-Truth Label Generation, `run_002`)** and **Phase 5 (Real-Data KAN Model Training, `run_real_001`)** requires formal, non-delegated PI review and execution.

---

## 2. Distinction Between Recommendations and Decisions

Under project governance, technical recommendations authored by the engineering team do **not** constitute approvals:

```
+---------------------------------------------------------------------------------------------------+
| ENGINEERING TEAM RESPONSIBILITY                                                                   |
| - Verify mathematical correctness of algorithms across all 48 recordings (1,104 candidate windows)|
| - Build defensive guards, tests, and automated validators (PISignoffValidator, PreflightChecker)  |
| - Provide empirical evidence distributions (beat counts, RR gaps, coverage fractions)             |
| - Author technical recommendations (e.g., Option A for D13, D14, D15)                            |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| PRINCIPAL INVESTIGATOR (PI) EXCLUSIVE AUTHORITY                                                   |
| - Formally evaluate and select options for Decisions D13, D14, and D15                            |
| - Execute formal approval of Ground-Truth Label Specification v1.0.0                              |
| - Formally sign acknowledgement of UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0                          |
| - Authorize transition of Scientific Approval Gate from OPEN to CLOSED                            |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. PI Review Checklist & Required Sign-Off Fields

The Principal Investigator must inspect [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) and complete the following 6 sections:

| Section | Governance Item | Technical Recommendation & Empirical Basis | Required Sign-Off Fields | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Sec. 2** | **Decision D13: Window-Level Maximum RR Gap Rule (3.0 s)** | **Option A (Retain 3.0 s threshold).** Maximum observed window RR interval in the entire cohort is $1.292\text{ s}$ (`VS02_Apnea`). 0 of 1,104 windows ($0.0\%$) exceed 3.0 s. Results in 100% window retention while guarding against pauses. | [ ] Option Selection (A, B, or C)<br>[ ] PI Name<br>[ ] PI Title & Institution<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD) | **PENDING PI** |
| **Sec. 3** | **Decision D14: Minimum Valid Beats Per Recording (20 Beats)** | **Option A (Retain 20 beats threshold).** Empirical beat count range across 48 recordings is 99 to 157 beats (mean: $129.2 \pm 14.8$). 0 of 48 recordings ($0.0\%$) rejected. Prevents corrupted/empty recordings. | [ ] Option Selection (A, B, or C)<br>[ ] PI Name<br>[ ] PI Title & Institution<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD) | **PENDING PI** |
| **Sec. 4** | **Decision D15: Pipeline Runner Default `output_dir` Guard** | **Option A (Enforce explicit `--output_dir` and block `outputs/phase2a`).** Prevents accidental corruption of immutable Phase 2A baselines. Verified in `test_d15_runner_guard.py`. | [ ] Option Selection (A or B)<br>[ ] PI Name<br>[ ] PI Title & Institution<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD) | **PENDING PI** |
| **Sec. 5** | **Ground-Truth Label Specification v1.0.0 Approval** | **Approve Specification.** Formalizes 10s window, 5s hop, 23 windows/rec ($1,104$ total), Lead-II ECG, $clean\_ecg\_nans$, absolute peak refinement, harmonic mean HR ($60 / \overline{\text{RR}}$). Canonical hash: `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`. | [ ] Approval Determination<br>[ ] PI Full Name<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD)<br>*(Also set `"approved_by"` in spec JSON)* | **PENDING PI** |
| **Sec. 6** | **Mandatory Hardware Timing Limitation Acknowledgement** | **Acknowledge Limitation.** Standardized code `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. Confirms nominal zero-shift alignment is assumed and microsecond hardware sync is unverified. | [ ] PI Name<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD) | **PENDING PI** |
| **Sec. 7** | **Phase 2A Gate Closure Authorization** | **Authorize Gate Closure.** Formally transitions Scientific Gate from `OPEN` to `CLOSED` and authorizes execution of Phase 2C supervised dataset generation (`run_002`). | [ ] Gate Closure Authorization<br>[ ] PI Name<br>[ ] PI Signature<br>[ ] Date (YYYY-MM-DD) | **PENDING PI** |

---

## 4. Scientific Boundaries of Hardware Timing Limitation

Before approving the protocol, the Principal Investigator must be aware of the exact scientific boundaries imposed by `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`:

### What CAN Be Concluded Scientifically:
1. **Window-Averaged Heart Rate Estimation:** Because HR is averaged over a 10.0-second rolling window containing 10–15 complete cardiac cycles, small timing offsets ($\Delta t < 0.5\text{ s}$) have negligible impact on mean window heart rate for stationary rhythms.
2. **Relative Physiological Trends:** Comparative heart rate variations across physiological states (e.g. baseline resting vs bradycardia during breath-hold apnea vs post-apnea tachycardia) are robustly measurable and verifiable.
3. **Model Generalization on Synthetic Benchmarks:** Algorithmic comparisons between KAN, CNN, and MLP baselines under Leave-One-Subject-Out (LOSO) cross-validation are mathematically valid and fully reproducible.

### What CANNOT Be Concluded Scientifically:
1. **Physical Microsecond Hardware Timing:** Software cross-correlation peaks cannot prove the physical latency of the FMCW radar hardware or patient monitor without an electrical common clock or pulse trigger.
2. **Pulse Transit Time (PTT) / Pulse Arrival Time (PAT):** Derivation of vascular transit times between the ECG R-wave and radar chest displacement peak cannot be asserted as true physiological transit times because start-time offset $\Delta t_0$ is uncalibrated.
3. **Beat-to-Beat Microsecond HRV:** High-frequency Heart Rate Variability (HRV) metrics that depend on exact single-millisecond beat alignment cannot be validated.

---

## 5. Step-by-Step Instructions for the Principal Investigator

1. **Step 1:** Open [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) in your editor.
2. **Step 2:** In Section 2, record your selection for Decision D13 (Option A, B, or C), enter your Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
3. **Step 3:** In Section 3, record your selection for Decision D14 (Option A, B, or C), enter your Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
4. **Step 4:** In Section 4, record your selection for Decision D15 (Option A or B), enter your Name, Title, Institution, Signature, and Date (`YYYY-MM-DD`).
5. **Step 5:** In Section 5, mark `APPROVED`, enter your Name, Signature, and Date (`YYYY-MM-DD`). Also open [`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json) and enter your name in the `"approved_by"` field.
6. **Step 6:** In Section 6, sign acknowledgement of `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` with Name, Signature, and Date (`YYYY-MM-DD`).
7. **Step 7:** In Section 7, mark `[X] AUTHORIZED`, enter your Name, Signature, and Date (`YYYY-MM-DD`).
8. **Step 8:** Save both files and notify the engineering team.

---

## 6. Safe Post-Sign-Off Execution Commands (For Engineering Team)

The engineering team must strictly follow this 3-step sequence:

```powershell
# Step 1: Run preflight checker in read-only mode to verify all signatures, dates, and hashes:
python kan_radar_HR/src/closure/phase2c_preflight.py

# Step 2: ONLY IF Step 1 returns exit code 0 (GO), execute Phase 2C supervised dataset generation:
python -m src.phase3.supervised_dataset_generator `
  --dataset-dir ../data/VITALSENSE_120_DATASET `
  --output-dir outputs/supervised_dataset/run_002 `
  --spec-sha256 ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44 `
  --acknowledge-hardware-timing-limitation

# Step 3: Audit generated run_002 manifest before initiating any Phase 5 real-data training.
```
