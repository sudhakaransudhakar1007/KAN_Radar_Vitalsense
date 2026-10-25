# DRAFT INVESTIGATOR DECISION & SIGNOFF TEMPLATE (UNAPPROVED / PENDING)
## Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals

> [!WARNING]
> **RESEARCH GOVERNANCE NOTICE: DRAFT TEMPLATE ONLY**  
> This file is an unexecuted, non-binding template intended for authorized human Principal Investigator review.  
> No fields have been signed, authorized, or approved. Real-data dataset generation (`run_002`) and model training (`run_real_001`) remain strictly **BLOCKED** while the governance gate is **OPEN**.

---

### Decision D13: Window-Level Maximum RR Gap Rule
- [ ] **Option A (Recommended):** Set maximum permitted RR gap to $3.0\text{ s}$. (Cohort max observed is $1.2920\text{ s}$; $100\%$ window yield retained).
- [ ] **Option B:** Set maximum permitted RR gap to $2.5\text{ s}$.
- [ ] **Option C:** Set maximum permitted RR gap to $2.0\text{ s}$.

- **PI Decision Choice:** `[PENDING]`
- **PI Name:** `[PENDING]`
- **PI Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`

---

### Decision D14: Minimum Valid Beats Per Recording
- [ ] **Option A (Recommended):** Require at least $20$ valid physiological beats per 60–120s recording. (Cohort range is $99\text{--}157$ beats; $100\%$ recording yield retained).
- [ ] **Option B:** Retain legacy $5$-beat heuristic.
- [ ] **Option C:** Require at least $30$ valid beats.

- **PI Decision Choice:** `[PENDING]`
- **PI Name:** `[PENDING]`
- **PI Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`

---

### Decision D15: Pipeline Runner Default `output_dir` Guard
- [ ] **Option A (Recommended):** Enforce programmatic write guards in runner scripts preventing accidental overwrites of baseline directories.
- [ ] **Option B:** Rely on documentation warnings only.

- **PI Decision Choice:** `[PENDING]`
- **PI Name:** `[PENDING]`
- **PI Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`

---

### Label Specification v1.0.0 Approval
- **Canonical SHA-256 Digest:** `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44`
- [ ] **APPROVE** `outputs/closure/spec/label_spec_v1.json`
- [ ] **REJECT**

- **Approver Name:** `[PENDING]`
- **Approver Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`

---

### Hardware Timing Limitation Acknowledgment
- **Mandatory Provenance Disclaimer:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`
- **Limitation Scope:** The 120-GHz FMCW radar digitizer and Mindray ECG reference monitor operated without hardware clock synchronization cables. Nominal time zero ($T_0 = 0.0\text{ s}$) is assumed for 10.0-second window harmonic mean heart-rate estimation.

- [ ] **ACKNOWLEDGED AND ACCEPTED**

- **PI Name:** `[PENDING]`
- **PI Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`

---

### Phase 2A Gate Closure & Phase 2C Authorization
- [ ] **Phase 2A Gate Closure is AUTHORIZED (Gate Status: CLOSED)**
- [ ] **Phase 2A Gate Closure is NOT AUTHORIZED (Gate Status: OPEN)**

- **PI Name:** `[PENDING]`
- **PI Signature:** `_________________________ [PENDING]`
- **Date:** `YYYY-MM-DD [PENDING]`
