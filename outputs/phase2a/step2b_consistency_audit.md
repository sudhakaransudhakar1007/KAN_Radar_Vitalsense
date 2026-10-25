# PHASE 2A — STEP 2B: SCIENTIFIC CONSISTENCY, SYNCHRONIZATION, TEST-INTEGRITY & INDEPENDENT-RECOMPUTATION AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 2A — Step 2B: Rigorous Audit of Synchronization Validation Pipeline & Artifacts  
**Audit Report File:** `outputs/phase2a/step2b_consistency_audit.md`  
**Dataset Path:** `data/VITALSENSE_120_DATASET` (VS01 through VS24)  
**Execution Date:** October 2026  
**Auditor Role:** Senior Biomedical Signal-Processing Researcher, Physiological-Signal Validation Specialist, & Python Test Engineer  
**Audit Status:** **PHASE 2A — STEP 2B STATUS: RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION.**  
**Core Decision Boundaries:**
- **Preprocessing:** `CONDITIONAL GO (in-memory working copies only)`
- **Supervised-label generation:** `NOT YET APPROVED`
- **Hardware clock synchronization:** `UNVERIFIED`
- **Respiratory alignment:** `CONSISTENT_NOT_PROVEN (Resting) / INCONCLUSIVE (Apnea)`
- **10-second window adequacy:** `NOT YET SUPPORTED`
**Scientific Headline Status:** Proposed headline *"WINDOW-LEVEL ALIGNMENT ADEQUATE FOR 10 s WINDOWS; HARDWARE CLOCK UNVERIFIED"* is **`NOT YET SUPPORTED`**; replaced with evidence-matched headline: *"EMPIRICAL RESTING CARDIAC-BAND AGREEMENT OBSERVED FOR 10 s WINDOWS AT ZERO SHIFT (MAE = 2.97 BPM); SUPERVISED LABEL GENERATION NOT YET APPROVED; HARDWARE CLOCK UNVERIFIED"*.

---

## 1. Executive Summary

This audit constitutes a formal, reproducible, independent scientific review of the Phase 2A Step 2 synchronization-validation pipeline, its mathematical code, test suite history, and resulting artifact tables. The primary objective is to evaluate whether the empirical claims reported in [`step2_sync_validation_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2_sync_validation_report.md) and [`sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/sync_validation_results.csv) are mathematically sound, reproducible from raw data, and free from selection bias or reporting errors.

### Key Audit Findings:
1. **Mathematical Reproducibility of Core Metrics (`VERIFIED_FROM_SOURCE`, `INDEPENDENTLY_RECOMPUTED`):**  
   Independent scratch recomputation of 11 metrics across 4 diverse candidate pairs (`VS01_Resting`, `VS24_Resting`, `VS09_Resting`, `VS02_Apnea`) matched the values in `sync_validation_results.csv` with 0.0000 discrepancy. The mathematical implementation of R-peak detection, 1 Hz ECG HR derivation, cross-correlation, and windowed FFT operates predictably.
2. **Confirmation of Monitor HR Latency (+6 to +7 s) (`VERIFIED_FROM_CSV`, `INDEPENDENTLY_RECOMPUTED`):**  
   The empirical lag scan across all 48 recordings firmly demonstrates that the commercial Mindray monitor's 120-point `HR` array lags physiological instantaneous ECG heart rate by $+6.21\text{ s}$ on average (median: $+7.0\text{ s}$, mode: $+7.0\text{ s}$, with 40/48 recordings falling in $[+4\text{ s}, +10\text{ s}]$). Supervised training of KAN models directly against the raw monitor `HR` array would severely corrupt window-level target labels.
3. **Identification of Reporting Errors & Contradictions (`CONTRADICTED`):**  
   - **Surrogate Correlation Contradiction:** The report asserted that phase-randomized surrogates "never exceeded 0.42" and "reduced correlation to 0.34". In truth, the CSV shows surrogate correlations reach up to **0.8123** (mean: **0.5077**, Resting mean: **0.6289**).
   - **Statistical Impossibility:** The report claimed surrogate significance at "$p < 0.001$" despite using only $N = 5$ surrogate draws (where minimum achievable empirical p-value is $1/(N+1) \approx 0.167$).
   - **Inverted Polarity Identification Error:** The report misidentified the negative-polarity Resting pairs as `VS02` and `VS19`. The actual negative-polarity pairs in the CSV are **`VS09` and `VS20`**.
   - **Correlation Threshold Overstatement:** The report claimed 14 of 24 Resting pairs had correlation $> 0.85$; the true count in the CSV is **6** (16 exceeded 0.70).
4. **Implementation Limitations & Selection Biases (`VERIFIED_FROM_SOURCE`):**  
   - **Heuristic Latency Thresholding:** In `runner.py`, candidate lags $< 4\text{ s}$ are assigned `NEAR_ZERO_LATENCY` even when the optimal lag is $-3\text{ s}$ (e.g., `VS05_Apnea`), with an contradictory reason string citing "curve flatness" even when the flatness flag was `False`.
   - **Superficial ECG Quality Metric:** `ecg_quality_status = PASS` is assigned whenever $\ge 5$ valid RR intervals exist in 120 seconds, which does not guarantee validated clean-trace quality.
   - **FFT Bin Discretization:** The 10-second cardiac FFT has a fixed bin width of $6.0\text{ bpm}$ with no parabolic or Gaussian peak interpolation.
   - **In-Sample Selection Optimism:** Diagnostic split tests demonstrated that selecting trial shifts $\tau \in [-5, +5]\text{ s}$ on all 23 windows overfits in-sample; held-out test windows show higher errors than zero-shift baselines.

---

## 2. Resolved Project Root & Audit Environment

- **Target Project Directory:** `kan_radar_HR`
- **Parent Workspace Path:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work`
- **Resolved Project Root:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR` (`VERIFIED_FROM_SOURCE`)
- **Python Runtime:** Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr 5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)]
- **Core Dependencies:** `numpy 2.2.6`, `scipy 1.15.3`, `pandas 2.3.1`, `pytest 9.1.1`
- **Git Availability:** `git` executable not present in system PATH; Git version history marked `NOT_VERIFIABLE`. File modification timestamps and historical execution logs were utilized for chronological verification.

---

## 3. Artifact Inspection Inventory

| Artifact Path | Inspection Status | Evidence State | Observations |
| :--- | :---: | :---: | :--- |
| `outputs/phase2a/sync_validation_results.csv` | **INSPECTED** | `VERIFIED_FROM_CSV` | 48 rows, 35 columns, 0 NaNs, 24 subjects, 2 conditions. |
| `outputs/phase2a/step2_sync_validation_report.md` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | 11 sections; reconciled against CSV; discrepancies identified. |
| `outputs/phase2a/step2_test_summary.md` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | 48 unit tests documented; synthetic controls segregated. |
| `tests/test_sync_validation.py` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | 16 test functions across 3 test classes. |
| `src/sync_validation/ecg_processor.py` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Contains `clean_ecg_nans`, `detect_r_peaks`, `derive_1hz_ecg_hr`, `scan_monitor_hr_lag`. |
| `src/sync_validation/respiratory_validator.py` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Contains `resample_signals_to_2000hz`, `compute_respiratory_xcorr`, `compute_surrogate_respiratory_control`. |
| `src/sync_validation/cardiac_radar_validator.py` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Contains `extract_radar_cardiac_signal`, `compute_window_level_hr_agreement`, `synthetic_known_offset_test`. |
| `src/sync_validation/runner.py` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Orchestrates batch processing, status assignment, CSV export. |
| `task-444.log` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Historical failure log: records 3 initial test failures. |
| `task-476.log` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Historical pass log: records 48/48 passed tests in 65.80s. |
| `.pytest_cache/v/cache/lastfailed` | **INSPECTED** | `VERIFIED_FROM_SOURCE` | Content `{}` (clean state following task-476). |
| Git History / Repos | **NOT_VERIFIABLE** | `NOT_VERIFIABLE` | `git` command not recognized in shell PATH. |

---

## 4. Audit Methods & Recomputation Protocol

1. **Static Code Analysis:** Manual, line-by-line inspection of mathematical formulas, edge-case branches, array slicing conventions, and status logic in all `src/sync_validation/` files.
2. **Direct CSV Structure Audit:** Programmatic validation of table geometry, null values, categorical domain integrity, duplicate primary keys (`subject_id`, `condition`), and data types.
3. **Independent Mathematical Recomputation:** Writing clean, minimal, non-production code in a separate scratch location (`scratch/independent_recompute.py`) to process raw `.mat` files for 4 representative recordings without calling production runner functions.
4. **Diagnostic Out-of-Sample Split Testing:** Slicing the 23 analysis windows of 120s recordings into a first-half training split (12 windows) and second-half held-out test split (11 windows) to measure empirical selection optimism in trial-shift lag optimization.
5. **Phase-Randomized Surrogate Null Assessment:** Evaluating Fourier phase randomization across synthetic and real recordings to audit the statistical validity of reported p-values and surrogate baseline correlations.
6. **Sandboxed Test Execution:** Executing `python -m pytest -p no:cacheprovider tests/test_sync_validation.py -q` under `PYTHONDONTWRITEBYTECODE=1` without modifying source files, raw data, or pre-existing cache directories.

---

## 5. Verified Facts vs. Unverified Claims

### 5.1 Verified Facts
1. **Radar Sampling & Units:** `VitalSig` is confirmed as chest displacement in millimeters (`mm`), 40,000 samples @ $333.3333\text{ Hz}$ ($120.0\text{ s}$). (`VERIFIED_FROM_SOURCE`)
2. **ECG Lead II Properties:** `ecg_lead2` is confirmed as $500\text{ Hz}$, 60,000 samples ($120.0\text{ s}$). Exactly 47 of 48 files contain 119 to 120 periodic single-sample NaNs occurring once every ~501 samples (~1.0s). `VS24_Resting_Mindray.mat` contains 0 NaNs. (`VERIFIED_FROM_SOURCE`, `INDEPENDENTLY_RECOMPUTED`)
3. **Respiration Sampling Rates:** In all 48 Mindray files, `Fs_resp` is stored as $256\text{ Hz}$ in the MAT header (matching 30,720 samples / 120s), confirming that the $62.5\text{ Hz}$ entry in `Subject Information.xlsx` was a documentation discrepancy. (`VERIFIED_FROM_SOURCE`)
4. **Gross Physical Alignment:** Author respiratory cross-correlation on Resting recordings produces an empirical mean lag of $+0.81\text{ ms}$ with standard deviation $8.73\text{ ms}$, bounded within $[-24.5\text{ ms}, +30.0\text{ ms}]$. (`VERIFIED_FROM_CSV`, `INDEPENDENTLY_RECOMPUTED`)
5. **Monitor HR Latency:** 40 of 48 candidate pairs show an optimal latency between $+4\text{ s}$ and $+10\text{ s}$ relative to ECG-derived heart rate (median: $+7.0\text{ s}$). (`VERIFIED_FROM_CSV`, `INDEPENDENTLY_RECOMPUTED`)

### 5.2 Unverified Claims & Contradictions
1. **Microsecond Hardware Synchronization:** Unverified. No hardware clock pulse, PPS trigger, or common digitizer timestamp exists in the MAT files. (`VERIFIED_FROM_SOURCE`)
2. **Surrogate Correlation $< 0.42$ & $p < 0.001$:** **CONTRADICTED**. In the actual CSV, surrogate correlation reaches $0.8123$ (mean: $0.5077$). A p-value of $p < 0.001$ is mathematically impossible from 5 surrogate draws. (`CONTRADICTED`)
3. **Negative Polarity Subjects (`VS02`, `VS19`):** **CONTRADICTED**. The CSV confirms negative polarities in `VS09_Resting` and `VS20_Resting`; `VS02` and `VS19` have positive polarity ($+1$). (`CONTRADICTED`)
4. **Ground Truth Validity from `PASS`:** Unverified. The detector requires only 5 valid beats in 120s to output `PASS`, which does not guarantee validated trace quality. (`VERIFIED_FROM_SOURCE`)

---

## 6. CSV Integrity & Report Reconciliation

### 6.1 CSV Table Geometry & Structural Checks
- **File Checked:** `outputs/phase2a/sync_validation_results.csv` (`VERIFIED_FROM_CSV`)
- **Row Count:** Exactly 48 data rows + 1 header row.
- **Column Count:** Exactly 35 columns. No trailing empty columns or malformed delimiters.
- **Key Uniqueness:** All 48 `(subject_id, condition)` pairs are unique (24 subjects $\times$ 2 conditions: Resting and Apnea). Exactly 0 duplicate rows.
- **Completeness:** 0 missing, null, or infinite values across all 1,680 data cells.

### 6.2 Full Discrepancy & Reconciliation Table

**Uniform Reporting Tolerances:** A uniform numerical reporting tolerance of $\pm 0.0100\text{ bpm}$ for heart-rate MAE metrics and $\pm 0.0100$ for correlation coefficients is applied consistently across this audit. Differences exceeding this threshold are formally marked **`DISCREPANCY`** rather than dismissed as rounding:

