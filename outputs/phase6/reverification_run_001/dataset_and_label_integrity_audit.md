# PHASE 6: DATASET & REFERENCE LABEL INTEGRITY AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Dataset Path:** `data/VITALSENSE_120_DATASET`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Data Quality Auditor  

---

## 1. Executive Summary

In compliance with Phase 6 Task 3, an independent audit of the physical dataset files, metadata structures, window segmentation arithmetic, and reference HR ground truth labels was conducted directly from raw files without model training.

All 48 experimental recordings across 24 human subjects (`VS01` through `VS24`) were audited. The independent recomputation verified that 1,056 candidate windows yield exactly **1,029 accepted windows** and **27 rejected windows**.

Crucially, this audit uncovered a **substantive reporting discrepancy** in prior Phase 5 narrative reports regarding the distribution and cause of rejected windows, which is documented and corrected below.

---

## 2. Dataset Inventory, Channels & Sampling Frequencies

### A. Physical File Structure & Pairing
- **Subject Inventory:** 24 subdirectories (`VS01/` through `VS24/`).
- **File Pairing:** Exactly 48 radar-reference pairs (24 `Resting`, 24 `Apnea`).
  - Radar files: `VSxx_Resting.mat`, `VSxx_Apnea.mat`
  - Reference files: `VSxx_Resting_Mindray.mat`, `VSxx_Apnea_Mindray.mat`
- **Pairing Integrity:** 100% matched subject and condition identifiers. 0 orphan, duplicated, or missing files.

### B. Signal Fields, Sampling Rates & Duration Consistency
Direct inspection of raw MAT file structures via `scipy.io.loadmat` revealed:

| Channel Modality | MAT Field Key | Raw Shape | Sampling Rate ($f_s$) | Source Variable | Duration (s) | Finite Value Check |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **FMCW Radar** | `VitalSig` | $(1, 40000)$ | **$333.333333\text{ Hz}$** | `Radar['fs']` | **$120.00\text{ s}$** | $100\%$ Finite (0 NaN/Inf) |
| **ECG Reference** | `ecg_lead2` | $(60000, 1)$ | **$500\text{ Hz}$** | `Fs_ecg` | **$120.00\text{ s}$** | Dropouts interpolated |
| **Bedside Monitor HR** | `HR` | $(120, 1)$ | **$1.0\text{ Hz}$** | 1 sample/sec | **$120.00\text{ s}$** | 100% Finite (delayed) |
| **Reference Respiration**| `respiration`| $(30720, 1)$ | **$256\text{ Hz}$** | `Fs_resp` | **$120.00\text{ s}$** | 100% Finite |

> **Critical Sampling Rate Correction:** Historical Phase 5 text casually stated that ECG was sampled at $1,000\text{ Hz}$. Independent raw MAT inspection proves that `Fs_ecg = 500 Hz` ($60,000\text{ samples} / 500\text{ Hz} = 120.0\text{ s}$). The underlying code in `mat_loader.py` dynamically extracts the true $500\text{ Hz}$ value from MAT metadata, but prior markdown reports misstated the nominal value.

---

## 3. Window Segmentation Arithmetic & Boundary Calculations

- **Window Duration ($T_{\text{win}}$):** $10.0\text{ seconds}$
  - Radar samples: $3,333\text{ samples}$ ($10.0\text{ s} \times 333.333333\text{ Hz}$)
  - ECG samples: $5,000\text{ samples}$ ($10.0\text{ s} \times 500\text{ Hz}$)
- **Window Stride ($\Delta t_{\text{stride}}$):** $5.0\text{ seconds}$ ($50\%$ overlap)
  - Radar stride: $1,667\text{ samples}$
  - ECG stride: $2,500\text{ samples}$
- **Candidate Windows per Recording:**
  $$K = \left\lfloor \frac{40,000 - 3,333}{1,667} \right\rfloor + 1 = \left\lfloor \frac{36,667}{1,667} \right\rfloor + 1 = 21 + 1 = 22\text{ windows}$$
- **Total Candidate Windows (48 recordings):** $22 \times 48 = \mathbf{1,056\text{ candidate windows}}$.
- **Excluded Tail Samples:** $40,000 - (3,333 + 21 \times 1,667) = 1,660\text{ samples}$ ($4.98\text{ seconds}$) discarded per recording to enforce exact integer windowing.
- **Duplicate Detection:** Zero duplicate windows detected across all candidate and accepted manifests.

---

## 4. Re-Verification of Window Acceptance & Disqualification Manifests

Independent recomputation from `accepted_window_manifest.csv` and `rejected_window_manifest.csv` confirmed:

### A. Window Counts by Condition

| Manifest Category | `Apnea` Windows | `Resting` Windows | Total Windows | Percentage |
| :--- | :---: | :---: | :---: | :---: |
| **Candidate Windows** | 528 | 528 | **1,056** | $100.00\%$ |
| **Accepted Windows** | 526 | 503 | **1,029** | $97.44\%$ |
| **Rejected Windows** | 2 | 25 | **27** | $2.56\%$ |

### B. True Rejection Reasons Breakdown (From Actual CSV Artifact)

| Documented Rejection Reason | Window Count | Percentage of Disqualified | Underlying Physical / Signal Cause |
| :--- | :---: | :---: | :--- |
| `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN` | **22** | $81.48\%$ | Lead-II boundary NaN or delimiter failure at recording edges |
| `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW` | **4** | $14.81\%$ | Detected RR interval exceeded physiological bounds ($< 0.324\text{s}$ or $> 1.714\text{s}$) |
| `RR_COVERAGE_BELOW_85_PCT (84.96%)` | **1** | $3.70\%$ | Window RR coverage dropped marginally below $85.0\%$ threshold |
| **Total Disqualified Windows** | **27** | **$100.00\%$** | Fully cataloged in `rejected_window_manifest.csv` |

### C. Discovery of Reporting Discrepancy in Prior Phase 5 Reports
Prior Phase 5 text (`outputs/phase5/run_002/dataset_validation_report.md`, Section 4) incorrectly claimed:
> *"All 27 disqualified windows occurred during Apnea sessions... All 528 candidate windows from Resting sessions met 100% of SQI criteria."*
The independent audit confirms that the **opposite** is true:
- **25 of the 27 rejections occurred in `Resting` recordings** (specifically due to boundary NaN delimiter errors in certain resting ECG traces).
- **Only 2 rejections occurred in `Apnea` recordings**.
- The accepted manifest count of **1,029 windows** remains exactly true and mathematically verified ($526\text{ Apnea} + 503\text{ Resting} = 1,029$).

---

## 5. Reference HR Label Quality & Distribution

- **Derivation:** Instantaneous RR intervals from Pan-Tompkins QRS detection on `ecg_lead2`:
  $$\text{HR}_{\text{ref}} = \frac{60}{\overline{RR}_{\text{window}}} \quad (\text{BPM})$$
- **Finite Check:** $100\%$ finite float values (0 NaNs, 0 Infs).
- **Empirical Label Distribution (1,029 Accepted Windows):**
  - Minimum Heart Rate: **$47.52\text{ BPM}$**
  - Maximum Heart Rate: **$82.89\text{ BPM}$**
  - Mean Heart Rate: **$64.44\text{ BPM}$**
  - Standard Deviation: **$7.09\text{ BPM}$**
- **Disqualification of Bedside Monitor HR:**
  The commercial Mindray monitor's displayed `HR` stream is permanently excluded from ground truth due to its verified $+6.21\text{ s}$ moving-average delay.
