"""MATLAB file inspection module with HDF5 and legacy MAT support."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

try:
    import scipy.io
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def compute_approved_summary_stats(data: Any) -> Dict[str, Any]:
    """Compute strictly approved summary statistics without exposing raw samples.

    Approved stats: counts, shapes, dtypes, min, max, mean, std, range, NaN/Inf counts.
    Never returns raw samples or slices.
    """
    if isinstance(data, (int, float, np.integer, np.floating)):
        val = float(data)
        is_nan = bool(np.isnan(val))
        is_posinf = bool(np.isposinf(val))
        is_neginf = bool(np.isneginf(val))
        return {
            "count": 1,
            "min": None if is_nan or is_posinf or is_neginf else val,
            "max": None if is_nan or is_posinf or is_neginf else val,
            "mean": None if is_nan or is_posinf or is_neginf else val,
            "std": 0.0,
            "range": 0.0,
            "nan_count": 1 if is_nan else 0,
            "posinf_count": 1 if is_posinf else 0,
            "neginf_count": 1 if is_neginf else 0,
        }

    if not isinstance(data, np.ndarray):
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "range": None,
            "nan_count": 0,
            "posinf_count": 0,
            "neginf_count": 0,
        }

    total_count = int(data.size)
    if total_count == 0:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "range": None,
            "nan_count": 0,
            "posinf_count": 0,
            "neginf_count": 0,
        }

    # Complex array handling (Patch 5)
    if np.iscomplexobj(data):
        nan_count = int(np.sum(np.isnan(data)))
        posinf_count = int(np.sum(np.isposinf(np.real(data)) | np.isposinf(np.imag(data))))
        neginf_count = int(np.sum(np.isneginf(np.real(data)) | np.isneginf(np.imag(data))))
        finite_mask = np.isfinite(data)
        if np.any(finite_mask):
            finite_mag = np.abs(data[finite_mask])
            c_min = float(np.min(finite_mag))
            c_max = float(np.max(finite_mag))
            c_mean = float(np.mean(finite_mag))
            c_std = float(np.std(finite_mag))
            c_range = c_max - c_min
        else:
            c_min, c_max, c_mean, c_std, c_range = None, None, None, None, None
        return {
            "count": total_count,
            "min": c_min,
            "max": c_max,
            "mean": c_mean,
            "std": c_std,
            "range": c_range,
            "nan_count": nan_count,
            "posinf_count": posinf_count,
            "neginf_count": neginf_count,
            "is_complex": True,
        }

    # Numeric real array
    if np.issubdtype(data.dtype, np.number):
        nan_count = int(np.sum(np.isnan(data)))
        posinf_count = int(np.sum(np.isposinf(data)))
        neginf_count = int(np.sum(np.isneginf(data)))
        finite_mask = np.isfinite(data)
        if np.any(finite_mask):
            finite_vals = data[finite_mask]
            d_min = float(np.min(finite_vals))
            d_max = float(np.max(finite_vals))
            d_mean = float(np.mean(finite_vals))
            d_std = float(np.std(finite_vals))
            d_range = d_max - d_min
        else:
            d_min, d_max, d_mean, d_std, d_range = None, None, None, None, None
        return {
            "count": total_count,
            "min": d_min,
            "max": d_max,
            "mean": d_mean,
            "std": d_std,
            "range": d_range,
            "nan_count": nan_count,
            "posinf_count": posinf_count,
            "neginf_count": neginf_count,
            "is_complex": False,
        }

    # Non-numeric or object array
    return {
        "count": total_count,
        "min": None,
        "max": None,
        "mean": None,
        "std": None,
        "range": None,
        "nan_count": 0,
        "posinf_count": 0,
        "neginf_count": 0,
        "is_complex": False,
    }


def assess_orientation(shape: Tuple[int, ...]) -> Tuple[str, str]:
    """Assess whether array dimensions are potentially ambiguous or transposed.

    Returns:
        (orientation_status, notes)
    """
    if len(shape) == 1:
        return "1D_VECTOR", "1D array as loaded; squeeze_me flattened MATLAB 1xN or Nx1 vector"
    if len(shape) == 2:
        if shape[0] == 1 or shape[1] == 1:
            return "POSSIBLY_TRANSPOSED", "2D row/column vector; orientation may depend on MATLAB/HDF5 convention"
        return "POSSIBLY_TRANSPOSED", f"2D matrix with shape {shape}; time vs channel axis ambiguous without metadata"
    if len(shape) > 2:
        return "POSSIBLY_TRANSPOSED", f"Multidimensional array with shape {shape}; dimension ordering unverified"
    return "SCALAR", "Scalar variable"


def inspect_scipy_object(
    obj: Any,
    var_path: str,
    depth: int = 0,
    max_depth: int = 5,
    visited: Optional[Set[int]] = None,
) -> List[Dict[str, Any]]:
    """Traverse scipy.io mat_struct, dicts, and arrays with bounded recursion."""
    if visited is None:
        visited = set()

    obj_id = id(obj)
    if obj_id in visited or depth > max_depth:
        return []
    visited.add(obj_id)

    records: List[Dict[str, Any]] = []

    # MATLAB struct (mat_struct)
    if hasattr(obj, "_fieldnames"):
        fieldnames = list(obj._fieldnames)
        records.append({
            "variable_path": var_path,
            "object_type": "mat_struct",
            "shape_as_read": "()",
            "dtype_as_read": "struct",
            "field_names": ", ".join(fieldnames),
            "orientation_status": "NOT_APPLICABLE",
            "notes": f"MATLAB struct with {len(fieldnames)} fields",
            "raw_object": obj,
        })
        for field in fieldnames:
            sub_obj = getattr(obj, field, None)
            sub_path = f"{var_path}.{field}" if var_path else field
            records.extend(inspect_scipy_object(sub_obj, sub_path, depth + 1, max_depth, visited))
        return records

    # NumPy ndarray
    if isinstance(obj, np.ndarray):
        shape = obj.shape
        dtype_str = str(obj.dtype)
        orient_status, orient_notes = assess_orientation(shape)

        # Handle object or structured ndarrays
        if obj.dtype == object and obj.ndim > 0 and obj.size <= 20:
            records.append({
                "variable_path": var_path,
                "object_type": "ndarray_object",
                "shape_as_read": str(shape),
                "dtype_as_read": dtype_str,
                "field_names": "NONE",
                "orientation_status": orient_status,
                "notes": f"Object array; {orient_notes}",
                "raw_object": obj,
            })
            for i, item in enumerate(obj.flat):
                sub_path = f"{var_path}[{i}]"
                records.extend(inspect_scipy_object(item, sub_path, depth + 1, max_depth, visited))
            return records

        records.append({
            "variable_path": var_path,
            "object_type": "ndarray",
            "shape_as_read": str(shape),
            "dtype_as_read": dtype_str,
            "field_names": "NONE",
            "orientation_status": orient_status,
            "notes": orient_notes,
            "raw_object": obj,
        })
        return records

    # Primitives (scalar float, int, str)
    if isinstance(obj, (int, float, str, np.integer, np.floating)):
        dtype_str = type(obj).__name__
        records.append({
            "variable_path": var_path,
            "object_type": "scalar",
            "shape_as_read": "()",
            "dtype_as_read": dtype_str,
            "field_names": "NONE",
            "orientation_status": "NOT_APPLICABLE",
            "notes": "Scalar value",
            "raw_object": obj,
        })
        return records

    # Fallback
    records.append({
        "variable_path": var_path,
        "object_type": type(obj).__name__,
        "shape_as_read": "UNKNOWN",
        "dtype_as_read": type(obj).__name__,
        "field_names": "NONE",
        "orientation_status": "NOT_APPLICABLE",
        "notes": f"Unhandled type: {type(obj).__name__}",
        "raw_object": obj,
    })
    return records


def inspect_hdf5_group(
    group: Any,
    prefix: str = "",
    depth: int = 0,
    max_depth: int = 5,
    visited: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Traverse HDF5 v7.3 datasets and groups with bounded recursion."""
    if visited is None:
        visited = set()

    if depth > max_depth or group.name in visited:
        return []
    visited.add(group.name)

    records: List[Dict[str, Any]] = []

    for key, item in group.items():
        var_path = f"{prefix}/{key}" if prefix else key

        if isinstance(item, h5py.Dataset):
            dtype = item.dtype
            shape = item.shape

            # Complex compound dtype handling (Patch 5)
            # MATLAB v7.3 stores complex numbers as compound types with fields 'r' and 'i'
            is_complex = False
            dtype_desc = str(dtype)
            if dtype.names and set(dtype.names) in [{"r", "i"}, {"real", "imag"}]:
                is_complex = True
                dtype_desc = "complex128" if dtype["r"] == np.float64 else "complex64"

            # Char array handling (Patch 5): MATLAB char in v7.3 may appear as uint16
            is_char = False
            matlab_class = item.attrs.get("MATLAB_class", None)
            if matlab_class == b"char" or matlab_class == "char" or (
                dtype == np.uint16 and item.attrs.get("MATLAB_int_decode")
            ):
                is_char = True
                dtype_desc = "matlab_char_uint16"

            orient_status, orient_notes = assess_orientation(shape)
            notes_list = [orient_notes]
            if is_complex:
                notes_list.append("HDF5 compound complex representation")
            if is_char:
                notes_list.append("MATLAB char encoded as uint16; text candidate")

            records.append({
                "variable_path": var_path,
                "object_type": "hdf5_dataset",
                "shape_as_read": str(shape),
                "dtype_as_read": dtype_desc,
                "field_names": ", ".join(dtype.names) if dtype.names else "NONE",
                "orientation_status": orient_status,
                "notes": "; ".join(notes_list),
                "raw_object": item,
            })

        elif isinstance(item, h5py.Group):
            keys = list(item.keys())
            records.append({
                "variable_path": var_path,
                "object_type": "hdf5_group",
                "shape_as_read": "()",
                "dtype_as_read": "group",
                "field_names": ", ".join(keys),
                "orientation_status": "NOT_APPLICABLE",
                "notes": f"HDF5 Group with {len(keys)} members",
                "raw_object": item,
            })
            records.extend(inspect_hdf5_group(item, var_path, depth + 1, max_depth, visited))

    return records


