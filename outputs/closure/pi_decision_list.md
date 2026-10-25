# Principal Investigator (PI) Decision List — Phase 2A / Phase 3 Transition

This document itemizes the thirteen critical technical, governance, and methodological decisions required from the Principal Investigator before the Phase 2A Finalization Gate can be formally closed and before supervised dataset generation or model training may proceed.

> [!IMPORTANT]
> **Methodological Pre-Specification Requirement:**
> None of the thresholds, outlier cutoffs, coverage percentages, or algorithmic choices listed below is prespecified in a registered clinical study protocol or independently validated on an external test cohort. Under strict scientific governance, all thirteen decisions **must be formally resolved and fixed prior to observing any machine learning training or validation results**, in order to eliminate post-hoc tuning bias and ensure scientific integrity.

All decisions are presented below with their technical options, empirical data from Stage 2/Stage 5 analyses, consequences, and supporting evidence files. Every decision field is deliberately left blank pending explicit PI sign-off.

---

## Decision D1: Window Slicing Rule & Discretization Formula
- **Context & Question:** Whether to generate candidate radar/ECG windows using the exact continuous-time formula ($t_{\text{start}} = \text{round}(k \times 5.0, 3)$, yielding exactly 23 windows per recording / 1,104 total) or retain the legacy integer-hop rule (`start_idx += 1667`, yielding 22 windows per recording / 1,056 total).
- **Options:**
  - **Option A (Recommended):** Exact continuous-time windowing ($23\text{ windows/recording}$, $1,104\text{ total candidate windows}$). Captures the window from $100.0\text{ s}$ to $120.0\text{ s}$ with zero trailing sample loss.
  - **Option B:** Legacy integer-hop accumulation ($22\text{ windows/recording}$, $1,056\text{ total candidate windows}$). Discards trailing $4.98\text{ s}$ ($1,660\text{ radar samples}$) per recording due to $+0.333\text{ sample}$ discretization drift over 22 hops.
- **Empirical Numbers:** Exact formula adds 48 viable 10-second windows ($+4.5\%$ dataset yield across all 48 recordings).
- **Consequences:** Option A maximizes valid training yield and eliminates arbitrary tail truncation. Option B preserves exact backward compatibility with preliminary `run_001` manifests.
- **Evidence File:** [`outputs/closure/window_indexing_j3.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_indexing_j3.py), Section 3 of [`outputs/closure/stage2h_notes.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/stage2h_notes.md).
- **Decision: _________Option A___________**

---

## Decision D2a: Ground-Truth Label Reference Source
- **Context & Question:** Whether ground-truth target heart rate is derived strictly from continuous ECG R-peak intervals at nominal zero shift ($\tau = 0\text{ s}$) or whether Mindray monitor HR can be used.
- **Options:**
  - **Option A (Recommended):** Derive ground truth exclusively from continuous ECG Lead II R-peak intervals at nominal zero shift ($\tau = 0\text{ s}$).
  - **Option B:** Allow use of Mindray patient monitor numerical HR.
- **Empirical Numbers:** Cross-correlation and lag analysis across all 48 recordings (ISS-06) established that the Mindray monitor HR exhibits an empirical latency of $+6.0\text{ s}$ to $+7.0\text{ s}$ relative to real-time ECG, with severe internal moving-average filtering.
- **Consequences:** Option A guarantees instantaneous physiological ground truth. Option B is scientifically prohibited because monitor latency would contaminate 10-second window targets with delayed historical heart rates.
- **Evidence File:** [`src/sync_validation/runner.py:132`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L132), Section 12 of [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md).
- **Decision: _________Option A___________**

---

## Decision D2b: Canonical Window Ground-Truth Heart-Rate Definition
- **Context & Question:** Whether window ground-truth heart rate is formally calculated as the harmonic mean ($60.0 / \overline{RR}$) or arithmetic mean ($\overline{60.0 / RR_i}$) of valid RR intervals falling within the window.
- **Options:**
  - **Option A (Harmonic Mean):** $HR = 60.0 / \overline{RR}$. Reflects true mean beat frequency over the elapsed window duration ($N / \sum RR_i$).
  - **Option B (Arithmetic Mean):** $HR = \frac{1}{N} \sum (60.0 / RR_i)$. Reflects average instantaneous heart rate.
