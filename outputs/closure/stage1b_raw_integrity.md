# STAGE 1B — RAW FILE INTEGRITY AUDIT REPORT: VS20_Resting_Mindray.mat

**Document ID:** `outputs/closure/stage1b_raw_integrity.md`  
**Execution Date:** 2026-10-18  
**Target File:** `data/VITALSENSE_120_DATASET/VS20/VS20_Resting_Mindray.mat`  
**Investigation Topic:** Verification of disk modification timestamp, cryptographic SHA-256 hash, internal array counts, write-pattern search, and file integrity relative to Phase 1 baseline records.

---

## 1. On-Disk File Metadata & Operating System Stat

A direct read-only query using Python `os.stat` and `hashlib.sha256` evaluated the target file on the local filesystem:

- **Target Path:** `data/VITALSENSE_120_DATASET/VS20/VS20_Resting_Mindray.mat`
- **File Size:** `233,082 bytes`
- **Cryptographic SHA-256:**  
  `518287f0d295f024a15f95c49a3c9929907274c30fa394356342c094ed726b87`
- **Modification Time (`st_mtime`):** `1789659396.4048858`  
  - UTC: `2026-09-17T15:36:36.404886+00:00`
- **Creation Time (`st_ctime` / Windows NTFS Creation):** `1791816227.889735`  
  - UTC: `2026-10-12T14:43:47.889735+00:00` (corresponds to initial dataset extraction on host machine)
- **Access Time (`st_atime`):** `2026-10-18T09:33:07.287630+00:00`

---

## 2. Comparison with Historical Phase 1 Baseline Records & Checksum Manifests

The on-disk properties were compared against all pre-existing baseline manifests in `outputs/`:

| Artifact Path | Recorded SHA-256 | Recorded Size | Recorded Modification Time | Status |
| :--- | :--- | :---: | :---: | :---: |
| `outputs/phase1_audit/file_inventory.csv` | `518287f0d295f024a15f95c49a3c9929907274c30fa394356342c094ed726b87` | 233,082 bytes | `2026-09-17T15:36:36.404886+00:00` | **EXACT MATCH** |
| `outputs/closure/stage0_snapshot.csv` (row 136) | `518287f0d295f024a15f95c49a3c9929907274c30fa394356342c094ed726b87` | 233,082 bytes | `2026-09-17T15:36:36Z` | **EXACT MATCH** |

### Origin of Apparent Anomaly:
The apparent modification timestamp `2026-10-18T05:36:36Z` cited in the investigation prompt originated exclusively from a typographical transcription error in previous assistant conversation text. The physical file on disk was never modified; its modification timestamp is and has always been `2026-09-17T15:36:36.404886+00:00`, which is 100% identical to the pre-audit Phase 1 inventory and the other 95 raw files.

---

## 3. Recomputed Array Counts (Read-Only Verification)

Direct read-only inspection of MAT structures (`scipy.io.loadmat` without modifying or re-saving) produced the following array counts:

| Variable | On-Disk Shape | On-Disk Dtype | On-Disk NaN Count | Historical Record in Phase 1 / Step 2B | Consistency Status |
| :--- | :---: | :---: | :---: | :--- | :---: |
| `ecg_lead2` | `(60000, 1)` | `float64` | `120` | `sync_validation_results.csv`: `ecg_nan_count = 120`<br>`candidate_fields.csv`: shape `(60000,)`, `float64` | **EXACT MATCH** |
| `HR` | `(120, 1)` | `uint8` | `0` | `reference_inventory.csv`: shape `(120,)`, `uint8`, 0 invalid<br>`candidate_fields.csv`: shape `(120,)`, `uint8` | **EXACT MATCH** |
| `respiration` | `(30720, 1)` | `float64` | `0` | `candidate_fields.csv`: shape `(30720,)`, `float64` | **EXACT MATCH** |

All remaining variables (`BPD`, `BPM`, `BPS`, `Fs_ecg`, `Fs_pleth`, `Fs_resp`, `RR`, `ecg_lead3`, `ecg_leadv1`, `pleth`) are intact and identical to candidate field definitions recorded in Phase 1.

---

## 4. Source Code and Test Suite Write-Pattern Audit

A recursive search was executed across `src/` and `tests/` for any routine that could write, touch, re-save, or open in write/append mode any `.mat` file:

- **Search in `src/`:**
  - `savemat` calls: **0** found.
  - File write operations: All writes in `src/` exclusively write JSON, CSV, or Markdown files into `outputs/` or demo directory.
  - No function in `src/` opens, modifies, or writes to any `.mat` file.
- **Search in `tests/`:**
  - `savemat` calls: **11** found across `tests/test_demo_simulation.py`, `tests/test_mat_inspection.py`, and `tests/test_phase3_pipeline.py`.
  - All test `savemat` calls write mock synthetic MAT files strictly into pytest temporary directories (`tmp_path`).
  - Zero test routines open, write, or touch files in `data/VITALSENSE_120_DATASET/`.

---

## 5. Formal Verdict

**`RAW_INTEGRITY = CONSISTENT_WITH_EARLIER_RECORDS`**

1. The target file `VS20_Resting_Mindray.mat` has **NOT** been modified.
2. Its cryptographic SHA-256 hash (`518287f0...`), byte size (`233,082`), and UTC modification timestamp (`2026-09-17T15:36:36.404886+00:00`) match the Phase 1 audit baseline recorded on 2026-09-17 bit-for-bit.
3. Internal signal lengths, data types, and NaN counts match all historical audit tables.
4. No code in the repository possesses the capability or authorization to write to raw data files.
