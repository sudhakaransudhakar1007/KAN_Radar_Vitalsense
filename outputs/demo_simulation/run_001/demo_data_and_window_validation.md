# PHASE 8 DATA AND WINDOWING VALIDATION REPORT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 8 — Recorded Radar Data Streaming Simulation  
**Document:** Data Ingestion & Rolling Window Boundary Validation  
**Run Directory:** `outputs/demo_simulation/run_001/`  
**Execution Date:** 2026-10-18  

---

## 1. Objective & Mathematical Formulation

This report documents the rigorous verification of radar signal ingestion, sampling rate extraction, signal finiteness, and rolling window segmentation implemented in the Phase 8 streaming simulation demo.

The segmentation parameters are defined by the authoritative project specification:
- **Radar Sampling Rate:** $f_s = 333.3333333333333\text{ Hz}$ ($T_{\text{frame}} = 0.003\text{ s}$)
- **Nominal Recording Duration:** $T_{\text{total}} = 120.0\text{ s}$
- **Total Raw Samples:** $N_{\text{total}} = 40,000\text{ samples}$
- **Window Duration:** $T_{\text{win}} = 10.0\text{ s}$
- **Hop Duration:** $T_{\text{hop}} = 5.0\text{ s}$

The exact discrete sample lengths are computed as:
$$N_{\text{win}} = \text{round}(T_{\text{win}} \times f_s) = \text{round}(10.0 \times 333.3333333333333) = 3,333\text{ samples}$$
$$N_{\text{hop}} = \text{round}(T_{\text{hop}} \times f_s) = \text{round}(5.0 \times 333.3333333333333) = 1,667\text{ samples}$$

The total number of complete, unpadded windows $K$ is given by:
$$K = \left\lfloor \frac{N_{\text{total}} - N_{\text{win}}}{N_{\text{hop}}} \right\rfloor + 1 = \left\lfloor \frac{40,000 - 3,333}{1,667} \right\rfloor + 1 = \left\lfloor 21.9958 \right\rfloor + 1 = 21 + 1 = 22\text{ windows}$$

---

## 2. Window Index and Boundary Arithmetic

The rolling window buffer evaluates index boundaries deterministically for each window $k \in \{0, 1, \dots, 21\}$:

$$\text{start\_sample\_idx}(k) = k \times N_{\text{hop}} = k \times 1,667$$
$$\text{end\_sample\_idx}(k) = \text{start\_sample\_idx}(k) + N_{\text{win}} = k \times 1,667 + 3,333$$
$$\text{start\_time\_s}(k) = \frac{\text{start\_sample\_idx}(k)}{f_s} \approx k \times 5.0\text{ s}$$
$$\text{end\_time\_s}(k) = \frac{\text{end\_sample\_idx}(k)}{f_s} \approx k \times 5.0 + 10.0\text{ s}$$

### Complete Window Boundary Schedule (Recording $N = 40,000$ samples)
| Window $k$ | Start Sample | End Sample | Sample Count | Start Time (s) | End Time (s) | Overlap with $k-1$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | 0 | 3,333 | 3,333 | 0.000 | 10.000 | N/A (Initial) |
| **1** | 1,667 | 5,000 | 3,333 | 5.001 | 15.001 | 1,666 samples (50.0%) |
| **2** | 3,334 | 6,667 | 3,333 | 10.002 | 20.002 | 1,666 samples (50.0%) |
| **3** | 5,001 | 8,334 | 3,333 | 15.003 | 25.003 | 1,666 samples (50.0%) |
| **4** | 6,668 | 10,001 | 3,333 | 20.004 | 30.004 | 1,666 samples (50.0%) |
| **5** | 8,335 | 11,668 | 3,333 | 25.005 | 35.005 | 1,666 samples (50.0%) |
| **6** | 10,002 | 13,335 | 3,333 | 30.006 | 40.006 | 1,666 samples (50.0%) |
| **7** | 11,669 | 15,002 | 3,333 | 35.007 | 45.007 | 1,666 samples (50.0%) |
| **8** | 13,336 | 16,669 | 3,333 | 40.008 | 50.008 | 1,666 samples (50.0%) |
| **9** | 15,003 | 18,336 | 3,333 | 45.009 | 55.009 | 1,666 samples (50.0%) |
| **10** | 16,670 | 20,003 | 3,333 | 50.010 | 60.010 | 1,666 samples (50.0%) |
| **11** | 18,337 | 21,670 | 3,333 | 55.011 | 65.011 | 1,666 samples (50.0%) |
| **12** | 20,004 | 23,337 | 3,333 | 60.012 | 70.012 | 1,666 samples (50.0%) |
| **13** | 21,671 | 25,004 | 3,333 | 65.013 | 75.013 | 1,666 samples (50.0%) |
| **14** | 23,338 | 26,671 | 3,333 | 70.014 | 80.014 | 1,666 samples (50.0%) |
| **15** | 25,005 | 28,338 | 3,333 | 75.015 | 85.015 | 1,666 samples (50.0%) |
| **16** | 26,672 | 30,005 | 3,333 | 80.016 | 90.016 | 1,666 samples (50.0%) |
| **17** | 28,339 | 31,672 | 3,333 | 85.017 | 95.017 | 1,666 samples (50.0%) |
| **18** | 30,006 | 33,339 | 3,333 | 90.018 | 100.018 | 1,666 samples (50.0%) |
| **19** | 31,673 | 35,006 | 3,333 | 95.019 | 105.019 | 1,666 samples (50.0%) |
| **20** | 33,340 | 36,673 | 3,333 | 100.020 | 110.020 | 1,666 samples (50.0%) |
| **21** | 35,007 | 38,340 | 3,333 | 105.021 | 115.021 | 1,666 samples (50.0%) |