- **Empirical Numbers:** Across all 1,029 accepted windows in the dataset (manifest `outputs/supervised_dataset/run_001/accepted_window_manifest.csv`), the mean absolute difference between harmonic and arithmetic definitions is $0.1474\text{ bpm}$ (maximum absolute difference: $2.9400\text{ bpm}$ in `VS15_Resting` window 18). In-memory recomputation across all 1,104 continuous-time candidate windows yields mean absolute difference $0.1441\text{ bpm}$ and maximum absolute difference $2.9400\text{ bpm}$ (also in `VS15_Resting` window 18). (Evidence: `outputs/closure/stage6c_r1_analysis.py`).
- **Consequences:** Option A is standard in physiological cardiology and mathematically preserves duration-weighted rate; Option B gives equal weight to short ectopic intervals. Setting a single canonical standard prevents ambiguity in loss computation.
- **Evidence File:** [`outputs/closure/s1_window_hr_comparison.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/s1_window_hr_comparison.csv), [`src/phase3/supervised_dataset_generator.py:136-138`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L136-L138).
- **Decision: __________Option A__________**

---

## Decision D3: Status & Disposition of Existing `run_001` Manifests
- **Context & Question:** What formal governance status and retention policy to apply to the preliminary `run_001` manifests under `outputs/supervised_dataset/run_001/`.
- **Options:**
  - **Option A (Recommended):** Formally designate `run_001` as `SUPERSEDED_UNAPPROVED` diagnostic archives; retain files untouched for provenance audit trail; generate canonical dataset under `outputs/supervised_dataset/run_002/`.
  - **Option B:** Permanently archive and compress `run_001` into a cold-storage tarball before generating `run_002/`.
- **Empirical Numbers:** `run_001` contains 1,029 accepted windows generated on 2026-10-15 prior to Phase 2A audit, using the legacy 22-window integer hop, pre-Stage-2 boundary cleaning (excluding all 22 windows of `VS10_Resting`), and un-harmonized detector logic.
- **Consequences:** Option A maintains full cryptographic reproducibility of past trajectory steps while strictly preventing unapproved arrays from entering model training.
- **Evidence File:** [`outputs/closure/run_001_status_note.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_001_status_note.md).
- **Decision: __________Option A__________**

---

