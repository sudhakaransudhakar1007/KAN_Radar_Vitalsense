# Forensic Audit: Dataset Manifests, Window Reconciliation, and LOSO Partition Integrity

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Biomedical Data Auditor, Scientific ML Specialist, & Research Reproducibility Reviewer  
**Artifact File:** `outputs/phase7b/run_001/dataset_and_loso_consistency_audit.md`  

---

## 1. Executive Summary & Audited Manifest Inventory

This forensic audit independently verified the integrity of the supervised dataset manifests and the 24-fold Leave-One-Subject-Out (LOSO) cross-validation evaluation splits without executing real-data model training.

### Verified File Provenance:
- Candidate Manifest: [`outputs/supervised_dataset/run_001/candidate_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/candidate_window_manifest.csv)
- Accepted Manifest: [`outputs/supervised_dataset/run_001/accepted_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/accepted_window_manifest.csv)
- Rejected Manifest: [`outputs/supervised_dataset/run_001/rejected_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/rejected_window_manifest.csv)
- LOSO Audit CSV: [`outputs/phase7/run_001/loso_integrity_reverification.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase7/run_001/loso_integrity_reverification.csv)

---

## 2. Comprehensive Dataset Accounting and Window Reconciliation

All 48 candidate recordings ($24\text{ subjects} \times 2\text{ conditions}$) were processed by [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py).

### Exact Mathematical Reconciliation:
$$\text{Candidate Windows Extracted} = \mathbf{1,056}$$
$$\text{Accepted Supervised Windows} = \mathbf{1,029}$$
$$\text{Rejected Candidate Windows} = \mathbf{27}$$
$$\mathbf{1,029\text{ (accepted)} + 27\text{ (rejected)} = 1,056\text{ (candidate)}}\quad (\text{Exact } 100\%\text{ balance})$$

```text
============================================================
1. Dataset Manifests Accounting
============================================================
Candidate windows: 1056
Accepted windows:  1029
Rejected windows:  27
Sum Acc + Rej:     1056 (Matches candidate: True)
Unique subjects in Candidate: 24
Unique subjects in Accepted:  24
Unique subjects in Rejected:  3
Total candidate recordings:   48
```

---

## 3. Condition Distribution and Rejection Cause Analysis

### 3.1 Accepted Supervised Windows by Condition
- **Apnea Windows Accepted:** **526 windows** ($51.1\%$)
- **Resting Windows Accepted:** **503 windows** ($48.9\%$)
- **Total Accepted:** **1,029 windows**

### 3.2 Rejected Windows by Condition
- **Resting Windows Rejected:** **25 windows** ($92.6\%$)
- **Apnea Windows Rejected:** **2 windows** ($7.4\%$)
- **Total Rejected:** **27 windows**

### 3.3 Root-Cause Categorization of Rejections
The 27 rejections occurred across exactly 3 subjects (`VS02`, `VS05`, `VS14`) due to the following specific biomedical SQI triggers:

| Subject ID | Condition | Window Index | Rejection Reason | Biomedical Root Cause |
| :---: | :---: | :---: | :--- | :--- |
| `VS02` | Resting | 0–21 (all 22) | `ECG_DELIMITER_INTERPOLATION_FAILED_OR_BOUNDARY_NAN` | Trailing NaN delimiter block in Lead-II MAT array |
| `VS05` | Resting | 13 | `RR_COVERAGE_BELOW_85_PCT (84.96%)` | Transient electrode contact loss ($84.96\% < 85.0\%$) |
| `VS05` | Resting | 14, 15 | `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW` | Instantaneous RR interval $< 0.3243\text{ s}$ ($> 185\text{ BPM}$) |
| `VS14` | Apnea | 10, 11 | `NON_PHYSIOLOGICAL_RR_INTERVAL_IN_WINDOW` | Instantaneous RR interval $< 0.3243\text{ s}$ ($> 185\text{ BPM}$) |

### Resolution of Historical Contradiction:
Early narrative notes in Phase 4 informally stated that "window rejections were concentrated in Apnea sessions due to respiratory motion". This audit conclusively refutes that claim:
- **25 of the 27 rejected windows ($92.6\%$) occurred in Resting sessions**, primarily caused by the 22 trailing NaN delimiter samples in `VS02_Resting`.
- **Only 2 windows ($7.4\%$) were rejected in Apnea sessions** (`VS14_Apnea`).

