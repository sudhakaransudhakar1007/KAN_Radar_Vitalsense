# Stage 2H Notes — Alignment Analysis & Boundary Findings

## 1. VS24_Resting Head vs. Tail Truncation Analysis (G9 Rephrased & Range-Based Argument)

`VS24_Resting_Mindray.mat` contains 30,600 respiration samples at $256\text{ Hz}$ ($119.53125\text{ s}$), leaving 120 missing samples ($0.46875\text{ s}$) relative to the full $120.0\text{ s}$ radar acquisition ($40,000$ samples at $333.3333\text{ Hz}$).

### Empirical Cross-Correlation Comparison:
- **Tail-Truncation Assumption (Standard Runner):**
  - Truncates trailing samples after resampling to $2000\text{ Hz}$ ($0.5\text{ ms}$ grid).
  - Optimal respiratory lag: **$-3.0\text{ ms}$** (evaluated on discrete $0.5\text{ ms}$ grid).
  - Cross-correlation: **$0.9044$**.
- **Head-Trim Assumption (Hypothetical Late Start):**
  - Trims first $0.46875\text{ s}$ ($156$ samples at $333.3333\text{ Hz}$) from radar signal head to match respiration start.
  - Optimal respiratory lag: **$+459.5\text{ ms}$**.
  - Cross-correlation: **$0.9007$**.
  - Net shift: **$+462.5\text{ ms}$** ($\approx 0.4625\text{ s}$), corresponding directly to the $0.46875\text{ s}$ truncation duration.

### Scientific Evaluation & Range-Based Argument:
1. **Range-Based Consistency:** The optimal lag under the tail-truncation assumption ($-3.0\text{ ms}$) lies squarely within the $[-33.5, +24.5]\text{ ms}$ range observed across the other 47 dataset recordings when using the authors' raw (DC-sensitive) lags, and within $[-30.0, +30.0]\text{ ms}$ when using the demeaned pipeline lags. In sharp contrast, the $+459.5\text{ ms}$ lag under the head-trim assumption is a massive outlier ($> 13\times$ larger than the maximum absolute lag of any other recording), caused by shifting the full 120-second signal by $0.46875\text{ s}$ ($156$ radar samples).
2. **Timing Boundary Constraint:** Hardware timing was not verified and cannot be verified without physical clock access, shared hardware triggers, or pulse-per-second (PPS) synchronization between the separate digitizers. The $-3.0\text{ ms}$ peak is an empirical alignment on an upsampled $2000\text{ Hz}$ software grid from unsynchronized clocks (radar $333.33\text{ Hz}$, Mindray $256\text{ Hz}$), confirming nominal acquisition alignment at $t = 0\text{ s}$ while hardware clock synchronization remains strictly **`UNVERIFIED`**.

---

## 2. Decoupled Status v3 Reconciliation (H1 & H2)

- **Recording-Level SQI Pass Prohibited:** Evaluated in-memory via `compute_ecg_sqi`. All 48 recordings exhibit `SQI_PARTIAL` (beat coverage $> 85\%$ and max RR gap $< 3.0\text{ s}$); zero recordings receive literal `PASS` because ECG amplitude stability criteria remain `UNSPECIFIED / NOT VALIDATED`.
- **Condition-Wide Mapping:** Section 13.1 status mapping correctly assigns `CONSISTENT_NOT_PROVEN` to all 24 Resting pairs and `INCONCLUSIVE` to all 24 Apnea pairs. The unvalidated $r \ge 0.40$ threshold is isolated to `respiratory_corr_below_0p40_flag` (True for `VS02`, `VS18`, `VS20` in Resting, and 13 Apnea recordings).

---

## 3. Window Count Accounting: Phase 3 vs. G3 Gate (H7 & J3)

- **G3 Gate Diagnostic:** Evaluates continuous-time intervals ($0, 5, \dots, 110\text{ s}$), producing exactly **23 windows** spanning $120.0\text{ s}$ ($1,104$ total across 48 recordings).
- **Phase 3 Window Generator:** Operates via cumulative integer increments (`hop_samples = int(round(5.0 * 333.3333333333333)) = 1667`, `win_samples = 3333`). Cumulative addition of integer $1667$ accumulates $+0.333\text{ samples}$ of discretization drift per hop ($22 \times 0.3333 = +7.33\text{ samples}$). At the 23rd window (index 22), `start_idx` reaches $36,674$, requiring `end_idx = 40,007` which exceeds the $40,000$ sample boundary by 7 samples ($21\text{ ms}$) and is dropped by the `start_idx + win_samples <= total_samples` check. This yields **22 windows** and $1,660$ trailing tail samples ($4.98\text{ s}$) excluded per recording ($1,056$ total across 48 recordings). Under the exact formula `round(k * 5.0 * fs)`, all 23 windows fit cleanly within $40,000$ samples without boundary overflow.
