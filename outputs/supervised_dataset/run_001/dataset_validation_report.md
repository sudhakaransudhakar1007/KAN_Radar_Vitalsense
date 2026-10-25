# Supervised Dataset Validation Report

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Supervised Dataset Generation Implementation & Quality Audit  
**Run ID:** `run_001`  
**Execution Date:** October 15, 2026  
**Status:** `VERIFIED_EVIDENCE_BASED`  

---

## 1. Window Inventory & Acceptance / Rejection Accounting

The supervised dataset generation pipeline evaluated all 48 candidate radar/reference recording pairs of the VITALSENSE dataset:

- **Total Candidate Windows Evaluated:** Exactly **1,056 windows** ($48\text{ recordings} \times 22\text{ windows/recording}$).
- **Total Accepted Windows:** **1,029 windows (97.44%)** meeting all user-approved SQI criteria.
- **Total Rejected Windows:** **27 windows (2.56%)** across 4 recordings.

### Rejection Breakdown by Specific Failure Cause:

| Rejection Category | Window Count | Affected Recordings | Detailed Technical Rationale |
| :--- | :---: | :--- | :--- |
| **Leading Boundary NaN** | 22 | `VS10_Resting` (wins 0–21) | Periodic delimiter NaN occurred at sample index `0` (`nan_indices = [0, 501, 1002, ...]`). Flagged as un-interpolable without boundary extrapolation. |
| **Non-Physiological RR Interval** | 4 | `VS16_Apnea` (wins 4, 5)<br>`VS16_Resting` (wins 0, 1) | Detected RR interval fell outside physiological bounds ($0.3243\text{ s} \le RR_i \le 1.7143\text{ s}$), indicating premature ectopic contraction or local artifact. |
| **RR Interval Coverage < 85%** | 1 | `VS03_Resting` (win 0) | RR interval coverage within the $[0.0\text{ s}, 10.0\text{ s})$ window was 84.96%, narrowly missing the 85.0% threshold. |
| **Total Rejections** | **27** | **4 recordings** | **Zero silent inclusions of unvalidated intervals.** |

---

## 2. Window Counts by Subject and Experimental Condition

### Accepted Window Counts per Subject:
- **44 Windows Accepted (100% of candidate windows):** 21 subjects
  - `VS01` (44), `VS02` (44), `VS04` (44), `VS05` (44), `VS06` (44), `VS07` (44), `VS08` (44), `VS09` (44), `VS11` (44), `VS12` (44), `VS13` (44), `VS14` (44), `VS15` (44), `VS17` (44), `VS18` (44), `VS19` (44), `VS20` (44), `VS21` (44), `VS22` (44), `VS23` (44), `VS24` (44).
- **43 Windows Accepted (97.7%):** `VS03` (22 Apnea, 21 Resting; 1 window rejected).
- **40 Windows Accepted (90.9%):** `VS16` (20 Apnea, 20 Resting; 4 windows rejected).
- **22 Windows Accepted (50.0%):** `VS10` (22 Apnea, 0 Resting; 22 Resting windows rejected).

### Accepted Window Counts by Condition:
- **Apnea:** **526 windows** (528 candidate windows minus 2 rejected in `VS16_Apnea`).
- **Resting:** **503 windows** (528 candidate windows minus 22 in `VS10_Resting`, 1 in `VS03_Resting`, 2 in `VS16_Resting`).
- **Total Accepted Windows:** $526 + 503 = 1029\text{ windows}$.

---

## 3. Reference HR Label Distribution & Physiological Properties

Descriptive statistics across all 1,029 accepted windows:

| Metric | Reference HR (`reference_hr_bpm`) | RR Coverage (`rr_coverage_pct`) | Maximum RR Gap (`max_rr_gap_s`) |
| :--- | :---: | :---: | :---: |
| **Count** | 1,029 | 1,029 | 1,029 |
| **Mean** | 64.44 bpm | 99.73% | 0.996 s |
| **Std Dev** | 6.88 bpm | 3.86% | 0.110 s |
| **Min** | 47.52 bpm | 88.04% | 0.766 s |
| **25th Percentile** | 59.14 bpm | 96.92% | 0.912 s |
| **Median (50th)** | 64.92 bpm | 99.60% | 0.978 s |
| **75th Percentile** | 69.43 bpm | 102.64% | 1.080 s |
| **Max** | 82.89 bpm | 110.28% | 1.292 s |

### Quality & Integrity Verification:
- **Missing (NaN) Labels in Accepted Windows:** Exactly **0** (0.0%).
- **Non-Finite / Infinite Labels:** Exactly **0** (0.0%).
- **Duplicate Windows:** Exactly **0** (0.0% duplicates across `[subject_id, condition, window_index]`).
- **Physiological Bound Satisfaction:** 100% of accepted labels fall within $[47.52, 82.89]\text{ bpm}$, fully compliant with the prespecified $[35.0, 185.0]\text{ bpm}$ physiological range.
- **Pairing Concordance:** 100% of candidate radar windows ($48 \times 22 = 1056$) successfully mapped to corresponding reference ECG intervals without index or timestamp overflow.

---

## 4. Subject-Independent Split Integrity (Leakage Prevention)

To guarantee that downstream KAN models are strictly evaluated on unseen subjects:
1. **Window-Level Shuffling Prohibited:** Random splitting of sliding windows into train/validation/test sets is strictly forbidden, as overlapping 10-second windows (5.0s hop) from the same subject would cause severe test set contamination.
2. **Subject-Stratified Protocol:**
   - **Primary Recommendation:** Leave-One-Subject-Out (LOSO) Cross-Validation across all 24 subjects (24 evaluation folds).
   - **Alternative Fixed Partition:** 16 training subjects (approx. 680–700 windows), 4 validation subjects (approx. 170 windows), and 4 test subjects (approx. 170 windows).
3. **Normalization Boundary:** Preprocessing z-score normalization must be computed strictly per-window or derived exclusively from the training subject fold.

---

## 5. Gate Enforcement & Delivery Verdict

While all 1,029 accepted windows and 27 rejected windows are exhaustively cataloged in their respective CSV manifests, **saving persistent binary training tensors (`X_radar.npy`, `y_hr.npy`) was halted** because the Phase 2A Finalization Gate remains formally open (`step2b_consistency_audit.md`).
