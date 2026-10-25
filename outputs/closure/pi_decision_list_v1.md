# Principal Investigator (PI) Decision List — Phase 2A / Phase 3 Transition

This document itemizes the eight critical technical, governance, and methodological decisions required by the Principal Investigator before the Phase 2A Finalization Gate can be formally closed and before supervised dataset generation or model training may proceed.

All decisions are presented with their technical options, empirical consequences, and supporting evidence files. Every decision field is deliberately left blank pending explicit PI sign-off.

---

## Decision D1: Window Slicing Rule & Discretization Formula
- **Context & Question:** Whether to generate candidate radar/ECG windows using the exact continuous-time formula ($t_{\text{start}} = \text{round}(k \times 5.0, 3)$, yielding exactly 23 windows per recording / 1,104 total) or retain the legacy integer-hop rule (`start_idx += 1667`, yielding 22 windows per recording / 1,056 total).
- **Options:**
  - **Option A (Recommended):** Exact continuous-time windowing ($23\text{ windows/recording}$, $1,104\text{ total}$). Captures $100.0\text{ s}$ to $120.0\text{ s}$ with zero trailing sample loss.
  - **Option B:** Legacy integer-hop accumulation ($22\text{ windows/recording}$, $1,056\text{ total}$). Discards trailing $4.98\text{ s}$ ($1,660\text{ radar samples}$) per recording due to $+0.333\text{ sample}$ discretization drift over 22 hops.
- **Consequences:** Option A increases dataset size by 48 windows ($+4.5\%$) and eliminates arbitrary tail truncation. Option B preserves exact backward compatibility with `run_001`.
- **Evidence File:** [`outputs/closure/window_indexing_j3.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/window_indexing_j3.py), Section 3 of `outputs/closure/stage2h_notes.md`.
- **Decision: ___________option A_________**

---

## Decision D2: Canonical Ground-Truth Heart-Rate Definition
- **Context & Question:** Whether ground-truth window heart rate is formally defined as the harmonic mean ($60.0 / \overline{RR}$) or arithmetic mean ($\overline{60.0 / RR}$) of valid RR intervals whose midpoints fall in the window.
- **Options:**
  - **Option A (Harmonic Mean):** $HR = 60.0 / \overline{RR}$. Represents true average beat frequency over the window duration ($\frac{N}{\sum RR}$).
  - **Option B (Arithmetic Mean):** $HR = \frac{1}{N} \sum (60.0 / RR_i)$. Represents the average of instantaneous heart rates.
- **Consequences:** Across all 1,029 accepted windows in the dataset, the mean absolute difference between harmonic and arithmetic definitions is $0.0527\text{ bpm}$ (max difference: $0.82\text{ bpm}$). Selecting either provides mathematical clarity for loss computation.
- **Evidence File:** [`outputs/closure/s1_window_hr_comparison.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/s1_window_hr_comparison.csv), [`src/phase3/supervised_dataset_generator.py:136-138`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L136-L138).
- **Decision: ________Harmonic HR____________**

---

## Decision D3: Status & Disposition of Existing `run_001` Manifests
- **Context & Question:** What formal status and storage policy to apply to the preliminary `run_001` manifests under `outputs/supervised_dataset/run_001/`.
- **Options:**
  - **Option A (Recommended):** Formally designate `run_001` as `SUPERSEDED_UNAPPROVED` diagnostic archives; retain files untouched for provenance audit trail; generate canonical dataset under `outputs/supervised_dataset/run_002/`.
  - **Option B:** Permanently archive and compress `run_001` into a cold-storage tarball before generating `run_002`.
- **Consequences:** Option A maintains full cryptographic reproducibility of past trajectory steps while strictly preventing unapproved arrays from entering model training.
- **Evidence File:** [`outputs/closure/run_001_status_note.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_001_status_note.md).
- **Decision: __________Option A__________**

---

## Decision D4: Formal Limitation Regarding Hardware Clock Synchronization
- **Context & Question:** How to formally specify hardware timing synchronization in dataset documentation and academic publications.
- **Options:**
  - **Option A (Recommended):** Formally classify hardware timing as `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`. State explicitly in all publications that radar and reference digitizers were started approximately simultaneously without a common hardware clock, pulse-per-second (PPS) trigger, or unified digitizer timestamps.
  - **Option B:** Re-acquire dataset using synchronized laboratory clock triggers before proceeding.
- **Consequences:** Option A permits rigorous, scientifically honest research publication with defensible limitations. Option B halts the computational project pending clinical hardware laboratory access.
- **Evidence File:** [`outputs/closure/stage2h_notes.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/stage2h_notes.md), Section 21.1 and Section 22 of `outputs/phase2a/step2b_consistency_audit.md`.
- **Decision: _________Option A___________**