## Decision D4: Formal Limitation Regarding Hardware Clock Synchronization
- **Context & Question:** How to formally specify hardware digitizer timing synchronization in dataset documentation and academic publications.
- **Options:**
  - **Option A (Recommended):** Formally adopt limitation `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. State explicitly in all publications that radar and reference digitizers have no common hardware clock, pulse-per-second (PPS) trigger, or shared microsecond digitizer timestamp; nominal alignment at $t_0 = 0\text{ s}$ is an unverified operational assumption.
  - **Option B:** Halt project until hardware re-acquisition with external trigger generator can be performed.
- **Empirical Numbers:** Inspection of all 96 raw `.mat` files and acquisition scripts confirms total absence of trigger lines, hardware clock headers, or microsecond timing metadata.
- **Consequences:** Option A permits rigorous, scientifically honest research publication with defensible limitations. Option B halts the computational project pending clinical hardware laboratory access.
- **Evidence File:** [`outputs/closure/stage2h_notes.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/stage2h_notes.md), Section 21.1 and Section 22 of [`outputs/phase2a/step2b_consistency_audit.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_consistency_audit.md).
- **Decision: ________Option A____________**

---

## Decision D5: Canonical Respiratory Cross-Correlation Reporting Standards
- **Context & Question:** Which methodology to adopt as canonical for reporting respiratory synchronization across the 48 recordings.
- **Options:**
  - **Option A (Recommended):** Report demeaned normalized cross-correlation with explicit disclosure of the wide correlation plateau (median width $95.0\text{ ms}$, range $34.5\text{ to }1,594.0\text{ ms}$ where $r \ge r_{\text{peak}} - 0.001$), reporting authors' raw method as a literature replication baseline. Demeaning changes the argmax lag in 27 of 28 recordings; mechanism NOT_ESTABLISHED (K3: rho = -0.1254, p = 0.3956; plateau median 95 ms).
  - **Option B:** Exclusively report authors' raw un-demeaned MATLAB cross-correlation values.
- **Empirical Numbers:** Demeaning changes the discrete argmax lag in 27 of 28 non-matching recordings. In Stage 2K (K3), correlation between mean product ($r_{\text{dc}}$) and lag shift was statistically non-significant ($\rho = -0.1254, p = 0.3956$). Plateau median width is $95.0\text{ ms}$.
- **Consequences:** Option A prevents misleading claims of sub-sample or microsecond physical synchronization and accurately reflects physiological signal uncertainty. Under Option B, the discrete argmax lag shift between demeaned and raw cross-correlation has no verified physical mechanism (the DC-product hypothesis is not supported: Spearman rho = -0.1254, p = 0.3956; physical mechanism NOT_ESTABLISHED per Stage 2K K3 in `outputs/closure/respiratory_robustness_k3.csv`).
- **Evidence File:** [`outputs/closure/respiratory_2x2_ablation.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/respiratory_2x2_ablation.csv), [`outputs/closure/respiratory_robustness_k3.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/respiratory_robustness_k3.csv).
- **Decision: __________Option A_________**

---

## Decision D6: Inclusion & Preprocessing of Recording `VS10_Resting`
- **Context & Question:** Whether to include `VS10_Resting` in the supervised dataset using Stage 2 nearest-neighbor boundary fill or exclude it based on pre-Stage-2 strict boundary rejection.
- **Options:**
  - **Option A (Recommended):** Include `VS10_Resting` using Stage 2 `clean_ecg_nans` nearest-neighbor fill for the single boundary NaN at index 0 (recovers 156 valid beats, $100\%$ match with Pan-Tompkins).
  - **Option B:** Exclude `VS10_Resting` entirely from supervised dataset generation.
- **Empirical Numbers:** `VS10_Resting` has exactly 1 NaN at index 0 out of 60,000 samples ($0.0017\%$). Stage 2 fill recovers 22 valid 10s windows (or 23 under D1). Excluding it leaves Subject 10 with 0 resting windows.
- **Consequences:** Option A preserves subject diversity and recovers 22/23 valid windows without signal distortion. Option B discards a viable subject recording.
- **Evidence File:** [`outputs/closure/run_k1_k2.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_k1_k2.py), ISS-24 in [`outputs/phase2a/step2b_issue_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_issue_register.csv).
- **Decision: _________Option A___________**

---

## Decision D7a: ECG Detector Fiducial Refinement Logic
- **Context & Question:** Whether local R-peak fiducial refinement on bandpass-filtered ECG searches for the positive maximum ($\text{argmax}(\text{filtered})$) or the maximum absolute amplitude ($\text{argmax}(|\text{filtered}|)$).
- **Options:**
  - **Option A (Recommended):** $\text{argmax}(|\text{filtered}|)$ (as in `sync_validation.detect_r_peaks`). Polarity-invariant; accurately identifies the dominant QRS deflection regardless of lead orientation.
  - **Option B:** $\text{argmax}(\text{filtered})$ (as in `phase3.detect_r_peaks_pan_tompkins`). Assumes upright positive R-waves; requires explicit lead-inversion detection.
- **Empirical Numbers (from B5a):** Evaluated across all 48 recordings. On 44 recordings, both detectors yield identical peak timestamps ($100\%$ match within $20\text{ ms}$). On `VS16` (both Apnea and Resting), the legacy detector detects an extra false peak producing non-physiological $RR < 0.343\text{ s}$ ($0.270\text{ s}$ and $0.274\text{ s}$). On `VS19` (both Apnea and Resting), Lead II exhibits inverted negative QRS polarity: Option B locks onto a minor positive side-lobe (+224.9/+231.8 raw amplitude), while Option A correctly identifies the true deep negative QRS deflection (-349.4/-358.5 bandpassed, -820 raw amplitude), resolving an empirical $44.0\text{ ms}$ fiducial shift ($0\%$ match within $20\text{ ms}$). (Evidence: `outputs/closure/stage6c_r4_audit.py:127-195`).
- **Consequences:** Option A provides robust, automated handling of inverted ECG leads without manual polarity configuration. Option B causes systematic timing errors on inverted-polarity subjects.
- **Evidence File:** [`outputs/closure/run_b5_analysis.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_b5_analysis.py), [`outputs/closure/s1_recording_peak_comparison.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/s1_recording_peak_comparison.csv).
- **Decision: ________Option A____________**

---

## Decision D7b: Physiological RR Interval Validity Range
- **Context & Question:** Which physiological heart-rate range to enforce when validating RR intervals for ground-truth calculation.
- **Options:**
  - **Option A:** $35\text{ to }185\text{ bpm}$ ($0.324\text{ s} \le RR \le 1.714\text{ s}$, current Phase 3 rule).
  - **Option B:** $30\text{ to }200\text{ bpm}$ ($0.300\text{ s} \le RR \le 2.000\text{ s}$, broad clinical gate rule).
  - **Option C:** $35\text{ to }175\text{ bpm}$ ($0.343\text{ s} \le RR \le 1.714\text{ s}$, current `sync_validation` rule).
- **Empirical Numbers:** In `VS16` (Apnea windows 4, 5 and Resting windows 0, 1), an isolated false double-peak detection error produced $RR = 0.270\text{ s}$ ($222.2\text{ bpm}$) and $0.274\text{ s}$ ($219.0\text{ bpm}$), which is correctly flagged as non-physiological under all three options.
- **Consequences:** Thresholds must be formally harmonized across all scripts so that quality gating in `sync_validation` exactly mirrors dataset filtering in `phase3`.
- **Evidence File:** [`src/phase3/ecg_reference.py:38-39`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L38-L39), [`src/sync_validation/ecg_processor.py:25`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L25).
- **Decision: _________Option A___________**

---

## Decision D7c: Interval-to-Window Temporal Assignment Rule
- **Context & Question:** Which geometric criterion determines whether an RR interval belongs to a given 10-second window $[t_{\text{start}}, t_{\text{end}})$.
- **Options:**
  - **Option A (Recommended):** RR interval midpoint in window ($(t_1 + t_2) / 2 \in [t_{\text{start}}, t_{\text{end}})$).
  - **Option B:** Second R-peak in window ($t_2 \in [t_{\text{start}}, t_{\text{end}})$).
- **Empirical Numbers (from B5b):** S1 reported 48 windows with $|\Delta HR| > 1.0\text{ bpm}$ between Phase 3 and `sync_validation` because Phase 3 used midpoint while `sync_validation` used second peak (representing $4.57\%$ of 1,051 valid paired windows in `s1_window_hr_comparison.csv`, $4.55\%$ of 1,056 `run_001` candidate windows, or $4.35\%$ of 1,104 continuous-time candidate windows). Counterfactual harmonization in B5b proves that aligning this rule drops windows with $|\Delta HR| > 1.0\text{ bpm}$ from 48 down to just 4 ($0.38\%$), and mean absolute difference drops from $0.2715\text{ bpm}$ to $0.0225\text{ bpm}$. (Evidence: `outputs/closure/stage6c_r2_analysis.py`).
- **Consequences:** Option A centers interval weight symmetrically inside the window and minimizes boundary edge effects.
- **Evidence File:** [`outputs/closure/run_b5_analysis.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_b5_analysis.py), [`src/phase3/supervised_dataset_generator.py:250-256`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L250-L256).
- **Decision: __________Option A__________**