---

## 4. 24-Fold Leave-One-Subject-Out (LOSO) Partition Integrity

We recomputed the LOSO cross-validation partition across all 24 subjects (`VS01` through `VS24`) using [`scratch/verify_dataset_loso.py`](file:///C:/Users/admin/.gemini/antigravity/brain/2aee08b1-0663-462c-814d-4f0ee6599ca8/scratch/verify_dataset_loso.py).

### 4.1 Subject Isolation & Zero Leakage
For each fold $k \in \{1, \dots, 24\}$ holding out subject $S_k$:
- Training subjects: $23$ unique subjects ($\{S_i \mid i \ne k\}$).
- Subject overlap between training and testing sets: **$0.0\%$ (ZERO LEAKAGE)**.
- Both conditions (Resting and Apnea) for subject $S_k$ are completely excluded from the training partition and evaluated exclusively in the held-out test fold.

### 4.2 Test Window Coverage Across Folds
- Sum of held-out test windows across the 24 folds: **exactly 1,029 windows**.
- Unique test window manifest indices evaluated: **exactly 1,029**.
- Every single eligible supervised window appears in **exactly one held-out test fold**.
- Zero duplicate evaluations; zero omitted windows.

```text
============================================================
4. LOSO Fold Verification (from accepted manifest)
============================================================
Total unique subjects in accepted manifest: 24
Sum of test windows across 24 folds: 1029
Unique test indices across 24 folds: 1029
Is every accepted window evaluated exactly once in held-out test fold? True
```

---

## 5. Target Normalization Isolation Code Verification

The prompt mandates verifying that training-only normalization is genuinely implemented in code, not merely documented.

In [`src/kan/normalization.py:31-72`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/normalization.py#L31-L72):
```python
class TargetNormalizer:
    def fit_transform(self, y_train: np.ndarray) -> np.ndarray:
        y_valid = np.array(y_train, dtype=np.float64).flatten()
        self.train_mean = float(np.mean(y_valid))
        raw_std = float(np.std(y_valid))
        self.train_std = raw_std if raw_std > 1e-6 else 1.0
        self.is_fitted = True
        return (y_valid - self.train_mean) / self.train_std

    def transform(self, y: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("TargetNormalizer must be fitted on training fold before transform.")
        return (np.array(y, dtype=np.float64).flatten() - self.train_mean) / self.train_std

    def inverse_transform(self, y_norm: np.ndarray) -> np.ndarray:
        return np.array(y_norm, dtype=np.float64).flatten() * self.train_std + self.train_mean
```

In [`src/kan/loso_evaluator.py:243-245`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/kan/loso_evaluator.py#L243-L245):
```python
243:         normalizer = TargetNormalizer()
244:         y_train_norm = normalizer.fit_transform(y_train)
245:         y_test_norm = normalizer.transform(y_test)
```
- `TargetNormalizer.fit_transform` computes `train_mean` and `train_std` **strictly on `y_train`**.
- `transform` projects test targets using the training statistics without altering `train_mean` or `train_std`.
- `inverse_transform` strictly maps predictions back to physical BPM using training fold parameters:
  $$\hat{y}_{\text{bpm}} = \hat{y}_{\text{norm}} \times \sigma_{\text{train}} + \mu_{\text{train}}$$
- Calling `transform()` before `fit_transform()` raises `RuntimeError("must be fitted on training fold")`.

**Verification Verdict:** Normalization isolation is strictly implemented, leakage-proof, and unit-tested in [`test_target_normalizer_training_only_fit`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_phase4d_completion.py#L42-L64) and [`test_target_normalizer_leakage_guards`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_phase4d_completion.py#L79-L91).

---

## 6. Audit Conclusion & Remediation
- **Manifest Accounting:** $1,056\text{ candidate} = 1,029\text{ accepted} + 27\text{ rejected}$. Verified with 0 discrepancy.
- **Rejection Cause Truth:** $25$ of $27$ rejections occurred in Resting recordings ($22$ from `VS02_Resting` NaN delimiters).
- **LOSO Partition:** Zero subject leakage across all 24 folds; all 1,029 windows evaluated exactly once.
- **Normalization Isolation:** Pure training-fold standardization verified in source code and unit tests.
- **Code Modifications Needed:** **NONE.**
