"""Unit tests for timing and synchronization validation."""

from __future__ import annotations

import numpy as np
import pytest

from src.phase1_audit.inspect_timing import (
    audit_synchronization_pair,
    compute_duration_seconds,
)


def test_duration_1d_array():
    """PATCH 3: Test duration calculation for 1D array with positive finite fs."""
    dur, status, notes = compute_duration_seconds((40000,), 333.3333333333333)
    assert dur == 120.0
    assert status == "CONFIRMED_1D"


def test_duration_invalid_fs():
    """PATCH 3: Test duration calculation rejects non-positive or non-finite fs."""
    dur, status, notes = compute_duration_seconds((40000,), 0.0)
    assert dur is None
    assert status == "INVALID_FS"

    dur_nan, status_nan, _ = compute_duration_seconds((40000,), np.nan)
    assert dur_nan is None
    assert status_nan == "INVALID_FS"


def test_duration_uncertain_2d_orientation():
    """PATCH 3: Test that uncertain 2D array reports POSSIBLY_TRANSPOSED and does NOT pick an axis."""
    shape = (1000, 200)
    dur, status, notes = compute_duration_seconds(shape, 100.0)
    assert dur is None
    assert status == "POSSIBLY_TRANSPOSED"
    assert "Axis 0" in notes
    assert "Axis 1" in notes


def test_duration_verified_2d_orientation():
    """PATCH 3: Test duration when axis is explicitly verified."""
    shape = (4, 40000)
    dur, status, notes = compute_duration_seconds(shape, 333.3333333333333, verified_time_axis=1)
    assert dur == 120.0
    assert status == "VERIFIED_AXIS"


def test_synchronization_audit_unverified():
    """Test synchronization audit returns UNVERIFIED_TIMING when hardware clock is missing."""
    rad_info = {"relative_path": "radar.mat", "fs": 333.3333333333333, "shape": (40000,)}
    ref_info = {"relative_path": "ref.mat", "fs_ecg": 500, "ecg_shape": (60000,), "hr_shape": (120,)}

    res = audit_synchronization_pair(rad_info, ref_info)
    assert res["radar_duration_seconds"] == 120.0
    assert res["ref_ecg_duration_seconds"] == 120.0
    assert res["duration_match"] is True
    assert res["synchronization_status"] == "UNVERIFIED_TIMING"
    assert "clock" in res["notes"].lower()