---

## Decision D7d: Outlier Rejection Rule for Window Acceptance
- **Context & Question:** Whether a 10-second window containing an isolated non-physiological RR interval should be entirely rejected or whether the window may be retained based on valid beat coverage.
- **Options:**
  - **Option A:** Strict all-or-nothing rejection: reject the window if ANY non-physiological RR interval midpoint falls inside it (Phase 3 current rule).
  - **Option B (Recommended):** Coverage-based rejection: exclude the invalid interval from the valid RR duration numerator, but accept the window if remaining valid RR coverage exceeds the required threshold (e.g., $\ge 80\%$).
- **Empirical Numbers (from B5c):** In `VS16_Apnea` (windows 4, 5) and `VS16_Resting` (windows 0, 1), an isolated false double-peak detection error ($0.270\text{ s} + 0.724\text{ s} = 0.994\text{ s}$; $0.274\text{ s} + 0.640\text{ s} = 0.914\text{ s}$) causes Option A to reject 4 entire windows, even though the remaining 10 beats in each window are normal physiological beats with valid coverage $> 85\%$.
- **Consequences:** Option A guards strictly against corrupted HR targets at the expense of discarding otherwise viable windows. Option B salvages 4 windows without distorting the mean heart rate.
- **Evidence File:** [`outputs/closure/run_b5_analysis.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_b5_analysis.py), [`outputs/supervised_dataset/run_001/rejected_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/rejected_window_manifest.csv).
- **Decision: _________Option A___________**