---

## Decision D5: Canonical Respiratory Cross-Correlation Reporting Standards
- **Context & Question:** Which methodology to adopt as canonical for reporting respiratory synchronization across the 48 recordings.
- **Options:**
  - **Option A (Recommended):** Report demeaned normalized cross-correlation with explicit disclosure of the wide correlation plateau (median width $95.0\text{ ms}$, range $34.5\text{ to }1,594.0\text{ ms}$ where $r \ge r_{\text{peak}} - 0.001$), reporting authors' raw method as a literature replication baseline.
  - **Option B:** Exclusively report authors' raw un-demeaned MATLAB cross-correlation values.
- **Consequences:** Option A prevents misleading claims of sub-sample or microsecond physical synchronization and explains the 28 non-matching lags as DC offset artifacts.
- **Evidence File:** [`outputs/closure/respiratory_2x2_ablation.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/respiratory_2x2_ablation.csv), [`outputs/closure/respiratory_robustness_k3.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/respiratory_robustness_k3.csv).
- **Decision: ___________Option A_________**

---

## Decision D6: Inclusion & Preprocessing of Recording `VS10_Resting`
- **Context & Question:** Whether to include `VS10_Resting` in the supervised dataset using Stage 2 nearest-neighbor boundary fill or exclude it based on pre-Stage-2 strict boundary rejection.
- **Options:**
  - **Option A (Recommended):** Include `VS10_Resting` using Stage 2 `clean_ecg_nans` nearest-neighbor fill for the single boundary NaN at index 0 (recovers 156 valid beats, $100\%$ match with Pan-Tompkins).
  - **Option B:** Exclude `VS10_Resting` entirely from supervised dataset generation.
- **Consequences:** Option A preserves subject diversity (Subject 10 has no resting windows in `run_001`) and recovers 22/23 valid windows without signal distortion. Option B discards a viable subject recording.
- **Evidence File:** [`outputs/closure/run_k1_k2.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/run_k1_k2.py), ISS-24 in `step2b_issue_register.csv`.
- **Decision: ________option A____________**

---

## Decision D7: Canonical ECG Detector & Window Quality Gate Harmonization
- **Context & Question:** Which ECG detector and window quality gating standard to establish as canonical across the codebase.
- **Options:**
  - **Option A (Recommended):** Adopt `sync_validation` detector (`detect_r_peaks` with `np.abs(ecg_filt)` refinement), which correctly resolves inverted Lead II polarity (`VS19`), combined with $> 80\%$ valid RR coverage gate.
  - **Option B:** Adopt Phase 3 detector (`detect_r_peaks_pan_tompkins` with positive peak refinement) with $> 85\%$ coverage gate and strict any-outlier rejection.
- **Consequences:** Option A resolves the $44\text{ ms}$ polarity offset in `VS19` while maintaining $100\%$ peak agreement on all 47 other recordings; Option B preserves Phase 3 code unchanged but requires polarity inversion handling for `VS19`.
- **Evidence File:** [`outputs/closure/s1_recording_peak_comparison.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/s1_recording_peak_comparison.csv), [`outputs/closure/s1_window_hr_comparison.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/s1_window_hr_comparison.csv).
- **Decision: ____________________**

---

## Decision D8: Regeneration of Official `outputs/phase2a/` Artifacts
- **Context & Question:** Whether to regenerate official `outputs/phase2a/sync_validation_results.csv` after implementing fixed PRNG seeding in `cardiac_surrogate_mae`, or preserve `outputs/phase2a/` as an immutable audit record and maintain updated tables in `outputs/closure/`.
- **Options:**
  - **Option A (Recommended):** Preserve `outputs/phase2a/` as an immutable audit baseline of the initial Phase 2A state; maintain all corrected, decoupled, and seeded results under `outputs/closure/` (`v2/` and `v3/`).
  - **Option B:** Overwrite `outputs/phase2a/sync_validation_results.csv` and report with final seeded decoupled results upon formal gate closure.
- **Consequences:** Option A ensures 100% cryptographic reproducibility of the original audit findings; Option B consolidates final state in `outputs/phase2a/`.
- **Evidence File:** [`outputs/phase2a/step2b_issue_register.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase2a/step2b_issue_register.csv) (ISS-23), [`outputs/closure/v2/sync_validation_results.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/v2/sync_validation_results.csv).
- **Decision: ___________Option A_________**