| Metric / Statement | Value in Report (`step2_sync_validation_report.md`) | Recomputed Value (`sync_validation_results.csv`) | Discrepancy | Explanation / Root Cause | Evidence State |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Resting Resp Lag Mean** | $+0.81\text{ ms}$ | $+0.8125\text{ ms}$ | $0.0025\text{ ms}$ | Within $\pm 0.0100\text{ ms}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Resting Resp Lag Std** | $8.73\text{ ms}$ | $8.7325\text{ ms}$ (ddof=1) | $0.0025\text{ ms}$ | Within $\pm 0.0100\text{ ms}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Resting Resp Lag Min** | $-24.50\text{ ms}$ | $-24.5000\text{ ms}$ | $0.0000\text{ ms}$ | Exact match (`VS02_Resting`). | `VERIFIED_FROM_CSV` |
| **Resting Resp Lag Max** | $+30.00\text{ ms}$ | $+30.0000\text{ ms}$ | $0.0000\text{ ms}$ | Exact match (`VS18_Resting`). | `VERIFIED_FROM_CSV` |
| **Resting Resp Corr Mean** | $0.7005$ | $0.7005$ | $0.0000$ | Exact match. | `VERIFIED_FROM_CSV` |
| **Resting Corr $> 0.85$ Count** | **14 of 24** | **6 of 24** | **-8 subjects** | **Report typographical error.** Exactly 6 exceed 0.85 (`VS03,07,10,12,17,24`); 16 exceed 0.70. | `DISCREPANCY (CONTRADICTED)` |
| **Resting Negative Polarity Pairs** | **`VS02`, `VS19`** | **`VS09`, `VS20`** | **Wrong subjects** | **Report transcription error.** Count (2) was correct, but wrong IDs cited. | `DISCREPANCY (CONTRADICTED)` |
| **Apnea Resp Lag Mean** | $+1.17\text{ ms}$ | $+1.1667\text{ ms}$ | $0.0033\text{ ms}$ | Within $\pm 0.0100\text{ ms}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Apnea Resp Lag Std** | $8.53\text{ ms}$ | $8.5283\text{ ms}$ | $0.0017\text{ ms}$ | Within $\pm 0.0100\text{ ms}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Apnea Resp Corr Mean** | $0.4130$ | $0.4130$ | $0.0000$ | Exact match. | `VERIFIED_FROM_CSV` |
| **Apnea Neg Polarity Count** | 4 | 4 | 0 | Exact match (`VS09`, `VS10`, `VS20`, `VS21`). | `VERIFIED_FROM_CSV` |
| **Monitor Lag Mean** | $+6.21\text{ s}$ | $+6.2083\text{ s}$ | $0.0017\text{ s}$ | Within $\pm 0.0100\text{ s}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Monitor Lag Median / Mode** | $+7.0\text{ s}$ / $+7\text{ s}$ (13 pairs) | $+7.0\text{ s}$ / $+7\text{ s}$ (13 pairs) | $0.0$ | Exact match. | `VERIFIED_FROM_CSV` |
| **Monitor Lag in $[+4, +10]\text{ s}$**| 40 of 48 ($83.3\%$) | 40 of 48 ($83.33\%$) | $0.0$ | Exact match. | `VERIFIED_FROM_CSV` |
| **Zero-Shift Monitor MAE** | $2.51\text{ bpm}$ | $2.5586\text{ bpm}$ | $+0.0486\text{ bpm}$ | Exceeds $\pm 0.0100\text{ bpm}$ tolerance (reporting average error). | `DISCREPANCY` |
| **Best-Shift Monitor MAE** | $1.82\text{ bpm}$ | $1.9029\text{ bpm}$ | $+0.0829\text{ bpm}$ | Exceeds $\pm 0.0100\text{ bpm}$ tolerance (reporting average error). | `DISCREPANCY` |
| **Zero-Shift Monitor Corr** | $0.26$ | $0.2579$ | $-0.0021$ | Within $\pm 0.0100$ tolerance. | `VERIFIED_FROM_CSV` |
| **Best-Shift Monitor Corr** | $0.69$ | $0.6504$ | $-0.0396$ | Exceeds $\pm 0.0100$ tolerance (overstated correlation). | `DISCREPANCY (CONTRADICTED)` |
| **Radar-ECG Window MAE (All)** | $3.38\text{ bpm}$ | $3.3807\text{ bpm}$ | $+0.0007\text{ bpm}$ | Within $\pm 0.0100\text{ bpm}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Radar-ECG Window MAE (Rest)**| $2.94\text{ bpm}$ | $2.9652\text{ bpm}$ | $+0.0252\text{ bpm}$ | Exceeds $\pm 0.0100\text{ bpm}$ tolerance (reporting average error). | `DISCREPANCY` |
| **Radar-ECG Window MAE (Apnea)**| $3.82\text{ bpm}$ | $3.7961\text{ bpm}$ | $-0.0239\text{ bpm}$ | Exceeds $\pm 0.0100\text{ bpm}$ tolerance (reporting average error). | `DISCREPANCY` |
| **Surrogate Cardiac MAE** | $4.32\text{ bpm}$ | $4.3203\text{ bpm}$ | $+0.0003\text{ bpm}$ | Within $\pm 0.0100\text{ bpm}$ tolerance. | `VERIFIED_FROM_CSV` |
| **Max Surrogate Resp Corr** | **$< 0.42$** | **$0.8123$ (Mean: $0.5077$)**| **$+0.3923$** | **Major report overstatement.** Real surrogates reached 0.81 (`VS24_Resting`). | `DISCREPANCY (CONTRADICTED)` |
| **Surrogate p-value** | **$p < 0.001$** | **$\ge 0.167$** | **Invalid statistic** | Mathematically impossible with $N=5$ surrogate trials. | `DISCREPANCY (CONTRADICTED)` |
| **Sync Status: `PARTIALLY_ALIGNED`**| 39 | 39 | 0 | Exact match in CSV column. | `VERIFIED_FROM_CSV` |
| **Sync Status: `UNVERIFIED_TIMING`**| 9 | 9 | 0 | Exact match in CSV column. | `VERIFIED_FROM_CSV` |

---

## 7. Monitor-HR Lag & Lag-Selection Bias Investigation

### 7.1 Pipeline Specification (`src/sync_validation/ecg_processor.py`)
- **Input Signals:** Continuous 1 Hz ECG HR series $HR_{\text{ecg}}(t)$ (length 120, float) and Mindray monitor array $HR_{\text{mon}}(t)$ (length 120, uint8 converted to float).
- **Candidate Shifts:** $\tau \in [-10, +10]\text{ seconds}$, integer grid, step size $1\text{ second}$.
- **Sign Convention:**
  $$HR_{\text{mon}}(t) \approx HR_{\text{ecg}}(t - \tau)$$
  Positive lag ($\tau > 0$) strictly represents **monitor display/averaging delay** (the monitor reports past heart rates).
- **Objective Function:** Minimum MAE over valid overlapping interval:
  $$\tau^* = \arg\min_{\tau} \frac{1}{120 - |\tau|} \sum |HR_{\text{mon}}(t) - HR_{\text{ecg}}(t - \tau)|$$
- **Tie-Breaking:** Python's `min(..., key=...)` returns the first encountered minimum.

### 7.2 Critique of Heuristic Thresholding in `runner.py`
In `src/sync_validation/runner.py` (lines 98–110), the status assignment rule is:
```python
if np.isfinite(best_lag_s) and best_lag_s >= 4:
    mon_latency_status = "EMPIRICAL_LATENCY_OBSERVED"
elif np.isfinite(best_lag_s):
    mon_latency_status = "INCONCLUSIVE_LOW_HRV" if mon_lag_res["is_ambiguous"] else "NEAR_ZERO_LATENCY"
```
#### Analysis of Case Anomalies:
1. **`VS05_Apnea` ($\tau^* = -3\text{ s}$):** Assigned `NEAR_ZERO_LATENCY`! Calling a 3-second negative shift "near zero" is scientifically unsound. A negative delay implies the monitor reports heart rates 3 seconds *ahead* of ECG ventricular depolarization.
2. **`VS13_Apnea` ($\tau^* = +3\text{ s}$):** Assigned `NEAR_ZERO_LATENCY`! A 3-second delay is 3,000 ms, which is substantial.
3. **Contradictory Reason String:** In both cases, `is_ambiguous` was `False`, yet the assigned reason string stated: `"Optimal lag X s; curve flatness indicates low HR variance"`. This is an internal code bug where the reason string contradicts the boolean flag.

### 7.3 Observed Relative Lag vs. Proven Monitor Latency
Relative lag between monitor and ECG is an **empirical observation of time-series alignment**. While physiological monitor designs universally implement 5–10s moving-average filters, the observation alone does not rule out software pipeline buffering, clock drift, or display refresh quantization. Recommended terminology: **`OBSERVED_RELATIVE_LAG`**, reserving `PROVEN_MONITOR_LATENCY` for manufacturer-verified filter specifications.

---

## 8. ECG Quality, Periodic NaNs, and R-Peak Validity Investigation

### 8.1 Source Data Properties & NaN Geometry
- **Dimensions:** 60,000 samples @ $500.0\text{ Hz}$ ($120.0\text{ s}$).
- **Periodic NaN Distribution:** Exactly 36 files have 120 NaNs, 11 files have 119 NaNs, and exactly 1 file (`VS24_Resting`) has 0 NaNs.
- **Periodicity:** In all 47 affected files, NaNs occur at exact periodic intervals of 501 samples (e.g., indices 258, 759, 1260, 1761, ...). At $500\text{ Hz}$, 501 samples corresponds to $1.002\text{ seconds}$, representing 1-second packet framing boundaries in the Mindray digital telemetry stream.
- **Repair Verification:** `clean_ecg_nans` operates strictly on in-memory array copies (`np.array(..., copy=True)`). The source `.mat` files remain completely unmodified on disk. The effect of single-sample linear interpolation over 2 ms gaps on 500 Hz QRS morphology has not been quantitatively benchmarked against uncorrupted adjacent complexes and is therefore marked **`UNVERIFIED`** pending quantitative distortion analysis.

### 8.2 The `VS24_Resting` Exception
`VS24_Resting_Mindray.mat` differs fundamentally from the other 47 files:
1. File size is 1,411,993 bytes (vs ~220,000–250,000 bytes for all other files).
2. Data format is uncompressed IEEE double-precision floating point with fractional voltage values (vs integer ADC counts in others).
3. Exactly 0 NaNs exist across all ECG, pleth, and respiration channels.
4. Respiration length is 30,600 samples ($119.53\text{ s}$) vs 30,720 samples ($120.0\text{ s}$).
**Scientific Conclusion on Causality:** Observed differences are recorded strictly as empirical formatting anomalies. The root cause or origin of these formatting differences is undocumented in dataset materials and formally **`NOT_VERIFIABLE`**; causal claims attributing them to author post-collection intervention are unverified.

### 8.3 R-Peak Detection & Acceptance Criteria
- **Detector Pipeline:** 2nd-order Butterworth bandpass (5–15 Hz), 1st difference derivative, squaring, 150 ms moving integration, adaptive percentile thresholding, and $\pm 80\text{ ms}$ local refinement on filtered ECG.
- **Critique of `ecg_quality_status = PASS`:**  
  In `src/sync_validation/ecg_processor.py`, line 133:
  ```python
  if len(valid_rr) < 5: qc_verdict = "WARNING_FEW_VALID_BEATS"
  else: qc_verdict = "PASS"
  ```
  This is a critical audit finding: `ecg_quality_status = PASS` requires only **5 valid beats** across 120 seconds. It does not evaluate signal-to-noise ratio, baseline wander, or ectopic beat percentage. While all 48 files empirically had between 104 and 178 valid beats with physiological RR intervals, the code's quality threshold is overly permissive.

---

## 9. Respiratory Alignment, Lag Boundaries, and Surrogate Controls

### 9.1 Preprocessing & Resampling Trace
- **Sample Rates:** Radar $333.3333\text{ Hz}$ ($1000/3\text{ Hz}$); Mindray respiration $256.0\text{ Hz}$.
- **Resampling:** Polyphase rational resampling (`signal.resample_poly`) to $2000.0\text{ Hz}$ ($6:1$ for radar; $125:16$ for respiration).
- **Array Preservation:** Resampling executes strictly in temporary memory; no resampled arrays are saved to disk.
- **Normalization:** Zero-mean, unit-variance normalization: $v_n = (v - \mu_v)/\sigma_v$.

### 9.2 Mathematical Definition of `respiratory_uniqueness`
$$\text{respiratory\_uniqueness} = \frac{c(\tau_{\text{pos}})}{\max_{|\tau - \tau_{\text{pos}}| > 0.5\text{ s}} c(\tau) + 10^{-6}}$$
- **Physical Meaning:** Ratio of the primary cross-correlation peak to the highest secondary peak outside a $\pm 0.5\text{ s}$ neighborhood.
- **Limitation:** Because human respiration is quasi-periodic ($T_{\text{resp}} \approx 3 - 5\text{ s}$), secondary peaks naturally appear at adjacent breathing cycles. Thus, `respiratory_uniqueness` reflects respiratory periodicity rather than random noise rejection.

### 9.3 Lag Boundary Investigation: The +30.0 ms Question
In the report, the Resting respiratory lag range was stated as $[-24.50\text{ ms}, +30.00\text{ ms}]$.
- **Audit Verification:** The search window parameter passed to `compute_respiratory_xcorr` in `runner.py` is `max_lag_sec = 30.0` (i.e., **$\pm 30.0\text{ seconds}$**, or $\pm 60,000\text{ samples}$ at $2000\text{ Hz}$).
- **Conclusion:** $+30.00\text{ ms}$ represents an empirical peak at exactly 60 samples ($60 \times 0.5\text{ ms} = 30.0\text{ ms}$) observed in `VS18_Resting`. It is **NOT** a search window boundary artifact (which would have been $30,000\text{ ms}$).

### 9.4 Surrogate Controls & Statistical Validity
- **Algorithm in Production:** Fourier phase randomization preserving the amplitude spectrum (Theiler et al., 1992) with $N = 5$ trials.
- **Real vs. Surrogate Correlation Comparison:**
  - **Resting Recordings:** Real mean correlation = **$0.7005$** vs. Surrogate mean correlation = **$0.6289$** (difference: only **$0.0716$**).
  - **Apnea Recordings:** Real mean correlation = **$0.4130$** vs. Surrogate mean correlation = **$0.3865$** (difference: only **$0.0265$**).
  - **Scientific Implication:** Phase randomization destroys temporal phase alignment while preserving the power spectrum. In low-frequency respiratory signals, broad spectral peaks allow surrogates to achieve correlations nearly as high as the real signal across a $\pm 30\text{ s}$ search window. This demonstrates that the current $N=5$ surrogate control has severely limited discriminative power.
