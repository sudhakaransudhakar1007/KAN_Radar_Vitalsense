# Proposed Wording Correction for Decision D7a Empirical Numbers

**Target:** `outputs/closure/pi_decision_list.md`, Decision D7a (line 102)  
**Status:** PROPOSAL ONLY (file `pi_decision_list.md` is NOT modified for this item per Stage 6D instructions)  

## 1. Finding & Root Cause
In `pi_decision_list.md:102`, the empirical description states:
> "Option B locks onto a minor positive side-lobe (+224.9/+231.8 raw amplitude), while Option A correctly identifies the true deep negative QRS deflection (-349.4/-358.5 bandpassed, -820 raw amplitude)"

Recomputation in Stage 6D (`outputs/closure/stage6d_d4_audit.py`) proves:
1. `+224.9` and `+231.8` are the **median bandpass-filtered amplitudes** (5-15 Hz) of Option B peaks in `VS19_Apnea` (+224.88) and `VS19_Resting` (+231.77), **NOT raw amplitude**. The true raw amplitudes at these positive side-lobes have medians of -96.00 and -88.00.
2. `-349.4` and `-358.5` are **VERIFIED** as the median bandpass-filtered amplitudes of Option A peaks (-349.40 and -358.50).
3. `-820` is **VERIFIED** as the median raw amplitude of Option A peaks in `VS19_Resting` (-820.00, with `VS19_Apnea` median at -812.00).

## 2. Proposed Corrected Wording
Replace the Empirical Numbers cell of Decision D7a with:
```markdown
- **Empirical Numbers (from B5a):** Evaluated across all 48 recordings. On 44 recordings, both detectors yield identical peak timestamps ($100\%$ match within $20\text{ ms}$). On `VS16` (both Apnea and Resting), the legacy detector detects an extra false peak producing non-physiological $RR < 0.343\text{ s}$ ($0.270\text{ s}$ and $0.274\text{ s}$). On `VS19` (both Apnea and Resting), Lead II exhibits inverted negative QRS polarity: Option B locks onto a minor positive side-lobe (+224.9/+231.8 median bandpassed amplitude, -96.0/-88.0 raw amplitude), while Option A correctly identifies the true deep negative QRS deflection (-349.4/-358.5 median bandpassed amplitude, -812/-820 median raw amplitude), resolving an empirical $44.0\text{ ms}$ fiducial shift ($0\%$ match within $20\text{ ms}$). (Evidence: `outputs/closure/stage6d_d4_audit.py`).
```
