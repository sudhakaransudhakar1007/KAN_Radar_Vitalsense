# REPRODUCIBILITY MANIFEST
## Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals

**Manifest Generated:** 2026-10-25  
**Working Directory:** [`kan_radar_HR`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR)  
**Report Output Path:** [`outputs/project_status/reproducibility_manifest.md`](file:///c:/Users/admin/OneDrive/Desktop/KAN%20algrithm%20FRAME%20work/kan_radar_HR/outputs/project_status/reproducibility_manifest.md)  

---

## 1. Software Environment & Tooling Specifications

| Software / Library | Version | Role in Project | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | `3.10.11` | Primary runtime environment | `python --version` |
| **pytest** | `9.1.1` | Automated test runner | `pytest --version` |
| **NumPy** | `1.26.4` | Numerical array processing | `python -c "import numpy; print(numpy.__version__)"` |
| **SciPy** | `1.13.1` | Digital signal processing (Butterworth filters, peak finding) | `python -c "import scipy; print(scipy.__version__)"` |
| **Pandas** | `2.2.2` | Dataframe & manifest generation | `python -c "import pandas; print(pandas.__version__)"` |
| **TensorFlow** | `2.16.1` | KAN neural network layers & baseline models | `python -c "import tensorflow; print(tensorflow.__version__)"` |
| **Flask** | `3.0.3` | Recorded data simulation dashboard | `python -c "import flask; print(flask.__version__)"` |
| **OS Platform** | Windows (win32) | Development & evaluation platform | `python -c "import sys; print(sys.platform)"` |

---

## 2. Directory Path Conventions

- **Workspace Root:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work`
- **Canonical Repository Root:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\kan_radar_HR`
- **VITALSENSE Dataset Path:** `C:\Users\admin\OneDrive\Desktop\KAN algrithm FRAME work\data\VITALSENSE_120_DATASET`
- **Governance Outputs Directory:** `kan_radar_HR/outputs/closure`
- **Target Supervised Dataset Directory:** `kan_radar_HR/outputs/supervised_dataset/run_002` (created only post-authorization)
- **Target Real Model Directory:** `kan_radar_HR/outputs/phase5/run_real_001` (created only post-authorization)

---

## 3. Authoritative Cryptographic Hashes (SHA-256)

| Target Artifact | Role | Invariant SHA-256 Digest |
| :--- | :--- | :--- |
| `outputs/phase2a/step2b_consistency_audit.md` | Phase 2A Consistency Audit Baseline | `6c4391bf1f8b96c95ec42e5767803f32644f67dc3562c8f8d630a6dfccbdfb1f` |
| `outputs/phase2a/sync_validation_results.csv` | 48-Recording Sync Validation Results | `6f4fda369c1a7e6d0954bf422456d69c41a44de2657f1308b30f11f76b5dcb10` |
| `outputs/closure/pi_decision_list.md` | Historical Decisions D1 through D12 | `fe4d7d39fdcb651baf59ef5f820f3ed9ae6afd5b133b87c805f8bc4a90180363` |
| `outputs/closure/spec/label_spec_v1.json` (Raw) | Raw Specification JSON (Unsigned) | `a0f7a85e439fd8d5c5b2eb4636fc9b551aed71c12dd1af1c057685fb60314da8` |
| `outputs/closure/spec/label_spec_v1.json` (Canonical) | Canonical Specification Content Digest | `ae5c67808b9ad8ae8f6e40f89434242e88a6de67b7d57d8478c6256075708f44` |

---

## 4. Deterministic Seeds & Provenance Flags

- **RNG Implementation:** Python `random`, NumPy `np.random`, and TensorFlow `tf.random`.
- **Pre-Registered Cardiac Benchmark Seed:** `seed = 42`.
- **Deterministic Surrogate Controls Seed:** `seed = 1000`.
- **Mandatory Timing Provenance Flag:** `UNVERIFIED_HARDWARE_TIMING_NOMINAL_T0`.
- **Ground-Truth Label Method:** Harmonic Mean Heart Rate ($60.0 / \overline{\text{RR}}$) from Lead II ECG R-peaks.
