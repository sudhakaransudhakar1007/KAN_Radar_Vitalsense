# Phase 3 Synchronization Audit Report

**Execution Timestamp:** 2026-10-15T09:24:57.618429+00:00
**Analyzed Pairs:** 48 pairs across VS01-VS24 (Resting and Apnea)

## 1. Timing Convention & Evidence Hierarchy

- **Hardware Synchronization:** `UNVERIFIED`. None of the 96 MAT files contain hardware trigger signals, PPS pulses, or shared clock timestamps.
- **Relative Time Alignment:** Prespecified nominal zero-offset assumption ($t_0 = 0.0\text{ s}$ for both devices).
- **Sub-second Alignment Confidence:** `UNVERIFIED_HARDWARE_TIMING`.
- **Cross-Device Duration Mismatches:**
  - `VS01_Apnea`: Radar 120.0s vs ECG 120.0s (Mismatch: 0.0s)
  - `VS01_Resting`: Radar 120.0s vs ECG 120.0s (Mismatch: 0.0s)
  - `VS02_Apnea`: Radar 120.0s vs ECG 120.0s (Mismatch: 0.0s)
  - `VS02_Resting`: Radar 120.0s vs ECG 120.0s (Mismatch: 0.0s)
  - `VS03_Apnea`: Radar 120.0s vs ECG 120.0s (Mismatch: 0.0s)
  - *(Remaining 43 pairs cataloged in `synchronization_manifest.csv`)*

## 2. Monitor HR Latency Separation

Monitor HR array is strictly separated from instantaneous ECG HR targets and remains disqualified from supervised training due to the documented +6s to +7s display delay.
