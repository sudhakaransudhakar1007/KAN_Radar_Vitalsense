# PHASE 4B: LEAVE-ONE-SUBJECT-OUT (LOSO) ISOLATION & LEAKAGE AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Audit Stage:** Phase 4B — LOSO Cross-Validation & Data Leakage Review  
**Audit File:** `outputs/phase4/audit_run_001/loso_leakage_audit.md`  

---

## 1. Audit of the 24 Subject-Independent Folds

The Leave-One-Subject-Out (LOSO) cross-validation partitioner was evaluated across all 24 subjects ($VS01$ through $VS24$) against `outputs/supervised_dataset/run_001/accepted_window_manifest.csv` and `outputs/phase4/run_001/fold_split_manifest.csv`:

### Summary of Audited Fold Properties:
- **Total Folds:** 24 folds ($VS01$ to $VS24$).
- **Test Subject Isolation:** In every fold $k$, the test set contains windows from **only** subject $VS_k$.
- **Training Subject Set:** In every fold $k$, the training set contains windows from **exactly the other 23 subjects**.
- **Subject Overlap:** $\text{Subjects}(\text{Train}_k) \cap \text{Subjects}(\text{Test}_k) = \emptyset$ (Verified **0% leakage** across all 24 folds).
- **Total Test Windows Audited Across All 24 Folds:** Exactly **1,029 windows** (matching the total accepted manifest).

---

## 2. Window Overlap & Temporal Isolation Analysis

A frequent vulnerability in sliding-window biomedical machine learning is **window overlap leakage**:
- If windows are sampled with a 5.0-second stride on a 10.0-second window, consecutive windows overlap by 50% ($5.0\text{ seconds}$).
- If an evaluation framework performs a random train/test split or a recording-level split, overlapping windows from the same recording could appear in both train and test sets, artificially inflating performance.

### Auditor Verification for VITALSENSE LOSO:
- In our framework, partitioning is strictly enforced at the **subject identifier boundary** (`subject_id`).
- When subject $VS01$ is held out, **all** windows from both $VS01\_Resting$ and $VS01\_Apnea$ are placed exclusively in the test set.
- **Zero windows** (overlapping or non-overlapping) from the held-out subject exist in the training set.
- Therefore, the 50% window overlap remains entirely contained within the held-out evaluation partition and cannot leak into model training.

---

## 3. Identification of Hidden Leakage Risks

While the subject partitioning logic passed verification, the auditor identified four subtle leakage risks that the unit tests alone do not detect:

### Risk 1: Global vs. In-Fold Normalization Leakage
- **The Risk:** If signal preprocessing (e.g., standardizing radar waveform amplitude or normalizing target heart rates via mean/std) is calculated across the entire 1,029-window dataset prior to fold splitting, statistics from the held-out subject contaminate the training set.
- **Current Status:** In Phase 4, no global feature normalization was fitted to real radar signals because real-data training was blocked.
- **Mitigation Requirement:** When real training is authorized, any normalization parameters ($\mu_{\text{train}}, \sigma_{\text{train}}$) must be computed **strictly on the 23 training subjects inside each fold**, and then applied to transform the test subject windows.

### Risk 2: Hyperparameter Selection & Architecture Tuning Leakage
- **The Risk:** If hyperparameters (such as learning rate, spline order $k$, knot grid size $G$, Conv1D kernel sizes, or early stopping epoch) are tuned by observing performance across the 24 held-out test subjects, the architecture will overfit to the test set, compromising true subject-independence.
- **Current Status:** Hyperparameters in `training_config.json` are currently fixed a priori based on literature ($k=3, G=5$, Huber $\delta=1.0$).
- **Mitigation Requirement:** If hyperparameter search is conducted, it must use **nested cross-validation** (e.g., an inner 5-fold CV over the 23 training subjects) without examining the outer held-out test subject.

### Risk 3: Cross-Condition Splitting Leakage
- **The Risk:** In some prior literature, researchers split by recording rather than by subject (e.g., training on $VS01\_Resting$ and testing on $VS01\_Apnea$). Because thoracic dimensions, cardiac morphology, and radar reflectivity are subject-specific, this causes severe subject identity leakage.
- **Auditor Verification:** Our audit verified that in all 24 folds, both Resting and Apnea conditions for the subject are held out simultaneously.

### Risk 4: Temporal Filtering Warm-Up Edge Effects
- **The Risk:** Zero-phase Butterworth filtering (`filtfilt`) across the 120-second continuous recording has transient edge effects at $t < 2.0\text{ s}$ and $t > 118.0\text{ s}$.
- **Auditor Verification:** The 4.98-second trailing tail exclusion eliminates end-of-signal edge effects. For initial windows, the Pan-Tompkins detector and Butterworth filter stabilize within the first 1.0 s, and windows with SQI anomalies are rejected.
