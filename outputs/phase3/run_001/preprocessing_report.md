# Phase 3 Radar Preprocessing Comparison Report

## 1. Signal Representation & Meaning

`VitalSig` represents a continuous phase-demodulated displacement signal capturing thoracic surface micromotions.

## 2. Comparative Filter Evaluation

Evaluated two configurations against raw `VitalSig` (48 recordings):
1. **Candidate 1–20 Hz Filter:** 3rd-order Butterworth bandpass (prompt Section 5.2). Passes broadband respiratory harmonics and cardiac motion.
2. **Cardiac 0.8–3.0 Hz Filter:** 3rd-order Butterworth bandpass (48–180 bpm). Isolates primary cardiac ballistocardiogram displacement.

| Configuration | Mean Cardiac Band Power Ratio | Mean P2P Amplitude | Filter Implementation |
| :--- | :---: | :---: | :--- |
| Raw VitalSig | 0.0060 | 7.0725 | Unfiltered |
| Candidate 1–20 Hz | 0.3911 | 0.7979 | Zero-phase filtfilt |
| Cardiac 0.8–3.0 Hz | 0.4843 | 0.8346 | Zero-phase filtfilt |

*(Nyquist bounds valid across all 48 recordings: $0 < 0.8 < 3.0 < 166.67\text{ Hz}$)*
