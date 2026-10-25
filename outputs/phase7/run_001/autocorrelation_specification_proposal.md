# PHASE 7: CLASSICAL AUTOCORRELATION BASELINE SPECIFICATION PROPOSAL

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  
**Document Purpose:** Algorithmic Specification Proposal (Awaiting Investigator Approval Prior to Implementation)  

---

## 1. Executive Summary

In compliance with Phase 7 Task H, this document defines a mathematically rigorous, reproducible specification for the classical autocorrelation-based heart-rate estimation baseline.

Unassisted autocorrelation on radar chest-wall displacement is mathematically ill-posed due to respiration harmonic masking. Rather than fabricating an ad-hoc implementation or speculative numbers, this proposal formalizes all 12 design choices, distinguishing established project constraints from decisions requiring formal investigator approval.

---

## 2. Complete Algorithmic Specification

### 1. Input Signal & Preprocessing
- **Input:** $10.0\text{-second}$ radar chest-wall displacement window ($N = 3,333\text{ samples}$ at $f_s \approx 333.333333\text{ Hz}$).
- **Pre-filtering:** 4th-order zero-phase Butterworth bandpass filter ($0.80 - 3.00\text{ Hz}$, $48.0 - 180.0\text{ BPM}$).
- *Status:* **ESTABLISHED PROJECT REQUIREMENT** (identical to neural baseline preprocessing).

### 2. Valid Frequency & Lag Range
- **Physiological Bounds:** $35.0\text{ BPM} \le \text{HR} \le 185.0\text{ BPM}$
- **Continuous Lag Range:** $\tau \in [0.3243\text{ s}, 1.7143\text{ s}]$
- **Discrete Sample Lag Bounds:**
  $$\tau_{\min} = \left\lceil 0.3243 \times 333.333333 \right\rceil = 108\text{ samples}$$
  $$\tau_{\max} = \left\lfloor 1.7143 \times 333.333333 \right\rfloor = 571\text{ samples}$$
- *Status:* **ESTABLISHED PROJECT REQUIREMENT**.

### 3. Autocorrelation Normalization
- **Formulation:** Unbiased, variance-normalized sample autocorrelation:
  $$R_{xx}[\tau] = \frac{1}{(N - \tau) \cdot \sigma_x^2} \sum_{n=0}^{N - \tau - 1} (x[n] - \mu_x)(x[n+\tau] - \mu_x)$$
  for $\tau \in [\tau_{\min}, \tau_{\max}]$, where $\mu_x$ and $\sigma_x^2$ are the window mean and sample variance.
- *Status:* **PROPOSED SPECIFICATION (Requires Investigator Approval)**.

### 4. Peak Detection & Sub-Sample Refinement
- **Candidate Peak Detection:** Identify local maxima $\tau_p$ such that $R_{xx}[\tau_p] > R_{xx}[\tau_p - 1]$ and $R_{xx}[\tau_p] > R_{xx}[\tau_p + 1]$.
- **Prominence Threshold:** Require relative peak prominence $\ge 0.15 \times \max_{\tau}(R_{xx}[\tau])$.
- **Parabolic Interpolation:** Refine discrete lag $\tau_p$ to continuous $\tau^*$ via 3-point parabolic fitting:
  $$\Delta \tau = \frac{R_{xx}[\tau_p - 1] - R_{xx}[\tau_p + 1]}{2 (R_{xx}[\tau_p - 1] - 2 R_{xx}[\tau_p] + R_{xx}[\tau_p + 1])}, \quad \tau^* = \tau_p + \Delta \tau$$
- *Status:* **PROPOSED SPECIFICATION (Requires Investigator Approval)**.

### 5. Periodicity-to-BPM Conversion
$$\text{HR}_{\text{BPM}} = \frac{60 \times f_s}{\tau^*} = \frac{60 \times 333.333333}{\tau^*} = \frac{20,000.0}{\tau^*}$$
- *Status:* **MATHEMATICAL DEFINITION**.

### 6. Respiration Harmonic Ambiguity Suppression
- **Problem:** Normal breathing at $0.2 - 0.35\text{ Hz}$ ($12 - 21\text{ breaths/min}$) produces 2nd and 3rd harmonics ($2f_R \in [0.4, 0.7]\text{ Hz}$, $3f_R \in [0.6, 1.05]\text{ Hz}$) that overlap resting heart rates ($36 - 63\text{ BPM}$).
- **Proposed Rejection Rule:**
  1. Compute wideband autocorrelation over $\tau \in [200, 1500]\text{ samples}$ to locate dominant breathing period $\tau_R$.
  2. If candidate cardiac peak $\tau^*$ satisfies $\left|\frac{\tau_R}{k} - \tau^*\right| < 10\text{ samples}$ for $k \in \{2, 3\}$, search for alternate prominence peak outside harmonic tolerance.
- *Status:* **PROPOSED SPECIFICATION (Requires Investigator Approval)**.

### 7. Invalid-Window Handling & Signal Quality Index (SQI)
- **Peak-to-Sidelobe Ratio (PSR):**
  $$\text{PSR} = \frac{R_{xx}[\tau^*] - \mu_{R}}{\sigma_R}$$
- If $\text{PSR} < 2.0$ or $R_{xx}[\tau^*] < 0.25$, window is flagged as `LOW_CONFIDENCE`.
- *Status:* **PROPOSED SPECIFICATION (Requires Investigator Approval)**.

### 8. Output Coverage & Evaluation Protocol
- Evaluate on the exact same 1,029 accepted windows as neural models.
- For windows where autocorrelation fails or yields low confidence, assign training-fold mean $\mu_{y,\text{train}}$ (fallback baseline) to ensure 100% test window coverage for fair comparative scoring.
- *Status:* **PROPOSED SPECIFICATION (Requires Investigator Approval)**.

### 9. Complexity & Runtime Reporting
- Trainable parameters: **0 parameters**.
- Non-trainable parameters: **0 parameters**.
- Latency: CPU FFT-based autocorrelation latency benchmarked over 200 runs.
- *Status:* **ESTABLISHED PROJECT REQUIREMENT**.

### 10. Required Unit Tests & Synthetic Fixtures
- Test with pure sinusoidal synthetic cardiac signals (verify $\text{MAE} < 0.1\text{ BPM}$).
- Test with multi-tone breathing + cardiac signals (verify harmonic suppression).
- Test with flatline / non-numeric inputs (verify graceful exception handling).
- *Status:* **ESTABLISHED PROJECT REQUIREMENT**.

---

## 3. Checklist of Investigator Decisions Needed Before Implementation

- [ ] Decision 1: Approve 3-point parabolic peak interpolation for sub-sample lag resolution.
- [ ] Decision 2: Approve the proposed respiration harmonic cancellation rule.
- [ ] Decision 3: Approve fallback to training-fold mean for unreadable autocorrelation windows to maintain 100% coverage parity with neural models.
