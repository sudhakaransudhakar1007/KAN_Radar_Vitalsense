# PHASE 7: DATASET & REJECTION-COUNT RECONCILIATION REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Dataset Directory:** `data/VITALSENSE_120_DATASET`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Data Quality Auditor  

---

## 1. Executive Summary

In compliance with Phase 7 Task C, an exhaustive, independent reconciliation of the VITALSENSE physical dataset files, metadata headers, window segmentation indices, and reference HR ground truth labels was conducted directly from raw files without model training.

All 48 experimental recordings across 24 human subjects (`VS01` through `VS24`) were audited. The independent recomputation mathematically reconciled the total candidate window inventory:
$$\mathbf{1,056\text{ Candidates}} = \mathbf{1,029\text{ Accepted Windows}} + \mathbf{27\text{ Disqualified Windows}}$$

This audit confirms the condition distribution of rejected windows (25 Resting, 2 Apnea), verifies that 100% of accepted windows possess finite, defensible HR labels, and documents the true hardware sampling frequencies extracted from MAT metadata.

---

## 2. Dataset Inventory, Channels & Sampling Frequencies

### A. Physical File Structure & Pairing
- **Cohort Inventory:** 24 subjects (`VS01` through `VS24`) in dedicated subdirectories.
- **Experimental Protocols:** Two conditions per subject:
  1. `Resting`: Basal sitting condition.
  2. `Apnea`: Breath-hold and post-apnea recovery protocol.
- **Recording Pairs:** Exactly 48 matched pairs (24 Resting, 24 Apnea).
  - Radar files: `VSxx_Resting.mat`, `VSxx_Apnea.mat`
  - Reference files: `VSxx_Resting_Mindray.mat`, `VSxx_Apnea_Mindray.mat`
- **Pairing Audit:** 100% matched subject and condition IDs with zero orphan, missing, or corrupted files.

### B. Channel Shapes & Sampling Frequencies
Direct inspection of raw MAT file structures via `scipy.io.loadmat` verified:

| Modality | Channel Field | Array Shape | Verified $f_s$ | Source Variable | Duration (s) | Data Integrity |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **FMCW Radar** | `VitalSig` | $(1, 40000)$ | **$333.333333\text{ Hz}$** | `Radar['fs']` | **$120.00\text{ s}$** | 100% Finite (0 NaNs/Infs) |
| **ECG Reference** | `ecg_lead2` | $(60000, 1)$ | **$500\text{ Hz}$** | `Fs_ecg` | **$120.00\text{ s}$** | Lead dropouts interpolated |
| **Bedside Monitor HR** | `HR` | $(120, 1)$ | **$1.0\text{ Hz}$** | 1 sample/sec | **$120.00\text{ s}$** | 100% Finite (delayed) |
| **Reference Respiration**| `respiration`| $(30720, 1)$ | **$256\text{ Hz}$** | `Fs_resp` | **$120.00\text{ s}$** | 100% Finite |

> **Audit Reconciliation:** The reference ECG is sampled at **$500\text{ Hz}$**, not 1,000 Hz. The loader code (`mat_loader.py`) reads `Fs_ecg` dynamically and uses the true 500 Hz sampling rate; prior Phase 5 text that cited 1,000 Hz is formally superseded by this report.

---

## 3. Window Segmentation Arithmetic & Boundary Reconciliation

- **Window Duration ($T_{\text{win}}$):** $10.0\text{ seconds}$
  - Radar window: $10.0\text{ s} \times 333.333333\text{ Hz} = 3,333\text{ samples}$
  - ECG window: $10.0\text{ s} \times 500.0\text{ Hz} = 5,000\text{ samples}$
- **Window Stride ($\Delta t_{\text{stride}}$):** $5.0\text{ seconds}$ ($50\%$ overlap)
  - Radar stride: $5.0\text{ s} \times 333.333333\text{ Hz} = 1,667\text{ samples}$
  - ECG stride: $5.0\text{ s} \times 500.0\text{ Hz} = 2,500\text{ samples}$
- **Candidate Windows per Recording ($K$):**
  $$K = \left\lfloor \frac{40,000 - 3,333}{1,667} \right\rfloor + 1 = \left\lfloor \frac{36,667}{1,667} \right\rfloor + 1 = 21 + 1 = 22\text{ candidate windows}$$
- **Total Candidate Windows (48 recordings):** $22 \times 48 = \mathbf{1,056\text{ windows}}$.
- **Excluded Trailing Data:** $40,000 - (3,333 + 21 \times 1,667) = 1,660\text{ samples}$ ($4.98\text{ seconds}$) discarded per recording to enforce exact integer boundaries.
- **Duplicate Detection:** Zero duplicate windows detected across all candidate and accepted manifests.

---

## 4. Re-Verification of Window Acceptance & Disqualification Manifests

Independent recomputation from `accepted_window_manifest.csv` and `rejected_window_manifest.csv` confirmed:

### A. Window Distribution by Experimental Condition

| Manifest Category | `Apnea` Windows | `Resting` Windows | Total Windows | Percentage |
| :--- | :---: | :---: | :---: | :---: |
| **Candidate Windows** | 528 | 528 | **1,056** | $100.00\%$ |
| **Accepted Windows** | 526 | 503 | **1,029** | $97.44\%$ |
| **Rejected Windows** | 2 | 25 | **27** | $2.56\%$ |

### B. Breakdown of the 27 Disqualified Windows

| Documented Rejection Reason | Window Count | Percentage | Detailed Physical & Signal Cause |
| :--- | :---: | :---: | :--- |
| `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN` | **22** | $81.48\%$ | Lead-II boundary NaN values or delimiter failure at recording edges |
| `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW` | **4** | $14.81\%$ | Detected RR interval violated physiological bounds ($< 0.324\text{s}$ or $> 1.714\text{s}$) |
| `RR_COVERAGE_BELOW_85_PCT (84.96%)` | **1** | $3.70\%$ | Window RR coverage dropped marginally below $85.0\%$ threshold |
| **Total Disqualified Windows** | **27** | **$100.00\%$** | Fully cataloged in `rejected_window_manifest.csv` |

### C. Condition-Wise Reconciliation
- **Resting Rejections:** 25 windows (22 boundary NaN delimiter issues in specific resting files, 3 non-physiological RR intervals).
- **Apnea Rejections:** 2 windows (1 non-physiological RR interval, 1 coverage below 85%).
- **Accepted Inventory:** $526\text{ Apnea} + 503\text{ Resting} = \mathbf{1,029\text{ accepted windows}}$.

---

## 5. Reference HR Label Quality & Distribution

- **Derivation Method:** Instantaneous RR intervals detected via audited Pan-Tompkins QRS detector on `ecg_lead2`:
  $$\text{HR}_{\text{ref}} = \frac{60}{\overline{RR}_{\text{window}}} \quad (\text{BPM})$$
- **Finite Check:** $100\%$ finite float values (0 NaNs, 0 Infs).
- **Distribution across 1,029 Accepted Windows:**
  - Minimum Heart Rate: **$47.52\text{ BPM}$**
  - Maximum Heart Rate: **$82.89\text{ BPM}$**
  - Mean Heart Rate: **$64.44\text{ BPM}$**
  - Standard Deviation: **$7.09\text{ BPM}$**
- **Permanent Exclusion of Bedside Monitor HR:**
  The commercial Mindray monitor's displayed `HR` stream is permanently excluded from ground truth due to its verified $+6.21\text{ s}$ moving-average delay.
