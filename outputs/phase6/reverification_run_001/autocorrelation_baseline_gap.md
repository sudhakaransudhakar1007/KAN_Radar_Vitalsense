# PHASE 6: CLASSICAL AUTOCORRELATION BASELINE SPECIFICATION GAP AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 6 — Independent Re-Verification & Scientific Readiness Audit  
**Run Directory:** `outputs/phase6/reverification_run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  
**Baseline Status:** **`NOT IMPLEMENTED / OUTSTANDING SPECIFICATION GAP`**  

---

## 1. Executive Summary

In compliance with Phase 6 Task 8, an independent audit of the comparative baseline catalog was conducted to determine whether a valid, reproducible classical autocorrelation-based heart-rate estimator exists in the repository.

The audit confirms that **no classical autocorrelation algorithm is implemented**. Unassisted autocorrelation on radar chest-wall displacement is mathematically ill-posed due to severe respiration-to-cardiac harmonic interference. In strict accordance with Task 8, this baseline is not fabricated or artificially approximated; rather, it is formally cataloged as an **outstanding implementation task** with 6 unresolved algorithmic prerequisites.

---

## 2. Technical Reasons Why Autocorrelation is Ill-Posed on Raw Radar Signals

Radar chest-wall displacement signals ($d[n]$) contain both respiratory motion and cardiac micro-Doppler motion:
$$d[n] = s_{\text{resp}}[n] + s_{\text{cardiac}}[n] + \eta[n]$$
1. **Amplitude Disparity:** Respiration displacement ($s_{\text{resp}}$) typically ranges from $1.0\text{ mm}$ to $12.0\text{ mm}$, whereas cardiac apex displacement ($s_{\text{cardiac}}$) ranges from $0.05\text{ mm}$ to $0.5\text{ mm}$ ($10\times$ to $50\times$ weaker).
2. **Harmonic Collision:** Normal human resting breathing occurs at $0.15 - 0.35\text{ Hz}$ ($9 - 21\text{ breaths/min}$). The 2nd and 3rd respiration harmonics ($2f_R$ and $3f_R$) fall in the range $0.30 - 1.05\text{ Hz}$ ($18 - 63\text{ BPM}$), which directly collides with resting cardiac fundamental frequencies ($45 - 75\text{ BPM}$).
3. **Autocorrelation Lobe Masking:** In the autocorrelation sequence $R_{xx}[\tau] = \sum_n x[n]x[n+\tau]$, the high-amplitude breathing harmonics generate dominant peaks that dwarf the true cardiac inter-beat lag, causing unassisted autocorrelation algorithms to consistently select the breathing harmonic rather than the heart rate.

---

## 3. Inventory of Six Unresolved Algorithmic Specifications

Before a classical autocorrelation baseline can be scientifically evaluated against neural models, the following 6 technical specifications must be approved:

| Technical Specification | Current Status | Required Algorithmic Formalization |
| :--- | :---: | :--- |
| **1. Pre-Filtering Configuration** | **UNRESOLVED** | Exact bandpass filter type (e.g., zero-phase 4th-order Butterworth), passband cutoffs ($0.8 - 3.0\text{ Hz}$ vs. adaptive filtering), and stopband attenuation depth ($> 40\text{ dB}$) required to suppress fundamental breathing without introducing phase distortion. |
| **2. Physiological Lag Search Bounds** | **UNRESOLVED** | Exact sample lag bounds $[\tau_{\min}, \tau_{\max}]$ corresponding to physiological heart rate boundaries. At $f_s = 333.333\text{ Hz}$, $35 - 185\text{ BPM}$ corresponds to $\tau \in [108, 571]\text{ samples}$ ($\tau \in [0.324\text{ s}, 1.714\text{ s}]$). |
| **3. Respiration Harmonic Suppression** | **UNRESOLVED** | An audited harmonic cancellation or comb filtering technique to eliminate $2f_R$ and $3f_R$ energy prior to autocorrelation peak extraction. |
| **4. Peak Selection & Prominence Criteria**| **UNRESOLVED** | A deterministic mathematical rule specifying whether to select the global maximum within $[\tau_{\min}, \tau_{\max}]$, the first peak exceeding a relative prominence threshold, or a parabolic-interpolated peak. |
| **5. Confidence & Invalid-Window Handling** | **UNRESOLVED** | Signal Quality Index (SQI) for the autocorrelation curve (e.g., Peak-to-Sidelobe Ratio $\text{PSR} \ge 2.5$) to flag unreadable or motion-corrupted windows without silent failure. |
| **6. Output Coverage & Evaluation Protocol**| **UNRESOLVED** | Documented protocol defining how discarded or unconfident autocorrelation windows are reconciled against neural network predictions that evaluate 100% of accepted windows. |

---

## 4. Scientific Conclusion & Governance Directive

In adherence to Phase 6 Task 8:
- **Do not invent an ad-hoc script** and present it as an established baseline.
- The classical autocorrelation method is formally documented as **`NOT IMPLEMENTED / OUTSTANDING IMPLEMENTATION TASK`**.
- Comparative evaluation in future phases must clearly acknowledge this gap and compare `KANRegressor` strictly against the verified neural baselines (`CNNRegressor`, `MLPRegressor`, and `MeanPredictorBaseline`).
