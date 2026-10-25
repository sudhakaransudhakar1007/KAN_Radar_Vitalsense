"""Unit tests for MATLAB file inspection (scipy and HDF5) and orientation flags."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest
import scipy.io

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

from src.phase1_audit.inspect_mat import (
    assess_orientation,
    compute_approved_summary_stats,
    inspect_single_mat_file,
)


def test_traditional_mat_inspection(tmp_path: Path):
    """Test inspection of standard v5/v7 MAT file saved with scipy.io."""
    mat_file = tmp_path / "sample_radar.mat"
    data = {
        "VitalSig": np.random.randn(100),
        "T_frame": 0.003,
    }
    scipy.io.savemat(mat_file, data)

    records, loader_used, status, err = inspect_single_mat_file(mat_file)
    assert status == "SUCCESS"
    assert loader_used == "scipy.io.loadmat"
    assert err is None
    var_paths = [r["variable_path"] for r in records]
    assert "VitalSig" in var_paths
    assert "T_frame" in var_paths

    vitalsig_rec = next(r for r in records if r["variable_path"] == "VitalSig")
    assert vitalsig_rec["shape_as_read"] == "(100,)"
    assert "float64" in vitalsig_rec["dtype_as_read"]


@pytest.mark.skipif(not HAS_H5PY, reason="h5py not available")
def test_hdf5_mat_inspection(tmp_path: Path):
    """Test inspection of synthetic HDF5 file."""
    h5_path = tmp_path / "v73_file.mat"
    with h5py.File(h5_path, "w") as f:
        f.create_dataset("VitalSig", data=np.ones(50, dtype=np.float32))
        grp = f.create_group("Radar")
        grp.create_dataset("fs", data=333.33)

    records, loader_used, status, err = inspect_single_mat_file(h5_path)
    assert status == "SUCCESS"
    assert loader_used == "h5py"
    assert err is None
    var_paths = [r["variable_path"] for r in records]
    assert "VitalSig" in var_paths
    assert "Radar/fs" in var_paths


@pytest.mark.skipif(not HAS_H5PY, reason="h5py not available")
def test_hdf5_complex_compound_array(tmp_path: Path):
    """PATCH 5: Test that complex arrays stored as compound types in HDF5 are reported as complex."""
    h5_path = tmp_path / "complex_h5.mat"
    comp_dtype = np.dtype([("r", np.float64), ("i", np.float64)])
    comp_data = np.zeros(20, dtype=comp_dtype)
    with h5py.File(h5_path, "w") as f:
        f.create_dataset("ComplexRadar", data=comp_data)

    records, loader_used, status, err = inspect_single_mat_file(h5_path)
    assert status == "SUCCESS"
    rec = next(r for r in records if r["variable_path"] == "ComplexRadar")
    assert "complex128" in rec["dtype_as_read"]


def test_orientation_status_flagging():
    """Test that 2D arrays are flagged POSSIBLY_TRANSPOSED without silent transposition."""
    # 1D array
    status_1d, _ = assess_orientation((40000,))
    assert status_1d == "1D_VECTOR"

    # 2D row/column vector
    status_row, _ = assess_orientation((1, 40000))
    assert status_row == "POSSIBLY_TRANSPOSED"

    status_col, _ = assess_orientation((40000, 1))
    assert status_col == "POSSIBLY_TRANSPOSED"

    # 2D matrix
    status_2d, _ = assess_orientation((100, 200))
    assert status_2d == "POSSIBLY_TRANSPOSED"


def test_approved_summary_stats_no_raw_leak():
    """PATCH 2: Verify summary stats contain only approved aggregates and no raw sample slices."""
    arr = np.array([1.0, 2.0, 3.0, 4.0, np.nan, np.inf])
    stats = compute_approved_summary_stats(arr)
    # Check approved keys
    for k in ["count", "min", "max", "mean", "std", "range", "nan_count", "posinf_count", "neginf_count"]:
        assert k in stats
    # Check no raw array or slice in stats
    assert "samples" not in stats
    assert "raw_data" not in stats
    assert stats["nan_count"] == 1
    assert stats["posinf_count"] == 1
    assert stats["count"] == 6