- **Audit Findings:**
  1. The report's claim that surrogate correlation "never exceeded 0.42" is **DISCREPANCY (CONTRADICTED)**. In the CSV, maximum surrogate correlations range from $0.1649$ to $0.8123$ (mean: $0.5077$, with $0.8123$ in `VS24_Resting`).
  2. The report's claim of "$p < 0.001$" is **DISCREPANCY (CONTRADICTED)**. Under the standard plus-one empirical p-value formula:
     $$p = \frac{1 + \text{count}}{N + 1}$$
     With $N = 5$ trials, the minimum possible empirical p-value is $1/(5+1) \approx 0.1667$. Achieving $p = 0.0010$ requires $N = 999$ trials, and achieving strict inequality $p < 0.001$ requires $N \ge 1000$ trials (e.g. $1/1001 \approx 0.000999$).

---

## 10. Radar–ECG Cardiac Agreement & Spectral Resolution

### 10.1 Estimator Architecture & FFT Resolution
- **Cardiac Bandpass:** Zero-phase 3rd-order Butterworth bandpass filter ($0.8 - 3.0\text{ Hz}$, corresponding to 48–180 bpm).
- **Window Geometry:** 10.0-second sliding windows with 5.0-second hop (23 windows across 120s).
- **FFT Length & Bin Resolution:**  
  $$N_{\text{win}} = \lfloor 10.0 \times 333.3333 \rfloor = 3333\text{ samples}$$
  $$\Delta f = \frac{f_s}{N_{\text{win}}} = \frac{333.3333}{3333} \approx 0.1000\text{ Hz}$$
  $$\Delta \text{HR}_{\text{bin}} = 0.1000\text{ Hz} \times 60 = \mathbf{6.000\text{ bpm}}$$
- **Quantization:** No parabolic interpolation or zero-padding was implemented in `cardiac_radar_validator.py`. Radar window HR estimates are strictly quantized to multiples of $6.0\text{ bpm}$ (e.g., 48, 54, 60, 66, 72, 78, 84, 90 bpm).

### 10.2 Resolving the "MAE Below 6 bpm" Question
A common misconception is that an estimator with $6\text{ bpm}$ bin spacing cannot achieve an MAE below $6\text{ bpm}$. This is mathematically false:
- Bin spacing $\Delta = 6.0\text{ bpm}$ represents the **maximum peak-to-peak quantization step**.
- The maximum rounding error for a continuous true heart rate rounded to the nearest bin is $\Delta / 2 = 3.0\text{ bpm}$.
- The expected mean absolute error for a uniformly distributed true HR within a bin is $\Delta / 4 = \mathbf{1.50\text{ bpm}}$.
- When averaged across 23 windows, achieving a mean MAE of $2.97\text{ bpm}$ (Resting) and $3.80\text{ bpm}$ (Apnea) is mathematically consistent with nearest-bin quantization around true physiological rates.

### 10.3 Selection Optimism in Best-Shift Optimization
In `compute_window_level_hr_agreement`, candidate trial shifts $\tau \in [-5, +5]\text{ s}$ were scanned, and the best shift was chosen by minimizing MAE on all 23 windows.
- **Diagnostic Split Results:** In 5 of 6 tested subjects, the shift selected on the first half of windows failed to generalize to the second half, with held-out MAE worsening substantially (e.g., `VS02`: held-out MAE $8.67\text{ bpm}$ vs zero-shift $7.19\text{ bpm}$; `VS05`: held-out MAE $5.50\text{ bpm}$ vs zero-shift $3.46\text{ bpm}$).
- **Scientific Conclusion:** Scanning multiple shifts on short 120s recordings introduces **in-sample selection optimism**. Best-shift metrics overstate timing precision. A **prespecified zero-shift baseline without best-shift optimization** ($2.97\text{ bpm}$ Resting MAE, $3.38\text{ bpm}$ overall MAE) must be adopted for window-level evaluation, noting that it remains subject to ECG-label quality limits and any real physical offset between radar and ECG.

---

## 11. Previous Test-Failure Investigation

Historical logs `task-444.log` and `task-476.log` provide transparent evidence of the three unit test failures encountered during initial Step 2 implementation and how they were resolved:

### 11.1 Test 1: `test_resample_signals_truncated`
- **Initial Failure (`task-444.log`):** `assert 239063 == 239062` (`AssertionError`).
- **Technical Analysis & Arithmetic:** Resampling 30,600 samples at $256\text{ Hz}$ resampled to $2000\text{ Hz}$ (factors 125/16) gives 239,063 samples:
  $$\text{Length} = \lceil 30,600 \times \frac{125}{16} \rceil = \lceil 239,062.5 \rceil = 239,063\text{ samples}$$
  The original test hardcoded an incorrect theoretical integer floor of 239,062.
- **Resolution:** The test assertion was updated to `assert abs(len(v_2000) - 239062) <= 1`.
- **Integrity Assessment:** **TOLERANCE ADJUSTMENT**. Resampling 30,600 samples at 256 Hz resampled to 2000 Hz (factors 125/16) gives 239,063 samples. The ceiling convention in `scipy.signal.resample_poly` returns exactly 239,063 samples. Provenance is `NOT_VERIFIABLE` (no git version history).

### 11.2 Test 2: `test_compute_surrogate_respiratory_control`
- **Initial Failure (`task-444.log`):** `assert 0.9804 < 0.3` (`AssertionError`).
- **Technical Analysis:** The original test fixture synthesized a pure stationary sinusoid at $0.25\text{ Hz}$ ($T = 4.0\text{ s}$). A circular shift of 60 seconds is an exact multiple of the period ($60 = 15 \times 4.0\text{ s}$), resulting in near-perfect self-correlation ($r \approx 0.98$).
- **Resolution:** The surrogate algorithm was changed from circular shifts to Fourier phase randomization, the test fixture was modified with broadband noise and AM modulation, and the assertion was loosened from `r < 0.30` to `r < 0.75`.
- **Integrity Assessment:** **THRESHOLD LOOSENING**. While phase randomization is mathematically superior to circular shifting, loosening the assertion threshold from $0.30$ to $0.75$ significantly weakens the unit test. A bound of $0.75$ allows high surrogate coherence to pass, so the test barely discriminates effective surrogate controls from noise.
- **Corrective Action:** In a later approved step, replace this assertion with a prespecified, justified criterion (e.g. real correlation exceeding a high percentile of an adequate surrogate distribution on a synthetic signal).

### 11.3 Test 3: `test_window_level_hr_agreement_synthetic`
- **Initial Failure (`task-444.log`):** `assert np.isclose(-5.0, 0.0, atol=1.0)` (`AssertionError`).
- **Technical Analysis:** The test fixture generated a stationary $1.2\text{ Hz}$ ($72\text{ bpm}$) sinusoid across all 60 seconds. Because heart rate was constant, every candidate shift $\tau \in [-5, +5]\text{ s}$ produced identical $\text{MAE} = 0.0\text{ bpm}$. Python's `min()` tie-breaker arbitrarily selected the first shift in the list ($\tau = -5.0\text{ s}$).
- **Resolution:** The test fixture was updated with a dynamic, time-varying heart-rate profile (60 bpm in the first half, 90 bpm in the second half), creating a unique, well-defined MAE minimum at $\tau = 0.0\text{ s}$.
- **Integrity Assessment:** **APPROPRIATE TEST-SIGNAL CORRECTION**. A flat objective curve caused by an ill-posed constant test signal was replaced by a physiologically representative dynamic signal that properly tests shift sensitivity.

---

## 12. Independent Recomputation Results for Selected Pairs

### 12.0 Scope Boundary of Raw-Data Verification
To maintain strict scientific precision, the scope of raw-data inspection is defined as follows:
1. **Direct Raw Array Inspection (All 48 Mindray Recordings):** All 48 continuous `ecg_lead2` waveforms were directly inspected from raw `.mat` files for shape `(60000,)`, `float64` dtype, and exact periodic delimiter NaN counts (CLM-19: 36 files @ 120, 11 files @ 119, 1 file @ 0). `VS24_Resting_Mindray.mat` was directly inspected for respiration array length = 30,600 samples (CLM-20).
2. **File Inventory Verification (All 96 Recordings):** File sizes, presence, and SHA-256 hashes for all 48 radar and 48 Mindray `.mat` files were verified against pre-audit Phase 1 snapshots (`outputs/phase1_audit/file_inventory.csv`).
3. **End-to-End Pipeline Recomputation (4 Selected Pairs Only):** The complete physiological signal processing pipeline (Pan-Tompkins QRS detection, continuous 1 Hz instantaneous HR derivation, candidate lag optimization, polyphase resampling to 2000 Hz, cross-correlation, and windowed FFT) was independently recomputed from raw arrays on **only the four selected candidate pairs** (`VS01_Resting`, `VS24_Resting`, `VS09_Resting`, `VS02_Apnea`) using scratch code (`independent_recompute.py`).
4. **Dataset-Wide Metrics (CSV_ONLY):** For the remaining 44 candidate pairs and all dataset-wide summary statistics (mean monitor lag, median monitor lag, mean window MAE, mean respiratory lag/correlation), values are verified from `outputs/phase2a/sync_validation_results.csv` and classified strictly as `CSV_ONLY`. Dataset-wide independent pipeline recomputation across all 96 files was not performed and is not claimed.

Selected candidate pairs for independent pipeline recomputation:
1. **`VS01_Resting`:** Typical Resting recording.
2. **`VS24_Resting`:** Formatting divergence (0 NaNs, 30,600 respiration samples; root cause `NOT_VERIFIABLE`).
3. **`VS09_Resting`:** Verified negative respiratory polarity recording.
4. **`VS02_Apnea`:** Apnea recording with large monitor HR latency (+10s).

### 12.1 Independent Recomputation vs. CSV Comparison Table

