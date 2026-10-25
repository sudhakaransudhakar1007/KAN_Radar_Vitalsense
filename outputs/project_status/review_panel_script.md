# SCIENTIFIC REVIEW PANEL DEMONSTRATION SCRIPT
## Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals

**Target Audience:** Institutional Review Board, Principal Investigators, Biomedical Research Auditors, and Technical Review Panel  
**Document Location:** [`outputs/project_status/review_panel_script.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/project_status/review_panel_script.md)  
**Demonstration Mode:** Offline Recorded Radar Simulation (`MODEL_UNAVAILABLE` Protected State)

---

## 1. Overview & Demonstration Objective

The purpose of this presentation is to demonstrate the operational maturity, scientific integrity safeguards, and reproducibility of the KAN FMCW Radar Heart-Rate Estimation Framework without misrepresenting unverified results or generating unauthorized predictions.

---

## 2. Step-by-Step Review Panel Walkthrough

### Part 1: Establishing the Governance Gate (1 Minute)
1. **Show Terminal Output:**
   Run the preflight verification command:
   ```powershell
   python kan_radar_HR/src/closure/phase2c_preflight.py
   ```
2. **Explain to Panel:**
   > *"As you can see from the preflight check, all 10 technical, cryptographic, and inventory checks pass with 100% compliance. However, the preflight verdict is strictly **NO-GO** with 6 failures. These 6 failures are not code defects; they represent human governance decisions (D13, D14, D15, label specification approval, hardware timing acknowledgment, and gate closure authorization). In strict adherence to scientific ethics, our automated agents are prohibited from fabricating approvals or assuming gate closure."*

---

### Part 2: Demonstrating the Research Dashboard (3 Minutes)
1. **Launch the Demo Server:**
   ```powershell
   python kan_radar_HR/src/demo/app.py
   ```
   Open web browser to: `http://127.0.0.1:5000`
2. **Highlight Key Interface Elements:**
   - **Header Title & Subtitle:**  
     Points out: *"Subject-Independent KAN Radar Heart-Rate Estimation — Recorded Radar Data — Streaming Replay & Rolling Window Simulation Demo"*.
   - **Prominent Badges:**  
     Points out the explicit badges: `RECORDED DATA PLAYBACK (OFFLINE SIMULATION)` and `STATE: MODEL_UNAVAILABLE`.
   - **Research Disclaimer Banner:**  
     Reads aloud the top banner:  
     > *"⚠️ Research Disclaimer: This is an offline software replay of recorded VITALSENSE radar signals. Hardware clock synchronization is unverified (nominal T₀=0s). No physical radar hardware is connected. Not clinical software."*
   - **Recording Selector:**  
     Shows the dropdown populated with verified recordings across all 24 subjects ($VS01\text{--}VS24$), Resting and Apnea.
   - **Metrics Card Grid:**  
     Points out the **Model Status** card displaying `UNAVAILABLE` (in red) and **Latest HR Estimate** displaying `N/A` (prediction suppressed).
   - **Live Playback:**  
     Clicks `▶ Start`. Shows the virtual clock advancing at $1.0\times$ speed, streaming the real 333.33 Hz FMCW radar displacement waveform and updating the rolling 10-second window buffer.
   - **Integrity Point to Panel:**  
     > *"Notice that despite streaming real recorded radar data, no estimated heart rate is displayed. Because the scientific gate is OPEN and real-data training is blocked, our model engine strictly suppresses predictions rather than inventing random numbers or presenting synthetic benchmarks as real data."*

---

### Part 3: Explaining the Scientific Foundations (2 Minutes)
1. **Timing Uncertainty Envelope:**
   > *"The VITALSENSE dataset lacks physical hardware clock synchronization cables between the FMCW radar digitizer and the Mindray ECG monitor. Our empirical audit determined a composite timing uncertainty envelope of $\pm 100\text{--}300\text{ ms}$ (upper bound $\pm 500\text{ ms}$). Our boundary-shift sensitivity analysis proves that over a 10-second observation window, this uncertainty shifts harmonic mean HR by less than $1.2\text{ BPM}$, well within the $\pm 5.0\text{ BPM}$ ANSI/AAMI clinical tolerance. Therefore, 10-second reference labels are scientifically valid under the mandatory provenance tag `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`."*
2. **Ground-Truth Heart Rate Mathematics:**
   > *"We proved mathematically that computing $60.0 / \overline{\text{RR}}$ is identical to the harmonic mean of instantaneous beat rates. Specification v1.0.0 strictly adopts the harmonic mean, preventing the $+0.5\text{ BPM}$ overestimation bias introduced by the arithmetic mean under heart rate variability."*

---

### Part 4: The Path to Phase 2C Execution (1 Minute)
1. **Present the Pending Sign-Off Protocol:**
   Show [`outputs/closure/pi_signoff_intake_protocol.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/closure/pi_signoff_intake_protocol.md).
2. **Conclusion to Panel:**
   > *"All 220 automated unit and regression tests pass. The dataset pipeline is 100% ready. As soon as the authorized Principal Investigator completes the six signature fields in this intake protocol, preflight will independently return **GO**, and the pipeline will automatically unlock supervised dataset generation (`run_002`) followed by real-data KAN Leave-One-Subject-Out cross-validation across all 24 subjects."*
