# Reference-Label & Window Pairing Audit

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Run ID:** `run_001`  
**Execution Date:** October 15, 2026  
**Status:** `VERIFIED_EVIDENCE_BASED`  

---

## 1. Reference Modality Hierarchy & Disqualification

In strict alignment with the evidence established in Phase 2A and Phase 3:

1. **Disqualification of Mindray Display HR (`HR` array, $f_s = 1.0\text{ Hz}$):**
   - Empirical lag analysis across all 48 pairs confirmed that the commercial monitor's displayed `HR` array lags physiological instantaneous ECG heart rate by $+6.21\text{ s}$ on average (median: $+7.0\text{ s}$, mode: $+7.0\text{ s}$).
   - Supervised training against this array would introduce catastrophic temporal label misalignment (lagging by 60–70% of a 10-second window).
   - **Verdict:** Strictly disqualified from serving as ground-truth training labels.

2. **Adoption of Instantaneous Lead II ECG Reference:**
   - Raw continuous ECG Lead II (`ecg_lead2`, $f_s = 500.0\text{ Hz}$) serves as the sole authoritative physical reference.
   - Ground-truth window HR labels are derived exclusively from validated QRS complexes detected via the standardized Pan-Tompkins algorithm on in-memory cleaned ECG.

---

## 2. In-Memory Delimiter NaN Handling

- **Observed Structure:** 47 of 48 Mindray reference files exhibit periodic single-sample NaNs in `ecg_lead2` spaced at nominal 1-second intervals (500 samples).
- **Protocol:** Single-sample internal delimiter NaNs are linearly interpolated in-memory strictly for QRS bandpass and derivative calculation. Zero raw MAT files are altered on disk.
- **Boundary Delimiter Finding (`VS10_Resting`):**
  - `VS10_Resting_Mindray.mat` contains a delimiter NaN at sample index `0` (`nan_indices = [0, 501, 1002, ..., 59619]`).
  - To prevent unverified extrapolation artifacts, leading boundary NaNs are flagged as un-interpolable. Consequently, `VS10_Resting` was excluded from QRS detection, and all 22 candidate windows were rejected with reason `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`.

---

## 3. Mathematical Formulation of Window Reference HR

For each candidate window $k \in \{0, 1, \dots, 21\}$ spanning nominal time $[t_{start}, t_{end}] = [k \cdot 5.0, k \cdot 5.0 + 10.0)\text{ seconds}$:

1. **RR Interval Identification:**
   Let $T_r = [t_1, t_2, \dots, t_M]$ be the set of Pan-Tompkins detected R-peak timestamps in seconds.
   The $i$-th RR interval is:
   $$RR_i = t_{i+1} - t_i \quad (\text{seconds})$$
   with interval midpoint:
   $$m_i = \frac{t_i + t_{i+1}}{2} \quad (\text{seconds})$$

2. **Window Interval Subset ($I_k$):**
   $$I_k = \{ i \in \{1, \dots, M-1\} : t_{start} \le m_i < t_{end} \}$$

3. **Physiological Validity Check:**
   Every interval $i \in I_k$ must satisfy:
   $$0.3243\text{ s} \le RR_i \le 1.7143\text{ s} \iff 35.0\text{ bpm} \le \frac{60.0}{RR_i} \le 185.0\text{ bpm}$$
   If any interval falls outside these bounds (e.g. premature ventricular contraction or artifact), the window is flagged as `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW`.

4. **Coverage & Gap Check:**
   - Total duration covered: $D_k = \sum_{i \in I_k} RR_i$.
   - Percentage coverage:
     $$\text{Coverage}(k) = \frac{D_k}{10.0\text{ s}} \times 100\% \ge 85.0\%$$
   - Maximum interval gap:
     $$\text{MaxGap}(k) = \max_{i \in I_k} RR_i < 3.0\text{ seconds}$$

5. **Reference Heart Rate Aggregation:**
   The primary reference label is computed as the standard harmonic mean heart rate:
   $$HR_{\text{ref}}(k) = \frac{60.0}{\frac{1}{|I_k|} \sum_{i \in I_k} RR_i} \quad (\text{BPM})$$
   The arithmetic mean of instantaneous rates $\frac{1}{|I_k|} \sum_{i \in I_k} \frac{60.0}{RR_i}$ is also cataloged in the manifest for comparison (mean absolute difference between harmonic and arithmetic definitions is $< 0.15\text{ bpm}$).

---

## 4. Window Pairing & Synchronization Assumptions

- **Pairing Rule:** Continuous phase-demodulated radar displacement over sample range $[k \cdot 1667, k \cdot 1667 + 3333)$ is paired with ECG interval $[k \cdot 5.0, k \cdot 5.0 + 10.0)\text{ seconds}$.
- **Timing Baseline:** Nominal zero-offset assumption ($t_0 = 0.0\text{ s}$).
- **Scientific Limitation:** No physical hardware trigger exists between the 120-GHz radar digitizer and the Mindray physiological monitor. This pairing represents an operational convention, not verified sub-second hardware synchronization.
