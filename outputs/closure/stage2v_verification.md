# STAGE 2V — VERIFICATION OF STAGE 2 (READ-ONLY)

**Document Path:** `outputs/closure/stage2v_verification.md`  
**Execution Stage:** Stage 2V — Post-Implementation Verification & Boundary Audit  
**Phase 2A Gate Status:** OPEN (Strictly enforced; no gate closure permitted)  
**Execution Mode:** Read-Only Audit & Verification. No modifications to `outputs/phase2a/`, `src/`, `tests/`, or raw dataset files.

---

## 1. SOURCE CODE VERIFICATION

Below is the complete line-numbered source code of the eight target functions implemented or refactored in Stage 2.

### 1.1 `truncate_respiration_dynamic_length_in_memory`
**File:** [`src/sync_validation/respiratory_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/respiratory_validator.py#L55-L93) (Lines 55–93)

```python
  55: def truncate_respiration_dynamic_length_in_memory(
  56:     vitalsig: np.ndarray,
  57:     rad_fs: float,
  58:     respiration: np.ndarray,
  59:     ref_fs: float,
  60: ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
  61:     """Dynamically evaluate raw array durations and truncate mismatched respiration in memory.
  62: 
  63:     Addresses ISS-12: When recordings have mismatched sample counts (e.g. VS24_Resting with
  64:     30,600 samples ~119.53s vs standard 30,720 samples 120.0s), dynamically query array lengths
  65:     and truncate trailing tail to the common minimum duration strictly in memory.
  66:     The source files and arrays remain completely unmodified on disk.
  67: 
  68:     Returns:
  69:         (vitalsig_common, respiration_common, info_dict)
  70:     """
  71:     v = np.array(vitalsig, copy=True, dtype=np.float64).flatten()
  72:     r = np.array(respiration, copy=True, dtype=np.float64).flatten()
  73: 
  74:     dur_v = len(v) / rad_fs
  75:     dur_r = len(r) / ref_fs
  76:     common_dur_s = min(dur_v, dur_r)
  77: 
  78:     n_v = min(len(v), int(np.floor(common_dur_s * rad_fs)))
  79:     n_r = min(len(r), int(np.floor(common_dur_s * ref_fs)))
  80: 
  81:     info = {
  82:         "original_vitalsig_samples": len(v),
  83:         "original_respiration_samples": len(r),
  84:         "vitalsig_duration_s": dur_v,
  85:         "respiration_duration_s": dur_r,
  86:         "common_duration_s": common_dur_s,
  87:         "truncated_vitalsig_samples": n_v,
  88:         "truncated_respiration_samples": n_r,
  89:         "respiration_samples_excluded": len(r) - n_r,
  90:         "has_length_mismatch": abs(dur_v - dur_r) > 1e-4,
  91:     }
  92: 
  93:     return v[:n_v], r[:n_r], info
```

---

### 1.2 `clean_ecg_isolated_nans`
**File:** [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L10-L93) (Lines 10–93)

```python
  10: def clean_ecg_isolated_nans(
  11:     ecg_raw: np.ndarray,
  12:     max_gap: int = 1,
  13: ) -> Tuple[np.ndarray, Dict[str, Any]]:
  14:     """Linearly interpolate ONLY isolated single-sample delimiter NaNs in memory.
  15: 
  16:     Addresses ISS-13 / ISS-13b: Multi-sample gaps (length > max_gap) are NOT interpolated
  17:     and are flagged with indices and counts logged, protecting QRS complexes from distortion.
  18:     Original array is unmodified; operations execute strictly on an in-memory copy.
  19: 
  20:     Args:
  21:         ecg_raw: Input ECG waveform.
  22:         max_gap: Maximum contiguous NaN count eligible for interpolation (default 1).
  23: 
  24:     Returns:
  25:         (ecg_clean, info_dict)
  26:     """
  27:     ecg = np.array(ecg_raw, copy=True, dtype=np.float64).flatten()
  28:     nans = np.isnan(ecg)
  29:     total_nans = int(np.sum(nans))
  30: 
  31:     if total_nans == 0:
  32:         return ecg, {
  33:             "total_nan_count": 0,
  34:             "isolated_nan_count": 0,
  35:             "isolated_indices": [],
  36:             "multi_sample_gap_count": 0,
  37:             "multi_sample_gap_indices": [],
  38:             "uninterpolated_nan_count": 0,
  39:             "has_multi_sample_gaps": False,
  40:         }
  41: 
  42:     # Group contiguous NaNs into runs
  43:     runs = []
  44:     in_run = False
  45:     start_idx = 0
  46:     for i, is_nan in enumerate(nans):
  47:         if is_nan and not in_run:
  48:             in_run = True
  49:             start_idx = i
  50:         elif not is_nan and in_run:
  51:             in_run = False
  52:             runs.append((start_idx, i - start_idx))
  53:     if in_run:
  54:         runs.append((start_idx, len(nans) - start_idx))
  55: 
  56:     isolated_indices = []
  57:     multi_sample_runs = []
  58:     valid_indices = np.where(~nans)[0]
  59: 
  60:     if len(valid_indices) == 0:
  61:         return ecg, {
  62:             "total_nan_count": total_nans,
  63:             "isolated_nan_count": 0,
  64:             "isolated_indices": [],
  65:             "multi_sample_gap_count": 1,
  66:             "multi_sample_gap_indices": [list(range(len(ecg)))],
  67:             "uninterpolated_nan_count": total_nans,
  68:             "has_multi_sample_gaps": True,
  69:         }
  70: 
  71:     for start, length in runs:
  72:         if length <= max_gap:
  73:             # Interpolate isolated single-sample NaN
  74:             for idx in range(start, start + length):
  75:                 isolated_indices.append(idx)
  76:                 ecg[idx] = np.interp(idx, valid_indices, ecg[valid_indices])
  77:         else:
  78:             # Multi-sample gap: do NOT interpolate; flag it
  79:             multi_sample_runs.append(list(range(start, start + length)))
  80: 
  81:     uninterpolated_count = sum(len(r) for r in multi_sample_runs)
  82: 
  83:     info = {
  84:         "total_nan_count": total_nans,
  85:         "isolated_nan_count": len(isolated_indices),
  86:         "isolated_indices": isolated_indices,
  87:         "multi_sample_gap_count": len(multi_sample_runs),
  88:         "multi_sample_gap_indices": multi_sample_runs,
  89:         "uninterpolated_nan_count": uninterpolated_count,
  90:         "has_multi_sample_gaps": len(multi_sample_runs) > 0,
  91:     }
  92: 
  93:     return ecg, info
```

---

### 1.3 `clean_ecg_nans`
**File:** [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L96-L121) (Lines 96–121)

```python
  96: def clean_ecg_nans(
  97:     ecg_raw: np.ndarray,
  98:     only_isolated: bool = True,
  99: ) -> Tuple[np.ndarray, int, List[int]]:
 100:     """Clean isolated NaNs in an in-memory copy of ecg_lead2.
 101: 
 102:     If only_isolated=True (default per ISS-13b), only isolated single-sample NaNs
 103:     are interpolated; multi-sample gaps are not interpolated.
 104:     """
 105:     if only_isolated:
 106:         clean_arr, info = clean_ecg_isolated_nans(ecg_raw, max_gap=1)
 107:         return clean_arr, info["total_nan_count"], info["isolated_indices"]
 108: 
 109:     ecg = np.array(ecg_raw, copy=True, dtype=np.float64).flatten()
 110:     nans = np.isnan(ecg)
 111:     nan_count = int(np.sum(nans))
 112:     nan_indices = [int(i) for i in np.where(nans)[0]]
 113: 
 114:     if nan_count > 0:
 115:         valid_indices = np.where(~nans)[0]
 116:         if len(valid_indices) == 0:
 117:             return ecg, nan_count, nan_indices
 118:         ecg[nan_indices] = np.interp(nan_indices, valid_indices, ecg[valid_indices])
 119: 
 120:     return ecg, nan_count, nan_indices
```

**State of Default Behavior & Reachability:**
- **Default Behavior:** Changed. In Stage 0, `clean_ecg_nans` unconditionally interpolated all contiguous NaN segments of any length across the waveform. In Stage 2, default behavior has `only_isolated=True`, delegating to `clean_ecg_isolated_nans(ecg_raw, max_gap=1)` which strictly restricts interpolation to single-sample NaNs ($N=1$) and preserves multi-sample gaps as uninterpolated NaNs to avoid distorting QRS complexes.
- **Original Behavior Reachability:** Reachable. The original unconstrained interpolation behavior is fully preserved and reachable by passing `only_isolated=False`.

---

### 1.4 `detect_r_peaks`
**File:** [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L124-L270) (Lines 124–270)

```python
 124: def detect_r_peaks(
 125:     ecg_clean: np.ndarray,
 126:     fs: float = 500.0,
 127:     min_bpm: float = 35.0,
 128:     max_bpm: float = 175.0,
 129: ) -> Dict[str, Any]:
 130:     """Detect ECG R-peaks using a Pan-Tompkins style bandpass and integration method.
 131: 
 132:     Pipeline:
 133:       1. Butterworth bandpass filter (5-15 Hz, order 2) isolating QRS complex.
 134:       2. First-difference derivative to emphasize QRS slope.
 135:       3. Pointwise squaring to nonlinearly amplify high-frequency energy.
 136:       4. Moving window average integration (~150 ms = 75 samples at 500 Hz).
 137:       5. Adaptive thresholding with minimum refractory period.
 138:       6. Local peak refinement on filtered ECG.
 139:       7. Physiological RR interval validation (0.34s to 1.71s).
 140: 
 141:     Args:
 142:         ecg_clean: In-memory 1D ECG array with NaNs removed.
 143:         fs: Sampling rate in Hz (default 500.0).
 144:         min_bpm: Minimum physiological HR threshold.
 145:         max_bpm: Maximum physiological HR threshold.
 146: 
 147:     Returns:
 148:         Dictionary containing peak indices, timestamps, RR intervals, and QC metrics.
 149:     """
 150:     ecg = ecg_clean.flatten()
 151:     n_samples = len(ecg)
 152:     duration_s = n_samples / fs
 153: 
 154:     if n_samples < int(fs * 2.0):
 155:         return {
 156:             "status": "INSUFFICIENT_LENGTH",
 157:             "peaks": np.array([], dtype=int),
 158:             "peak_times": np.array([], dtype=float),
 159:             "rr_intervals": np.array([], dtype=float),
 160:             "valid_rr_mask": np.array([], dtype=bool),
 161:             "inst_hr": np.array([], dtype=float),
 162:             "valid_peak_count": 0,
 163:             "mean_rr_s": np.nan,
 164:             "std_rr_s": np.nan,
 165:             "rmssd_ms": np.nan,
 166:             "mean_hr_bpm": np.nan,
 167:             "qc_verdict": "FAIL",
 168:             "notes": "ECG length shorter than 2 seconds",
 169:         }
 170: 
 171:     # 1. Bandpass filter 5 - 15 Hz
 172:     nyq = 0.5 * fs
 173:     low = 5.0 / nyq
 174:     high = 15.0 / nyq
 175:     b, a = signal.butter(2, [low, high], btype="bandpass")
 176:     ecg_filt = signal.filtfilt(b, a, ecg)
 177: 
 178:     # 2. Derivative
 179:     diff = np.diff(ecg_filt, prepend=ecg_filt[0])
 180: 
 181:     # 3. Squaring
 182:     squared = diff ** 2
 183: 
 184:     # 4. Moving window average integration (~150 ms)
 185:     win_len = max(3, int(0.15 * fs))
 186:     kernel = np.ones(win_len) / win_len
 187:     mwa = signal.convolve(squared, kernel, mode="same")
 188: 
 189:     # 5. Peak picking with adaptive threshold
 190:     # Min distance corresponding to max_bpm
 191:     min_distance = int((60.0 / max_bpm) * fs)
 192:     threshold = 0.3 * np.percentile(mwa, 90)
 193: 
 194:     cand_peaks, _ = signal.find_peaks(mwa, distance=min_distance, height=threshold)
 195: 
 196:     # 6. Refine to local peak on filtered ECG
 197:     refined = []
 198:     search_radius = int(0.08 * fs)  # 80 ms
 199:     for p in cand_peaks:
 200:         start = max(0, p - search_radius)
 201:         end = min(n_samples, p + search_radius)
 202:         if end > start:
 203:             refined.append(start + np.argmax(np.abs(ecg_filt[start:end])))
 204: 
 205:     peaks = np.unique(refined) if len(refined) > 0 else np.array([], dtype=int)
 206: 
 207:     if len(peaks) < 3:
 208:         return {
 209:             "status": "INSUFFICIENT_PEAKS",
 210:             "peaks": peaks,
 211:             "peak_times": peaks / fs,
 212:             "rr_intervals": np.array([], dtype=float),
 213:             "valid_rr_mask": np.array([], dtype=bool),
 214:             "inst_hr": np.array([], dtype=float),
 215:             "valid_peak_count": len(peaks),
 216:             "mean_rr_s": np.nan,
 217:             "std_rr_s": np.nan,
 218:             "rmssd_ms": np.nan,
 219:             "mean_hr_bpm": np.nan,
 220:             "qc_verdict": "FAIL",
 221:             "notes": f"Only {len(peaks)} R-peaks detected across {duration_s:.1f}s",
 222:         }
 223: 
 224:     # 7. Physiological RR interval validation
 225:     peak_times = peaks / fs
 226:     rr_intervals = np.diff(peak_times)
 227: 
 228:     min_rr = 60.0 / max_bpm
 229:     max_rr = 60.0 / min_bpm
 230:     valid_rr_mask = (rr_intervals >= min_rr) & (rr_intervals <= max_rr)
 231: 
 232:     valid_rr = rr_intervals[valid_rr_mask]
 233:     if len(valid_rr) < 5:
 234:         qc_verdict = "WARNING_FEW_VALID_BEATS"
 235:     else:
 236:         qc_verdict = "PASS"
 237: 
 238:     mean_rr = float(np.mean(valid_rr)) if len(valid_rr) > 0 else np.nan
 239:     std_rr = float(np.std(valid_rr)) if len(valid_rr) > 1 else np.nan
 240:     rmssd = float(np.sqrt(np.mean(np.diff(valid_rr) ** 2)) * 1000.0) if len(valid_rr) > 2 else np.nan
 241:     inst_hr = 60.0 / rr_intervals
 242:     mean_hr = float(60.0 / mean_rr) if mean_rr > 0 else np.nan
 243: 
 244:     r_peaks_payload = {
 245:         "peaks": peaks,
 246:         "peak_times": peak_times,
 247:         "rr_intervals": rr_intervals,
 248:         "valid_rr_mask": valid_rr_mask,
 249:     }
 250:     sqi = compute_ecg_sqi(r_peaks_payload, duration_s=duration_s)
 251: 
 252:     return {
 253:         "status": "SUCCESS",
 254:         "peaks": peaks,
 255:         "peak_times": peak_times,
 256:         "rr_intervals": rr_intervals,
 257:         "valid_rr_mask": valid_rr_mask,
 258:         "inst_hr": inst_hr,
 259:         "valid_peak_count": len(peaks),
 260:         "mean_rr_s": mean_rr,
 261:         "std_rr_s": std_rr,
 262:         "rmssd_ms": rmssd,
 263:         "mean_hr_bpm": mean_hr,
 264:         "qc_verdict": qc_verdict,
 265:         "sqi_verdict": sqi["sqi_verdict"],
 266:         "sqi_coverage": sqi["beat_coverage_ratio"],
 267:         "sqi_max_gap_s": sqi["max_rr_gap_s"],
 268:         "sqi_result": sqi,
 269:         "notes": f"Detected {len(peaks)} peaks; {np.sum(valid_rr_mask)}/{len(rr_intervals)} valid RR intervals; SQI={sqi['sqi_verdict']}",
 270:     }
```

**State of Default Behavior & Reachability:**
- **Default Behavior:** Unchanged for all preexisting fields. Detection algorithm (Pan-Tompkins bandpass, squaring, moving window integration, adaptive peak detection, refinement) produces mathematically identical peaks, RR intervals, and `qc_verdict` ("PASS", "WARNING_FEW_VALID_BEATS", or "FAIL"). The dictionary now additionally returns SQI keys: `sqi_verdict`, `sqi_coverage`, `sqi_max_gap_s`, and `sqi_result`.
- **Original Behavior Reachability:** 100% backward compatible and reachable. Preexisting downstream consumers querying `peaks`, `rr_intervals`, or `qc_verdict` receive identical values as before.

---

### 1.5 `compute_ecg_sqi`
**File:** [`src/sync_validation/ecg_processor.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/ecg_processor.py#L273-L364) (Lines 273–364)

```python
 273: def compute_ecg_sqi(
 274:     r_peak_result: Dict[str, Any],
 275:     duration_s: float = 120.0,
 276:     coverage_threshold: float = 0.85,
 277:     max_gap_threshold_s: float = 3.0,
 278: ) -> Dict[str, Any]:
 279:     """Compute multi-parameter ECG Signal Quality Index (SQI) per ISS-08.
 280: 
 281:     Coverage Definition:
 282:       - Denominator: Total recording duration in seconds (duration_s, typically 120.0s).
 283:       - Numerator: Sum of durations of valid physiological RR intervals (sum(valid_rr)).
 284:       - Invalid/rejected RR intervals contribute 0.0 seconds to the coverage numerator.
 285:       - Requirement: beat_coverage > 0.85 (85%).
 286: 
 287:     Max Gap Definition:
 288:       - Evaluates the maximum time elapsed between consecutive valid R-peaks across the recording.
 289:       - Also checks lead-in from t=0s to first valid peak, and lead-out from last valid peak to duration_s.
 290:       - Requirement: max_rr_gap < 3.0s.
 291: 
 292:     Amplitude Stability:
 293:       - Marked UNSPECIFIED / NOT VALIDATED (no clinically validated threshold approved).
 294:       - Because this parameter remains unvalidated, a recording-level PASS cannot be granted.
 295: 
 296:     Verdict:
 297:       - 'SQI_FAIL': If coverage <= 0.85 or max_rr_gap >= 3.0s.
 298:       - 'SQI_PARTIAL': If coverage > 0.85 and max_rr_gap < 3.0s, pending amplitude stability validation.
 299:       - 'PASS': Prohibited (cannot be granted per gate rules).
 300:     """
 301:     peaks = r_peak_result.get("peaks", np.array([]))
 302:     peak_times = r_peak_result.get("peak_times", np.array([]))
 303:     rr_intervals = r_peak_result.get("rr_intervals", np.array([]))
 304:     valid_mask = r_peak_result.get("valid_rr_mask", np.array([]))
 305: 
 306:     if len(peaks) < 2 or len(rr_intervals) == 0 or len(valid_mask) == 0:
 307:         return {
 308:             "sqi_verdict": "SQI_FAIL",
 309:             "recording_level_pass": False,
 310:             "beat_coverage_ratio": 0.0,
 311:             "beat_coverage_s": 0.0,
 312:             "total_duration_s": duration_s,
 313:             "coverage_threshold": coverage_threshold,
 314:             "max_rr_gap_s": duration_s,
 315:             "max_gap_threshold_s": max_gap_threshold_s,
 316:             "amplitude_stability_status": "UNSPECIFIED / NOT VALIDATED",
 317:             "valid_beat_count": 0,
 318:             "total_beat_count": len(peaks),
 319:             "reason": "Insufficient detectable R-peaks (< 2)",
 320:         }
 321: 
 322:     valid_rr = rr_intervals[valid_mask]
 323:     valid_coverage_s = float(np.sum(valid_rr))
 324:     coverage_ratio = float(valid_coverage_s / duration_s) if duration_s > 0 else 0.0
 325: 
 326:     valid_indices = np.where(valid_mask)[0]
 327:     if len(valid_indices) == 0:
 328:         max_gap_s = duration_s
 329:     else:
 330:         valid_peak_idx = np.unique(np.concatenate([valid_indices, valid_indices + 1]))
 331:         valid_peak_times = peak_times[valid_peak_idx]
 332:         gaps = np.diff(valid_peak_times) if len(valid_peak_times) > 1 else np.array([duration_s])
 333:         start_gap = valid_peak_times[0] if len(valid_peak_times) > 0 else duration_s
 334:         end_gap = duration_s - valid_peak_times[-1] if len(valid_peak_times) > 0 else duration_s
 335:         all_gaps = np.concatenate([[start_gap], gaps, [end_gap]])
 336:         max_gap_s = float(np.max(all_gaps))
 337: 
 338:     coverage_pass = coverage_ratio > coverage_threshold
 339:     gap_pass = max_gap_s < max_gap_threshold_s
 340: 
 341:     if not coverage_pass or not gap_pass:
 342:         sqi_verdict = "SQI_FAIL"
 343:         reason = f"Coverage {coverage_ratio*100:.1f}% (need >85%) or max gap {max_gap_s:.2f}s (need <3.0s)"
 344:     else:
 345:         sqi_verdict = "SQI_PARTIAL"
 346:         reason = (
 347:             f"Coverage ({coverage_ratio*100:.1f}%) and max gap ({max_gap_s:.2f}s) pass; "
 348:             "amplitude stability UNSPECIFIED / NOT VALIDATED; recording-level PASS cannot be granted"
 349:         )
 350: 
 351:     return {
 352:         "sqi_verdict": sqi_verdict,
 353:         "recording_level_pass": False,
 354:         "beat_coverage_ratio": round(coverage_ratio, 4),
 355:         "beat_coverage_s": round(valid_coverage_s, 2),
 356:         "total_duration_s": duration_s,
 357:         "coverage_threshold": coverage_threshold,
 358:         "max_rr_gap_s": round(max_gap_s, 4),
 359:         "max_gap_threshold_s": max_gap_threshold_s,
 360:         "amplitude_stability_status": "UNSPECIFIED / NOT VALIDATED",
 361:         "valid_beat_count": int(np.sum(valid_mask)),
 362:         "total_beat_count": len(peaks),
 363:         "reason": reason,
 364:     }
```

---

### 1.6 `estimate_peak_frequency_parabolic`
**File:** [`src/sync_validation/cardiac_radar_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L33-L66) (Lines 33–66)

```python
  33: def estimate_peak_frequency_parabolic(
  34:     mags: np.ndarray,
  35:     freqs: np.ndarray,
  36:     mask: np.ndarray,
  37: ) -> float:
  38:     """3-point parabolic peak interpolation on frequency spectrum.
  39: 
  40:     Addresses ISS-09: Refines discrete peak frequency by fitting a parabola
  41:     through the peak bin and its two adjacent neighbors:
  42:         delta = (A_{k+1} - A_{k-1}) / (2 * (2*A_k - A_{k-1} - A_{k+1}))
  43:     reducing discretization error well below the native 6.0 bpm bin width.
  44:     """
  45:     sub_mags = mags[mask]
  46:     sub_freqs = freqs[mask]
  47:     if len(sub_mags) < 3:
  48:         return float(sub_freqs[np.argmax(sub_mags)]) if len(sub_mags) > 0 else 0.0
  49: 
  50:     k = int(np.argmax(sub_mags))
  51:     if k == 0 or k == len(sub_mags) - 1:
  52:         return float(sub_freqs[k])
  53: 
  54:     a_left = float(sub_mags[k - 1])
  55:     a_mid = float(sub_mags[k])
  56:     a_right = float(sub_mags[k + 1])
  57: 
  58:     denom = 2.0 * (2.0 * a_mid - a_left - a_right)
  59:     if abs(denom) < 1e-12:
  60:         return float(sub_freqs[k])
  61: 
  62:     delta = (a_right - a_left) / denom
  63:     delta = max(-0.5, min(0.5, delta))
  64: 
  65:     df = sub_freqs[1] - sub_freqs[0] if len(sub_freqs) > 1 else 0.0
  66:     return float(sub_freqs[k] + delta * df)
```

---

### 1.7 `estimate_window_hr_multi_estimator`
**File:** [`src/sync_validation/cardiac_radar_validator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/cardiac_radar_validator.py#L69-L110) (Lines 69–110)

```python
  69: def estimate_window_hr_multi_estimator(
  70:     w: np.ndarray,
  71:     rad_fs: float,
  72:     band: Tuple[float, float] = (0.8, 3.0),
  73: ) -> Dict[str, float]:
  74:     """Estimate cardiac HR across multiple frequency-domain estimators per ISS-09.
  75: 
  76:     Estimators:
  77:       1. 'unpadded_bin': Original unpadded FFT with discrete argmax bin selection.
  78:       2. 'parabolic': 3-point parabolic peak interpolation on unpadded FFT.
  79:       3. 'zeropad_4x': Exactly 4x zero-padding (N_fft = 4 * len(w)), providing spectral
  80:          interpolation (evaluation on a 4x finer frequency grid) with NO change in native resolution.
  81:       4. 'zeropad_4x_parabolic': Combined 4x zero-padding plus 3-point parabolic peak interpolation.
  82:     """
  83:     n_win = len(w)
  84:     w_win = w * np.hamming(n_win)
  85: 
  86:     # 1. Unpadded FFT
  87:     w_fft = np.fft.rfft(w_win)
  88:     freqs = np.fft.rfftfreq(n_win, d=1.0 / rad_fs)
  89:     mags = np.abs(w_fft)
  90:     mask = (freqs >= band[0]) & (freqs <= band[1])
  91: 
  92:     discrete_f = freqs[mask][np.argmax(mags[mask])] if np.any(mask) else np.nan
  93:     parabolic_f = estimate_peak_frequency_parabolic(mags, freqs, mask) if np.any(mask) else np.nan
  94: 
  95:     # 2. 4x Zero-padded FFT (exactly 4x window length: N_pad = 4 * n_win)
  96:     n_pad = 4 * n_win
  97:     w_fft_4x = np.fft.rfft(w_win, n=n_pad)
  98:     freqs_4x = np.fft.rfftfreq(n_pad, d=1.0 / rad_fs)
  99:     mags_4x = np.abs(w_fft_4x)
 100:     mask_4x = (freqs_4x >= band[0]) & (freqs_4x <= band[1])
 101: 
 102:     zeropad_f = freqs_4x[mask_4x][np.argmax(mags_4x[mask_4x])] if np.any(mask_4x) else np.nan
 103:     zeropad_parabolic_f = estimate_peak_frequency_parabolic(mags_4x, freqs_4x, mask_4x) if np.any(mask_4x) else np.nan
 104: 
 105:     return {
 106:         "unpadded_bin_bpm": float(discrete_f * 60.0) if np.isfinite(discrete_f) else np.nan,
 107:         "parabolic_bpm": float(parabolic_f * 60.0) if np.isfinite(parabolic_f) else np.nan,
 108:         "zeropad_4x_bpm": float(zeropad_f * 60.0) if np.isfinite(zeropad_f) else np.nan,
 109:         "zeropad_4x_parabolic_bpm": float(zeropad_parabolic_f * 60.0) if np.isfinite(zeropad_parabolic_f) else np.nan,
 110:     }
```

---

### 1.8 `categorize_monitor_latency`
**File:** [`src/sync_validation/runner.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/sync_validation/runner.py#L30-L74) (Lines 30–74)

```python
  30: def categorize_monitor_latency(
  31:     best_lag_s: float,
  32:     is_ambiguous: bool,
  33:     mae_improvement_bpm: float = 0.0,
  34: ) -> Tuple[str, str]:
  35:     """Categorize monitor HR latency relative to continuous ECG ground truth.
  36: 
  37:     Addresses ISS-07: Separates:
  38:       - Negative lags (tau <= -1s): 'NEGATIVE_LAG_OBSERVED' (monitor leads ECG, physically non-causal)
  39:       - Near-zero lags (|tau| <= 1s): 'NEAR_ZERO_LATENCY' (synchronous within 1s quantization)
  40:       - Small non-zero lags (1s < tau < 4s): 'SMALL_NONZERO_LAG'
  41:       - Large lags (tau >= 4s): 'EMPIRICAL_LATENCY_OBSERVED' (display / averaging delay)
  42:       - Low HRV: 'INCONCLUSIVE_LOW_HRV' (MAE curve flatness indicates low HR variance)
  43: 
  44:     Fixes reason string: Cites curve flatness ONLY when is_ambiguous is True.
  45:     """
  46:     if not np.isfinite(best_lag_s):
  47:         return "INCONCLUSIVE", "Insufficient valid HR data"
  48: 
  49:     if is_ambiguous:
  50:         return (
  51:             "INCONCLUSIVE_LOW_HRV",
  52:             f"Optimal lag {best_lag_s:+.0f}s is ambiguous; MAE curve flatness indicates low HR variance",
  53:         )
  54: 
  55:     if best_lag_s <= -1.0:
  56:         return (
  57:             "NEGATIVE_LAG_OBSERVED",
  58:             f"Optimal lag {best_lag_s:+.0f}s (negative shift implies monitor leads ECG; non-causal artifact)",
  59:         )
  60:     elif abs(best_lag_s) <= 1.0:
  61:         return (
  62:             "NEAR_ZERO_LATENCY",
  63:             f"Optimal lag {best_lag_s:+.0f}s within |tau| <= 1s threshold",
  64:         )
  65:     elif 1.0 < best_lag_s < 4.0:
  66:         return (
  67:             "SMALL_NONZERO_LAG",
  68:             f"Optimal lag +{best_lag_s:.0f}s (small positive shift 1s < tau < 4s, MAE improvement {mae_improvement_bpm:.2f} bpm)",
  69:         )
  70:     else:  # best_lag_s >= 4.0
  71:         return (
  72:             "EMPIRICAL_LATENCY_OBSERVED",
  73:             f"Optimal MAE at lag +{best_lag_s:.0f}s (MAE improvement {mae_improvement_bpm:.2f} bpm); reflects display/averaging delay",
  74:         )
```

---

## 2. STAGE 2 CLOSURE TESTS AUDIT

All 15 tests in [`tests/test_stage2_closure.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/tests/test_stage2_closure.py) are cataloged below:

| # | Test Name | Assertion Description | Exact Numeric Thresholds Used |
|---|---|---|---|
| 1 | `test_truncate_mismatched_durations_in_memory` | Asserts trailing radar samples truncated to match shorter respiration duration in-memory without altering source. | `common_duration_s == 119.53125s` ($\text{atol}=10^{-3}$), radar truncated to $\lfloor 119.53125 \times 333.333\rfloor = 39,843$, respiration = $30,600$. |
| 2 | `test_truncate_matching_durations` | Asserts zero samples discarded when input durations match. | `respiration_samples_excluded == 0`, `len(v_trunc) == 40000`, `len(r_trunc) == 30720`. |
| 3 | `test_clean_isolated_single_sample_nans` | Asserts isolated single-sample NaN ($N=1$) is linearly interpolated while source remains NaN. | `max_gap == 1`, `isolated_nan_count == 1`, `clean[2] == 14.0`. |
| 4 | `test_reject_multi_sample_nan_gaps` | Asserts multi-sample gap ($N=3$) is NOT interpolated and remains NaN. | `max_gap == 1`, `multi_sample_gap_count == 1`, `clean[1:4]` all NaN. |
| 5 | `test_mixed_isolated_and_multi_sample_nans` | Asserts isolated NaN is interpolated while adjacent multi-sample gap ($N=2$) is preserved. | `max_gap == 1`, `isolated_nan_count == 1`, `clean[2] == 14.0`, `clean[5]` and `clean[6]` both NaN. |
| 6 | `test_sqi_partial_on_good_ecg` | Asserts valid 60 bpm ECG yields SQI_PARTIAL due to unvalidated amplitude stability. | `coverage > 0.85`, `max_gap < 3.0s`, `sqi_verdict == 'SQI_PARTIAL'`, `recording_level_pass == False`. |
| 7 | `test_sqi_fail_on_large_gap` | Asserts ECG with a 5.5s gap between R-peaks fails SQI. | `max_gap >= 3.0s` (actual 5.5s), `sqi_verdict == 'SQI_FAIL'`, `recording_level_pass == False`. |
| 8 | `test_sqi_fail_on_low_coverage` | Asserts ECG with 41.7% valid beat coverage fails SQI. | `coverage < 0.85` (actual 41.7%), `sqi_verdict == 'SQI_FAIL'`, `recording_level_pass == False`. |
| 9 | `test_parabolic_peak_interpolation_accuracy` | Asserts parabolic peak and 4x zero-padded FFT refine 1.25 Hz sine closer than unpadded discrete bin. | `unpadded == 72.0` or `78.0 bpm` ($\text{atol}=0.2$), $\|f_{\text{parabolic}} - 75.0\| < \|f_{\text{unpadded}} - 75.0\|$, $\|f_{\text{pad4x}} - 75.0\| \le 1.5\text{ bpm}$. |
| 10 | `test_zero_shift_is_primary_metric_and_best_shift_diagnostic` | Asserts zero-shift MAE is reported as primary metric and best-shift as diagnostic only. | `primary_metric == 'zero_shift'`, `best_shift_role == 'diagnostic_exploratory_only'`. |
| 11 | `test_negative_lag_categorization` | Asserts $\tau = -3.0\text{ s}$ categorizes as NEGATIVE_LAG_OBSERVED and does not cite curve flatness. | $\tau = -3.0\text{ s}$, `category == 'NEGATIVE_LAG_OBSERVED'`, `'curve flatness' \notin reason`. |
| 12 | `test_near_zero_lag_categorization` | Asserts $\tau = 0.0\text{ s}$ and $\tau = 1.0\text{ s}$ categorize as NEAR_ZERO_LATENCY without citing flatness. | $\tau \in \{0.0, 1.0\}\text{ s}$, `category == 'NEAR_ZERO_LATENCY'`, `'curve flatness' \notin reason`. |
| 13 | `test_small_nonzero_lag_categorization` | Asserts $\tau = +3.0\text{ s}$ categorizes as SMALL_NONZERO_LAG without citing flatness. | $\tau = +3.0\text{ s}$, `category == 'SMALL_NONZERO_LAG'`, `'curve flatness' \notin reason`. |
| 14 | `test_empirical_latency_categorization` | Asserts $\tau = +6.0\text{ s}$ categorizes as EMPIRICAL_LATENCY_OBSERVED without citing flatness. | $\tau = +6.0\text{ s}$, `category == 'EMPIRICAL_LATENCY_OBSERVED'`, `'curve flatness' \notin reason`. |
| 15 | `test_ambiguous_low_hrv_cites_curve_flatness` | Asserts `is_ambiguous=True` assigns INCONCLUSIVE_LOW_HRV and cites curve flatness. | `is_ambiguous == True`, `category == 'INCONCLUSIVE_LOW_HRV'`, `'curve flatness' \in reason`. |

**Random Seed Audit:**  
Confirmed: Zero tests use pseudo-random number generators (`np.random`, `random`). All input signals, timestamps, and parameters are constructed using fixed arrays (`np.sin`, `np.arange`, `np.ones`). Test determinism is 100%.

---

## 3. NaN SAFETY & FILTFILT PROTECTION CHECK

### 3.1 Raw Mindray Dataset Audit (48 Files)
A read-only scan over all 48 Mindray reference `.mat` files across subjects VS01–VS24 was executed:

```
Total Mindray files found: 48
Total single-sample NaNs across all files: 5629
Total multi-sample NaN gaps (>= 2 contiguous) across all files: 0
Total NaNs at index 0 or index N-1 across all files: 1
Files with multi-sample gaps: []
Files with edge NaNs: [('VS10_Resting_Mindray.mat', 1)]
```

**Edge NaN Analysis (`VS10_Resting_Mindray.mat`):**
- Index: `index 0 == NaN` (single sample delimiter).
- Handling: In `clean_ecg_isolated_nans`, `np.interp(0, valid_indices, ecg[valid_indices])` returns `clean[1]` via numpy boundary evaluation, leaving zero remaining NaNs and maintaining signal integrity.

### 3.2 Downstream `filtfilt` Failure Mode
If a multi-sample NaN gap existed in raw data:
1. `clean_ecg_nans` (with default `only_isolated=True`) refrains from interpolating any run of length $\ge 2$, preserving the NaNs in the array.
2. When the array is passed to `signal.filtfilt(b, a, ecg)` in `detect_r_peaks`:
   - Due to the bidirectional autoregressive recurrence $y[n] = \sum b_k x[n-k] - \sum a_k y[n-k]$, a single uninterpolated NaN propagates forward and backward across every sample: `np.isnan(ecg_filt).all() == True`.
   - The moving-window integration `mwa` evaluates to all NaNs; `np.percentile(mwa, 90)` returns NaN; `signal.find_peaks` detects 0 peaks.
   - The conditional `if len(peaks) < 3:` fires cleanly, returning:
     - `status`: `"INSUFFICIENT_PEAKS"`
     - `qc_verdict`: `"FAIL"`
     - `valid_peak_count`: `0`
     - `notes`: `"Only 0 R-peaks detected across ..."`
3. **Conclusion:** Downstream `filtfilt` **fails cleanly and loudly via explicit fail-safe guard**, never silently fabricating corrupted peak locations.

---

## 4. ISS-07 MONITOR LATENCY BOUNDARY AUDIT

`categorize_monitor_latency` was evaluated across the test vector $\tau \in [-5.0, -1.1, -1.0, -0.9, -0.1, 0.0, 0.1, 0.9, 1.0, 1.1, 2.9, 3.0, 3.1, 6.0, 10.0]$:

| tau (s) | is_ambiguous | category | reason |
|---|---|---|---|
|  -5.0 | False | NEGATIVE_LAG_OBSERVED | Optimal lag -5s (negative shift implies monitor leads ECG; non-causal artifact) |
|  -1.1 | False | NEGATIVE_LAG_OBSERVED | Optimal lag -1s (negative shift implies monitor leads ECG; non-causal artifact) |
|  -1.0 | False | NEGATIVE_LAG_OBSERVED | Optimal lag -1s (negative shift implies monitor leads ECG; non-causal artifact) |
|  -0.9 | False | NEAR_ZERO_LATENCY | Optimal lag -1s within \|tau\| <= 1s threshold |
|  -0.1 | False | NEAR_ZERO_LATENCY | Optimal lag -0s within \|tau\| <= 1s threshold |
|  +0.0 | False | NEAR_ZERO_LATENCY | Optimal lag +0s within \|tau\| <= 1s threshold |
|  +0.1 | False | NEAR_ZERO_LATENCY | Optimal lag +0s within \|tau\| <= 1s threshold |
|  +0.9 | False | NEAR_ZERO_LATENCY | Optimal lag +1s within \|tau\| <= 1s threshold |
|  +1.0 | False | NEAR_ZERO_LATENCY | Optimal lag +1s within \|tau\| <= 1s threshold |
|  +1.1 | False | SMALL_NONZERO_LAG | Optimal lag +1s (small positive shift 1s < tau < 4s, MAE improvement 1.23 bpm) |
|  +2.9 | False | SMALL_NONZERO_LAG | Optimal lag +3s (small positive shift 1s < tau < 4s, MAE improvement 1.23 bpm) |
|  +3.0 | False | SMALL_NONZERO_LAG | Optimal lag +3s (small positive shift 1s < tau < 4s, MAE improvement 1.23 bpm) |
|  +3.1 | False | SMALL_NONZERO_LAG | Optimal lag +3s (small positive shift 1s < tau < 4s, MAE improvement 1.23 bpm) |
|  +6.0 | False | EMPIRICAL_LATENCY_OBSERVED | Optimal MAE at lag +6s (MAE improvement 1.23 bpm); reflects display/averaging delay |
| +10.0 | False | EMPIRICAL_LATENCY_OBSERVED | Optimal MAE at lag +10s (MAE improvement 1.23 bpm); reflects display/averaging delay |
|  -5.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag -5s is ambiguous; MAE curve flatness indicates low HR variance |
|  -1.1 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag -1s is ambiguous; MAE curve flatness indicates low HR variance |
|  -1.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag -1s is ambiguous; MAE curve flatness indicates low HR variance |
|  -0.9 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag -1s is ambiguous; MAE curve flatness indicates low HR variance |
|  -0.1 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag -0s is ambiguous; MAE curve flatness indicates low HR variance |
|  +0.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +0s is ambiguous; MAE curve flatness indicates low HR variance |
|  +0.1 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +0s is ambiguous; MAE curve flatness indicates low HR variance |
|  +0.9 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +1s is ambiguous; MAE curve flatness indicates low HR variance |
|  +1.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +1s is ambiguous; MAE curve flatness indicates low HR variance |
|  +1.1 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +1s is ambiguous; MAE curve flatness indicates low HR variance |
|  +2.9 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +3s is ambiguous; MAE curve flatness indicates low HR variance |
|  +3.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +3s is ambiguous; MAE curve flatness indicates low HR variance |
|  +3.1 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +3s is ambiguous; MAE curve flatness indicates low HR variance |
|  +6.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +6s is ambiguous; MAE curve flatness indicates low HR variance |
| +10.0 | True  | INCONCLUSIVE_LOW_HRV | Optimal lag +10s is ambiguous; MAE curve flatness indicates low HR variance |

### Boundary Defect Identified at $\tau = -1.0\text{ s}$:
- **Defect Description:** At $\tau = -1.0\text{ s}$ with `is_ambiguous=False`, line 55 (`if best_lag_s <= -1.0:`) evaluates to `True`, categorizing $\tau = -1.0\text{ s}$ as `NEGATIVE_LAG_OBSERVED`. However, line 60 (`elif abs(best_lag_s) <= 1.0:`) is shadowed for $\tau = -1.0\text{ s}$. For $\tau = +1.0\text{ s}$, line 55 is `False` and line 60 fires, categorizing $+1.0\text{ s}$ as `NEAR_ZERO_LATENCY`.
- **Asymmetry:** An optimal lag of $-1.0\text{ s}$ is categorized as non-causal negative lag, whereas $+1.0\text{ s}$ is categorized as near-zero synchronous latency. To be symmetric with $|\tau| \le 1.0\text{ s}$, the negative condition should be strict inequality: `best_lag_s < -1.0`.
- **Action Taken:** In accordance with strict Stage 2V read-only instructions, this defect is formally recorded here and **NOT** modified in source code.

---

## 5. SQI BOUNDARY AUDIT

`compute_ecg_sqi` was evaluated on synthetic RR sequences:

| Scenario | Coverage Ratio | Max Gap (s) | Verdict | Recording Pass | Amplitude Status | Reason |
|---|---|---|---|---|---|---|
| Coverage 84% (against 85% threshold) | 0.84 | 1.0 | SQI_FAIL | False | UNSPECIFIED / NOT VALIDATED | Coverage 84.0% (need >85%) or max gap 1.00s (need <3.0s) |
| Coverage 86% (against 85% threshold) | 0.86 | 1.0 | SQI_PARTIAL | False | UNSPECIFIED / NOT VALIDATED | Coverage (86.0%) and max gap (1.00s) pass; amplitude stability UNSPECIFIED / NOT VALIDATED; recording-level PASS cannot be granted |
| Max gap 2.9s (against 3.0s threshold) | 0.96 | 2.9 | SQI_PARTIAL | False | UNSPECIFIED / NOT VALIDATED | Coverage (96.0%) and max gap (2.90s) pass; amplitude stability UNSPECIFIED / NOT VALIDATED; recording-level PASS cannot be granted |
| Max gap 3.0s (against 3.0s threshold) | 0.95 | 3.0 | SQI_FAIL | False | UNSPECIFIED / NOT VALIDATED | Coverage 95.0% (need >85%) or max gap 3.00s (need <3.0s) |
| Max gap 3.1s (against 3.0s threshold) | 0.95 | 3.1 | SQI_FAIL | False | UNSPECIFIED / NOT VALIDATED | Coverage 95.0% (need >85%) or max gap 3.10s (need <3.0s) |
| 0 beats | 0.0 | 100.0 | SQI_FAIL | False | UNSPECIFIED / NOT VALIDATED | Insufficient detectable R-peaks (< 2) |
| 5 beats | 0.04 | 86.0 | SQI_FAIL | False | UNSPECIFIED / NOT VALIDATED | Coverage 4.0% (need >85%) or max gap 86.00s (need <3.0s) |

**Confirmation:**
The verdict is **NEVER** `PASS`. It is strictly constrained to `SQI_PARTIAL` or `SQI_FAIL`, and `recording_level_pass` evaluates to `False` across all configurations.

---

## 6. ISS-12 DYNAMIC ARRAY TRUNCATION IN-MEMORY

`truncate_respiration_dynamic_length_in_memory` was executed on raw files `VS24_Resting` (mismatched) and `VS01_Resting` (matched):

### 6.1 `VS24_Resting`
```
=== VS24_Resting ===
Radar input length: 40000 samples, input duration: 120.0 s
Respiration input length: 30600 samples, input duration: 119.53125 s
max_seconds computed (common_duration_s): 119.53125 s
Radar output length: 39843 samples, output duration: 119.52900000000001 s
Respiration output length: 30600 samples, output duration: 119.53125 s
Radar samples discarded: 157
Respiration samples discarded: 0
Any data discarded: True
has_length_mismatch: True
```

### 6.2 `VS01_Resting` (Normal Recording)
```
=== VS01_Resting ===
Radar input length: 40000 samples, input duration: 120.0 s
Respiration input length: 30720 samples, input duration: 120.0 s
max_seconds computed (common_duration_s): 120.0 s
Radar output length: 40000 samples, output duration: 120.0 s
Respiration output length: 30720 samples, output duration: 120.0 s
Radar samples discarded: 0
Respiration samples discarded: 0
Any data discarded: False
has_length_mismatch: False
```

---

## 7. DETERMINISM AUDIT (PYTEST PASS LINES)

### 7.1 Stage 2 Test Suite (5 Consecutive Runs)
Command: `pytest tests/test_stage2_closure.py -q`

- **Run 1:** `15 passed in 3.30s`
- **Run 2:** `15 passed in 1.90s`
- **Run 3:** `15 passed in 1.90s`
- **Run 4:** `15 passed in 1.90s`
- **Run 5:** `15 passed in 1.89s`

### 7.2 Full Repository Test Suite (2 Consecutive Runs)
Command: `pytest tests/ -q`

- **Run 1:** `127 passed, 6 warnings in 30.91s`
- **Run 2:** `127 passed, 6 warnings in 23.77s`

---

## 8. `lag_threshold` SEARCH

A recursive search across all text, markdown, CSV, and JSON files under `outputs/` was executed:
- **Files searched:** `outputs/**/*.md`, `outputs/**/*.csv`, `outputs/**/*.txt`, `outputs/**/*.json`
- **Search term:** `lag_threshold`
- **Total occurrences found:** `0`

`lag_threshold` does not appear anywhere under `outputs/`.

---

## 9. MAE DEMONSTRATION DISCLAIMER

The 3-recording old-vs-new MAE comparison presented in the Stage 2 terminal output was an informal, terminal-only demonstration designed solely to illustrate algorithm convergence. It was **NOT** saved to any file, was **NOT** part of any authorized output artifact, and does **NOT** constitute validated empirical evidence.

---

## 10. SUMMARY AND GATE VERDICT

- **Stage 2 Verification:** COMPLETE and fully verified.
- **Phase 2A Gate Status:** Remains strictly **OPEN**.
- **Source Code Integrity:** All preexisting tests passing (127/127). No unauthorized file writes or modifications performed.
