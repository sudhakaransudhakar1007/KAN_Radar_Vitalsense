"""Command-line runner for deterministic recorded radar replay simulation.

Allows running, auditing, and exporting streaming simulations from the terminal
without requiring a web browser.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure kan_radar_HR root is in sys.path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.demo.model_loader import SafeModelInferenceEngine
from src.demo.simulation_engine import RadarSimulationEngine


def main():
    parser = argparse.ArgumentParser(
        description="Recorded Radar Data — Streaming Replay Simulation CLI Runner"
    )
    parser.add_argument(
        "--dataset-dir",
        default="../data/VITALSENSE_120_DATASET",
        help="Path to VITALSENSE dataset directory",
    )
    parser.add_argument(
        "--recording",
        default="VS01_Resting",
        help="Recording ID or filename to replay (e.g. VS01_Resting)",
    )
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Path to optional model checkpoint",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/demo_simulation/run_001",
        help="Directory to save simulation audit logs",
    )
    parser.add_argument(
        "--max-windows",
        type=int,
        default=22,
        help="Maximum number of windows to process",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("RECORDED RADAR DATA — STREAMING SIMULATION CLI")
    print("Disclaimer: Software replay of recorded radar. Hardware clock unverified.")
    print("=" * 70)

    # Initialize model engine
    model_engine = SafeModelInferenceEngine(
        model_name="KANRegressor",
        checkpoint_path=args.checkpoint,
    )
    compat = model_engine.get_compatibility_status()
    print(f"Operating Mode:    {compat.operating_mode}")
    print(f"Model Name:        {compat.model_name}")
    print(f"Model Available:   {compat.is_available}")
    print(f"Model Note:        {compat.status_reason}")

    # Initialize simulation engine
    engine = RadarSimulationEngine(
        dataset_dir=args.dataset_dir,
        model_engine=model_engine,
    )

    # Find recording file
    recordings = engine.discover_recordings()
    target_rec = None
    for r in recordings:
        if r["recording_id"] == args.recording or Path(r["file_path"]).name == args.recording:
            target_rec = r["file_path"]
            break

    if not target_rec:
        print(f"\n[ERROR] Recording '{args.recording}' not found in {args.dataset_dir}")
        print("Available recordings:")
        for r in recordings[:10]:
            print(f"  {r['recording_id']} ({r['condition']})")
        sys.exit(1)

    print(f"\nLoading recording: {target_rec}")
    ok = engine.load_recording(target_rec)
    if not ok:
        print(f"[ERROR] Failed to load recording: {engine.error_message}")
        sys.exit(1)

    snap = engine.get_snapshot()
    print(f"Recording ID:      {snap.recording_id}")
    print(f"Sampling Rate:     {snap.sampling_rate_hz:.4f} Hz")
    print(f"Total Duration:    {snap.total_duration_s:.2f} s ({snap.total_samples} samples)")
    print(f"Window Config:     {snap.window_duration_s}s window ({snap.window_samples} pts) / {snap.hop_duration_s}s hop ({snap.hop_samples} pts)")
    print(f"Total Windows:     {snap.total_windows}")
    print(f"Signal Quality:    {snap.signal_quality_status}")

    print("\n" + "=" * 70)
    print(f"{'Win #':<7} | {'Time Interval':<16} | {'Samples':<8} | {'Status':<18} | {'HR (BPM)':<10} | {'Latency':<8}")
    print("-" * 70)

    # Step through windows
    processed = 0
    while processed < args.max_windows and engine.playback_state != "COMPLETED":
        rec = engine.step()
        if not rec:
            break
        processed += 1
        bpm_str = f"{rec.prediction_bpm:.2f}" if rec.prediction_bpm is not None else "N/A"
        lat_str = f"{rec.inference_latency_ms:.1f}ms" if rec.inference_latency_ms > 0 else "0.0ms"
        time_str = f"[{rec.start_time_s:5.1f} - {rec.end_time_s:5.1f}s]"
        print(f"#{rec.window_index:<6} | {time_str:<16} | {rec.sample_count:<8} | {rec.processing_status:<18} | {bpm_str:<10} | {lat_str:<8}")

    print("-" * 70)
    print(f"Simulation completed: {processed} windows processed.")

    # Export session logs
    meta_p, hist_p = engine.export_session_logs(args.output_dir)
    print(f"\nAudit logs saved:")
    print(f"  Metadata: {meta_p}")
    print(f"  History:  {hist_p}")


if __name__ == "__main__":
    main()
