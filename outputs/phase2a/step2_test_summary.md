# PHASE 2A — STEP 2 TEST SUITE SUMMARY REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 2A — Step 2: Synchronization Validation & Monitor Latency Investigation  
**Test Framework:** Pytest 9.1.1 (Python 3.10.11 on Windows)  
**Date of Execution:** October 2026  
**Test Suite Verdict:** **ALL 48 TESTS PASSED (100% PASS RATE, 0 FAILURES, 0 SKIPPED)**  
**Total Runtime:** 14.01 seconds  

---

## 1. Overall Test Results Summary

| Metric | Result |
| :--- | :--- |
| **Total Test Items Collected** | **48** |
| **Tests Passed** | **48 (100%)** |
| **Tests Failed** | **0** |
| **Tests Skipped** | **0** |
| **Execution Errors** | **0** |
| **Total Test Duration** | **14.01 s** |
| **Overall Status** | **PASSED** |

---

## 2. Test Module Breakdown

| Module | Purpose / Scope | Tests Run | Passed | Failed |
| :--- | :--- | :---: | :---: | :---: |
| [`tests/test_candidate_fields.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_candidate_fields.py) | Verification of radar signal and reference HR candidate field attributes | 3 | 3 | 0 |
| [`tests/test_file_discovery.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_file_discovery.py) | Verification of 24 subject folders, 96 MAT files, and directory structure | 8 | 8 | 0 |
| [`tests/test_mat_inspection.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_mat_inspection.py) | MAT variable type, shape, and structure verification | 5 | 5 | 0 |
| [`tests/test_matching.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_matching.py) | Pairing classification logic (ensures PROBABLE_MATCH for separate files) | 3 | 3 | 0 |
| [`tests/test_same_file_pairing.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_same_file_pairing.py) | Rejection of erroneous same-file assumptions | 1 | 1 | 0 |
| [`tests/test_signal_quality.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_signal_quality.py) | Signal integrity, finite checks, dynamic range, and dropout checks | 7 | 7 | 0 |
| [`tests/test_sync_validation.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_sync_validation.py) | **Phase 2A Step 2:** R-peak detection, monitor lag, xcorr, controls, polarity | 16 | 16 | 0 |
| [`tests/test_timing_validation.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_timing_validation.py) | Duration calculation and UNVERIFIED_TIMING classification rules | 5 | 5 | 0 |
| **Total** | **All 8 Test Suites** | **48** | **48** | **0** |

---

## 3. Detailed Specifications of Synchronization Validation Unit Tests

