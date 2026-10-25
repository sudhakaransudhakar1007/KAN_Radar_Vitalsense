# PHASE 4B: DATASET WINDOW ARITHMETIC & SAMPLE-LEVEL AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Audit Stage:** Phase 4B — Window Arithmetic and Sampling Rate Verification  
**Audit File:** `outputs/phase4/audit_run_001/window_arithmetic_audit.md`  

---

## 1. Nominal vs. Exact Sampling Rates & Durations

A rigorous mathematical distinction must be maintained between nominal dataset metadata and exact float values derived from the underlying FMCW hardware digitizer:

| Parameter | Nominal Value | Exact Decimal Float | Formula / Hardware Derivation |
| :--- | :--- | :--- | :--- |
| **Radar Sampling Rate ($f_s$)** | $333.33\text{ Hz}$ | **$333.3333333333333\text{ Hz}$** | $1000 / 3\text{ Hz}$ (Chirp repetition interval: $3.0\text{ ms}$) |
| **Total Radar Samples ($N$)** | $40,000$ | $40,000$ | Binary dimension of `VitalSig` array in MAT files |
| **Nominal Signal Duration** | $120.0012\text{ s}$ | **$120.000000\text{ s}$** | $40,000 / (1000/3) = 120.0\text{ s}$ exact |
| **ECG Sampling Rate ($f_{s, \text{ecg}}$)**| $500.0\text{ Hz}$ | $500.0\text{ Hz}$ | Mindray digitizer clock ($2.0\text{ ms}$ interval) |
| **Total ECG Samples ($M$)** | $60,000$ | $60,000$ | Binary dimension of `ecg_lead2` array |
| **Exact ECG Duration** | $120.0\text{ s}$ | **$120.000000\text{ s}$** | $60,000 / 500.0 = 120.0\text{ s}$ exact |

**Auditor Note:** When computed using the exact rational frequency $f_s = 1000/3\text{ Hz}$, the radar and ECG signals have **identical duration of 120.000000 seconds**. The apparent $1.2\text{ ms}$ discrepancy only arose in legacy code that rounded $f_s$ to $333.33\text{ Hz}$.

---

## 2. Window Length, Stride & Trailing Tail Derivation

### A. Window Length ($T_w = 10.0\text{ seconds}$):
- Theoretical sample count:
  $$N_w = 10.0 \times \frac{1000}{3} = \frac{10,000}{3} = 3,333.333\dots \text{ samples}$$
- Discrete integer rounding applied:
  $$N_w = \mathbf{3,333\text{ samples}}$$
- Actual physical duration of 3,333 samples:
  $$T_{w, \text{actual}} = \frac{3,333}{333.333333} = \mathbf{9.9990\text{ seconds}}$$
  *(Discrepancy from nominal 10.0 s: $-0.0010\text{ s}$ or $-1.0\text{ ms}$, representing less than one-third of a radar frame period).*

### B. Stride ($T_s = 5.0\text{ seconds}$):
- Theoretical sample count:
  $$N_s = 5.0 \times \frac{1000}{3} = \frac{5,000}{3} = 1,666.666\dots \text{ samples}$$
- Discrete integer rounding applied:
  $$N_s = \mathbf{1,667\text{ samples}}$$
- Actual physical duration of 1,667 samples:
  $$T_{s, \text{actual}} = \frac{1,667}{333.333333} = \mathbf{5.0010\text{ seconds}}$$
  *(Discrepancy from nominal 5.0 s: $+0.0010\text{ s}$ or $+1.0\text{ ms}$).*

### C. Total Window Count & Trailing Tail:
For $K$ windows with stride $N_s$ and window length $N_w$:
$$\text{End Sample}(k) = k \cdot N_s + N_w$$
For $k = 21$ (the 22nd window, index 0 to 21):
$$\text{Start Sample}(21) = 21 \times 1,667 = 35,007$$
$$\text{End Sample}(21) = 35,007 + 3,333 = \mathbf{38,340}$$
For $k = 22$ (hypothetical 23rd window):
$$\text{End Sample}(22) = 22 \times 1,667 + 3,333 = 36,674 + 3,333 = \mathbf{40,007} > 40,000$$
Because sample $40,007$ exceeds the recording boundary ($40,000$), a 23rd full 10-second window cannot be formed.
- **Trailing Tail Excluded Samples:**
  $$N_{\text{tail}} = 40,000 - 38,340 = \mathbf{1,660\text{ samples}}$$
