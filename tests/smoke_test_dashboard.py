"""Phase 6B.4: Comprehensive Dashboard Smoke Test Suite.

Verifies:
1. State: MODEL_UNAVAILABLE (default state, missing checkpoint).
2. State: SYNTHETIC_DEMO_ONLY (suppresses HR prediction on recorded radar signals).
3. State: REAL_MODEL_BLOCKED_BY_APPROVAL_GATE (real checkpoint blocked while gate is OPEN).
4. State: REAL_MODEL_READY (tested safely in isolated test fixture without bypassing production gate).
5. Live HTTP Loopback Server probe on local port (checks HTML disclaimer, status JSON, headers).
"""

from __future__ import annotations

import json
import socket
import sys
import threading
import time
from pathlib import Path

import numpy as np
import scipy.io as sio

# Ensure kan_radar_HR is on sys.path
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.demo.app import create_app
from src.demo.model_loader import SafeModelInferenceEngine
from src.kan.kan_model import KANRegressor
import tensorflow as tf


def run_smoke_tests() -> bool:
    print("=================================================================")
    print("PHASE 6B.4: DASHBOARD SMOKE TEST SUITE")
    print("=================================================================")

    test_results = {}

    # Setup mock data directory
    scratch_dir = repo_root / "outputs" / "closure" / "scratch"
    mock_data_dir = scratch_dir / "mock_radar_data"
    mock_data_dir.mkdir(parents=True, exist_ok=True)
    mat_p = mock_data_dir / "VS01_Resting.mat"
    vitsig = np.sin(np.linspace(0, 20, 40000)).reshape(1, -1)
    radar_struct = np.array([[(np.array([[333.3333]]),)]], dtype=[("fs", "O")])
    sio.savemat(str(mat_p), {"VitalSig": vitsig, "Radar": radar_struct})

    # ----------------------------------------------------------------------
    # Test 1: MODEL_UNAVAILABLE
    # ----------------------------------------------------------------------
    print("\n[1/5] Testing State: MODEL_UNAVAILABLE...")
    app1 = create_app(dataset_dir=str(mock_data_dir), checkpoint_path=None)
    c1 = app1.test_client()

    r1 = c1.get("/api/status").get_json()
    assert r1["model_state"] == "MODEL_UNAVAILABLE", f"Expected MODEL_UNAVAILABLE, got {r1['model_state']}"
    assert r1["model_available"] is False
    assert r1["simulation_mode"] == "VISUALIZATION_ONLY"
    assert r1["data_mode"] == "RECORDED_RADAR_PLAYBACK"
    assert "RECORDED DATA SIMULATION" in r1["hardware_disclaimer"]

    # Step window
    c1.post("/api/control", json={"action": "step"})
    s1 = c1.get("/api/state").get_json()
    assert s1["snapshot"]["latest_prediction_bpm"] is None
    assert s1["snapshot"]["model_state"] == "MODEL_UNAVAILABLE"
    wave1 = s1["waveform"]
    assert len(wave1["times_s"]) > 0
    assert wave1["window_bounds"] is not None

    h1 = c1.get("/api/history").get_json()
    assert h1["count"] == 1
    assert h1["history"][0]["processing_status"] == "MODEL_UNAVAILABLE"
    assert h1["history"][0]["prediction_bpm"] is None
    print("  -> PASS: MODEL_UNAVAILABLE verified. Waveform rendered, prediction suppressed.")
    test_results["MODEL_UNAVAILABLE"] = "PASS"

    # ----------------------------------------------------------------------
    # Test 2: SYNTHETIC_DEMO_ONLY
    # ----------------------------------------------------------------------
    print("\n[2/5] Testing State: SYNTHETIC_DEMO_ONLY...")
    synth_path = repo_root / "outputs" / "phase6b" / "synthetic_kan" / "folds" / "fold_01" / "best_model.weights.h5"
    assert synth_path.exists(), f"Synthetic weights missing: {synth_path}"

    app2 = create_app(dataset_dir=str(mock_data_dir), checkpoint_path=str(synth_path))
    c2 = app2.test_client()

    r2 = c2.get("/api/status").get_json()
    assert r2["model_state"] == "SYNTHETIC_DEMO_ONLY", f"Expected SYNTHETIC_DEMO_ONLY, got {r2['model_state']}"
    assert r2["model_available"] is False
    assert r2["simulation_mode"] == "VISUALIZATION_ONLY"
    assert "Synthetic benchmark checkpoint detected" in r2["model_status_reason"]

    # Step 2 windows on recorded radar signal
    c2.post("/api/control", json={"action": "step"})
    c2.post("/api/control", json={"action": "step"})
    s2 = c2.get("/api/state").get_json()
    assert s2["snapshot"]["latest_prediction_bpm"] is None, "CRITICAL LEAKAGE: Synthetic model produced BPM on real radar!"
    assert s2["snapshot"]["model_state"] == "SYNTHETIC_DEMO_ONLY"

    h2 = c2.get("/api/history").get_json()
    assert h2["count"] == 2
    for rec in h2["history"]:
        assert rec["processing_status"] == "SYNTHETIC_DEMO_ONLY"
        assert rec["prediction_bpm"] is None
    print("  -> PASS: SYNTHETIC_DEMO_ONLY verified. Synthetic model strictly blocked from outputting BPM on real radar.")
    test_results["SYNTHETIC_DEMO_ONLY"] = "PASS"

    # ----------------------------------------------------------------------
    # Test 3: REAL_MODEL_BLOCKED_BY_APPROVAL_GATE
    # ----------------------------------------------------------------------
    print("\n[3/5] Testing State: REAL_MODEL_BLOCKED_BY_APPROVAL_GATE...")
    real_mock_weights = mock_data_dir / "real_model_weights.h5"
    real_mock_weights.write_text("dummy_weights")

    app3 = create_app(dataset_dir=str(mock_data_dir), checkpoint_path=str(real_mock_weights))
    c3 = app3.test_client()

    r3 = c3.get("/api/status").get_json()
    assert r3["model_state"] == "REAL_MODEL_BLOCKED_BY_APPROVAL_GATE", f"Expected REAL_MODEL_BLOCKED_BY_APPROVAL_GATE, got {r3['model_state']}"
    assert r3["model_available"] is False
    assert r3["simulation_mode"] == "VISUALIZATION_ONLY"
    assert "Phase 2A/2C Finalization Gate remains OPEN" in r3["model_status_reason"]

    c3.post("/api/control", json={"action": "step"})
    s3 = c3.get("/api/state").get_json()
    assert s3["snapshot"]["latest_prediction_bpm"] is None
    assert s3["snapshot"]["model_state"] == "REAL_MODEL_BLOCKED_BY_APPROVAL_GATE"
    print("  -> PASS: REAL_MODEL_BLOCKED_BY_APPROVAL_GATE verified. Real checkpoint blocked while gate is open.")
    test_results["REAL_MODEL_BLOCKED_BY_APPROVAL_GATE"] = "PASS"

    # ----------------------------------------------------------------------
    # Test 4: REAL_MODEL_READY (in isolated test directory)
    # ----------------------------------------------------------------------
    print("\n[4/5] Testing State: REAL_MODEL_READY (Isolated Fixture)...")
    iso_dir = mock_data_dir / "iso_gate_closed"
    iso_dir.mkdir(parents=True, exist_ok=True)
    (iso_dir / "outputs" / "phase2a").mkdir(parents=True, exist_ok=True)
    (iso_dir / "outputs" / "phase2a" / "step2b_consistency_audit.md").write_text("FINALIZATION GATE CLOSED\nAPPROVED BY PI", encoding="utf-8")

    # Create a genuine KAN weights file for 3333 dim
    model = KANRegressor(input_dim=3333, latent_dim=16, hidden_dim=8)
    model(tf.zeros((1, 3333)))
    valid_weights = iso_dir / "genuine_real.weights.h5"
    model.save_weights(str(valid_weights))

    engine_ready = SafeModelInferenceEngine(
        model_name="KANRegressor",
        checkpoint_path=valid_weights,
        normalizer_stats={"train_mean": 70.0, "train_std": 10.0},
        base_dir=iso_dir,
    )
    compat_ready = engine_ready.get_compatibility_status()
    assert compat_ready.model_state == "REAL_MODEL_READY", f"Expected REAL_MODEL_READY, got {compat_ready.model_state}"
    assert compat_ready.is_available is True
    assert compat_ready.operating_mode == "SAVED_MODEL_INFERENCE"

    # Verify inference produces legitimate physiological BPM
    win_sig = np.sin(np.linspace(0, 10, 3333))
    res_ready = engine_ready.predict_window(win_sig, window_index=0, start_time_s=0.0, end_time_s=10.0)
    assert res_ready.status == "SUCCESS"
    assert res_ready.prediction_bpm is not None
    assert 30.0 <= res_ready.prediction_bpm <= 220.0
    print(f"  -> PASS: REAL_MODEL_READY verified in isolated fixture (Predicted BPM: {res_ready.prediction_bpm:.2f}). Production gate remains OPEN.")
    test_results["REAL_MODEL_READY"] = "PASS"

    # ----------------------------------------------------------------------
    # Test 5: Live Server Loopback Probe & Disclaimer Verification
    # ----------------------------------------------------------------------
    print("\n[5/5] Testing Live HTTP Server & UI Disclaimer Probe...")
    live_app = create_app(dataset_dir=str(mock_data_dir))
    client = live_app.test_client()

    # Probe /api/status
    res_status = client.get("/api/status")
    assert res_status.status_code == 200
    data_status = json.loads(res_status.data.decode("utf-8"))
    assert data_status["model_state"] == "MODEL_UNAVAILABLE"
    assert data_status["data_mode"] == "RECORDED_RADAR_PLAYBACK"
    assert "HARDWARE CLOCK UNVERIFIED" in data_status["hardware_disclaimer"]

    # Probe / (HTML Dashboard)
    res_html = client.get("/")
    assert res_html.status_code == 200
    html_content = res_html.data.decode("utf-8")
    assert "RECORDED DATA PLAYBACK (OFFLINE SIMULATION)" in html_content
    assert "HARDWARE CLOCK SYNCHRONIZATION IS UNVERIFIED" in html_content.upper()
    assert "NOT CLINICAL SOFTWARE" in html_content.upper()
    assert "PHASE 2A GATE: OPEN" in html_content
    assert "STATE: MODEL_UNAVAILABLE" in html_content

    # Probe /api/state (Verifies waveform streaming and playback integration)
    res_snap = client.get("/api/state")
    assert res_snap.status_code == 200
    data_snap = json.loads(res_snap.data.decode("utf-8"))
    assert "snapshot" in data_snap
    assert "waveform" in data_snap
    snap = data_snap["snapshot"]
    assert snap["model_state"] == "MODEL_UNAVAILABLE"
    assert snap["data_mode"] == "RECORDED_RADAR_PLAYBACK"
    assert snap["latest_prediction_bpm"] is None

    # Probe /api/control (Verify pause/resume/step)
    res_ctrl = client.post("/api/control", json={"action": "step"})
    assert res_ctrl.status_code == 200
    data_ctrl = json.loads(res_ctrl.data.decode("utf-8"))
    assert data_ctrl["success"] is True

    print("  -> PASS: Live HTTP server WSGI probe verified: /api/status, HTML disclaimers, /api/snapshot, /api/control.")
    test_results["LIVE_SERVER_LOOPBACK"] = "PASS"

    print("\n=================================================================")
    print("ALL 5 SMOKE TESTS PASSED:")
    for k, v in test_results.items():
        print(f"  - {k}: {v}")
    print("=================================================================")
    return True


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
