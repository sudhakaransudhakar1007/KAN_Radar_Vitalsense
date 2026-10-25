# PHASE 5: DATASET & REFERENCE LABEL VALIDATION AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 5 — Subject-Independent KAN Training and Baseline Experiments  
**Run Directory:** `outputs/phase5/run_001/`  
**Audit Date:** October 16, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific ML Auditor  

---

## 1. Executive Summary

In preparation for Phase 5 model training, an independent non-training audit of the supervised dataset inventory and reference labels was conducted. The audit verified the contents of `outputs/supervised_dataset/run_001/`, the underlying raw VITALSENSE radar and reference MAT files, window segmentation parameters, reference heart rate derivations, and operational timing conventions.

All 1,029 accepted windows across 24 human subjects and 48 recording sessions meet the strict biomedical signal quality criteria established in Phase 3. However, persistent real-data ML training arrays remain withheld in compliance with the Phase 2A governance gate.

---

## 2. Dataset Inventory & Subject Coverage

The supervised dataset inventory was audited against the physical files on disk:
- **Root Dataset Directory:** `data/VITALSENSE_120_DATASET`
- **Total Subjects:** 24 human subjects (`S01` through `S24`).
- **Total Experimental Recordings:** 48 sessions (2 per subject):
  - **Resting condition (`rest`):** 24 sessions.
  - **Post-exercise condition (`post_exercise`):** 24 sessions.
- **Radar Sensor:** 120-GHz FMCW radar operating at nominal sampling frequency $f_s \approx 333.333\text{ Hz}$ ($T_s = 3.0\text{ ms}$).
- **Reference Sensor:** ECG bio-signal recorder sampled at $f_{s,\text{ECG}} = 1000\text{ Hz}$.

### Window Segmentation Integrity
- **Nominal Window Length:** $T_{\text{window}} = 10.0\text{ seconds}$ ($3,333\text{ radar samples}$, $10,000\text{ ECG samples}$).
- **Nominal Window Stride:** $\Delta t_{\text{stride}} = 5.0\text{ seconds}$ ($50\%\text{ overlap}$).
- **Candidate Windows Generated:** 1,056 windows ($22\text{ candidate windows/recording} \times 48\text{ recordings}$).
- **Accepted Windows:** 1,029 windows ($97.44\%$).
- **Rejected Windows:** 27 windows ($2.56\%$).
- **Trailing Unused Data:** $1,660\text{ samples}$ ($4.98\text{ seconds}$) per recording discarded to maintain exact integer window lengths.

---

## 3. Reference Label Derivation & Signal Quality Indices (SQI)

### A. Reference Ground Truth Definition
Reference heart rate labels are derived exclusively from instantaneous RR intervals detected via an audited Pan-Tompkins R-peak detector:
$$\text{HR}_{\text{ref}} = \frac{60}{\overline{RR}_{\text{window}}} \quad (\text{BPM})$$
where $\overline{RR}_{\text{window}}$ represents the mean RR interval in seconds within the 10-second window (harmonic mean definition of heart rate).

### B. Approved SQI Rejection Thresholds
In accordance with user-approved Phase 3 preflight criteria:
1. **Valid RR Coverage:** $\text{Coverage}_{\text{RR}} \ge 85\%$ (ratio of valid detected RR intervals to expected duration).
2. **Maximum Permissible RR Gap:** $\Delta t_{\text{gap, max}} \le 3.0\text{ seconds}$ (rejection of windows containing electrode disconnections or severe ectopic bursts).
3. **Physiological Feasibility Limits:** $30\text{ BPM} \le \text{HR}_{\text{ref}} \le 210\text{ BPM}$.

### C. Rejection Audit (27 Disqualified Windows)
The 27 rejected windows were verified across `outputs/supervised_dataset/run_001/rejected_window_manifest.csv`:
- All 27 rejections occurred in post-exercise recordings during periods of high perspiration, motion artifact, or transient electrode lead detachment.
- Rejection reasons:
  - $\text{Coverage}_{\text{RR}} < 85\%$: 19 windows.
  - $\Delta t_{\text{gap, max}} > 3.0\text{ seconds}$: 8 windows.
- Zero windows were rejected due to artificial boundary truncations or software bugs.

---

## 4. Disqualification of Displayed Monitor HR

Phase 2A cross-correlation and step-response audits revealed a systematic latency in the bedside monitor's displayed numeric HR stream:
- **Observed Mean Latency:** $+6.21\text{ seconds}$ relative to instantaneous ECG R-peak ground truth.
- **Root Cause:** Proprietary moving-average smoothing filter on commercial bedside monitor hardware.
- **Scientific Audit Finding:** The bedside monitor HR stream is **permanently disqualified** from serving as ground truth reference labels. Using monitor HR would introduce severe phase distortion and artificial label error into supervised learning.

---

## 5. Radar Preprocessing & Synchronization Operational Convention

### A. Primary Radar Preprocessing Filter
- **Filter Type:** 4th-order zero-phase Butterworth bandpass filter.
- **Passband:** $0.8\text{ Hz} - 3.0\text{ Hz}$ ($48 - 180\text{ BPM}$).
- **Scientific Caveat:** Preserved as the primary candidate filter based on Phase 3 spectral analysis; no claim of superior accuracy is made prior to rigorous Phase 5 model evaluations.

### B. Synchronization Operational Status
- **Physical Reality:** No shared hardware clock or common electronic trigger exists between the FMCW radar digitizer and the ECG recorder.
- **Operational Convention:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.
- **Convention Details:** Radar and ECG data streams are aligned assuming their recording file start indices correspond to nominal $t=0.0\text{s}$. This operational assumption is documented as a scientific limitation.

---

## 6. Audit Conclusion

The supervised dataset and reference label pipeline are verified, reproducible, and ready for model ingestion. However, because the Phase 2A Finalization Gate remains officially **`OPEN`**, real-data tensor ingestion for training remains **BLOCKED**.
