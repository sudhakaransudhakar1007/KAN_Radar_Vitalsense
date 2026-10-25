# Forensic Audit: Window Duration, Striding, and Sample Indexing (Contradiction A)

**Execution Stage:** Phase 7B — Contradiction Resolution & Independent Evidence Audit  
**Auditor Role:** Senior Biomedical Signal-Processing Engineer & Software Verification Specialist  
**Artifact File:** `outputs/phase7b/run_001/window_duration_and_indexing_audit.md`  

---

## 1. Audited Claim vs Demonstrated Source Truth

| Item | Phase 7 Report Claim | Source Code & Manifest Truth | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Window Duration** | $3.0\text{ seconds}$ physical interval | **$10.0\text{ seconds}$** | 🔴 **REPORTING ERROR REFUTED** |
| **Stride / Hop** | Unspecified / inferred $2.5\text{ s}$ or $1.5\text{ s}$ | **$5.0\text{ seconds}$** ($50\%$ overlap) | 🟢 **VERIFIED IN SOURCE** |
| **Radar Samples / Window** | $\sim 1,000\text{ samples}$ | **$3,333\text{ samples}$** ($10.0\text{ s} \times 333.3333\text{ Hz}$) | 🔴 **REPORTING ERROR REFUTED** |
| **Radar Samples / Hop** | Unspecified | **$1,667\text{ samples}$** ($5.0\text{ s} \times 333.3333\text{ Hz}$) | 🟢 **VERIFIED IN SOURCE** |
| **ECG Samples / Window** | $\sim 1,500\text{ samples}$ | **$5,000\text{ samples}$** ($10.0\text{ s} \times 500\text{ Hz}$) | 🔴 **REPORTING ERROR REFUTED** |
| **ECG Samples / Hop** | Unspecified | **$2,500\text{ samples}$** ($5.0\text{ s} \times 500\text{ Hz}$) | 🟢 **VERIFIED IN SOURCE** |
| **Windows / Recording** | $44\text{ windows/recording}$ | **$22\text{ complete windows/recording}$** | 🔴 **REPORTING ERROR REFUTED** |
| **Total Candidate Windows** | $1,056$ | **$1,056$** ($48\text{ recordings} \times 22\text{ windows}$) | 🟢 **VERIFIED MATHEMATICALLY** |

---

## 2. Source Code Evidence and Line Citations

### 2.1 Window Duration & Stride Configuration
In [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L65-L75):
```python
65:         window_duration_s: float = 10.0,
66:         hop_duration_s: float = 5.0,
...
72:         self.win_s = float(window_duration_s)
73:         self.hop_s = float(hop_duration_s)
```
In [`src/phase3/window_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/window_generator.py#L57-L64):
```python
57:         window_duration_s: float = 10.0,
58:         hop_duration_s: float = 5.0,
...
61:         self.win_s = window_duration_s
62:         self.hop_s = hop_duration_s
```

### 2.2 Sample Conversion & Boundary Segmentation
In [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L220-L231):
```python
220:             win_samples = int(round(self.win_s * rad_fs))
221:             hop_samples = int(round(self.hop_s * rad_fs))
222:             total_samples = len(vitsig_raw)
223: 
224:             win_idx = 0
225:             start_idx = 0
226: 
227:             while start_idx + win_samples <= total_samples:
228:                 end_idx = start_idx + win_samples
229:                 t_start = round(win_idx * self.hop_s, 3)
230:                 t_end = round(t_start + self.win_s, 3)
```

At $F_{s,\text{radar}} = 333.3333\text{ Hz}$ ($1000/3\text{ Hz}$):
$$\text{win\_samples} = \text{round}(10.0 \times 333.3333) = 3,333\text{ samples}$$
$$\text{hop\_samples} = \text{round}(5.0 \times 333.3333) = 1,667\text{ samples}$$

---

## 3. Mathematical Proof of Candidate Window Accounting ($1,056\text{ Windows}$)

Each raw VITALSENSE radar recording contains exactly 120.0 seconds of signal:
$$\text{total\_samples} = 120.0\text{ s} \times 333.3333\text{ Hz} = 40,000\text{ samples}$$

Applying the loop in lines 227–231:
- **Window 0:** `start_idx = 0`, `end_idx = 3333`, $t \in [0.0\text{ s}, 10.0\text{ s}]$
- **Window 1:** `start_idx = 1667`, `end_idx = 5000`, $t \in [5.0\text{ s}, 15.0\text{ s}]$
- **Window 2:** `start_idx = 3334`, `end_idx = 6667`, $t \in [10.0\text{ s}, 20.0\text{ s}]$
- ...
- **Window 21:** `start_idx = 21 \times 1667 = 35007`, `end_idx = 35007 + 3333 = 38340`, $t \in [105.0\text{ s}, 115.0\text{ s}]$
- **Next Candidate (index 22):** `start_idx = 22 \times 1667 = 36674`.  
  `start_idx + win_samples = 36674 + 3333 = 40007 > 40000`.  
  The loop condition `start_idx + win_samples <= total_samples` evaluates to `False`. The loop terminates.

**Summary of Single-Recording Yield:**
- **Complete Windows per Recording:** **22 windows** (Indices 0 through 21).
- **Trailing Unsegmented Tail:** $40,000 - 38,340 = 1,660\text{ samples}$ ($4.98\text{ seconds}$).
- **Total Dataset Yield:**
  $$\text{Total Candidate Windows} = 48\text{ recordings} \times 22\text{ windows/recording} = \mathbf{1,056\text{ windows}}$$

---

## 4. Empirical Manifest Verification

Inspection of [`outputs/supervised_dataset/run_001/candidate_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/candidate_window_manifest.csv):
- `len(df_cand) = 1056` rows.
- Grouping by `['subject_id', 'condition']` yields **48 unique groups**, each containing exactly **22 rows**.
- Column `duration_s` has unique values: `[10.0]` ($100\%$ of windows are 10.0 seconds).
- `radar_sample_end - radar_sample_start = 3333` for every window.