- **Trailing Tail Excluded Duration:**
  $$T_{\text{tail}} = \frac{1,660}{333.333333} = \mathbf{4.9800\text{ seconds}}$$

---

## 3. Comprehensive Window Index Manifest Table

The 22 candidate windows per recording follow the audited boundaries below:

| Window Index | Start Sample | End Sample | Window Samples | Nominal $t_{\text{start}}$ (s) | Nominal $t_{\text{end}}$ (s) | Actual $t_{\text{end}} - t_{\text{start}}$ (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 0 | 3,333 | 3,333 | 0.0 | 10.0 | 9.9990 |
| **1** | 1,667 | 5,000 | 3,333 | 5.0 | 15.0 | 9.9990 |
| **2** | 3,334 | 6,667 | 3,333 | 10.0 | 20.0 | 9.9990 |
| **3** | 5,001 | 8,334 | 3,333 | 15.0 | 25.0 | 9.9990 |
| **4** | 6,668 | 10,001 | 3,333 | 20.0 | 30.0 | 9.9990 |
| **5** | 8,335 | 11,668 | 3,333 | 25.0 | 35.0 | 9.9990 |
| **6** | 10,002 | 13,335 | 3,333 | 30.0 | 40.0 | 9.9990 |
| **7** | 11,669 | 15,002 | 3,333 | 35.0 | 45.0 | 9.9990 |
| **8** | 13,336 | 16,669 | 3,333 | 40.0 | 50.0 | 9.9990 |
| **9** | 15,003 | 18,336 | 3,333 | 45.0 | 55.0 | 9.9990 |
| **10** | 16,670 | 20,003 | 3,333 | 50.0 | 60.0 | 9.9990 |
| **11** | 18,337 | 21,670 | 3,333 | 55.0 | 65.0 | 9.9990 |
| **12** | 20,004 | 23,337 | 3,333 | 60.0 | 70.0 | 9.9990 |
| **13** | 21,671 | 25,004 | 3,333 | 65.0 | 75.0 | 9.9990 |
| **14** | 23,338 | 26,671 | 3,333 | 70.0 | 80.0 | 9.9990 |
| **15** | 25,005 | 28,338 | 3,333 | 75.0 | 85.0 | 9.9990 |
| **16** | 26,672 | 30,005 | 3,333 | 80.0 | 90.0 | 9.9990 |
| **17** | 28,339 | 31,672 | 3,333 | 85.0 | 95.0 | 9.9990 |
| **18** | 30,006 | 33,339 | 3,333 | 90.0 | 100.0 | 9.9990 |
| **19** | 31,673 | 35,006 | 3,333 | 95.0 | 105.0 | 9.9990 |
| **20** | 33,340 | 36,673 | 3,333 | 100.0 | 110.0 | 9.9990 |
| **21** | 35,007 | 38,340 | 3,333 | 105.0 | 115.0 | 9.9990 |

---

## 4. Manifest Integrity Audit

An automated check was conducted on `outputs/supervised_dataset/run_001/accepted_window_manifest.csv`:
- **Total Rows in File:** Exactly **1,029** (excluding CSV header).
- **Unique Primary Keys (`subject_id` + `condition` + `window_index`):** Exactly **1,029**.
- **Candidate Pool:** $48\text{ recordings} \times 22\text{ windows} = \mathbf{1,056\text{ candidate windows}}$.
- **Documented Rejections:** Exactly **27 windows** rejected due to SQI screening:
  - `VS10_Resting`: All 22 windows rejected (Phase 3 audit identified invalid corrupted ECG trace).
  - `VS16_Resting`: Windows 0 and 1 rejected (boundary NaN values in ECG).
  - `VS16_Apnea`: Windows 0 and 1 rejected (boundary NaN values in ECG).
  - `VS03_Resting`: Window 0 rejected (coverage $< 85\%$).
  - Total rejections: $22 + 2 + 2 + 1 = \mathbf{27\text{ rejected windows}}$.
- **Net Accepted Windows:** $1,056 - 27 = \mathbf{1,029\text{ accepted windows}}$.

**Auditor Confirmation:** The counts agree 100% with the source raw MAT files and manifest logs. No windows were silently added or discarded.
