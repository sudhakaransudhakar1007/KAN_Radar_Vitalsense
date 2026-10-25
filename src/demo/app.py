"""Flask Web Application and REST API for Recorded Radar Data Streaming Demo.

Serves the interactive research dashboard and provides REST endpoints for
deterministic playback control, real-time waveform streaming, and window history.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure kan_radar_HR root is in sys.path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from flask import Flask, jsonify, render_template, request, send_from_directory

from src.demo.model_loader import SafeModelInferenceEngine
from src.demo.simulation_engine import RadarSimulationEngine


def create_app(
    dataset_dir: str = "../data/VITALSENSE_120_DATASET",
    checkpoint_path: Optional[str] = None,
    output_dir: str = "outputs/demo_simulation/run_001",
    model_engine: Optional[SafeModelInferenceEngine] = None,
) -> Flask:
    """Application factory for demo simulation server."""
    base_dir = Path(__file__).resolve().parent
    template_dir = base_dir / "templates"
    static_dir = base_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )

    # Initialize model engine and simulation engine
    if model_engine is None:
        model_engine = SafeModelInferenceEngine(
            model_name="KANRegressor",
            checkpoint_path=checkpoint_path,
        )
    engine = RadarSimulationEngine(
        dataset_dir=dataset_dir,
        model_engine=model_engine,
    )

    # Background playback loop state
    playback_lock = threading.Lock()
    playback_thread: Optional[threading.Thread] = None
    stop_event = threading.Event()

    def background_playback_worker():
        """Background thread advancing virtual simulation clock according to playback state and speed."""
        last_wall_time = time.time()
        while not stop_event.is_set():
            time.sleep(0.05)  # 20 Hz update loop
            now = time.time()
            wall_dt = now - last_wall_time
            last_wall_time = now

            with playback_lock:
                if engine.playback_state == "RUNNING":
                    # Scale virtual clock by simulation speed
                    sim_dt = wall_dt * engine.simulation_speed
                    engine.advance_time(sim_dt)

    # Start persistent background thread
    playback_thread = threading.Thread(target=background_playback_worker, daemon=True)
    playback_thread.start()

    # Automatically load first recording if available
    recordings = engine.discover_recordings()
    if recordings:
        engine.load_recording(recordings[0]["file_path"])

    @app.route("/")
    def index():
        """Serves main research dashboard single page application."""
        return render_template("index.html")

    @app.route("/api/status", methods=["GET"])
    def get_status():
        """System governance, mode, and disclaimer status."""
        compat = model_engine.get_compatibility_status()
        return jsonify({
            "project_title": "Subject-Independent KAN FMCW Radar HR Estimation",
            "phase": "Phase 8 — Recorded Radar Data Streaming Simulation",
            "simulation_mode": compat.operating_mode,
            "governance_gate": "OPEN (outputs/phase2a/step2b_consistency_audit.md)",
            "hardware_disclaimer": "RECORDED DATA SIMULATION — HARDWARE CLOCK UNVERIFIED — NOT CLINICAL SOFTWARE",
            "model_name": compat.model_name,
            "model_available": compat.is_available,
            "model_state": compat.model_state,
            "data_mode": compat.data_mode,
            "model_status_reason": compat.status_reason,
            "session_id": engine.session_id,
        })

    @app.route("/api/recordings", methods=["GET"])
    def list_recordings():
        """Returns list of all available radar recordings in dataset directory."""
        recs = engine.discover_recordings()
        return jsonify({
            "count": len(recs),
            "recordings": recs,
            "current_selected": engine.recording_id,
        })

    @app.route("/api/select", methods=["POST"])
    def select_recording():
        """Selects and loads a specific recorded radar file."""
        data = request.get_json(force=True, silent=True) or {}
        file_path = data.get("file_path")
        recording_id = data.get("recording_id")

        if not file_path and recording_id:
            for r in engine.discover_recordings():
                if r["recording_id"] == recording_id:
                    file_path = r["file_path"]
                    break

        if not file_path:
            return jsonify({"success": False, "error": "file_path or recording_id required"}), 400

        with playback_lock:
            ok = engine.load_recording(file_path)
            if ok:
                return jsonify({
                    "success": True,
                    "recording_id": engine.recording_id,
                    "sampling_rate_hz": engine.fs_hz,
                    "total_samples": len(engine.raw_signal),
                    "total_duration_s": round(len(engine.raw_signal) / engine.fs_hz, 2),
                    "total_windows": engine.total_windows,
                })
            else:
                return jsonify({"success": False, "error": engine.error_message}), 400

    @app.route("/api/control", methods=["POST"])
    def control_simulation():
        """Controls simulation playback: start, pause, resume, reset, step, speed."""
        data = request.get_json(force=True, silent=True) or {}
        action = data.get("action", "").lower()

        with playback_lock:
            if action == "start":
                engine.start()
            elif action == "pause":
                engine.pause()
            elif action == "resume":
                engine.resume()
            elif action == "reset":
                engine.reset()
            elif action == "step":
                engine.step()
            elif action == "speed":
                speed = float(data.get("speed", 1.0))
                if speed in (0.5, 1.0, 2.0):
                    engine.simulation_speed = speed
                else:
                    return jsonify({"success": False, "error": "Invalid speed. Choose 0.5, 1.0, or 2.0"}), 400
            else:
                return jsonify({"success": False, "error": f"Unknown action: {action}"}), 400

            snap = engine.get_snapshot()
            return jsonify({
                "success": True,
                "action": action,
                "playback_state": engine.playback_state,
                "elapsed_sim_time_s": engine.elapsed_sim_time_s,
                "current_window_idx": engine.current_window_idx,
            })

    @app.route("/api/state", methods=["GET"])
    def get_state():
        """Provides snapshot of simulation state and downsampled waveform for rendering."""
        with playback_lock:
            snap = engine.get_snapshot()
            waveform = engine.get_waveform_display_data(max_points=500)
            return jsonify({
                "snapshot": asdict(snap),
                "waveform": waveform,
            })

    @app.route("/api/history", methods=["GET"])
    def get_history():
        """Returns full window processing history."""
        with playback_lock:
            return jsonify({
                "count": len(engine.window_history),
                "history": [asdict(r) for r in engine.window_history],
            })

    @app.route("/api/export", methods=["POST"])
    def export_logs():
        """Exports session logs and window history to output_dir."""
        with playback_lock:
            m_path, h_path = engine.export_session_logs(output_dir)
            return jsonify({
                "success": True,
                "metadata_file": str(m_path),
                "history_file": str(h_path),
            })

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Demo Simulation Dashboard on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
