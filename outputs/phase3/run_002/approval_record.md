# Phase 3 User Approval Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Dataset:** VITALSENSE (Subjects VS01–VS24, Resting and Apnea)  
**Execution Stage:** Phase 3 — Final Completion & Approval Record  
**Run ID:** `run_002`  
**Execution & Approval Date:** October 15, 2026  
**Auditor & Scientific ML Engineering Team**  

---

## 1. Context & Purpose

This document formally records the user's approval decisions regarding the Phase 3 preflight methodology and quality-screening framework. In accordance with the project charter, these decisions are cataloged strictly as **operational user-approved decisions** to govern downstream dataset preparation, **not as independent physical proof** that hardware synchronization was established or that all physiological reference recordings are inherently artifact-free.

---

## 2. Decision 1: Radar–ECG Synchronization Audit Approach

- **Decision ID:** `DEC-01`
- **Topic:** Radar–ECG Synchronization Methodology & Time Alignment Convention
- **Status:** **`USER_APPROVED`**
- **Approved Scope:** The user has approved proceeding under the documented synchronization assumptions, constraints, and limitations established during the Phase 2A and Phase 3 audits.

### Retained Assumptions & Limitations:
1. **Hardware Synchronization Status:** `UNVERIFIED`. A comprehensive audit across all 96 MAT files in the VITALSENSE dataset revealed zero physical hardware trigger channels, zero Pulse-Per-Second (PPS) signals, and zero shared-clock digitizer timestamps.
2. **Relative Time Alignment:** Evaluated under the prespecified nominal zero-offset assumption ($t_0 = 0.0\text{ s}$ for both the 120-GHz radar and the Mindray physiological monitor). This nominal alignment is an operational convention, not measured proof of zero-latency synchronization.
3. **Monitor HR Disqualification:** The Mindray monitor's 120-point displayed `HR` array remains strictly **disqualified** from serving as supervised training labels due to the documented $+6.0\text{ s}$ to $+7.0\text{ s}$ moving-average filter delay relative to instantaneous cardiac events.
4. **Scientific Boundary:** This approval acknowledges the limitation that hardware synchronization is unverified, enabling window-level exploration while prohibiting claims of verified physical synchrony.

---

## 3. Decision 2: ECG R-Peak Detection & Quality-Screening Approach

- **Decision ID:** `DEC-02`
- **Topic:** ECG Reference Validation, Delimiter Handling, and Signal Quality Index (SQI) Screening
- **Status:** **`USER_APPROVED`**
- **Approved Scope:** The user has approved the continuous ECG R-peak detection method (Pan-Tompkins algorithm) and the proposed multi-parameter SQI screening criteria to govern reference label eligibility.

### Exact Approved SQI Thresholds:
- **Valid RR Coverage:** $> 85.0\%$ of total recording duration.
- **Maximum RR Interval Gap:** $< 3.0\text{ seconds}$.
- **Physiological Heart-Rate Bounds:** $35.0\text{ bpm} \le \text{HR} \le 185.0\text{ bpm}$ (corresponding to RR interval limits of $0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$).

### Retained Assumptions & Limitations:
1. **Periodic Delimiter NaNs:** In-memory single-sample linear interpolation of isolated delimiter NaNs (present in 47 of 48 Mindray files) is authorized strictly for continuous QRS filtering. Zero raw `.mat` files are modified on disk.
2. **Documented Borderline / Failing Cases:**
   - `VS20_Apnea` exhibited a reported maximum RR gap of $3.12\text{ s}$, failing the $< 3.0\text{ s}$ maximum-gap criterion.
   - `VS10_Resting` exhibits a delimiter NaN at sample index 0 (leading boundary), which must be handled reproducibly.
3. **Reproducible Exclusion Protocol:** Any recording or window that fails the approved SQI criteria must be strictly flagged and excluded from supervised loss computation during model evaluation.
4. **Scientific Boundary:** A passing SQI score confirms internal physiological consistency of the ECG Lead II trace; it does **not** prove physical cross-sensor alignment with the radar signal.

---

## 4. Decision 3: Primary Radar Preprocessing Filter Selection

- **Decision ID:** `DEC-03`
- **Topic:** Radar Signal Preprocessing Filter Topology
- **Status:** **`USER_APPROVED`**
- **Approved Filter:** 3rd-order zero-phase Butterworth bandpass filter spanning **0.8 Hz to 3.0 Hz** (48 to 180 bpm).

### Empirical Basis & Boundary:
1. **Empirical Power Concentration:** The 0.8–3.0 Hz bandpass filter concentrates **48.43%** of signal power in the cardiac band, compared to **39.11%** for the candidate 1.0–20.0 Hz filter and **0.60%** for unfiltered raw `VitalSig`.
2. **Nyquist Bound Compliance:** Validated across all 48 recordings ($0 < 0.8 < 3.0 < 166.67\text{ Hz}$).
3. **Explicit Scientific Boundary:** This choice is approved strictly on the basis of cardiac-band spectral power concentration. **No claim is made that this filter improves KAN model accuracy** in the absence of downstream empirical training and evaluation evidence.

---

## 5. Governance & Completion Gate Alignment

> [!IMPORTANT]
> The recording of these user approvals does **NOT** automatically close the Phase 2A Finalization Gate, nor does it authorize immediate generation of persistent supervised window datasets. In compliance with Section 6 and Section 9 execution rules, supervised window dataset generation remains **`BLOCKED BY PHASE 2A GATE`**.