| Subject & Condition | Evaluated Metric | CSV Stored Value | Independent Recomputed Value | Discrepancy | Tolerance / Rule | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`VS01_Resting`** | ECG Sample Count | 60,000 | 60,000 | 0.0000 | 0 | **EXACT** |
| `VS01_Resting` | ECG NaN Count | 120 | 120 | 0.0000 | 0 | **EXACT** |
| `VS01_Resting` | Valid R-Peak Count | 113 | 113 | 0.0000 | 0 | **EXACT** |
| `VS01_Resting` | Mean ECG HR (bpm) | 56.53 | 56.53 | 0.0000 | $\pm 0.05$ | **EXACT** |
| `VS01_Resting` | Monitor HR Lag (s) | +7 | +7 | 0.0000 | 0 | **EXACT** |
| `VS01_Resting` | Monitor Zero MAE (bpm) | 1.7813 | 1.7813 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS01_Resting` | Monitor Best MAE (bpm) | 1.3787 | 1.3787 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS01_Resting` | Resp Lag (ms) | +0.50 | +0.50 | 0.0000 | $\pm 0.5$ | **EXACT** |
| `VS01_Resting` | Resp Corr | 0.4434 | 0.4434 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS01_Resting` | Resp Polarity | +1 | +1 | 0.0000 | 0 | **EXACT** |
| `VS01_Resting` | Radar Window MAE Zero (bpm) | 2.1113 | 2.1113 | 0.0000 | $\pm 0.05$ | **EXACT** |
| **`VS24_Resting`** | ECG Sample Count | 60,000 | 60,000 | 0.0000 | 0 | **EXACT** |
| `VS24_Resting` | ECG NaN Count | 0 | 0 | 0.0000 | 0 | **EXACT** |
| `VS24_Resting` | Valid R-Peak Count | 142 | 142 | 0.0000 | 0 | **EXACT** |
| `VS24_Resting` | Mean ECG HR (bpm) | 71.08 | 71.08 | 0.0000 | $\pm 0.05$ | **EXACT** |
| `VS24_Resting` | Monitor HR Lag (s) | +6 | +6 | 0.0000 | 0 | **EXACT** |
| `VS24_Resting` | Monitor Zero MAE (bpm) | 2.7305 | 2.7305 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS24_Resting` | Monitor Best MAE (bpm) | 2.2950 | 2.2950 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS24_Resting` | Resp Lag (ms) | -3.00 | -3.00 | 0.0000 | $\pm 0.5$ | **EXACT** |
| `VS24_Resting` | Resp Corr | 0.9044 | 0.9044 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS24_Resting` | Resp Polarity | +1 | +1 | 0.0000 | 0 | **EXACT** |
| `VS24_Resting` | Radar Window MAE Zero (bpm) | 1.4821 | 1.4821 | 0.0000 | $\pm 0.05$ | **EXACT** |
| **`VS09_Resting`** | ECG Sample Count | 60,000 | 60,000 | 0.0000 | 0 | **EXACT** |
| `VS09_Resting` | ECG NaN Count | 120 | 120 | 0.0000 | 0 | **EXACT** |
| `VS09_Resting` | Valid R-Peak Count | 133 | 133 | 0.0000 | 0 | **EXACT** |
| `VS09_Resting` | Mean ECG HR (bpm) | 66.53 | 66.53 | 0.0000 | $\pm 0.05$ | **EXACT** |
| `VS09_Resting` | Monitor HR Lag (s) | +8 | +8 | 0.0000 | 0 | **EXACT** |
| `VS09_Resting` | Monitor Zero MAE (bpm) | 2.0193 | 2.0193 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS09_Resting` | Monitor Best MAE (bpm) | 1.1413 | 1.1413 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS09_Resting` | Resp Lag (ms) | +1.00 | +1.00 | 0.0000 | $\pm 0.5$ | **EXACT** |
| `VS09_Resting` | Resp Corr | 0.6418 | 0.6418 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS09_Resting` | Resp Polarity | -1 | -1 | 0.0000 | 0 | **EXACT** |
| `VS09_Resting` | Radar Window MAE Zero (bpm) | 1.5734 | 1.5734 | 0.0000 | $\pm 0.05$ | **EXACT** |
| **`VS02_Apnea`** | ECG Sample Count | 60,000 | 60,000 | 0.0000 | 0 | **EXACT** |
| `VS02_Apnea` | ECG NaN Count | 120 | 120 | 0.0000 | 0 | **EXACT** |
| `VS02_Apnea` | Valid R-Peak Count | 145 | 145 | 0.0000 | 0 | **EXACT** |
| `VS02_Apnea` | Mean ECG HR (bpm) | 72.63 | 72.63 | 0.0000 | $\pm 0.05$ | **EXACT** |
| `VS02_Apnea` | Monitor HR Lag (s) | +10 | +10 | 0.0000 | 0 | **EXACT** |
| `VS02_Apnea` | Monitor Zero MAE (bpm) | 3.2403 | 3.2403 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS02_Apnea` | Monitor Best MAE (bpm) | 1.9434 | 1.9434 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS02_Apnea` | Resp Lag (ms) | 0.00 | 0.00 | 0.0000 | $\pm 0.5$ | **EXACT** |
| `VS02_Apnea` | Resp Corr | 0.3841 | 0.3841 | 0.0000 | $\pm 0.01$ | **EXACT** |
| `VS02_Apnea` | Resp Polarity | +1 | +1 | 0.0000 | 0 | **EXACT** |
| `VS02_Apnea` | Radar Window MAE Zero (bpm) | 3.9921 | 3.9921 | 0.0000 | $\pm 0.05$ | **EXACT** |

---

## 13. Synchronization-Status Classification Audit

### 13.1 Orthogonal Status Decomposition
The current pipeline conflates hardware clock timing, respiratory cross-correlation, and window-level cardiac agreement into a single legacy column (`radar_to_ecg_sync_status`). To establish rigorous scientific boundaries, evaluation must be decoupled into three independent dimensions:

1. **`hardware_clock_status`:**  
   - Formal Status: **`UNVERIFIED` across all 48 candidate pairs (100%)**.  
   - Rationale: Neither radar digitizer nor Mindray monitor headers contain shared hardware clock timestamps, common TTL trigger channels, or synchronizing digital markers.
2. **`respiratory_alignment_status`:**  
   - Formal Status: **`CONSISTENT_NOT_PROVEN` for 24/24 Resting pairs; `INCONCLUSIVE` (suppressed breathing) for 24/24 Apnea pairs**.  
   - Legacy CSV Label (Historical): `EMPIRICALLY_ALIGNED_SUB_30MS` (21 Resting pairs) / `WEAK_CORRELATION` (3 Resting pairs: `VS02`, `VS18`, `VS20`).  
   - Scientific Reason for Downgrade: The $N = 5$ surrogate control has severely limited discriminative power (Resting real mean 0.7005 vs surrogate mean 0.6289; $p_{\min} \approx 0.167$). In accordance with Section 6.2, respiratory alignment remains `CONSISTENT_NOT_PROVEN` until an approved $N \ge 1000$ surrogate run is completed.
3. **`cardiac_window_adequacy_status`:**  
   - Formal Status: **`NOT YET SUPPORTED` across all 48 candidate pairs**.  
   - Legacy CSV Label (Historical): `ADEQUATE_FOR_10S_WINDOWS` (39 pairs) / `EVALUATE_WITH_CAUTION` (9 pairs).  
   - Scientific Reason: No "adequate" cardiac window status can be granted while the 10-second window-alignment headline remains `NOT YET SUPPORTED` due to the lack of an independently justified, prespecified adequacy gate and unvalidated amplitude stability.

### 13.2 Inventory of the 9 Historical `UNVERIFIED_TIMING` Pairs & Threshold Provenance
In `sync_validation_results.csv`, 9 pairs failed the internal classification rule of `runner.py`:
- `VS02_Resting`: Weak respiratory correlation ($r = 0.2029 < 0.40$).
- `VS18_Resting`: Weak respiratory correlation ($r = 0.2437 < 0.40$).
- `VS20_Resting`: Weak respiratory correlation ($r = 0.3385 < 0.40$).
- `VS03_Apnea`: Cardiac window zero-shift MAE ($6.48\text{ bpm} \ge 5.0$).
- `VS06_Apnea`: Cardiac window zero-shift MAE ($5.45\text{ bpm} \ge 5.0$).
- `VS10_Apnea`: Cardiac window zero-shift MAE ($5.30\text{ bpm} \ge 5.0$).
- `VS11_Apnea`: Cardiac window zero-shift MAE ($7.43\text{ bpm} \ge 5.0$).
- `VS14_Apnea`: Cardiac window zero-shift MAE ($6.97\text{ bpm} \ge 5.0$).
- `VS20_Apnea`: Cardiac window zero-shift MAE ($8.32\text{ bpm} \ge 5.0$).

**Threshold Provenance Trace:**
- **Cardiac Window MAE Threshold ($5.0\text{ bpm}$):** Defined in `src/sync_validation/runner.py` (line 101) as the decision boundary for Apnea cardiac window-level HR agreement (`cardiac_res.get("zero_shift_mae_bpm") < 5.0`).
- **Trial Shift / Lag Exploration Range ($5.0\text{ s}$):** Defined in `src/sync_validation/cardiac_radar_validator.py` (lines 47, 51) as the trial shift range $\tau \in [-5.0, +5.0]\text{ s}$ across which optimal lag is evaluated.
- **Respiratory Correlation Threshold ($r \ge 0.40$):** Defined in `src/sync_validation/runner.py` (line 93).
- **Threshold Provenance:** Neither the dataset documentation (`README.txt`, `Subject Information.xlsx`), nor `TechValidation.m` (which is absent), nor any pre-experimental protocol defined or justified these specific numeric values. The 0.40, 50 ms, and 5.0 bpm thresholds were not prespecified in any available document; provenance NOT_VERIFIABLE (no git version history or commit logs available in the local repository).

---

## 14. Identified Discrepancies with Specific Subject Examples

1. **Negative Polarity Misidentification:**  
   - Report stated: `VS02_Resting` and `VS19_Resting` were negative polarity.  
   - Actual CSV evidence: `VS02_Resting` ($+1$, $r = +0.2029$), `VS19_Resting` ($+1$, $r = +0.5001$), `VS09_Resting` ($-1$, $r = -0.6418$), `VS20_Resting` ($-1$, $r = -0.3385$).
2. **Surrogate Maximum Correlation Overstatement:**  
   - Report stated: Surrogate correlation "never exceeded 0.42".  
   - Actual CSV evidence: Reaches up to **$0.8123$** in `VS24_Resting`, **$0.8058$** in `VS10_Resting`, and **$0.7898$** in `VS17_Resting`. Maximum surrogate correlation across the entire dataset is **`VS24_Resting` (0.8123)**.
3. **Resting Correlation $> 0.85$ Subject List:**  
   - Report stated: 14 subjects exceeded 0.85.  
   - Actual CSV evidence: Exactly 6 subjects exceeded 0.85: **`VS03` (0.8882), `VS07` (0.8666), `VS10` (0.9327), `VS12` (0.8606), `VS17` (0.8958), `VS24` (0.9044)**.
4. **Heuristic Latency Misclassification (`VS05_Apnea`):**  
   - Optimal lag: $-3\text{ s}$ (best MAE: $4.51\text{ bpm}$).  
   - Code assignment: `NEAR_ZERO_LATENCY` with reason citing "curve flatness", even though `is_ambiguous` was `False`.

---

## 15. Risk Assessment Ranked by Severity

### Critical Severity:
- **`RISK-CRIT-01` (Supervision Contamination via Monitor `HR`):** Training KAN models against the raw monitor `HR` array would introduce a systematic 6–7 second temporal lag, directly misaligning ground-truth targets with radar input windows.

### High Severity:
- **`RISK-HIGH-01` (Hardware Clock Absence):** Sub-second physical synchronization cannot be established at the hardware clock level. While empirical cardiac-band agreement is observed at zero shift for 10-second windows in Resting recordings, the 10-second window adequacy headline remains NOT YET SUPPORTED, and millisecond-level physiological modeling (e.g., pulse transit time) is strictly unfeasible.
- **`RISK-HIGH-02` (Overly Permissive ECG QC):** `ecg_quality_status = PASS` requires only 5 valid beats. Poor-quality segments could introduce noisy instantaneous HR labels if not filtered with stricter signal quality indices.

### Medium Severity:
- **`RISK-MED-01` (Selection Optimism in Trial Shifts):** Searching multiple lags on 23 windows introduces in-sample overfitting. Models must be supervised using strictly zero-shift ECG labels.
- **`RISK-MED-02` (FFT Bin Quantization Noise):** A 10-second window yields $6.0\text{ bpm}$ discrete bins. Estimator benchmarks without parabolic peak interpolation suffer from discretization noise.
- **`RISK-MED-03` (Apnea Respiratory Fallacy):** Cross-correlating flatline or low-amplitude respiration during voluntary apnea produces arbitrary peaks.

### Low Severity:
- **`RISK-LOW-01` (`VS24_Resting` Formatting Divergence):** Uncompressed 1.4 MB MAT format, 0 NaNs, and 30,600 respiration samples represent empirical formatting anomalies whose origin is NOT_VERIFIABLE, requiring dynamic in-memory trailing tail truncation.

---

## 16. Recommended Corrections Linked to Evidence

1. **Mandate ECG R-Peak Ground Truth (`src/preprocessing/`):**  
   Generate training targets exclusively by averaging continuous instantaneous heart rates $HR_{\text{ecg}}(t)$ derived from Pan-Tompkins QRS detection on `ecg_lead2`. Permanently reject the 120-point monitor `HR` array as a training label source.
2. **Implement Multi-Feature ECG Quality Index (SQI):**  
   Upgrade `detect_r_peaks` to compute physiological RR interval coverage ($> 85\%$ of recording), maximum allowable gap ($< 3.0\text{ s}$), and QRS amplitude consistency before granting `PASS`.
3. **Decouple Status Columns:**  
   Split `radar_to_ecg_sync_status` into `hardware_clock_status` and `window_alignment_status` to prevent false claims of verified hardware timing.
4. **Implement Parabolic Peak Interpolation:**  
   Refine cardiac FFT frequency peaks using 3-point parabolic interpolation:
   $$\delta = \frac{A_{k+1} - A_{k-1}}{2(2A_k - A_{k-1} - A_{k+1})}$$
   reducing quantization error well below the native $6.0\text{ bpm}$ bin width.

---

## 17. Limitations & Unresolved Questions

1. **Manufacturer Averaging Algorithm:** The exact mathematical transfer function (FIR, IIR, or moving median) used by the Mindray monitor to compute `HR` is undocumented in the public dataset.
2. **Hardware Clock Verification:** Without oscilloscope trigger logs or common hardware timestamps, absolute sub-millisecond start-time synchronization remains unverified.
3. **Post-Processing Provenance of `VS24_Resting`:** The exact software tool and rationale used by the authors to produce the floating-point, zero-NaN `VS24_Resting_Mindray.mat` file remains unknown.

---

## 18. Explicit Decision: Preprocessing Pipeline

### **DECISION: Preprocessing: CONDITIONAL GO (in-memory working copies only)**

#### Justification & Operational Findings:

### 18.1 Intact Signal Integrity Verified
All 48 radar signals (`VitalSig`, 40,000 samples @ 333.33 Hz) and reference signals (`ecg_lead2`, 60,000 samples @ 500 Hz) are mathematically clean, finite, and free from fatal corruption.

### 18.2 In-Memory Working Copies
- **In-Memory Working Copies: Requirement (current implementation status: IMPLEMENTED)**  
  All exploratory preprocessing operations (bandpass filtering, single-sample NaN interpolation, polyphase resampling, spectral peak tracking) must operate strictly on temporary working copies in memory, preserving the original `.mat` files unmodified on disk.  
  *Code Evidence:* `src/sync_validation/ecg_processor.py:22` creates copies via `np.array(ecg_raw, copy=True, dtype=np.float64)` and `src/sync_validation/respiratory_validator.py:25-26` creates copies via `np.array(vitalsig, copy=True, dtype=np.float64)` and `np.array(respiration, copy=True, dtype=np.float64)`. All routines execute in-memory; no routines write, touch, or re-save raw `.mat` files.

### 18.3 Dynamic Array Lengths & Trailing Tail Truncation
- **Dynamic Array Lengths: Requirement (current implementation status: PARTIAL)**  
  Preprocessing code must dynamically query array lengths and safely truncate mismatched signals to the common minimum length in memory, avoiding hardcoded sample counts (e.g., 30,720 samples across recordings).  
  *Code Evidence:* `src/sync_validation/respiratory_validator.py:51-52` dynamically computes `min_len = min(len(v_2000), len(r_2000))` and truncates to `[:min_len]`. However, raw array length verification and length discrepancy logging for `VS24_Resting` (30,600 samples vs standard 30,720 samples) is not yet formalized at raw loading time (planned Stage 2 fix ISS-12).

### 18.4 Single-Sample NaN Interpolation
- **Single-Sample NaN Interpolation: Requirement (current implementation status: PARTIAL)**  
  Linear in-memory interpolation must apply exclusively to isolated single-sample periodic delimiter NaNs (~120 per 120s trace); multi-sample gaps must not be interpolated and must be explicitly flagged with indices logged.  
  *Code Evidence:* `src/sync_validation/ecg_processor.py:27-32` implements in-memory linear interpolation via `ecg[nan_indices] = np.interp(nan_indices, valid_indices, ecg[valid_indices])`. However, it currently interpolates all detected NaNs uniformly without checking for isolation ($N_{\text{gap}} = 1$) or rejecting multi-sample gaps ($N_{\text{gap}} \ge 2$) (planned Stage 2 fix ISS-13).

### 18.5 Peak Interpolation & Spectral Grid Refinement
- **4x Zero-Padding: Requirement (current implementation status: NOT_IMPLEMENTED)**  
  Evaluating the DTFT on a denser frequency grid via 4x zero-padding ($N_{\text{fft}} = 4 \times N_{\text{win}}$, exactly 4x the window length as prespecified in ISS-09; the 65,536-bin parameter was an unapproved heuristic from generic DSP conventions and is removed) provides spectral interpolation (a finer frequency evaluation grid) with no improvement in native resolution.  
  *Code Evidence:* Missing in `src/sync_validation/cardiac_radar_validator.py:88, 126, 168`, which currently executes unpadded FFTs `np.fft.rfft(w * np.hamming(len(w)))` with $N_{\text{fft}} = \text{len}(w) \approx 3,333\text{ bins}$ (planned Stage 2 fix ISS-09).
- **Parabolic Peak Interpolation: Requirement (current implementation status: NOT_IMPLEMENTED)**  
  3-point parabolic peak interpolation is required to resolve continuous peak frequencies beyond discrete bin discretization ($0.1\text{ Hz} = 6.0\text{ bpm}$). Only parabolic interpolation directly addresses discrete peak discretization error.  
  *Code Evidence:* Missing in `src/sync_validation/cardiac_radar_validator.py:91, 129, 171`, which currently selects the discrete FFT bin directly using `freqs[mask][np.argmax(np.abs(w_fft[mask]))]` without interpolation (planned Stage 2 fix ISS-09).

*Spectral vs Time-Domain Distinction:* Zero-padding provides spectral interpolation (evaluating the discrete-time Fourier transform on a finer frequency grid without altering native Rayleigh resolution), and only 3-point parabolic interpolation addresses peak frequency discretization error. Both frequency-domain refinements apply strictly to discrete frequency estimation of the bandpassed cardiac signal; they are distinct from time-domain sample interpolation.

---

## 19. Explicit Decision: Supervised-Label Generation

### **DECISION: Supervised-label generation: NOT YET APPROVED**

#### Justification & Evaluation Gates:
1. **Permanent Disqualification of Monitor `HR` Array:** The 120-point Mindray `HR` array is permanently rejected as a ground-truth label source for this project and version due to its confirmed $+6\text{ to }+7\text{ second}$ latency. It may be used only as a secondary descriptive cross-check.
2. **Conditional Path for Future Label Generation:** Future supervised window labels may be considered exclusively from **ECG R-peak-derived heart rate** ($HR_{\text{ecg}}(t)$), evaluated strictly at zero time shift ($\tau = 0$). No label generation is authorized by this audit.
3. **Mandatory Future Approval Gates:**
   - **Recording-Level SQI Gate:** Before any recording is admitted for label generation, it must achieve recording-level SQI `PASS` based on: (1) beat coverage $> 85\%$ of the 120s duration, (2) maximum RR gap strictly below $3.0\text{ s}$, and (3) amplitude stability. The amplitude-stability threshold is currently **UNSPECIFIED / NOT VALIDATED**; no recording-level SQI `PASS` can be granted until an amplitude-stability threshold is formally proposed and approved.
   - **Window-Level Coverage Gate:** Every 10-second candidate window must possess valid RR coverage $> 80\%$ (i.e. $\sum \text{valid } RR \ge 8.0\text{ s}$ within the $[t_w, t_w + 10\text{ s}]$ interval). Windows failing this criterion are disqualified from supervised label generation without silent interpolation or artificial repair.
   - **Condition Segregation:** Resting and Apnea recordings represent distinct physiological dynamics and are separated into isolated pipelines without cross-condition pooling.

---

## 20. Automated Test Commands & Verification Outcomes

The sandboxed unit test suite was executed in compliance with Section 10 safety guidelines:

- **Component Test Command:**  
  `$env:PYTHONDONTWRITEBYTECODE="1"; python -m pytest -p no:cacheprovider tests/test_sync_validation.py -q`
- **Component Test Result:**  
  `................ [100%]`  
  **16 passed in 8.30 seconds (0 failed, 0 skipped, 0 warnings)**
- **Full Project Test Command:**  
  `$env:PYTHONDONTWRITEBYTECODE="1"; python -m pytest -p no:cacheprovider tests/ -q`
- **Full Project Test Result:**  
  `................................................ [100%]`  
  **48 passed in 17.56 seconds (0 failed, 0 skipped, 0 warnings)**
- **Sandboxed Execution Integrity:** Environment flag `PYTHONDONTWRITEBYTECODE=1` prevented bytecode compilation. The `-p no:cacheprovider` flag ensured `.pytest_cache` was not modified or written.

---

## 21. Phase 2A — Step 2B Reconciliation Addendum & Finalization Gate

### 21.1 Phase 1 Versus Step 2B ECG NaN Discrepancy Resolution & Audit Trace

#### The Discrepancy:
Phase 1 audit artifacts (`outputs/phase1_audit/data_quality_report.csv` and `outputs/phase1_audit/reference_inventory.csv`) reported **0 NaNs** in reference vital signs, whereas Step 2B identified **119 to 120 periodic single-sample NaNs** occurring every ~501 samples (~1.0s) in 47 of 48 `ecg_lead2` recordings.

#### Forensic Code & File Trace:
1. **Phase 1 Validation Target (`src/phase1_audit/validate_data.py`, lines 315–439):**  
   In Phase 1, `validate_reference_signal` examined exclusively the variable `HR` (`ref_field_path = "HR"`, `uint8`, shape `(120, 1)`). For all 48 files, `HR` is an 8-bit unsigned integer array with exactly 0 NaNs. Lines 509–523 performed only a presence and shape check on `ecg_lead2` (`check_performed = "field_presence_ecg"`), never computing `np.isnan(ecg_lead2).sum()`.
2. **Step 2B Validation Target (`src/sync_validation/ecg_processor.py`, lines 18–35):**  
   Step 2B introduced the Pan-Tompkins QRS detector, which evaluated the full 60,000-sample continuous `ecg_lead2` array (`float64`). Here, the single-sample NaNs were discovered.
3. **Distribution of NaNs Across Raw Files:**  
   Direct evaluation across all 48 `*_Mindray.mat` raw files confirms:
   - **36 files:** Exactly 120 single-sample NaNs.
   - **11 files:** Exactly 119 single-sample NaNs.
   - **1 file (`VS24_Resting_Mindray.mat`):** Exactly 0 NaNs.
   - **Total NaNs in `ecg_lead2`:** $36 \times 120 + 11 \times 119 + 0 = 5,629\text{ NaNs}$.
   - **Total NaNs in `HR`:** Exactly 0 across all 48 files.

#### Reconciliation Conclusion:
The discrepancy is **RESOLVED**. There was no mathematical contradiction between the tools; rather, Phase 1 audited the `HR` field, whereas Step 2B audited the raw continuous `ecg_lead2` waveform. Single-sample NaNs in `ecg_lead2` represent periodic digital packet boundary delimiters.

---

### 21.2 `TechValidation.m` Provenance & Exclusion from Scope

- **Filesystem Search Result:** A recursive search of the workspace (`c:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work`) confirmed that `TechValidation.m` is **NOT PRESENT** on local disk.
- **Formal Provenance Status:** **`NOT_AVAILABLE — EXCLUDED FROM SCOPE`**.
- **Audit Impact:**
  - All statements in Phase 1 or Phase 2A reports attributing specific algorithmic validation or empirical synchronization to `TechValidation.m` are formally designated **`UNVERIFIED`**.
  - The current Python validation pipeline (`src/sync_validation/`) operates independently of `TechValidation.m`, implementing self-contained mathematical routines for polyphase resampling, Pan-Tompkins detection, and cross-correlation.

---

### 21.3 Dynamic Array-Length & Respiration Truncation Protocol (`VS24_Resting`)

- **Empirical Array Lengths:**
  - Standard files (47 recordings): `respiration` = 30,720 samples (120.0s @ 256 Hz); `VitalSig` = 40,000 samples (120.0s @ 333.33 Hz).
  - Exception file (`VS24_Resting`): `respiration` = 30,600 samples (119.53s @ 256 Hz); `VitalSig` = 40,000 samples (120.0s @ 333.33 Hz).
- **Safe Truncation Rule:**
  - Common minimum length for respiration = 30,600 samples.
  - Number of trailing samples excluded from standard respiration arrays: 120 samples ($0.47\text{ s}$).
  - All length truncation must occur dynamically in-memory on working arrays. The raw `VS24_Resting_Mindray.mat` file remains untouched.

---

### 21.4 Isolated Delimiter NaN In-Memory Interpolation Protocol

- **Eligibility Criterion:** Linear interpolation is permitted strictly for isolated, single-sample NaNs ($N_{\text{gap}} = 1$) spaced at periodic intervals ($\Delta t \approx 501\text{ samples} \approx 1.0\text{ s}$).
- **Prohibition:** Any multi-sample gap ($N_{\text{gap}} \ge 2$) or non-periodic burst of NaNs is ineligible for interpolation and must trigger window rejection.
- **Trace Preservation:** In-memory interpolation must be executed on temporary arrays; the raw array and its exact NaN indices must be logged and preserved.

---

### 21.5 Prespecified Signal Quality Gates

Before supervised training labels may ever be generated, candidate recordings and windows must satisfy two rigorous, hierarchical gates:

#### Gate 1: Recording-Level SQI Gate
A recording receives an SQI verdict of `PASS` only if all three criteria are met:
1. **Beat Coverage:** $\frac{\sum \text{valid } RR}{120.0\text{ s}} > 85\%$.
2. **Maximum RR Gap:** $\max(RR) < 3.0\text{ s}$ across the entire 120s duration.
3. **Amplitude Stability:** QRS amplitude consistency across the recording. Because no validated amplitude-stability threshold currently exists in the codebase or literature for this dataset, this criterion is formally marked **`UNSPECIFIED / NOT VALIDATED`**. Consequently, no recording-level SQI `PASS` is awarded during this phase.

#### Gate 2: Window-Level Coverage Gate
For every candidate 10-second target window $[t_w, t_w + 10\text{ s}]$:
- **Numerator:** Sum of durations of valid RR intervals falling within the window.
- **Denominator:** Window duration ($10.0\text{ s}$).
- **Threshold:** Valid RR coverage $> 80\%$ ($> 8.0\text{ s}$).
- **Enforcement:** Windows failing coverage $> 80\%$ must be rejected outright. Interpolation or synthetic beat imputation across failed windows is prohibited.

---

### 21.6 Respiratory Surrogate Control Limitation ($N=5$) and Future Protocol

- **Sample Size Deficiency:** The current pipeline computed surrogate cross-correlation across only $N = 5$ phase-randomized surrogate realizations.
- **Mathematical Bound on P-Values:** In a permutation/surrogate test with $N$ realizations, under the standard plus-one empirical p-value formulation:
  $$p = \frac{1 + \text{count}}{N + 1}$$
  With $N = 5$ trials, the minimum possible empirical p-value is:
  $$p_{\min} = \frac{1}{5 + 1} = \frac{1}{6} \approx 0.1667$$
- **Refutation of Prior Report Claims:** The prior claim that respiratory cross-correlation was significant at "$p < 0.001$" is mathematically false. Furthermore, surrogate correlations in the CSV reach up to **0.8123** (mean: **0.5077**, Resting mean: **0.6289**, observed in `VS24_Resting`), proving that phase-randomized surrogates can preserve substantial low-frequency correlation.
- **Real vs. Surrogate Correlation Comparison (Recomputed from CSV):**
  - **Resting Recordings:** Real mean correlation = **0.7005** vs. Surrogate mean correlation = **0.6289** (difference: only **0.0716**).
  - **Apnea Recordings:** Real mean correlation = **0.4130** vs. Surrogate mean correlation = **0.3865** (difference: only **0.0265**).
  - **Scientific Implication:** Phase randomization destroys temporal phase alignment while preserving the power spectrum. In low-frequency respiratory signals with broad spectral peaks, phase-randomized surrogates achieve correlations nearly as high as the real signal across a $\pm 30\text{ s}$ search window. This minimal separation demonstrates that the current $N=5$ surrogate control has severely limited discriminative power.
- **Status Assignment:** **`Respiratory alignment status: CONSISTENT_NOT_PROVEN`** (Resting) / **`INCONCLUSIVE`** (Apnea).
- **Specification for Future $N \ge 1000$ Protocol:**
  - Realizations: $N \ge 1000$ independent phase-randomized surrogate traces. (Note: $N = 999$ yields $p_{\min} = 1/1000 = 0.0010$, which does not satisfy strict inequality $p < 0.001$; $N \ge 1000$ is strictly required).
  - Test Statistic: Maximum absolute normalized cross-correlation $|r_{\max}|$.
  - Alpha Level: $\alpha = 0.05$ with Bonferroni correction for multiple comparisons across subjects.
  - Total Confidence Interval Width: Required to be strictly $< 1.0\text{ s}$ per recording.
  - **Evidence Gate Distinction:** The observed across-subject mean lag 95% confidence interval width ($6.99\text{ ms}$, CLM-14) is a confidence interval of the *across-subject mean*, NOT a per-recording lag CI. It does NOT satisfy this per-recording evidence gate.

---

### 21.7 Test-Threshold Loosening and Assertion Integrity Audit

An audit of `tests/test_sync_validation.py` and historical execution traces revealed two specific assertion adjustments:

| Test Name | Original / Expected Assertion | Current Implemented Assertion | Reason for Change | Scientific Impact | Required Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `test_compute_surrogate_respiratory_control` | `ctrl['max_surrogate_corr'] < 0.30` | `ctrl['max_surrogate_corr'] < 0.75` (line 183) | Circular shift fixture failed on pure sine wave due to harmonic periodicity ($60\text{s} = 15$ full cycles, $r = 1.0$). Test fixture was modified by adding broadband noise and AM modulation. | **THRESHOLD LOOSENING (WEAKENS TEST)**: A threshold of $0.75$ allows high surrogate coherence to pass, weakening the test's ability to discriminate between authentic coupling and spectral harmonic artifacts. The modification constitutes a threshold loosening that weakens verification rigor rather than an algorithmic improvement or fix. | Retain test for pass in current audit. In a later approved phase (not now), replace with a prespecified, justified assertion (e.g., real correlation exceeding 95th percentile of surrogate distribution on synthetic signal). |
| `test_resample_signals_truncated` | `len(v_2000) == 239062` | `abs(len(v_2000) - 239062) <= 1` (line 134) | Polyphase rational resampling (`scipy.signal.resample_poly`) of 30,600 samples by $125/16$ produces exactly: $30600 \times 125 / 16 = 239,062.5$. Ceiling: $239,063$. Direct verification confirms the installed implementation strictly follows the ceiling convention, returning exactly $239,063$ samples (`len(y) == 239063` evaluates to `True`). | **ASSERTION EVALUATION**: The appropriate exact expected-length assertion is `== 239063`. The original expectation `== 239062` was inconsistent with the verified ceiling convention, and the current `abs(len - 239062) <= 1` assertion is unnecessarily permissive because it tolerates 239,061, 239,062, and 239,063. Note: `git` is unavailable to inspect commit provenance (history unavailable). | Finding documented for future pipeline cleanup; current test file is retained unmodified per read-only constraints. |

---

### 21.8 Headline Wording Evidence Gate & Scientific Justification

- **Proposed Headline:** *"WINDOW-LEVEL ALIGNMENT ADEQUATE FOR 10 s WINDOWS; HARDWARE CLOCK UNVERIFIED"*
- **Evidence Gate Evaluation:**
  1. *Prespecified Adequacy Criterion:* None was established prior to viewing empirical MAE results.
  2. *Origin of Thresholds:* The $5.0\text{ bpm}$ MAE, $50\text{ ms}$ lag, and $r = 0.40$ correlation thresholds in `src/sync_validation/runner.py` (lines 93, 101) were not prespecified in any available document; provenance NOT_VERIFIABLE.
  3. *Selection Optimism:* In-sample shift optimization ($\tau \in [-5, +5]\text{ s}$) produces an artificial $0.50\text{ bpm}$ reduction in MAE ($2.47\text{ bpm}$ best-shift vs $2.97\text{ bpm}$ zero-shift). Diagnostic split tests proved that chosen shifts do not reliably generalize out-of-sample.
  4. *Baseline Terminology:* The zero-shift baseline exhibits observed empirical errors ($2.97\text{ bpm}$ Resting MAE) rather than unbiasedness, remaining subject to ECG-label quality limits, R-peak detector jitter, and any physiological offset between thoracic displacement and ventricular depolarization. It is formally designated a **"prespecified zero-shift baseline without best-shift optimization ($2.97\text{ bpm}$ Resting MAE)"**.
  5. *Condition Disaggregation:* Resting ($2.97\text{ bpm}$ MAE) and Apnea ($3.80\text{ bpm}$ MAE) show distinct dynamics and must be reported separately.
  6. *Unresolved Signal Quality:* Amplitude stability remains unvalidated, and monitor HR latency introduces potential reference bias.
- **Formal Status:** The proposed headline is **`NOT YET SUPPORTED`**.
- **Conservative Replacement Headline:**
  **\"EMPIRICAL RESTING CARDIAC-BAND AGREEMENT OBSERVED FOR 10 s WINDOWS AT ZERO SHIFT (MAE = 2.97 BPM); SUPERVISED LABEL GENERATION NOT YET APPROVED; HARDWARE CLOCK UNVERIFIED\"**

---

### 21.9 Comprehensive Numerical-Claim Reconciliation Table

All 26 material numerical claims audited across Phase 1, Phase 2A, and Step 2B artifacts are reconciled below. Per audit rules, verification types are strictly restricted to: `RAW_RECOMPUTED`, `SAME_ALGORITHM_REPRODUCED`, `FILESYSTEM_SEARCH`, `CSV_ONLY`, `REPORT_ONLY`, or `UNVERIFIED`:

| Claim ID | Reported Claim | Source Artifact | Data Location | Recalculation Method | Expected vs Recomputed | Difference and Tolerance | Verification Type | Audit Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **CLM-01** | Monitor HR mean lag = $+6.21\text{ s}$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_lag_estimate_s` (48 rows) | Arithmetic mean across 48 recordings (4 pairs recomputed from raw MAT) | Expected: $+6.2083\text{ s}$<br>Recomputed: $+6.2083\text{ s}$ | $0.0000\text{ s}$ (tol $\pm 0.0100\text{ s}$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-02** | Monitor HR median lag = $+7.0\text{ s}$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_lag_estimate_s` (48 rows) | 50th percentile across 48 recordings | Expected: $+7.0\text{ s}$<br>Recomputed: $+7.0\text{ s}$ | $0.0000\text{ s}$ (tol $\pm 0.0000\text{ s}$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-03** | Monitor HR mode lag = $+7.0\text{ s}$ (13 pairs) | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_lag_estimate_s` (48 rows) | Value frequency count across 48 recordings | Expected: 13 pairs at $+7\text{ s}$<br>Recomputed: 13 pairs at $+7\text{ s}$ | 0 pairs | `CSV_ONLY` | **VERIFIED** |
| **CLM-04** | Monitor HR lags in $[+4\text{ s}, +10\text{ s}]$ = 40 pairs | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_lag_estimate_s` (48 rows) | Range count $4 \le \tau \le 10$ across 48 recordings | Expected: 40 pairs ($83.33\%$)<br>Recomputed: 40 pairs ($83.33\%$) | 0 pairs | `CSV_ONLY` | **VERIFIED** |
| **CLM-05** | Monitor HR lags $< +4\text{ s}$ = 8 pairs | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_lag_estimate_s` (48 rows) | Count of $\tau < 4$ across 48 recordings | Expected: 8 pairs<br>Recomputed: 8 pairs | 0 pairs | `CSV_ONLY` | **VERIFIED** |
| **CLM-06** | `VS05_Apnea` optimal lag = $-3\text{ s}$ | `outputs/phase2a/sync_validation_results.csv` | Row 8 (`VS05`, `Apnea`) | Cell lookup | Expected: $-3\text{ s}$, `NEAR_ZERO_LATENCY`<br>Recomputed: $-3\text{ s}$, `NEAR_ZERO_LATENCY` | $0\text{ s}$ | `CSV_ONLY` | **VERIFIED** |
| **CLM-07** | Surrogate correlation maximum $< 0.42$ | `outputs/phase2a/sync_validation_results.csv` | Column `surrogate_control_corr` (48 rows) | Maximum value across 48 recordings | Claimed: $< 0.42$<br>Recomputed: $0.8123$ (`VS24_Resting`) | $+0.3923$ (tol $\pm 0.0100$) | `CSV_ONLY` | **DISCREPANCY (CONTRADICTED)** |
| **CLM-08** | Surrogate correlation mean = $0.5077$ | `outputs/phase2a/sync_validation_results.csv` | Column `surrogate_control_corr` (48 rows) | Arithmetic mean across 48 recordings | Expected: $0.5077$<br>Recomputed: $0.5077$ | $0.0000$ (tol $\pm 0.0100$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-09** | Resting surrogate correlation mean = $0.6289$ | `outputs/phase2a/sync_validation_results.csv` | Column `surrogate_control_corr` (24 Resting) | Arithmetic mean across 24 Resting recordings | Expected: $0.6289$<br>Recomputed: $0.6289$ | $0.0000$ (tol $\pm 0.0100$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-10** | Apnea surrogate correlation mean = $0.3865$ | `outputs/phase2a/sync_validation_results.csv` | Column `surrogate_control_corr` (24 Apnea) | Arithmetic mean across 24 Apnea recordings | Expected: $0.3865$<br>Recomputed: $0.3865$ | $0.0000$ (tol $\pm 0.0100$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-11** | Negative polarity subjects = `VS02`, `VS19` | `outputs/phase2a/sync_validation_results.csv` | Column `respiratory_polarity` (24 Resting) | Rows with polarity = -1 | Claimed: `VS02`, `VS19`<br>Recomputed: `VS09` ($-1$), `VS20` ($-1$) | Subject mismatch | `CSV_ONLY` | **DISCREPANCY (CONTRADICTED)** |
| **CLM-12** | Resting respiratory correlation $> 0.85$ = 14 subjects | `outputs/phase2a/sync_validation_results.csv` | Column `respiratory_corr` (24 Resting) | Count $> 0.85$ | Claimed: 14 subjects<br>Recomputed: 6 subjects (`VS03,07,10,12,17,24`) | $-8$ subjects | `CSV_ONLY` | **DISCREPANCY (CONTRADICTED)** |
| **CLM-13** | Resting respiratory lag mean = $+0.81\text{ ms}$ | `outputs/phase2a/sync_validation_results.csv` | Column `respiratory_lag_ms` (24 Resting) | Arithmetic mean across 24 Resting recordings | Expected: $+0.8125\text{ ms}$<br>Recomputed: $+0.8125\text{ ms}$ | $0.0000\text{ ms}$ (tol $\pm 0.0100\text{ ms}$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-14** | Across-subject aggregate 95% CI of mean respiratory lag ($6.99\text{ ms} < 1.0\text{ s}$) (CSV_ONLY; NOT a per-recording lag CI and does NOT satisfy the respiratory evidence gate) | `outputs/phase2a/sync_validation_results.csv` | Column `respiratory_lag_ms` (24 Resting) | $1.96 \times (\text{std}/\sqrt{24})$ across 24 subjects | Expected: Width $6.99\text{ ms} < 1000\text{ ms}$<br>Recomputed: $6.99\text{ ms}$ | $0.00\text{ ms}$ | `CSV_ONLY` | **VERIFIED** |
| **CLM-15** | Resting cardiac zero-shift MAE mean = $2.94\text{ bpm}$ | `outputs/phase2a/sync_validation_results.csv` | Column `radar_ecg_window_mae_zero` (24 Resting) | Arithmetic mean across 24 Resting recordings | Claimed: $2.94\text{ bpm}$<br>Recomputed: $2.9652\text{ bpm}$ | $+0.0252\text{ bpm}$ (tol $\pm 0.0100\text{ bpm}$) | `CSV_ONLY` | **DISCREPANCY** |
| **CLM-16** | Resting cardiac zero-shift MAE $< 5.0\text{ bpm}$ = 21 pairs | `outputs/phase2a/sync_validation_results.csv` | Column `radar_ecg_window_mae_zero` (24 Resting) | Count $< 5.0\text{ bpm}$ across 24 Resting recordings | Expected: 21 pairs ($87.5\%$)<br>Recomputed: 21 pairs ($87.5\%$) | 0 pairs | `CSV_ONLY` | **VERIFIED** |
| **CLM-17** | Resting cardiac best-shift MAE mean = $2.47\text{ bpm}$ | `outputs/phase2a/sync_validation_results.csv` | Column `radar_ecg_best_shift_mae` (24 Resting) | Arithmetic mean across 24 Resting recordings | Expected: $2.4702\text{ bpm}$<br>Recomputed: $2.4702\text{ bpm}$ | $0.0000\text{ bpm}$ (tol $\pm 0.0100\text{ bpm}$) | `CSV_ONLY` | **VERIFIED** |
| **CLM-18** | Apnea cardiac zero-shift MAE mean = $3.80\text{ bpm}$ | `outputs/phase2a/sync_validation_results.csv` | Column `radar_ecg_window_mae_zero` (24 Apnea) | Arithmetic mean across 24 Apnea recordings | Claimed: $3.82\text{ bpm}$<br>Recomputed: $3.7961\text{ bpm}$ | $-0.0239\text{ bpm}$ (tol $\pm 0.0100\text{ bpm}$) | `CSV_ONLY` | **DISCREPANCY** |
| **CLM-19** | ECG Lead II periodic NaN counts (47 files with 119–120 NaNs) | `data/VITALSENSE_120_DATASET/*/*_Mindray.mat` | Variable `ecg_lead2` across all 48 files | Direct NumPy inspection `np.isnan().sum()` | Expected: 36 @ 120, 11 @ 119, 1 @ 0<br>Recomputed: 36 @ 120, 11 @ 119, 1 @ 0 | 0 files | `RAW_RECOMPUTED` | **VERIFIED (DISCREPANCY RESOLVED)** |
| **CLM-20** | `VS24_Resting` respiration length = 30,600 samples | `data/VITALSENSE_120_DATASET/VS24/VS24_Resting_Mindray.mat` | Variable `respiration` | Direct SciPy MAT inspection `len(respiration)` | Expected: 30,600 samples<br>Recomputed: 30,600 samples | 0 samples | `RAW_RECOMPUTED` | **VERIFIED** |
| **CLM-21** | `TechValidation.m` presence = 0 files | Local workspace filesystem | Entire repository / workspace | Recursive filesystem search | Expected: 0 files found<br>Recomputed: 0 files found | 0 files | `FILESYSTEM_SEARCH` | **VERIFIED (STATUS: NOT_AVAILABLE)** |
| **CLM-22** | Minimum achievable empirical p-value for $N=5$ | Mathematical formulation / `step2_sync_validation_report.md` | Statistical claim in report | Exact formula $p = (1 + \text{count}) / (N + 1)$ | Claimed: $p < 0.001$<br>Recomputed: $p_{\min} = 1/6 \approx 0.1667$ | Mathematically impossible; requires $N \ge 1000$ for strict $p < 0.001$ | `REPORT_ONLY` | **DISCREPANCY (CONTRADICTED)** |
| **CLM-23** | Zero-shift monitor MAE = $2.51\text{ bpm}$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_mae_zero` (48 rows) | Arithmetic mean across 48 recordings | Claimed: $2.51\text{ bpm}$<br>Recomputed: $2.5586\text{ bpm}$ | $+0.0486\text{ bpm}$ (tol $\pm 0.0100\text{ bpm}$) | `CSV_ONLY` | **DISCREPANCY** |
| **CLM-24** | Best-shift monitor MAE = $1.82\text{ bpm}$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_mae_best` (48 rows) | Arithmetic mean across 48 recordings | Claimed: $1.82\text{ bpm}$<br>Recomputed: $1.9029\text{ bpm}$ | $+0.0829\text{ bpm}$ (tol $\pm 0.0100\text{ bpm}$) | `CSV_ONLY` | **DISCREPANCY** |
| **CLM-25** | Best-shift monitor correlation = $0.69$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_corr_best` (48 rows) | Arithmetic mean across 48 recordings | Claimed: $0.69$<br>Recomputed: $0.6504$ | $-0.0396$ (tol $\pm 0.0100$) | `CSV_ONLY` | **DISCREPANCY (CONTRADICTED)** |
| **CLM-26** | Zero-shift monitor correlation = $0.26$ | `outputs/phase2a/sync_validation_results.csv` | Column `monitor_hr_corr_zero` (48 rows) | Arithmetic mean across 48 recordings | Expected: $0.26$<br>Recomputed: $0.2579$ | $-0.0021$ (tol $\pm 0.0100$) | `CSV_ONLY` | **VERIFIED** |

#### Reconciliation Summary by Verification Type and Audit Result:
- **By Verification Type (26 claims total):**
  - `CSV_ONLY`: **22 claims** ($84.6\%$; CLM-01 to CLM-18, CLM-23 to CLM-26; 4 candidate pairs `VS01_Resting`, `VS24_Resting`, `VS09_Resting`, `VS02_Apnea` independently confirmed on raw MAT arrays via `SAME_ALGORITHM_REPRODUCED`).
  - `RAW_RECOMPUTED`: **2 claims** ($7.7\%$; CLM-19 and CLM-20, audited across raw arrays).
  - `FILESYSTEM_SEARCH`: **1 claim** ($3.8\%$; CLM-21, filesystem search confirming absence of `TechValidation.m`).
  - `REPORT_ONLY`: **1 claim** ($3.8\%$; CLM-22, mathematical derivation of empirical p-value bound).
  - `SAME_ALGORITHM_REPRODUCED`: **0 aggregate claims exclusively** (4 individual pairs independently reproduced).
  - `UNVERIFIED`: **0 claims** ($0.0\%$).
  - **Total:** **26 claims** ($100.0\%$).
- **By Audit Result (26 claims total):**
  - **`VERIFIED`:** **17 claims** ($65.4\%$).
  - **`DISCREPANCY (CONTRADICTED / EXCEEDING TOLERANCE)`:** **9 claims** ($34.6\%$).
  - **`UNVERIFIED`:** **0 claims** ($0.0\%$).
  - **Total:** **26 claims** ($100.0\%$).

#### Reconciling the UNVERIFIED Count and Historical Scope Boundaries:
The accounting above yields `UNVERIFIED: 0` strictly within the defined set of 26 empirical numerical claims itemized in the table. This must not be misconstrued as validating historical claims made in Phase 1 or Step 2 reports:
1. **Historical `TechValidation.m` Claims:** All claims in prior documentation asserting that `TechValidation.m` executed or established microsecond synchronization or algorithm validity are **outside the 26-claim table** and remain formally designated **`UNVERIFIED`** (Section 21.2).
2. **CLM-21 Scope:** CLM-21 audits specifically the fact that `TechValidation.m` is absent from the workspace. Confirming this absence via `FILESYSTEM_SEARCH` is awarded `VERIFIED (STATUS: NOT_AVAILABLE)`. This verification of its physical absence reinforces—rather than resolves—the `UNVERIFIED` status of all historical claims that relied upon it.

#### Complete Register of All Nine Numerical Discrepancies:

| Discrepancy ID | Claim ID | Metric / Description | Original Reported Value | Reproduced Value | Tolerance | Difference | Verification Type | Disposition & Status |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **DISC-01** | **CLM-07** | Maximum surrogate respiratory correlation | $< 0.42$ | $0.8123$ (`VS24_Resting`) | $\pm 0.0100$ | $+0.3923$ | `CSV_ONLY` | **CONTRADICTED**: Prior report understated surrogate correlation. Unresolved blocker for respiratory evidence gate. |
| **DISC-02** | **CLM-11** | Negative-polarity Resting subjects | `VS02`, `VS19` | `VS09` ($-1$), `VS20` ($-1$) | Exact IDs | Subject mismatch | `CSV_ONLY` | **CONTRADICTED**: Report transcription error (`VS02` and `VS19` are $+1$). Corrected in report narrative and issue register. |
| **DISC-03** | **CLM-12** | Resting correlation $> 0.85$ subject count | 14 subjects | 6 subjects (`VS03,07,10,12,17,24`) | Exact count | $-8$ subjects | `CSV_ONLY` | **CONTRADICTED**: Report typographical overstatement (16 exceed 0.70). Corrected in report narrative and issue register. |
| **DISC-04** | **CLM-15** | Resting cardiac zero-shift MAE mean | $2.94\text{ bpm}$ | $2.9652\text{ bpm}$ | $\pm 0.0100\text{ bpm}$ | $+0.0252\text{ bpm}$ | `CSV_ONLY` | **EXCEEDS TOLERANCE**: Discrepancy from reporting average error. Recomputed value ($2.97\text{ bpm}$) preserved. |
| **DISC-05** | **CLM-18** | Apnea cardiac zero-shift MAE mean | $3.82\text{ bpm}$ | $3.7961\text{ bpm}$ | $\pm 0.0100\text{ bpm}$ | $-0.0239\text{ bpm}$ | `CSV_ONLY` | **EXCEEDS TOLERANCE**: Discrepancy from reporting average error. Recomputed value ($3.80\text{ bpm}$) preserved. |
| **DISC-06** | **CLM-22** | Minimum achievable empirical p-value ($N=5$) | $p < 0.001$ | $p_{\min} \approx 0.1667$ | Exact formula | Impossible | `REPORT_ONLY` | **CONTRADICTED**: Mathematically impossible with $N=5$; requires $N \ge 1000$ for strict $p < 0.001$. Unresolved blocker. |
| **DISC-07** | **CLM-23** | Zero-shift monitor MAE mean | $2.51\text{ bpm}$ | $2.5586\text{ bpm}$ | $\pm 0.0100\text{ bpm}$ | $+0.0486\text{ bpm}$ | `CSV_ONLY` | **EXCEEDS TOLERANCE**: Discrepancy from reporting average error. Recomputed value ($2.56\text{ bpm}$) preserved. |
| **DISC-08** | **CLM-24** | Best-shift monitor MAE mean | $1.82\text{ bpm}$ | $1.9029\text{ bpm}$ | $\pm 0.0100\text{ bpm}$ | $+0.0829\text{ bpm}$ | `CSV_ONLY` | **EXCEEDS TOLERANCE**: Discrepancy from reporting average error. Recomputed value ($1.90\text{ bpm}$) preserved. |
| **DISC-09** | **CLM-25** | Best-shift monitor correlation mean | $0.69$ | $0.6504$ | $\pm 0.0100$ | $-0.0396$ | `CSV_ONLY` | **CONTRADICTED**: Overstated correlation. Recomputed value ($0.65$) preserved. |

---

### 21.10 Issue Register CSV Structural Validation & Repair Report

#### Actual Dual-Parser Validation Output:
Executed directly against `outputs/phase2a/step2b_issue_register.csv`:
```text
=== Strict csv.reader Validation ===
Total Rows (including header): 23
Header Columns: 7
Row Widths Set: {7}
Column Shift Check: PASS (0 shifted rows)

=== pandas.read_csv Validation ===
Dataframe Shape: (22, 7)
Unique issue_id Count: 22
Missing / Null Values: 0
Status Distribution:
  DOCUMENTED:   9
  OPEN:         9
  CONFIRMED:    2
  RESOLVED:     2

=== Unresolved Code/Design Defect Status Check ===
ISS-07 (Runner latency classification heuristic):     OPEN
ISS-08 (Lenient 5-beat R-peak QC rule):               OPEN
ISS-09 (FFT 6.0 bpm bin quantization):                OPEN
ISS-10 (Trial-shift optimization overfitting):        OPEN
ISS-12 (VS24 formatting divergence tail-trunc):        OPEN
ISS-15 (Surrogate test threshold loosening):          OPEN
ISS-17 (Surrogate control N=5 underpowering):         OPEN
ISS-21 (Isolated NaN interpolation guard):            OPEN
ISS-22 (VS24 respiration tail truncation assumption):    OPEN

=== Field Alignment Check for Quoted Issues ===
ISS-08: Status = OPEN | Recommended Action: "Implement multi-parameter Signal Quality Index (SQI) evaluating beat coverage (> 85%), maximum gap (< 3s), and amplitude stability in a future approved step."
ISS-10: Status = OPEN | Recommended Action: "Use prespecified zero-shift baseline without best-shift optimization (2.97 bpm Resting MAE) for window-level evaluation, noting it remains subject to ECG-label limits."
ISS-12: Status = OPEN | Scientific Risk: "Potential array mismatch if full 120s (30,720 samples) is assumed without checking sample counts; cause of formatting difference is NOT_VERIFIABLE."
```

*Note (2026-10-18): Reconciled to current register state (22 issues: 9 DOCUMENTED, 9 OPEN, 2 CONFIRMED, 2 RESOLVED). The previous Section 21.10 text recorded DOCUMENTED: 9 / CONFIRMED: 3 due to a historical transcription error against the baseline 20-row register (which had 10 DOCUMENTED, 6 OPEN, 2 CONFIRMED, 2 RESOLVED, as recorded in Section 21.12); the register was subsequently expanded in Stage 2F/2R with ISS-21/ISS-22 (OPEN) and ISS-12 reopened.*

#### Complete Issue Register Table (`outputs/phase2a/step2b_issue_register.csv`):

| Issue ID | Severity | Status | File or Function | Description Summary |
| :---: | :---: | :---: | :--- | :--- |
| **ISS-01** | Critical | **CONFIRMED** | `src/sync_validation/ecg_processor.py:scan_monitor_hr_lag` | Monitor HR array exhibits systematic +6s to +7s latency relative to ECG instantaneous HR. |
| **ISS-02** | High | **CONFIRMED** | `outputs/phase2a/sync_validation_results.csv` | Lack of hardware clock, PPS pulse, or common digitizer timestamps across MAT files. |
| **ISS-03** | High | **DOCUMENTED** | `outputs/phase2a/step2_sync_validation_report.md` | Report claimed surrogate correlation never exceeded 0.42; CSV shows values reach 0.8123. |
| **ISS-04** | Medium | **DOCUMENTED** | `outputs/phase2a/step2_sync_validation_report.md` | Report claimed surrogate p < 0.001; mathematically refuted; corrected to N >= 1000 in narrative. |
| **ISS-05** | Medium | **DOCUMENTED** | `outputs/phase2a/step2_sync_validation_report.md` | Negative polarity subjects misidentified as VS02/VS19; corrected to VS09/VS20 in narrative. |
| **ISS-06** | Low | **DOCUMENTED** | `outputs/phase2a/step2_sync_validation_report.md` | Correlation > 0.85 count claimed 14; corrected to exact 6 subjects in narrative. |
| **ISS-07** | High | **OPEN** | `src/sync_validation/runner.py:lines 98-110` | Lumping lags < 4s into NEAR_ZERO_LATENCY and contradictory reason string logic. |
| **ISS-08** | High | **OPEN** | `src/sync_validation/ecg_processor.py:detect_r_peaks` | QC rule requires only 5 valid beats in 120s to award PASS verdict. |
| **ISS-09** | Medium | **OPEN** | `src/sync_validation/cardiac_radar_validator.py` | 10s window yields 6.0 bpm discrete FFT bins with no parabolic peak interpolation. |
| **ISS-10** | Medium | **OPEN** | `src/sync_validation/cardiac_radar_validator.py` | Trial shift optimization in [-5, +5]s evaluated on same windows; fails out-of-sample. |
| **ISS-11** | Medium | **DOCUMENTED** | `src/sync_validation/respiratory_validator.py` | Apnea respiratory cross-correlation correlates baseline drift; marked INCONCLUSIVE. |
| **ISS-12** | Low | **OPEN** | `data/VITALSENSE_120_DATASET/VS24/VS24_Resting_Mindray.mat` | VS24 formatting divergence (0 NaNs, 30,600 samples); cause is NOT_VERIFIABLE. |
| **ISS-13** | High | **RESOLVED** | `data_quality_report.csv vs step2b_consistency_audit.md` | ECG NaN discrepancy resolved via forensic trace (Phase 1 checked HR; Step 2B checked ecg_lead2). |
| **ISS-14** | High | **DOCUMENTED** | `README.txt / Step 1 & 2 summaries` | TechValidation.m absent from workspace; marked NOT_AVAILABLE — EXCLUDED FROM SCOPE. |
| **ISS-15** | Medium | **OPEN** | `tests/test_sync_validation.py` | Unit test threshold loosened from r < 0.30 to r < 0.75; weakens test discriminative power. |
| **ISS-16** | High | **DOCUMENTED** | `outputs/phase2a/step2_sync_validation_report.md` | Headline claiming 10s window alignment adequate marked NOT YET SUPPORTED. |
| **ISS-17** | Medium | **OPEN** | `src/sync_validation/respiratory_validator.py` | Surrogate control N=5 underpowered; status held as CONSISTENT_NOT_PROVEN. |
| **ISS-18** | Medium | **DOCUMENTED** | `src/sync_validation/runner.py:lines 93, 101` | 5.0 bpm MAE, 50 ms lag, and 0.40 correlation thresholds not prespecified in any available document; provenance NOT_VERIFIABLE. |
| **ISS-19** | Low | **RESOLVED** | `outputs/phase2a/step2b_consistency_audit.md` | Prior unverified claims on interpolation distortion and VS24 causality qualified. |
| **ISS-20** | Low | **DOCUMENTED** | `outputs/phase2a/step2b_consistency_audit.md` | Differences exceeding 0.0100 bpm tolerance in Section 6.2 classified as DISCREPANCY. |
| **ISS-21** | Medium | **OPEN** | `src/sync_validation/ecg_processor.py:clean_ecg_isolated_nans` | Single-sample delimiter NaN interpolation guard (max_gap=1); multi-sample gaps un-interpolated. |
| **ISS-22** | Low | **OPEN** | `data/VITALSENSE_120_DATASET/VS24/VS24_Resting_Mindray.mat` | VS24 respiration tail-truncation assumption is NOT_VERIFIABLE; requires sensitivity analysis. |

---

### 21.11 Script Provenance & Source-Code Baseline Snapshot

#### Audit Script Provenance:
All temporary analysis scripts used during this audit were executed within sandboxed scratch directories and have been removed. Their provenance, purpose, and cryptographic SHA-256 hashes are recorded below for full scientific reproducibility:
1. **`update_issue_register.py`**
   - **SHA-256:** `e5c969a09fa5fd708254b148716f2e03e44102a8ee7679105f9f56d0321fc22e`
   - **Purpose:** Generated and repaired `outputs/phase2a/step2b_issue_register.csv`, formatted all 20 issues with proper quoting and status assignments, and performed automated dual-parser validation.
2. **`independent_recompute.py`**
   - **SHA-256:** `bfa39e6a978d780ea3b508ad964359d997235544cfb57a79f8c61fa25f9b4dd6`
   - **Purpose:** Recomputed 4 diverse candidate pairs (`VS01_Resting`, `VS24_Resting`, `VS09_Resting`, `VS02_Apnea`) directly from raw MAT files without importing runner functions.
3. **`diagnostic_split.py`**
   - **SHA-256:** `9dc21fa6c125dc2c1a82f347781b0a850ee8568c076239bc7a6cae7077a16e78`
   - **Purpose:** Diagnostic split testing comparing first-half lag selection against second-half out-of-sample evaluation across 6 Resting recordings.
4. **Direct Python Inspection Commands:**
   - Evaluated continuous `ecg_lead2` waveforms across all 48 Mindray files for NaNs, array shapes, and dtypes.
   - Performed recursive filesystem search confirming absence of `TechValidation.m`.
   - Verified `scipy.signal.resample_poly` output length on 30,600 samples resampled by $125/16$ equals $239,063$ (`ceil(n * up / down)`).

#### Source-Code and Test Baseline Cryptographic Snapshot:
Because no pre-audit cryptographic snapshot of `src/` and `tests/` exists, pre/post code integrity against prior states is formally **`NOT_VERIFIABLE`**. The cryptographic hashes below record the current state as a strict baseline for future comparison:

| File Path | SHA-256 Hash |
| :--- | :--- |
| `src/__init__.py` | `48858318919570f3f5eb2340d9b833fca2f7a7890b1997efb90317708fa7691f` |
| `src/phase1_audit/__init__.py` | `906b2c238aec6c35766a752c9ffd630f6e45854662d4fbd35314c223cdc46b34` |
| `src/phase1_audit/discover_files.py` | `9e8fefe99a8ccb85276b064ff124d16e6c22ef96a625f69c3d01668752e65432` |
| `src/phase1_audit/identify_fields.py` | `c993ff6e88bf5bbef94b77dab6e066632b4406b6ebe436315dce6d316693ce70` |
| `src/phase1_audit/inspect_mat.py` | `656c42f905e0e49fcf24644bf9a57d1fc97b611a449955381a8b5e920596430a` |
| `src/phase1_audit/inspect_timing.py` | `44050837b7ebcf723c86e92d1d24a82bcf3bc92d0c85306a2688231f6ce1c3fd` |
| `src/phase1_audit/match_recordings.py` | `59f9a1b2949aa17ca23f31b5412a306f328bdd5bea82a9d31d409ff27e9c9335` |
| `src/phase1_audit/run_audit.py` | `fcf4688b6b4b08b26ff6a5e21f1d89aaf3fc51880e8c2763c527c95223db9a6b` |
| `src/phase1_audit/subject_inventory.py` | `acfb2a79e6454e0054b996ed87ddefa32e764e35c0a980143d3405986e517318` |
| `src/phase1_audit/validate_data.py` | `643e337d162422a018b2df1ff5d7e55fe471fd09613f70490d1abb531e85efd6` |
| `src/sync_validation/__init__.py` | `b6d80880c0a695828be747134207fb4a51227576b9e007a2aec66f6bcc21a97c` |
| `src/sync_validation/cardiac_radar_validator.py` | `5140e7f3d6c1bd00e795fa41b7e356d0ba0f0dd61575a91bedd0f46c60ea2848` |
| `src/sync_validation/ecg_processor.py` | `e06d415097ef9d7188c90989c8b3d09f12373527690ea0590e028eb4d358ccc2` |
| `src/sync_validation/respiratory_validator.py` | `4a329de44d9d116ddf3de9ffba9714ebff9639b1ebf9e31b17d4180528c392dd` |
| `src/sync_validation/runner.py` | `95b04e7a1c55b4feb96dd887fd11830bba4b3a944a2e3cb42202fd83bdf41969` |
| `tests/conftest.py` | `397bf28051e8072cd8afbd69b801718cbeb9a1aa3c686b91ca607d36ba2c6e89` |
| `tests/test_candidate_fields.py` | `84eb027ebb6931b2765cb5dd22bab2c85e26404e8dc414cb68ce2fdf3d77b59a` |
| `tests/test_file_discovery.py` | `42538159a07d8ee2c35e92c45dd2ff7ef0cbce83028c2fdcceae900451536e39` |
| `tests/test_mat_inspection.py` | `c151b5060ae10a63d85208d69f32c27f93a2680ac23dffff54f41a7becd088fe` |
| `tests/test_matching.py` | `fed5484fce6ed3509917c8adf895ee17fb4912e4e7f78ab41272c4fcb8d7af1d` |
| `tests/test_same_file_pairing.py` | `5ced19320aa586bd82b03255e5a42d5c97a13f881d1d75319e9a1c9ecb217044` |
| `tests/test_signal_quality.py` | `9b469c39c4f052983bf760c8be0d025aca22fe894bd09a127b9fb5d13db03111` |
| `tests/test_sync_validation.py` | `5dd4cc86503a9dcf45d60da21e36392251508bccb4fcfa251465186359e46377` |
| `tests/test_timing_validation.py` | `a0a141ed5d3f6388c7a81ce593cd92d0ef7fbfc1200575f154c3f8dc14a6e87d` |

---

### 21.12 Finalization Gate Checklist & Source Immutability Confirmation

| Finalization Criteria | Verification Status | Evidence / Notes |
| :--- | :---: | :--- |
| **All 20 Report Sections Checked & Preserved** | **VERIFIED** | Sections 1 through 20 fully preserved with internal cross-references updated. |
| **Reconciliation Addendum Complete** | **VERIFIED** | Section 21 fully populated with forensic audit traces, claim accounting, and discrepancy table. |
| **Issue Register Structure Repaired & Validated** | **VERIFIED** | Exactly 22 issues $\times$ 7 columns; verified by strict `csv.reader` and `pandas` (9 DOCUMENTED, 9 OPEN, 2 CONFIRMED, 2 RESOLVED) — updated 2026-10-18 following Stage 2F/2R additions. |
| **Numerical Claims Reconciled** | **VERIFIED** | 26 material claims evaluated: 17 verified, 9 discrepancies documented, 0 unverified in empirical table (historical TechValidation.m claims remain UNVERIFIED). |
| **Test Integrity & Threshold History Documented** | **VERIFIED** | Assertion changes in `test_sync_validation.py` documented; all 149 test suite tests pass (including 13 in `test_stage2g_gaps.py`). |
| **Operational Decision Boundaries Preserved** | **VERIFIED** | Preprocessing = `CONDITIONAL GO (in-memory working copies only)`; Supervised-label generation = `NOT YET APPROVED`; Hardware clock synchronization = `UNVERIFIED`; Respiratory alignment = `CONSISTENT_NOT_PROVEN (Resting) / INCONCLUSIVE (Apnea)`; 10-second window adequacy = `NOT YET SUPPORTED`. |
| **Status Dimensions Decoupled** | **VERIFIED** | Hardware Clock = `UNVERIFIED`; Respiratory Alignment = `CONSISTENT_NOT_PROVEN`. |
| **Headline Status Resolved** | **VERIFIED** | 10s window headline marked `NOT YET SUPPORTED`; replaced with evidence-matched text. |
| **Raw MAT Files Immutability** | **VERIFIED_MATCHED_PRE_AUDIT_SNAPSHOT** | All 48 radar MAT files and 48 Mindray MAT files match pre-audit SHA-256 and modification time snapshot in `file_inventory.csv`. |
| **Source Code & Test Immutability** | **NOT_VERIFIABLE** | Pre/post comparison of `src/` and `tests/` against pre-audit state is formally not verifiable due to absence of a pre-audit cryptographic snapshot. Current baseline snapshot recorded in Section 21.11; zero files modified during this review. |
| **Scratch Space Sanitized** | **VERIFIED** | Scratch directory verified empty; script hashes and purposes archived in report. |

---

`PHASE 2A — STEP 2B FINALIZATION GATE: OPEN — RECONCILIATION PARTIAL; BLOCKERS REMAIN PENDING PRE-SPECIFIED SQI & ADEQUACY GATES`



---

## 22. Stage 5 Closure Package Addendum & Status Re-Audit (2026-10-19)

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
- Statistical evaluation in Stage 2K (K3) established that the correlation between the DC product metric ($r_{\text{dc}}$) and discrete lag shift is statistically non-significant ($\rho = -0.1254, p = 0.3956$).
- The true underlying phenomenon is that the cross-correlation function sits on an extended, flat plateau spanning a median width of **95.0 ms** (range **34.5 ms to 1,594.0 ms** for $r \ge r_{\text{peak}} - 0.001$).
- Discrete lag alignment at 0.0 ms is an artifact of searching on a discrete 0.5 ms grid over this broad plateau and does **not** demonstrate physical sub-sample hardware clock synchronization. Hardware timing remains strictly **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**.

### 23.3 Comprehensive Status Table for Section 18.x Preprocessing Requirements
The following table documents the current implementation and wiring status of each preprocessing requirement specified in Section 18:

| Requirement Section | Specification Description | Current Status | Pipeline / Source File & Line | Unit Test Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Section 18.1** | Intact Signal Integrity across all 48 radar (40,000 samples @ 333.33 Hz) and 48 Mindray (60,000 samples @ 500 Hz) signals | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/phase1_audit/inspect_mat.py:42`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase1_audit/inspect_mat.py#L42); all 96 `.mat` files verified unmodified | `tests/test_mat_inspection.py` |
| **Section 18.2** | In-Memory Working Copies: all operations execute on `np.array(..., copy=True)` working arrays; raw disk files untouched | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/runner.py:112-140`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L112-L140); [`src/sync_validation/ecg_processor.py:22`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L22); [`src/sync_validation/respiratory_validator.py:25-26`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L25-L26) | `tests/test_stage2_closure.py` |
| **Section 18.3** | Dynamic Array Lengths: safe in-memory truncation to common minimum length; no hardcoded 30,720 sample counts | **`TEST_ONLY`** (standalone function) / **`WIRED`** (pipeline equivalent) | Standalone: [`src/sync_validation/respiratory_validator.py:65-94`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L65-L94); Pipeline: [`src/sync_validation/respiratory_validator.py:51-52`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L51-L52) (`resample_signals_to_2000hz`) | `tests/test_stage2_closure.py:test_truncate_respiration_dynamic_length` |
| **Section 18.4** | Single-Sample NaN Interpolation: linear interpolation restricted to isolated single NaNs; multi-sample gaps flagged and un-interpolated | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/ecg_processor.py:46-86`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L46-L86) (`clean_ecg_isolated_nans`), wired into `clean_ecg_nans` at line 98, called at [`src/sync_validation/runner.py:125`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L125) | `tests/test_stage2_closure.py:test_clean_ecg_nans_isolated_only` |
| **Section 18.5a** | 4x Zero-Padding: evaluating DTFT on denser frequency grid ($N_{\text{fft}} = 4 \times N_{\text{win}}$) for spectral interpolation | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/cardiac_radar_validator.py:69-110`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L69-L110) (`estimate_window_hr_multi_estimator`), wired into `compute_window_level_hr_agreement` at line 170 | `tests/test_stage2_closure.py:test_estimate_window_hr_multi_estimator` |
| **Section 18.5b** | 3-Point Parabolic Peak Interpolation: continuous parabolic peak interpolation resolving discrete bin discretization | **`IMPLEMENTED_AND_TESTED`** / **`WIRED`** | [`src/sync_validation/cardiac_radar_validator.py:33-66`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L33-L66) (`estimate_peak_frequency_parabolic`), wired into `compute_window_level_hr_agreement` at line 170 | `tests/test_stage2_closure.py:test_estimate_peak_frequency_parabolic` |