---

## Decision D7e: Window Beat Coverage Threshold
- **Context & Question:** What minimum cumulative valid RR interval duration (coverage percentage of the 10-second window) is required to accept a window.
- **Options:**
  - **Option A:** $85\%$ coverage threshold ($8.5\text{ s}$ of valid RR intervals, current Phase 3 rule).
  - **Option B:** $80\%$ coverage threshold ($8.0\text{ s}$ of valid RR intervals, current `sync_validation` rule).
- **Empirical Numbers (from B5c):** `VS03_Resting` window 0 ([0.0s - 10.0s]) has a valid cumulative RR duration of $8.496\text{ s}$ ($84.96\%$ coverage) due to a $1.106\text{ s}$ lead-in before the first detected beat. All 8 beats in the window are regular (54.4 to 59.6 bpm). Under Option A, it is rejected for missing the cutoff by $0.04\%$; under Option B, it is accepted.
- **Consequences:** Option A enforces a conservative threshold; Option B recovers edge windows where initial lead-in slightly delays the first beat.
- **Evidence File:** [`outputs/closure/run_b5_analysis.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_b5_analysis.py), [`src/phase3/supervised_dataset_generator.py:46`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L46).
- **Decision: _________Option B ___________**

---

## Decision D8: Regeneration of Official `outputs/phase2a/` Artifacts
- **Context & Question:** Whether to regenerate official `outputs/phase2a/sync_validation_results.csv` after implementing fixed PRNG seeding in `cardiac_surrogate_mae`, or preserve `outputs/phase2a/` as an immutable audit record and maintain updated tables in `outputs/closure/`.
- **Options:**
  - **Option A (Recommended):** Preserve `outputs/phase2a/` as an immutable audit baseline of the initial Phase 2A state; maintain all corrected, decoupled, and seeded results under `outputs/closure/` (`v2/` and `v3/`).
  - **Option B:** Overwrite `outputs/phase2a/sync_validation_results.csv` and report with final seeded decoupled results upon formal gate closure.
- **Empirical Numbers:** `outputs/phase2a/sync_validation_results.csv` currently contains unseeded surrogate MAE results and coupled monitor latency status. Updated results with fixed seed 42 and decoupled statuses are preserved in `outputs/closure/v2/sync_validation_results.csv` and `outputs/closure/sync_status_decoupled_v3.csv`.
- **Consequences:** Option A guarantees 100% cryptographic reproducibility of the original Phase 2A audit trajectory. Option B consolidates final outputs into the canonical phase directory.
- **Evidence File:** [`outputs/phase2a/step2b_issue_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_issue_register.csv) (ISS-23), [`outputs/closure/v2/sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/v2/sync_validation_results.csv).
- **Decision: ________Option A____________**

D9: Recording-level ECG SQI amplitude stability.
Options: A) Amplitude stability is not assessed; recording SQI uses coverage > 85 % of 120 s and max RR gap < 3.0 s only; verdict is SQI_PARTIAL, never PASS, and all reports state "amplitude stability not assessed". B) Prespecify an amplitude-stability threshold now, before any training result is seen (the threshold and its provenance must be written down and marked UNVERIFIED_PROVENANCE).
Evidence: audit Section 18 (amplitude stability UNSPECIFIED / NOT VALIDATED), sync_status_decoupled_v3.csv (SQI_PARTIAL x48).
Decision: __________Option A___________

D10: Definition of "10 s window adequacy".
Options: A) Descriptive only: report radar-vs-ECG window MAE with confidence intervals and the baselines (LOSO constant-mean 5.82 bpm; zero-shift spectral parabolic 2.8977 bpm [recomputed in outputs/closure/stage6c_r6_compute.py]), no numeric gate. B) Prespecify a numeric MAE gate now, before any training result is seen.
Evidence: Stage 5 S2 baselines, window_coverage_gate_diagnostic.csv (1,104/1,104 windows pass).
Decision: ___________Option A_________

---

## Decision D13: Window-Level Maximum RR Gap Rule (3.0 s)
- **Context & Question:** Whether to retain the window-level rule rejecting windows with maximum RR gap $\ge 3.0\text{ s}$ (`supervised_dataset_generator.py:98,213`), drop the rule, or change the threshold.
- **Options:**
  - **Option A:** Keep the window-level max-gap threshold at $3.0\text{ s}$ (strict consistency with recording-level SQI gap rule).
  - **Option B:** Drop the window-level max-gap threshold and rely exclusively on cumulative valid RR duration coverage ($\ge 80\%$).
  - **Option C:** Change the window-level max-gap threshold to a prespecified physiological limit (e.g., $4.0\text{ s}$).
- **Consequences:** Option A guards against undetected beat dropouts or bradycardia episodes distorting window harmonic mean HR. Option B avoids redundant filtering when coverage is already high. Option C provides intermediate filtering.
- **Evidence File:** [`src/phase3/supervised_dataset_generator.py:98,213`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L98), [`outputs/closure/spec_gap_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec_gap_register.csv).
- **Decision: ____________________**