def inspect_single_mat_file(file_path: Path) -> Tuple[List[Dict[str, Any]], str, str, str | None]:
    """Inspect structure of a single .mat file following required loading order.

    Order:
      1. Check h5py.is_hdf5(file_path) first.
      2. If HDF5: load with h5py.
      3. Otherwise: try scipy.io.loadmat(file_path, struct_as_record=False, squeeze_me=True).
      4. Catch NotImplementedError and other loading exceptions.

    Returns:
        (structure_records, loader_used, read_status, error_message)
    """
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        return [], "NONE", "FILE_NOT_FOUND", f"File does not exist: {file_path}"

    # Step 1: Check h5py
    if HAS_H5PY and h5py.is_hdf5(file_path):
        try:
            with h5py.File(file_path, "r") as h5_file:
                records = inspect_hdf5_group(h5_file)
                for rec in records:
                    rec["loader_used"] = "h5py"
                    rec["read_status"] = "SUCCESS"
                return records, "h5py", "SUCCESS", None
        except Exception as exc:
            return [], "h5py", "READ_ERROR", f"h5py inspection error: {type(exc).__name__}: {exc}"

    # Step 2: Try scipy.io.loadmat
    if HAS_SCIPY:
        try:
            mat_dict = scipy.io.loadmat(
                file_path,
                struct_as_record=False,
                squeeze_me=True,
            )
            records: List[Dict[str, Any]] = []
            for key, val in mat_dict.items():
                if key.startswith("__"):
                    continue
                records.extend(inspect_scipy_object(val, key))

            for rec in records:
                rec["loader_used"] = "scipy.io.loadmat"
                rec["read_status"] = "SUCCESS"

            return records, "scipy.io.loadmat", "SUCCESS", None
        except NotImplementedError as exc:
            return [], "scipy.io.loadmat", "UNREADABLE_V7_3", f"NotImplementedError: {exc}"
        except Exception as exc:
            return [], "scipy.io.loadmat", "READ_ERROR", f"{type(exc).__name__}: {exc}"

    return [], "NONE", "UNREADABLE", "Neither h5py nor scipy.io available to inspect file"