The 16 newly implemented automated tests in [`tests/test_sync_validation.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_sync_validation.py) evaluate the core mathematical, algorithmic, and synthetic control components:

### 3.1 ECG Preprocessing & R-Peak Detection Tests
1. **`test_clean_ecg_nans_isolated`:**  
   Verifies that periodic isolated single-sample NaNs (inserted by the Mindray digital stream once every ~501 samples) are detected, cataloged by index, and linearly interpolated on temporary in-memory copies without modifying the underlying raw array.
2. **`test_clean_ecg_nans_no_nans`:**  
   Verifies that completely clean arrays pass through without modification or index recording.
3. **`test_detect_r_peaks_synthetic`:**  
   Synthesizes an ECG signal with known QRS complex spikes at exact 1.0-second intervals ($60.0\text{ bpm}$) at $500\text{ Hz}$. Validates that the Pan-Tompkins style bandpass (5–15 Hz), derivative, squaring, moving integration (150 ms), and adaptive threshold detect all beats with mean heart rate $60.0 \pm 0.5\text{ bpm}$ and status `PASS`.
4. **`test_detect_r_peaks_insufficient_length`:**  
   Verifies that signals shorter than 2.0 seconds trigger status `INSUFFICIENT_LENGTH` and verdict `FAIL` without crashing.
5. **`test_derive_1hz_ecg_hr`:**  
   Validates continuous instantaneous heart rate derivation $60 / RR$ mapped onto the integer second grid $t \in [0, 9]\text{ s}$ via piecewise linear interpolation between beat timestamps.

### 3.2 Monitor HR Latency Scan & Convention Tests
6. **`test_scan_monitor_hr_lag_sign_convention`:**  
   Constructs a synthetic physiological step-change where ECG-derived HR jumps from 60 to 80 bpm at $t = 20\text{ s}$, and the monitor HR array reflects the same step delayed by $+6\text{ s}$ (at $t = 26\text{ s}$). Validates that the lag scan correctly recovers $\tau^* = +6\text{ s}$ with minimum $\text{MAE} = 0.0\text{ bpm}$, confirming the positive-lag sign convention ($\text{mon}[t] \approx \text{ecg}[t - \tau]$).
7. **`test_scan_monitor_hr_lag_ambiguous`:**  
   Supplies constant HR traces to verify that flat lag-agreement curves properly trigger the `is_ambiguous = True` uncertainty flag when MAE variation across shifts is $< 0.25\text{ bpm}$.

### 3.3 Respiratory Cross-Correlation & Resampling Tests
8. **`test_resample_signals_to_2000hz`:**  
   Validates in-memory rational polyphase resampling to $2000\text{ Hz}$ from $333.3333\text{ Hz}$ ($6:1$) and $256.0\text{ Hz}$ ($125:16$), verifying exact matching sample counts ($240,000$ samples for $120.0\text{ s}$).
9. **`test_resample_signals_truncated`:**  
   Tests handling of edge-case truncated respiration traces (e.g., `VS24_Resting_Mindray.mat` with 30,600 samples = $119.53\text{ s}$), verifying safe truncation to the common minimum length ($239,063$ samples) without array dimension mismatch.
10. **`test_compute_respiratory_xcorr_known_lag`:**  
    Injects a known $+10\text{ sample}$ ($+5.0\text{ ms}$) shift into a synthetic 0.25 Hz respiratory oscillation. Verifies that the cross-correlation algorithm recovers the exact $+5.0 \pm 0.5\text{ ms}$ lag with correlation $r > 0.95$ and polarity $+1$.
11. **`test_compute_respiratory_xcorr_polarity_inversion`:**  
    Inverts the radar signal (sign flip $-x(t)$) to simulate inverted displacement orientation. Verifies that the algorithm identifies $\text{polarity} = -1$ with negative correlation $r < -0.90$.
12. **`test_compute_respiratory_xcorr_low_variation`:**  
    Passes flat signals (simulating strict voluntary breath-hold apnea) and confirms proper identification of `INSUFFICIENT_VARIATION` without numerical exceptions.
13. **`test_compute_surrogate_respiratory_control`:**  
    Implements phase-randomized surrogate data generation (Theiler et al., 1992), verifying that destroying temporal phase alignment reduces cross-correlation significantly below the true signal level.

### 3.4 Cardiac Radar & Known-Offset Controls
14. **`test_extract_radar_cardiac_signal`:**  
    Verifies that zero-phase Butterworth bandpass filtering ($0.8 - 3.0\text{ Hz}$) preserves cardiac micro-motions while eliminating low-frequency respiratory swings.
15. **`test_synthetic_known_offset`:**  
    Synthesizes a multi-component cardio-respiratory oscillatory waveform, shifts by a known offset of $+60\text{ ms}$, and verifies that cross-correlation recovers the known offset with error $< 1\text{ sample}$ ($< 3.0\text{ ms}$).
16. **`test_window_level_hr_agreement_synthetic`:**  
    Constructs a time-varying synthetic heart-rate signal (60 bpm transitioning to 90 bpm) and evaluates sliding 10-second windows with 5-second hop against synthetic R-peaks. Verifies that zero-shift window-level MAE $< 5.0\text{ bpm}$ and best shift is identified at $0.0 \pm 1.0\text{ s}$.

---

## 4. Separation of Synthetic Controls from Real Dataset Findings

> [!IMPORTANT]
> All synthetic tests described in Section 3 are strictly segregated within `tests/test_sync_validation.py` and execute exclusively on temporary generated test signals.  
> Real dataset evaluations across all 48 physical recordings from `VS01` to `VS24` were executed separately via `src/sync_validation/runner.py`, and their authentic empirical findings are documented in `outputs/phase2a/sync_validation_results.csv` and `outputs/phase2a/step2_sync_validation_report.md`. No synthetic signals were saved to dataset directories or mixed with real patient records.
