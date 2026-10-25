# PHASE 4C: GROUND-TRUTH CONSTRUCTION & SYNCHRONIZATION EVIDENCE REVIEW

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Verification Stage:** Phase 4C — Ground-Truth Derivation and Synchronization Taxonomy  
**Verification File:** `outputs/phase4/verification_run_001/ground_truth_and_sync_review.md`  

---

## 1. Trace of Ground-Truth Construction Pipeline

The ground truth heart-rate reference labels paired with radar windows in `accepted_window_manifest.csv` were traced from raw binary files through code execution:

```
Raw Mindray MAT (ecg_lead2, 60,000 samples @ 500 Hz)
  │
  ▼
[Missing Sample QC] ───────────────► In-memory linear interpolation for isolated single NaNs
  │                                    Boundary NaNs flagged -> Window rejected
  ▼
[Pan-Tompkins QRS Detector] ──────► 5-15 Hz bandpass -> Derivative -> Squaring -> 150 ms Moving Window
  │                                    Adaptive 90th-percentile threshold -> 250 ms refractory period
  ▼
[R-Peak Indices & Timestamps] ────► Local peak search ±100 ms -> R-peak timestamps t_peaks (s)
  │
  ▼
[RR Interval Extraction] ──────────► rr_intervals = diff(t_peaks)
  │                                    Physiological screening: 35 BPM (1.714 s) <= RR <= 185 BPM (0.324 s)
  ▼
[Window Midpoint Slicing] ─────────► Interval midpoint (t_i + t_{i+1})/2 mapped into [t_start, t_end]
  │
  ▼
[Window SQI Evaluation] ──────────► 1. Valid RR coverage >= 85% of 10.0 s window (>= 8.5 s)
  │                                    2. Maximum RR gap < 3.0 s
  ▼
[Reference HR Calculation] ────────► Harmonic Mean: HR_ref = 60.0 / mean(valid_RR)
                                       Arithmetic Mean: HR_arith = mean(60.0 / valid_RR)
```

### Detailed Evaluation of Code Mechanics:
1. **Mathematical Rigor of Harmonic Mean (`ref_hr_bpm`):**  
   In physiology, mean heart rate over a time interval $T$ with $K$ beat intervals $RR_k$ is the total beats divided by total time:
   $$\text{Mean HR} = \frac{K}{\sum_{k=1}^K RR_k} \times 60 = \frac{60}{\frac{1}{K} \sum_{k=1}^K RR_k} \equiv \frac{60}{\text{mean}(RR)}$$
   This is the **harmonic mean** of instantaneous heart rates. The code correctly computes this as primary target `ref_hr_bpm`, while also recording the arithmetic mean `ref_hr_arithmetic_bpm` for diagnostic transparency.
2. **Quality Screening Criteria (SQI):**  
   - Windows failing coverage ($<85\%$) are rejected (`RR_COVERAGE_BELOW_85_PCT`).
   - Windows with long pauses ($>3.0\text{ s}$) are rejected (`MAX_RR_GAP_EXCEEDED_3.0S`).
   - Corrupted ECG recordings (e.g., `VS10_Resting`) have 100% of windows rejected.
3. **Defensibility of Reference Targets:**  
   Every one of the 1,029 accepted windows has a verified, physiologically bounded, dense RR-interval trace with $>85\%$ coverage and no gap exceeding $3.0\text{ s}$.

---

## 2. Four-Tier Scientific Synchronization Taxonomy

A strict taxonomy of synchronization evidence was applied to eliminate ambiguity between physical proof and operational assumptions:

```
┌────────────────────────────────────────────────────────────────────────┐
│               FOUR-TIER SYNCHRONIZATION EVIDENCE AUDIT                 │
└────────────────────────────────────────────────────────────────────────┘
  │
  ├──► TIER 1: PHYSICALLY VERIFIED SYNCHRONIZATION:
  │    • Status: UNVERIFIED (0 of 96 MAT files contain trigger channels, PPS
  │      pulses, or hardware timestamp packets).
  │    • Both systems operated on independent internal quartz oscillators.
  │
  ├──► TIER 2: EMPIRICALLY ESTIMATED ALIGNMENT:
  │    • Status: PARTIALLY ESTIMATED & CONSTRAINED.
  │    • Monitor HR array has verified +6.21 s display lag (disqualified).
  │    • Cross-device 10 s cardiac FFT agreement observed at zero-shift
  │      (MAE = 2.97 BPM on Resting pairs in Phase 2A).
  │
  ├──► TIER 3: ASSUMED NOMINAL t0 ALIGNMENT:
  │    • Status: OPERATIONAL MODELING ASSUMPTION ONLY.
  │    • Radar sample 0 and ECG sample 0 are mapped to t = 0.0 s.
  │    • User-approved working convention for preflight and architecture
  │      exploration, tagged as UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0.
  │
  └──► TIER 4: UNKNOWN OR UNVERIFIED TIMING:
       • Status: ACKNOWLEDGED SCIENTIFIC UNCERTAINTY.
       • Sub-second latency jitter between operator manual triggers and
         drift between uncoupled oscillators over 120 s cannot be measured.
```

---

## 3. Ground-Truth Defensibility Verdict

**Is every accepted radar window time-aligned to a defensible reference target?**
- **YES, under the stated operational convention:**
  Within the context of the user-approved `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0` convention, every accepted window's target is derived from validated instantaneous ECG R-peaks using the mathematically exact harmonic mean formula.
- **NO hardware physical co-triggering is claimed:**
  The ground-truth targets are robust to sub-second shifts because 10-second cardiac interval averaging filters out small timing perturbations, but hardware synchronization remains an explicit unverified boundary condition for the study.
