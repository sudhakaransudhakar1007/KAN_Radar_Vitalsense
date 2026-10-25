# A Subject-Independent KAN-Based Framework for Non-Contact Heart-Rate Estimation from 120-GHz FMCW Radar Signals

## Phase 1: VITALSENSE Dataset Audit

### Overview
This repository contains the Phase 1 scientific audit of the **VITALSENSE** millimeter-wave (120-GHz FMCW) radar vital sensing dataset. The audit verifies dataset completeness, inspects MATLAB `.mat` data formats and variable hierarchies, identifies candidate radar and reference heart-rate (HR) signals, evaluates temporal synchronization evidence, and assesses dataset readiness before any model development (Phase 2).

---

### Environment & Prerequisites
- **Python Version:** `Python 3.10.11`
- **Dependencies:**
  - `numpy`
  - `scipy`
  - `pandas`
  - `pyyaml`
  - `pytest`
  *(All specified in `requirements.txt`)*

To install dependencies:
```bash
pip install -r requirements.txt
```

---

### Project Structure
```text
kan_radar_hr/
├── src/
│   ├── __init__.py
│   └── phase1_audit/
│       ├── __init__.py
│       ├── discover_files.py       # File discovery, metadata, and SHA-256 calculation
│       ├── inspect_mat.py          # MATLAB v5/v7 and HDF5 v7.3 structure inspection
│       ├── identify_fields.py      # Candidate field discovery & documentation evidence
│       ├── match_recordings.py     # Same-file and separate-file pairing analysis
│       ├── inspect_timing.py       # Duration calculation and synchronization audit
│       ├── validate_data.py        # Signal quality & reference bounds validation
│       ├── subject_inventory.py    # Subject inventory & four distinct aggregate counts
│       └── run_audit.py            # CLI entrypoint with Stage B safety gate
├── configs/
│   └── audit_config.yaml           # Configurable audit parameters and paths
├── docs/                           # Documentation references
├── tests/
│   ├── conftest.py
│   ├── test_file_discovery.py
│   ├── test_mat_inspection.py
│   ├── test_candidate_fields.py
│   ├── test_same_file_pairing.py
│   ├── test_matching.py
│   ├── test_timing_validation.py
│   └── test_signal_quality.py
├── outputs/
│   └── phase1_audit/               # Generated audit CSVs, summaries, and logs
├── pytest.ini
├── requirements.txt
└── README.md
```

---

### Reproducible Commands

All commands should be executed from the `kan_radar_hr/` project root directory:

#### 1. View CLI Options
```bash
python -m src.phase1_audit.run_audit --help
```

#### 2. Run Stage A (Discovery and Structural Inspection)
Stage A discovers files, computes SHA-256 hashes, inspects MATLAB structures, identifies candidate fields, extracts documentation evidence, and compares findings with initial dataset hypotheses:
```bash
python -m src.phase1_audit.run_audit --stage A
```

Optional path overrides:
```bash
python -m src.phase1_audit.run_audit --stage A --dataset-root "../data/VITALSENSE_120_DATASET" --docs-dir "../data/VITALSENSE_120_DATASET"
```

#### 3. Run Unit Test Suite
```bash
python -m pytest -v
```

#### 4. Stage B Execution (Requires Explicit Approval)
Stage B evaluates radar/reference pairing, synchronization, full signal quality, and subject inventory. 

**Safety Gate:** The CLI will refuse `--stage B` unless:
1. `outputs/phase1_audit/stage_a_summary.json` exists from a successful Stage A run, AND
2. The `--approve-stage-b` flag is explicitly provided.

```bash
python -m src.phase1_audit.run_audit --stage B --approve-stage-b
```

---

### Audit Artifacts Generated in Stage A
- `outputs/phase1_audit/file_inventory.csv`: Privacy-preserving inventory of all 96 `.mat` files with SHA-256 hashes and candidate roles.
- `outputs/phase1_audit/mat_structure_inventory.csv`: Variable paths, loader used, exact shapes, dtypes, and orientation status.
- `outputs/phase1_audit/candidate_fields.csv`: Candidate radar (`VitalSig`, `Radar.fs`) and reference (`HR`, `ecg_lead2`) fields with documented evidence.
- `outputs/phase1_audit/stage_a_summary.json`: Structured machine-readable findings and hypothesis comparisons.
- `outputs/phase1_audit/stage_a_summary.md`: Detailed markdown summary report.
- `outputs/phase1_audit/phase1_audit.log`: Dual console/file execution audit log.
