// KAN FMCW Radar Heart-Rate Estimation Demo Frontend JavaScript
document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const recSelect = document.getElementById("recording-select");
  const speedSelect = document.getElementById("speed-select");
  const btnStart = document.getElementById("btn-start");
  const btnPause = document.getElementById("btn-pause");
  const btnResume = document.getElementById("btn-resume");
  const btnStep = document.getElementById("btn-step");
  const btnReset = document.getElementById("btn-reset");
  const btnExport = document.getElementById("btn-export");

  const valState = document.getElementById("val-state");
  const subState = document.getElementById("sub-state");
  const valTime = document.getElementById("val-time");
  const subTime = document.getElementById("sub-time");
  const valWindow = document.getElementById("val-window");
  const subWindow = document.getElementById("sub-window");
  const valFs = document.getElementById("val-fs");
  const valQuality = document.getElementById("val-quality");
  const valModel = document.getElementById("val-model");
  const subModel = document.getElementById("sub-model");
  const valHr = document.getElementById("val-hr");
  const subHr = document.getElementById("sub-hr");
  const valLatency = document.getElementById("val-latency");
  const lblSession = document.getElementById("lbl-session");
  const badgeMode = document.getElementById("badge-mode");
  const predTag = document.getElementById("pred-chart-tag");
  const windowCountPill = document.getElementById("window-count-pill");
  const historyTbody = document.getElementById("history-tbody");

  const radarCanvas = document.getElementById("radar-canvas");
  const hrCanvas = document.getElementById("hr-canvas");
  const ctxRadar = radarCanvas.getContext("2d");
  const ctxHr = hrCanvas.getContext("2d");

  let currentPlaybackState = "READY";
  let historyCache = [];
  let pollInterval = null;

  // 1. Initialize
  fetchStatus();
  fetchRecordings();
  startPolling();

  // 2. Fetch System Status
  async function fetchStatus() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      lblSession.textContent = data.session_id || "--";

      const badgeState = document.getElementById("badge-model-state");
      if (badgeState) {
        badgeState.textContent = `STATE: ${data.model_state || "MODEL_UNAVAILABLE"}`;
      }

      if (data.model_available && data.model_state === "REAL_MODEL_READY") {
        badgeMode.textContent = "SAVED MODEL INFERENCE";
        badgeMode.className = "badge badge-model-available";
        valModel.textContent = "REAL_MODEL_READY";
        valModel.className = "metric-value text-green";
        subModel.textContent = data.model_name;
        predTag.textContent = "Real Model Inference Active";
        predTag.className = "chart-tag";
      } else if (data.model_state === "SYNTHETIC_DEMO_ONLY") {
        badgeMode.textContent = "SYNTHETIC DEMO ONLY";
        badgeMode.className = "badge badge-model-unavailable";
        valModel.textContent = "SYNTHETIC ONLY";
        valModel.className = "metric-value text-amber";
        subModel.textContent = "Synthetic checkpoint — Real HR suppressed";
        predTag.textContent = "Synthetic Checkpoint — Real HR Predictions Suppressed";
        predTag.className = "chart-tag tag-warning";
      } else if (data.model_state === "REAL_MODEL_BLOCKED_BY_APPROVAL_GATE") {
        badgeMode.textContent = "GATE BLOCKED";
        badgeMode.className = "badge badge-model-unavailable";
        valModel.textContent = "GATE BLOCKED";
        valModel.className = "metric-value text-red";
        subModel.textContent = "Phase 2A Gate Open — Inference Blocked";
        predTag.textContent = "Real Model Blocked by Approval Gate";
        predTag.className = "chart-tag tag-warning";
      } else {
        badgeMode.textContent = "VISUALIZATION ONLY";
        badgeMode.className = "badge badge-model-unavailable";
        valModel.textContent = "UNAVAILABLE";
        valModel.className = "metric-value text-red";
        subModel.textContent = "No trained checkpoint";
        predTag.textContent = "Model Unavailable — Visualization Mode";
        predTag.className = "chart-tag tag-warning";
      }
    } catch (e) {
      console.error("Failed to fetch status:", e);
    }
  }

  // 3. Fetch Recordings List
  async function fetchRecordings() {
    try {
      const res = await fetch("/api/recordings");
      const data = await res.json();
      recSelect.innerHTML = "";
      if (data.recordings.length === 0) {
        recSelect.innerHTML = '<option value="">No recordings found</option>';
        return;
      }
      data.recordings.forEach((r) => {
        const opt = document.createElement("option");
        opt.value = r.recording_id;
        opt.textContent = `${r.recording_id} (${r.condition}, ${(r.file_size_bytes / 1024 / 1024).toFixed(1)} MB)`;
        if (r.recording_id === data.current_selected) {
          opt.selected = true;
        }
        recSelect.appendChild(opt);
      });
    } catch (e) {
      console.error("Failed to fetch recordings:", e);
    }
  }

  // 4. Polling Loop
  function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(updateDashboardState, 250);
  }

  async function updateDashboardState() {
    try {
      const res = await fetch("/api/state");
      const data = await res.json();
      const snap = data.snapshot;
      const wave = data.waveform;

      currentPlaybackState = snap.playback_state;
      updateControlButtons(currentPlaybackState);

      // Update Metric Cards
      valState.textContent = snap.playback_state;
      valState.className =
        snap.playback_state === "RUNNING"
          ? "metric-value text-green"
          : snap.playback_state === "PAUSED"
          ? "metric-value text-amber"
          : snap.playback_state === "COMPLETED"
          ? "metric-value text-muted"
          : "metric-value text-amber";

      subState.textContent = snap.error_message || (snap.playback_state === "RUNNING" ? `Replay @ ${snap.simulation_speed}x` : "Buffer ready");
      valTime.textContent = `${snap.elapsed_sim_time_s.toFixed(2)} s`;
      subTime.textContent = `Total: ${snap.total_duration_s.toFixed(1)} s (${snap.total_samples} pts)`;

      if (snap.current_window_idx >= 0) {
        valWindow.textContent = `#${snap.current_window_idx} [${(snap.current_window_idx * snap.hop_duration_s).toFixed(1)} - ${(snap.current_window_idx * snap.hop_duration_s + snap.window_duration_s).toFixed(1)}s]`;
      } else {
        valWindow.textContent = "None (Buffered)";
      }
      subWindow.textContent = `Window ${snap.processed_window_count} of ${snap.total_windows} max`;

      valFs.textContent = `${snap.sampling_rate_hz.toFixed(2)} Hz`;
      valQuality.textContent = snap.signal_quality_status;

      if (snap.latest_prediction_bpm !== null) {
        valHr.textContent = `${snap.latest_prediction_bpm.toFixed(1)} BPM`;
        valHr.className = "metric-value text-green";
        subHr.textContent = "Live KAN prediction";
        valLatency.textContent = `${snap.latest_latency_ms.toFixed(1)} ms`;
      } else {
        valHr.textContent = "N/A";
        valHr.className = "metric-value text-muted";
        subHr.textContent = snap.model_state === "SYNTHETIC_DEMO_ONLY"
          ? "Synthetic model (Real HR suppressed)"
          : snap.model_state === "REAL_MODEL_BLOCKED_BY_APPROVAL_GATE"
          ? "Gate blocked (Predictions suppressed)"
          : (snap.operating_mode === "VISUALIZATION_ONLY" ? "Model unavailable" : "No prediction");
        valLatency.textContent = "N/A";
      }

      // Draw Canvases
      drawRadarWaveform(wave);
      fetchAndUpdateHistory();
    } catch (e) {
      console.error("Dashboard update error:", e);
    }
  }

  // 5. Update Control Button States
  function updateControlButtons(state) {
    if (state === "RUNNING") {
      btnStart.disabled = true;
      btnPause.disabled = false;
      btnResume.disabled = true;
      btnStep.disabled = true;
    } else if (state === "PAUSED") {
      btnStart.disabled = true;
      btnPause.disabled = true;
      btnResume.disabled = false;
      btnStep.disabled = false;
    } else if (state === "COMPLETED") {
      btnStart.disabled = false;
      btnPause.disabled = true;
      btnResume.disabled = true;
      btnStep.disabled = true;
    } else {
      // READY or ERROR
      btnStart.disabled = false;
      btnPause.disabled = true;
      btnResume.disabled = true;
      btnStep.disabled = false;
    }
  }

  // 6. Draw Radar Waveform Canvas
  function drawRadarWaveform(wave) {
    const w = radarCanvas.width;
    const h = radarCanvas.height;
    ctxRadar.clearRect(0, 0, w, h);

    // Background Grid
    ctxRadar.strokeStyle = "#1e293b";
    ctxRadar.lineWidth = 1;
    for (let x = 0; x < w; x += 80) {
      ctxRadar.beginPath();
      ctxRadar.moveTo(x, 0);
      ctxRadar.lineTo(x, h);
      ctxRadar.stroke();
    }
    for (let y = 0; y < h; y += 50) {
      ctxRadar.beginPath();
      ctxRadar.moveTo(0, y);
      ctxRadar.lineTo(w, y);
      ctxRadar.stroke();
    }

    if (!wave || !wave.times_s || wave.times_s.length < 2) {
      ctxRadar.fillStyle = "#64748b";
      ctxRadar.font = "13px monospace";
      ctxRadar.textAlign = "center";
      ctxRadar.fillText("No radar signal buffer loaded", w / 2, h / 2);
      return;
    }

    const tMin = wave.times_s[0];
    const tMax = wave.times_s[wave.times_s.length - 1];
    const tSpan = Math.max(0.1, tMax - tMin);

    // Amplitude scale
    let yMin = Math.min(...wave.filtered_radar);
    let yMax = Math.max(...wave.filtered_radar);
    if (Math.abs(yMax - yMin) < 1e-4) {
      yMin -= 1.0;
      yMax += 1.0;
    }
    const ySpan = yMax - yMin;

    // Highlight Active 10-Second Window
    if (wave.window_bounds) {
      const xStart = ((wave.window_bounds.start_time_s - tMin) / tSpan) * w;
      const xEnd = ((wave.window_bounds.end_time_s - tMin) / tSpan) * w;
      const boxW = Math.max(2, xEnd - xStart);

      ctxRadar.fillStyle = "rgba(56, 189, 248, 0.12)";
      ctxRadar.fillRect(xStart, 0, boxW, h);

      ctxRadar.strokeStyle = "rgba(56, 189, 248, 0.7)";
      ctxRadar.lineWidth = 1.5;
      ctxRadar.strokeRect(xStart, 0, boxW, h);

      ctxRadar.fillStyle = "#38bdf8";
      ctxRadar.font = "11px sans-serif";
      ctxRadar.textAlign = "left";
      ctxRadar.fillText(`Window [${wave.window_bounds.start_time_s} - ${wave.window_bounds.end_time_s}s]`, Math.max(10, xStart + 6), 18);
    }

    // Draw Signal Line
    ctxRadar.beginPath();
    ctxRadar.strokeStyle = "#38bdf8";
    ctxRadar.lineWidth = 2.0;

    for (let i = 0; i < wave.times_s.length; i++) {
      const x = ((wave.times_s[i] - tMin) / tSpan) * w;
      const y = h - ((wave.filtered_radar[i] - yMin) / ySpan) * (h - 40) - 20;
      if (i === 0) ctxRadar.moveTo(x, y);
      else ctxRadar.lineTo(x, y);
    }
    ctxRadar.stroke();

    // Time Axis Labels
    ctxRadar.fillStyle = "#94a3b8";
    ctxRadar.font = "10px monospace";
    ctxRadar.textAlign = "left";
    ctxRadar.fillText(`t=${tMin.toFixed(1)}s`, 10, h - 8);
    ctxRadar.textAlign = "right";
    ctxRadar.fillText(`t=${tMax.toFixed(1)}s`, w - 10, h - 8);
  }

  // 7. Update Heart Rate Predictions Canvas & Table
  async function fetchAndUpdateHistory() {
    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      historyCache = data.history || [];

      windowCountPill.textContent = `${historyCache.length} Windows Processed`;
      drawHrPlot(historyCache);
      renderHistoryTable(historyCache);
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  }

  function drawHrPlot(history) {
    const w = hrCanvas.width;
    const h = hrCanvas.height;
    ctxHr.clearRect(0, 0, w, h);

    // Grid
    ctxHr.strokeStyle = "#1e293b";
    ctxHr.lineWidth = 1;
    for (let y = 40; y < h; y += 40) {
      ctxHr.beginPath();
      ctxHr.moveTo(0, y);
      ctxHr.lineTo(w, y);
      ctxHr.stroke();
    }

    const validPredictions = history.filter((r) => r.prediction_bpm !== null);

    if (validPredictions.length === 0) {
      // Clean, honest placeholder when model is unavailable
      ctxHr.fillStyle = "#475569";
      ctxHr.font = "13px sans-serif";
      ctxHr.textAlign = "center";
      ctxHr.fillText("MODEL UNAVAILABLE (VISUALIZATION ONLY)", w / 2, h / 2 - 12);
      ctxHr.fillStyle = "#64748b";
      ctxHr.font = "11px monospace";
      ctxHr.fillText("Zero predictions plotted — No fabricated BPM values", w / 2, h / 2 + 12);
      return;
    }

    // If valid predictions exist, plot them
    const bpmMin = 40;
    const bpmMax = 140;
    const tMin = 0;
    const tMax = 120;

    // Y Axis markings
    ctxHr.fillStyle = "#64748b";
    ctxHr.font = "10px sans-serif";
    ctxHr.textAlign = "left";
    ctxHr.fillText("140 BPM", 8, 20);
    ctxHr.fillText("90 BPM", 8, h / 2);
    ctxHr.fillText("40 BPM", 8, h - 10);

    ctxHr.beginPath();
    ctxHr.strokeStyle = "#34d399";
    ctxHr.lineWidth = 2.5;

    validPredictions.forEach((p, idx) => {
      const x = (p.end_time_s / tMax) * (w - 40) + 30;
      const y = h - ((p.prediction_bpm - bpmMin) / (bpmMax - bpmMin)) * (h - 40) - 20;

      if (idx === 0) ctxHr.moveTo(x, y);
      else ctxHr.lineTo(x, y);
    });
    ctxHr.stroke();

    // Draw points
    ctxHr.fillStyle = "#34d399";
    validPredictions.forEach((p) => {
      const x = (p.end_time_s / tMax) * (w - 40) + 30;
      const y = h - ((p.prediction_bpm - bpmMin) / (bpmMax - bpmMin)) * (h - 40) - 20;
      ctxHr.beginPath();
      ctxHr.arc(x, y, 4, 0, 2 * Math.PI);
      ctxHr.fill();
    });
  }

  function renderHistoryTable(history) {
    if (history.length === 0) {
      historyTbody.innerHTML = `
        <tr class="empty-row">
          <td colspan="7">No windows processed yet. Click <strong>Start</strong> or <strong>Step Window</strong> to begin simulation replay.</td>
        </tr>`;
      return;
    }

    // Render in reverse chronological order (newest on top)
    const reversed = [...history].reverse();
    let html = "";
    reversed.forEach((r) => {
      const statusClass =
        r.processing_status === "SUCCESS"
          ? "chip-success"
          : r.processing_status === "MODEL_UNAVAILABLE"
          ? "chip-unavail"
          : "chip-invalid";

      const bpmDisplay = r.prediction_bpm !== null ? `${r.prediction_bpm.toFixed(1)}` : "N/A";
      const latDisplay = r.inference_latency_ms > 0 ? `${r.inference_latency_ms.toFixed(1)}` : "0.0";

      html += `
        <tr>
          <td><strong>#${r.window_index}</strong></td>
          <td>${r.start_time_s.toFixed(1)} - ${r.end_time_s.toFixed(1)} s</td>
          <td>${r.sample_count}</td>
          <td><span class="${statusClass}">${r.processing_status}</span></td>
          <td>${bpmDisplay}</td>
          <td>${latDisplay}</td>
          <td><small>${r.provenance_note} ${r.error_reason ? `(${r.error_reason})` : ""}</small></td>
        </tr>`;
    });
    historyTbody.innerHTML = html;
  }

  // 8. Event Listeners for Controls
  btnStart.addEventListener("click", () => postControl("start"));
  btnPause.addEventListener("click", () => postControl("pause"));
  btnResume.addEventListener("click", () => postControl("resume"));
  btnStep.addEventListener("click", () => postControl("step"));
  btnReset.addEventListener("click", () => postControl("reset"));

  speedSelect.addEventListener("change", (e) => {
    postControl("speed", { speed: parseFloat(e.target.value) });
  });

  recSelect.addEventListener("change", async (e) => {
    const recId = e.target.value;
    if (!recId) return;
    try {
      const res = await fetch("/api/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recording_id: recId }),
      });
      const data = await res.json();
      if (!data.success) {
        alert(`Failed to load recording: ${data.error}`);
      }
    } catch (err) {
      console.error("Select error:", err);
    }
  });

  btnExport.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/export", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert(`Session logs exported successfully:\nMetadata: ${data.metadata_file}\nHistory: ${data.history_file}`);
      }
    } catch (err) {
      console.error("Export error:", err);
    }
  });

  async function postControl(action, payload = {}) {
    try {
      const body = { action, ...payload };
      await fetch("/api/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch (e) {
      console.error(`Control error on ${action}:`, e);
    }
  }
});
