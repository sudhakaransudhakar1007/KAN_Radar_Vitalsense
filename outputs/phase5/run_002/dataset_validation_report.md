# PHASE 5: COMPREHENSIVE DATASET & REFERENCE LABEL VALIDATION REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Run Audit & LOSO Experiment Readiness  
**Run Directory:** `outputs/phase5/run_002/`  
**Dataset Directory:** `data/VITALSENSE_120_DATASET`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Data Quality Auditor  

---

## 1. Executive Summary

In compliance with Phase 5 Task 3, a full, independent validation of the physical dataset files, signal fields, sampling frequencies, window segmentation parameters, and reference HR ground truth labels was performed.

The dataset contains exactly 24 human subjects (`VS01` through `VS24`) recorded under two experimental protocols (`Resting` and `Apnea`), yielding 48 paired radar-ECG recordings. Window segmentation at 10.0-second duration and 5.0-second stride generates exactly 1,056 candidate windows, of which **1,029 windows are accepted** and **27 windows are rejected** under strict biomedical Signal Quality Indices (SQI).

---

## 2. Dataset Inventory & File Verification

### A. Physical File Structure
- **Root Directory:** `data/VITALSENSE_120_DATASET/`
- **Subject Directories:** 24 subfolders (`VS01/`, `VS02/`, ..., `VS24/`).
- **Files per Subject:**
  1. `<Subject>_Resting.mat`: FMCW Radar recording during resting condition.
  2. `<Subject>_Resting_Mindray.mat`: Synchronous bio-signal reference recording during resting condition.
  3. `<Subject>_Apnea.mat`: FMCW Radar recording during breath-hold / recovery condition.
  4. `<Subject>_Apnea_Mindray.mat`: Synchronous bio-signal reference recording during breath-hold / recovery condition.
- **Total Valid Candidate Pairs:** 48 pairs (24 Resting, 24 Apnea).
- **Pairing Integrity:** 100% matched subject and condition IDs with zero orphan or unpaired files.

### B. Signal Fields & Sampling Frequencies
- **Radar Signal Field:** `VitalSig` (1D array of chest-wall displacement samples extracted from range-bin peak phase).
- **Radar Sampling Rate:** Stored in `Radar.fs` as $333.333333\text{ Hz}$ ($T_s = 3.0\text{ ms}$).
- **Radar Duration:** 40,000 samples per recording ($120.0\text{ seconds}$).
- **ECG Reference Field:** `ecg_lead2` (Lead-II electrocardiogram).
- **ECG Sampling Rate:** $1,000\text{ Hz}$ ($T_s = 1.0\text{ ms}$).
- **ECG Duration:** 120,000 samples per recording ($120.0\text{ seconds}$).
- **Finite-Value Verification:** All radar signals contain 100% finite float values (0 NaNs, 0 Infs). Isolated ECG dropouts in raw files are handled via shape-preserving linear interpolation during QRS preprocessing.

---

## 3. Window Segmentation & Arithmetic Verification

Windows are partitioned across each 120-second recording with fixed duration and overlap:

$$\text{Window Length } T_{\text{win}} = 10.0\text{ s} \quad \implies \quad N_{\text{radar}} = 3,333\text{ samples}, \quad N_{\text{ecg}} = 10,000\text{ samples}$$
$$\text{Window Stride } \Delta t_{\text{stride}} = 5.0\text{ s} \quad \implies \quad S_{\text{radar}} = 1,667\text{ samples}, \quad S_{\text{ecg}} = 5,000\text{ samples}$$

### Exact Sample Arithmetic per Recording:
- **Number of Candidate Windows ($K$):**
  $$K = \left\lfloor \frac{40,000 - 3,333}{1,667} \right\rfloor + 1 = \left\lfloor \frac{36,667}{1,667} \right\rfloor + 1 = 21 + 1 = 22\text{ windows}$$
- **Total Candidate Windows (48 recordings):** $22 \times 48 = 1,056\text{ candidate windows}$.
- **Trailing Discarded Samples:**
  $$40,000 - (3,333 + 21 \times 1,667) = 40,000 - 38,340 = 1,660\text{ samples } (4.98\text{ s})$$
  Discarded strictly to avoid incomplete fractional windows.
- **Duplicate-Window Detection:** Checked start/end sample indices across all 1,056 windows. **0 duplicate windows detected**.

---

## 4. Reference HR Derivation & SQI Screening

### A. Ground Truth Derivation
Reference heart rate is computed from instantaneous RR intervals detected via an audited Pan-Tompkins QRS detector:
$$\text{HR}_{\text{ref}} = \frac{60}{\overline{RR}_{\text{window}}} \quad (\text{BPM})$$
where $\overline{RR}_{\text{window}}$ is the harmonic mean interval of all valid cardiac cycles within $[t_{\text{start}}, t_{\text{end}}]$.

### B. Approved SQI Rejection Thresholds
1. **Valid RR Coverage:** $\ge 85.0\%$ of window duration covered by detected cardiac intervals.
2. **Maximum Permissible RR Gap:** $\le 3.0\text{ seconds}$ (rejection of transient electrode disconnections).
3. **Physiological Feasibility Limits:** $35.0\text{ BPM} \le \text{HR}_{\text{ref}} \le 185.0\text{ BPM}$ ($0.3243\text{ s} \le RR \le 1.7143\text{ s}$).

### C. Rejection Breakdown (27 Disqualified Windows)

| Rejection Category | Window Count | Percentage | Observations |
| :--- | :---: | :---: | :--- |
| **Insufficient RR Coverage ($< 85\%$)** | 19 | $1.80\%$ | Excessive perspiration / lead noise in post-apnea recovery |
| **Excessive RR Gap ($> 3.0\text{ s}$)** | 8 | $0.76\%$ | Transient baseline wander or electrode detachment |
| **Physiological Bounds Violation** | 0 | $0.00\%$ | No unphysiological heart rates in surviving windows |
| **Total Disqualified Windows** | **27** | **$2.56\%$** | Cataloged in `rejected_window_manifest.csv` |
| **Total Accepted Windows** | **1,029** | **$97.44\%$** | Cataloged in `accepted_window_manifest.csv` |

All 27 disqualified windows occurred during `Apnea` sessions under high physiological stress. All 528 candidate windows from `Resting` sessions met 100% of SQI criteria.

---

## 5. Disqualification of Displayed Bedside Monitor HR

As established in Phase 2A and reconfirmed:
- The commercial Mindray bedside monitor displayed HR array has a confirmed **$+6.21\text{ s}$ smoothing latency**.
- It is **permanently disqualified** from ground truth use.
- Instantaneous R-peak harmonic mean is the sole valid reference standard.

---

## 6. Preprocessing Consistency Audit

- **Bandpass Filter:** 4th-order zero-phase Butterworth filter, passband $0.8 - 3.0\text{ Hz}$ ($48 - 180\text{ BPM}$).
- **Inference Consistency:** The identical filter specification is applied to training, validation, and test sets.
- **Timing Assumption:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` (assumes nominal $t_0 = 0.0\text{ s}$ at file start).
