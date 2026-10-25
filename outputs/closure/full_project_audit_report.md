# FULL PROJECT AUDIT REPORT — KAN RADAR HEART-RATE ESTIMATION

**Project:** *A Subject-Independent Kolmogorov-Arnold Network (KAN)-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals*  
**Repository Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Audit Date:** October 2026  
**Auditor Roles:** Senior Biomedical Signal-Processing Researcher, KAN Specialist, Python Software Architect, QA & MLOps Engineer, Scientific Reproducibility Auditor  
**Report Output Path:** [`outputs/closure/full_project_audit_report.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/full_project_audit_report.md)  
**Associated Traceability Matrix:** [`outputs/closure/project_plan_traceability_matrix.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/project_plan_traceability_matrix.csv)  

---

## 1. Executive Summary & Audit Mandate

This report delivers an exhaustive, independent scientific and software engineering audit of the KAN radar heart-rate estimation framework. The repository has been evaluated across 8 primary technical domains (B1 through B8), the full regression suite has been executed on live runtime environments, immutable baselines have been cryptographically re-verified, and software defects have been systematically classified and tracked.

### Core Governance Determination:
- **Scientific Gate Status:** Strictly **`OPEN`** (`RECONCILIATION PARTIAL; ADDENDUM REQUIRED BEFORE FINALIZATION`).
- **Phase 2C Real-Data Ground-Truth Generation (`run_002`):** Strictly **`BLOCKED`**.
- **Real-Data Model Training (`run_real_001`):** Strictly **`BLOCKED`**.
- **Preflight Check Status:** **`NO-GO`** (Exit Code 1 via [`src/closure/phase2c_preflight.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/closure/phase2c_preflight.py)).

---

## 2. Technical Domain Audits (B1 – B8)

### B1. Dataset Integrity & Structural Validation
1. **Source File Inventory:**
   - Evaluated directly inside [`data/VITALSENSE_120_DATASET`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/data/VITALSENSE_120_DATASET).
   - Confirmed exactly **96 MATLAB `.mat` files**: exactly **48 radar recordings** (`<Subject>_<Condition>.mat`) and exactly **48 Mindray reference ECG recordings** (`<Subject>_<Condition>_Mindray.mat`).
   - All 24 subjects (`VS01` through `VS24`) are present. Every subject has exactly two recordings: `Apnea` and `Resting`. Zero unpaired files detected.
2. **Sampling Frequencies & Metadata Provenance:**
   - Radar: In all 48 radar files, `T_frame = 0.003 s` is embedded in the MAT structure, yielding an exact sampling rate of:
     $$f_{s,\text{radar}} = \frac{1}{0.003\text{ s}} = 333.333333...\text{ Hz}$$
   - ECG Reference: In all 48 reference files, `Fs_ecg = 500.0` is explicitly recorded in the MAT structure ($f_{s,\text{ecg}} = 500.0\text{ Hz}$).
3. **Signal Dimensions & Duration:**
   - Radar `VitalSig`: Exactly **40,000 samples** per recording in 100% of the 48 files.
     $$\text{Duration}_{\text{radar}} = \frac{40,000\text{ samples}}{333.333333\text{ Hz}} = 120.000\text{ seconds}$$
   - ECG `ecg_lead2`: Exactly **60,000 samples** per recording in 100% of the 48 files.
     $$\text{Duration}_{\text{ecg}} = \frac{60,000\text{ samples}}{500.000\text{ Hz}} = 120.000\text{ seconds}$$
   - Both streams possess identical nominal temporal duration ($120.0\text{ s}$).

### B2. ECG Reference Signal Processing
1. **Lead Selection:** Lead-II (`ecg_lead2`) is utilized across all recordings in compliance with standard clinical vectorcardiography.
2. **Delimiter NaN Handling:**
   - 47 of 48 reference files contain delimiter NaNs (exactly 119 or 120 NaNs per file, spaced exactly 500 samples / 1.0 second apart, corresponding to Mindray packet boundaries). `VS24_Resting` contains 0 NaNs.
   - Cleaned using [`clean_ecg_nans`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L42) with `only_isolated=True, fill_boundary=True`. Boundary fill ensures that delimiter NaNs at index 0 or index -1 are linearly interpolated from nearest valid neighbors without propagation.
3. **R-Peak Detection & Refinement:**
   - Evaluated using bandpass filtering ($0.5\text{--}40.0\text{ Hz}$, order 3 Butterworth) and local dynamic thresholding.
   - Peak refinement uses absolute maximum refinement `np.argmax(np.abs(ecg_filt))` within a $[-50\text{ ms}, +50\text{ ms}]$ local window. This correctly resolves upright R-peaks as well as negative Q-wave dominant polarities (e.g., `VS09` and `VS20`).
4. **Physiological RR Bounds & Quality Control:**
   - Enforces $35.0\text{ BPM} \le \text{HR} \le 185.0\text{ BPM}$ ($0.3243\text{ s} \le \text{RR} \le 1.7143\text{ s}$).
   - Recording-level SQI requires $\ge 85.0\%$ cumulative valid RR coverage, $\max(\text{RR gap}) < 3.0\text{ s}$, and $\ge 20\text{ valid beats}$. All 48 recordings in the cohort pass recording-level SQI ($100\%$ pass rate).

### B3. Synchronization and Scientific Validity
1. **Physical Hardware Reality:**
   - The radar hardware and Mindray patient monitor were acquired on independent clocks without a shared hardware trigger channel or common clock generator.
   - The dataset provides no hardware timestamp channel recording physical sample arrival.
2. **Governance Status:**
   - Software alignment assumes nominal $T_0 = 0.0\text{ s}$ alignment.
   - It is strictly forbidden to claim that software correlation analyses prove physical microsecond hardware timing. All documentation and APIs permanently bind this limitation to the code:
     `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.
3. **Monitor Latency Discrepancy:**
   - Physiological delay and monitor display smoothing latency ($\tau \approx 4\text{ s}$) documented in MATLAB script `TechValidation.m` reflect monitor display lag, not ground-truth Lead-II R-peak detection delay. The Lead-II ECG R-peaks represent immediate instantaneous cardiac depolarization.

### B4. Window Generation & Boundary Accounting
1. **Window Duration and Hop:**
   - Window duration: $T_{\text{win}} = 10.0\text{ s}$ ($3,333\text{ radar samples}$, $5,000\text{ ECG samples}$).
   - Hop duration: $T_{\text{hop}} = 5.0\text{ s}$ ($1,667\text{ nominal radar samples}$, $2,500\text{ ECG samples}$).
2. **Window Count Budget:**
   - Under the canonical label specification ([`outputs/closure/spec/label_spec_v1.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec/label_spec_v1.json)), sample boundaries are defined by:
     $$\text{start}(k) = \text{round}(k \times 5.0 \times f_s), \quad \text{end}(k) = \text{start}(k) + \text{round}(10.0 \times f_s)$$
   - At $k = 22$ (the 23rd window): $\text{start}(22) = \text{round}(110.0 \times 333.3333) = 36,667$; $\text{end}(22) = 36,667 + 3,333 = 40,000$ samples.
   - Exactly **23 candidate windows** are generated per 120-second recording without trailing truncation.
   - Cohort total: $48 \times 23 = \mathbf{1,104\text{ candidate windows}}$.
3. **Interactive Demo Boundary Note:**
   - In [`src/demo/simulation_engine.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/demo/simulation_engine.py), an incremental integer hop of $1,667\text{ samples}$ was used for real-time buffer simulation. Accumulated rounding ($22 \times 1,667 = 36,674$) yields $36,674 + 3,333 = 40,007 > 40,000$, causing the simulation buffer to process 22 windows and treat the remaining $1,660\text{ samples}$ ($4.98\text{ s}$) as trailing tail. This difference is formally recorded in the issue register (ISS-ENG-01).

### B5. Radar Signal Processing
1. **VitalSig Extraction & Filtering:**
   - `VitalSig` is filtered using a 3rd-order Butterworth bandpass filter ($0.8\text{--}3.0\text{ Hz}$, equivalent to $48\text{--}180\text{ BPM}$).
   - Implemented using SciPy `filtfilt` forward-backward zero-phase filtering. This avoids phase distortion and prevents group delay from corrupting peak timings.
2. **Leakage Prevention:**
   - In [`src/kan/normalization.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/normalization.py) and [`src/kan/feature_scaler.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/feature_scaler.py), normalizers are strictly fit on training subjects only.
   - Validation and test subjects are transformed using parameters $(\mu_{\text{train}}, \sigma_{\text{train}})$ learned exclusively from training subjects. Zero test-subject data leaks into scaling parameters.

### B6. KAN Implementation
1. **Architecture Formulation:**
   - Implemented in [`src/kan/kan_layer.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_layer.py) and [`src/kan/kan_model.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/kan_model.py) strictly following Liu et al. (2024):
     $$\phi_{j, i}(x_i) = w_{b, j, i} \cdot \text{SiLU}(x_i) + w_{s, j, i} \sum_{m} c_{j, i, m} B_{m, k}(x_i)$$
   - Uses Cox-de Boor B-spline recursion over a uniform grid with extended boundary knots.
   - Parameter capacity:
     - `ConvFeatureExtractor`: 3,360 trainable parameters.
     - `KANFeatureRegressor` (16 $\rightarrow$ 8 $\rightarrow$ 1): 1,360 trainable parameters.
     - `KANRegressor` Total: **4,720 trainable parameters**.
2. **Inference Latency & Determinism:**
   - Benchmarked on live CPU (Intel/AMD x86_64, Windows):
     - **KAN Regressor CPU Latency:** $\text{mean} = 66.08\text{ ms}$, $\text{median} = 65.88\text{ ms}$, $\text{std} = 1.41\text{ ms}$.
     - Well within real-time streaming constraints (hop duration is $5,000\text{ ms}$, inference consumes only $\sim 1.3\%$ of available window hop budget).

### B7. Baseline Fairness & Synthetic Benchmark Reconciliation
1. **Model Parameter Reconciliation:**
   - `ConvFeatureExtractor` backbone is 100% shared across all models (3,360 params).
   - Comparative Capacities:
     - Mean Baseline: 0 parameters.
     - CNN Regressor: 3,377 parameters (readout: 17 params).
     - MLP Regressor: 3,505 parameters (Dense 16 $\rightarrow$ 8 $\rightarrow$ 1: 145 params).
     - KAN Regressor: 4,720 parameters (KAN head: 1,360 params).
2. **Synthetic Benchmark Results:**
   - Evaluated across 8 synthetic subjects (80 test windows) under strict LOSO cross-validation.
   - Audited metrics from [`outputs/phase6b/baseline_comparison_summary.json`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase6b/baseline_comparison_summary.json):
     - **KAN:** $\text{MAE} = 2.592\text{ BPM}$, $\text{RMSE} = 4.144\text{ BPM}$, $\text{MedAE} = 1.105\text{ BPM}$, $\le \pm 10\text{ BPM} = 95.00\%$.
     - **CNN:** $\text{MAE} = 3.035\text{ BPM}$, $\text{RMSE} = 5.063\text{ BPM}$, $\text{MedAE} = 1.385\text{ BPM}$, $\le \pm 10\text{ BPM} = 90.00\%$.
     - **MLP:** $\text{MAE} = 3.365\text{ BPM}$, $\text{RMSE} = 4.606\text{ BPM}$, $\text{MedAE} = 2.255\text{ BPM}$, $\le \pm 10\text{ BPM} = 96.25\%$.
     - **Mean Baseline:** $\text{MAE} = 11.834\text{ BPM}$, $\text{RMSE} = 14.181\text{ BPM}$.

### B8. LOSO Evaluation Integrity
- Leave-One-Subject-Out strictly isolates all recordings of a given subject (both Apnea and Resting) into the test partition.
- Models are trained exclusively on the remaining $N-1$ subjects.
- Synthetic benchmark results are strictly segregated from real data. No real-data performance claims are made based on synthetic subjects.

---

## 3. Comprehensive Issue Register & Classification Matrix

Every issue discovered or tracked during the project is cataloged below with severity classification:
- **P0:** Critical data integrity, scientific validity, or authorization bypass blocker.
- **P1:** Major correctness, data leakage, or model loading issue.
- **P2:** Reliability, reproducibility, or maintainability issue.
- **P3:** Minor documentation, typing, or usability issue.

| Issue ID | Severity | Category | Description & Location | Root Cause | Fix / Resolution Status | Test Evidence | Remaining Risk | PI Approval Required? |
| :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **ISS-01** | **P0** | Governance | Scientific Gate is OPEN pending formal PI Sign-Off | Phase 2A audit finalized as RECONCILIATION PARTIAL | Staged in [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md) | [`test_closure_validators.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_closure_validators.py) | Real data label generation blocked | **YES (PI)** |
| **ISS-02** | **P0** | Governance | Ground-Truth Label Spec `approved_by` field is blank | Protocol requires formal PI sign-off | Validator enforces blank rejection; canonical hash `ae5c6780...` frozen | [`test_closure_validators.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_closure_validators.py) | Cannot generate `run_002` until signed | **YES (PI)** |
| **ISS-03** | **P1** | Signal | Mindray packet delimiter NaNs at 1-sec boundaries | Hardware streaming protocol writes isolated NaNs | Implemented [`clean_ecg_nans`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L42) with boundary fill | [`test_stage2g_gaps.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_stage2g_gaps.py) | None (100% resolved in code) | No |
| **ISS-04** | **P1** | Signal | Q-wave negative polarity in subjects `VS09` and `VS20` | Lead-II anatomical cardiac vector inversion | Implemented absolute peak refinement `np.argmax(np.abs(...))` | [`test_stage6_label_spec.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_stage6_label_spec.py) | None (100% resolved in code) | No |
| **ISS-05** | **P1** | Quality | Window ECG coverage reported up to 110.28% | Unclipped summation of midpoint-assigned straddling beats | Reconciled: clipped overlap is 100.0%; target HR is identical | [`test_coverage_audit.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_coverage_audit.py) | None (Mathematically proven) | No |
| **ISS-06** | **P1** | Safety | Pipeline runner default `output_dir` risk to Phase 2A | Default parameter could overwrite audited Phase 2A files | Implemented strict guard raising ValueError/PermissionError | [`test_d15_runner_guard.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_d15_runner_guard.py) | None (Decision D15 pending PI sign) | **YES (PI D15)** |
| **ISS-07** | **P2** | Modeling | Demo simulation engine fixed-hop windowing (22 vs 23) | Incremental `1667` hop sample rounding accumulated 7 samples | Documented in `DEMO_README.md` and traceability matrix | [`test_demo_simulation.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_demo_simulation.py) | None (Offline training uses 23 windows) | No |
| **ISS-08** | **P2** | Packaging | `requirements.txt` omitted core runtime dependencies | File originally only had 5 packages (omitted TensorFlow, Flask) | Updated `requirements.txt` to include `tensorflow`, `flask`, `matplotlib` | Live environment verification | None (Fully reproducible) | No |
| **ISS-09** | **P2** | Validation | Date parsing in sign-off validator lacked calendar checks | Basic regex could accept invalid dates (e.g., Feb 29 non-leap) | Implemented ISO 8601 `YYYY-MM-DD` parser with `datetime` calendar validation | [`test_closure_validators.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_closure_validators.py) | None (Rejects invalid dates) | No |
| **ISS-10** | **P3** | Cleanliness | Deprecation warning for escape sequence `\s` in docstring | Python 3.12+ invalid escape sequence in string literal | Converted docstring to raw docstring `r"""..."""` | Clean pytest output | None | No |

---

## 4. Test Suite Execution & Regression Audit

The full pytest test suite was executed across all 25 test modules:
```
Execution Command: python -m pytest tests/ -q
Result: 207 passed, 114 warnings in 91.88s (0:01:31)
Failures: 0
Errors: 0
Skipped: 0
Pass Rate: 100.0%
```
*(All 114 warnings are deprecation notices originating from TensorFlow 2.21 internal Keras NumPy copy keyword handling and do not affect project code).*

---

## 5. Audit Conclusions & Gate Verdict

1. **Software Engineering Production Readiness:** **VERIFIED FOR AUTHORIZED MODULES**.  
   - All dataset loading, windowing, filtering, B-spline KAN layers, baseline models, evaluators, and preflight validators are robust, fully tested, and numerically stable.
2. **Scientific Governance:** **FAIL-CLOSED / OPEN**.  
   - The Phase 2A/2C Scientific Gate remains **`OPEN`**.
   - Ground-truth label generation (`run_002`) and real-data training (`run_real_001`) remain strictly **`BLOCKED`**.
   - No human authorization has been fabricated; software enforces fail-closed behavior until the Principal Investigator reviews and signs [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md).
