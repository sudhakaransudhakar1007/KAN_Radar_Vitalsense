# Forensic Audit: Filter Causality, Edge Effects, and Streaming Applicability (Contradiction E)

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Biomedical Signal-Processing Engineer & DSP Auditor  
**Artifact File:** `outputs/phase7b/run_001/filter_causality_and_edge_effects_audit.md`  

---

## 1. Audited Claim vs Demonstrated DSP Truth

| Dimension | Phase 7 Report Claim | Source Code & Signal Processing Truth | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Filter Causality** | Described as "causal" in executive text | Strictly **NON-CAUSAL** (`scipy.signal.filtfilt`) | 🔴 **TERMINOLOGY ERROR REFUTED** |
| **Phase Response** | Zero-phase forward-backward filtering | **Zero-phase response** ($\angle H(e^{j\omega}) = 0$) | 🟢 **CONFIRMED ACCURATE** |
| **Filtering Scope** | "Zero leakage windowing" | Applied to **entire 120s recording** before windowing | 🟢 **CONFIRMED FROM CODE** |
| **Future Sample Influence** | Implied absent by "causal" label | **Yes:** backward pass incorporates future samples | 🔴 **CORRECTED** |
| **Boundary / Edge Effects** | Unanalyzed | **Present at recording ends** via reflection padding | 🟡 **DOCUMENTED LIMITATION** |
| **Offline Retrospective Study** | Applicable | **Fully valid and standard** for retrospective ML | 🟢 **SCIENTIFICALLY DEFENSIBLE** |
| **Real-Time Streaming** | Implied applicable | **Cannot be deployed in streaming without redesign** | 🔴 **SCOPE CLARIFIED** |

---

## 2. Source Code Implementation Analysis

