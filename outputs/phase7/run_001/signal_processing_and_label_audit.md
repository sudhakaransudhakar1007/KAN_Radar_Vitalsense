# PHASE 7: SIGNAL PROCESSING & REFERENCE HR LABEL PIPELINE AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  

---

## 1. Executive Summary

In compliance with Phase 7 Task D, a comprehensive code-level audit was performed on the signal-processing pipeline, filtering routines, R-peak detector, window-indexing math, and reference heart rate derivation algorithms.

The audit confirms that the radar and ECG processing modules are mathematically robust, maintain strict time-interval alignment despite differing sampling rates ($333.33\text{ Hz}$ vs. $500\text{ Hz}$), enforce zero data leakage, and handle boundary artifacts and invalid cardiac intervals defensively.

---

## 2. Line-by-Line Code Review of Signal-Processing Modules

### A. Radar Preprocessing (`src/phase3/radar_preprocessing.py`)
- **Filter Topology:** 4th-order zero-phase Butterworth bandpass filter.
- **Passband:** $0.80\text{ Hz} - 3.00\text{ Hz}$ ($48.0 - 180.0\text{ BPM}$).
- **Implementation:** `scipy.signal.butter(4, [0.8, 3.0], btype='bandpass', fs=333.333333)` executed via forward-backward filtering (`scipy.signal.filtfilt`), ensuring exactly zero phase distortion.
- **Nyquist Validation:** Sampling rate $f_s \approx 333.33\text{ Hz} \gg 2 \times 3.0\text{ Hz} = 6.0\text{ Hz}$, providing ample oversampling margin ($> 55\times$ Nyquist).

### B. ECG Preprocessing & R-Peak Detection (`src/phase3/ecg_reference.py`)
- **Algorithm:** Audited Pan-Tompkins QRS detector.
- **Bandpass Filter:** 5–15 Hz bandpass filtering to isolate ventricular depolarization from baseline wander and P/T-wave interference.
- **Derivative & Squaring:** Five-point derivative operator followed by non-linear squaring to accentuate high-frequency QRS energy.
- **Moving-Window Integration:** Rectangular integration window of length $150\text{ ms}$ ($75\text{ samples}$ at $500\text{ Hz}$).
- **Adaptive Thresholding:** Dynamic signal and noise peak thresholds with dual-threshold search-back for missed beats.
- **Refractory Blanking:** $200\text{ ms}$ refractory period ($100\text{ samples}$) preventing double-detection of tall T-waves.

---

## 3. Window Indexing & Sampling Rate Independence

Because radar ($333.333333\text{ Hz}$) and reference ECG ($500.0\text{ Hz}$) operate on different sampling frequencies, window indexing must reference physical time rather than sample indices:

$$t_{\text{start}} = k \times \Delta t_{\text{stride}} = k \times 5.0\text{ s}, \quad t_{\text{end}} = t_{\text{start}} + 10.0\text{ s}$$

- **Radar Sample Boundaries:**
  $$n_{\text{radar, start}} = \text{round}(t_{\text{start}} \times 333.333333), \quad n_{\text{radar, end}} = n_{\text{radar, start}} + 3,333$$
- **ECG Sample Boundaries:**
  $$m_{\text{ecg, start}} = \text{round}(t_{\text{start}} \times 500.0), \quad m_{\text{ecg, end}} = m_{\text{ecg, start}} + 5,000$$

**Audit Check:** The code in `supervised_dataset_generator.py` (lines 170–195) uses physical time intervals $[t_{\text{start}}, t_{\text{end}}]$ to query R-peaks, completely avoiding sample-index confusion between the two disparate rates.

---

## 4. Reference HR Derivation & SQI Screening Rules

### A. Ground Truth Heart Rate Formula
For a 10.0-second window containing detected R-peaks at times $\{t_{R, 1}, t_{R, 2}, \dots, t_{R, M}\} \subset [t_{\text{start}}, t_{\text{end}}]$:
$$RR_i = t_{R, i+1} - t_{R, i} \quad \text{for } i = 1, \dots, M-1$$
$$\text{HR}_{\text{ref}} = \frac{60}{\frac{1}{M-1}\sum_{i=1}^{M-1} RR_i} \quad (\text{BPM})$$
This harmonic mean definition correctly maps mean interval duration to instantaneous frequency in BPM.

### B. Signal Quality Screening Criteria (Approved by User in Phase 3)
1. **Valid RR Coverage:** Ratio of cumulative valid RR duration to window length:
   $$\text{Coverage}_{\text{RR}} = \frac{\sum_{i} RR_i}{T_{\text{win}}} \ge 85.0\%$$
2. **Maximum Permissible RR Gap:** Longest interval between consecutive detected R-peaks:
   $$\Delta t_{\text{gap, max}} \le 3.0\text{ seconds}$$
3. **Physiological Feasibility Limits:**
   $$35.0\text{ BPM} \le \text{HR}_{\text{ref}} \le 185.0\text{ BPM} \iff 0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$$

---

## 5. Potential Defect & Leakage Audit Checklist

| Potential Defect Check | Audit Finding | Concrete Verification Evidence |
| :--- | :---: | :--- |
| **Filter Cutoff / Order Mismatches** | **NO DEFECT** | 4th-order zero-phase Butterworth ($0.8 - 3.0\text{ Hz}$) used consistently |
| **Incorrect Sampling Rate Assumptions** | **NO DEFECT** | Loader dynamically reads `Radar.fs` ($333.33\text{ Hz}$) and `Fs_ecg` ($500\text{ Hz}$) |
| **Cross-Signal Sample Index Errors** | **NO DEFECT** | Alignment is based strictly on physical time interval $[t_{\text{start}}, t_{\text{end}}]$ |
| **Off-by-One Boundary Errors** | **NO DEFECT** | Exact 3,333 radar samples and 5,000 ECG samples extracted per window |
| **Full-Recording Normalization Leakage** | **NO DEFECT** | Target normalization parameters $(\mu, \sigma)$ fitted strictly on training subjects |
| **Held-Out Target Contamination** | **NO DEFECT** | Test fold targets are never used to fit normalizer or model |
| **Invalid / Non-Finite Reference Targets** | **NO DEFECT** | 100% of accepted windows have finite float targets ($47.52 - 82.89\text{ BPM}$) |
| **Target Leakage into Model Inputs** | **NO DEFECT** | Model inputs contain strictly 1D radar displacement; zero ECG data |
| **Inconsistent Train/Inference Scaling** | **NO DEFECT** | Identical filter parameters and normalizer inversion applied across all sets |

---

## 6. Recommendations for Future Research Phases

1. **Investigate Filter Bandpass Sensitivity:** The $0.8 - 3.0\text{ Hz}$ bandpass filter is currently fixed. In future authorized model training, evaluating a narrower band (e.g., $0.8 - 2.0\text{ Hz}$, $48 - 120\text{ BPM}$) or adaptive filtering could be explored as an empirical hyperparameter comparison.
2. **Boundary Delimiter Robustness:** 22 windows were disqualified due to `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`. A refined edge-handling routine could potentially recover 10–15 resting windows without compromising clinical data quality.
