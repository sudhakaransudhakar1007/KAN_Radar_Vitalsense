# PHASE 4B: PHASE 2A READINESS & SYNCHRONIZATION EVIDENCE REVIEW

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Audit Stage:** Phase 4B — Scientific Readiness & Governance Review  
**Audit File:** `outputs/phase4/audit_run_001/phase2a_readiness_review.md`  

---

## 1. Review of Current Phase 2A Governance Status

A thorough re-inspection of [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md) confirmed the official gate status:

- **Overall Stage Verdict:** **`RECONCILIATION PARTIAL — FINALIZATION GATE OPEN`**
- **Hardware Clock Synchronization:** **`UNVERIFIED`**
- **Respiratory Alignment:** **`CONSISTENT_NOT_PROVEN`**
- **Supervised-Label Generation:** **`NOT YET APPROVED`**
- **10-Second Window-Alignment Adequacy:** **`NOT YET SUPPORTED without its evidence gate`**

This gate has **not** been closed. In compliance with project governance, no automated code or model training is permitted to unilaterally close this gate without explicit user authorization.

---

## 2. Physical Synchronization Evidence vs. Nominal $t_0$ Convention

A critical distinction must be maintained between **physical hardware synchronization** and the **nominal $t_0$ operational assumption**:

### What Physical Evidence Exists?
1. **0 of 96 MAT files** contain shared clock channels, synchronization markers, TTL triggers, or timestamp strings.
2. The radar digitizer and Mindray physiological monitor operated on uncoupled, independent internal crystal oscillators.
3. Therefore, **physical hardware clock synchronization is completely UNVERIFIED**. There is zero physical evidence of sample-accurate co-triggering.

### What is the Nominal $t_0 = 0.0\text{ s}$ Assumption?
- In [`outputs/supervised_dataset/run_001/synchronization_assumptions_record.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/synchronization_assumptions_record.md), window extraction paired radar sample 0 with ECG sample 0 under the explicit assumption that both digitizers started recording at $t = 0.0\text{ s}$.
- This is an **unproven modeling convention**, approved by the user as a working assumption to explore preprocessing and architecture feasibility, **not** as verified clinical ground truth.

### Disqualification of Monitor Display HR:
- The Phase 2A audit conclusively proved that the Mindray commercial monitor's displayed `HR` array has an average lag of **$+6.21\text{ seconds}$** (median: $+7.0\text{ s}$, mode: $+7.0\text{ s}$) relative to continuous instantaneous ECG R-peaks.
- Training any neural network against the raw monitor `HR` array would severely corrupt target labels. Instantaneous ECG R-peak harmonic derivation is mandatory.

---

## 3. Summary of Verified Facts, Uncertainties, and Gate Decision Requirements

### A. What Can Be Scientifically Concluded:
1. **Mathematical Integrity:** The Pan-Tompkins QRS detection, SQI screening (>85% coverage, <3.0s gap), and harmonic mean HR derivation ($60 / \text{mean}(RR)$) are mathematically verified and reproducible.
2. **Window Extraction Consistency:** Exactly 1,029 unique windows were extracted from 48 recordings with correct integer sample boundaries (3,333 samples per 10 s window, 1,667 stride, 1,660 trailing tail samples).
3. **Model & Code Readiness:** The authentic B-spline KAN layer, Conv1D feature extractor, baseline MLP, and 24-fold LOSO isolation logic are fully implemented and verified via unit tests.
4. **Subject Independence:** All 24 folds exhibit 0% subject leakage.

### B. What Remains Scientifically Uncertain:
1. **Residual Timing Offset ($\Delta t$):** Because hardware clocks were uncoupled, the true start-time offset between radar and ECG could range from milliseconds to a few seconds. While 10-second cardiac averaging provides tolerance against small sub-second shifts, unmodeled offsets $>2\text{ s}$ would degrade label precision.
2. **Radar Cardiac Modulation Signal-to-Noise Ratio (SNR):** In apnea recordings and resting conditions with subtle chest displacement, the Doppler phase SNR can be low. Whether a KAN can generalize across unseen subject chest morphologies on real radar data without overfitting remains unknown until authorized training occurs.

### C. Defensible Gate Decision Requirements:
For the user to make an informed, defensible Phase 2A Finalization Gate decision, the following record is established:
- **Prerequisite 1:** Acknowledge that hardware clock synchronization cannot be proven from the dataset files, and that all models operate under the documented `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` convention.
- **Prerequisite 2:** Approve the target normalization and output bias initialization enhancements to prevent the high-bias artifact identified in the synthetic benchmark.
- **Prerequisite 3:** Formally authorize Phase 4 real-data LOSO training across the 24 folds under these explicit constraints.
