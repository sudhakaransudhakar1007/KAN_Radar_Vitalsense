# PHASE 8 MODEL INFERENCE COMPATIBILITY AND GOVERNANCE AUDIT

**Project Title:** A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals  
**Execution Stage:** Phase 8 — Recorded Radar Data Streaming Simulation  
**Document:** Model Inference Compatibility, Checkpoint Audit, and Zero-Fabrication Verification  
**Run Directory:** `outputs/demo_simulation/run_001/`  
**Execution Date:** 2026-10-18  

---

## 1. Executive Verdict & Operating Mode

| Metric / Audit Check | Status | Verification Detail |
|---|:---:|---|
| **Repository Checkpoint Audit** | **0 Checkpoints Found** | Exhaustive search for `.h5`, `.keras`, `.pt`, `.ckpt` yielded 0 trained weights. |
| **Phase 2A Governance Gate** | **STRICTLY OPEN** | `outputs/phase2a/step2b_consistency_audit.md`: Real-data training unauthorized. |
| **Active Operating Mode** | **MODE A: VISUALIZATION ONLY** | All model predictions suppressed; UI displays `HR: NOT AVAILABLE`. |
| **Secondary Operating Mode** | **MODE B: SAVED-MODEL READY** | `SafeModelInferenceEngine` implemented and verified ready for future authorized weights. |
| **Fabrication Audit** | **ZERO FABRICATION** | No random BPM generation (`np.random`), no synthetic substitute claims. |
| **Inference Weight Safety** | **ZERO MODIFICATIONS** | Inference runs without gradient tapes; no weight updates during demo runtime. |

---

## 2. Checkpoint Search and Audit Evidence

An exhaustive filesystem scan of the repository was conducted:
```powershell
Get-ChildItem -Recurse -Include *.h5, *.keras, *.pt, *.ckpt, *.pb, *.weights
```
**Result:** Exactly zero (0) trained model checkpoint files exist in the repository.

### Governance Rationale
The absence of trained model checkpoints is scientifically correct and strictly compliant with project governance:
1. **Phase 2A Gate:** The synchronization and data-consistency gate (`outputs/phase2a/step2b_consistency_audit.md`) concluded with status `RECONCILIATION PARTIAL — FINALIZATION GATE NOT YET APPROVED`.
2. **Phase 5 Training Restraint:** In Phase 5, Phase 6, Phase 7, and Phase 7B, the execution engine strictly respected the mandatory rule: *"Do not train any model on real VITALSENSE data; do not close the Phase 2A governance gate."*
3. **Integrity Rule Adherence:** Consequently, no supervised training on real radar data has ever taken place. Creating fake weights or claiming a trained KAN exists would violate scientific integrity.

---

## 3. Operational Mode Specifications

### 3.1 Mode A: Visualization Only — Model Unavailable (ACTIVE)
In the absence of an authorized trained checkpoint, the demo operates honestly in Mode A:
- **`SafeModelInferenceEngine.get_compatibility_status()`**:
  ```python
  ModelCompatibilityStatus(
      model_name="KANRegressor",
      checkpoint_path=None,
      is_available=False,
      operating_mode="VISUALIZATION_ONLY",
      status_reason="No trained KAN checkpoint found in repository (Phase 2A Gate OPEN: real-data training not authorized)"
  )
  ```
- **Prediction Suppression:** `SafeModelInferenceEngine.predict_window()` immediately returns:
  ```python
  ModelInferenceResult(
      window_index=k,
      start_time_s=t_start,
      end_time_s=t_end,
      prediction_bpm=None,              # Strictly None, never random BPM
      raw_normalized_output=None,
      confidence_interval=(None, None),
      status="MODEL_UNAVAILABLE",
      provenance_note="Operating in Mode A: VISUALIZATION_ONLY. No trained checkpoint available."
  )
  ```
- **Dashboard Presentation:** The web interface renders:
  - Metric Card: `HR PREDICTION: NOT AVAILABLE`
  - Chart Watermark: `MODEL UNAVAILABLE (MODE A: VISUALIZATION ONLY)`
  - History Table: `--` for BPM column with status badge `MODEL_UNAVAILABLE`

### 3.2 Mode B: Saved-Model Inference (GATED & COMPATIBLE)
When the investigator formally authorizes Phase 2A gate closure and trains models under a supervised protocol, `SafeModelInferenceEngine` will automatically switch to Mode B upon pointing to the valid checkpoint:
- **Model Architecture:** Feature-based KAN Regressor (`src.phase4.kan_model.KANFeatureRegressor`) or dual-input KAN (`KANRegressor`).
- **Input Dimension Contract:**
  - Raw window signal: Shape `(1, 3333, 1)` containing 10.0 seconds of bandpass-filtered radar displacement.
  - Engineered feature vector: Shape `(1, 6)` extracted via `RadarFeatureExtractor` (autocorrelation peak, spectral centroid, spectral power, etc.).
- **Target Inverse Normalization:** Targets normalized to $[0, 1]$ during training must be mapped back to physiological BPM using fold-specific statistics:
  $$\text{BPM} = \hat{y} \times (\text{HR}_{\max} - \text{HR}_{\min}) + \text{HR}_{\min}$$
- **Zero Training Safeguard:** Inference execution is decorated with `tf.function` or pure forward evaluation, isolated from any loss functions or optimizers.

---

## 4. Input Validation & Error Handling Contract

`SafeModelInferenceEngine.predict_window` implements strict defensive barriers:
1. **Sample Length Rejection:** If an incomplete window (e.g. $N \ne 3,333$) is submitted, the engine refuses inference and returns `status = "INVALID_INPUT"` with error message `"Expected 3333 samples, got {len}"`.
2. **Non-Finite Sample Rejection:** If any sample in the window is `NaN` or `Inf`, the engine returns `status = "INVALID_INPUT"` with error message `"Window contains non-finite samples"`.
3. **Corrupted Checkpoint Rejection:** If a checkpoint file is present but has incompatible layer weights, corrupted HDF5 groups, or mismatched spline knots, the engine traps the exception, sets `is_available = False`, logs the exact traceback, and falls back gracefully to Mode A without application crashing.

---

## 5. Automated Verification Summary

The model compatibility safeguards were independently tested and verified in `tests/test_demo_simulation.py`:
- `test_missing_checkpoint_suppresses_predictions`: PASSED. Confirms `prediction_bpm is None` and `status == "MODEL_UNAVAILABLE"`.
- `test_invalid_input_window_rejection`: PASSED. Confirms rejection of truncated buffers ($N = 1000$) and non-finite signals without runtime crashes.
- `test_research_integrity_safeguards`: PASSED. Confirms Phase 2A gate file remains open and zero persistent supervised tensors exist.
