# PHASE 7: SYNCHRONIZATION EVIDENCE & HARDWARE TIMING LIMITATION RECORD

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 7 — Final Re-Verification, Defect Investigation & Governance Readiness Audit  
**Run Directory:** `outputs/phase7/run_001/`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Senior Biomedical Signal Processing Engineer & Scientific Reproducibility Auditor  
**Timing Limitation Code:** **`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`**  

---

## 1. Executive Summary

In compliance with Phase 7 Task G and Task 13, an independent engineering review of the physical timing and synchronization infrastructure was conducted.

The audit confirms that **physical hardware synchronization has not been established**. No common electronic trigger, shared oscillator, pulse-per-second (PPS) synchronization, or cross-device hardware timestamp exists in the VITALSENSE dataset.

All windowed analysis relies on the operational assumption `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. In strict adherence to scientific integrity rules, high empirical cross-correlation is explicitly distinguished from physical synchronization proof.

---

## 2. Four Hierarchical Levels of Timing Evidence

To prevent misleading claims, the project maintains strict conceptual separation across four distinct levels of timing evidence:

| Level of Timing Evidence | Description & Mathematical Basis | Status in Project | What It Establishes | What It CANNOT Establish |
| :--- | :--- | :---: | :--- | :--- |
| **Level 1: Sample-Rate Metadata** | Header metadata specifying $f_{s,\text{radar}} \approx 333.33\text{ Hz}$ and $f_{s,\text{ecg}} = 500\text{ Hz}$. | **VERIFIED** | Nominal sample interval ($T_s = 3\text{ms}$ / $2\text{ms}$) and recording duration ($120.0\text{s}$). | Physical start-time relationship between devices. |
| **Level 2: Nominal Start Alignment** | Setting sample index 0 in both files to nominal $t_0 = 0.0\text{ s}$ (`UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`). | **OPERATIONAL ASSUMPTION** | Pragmatic software time axis for window segmentation. | Verification that recording started simultaneously in hardware. |
| **Level 3: Empirically Estimated Alignment** | Cross-correlation and windowed agreement showing resting MAE $\approx 2.97\text{ BPM}$ at $\tau = 0\text{ s}$. | **EMPIRICALLY OBSERVED** | Macro-level statistical agreement over 10.0-second intervals. | Sub-second phase lock, beat-to-beat PTT, or hardware sync proof. |
| **Level 4: Verified Physical Synchronization** | Shared TTL trigger, PPS pulse, or genlock clock recorded on both hardware digitizers. | **UNVERIFIED / ABSENT** | Definite hardware clock synchronization. | N/A (Not present in dataset). |

---

## 3. Detailed Hardware Timing Uncertainty Analysis

1. **Host-Level Operating System Skew:** Data acquisition was initiated via software commands on a host PC. Non-real-time OS thread scheduling and USB/Ethernet buffer latencies introduce an unknown start skew $\tau_0 \in [0, 500]\text{ ms}$.
2. **Independent Crystal Oscillator Drift:** Quartz crystals drift by $\pm 20 - 50\text{ ppm}$. Over $120.0\text{ seconds}$, independent clock drift can produce a cumulative time discrepancy of:
   $$\Delta t_{\text{drift}} = 120\text{ s} \times 100 \times 10^{-6} \approx 12.0\text{ ms}$$
3. **Clinical Monitor Latency (+6.21 s):** Cross-correlation lag scans confirmed that the Mindray patient monitor's displayed `HR` stream lags instantaneous ECG R-peak ground truth by a mean of $+6.21\text{ seconds}$ (median $+7.0\text{ s}$). The monitor HR is permanently disqualified as ground truth.

---

## 4. Current Status & Mandatory Investigator Decisions Needed

- **Current Status:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` remains an active, unresolved scientific limitation.
- **Investigator Decision Required:** The principal investigator must formally review this limitation and elect one of two pathways:
  - **Option A (Halt for Additional Hardware Evidence):** Require physical trigger data or hardware synchronization evidence before permitting supervised model training.
  - **Option B (Proceed Conditionally under Bounded Scope):** Formally accept the nominal start-time alignment as a documented scientific constraint for 10-second windowed average HR estimation, with explicit publication caveats that micro-Doppler phase lock and PTT are unverified.