---

## Decision D14: Minimum Valid Beats Per Recording (20 Beats)
- **Context & Question:** Whether to retain the recording-level SQI requirement of at least 20 valid RR beats (`ecg_reference.py:283`), drop the rule, or adjust the beat threshold.
- **Options:**
  - **Option A:** Keep the minimum valid beat threshold of 20 beats per 120 s recording.
  - **Option B:** Drop the beat count threshold and rely exclusively on cumulative valid RR coverage $> 85\%$ of 120 s.
  - **Option C:** Increase or decrease the minimum beat threshold.
- **Consequences:** Option A ensures adequate sample size for recording-level SQI evaluation. Option B simplifies rules by tying gating strictly to time duration.
- **Evidence File:** [`src/phase3/ecg_reference.py:283`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/ecg_reference.py#L283), [`outputs/closure/spec_gap_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/spec_gap_register.csv).
- **Decision: ____________________**

---

## Decision D15: Pipeline Runner Default `output_dir` Guard
- **Context & Question:** Whether to apply the proposed code patch in `outputs/closure/proposed_runner_guard.diff` requiring explicit `output_dir` in `src/sync_validation/runner.py`, or maintain operational documentation only.
- **Options:**
  - **Option A:** Apply the code patch in `proposed_runner_guard.diff` so that omitting `output_dir` raises `ValueError` and writing to `outputs/phase2a` requires an explicit override flag.
  - **Option B:** Maintain operational documentation only (`runner_output_dir_rule.md`) without modifying `src/sync_validation/runner.py`.
- **Consequences:** Option A provides hard programmatic protection against accidental overwrites of `outputs/phase2a/`. Option B preserves existing code signatures at the cost of requiring procedural developer compliance.
- **Evidence File:** [`outputs/closure/proposed_runner_guard.diff`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/proposed_runner_guard.diff), [`outputs/closure/runner_output_dir_rule.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/runner_output_dir_rule.md).
- **Decision: ____________________**