In [`src/phase3/radar_preprocessing.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/radar_preprocessing.py#L73-L100):
```python
73:     def apply_bandpass(
74:         self,
75:         signal_array: np.ndarray,
76:         fs_hz: float,
77:         low_hz: float,
78:         high_hz: float,
79:         order: int = 3,
80:         causal: bool = False,
81:     ) -> Tuple[np.ndarray, bool, str]:
...
89:         b, a = signal.butter(order, wn, btype="bandpass")
90: 
91:         if causal:
92:             # Causal IIR for real-time simulation (has phase distortion and group delay)
93:             y = signal.lfilter(b, a, x)
94:             method = "causal_lfilter"
95:         else:
96:             # Zero-phase filtfilt for offline retrospective training
97:             y = signal.filtfilt(b, a, x)
98:             method = "zero_phase_filtfilt"
```

In [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L186-L191):
```python
186:             # 2. Preprocess Radar (Cardiac 0.8 - 3.0 Hz bandpass)
187:             vitsig_filt, filter_ok, filter_note = self.radar_prep.apply_bandpass(
188:                 vitsig_raw, rad_fs, low_hz=0.8, high_hz=3.0, order=3
189:             )
190:             filter_name = "butterworth_0.8_3.0hz_zero_phase_order3"
```
Because `causal` defaults to `False`, the pipeline executes `scipy.signal.filtfilt(b, a, vitsig_raw)` on the continuous 120-second array ($40,000$ samples) prior to window slicing.

---

## 3. Detailed Answers to the Six Mandated Audit Questions

### 1. Whether the filter is causal or non-causal?
**Determination: Strictly NON-CAUSAL.**  
The mathematical operation of `scipy.signal.filtfilt` executes a two-pass recursive process:
1. Forward pass: $w[n] = \sum_{k=0}^{M} b_k x[n-k] - \sum_{k=1}^{N} a_k w[n-k]$ for $n = 0, \dots, L-1$.
2. Time-reversal: $\tilde{w}[n] = w[L - 1 - n]$.
3. Reverse pass: $v[n] = \sum_{k=0}^{M} b_k \tilde{w}[n-k] - \sum_{k=1}^{N} a_k v[n-k]$ for $n = 0, \dots, L-1$.
4. Final time-reversal: $y[n] = v[L - 1 - n]$.

Because the impulse response $h[n]$ satisfies $h[-n] = h[n] \ne 0$ for $n < 0$, the filter is strictly non-causal.

### 2. Whether filtering occurs on the entire recording or independently inside each window?
**Determination: Entire Recording.**  
Line 187 passes the entire unsegmented recording `vitsig_raw` ($40,000$ samples) into `apply_bandpass`. Candidate windows are extracted from `vitsig_raw` (or `vitsig_filt`) subsequently in lines 227–231 via slicing:
`start_idx : start_idx + win_samples`
Filtering is **never** applied independently inside individual 10-second window blocks.

### 3. Whether future samples influence the filtered output at a given time?
**Determination: YES.**  
Because of the backward pass in `filtfilt`, the sample $y[n]$ at time $t_n$ is a linear combination of both past samples ($x[k]$ for $k < n$) and future samples ($x[k]$ for $k > n$). For example, the filtered cardiac signal at $t = 10.0\text{ s}$ is influenced by radar reflections occurring at $t = 15.0\text{ s}$, $20.0\text{ s}$, and beyond.

### 4. Whether padding or edge effects can affect window boundaries?
**Determination: YES, at recording endpoints.**  
`scipy.signal.filtfilt` mitigates boundary discontinuities using odd-reflection padding:
$$\text{padlen} = 3 \times \max(\text{len}(a), \text{len}(b))$$
For an order-3 Butterworth filter, `padlen` is small ($\sim 21$ samples, $\sim 0.063\text{ s}$).
- For interior windows ($k \in [1, 20]$, covering $t \in [5.0\text{ s}, 110.0\text{ s}]$), the filter transient has decayed to zero ($> 5\text{ seconds}$ from the boundaries), and no boundary padding artifacts exist.
- For Window 0 ($t \in [0.0\text{ s}, 10.0\text{ s}]$), the initial $\sim 0.1\text{ s}$ contains minor filter start-up transients from reflection padding.
- For Window 21 ($t \in [105.0\text{ s}, 115.0\text{ s}]$), the trailing samples end at $115.0\text{ s}$, safely buffered from the recording end ($120.0\text{ s}$) by the $4.98\text{ s}$ excluded tail.

### 5. Whether the method is suitable for offline retrospective evaluation?
**Determination: YES, Scientifically Standard and Recommended.**  
In retrospective biomedical ML research, zero-phase filtering is the gold standard because it guarantees **zero phase distortion** ($\angle H(e^{j\omega}) = 0$) and **zero group delay** ($\tau_g(\omega) = 0$). Peak maxima and minima in the radar vital sign signal occur at the exact physical moment of cardiac contraction, allowing direct time alignment with ECG R-peaks without artificial group-delay calibration.

### 6. Whether it is suitable for a claimed real-time streaming implementation without modification?
**Determination: NO.**  
A real-time edge embedded system (e.g., monitoring a patient in real time) receives radar reflections sequentially and cannot access future radar samples. To deploy this framework in a real-time streaming context, the system must either:
1. Transition to a causal IIR filter (`signal.lfilter`), which introduces non-linear phase distortion and a frequency-dependent group delay ($\sim 0.15 - 0.35\text{ s}$) that must be calibrated; or
2. Use a linear-phase FIR filter with constant group delay, introducing an intentional algorithmic latency equal to $(N-1)/(2 F_s)$; or
3. Implement block-based overlap-add/overlap-save filtering with trailing-window latency.

---

## 4. Audit Conclusion & Remediation
- **Terminology Correction:** Describing the current filtering pipeline as "causal" in any project document is scientifically incorrect. The correct designation is **"Offline Zero-Phase Forward-Backward Bandpass Filter"**.
- **Code Modifications Needed:** **NONE.** The code in `src/phase3/radar_preprocessing.py` explicitly supports both `causal=False` (default zero-phase) and `causal=True` (`signal.lfilter`). The retrospective training pipeline correctly uses zero-phase `filtfilt`.
- **Reporting Remediation:** All documentation must clearly distinguish between the current retrospective zero-phase evaluation and future real-time streaming deployment requirements.