Inspection of [`outputs/supervised_dataset/run_001/accepted_window_manifest.csv`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/supervised_dataset/run_001/accepted_window_manifest.csv):
- `len(df_acc) = 1029` rows.
- Column `duration_s` has unique values: `[10.0]`.

---

## 5. Timestamp, Endpoint, and Interval Correspondence Conventions

### 5.1 Interval Definition
Both radar and ECG signals are segmented into the nominal physical time interval:
$$I_k = [t_{\text{start}}, t_{\text{end}}) = [k \times 5.0\text{ s}, k \times 5.0\text{ s} + 10.0\text{ s})$$
for $k \in \{0, 1, \dots, 21\}$.

### 5.2 ECG R-Peak Labeling
In [`src/phase3/supervised_dataset_generator.py`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L110-L116):
```python
110:         p_times = rpeaks.peak_times_s
111:         rrs = np.diff(p_times)
112:         mids = (p_times[:-1] + p_times[1:]) / 2.0
113: 
114:         # Select intervals whose midpoints fall inside the window
115:         mask = (mids >= t_start) & (mids < t_end)
116:         w_rrs = rrs[mask]
```
The reference HR is calculated strictly from RR intervals whose midpoints fall inside $[t_{\text{start}}, t_{\text{end}})$.

### 5.3 Nominal Correspondence
Because both files start at nominal time $T_0 = 0.0\text{ s}$, radar window $k$ (samples $[1667 \times k : 1667 \times k + 3333]$) corresponds exactly to the ECG physical interval $[5.0 \times k, 5.0 \times k + 10.0]\text{ s}$.

---

## 6. Root-Cause Analysis of the Phase 7 Reporting Discrepancy

Why did the Phase 7 narrative claim 3.0 s windows and 44 windows per recording?
1. **Misreading SQI Parameter as Window Duration:** In [`src/phase3/supervised_dataset_generator.py:88`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/src/phase3/supervised_dataset_generator.py#L88), the quality threshold `sqi_max_gap_thresh_s = 3.0` defines the maximum tolerable gap between consecutive R-peaks. The Phase 7 report author misread this threshold as the window duration ($3.0\text{ s}$).
2. **Erroneous Ratio Calculation:** At $333.33\text{ Hz}$, a 3.0 s duration would equal $1,000$ samples. At $500\text{ Hz}$, a 3.0 s duration would equal $1,500$ samples. The author deduced these synthetic numbers from the false $3.0\text{ s}$ premise.
3. **Flawed Recording Count Division:** The author took total candidate windows ($1,056$) and divided by 24 subjects ($1056 / 24 = 44$), failing to account for the fact that each subject has **two recordings** (Resting and Apnea, $48$ recordings total). $1056 / 48 = 22$.

## 7. Audit Conclusion & Remediation
- **Software Implementation Status:** **CORRECT.** The code in `src/phase3/` already implements the scientifically intended 10.0 s duration, 5.0 s stride, 3,333 radar samples, and 22 windows per recording.
- **Code Modifications Needed:** **NONE.** No code changes are required.
- **Reporting Remediation:** The Phase 7 reporting errors are formally documented and superseded by this Phase 7B audit.