---

## 3. Trailing Tail Accounting

The end index of window 21 is:
$$\text{end\_sample\_idx}(21) = 35,007 + 3,333 = 38,340\text{ samples}$$

The remaining samples in the 120-second recording are:
$$N_{\text{tail}} = N_{\text{total}} - \text{end\_sample\_idx}(21) = 40,000 - 38,340 = 1,660\text{ samples}$$
$$T_{\text{tail}} = \frac{1,660}{333.3333333333333} = 4.980\text{ s}$$

### Trailing Tail Safeguards:
1. **Zero Silent Padding:** The simulation engine refuses to synthesize zero-padded samples or duplicate frames to force a 23rd window.
2. **Deterministic Termination:** When the virtual clock reaches $t = 120.0\text{ s}$, the engine identifies that $1,660 < 3,333$, transitions `playback_state` to `COMPLETED`, and logs the trailing tail without crashing.
3. **Consistency:** This identical 22-window count is verified across all 48 radar recordings in the VITALSENSE dataset and matches the Phase 3/Phase 4 accepted window counts.

---

## 4. Signal Ingestion and Quality Validation

Every loaded recording undergoes automated validation in `RadarSimulationEngine.load_recording`:
1. **MAT-File Structure:** Verified using `RobustMatLoader.inspect_mat_version` to confirm MATLAB v5/v7 binary format.
2. **Variable Integrity:** Presence of 1D/2D `VitalSig` verified. Non-existent variable triggers immediate `playback_state = "ERROR"`.
3. **Sampling Frequency Check:** Checks `Radar.fs` struct field first; falls back to $1.0 / T_{\text{frame}}$ if `T_frame` is present. Missing or negative $f_s$ triggers `playback_state = "ERROR"`.
4. **Finiteness Audit:** Computes $\sum \text{isnan}(x)$ and $\sum \text{isinf}(x)$. If all samples are finite, flags `VALID_FINITE_SIGNAL`; if non-finite samples are detected, flags `NON_FINITE_SAMPLES_DETECTED` and records quality warnings.
5. **Preprocessing Verification:** Applies zero-phase 3rd-order Butterworth bandpass filter ($0.8\text{--}3.0\text{ Hz}$). Filtered signal maintains identical sample length ($40,000$) and finite bounds.

---

## 5. Verification Against Authoritative Pipeline

| Specification Item | Authoritative Baseline | Phase 8 Demo Engine | Verification Status |
|---|---|---|:---:|
| Sampling Rate ($f_s$) | $333.3333\text{ Hz}$ | $333.3333\text{ Hz}$ | **MATCH** |
| Window Length ($T_{\text{win}}$) | $10.0\text{ s}$ | $10.0\text{ s}$ | **MATCH** |
| Window Samples ($N_{\text{win}}$) | $3,333\text{ samples}$ | $3,333\text{ samples}$ | **MATCH** |
| Hop Length ($T_{\text{hop}}$) | $5.0\text{ s}$ | $5.0\text{ s}$ | **MATCH** |
| Hop Samples ($N_{\text{hop}}$) | $1,667\text{ samples}$ | $1,667\text{ samples}$ | **MATCH** |
| Windows per Recording | $22\text{ complete windows}$ | $22\text{ complete windows}$ | **MATCH** |
| Bandpass Passband | $0.8\text{--}3.0\text{ Hz}$ | $0.8\text{--}3.0\text{ Hz}$ | **MATCH** |
| Bandpass Filter Order | 3rd order Butterworth | 3rd order Butterworth | **MATCH** |
| Bidirectional Zero-Phase | `scipy.signal.filtfilt` | `scipy.signal.filtfilt` | **MATCH** |
| Zero Silent Padding | Enforced | Enforced | **MATCH** |

Both unit tests (`test_windowing_deterministic_counts`) and live execution on `VS01_Resting.mat` confirm complete adherence to the authoritative pipeline.
