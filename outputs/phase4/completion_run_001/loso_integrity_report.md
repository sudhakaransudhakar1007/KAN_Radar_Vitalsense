# PHASE 4D: LOSO CROSS-VALIDATION INTEGRITY & LEAKAGE AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Stage:** Phase 4D — Task 7: LOSO Infrastructure Verification  
**Run Directory:** `outputs/phase4/completion_run_001/`  
**Execution Date:** October 16, 2026  

---

## 1. Audit of the 24 Subject-Independent Folds

The Leave-One-Subject-Out (LOSO) cross-validation partitioner was verified across all 24 subjects ($VS01$ through $VS24$) in [`fold_split_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/phase4/completion_run_001/fold_split_manifest.csv) against [`accepted_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/accepted_window_manifest.csv):

### Mandatory Invariants Verified:
1. **Zero Subject Overlap:**  
   $$\text{Subjects}(\text{Train}_k) \cap \text{Subjects}(\text{Test}_k) = \emptyset \quad \forall k \in [1, 24]$$
   Verified **0.0% subject leakage** across all 24 folds.
2. **Coupled Condition Holding:**  
   In all 24 folds, both Resting and Apnea recordings for the held-out subject are placed in the test set simultaneously. No subject has a split recording condition across train and test.
3. **Partition Completeness:**  
   - 21 subjects have 44 test windows (22 Resting, 22 Apnea).
   - $VS03$ has 43 test windows (21 Resting, 22 Apnea; Window 0 rejected by SQI).
   - $VS10$ has 22 test windows (0 Resting, 22 Apnea; `VS10_Resting` rejected by SQI).
   - $VS16$ has 40 test windows (20 Resting, 20 Apnea; Windows 0 and 1 rejected by SQI).
   - **Sum of Test Windows Across All 24 Folds:** $21 \times 44 + 43 + 22 + 40 = \mathbf{1,029\text{ windows}}$ (matches 100% of the accepted dataset).

---

## 2. Window Overlap & Temporal Isolation

Sliding windows have a duration of $10.0\text{ seconds}$ and a stride of $5.0\text{ seconds}$, yielding a 50% temporal overlap between consecutive windows from the same recording.
- Because all windows from a subject are held out together, all overlapping windows are confined within either the training partition or the testing partition.
- **Zero overlapping windows cross the train/test boundary.**

---

## 3. Protocol for Checkpoint Selection & Hyperparameter Isolation

To preserve subject independence during future model training (Phase 5):
1. **Validation Checkpoint Selection:**  
   When early stopping or model checkpointing is used, the validation set must be formed from a subset of the **training subjects** (e.g., 3 subjects held out from the 23 training subjects), **never** from the test subject.
2. **Held-Out Test Target Blindness:**  
   The held-out test subject targets ($y_{\text{test}}$) are strictly isolated during training, optimizer updates, learning rate scheduling, and early stopping. They are evaluated exactly once at the end of training for final test metric calculation.
