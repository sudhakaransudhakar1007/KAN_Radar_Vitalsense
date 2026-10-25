# Phase 3 Synchronization Audit Record

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_002`  
**Execution Date:** October 15, 2026  
**Status:** `VERIFIED_WITH_DOCUMENTED_LIMITATIONS`  

---

## 1. Summary of Synchronization Findings

A comprehensive review of the Phase 2A and Phase 3 synchronization manifests across all 48 candidate radar/reference pairs confirmed the following physical and empirical properties:

```
+--------------------------------------------------------------------------------------------------+
|                            SYNCHRONIZATION EVIDENCE HIERARCHY                                    |
+--------------------------------------------------------------------------------------------------+
| Level 1: Hardware Sync Markers / PPS Triggers ─────────► ABSENT across all 96 MAT files          |
| Level 2: Shared Clock Digitizer Timestamps ───────────► ABSENT (Unverified Clock Drift)          |
| Level 3: Cross-Sensor Common Event Alignment ──────────► INCONCLUSIVE (Apnea respiratory drift)  |
| Level 4: Prespecified Nominal Alignment (t0 = 0.0 s) ──► ADOPTED OPERATIONAL ASSUMPTION          |
+--------------------------------------------------------------------------------------------------+
```

1. **Hardware Clock Status:** `UNVERIFIED`.
   - Inspection of all struct fields, variable headers, and channel arrays across all 96 MAT files confirmed the complete absence of physical hardware trigger channels, external TTL pulses, or Pulse-Per-Second (PPS) timestamps.
   - The radar digitizer and the Mindray physiological monitor operated on independent internal crystal oscillators without a shared master clock.

2. **Nominal Zero-Offset Timing Convention:**
   - The pipeline adopts a nominal alignment assumption ($t_0 = 0.0\text{ s}$ for both sensors).
   - This convention is an **operational assumption**, not measured or physical proof of zero-latency synchronization.
   - Any sub-second alignment is formally labeled `UNVERIFIED_HARDWARE_TIMING`.

3. **Duration Concordance & Discrepancy:**
   - **47 of 48 pairs** exhibit matching 120.0-second nominal durations:
     - Radar: 40,000 samples at $f_s = 333.3333\text{ Hz}$ ($40000 / 333.3333 = 120.000\text{ s}$).
     - ECG Lead II: 60,000 samples at $f_s = 500.0\text{ Hz}$ ($60000 / 500.0 = 120.000\text{ s}$).
     - Respiration: 30,720 samples at $f_s = 256.0\text{ Hz}$ ($30720 / 256.0 = 120.000\text{ s}$).
     - Monitor HR: 120 samples at $f_s = 1.0\text{ Hz}$ ($120 / 1.0 = 120.000\text{ s}$).
   - **1 pair (`VS24_Resting`) exhibits an empirical respiration duration discrepancy:**
     - The Mindray file `VS24_Resting_Mindray.mat` contains exactly 30,600 respiration samples (instead of 30,720 samples).
     - At the documented sampling rate of 256.0 Hz:
       $$\text{Duration} = \frac{30,600}{256.0} = 119.53125\text{ seconds}$$
     - This represents a discrepancy of **0.46875 seconds** (~120 samples at 256 Hz) shorter than the nominal 120.0-second recording duration.
     - The ECG array in `VS24_Resting_Mindray.mat` contains 60,000 samples (120.0 s).
     - Preprocessing routines must dynamically query array lengths and avoid assuming fixed 30,720 sample buffers.

4. **Prohibition of Fabricated Offsets:**
   - No arbitrary, post-hoc, or in-sample optimized cross-device shift $\tau$ is applied to force alignment.
   - The evaluation framework maintains the prespecified zero-shift baseline as the primary reference protocol.
