# Stage 2I Notes — Technical Validation Replication & Methodological Forensic Audit

## 1. Scope of the Replication
The code in `outputs/closure/authors_method_replication.py` replicates the authors' MATLAB technical validation script (`TechValidation.m` logic) in Python using SciPy (`resample_poly` and `correlate`).

The script successfully reproduces the published validation table (`outputs/closure/authors_technical_validation_results.csv`) with:
- **`48 / 48 (100.0%)` exact matches** across all recordings ($0.0\text{ ms}$ discrepancy).
- Zero numerical discrepancies across all 24 Resting and 24 Apnea recordings.

---

## 2. Resolving the `maxCorr` Nomenclature Anomaly (DISC-01 Forensic Trace)
The authors' dataset publication reported a table with columns `timeLag_ms` and `maxCorr`.
Across all 48 recordings:
$$\text{maxCorr} = 2 \times \text{timeLag\_ms}$$
Because sampling at $2000\text{ Hz}$ corresponds to a sampling period of $\Delta t = 0.5\text{ ms}$, a lag of $N$ samples equals $N \times 0.5\text{ ms}$. Conversely:
$$\text{Sample Lag } N = \frac{\text{timeLag\_ms}}{0.5\text{ ms}} = 2 \times \text{timeLag\_ms}$$
This proves conclusively that the published column named **`maxCorr` is a sample lag index (`lag_max`), NOT a correlation coefficient ($r$)**. Prior report claims that surrogate controls or correlation coefficients did not exceed values in this table were grounded in a fundamental misinterpretation of the authors' MATLAB variable naming.

---

## 3. Absence of Hardware Timing Evidence & Strict Boundary Constraints
1. **No Hardware Clock or Synchronization Evidence:** This cross-correlation evaluates only the relative phase agreement of low-frequency respiratory displacement between radar phase unwrapping and chest-band impedance pneumography. It provides **zero physical evidence** of hardware synchronization, clock synchronization, PPS pulses, or common ADC triggers.
2. **Hardware Timing Status Remains `UNVERIFIED`:** All candidate pairs remain formally designated **`HARDWARE_CLOCK: UNVERIFIED`**.
3. **Prohibition of "Sub-Sample" or "Millisecond" Synchronization Claims:** The signals have native sampling intervals of $3.0\text{ ms}$ (radar, $333.33\text{ Hz}$) and $3.90625\text{ ms}$ (Mindray respiration, $256\text{ Hz}$). Upsampling both to $2000\text{ Hz}$ creates a synthetic numerical grid of $0.5\text{ ms}$ bins. Achieving an argmax peak at e.g. $\pm 1.5\text{ ms}$ or $-3.0\text{ ms}$ reflects only polyphase sinc interpolation of slow respiratory motion (~0.25 Hz). It does **NOT** establish physical sub-sample or millisecond synchronization of the recording hardware.
4. **Differences from Current Pipeline:** The pipeline (`src/sync_validation/respiratory_validator.py`) demeans and normalizes signals to zero-mean unit-variance and truncates to equal length, whereas the authors' MATLAB code ran raw unnormalized cross-correlation with unequal arrays zero-padded at the tail. This difference accounts for the 28 recordings where raw DC-biased correlation diverges from zero-mean correlation (e.g. `VS01_Apnea`: 9.0 ms vs 0.0 ms).
