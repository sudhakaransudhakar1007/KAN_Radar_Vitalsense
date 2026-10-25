# Status Note — Supervised Dataset `run_001` Manifests

## 1. Executive Summary & Status
- **Status:** **`UNAPPROVED`**, **`SUPERSEDED`**, **`NOT FOR TRAINING`** pending investigator decision.
- **Physical State:** The `run_001` files are retained in-place under `outputs/supervised_dataset/run_001/` and are **neither moved nor modified**, preserving strict cryptographic and provenance integrity.
- **Prohibition:** These manifests must NOT be used for model training, feature extraction, supervised array generation, or LOSO evaluation.

---

## 2. Provenance & Generation Context
1. **Creation Timestamp:** Generated on **2026-10-15T15:13:06Z** prior to the formal Phase 2A Finalization Gate decision.
2. **Window Indexing Rule:** Produced using the cumulative integer-hop rule (`hop_samples = int(round(5.0 * 333.3333333333333)) = 1667`, `win_samples = 3333`), which accumulates discretization drift and yields **22 candidate windows per recording** ($1,056$ total) rather than the mathematically complete **23 windows** ($1,104$ total) achieved under the exact continuous-time formula.
3. **Pre-Stage-2 ECG Cleaning:** Sourced from pre-Stage-2 ECG missing-sample handling in `src/phase3/ecg_reference.py:101-116`, where any boundary/delimiter NaN (specifically the index-0 NaN in `VS10_Resting`) resulted in rejection of the entire recording (`ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN`), whereas Stage 2 boundary-fill logic cleanly recovers all 156 beats in that recording.
4. **Presence of Reference Labels:** All three manifests contain reference-HR label columns derived from reference ECG R-peaks at nominal $t_0 = 0\text{ s}$ zero shift (`reference_hr_bpm`, `reference_hr_arithmetic_bpm`, `valid_rr_count`, `rr_coverage_pct`, `max_rr_gap_s`).

---

## 3. Cryptographic Manifest Inventory
The three `run_001` manifests under `outputs/supervised_dataset/run_001/` possess the following cryptographic and structural properties:

| Manifest Path | SHA-256 | Size (bytes) | Row Count |
| :--- | :--- | :--- | :--- |
| `outputs/supervised_dataset/run_001/candidate_window_manifest.csv` | `4deb6fab9d77df91474f1d6e7faa5e5d9304500457f3c4a0e8cdde0ac2cb1d8e` | 275,518 | 1,056 |
| `outputs/supervised_dataset/run_001/accepted_window_manifest.csv` | `cbe9358b2e649b4b8ca81d70f7863d418e07cec7cc9d91abb04145963e987e51` | 267,622 | 1,029 |
| `outputs/supervised_dataset/run_001/rejected_window_manifest.csv` | `bafa101219e735d82ffb577a4c6e4342e32d1fedfe2673e81215596e7ff7512e` | 8,208 | 27 |

---

## 4. Governance Decision Required
Formal adoption or re-generation of supervised training manifests requires an explicit investigator decision closing or amending the Phase 2A Finalization Gate, approving:
1. Exact-time 23-window discretization (`round(k * 5.0 * fs)`) yielding 1,104 candidate windows.
2. Prespecified recording-level and window-level SQI gating criteria.
3. Explicit reference HR convention and hardware clock synchronization confidence classification.
