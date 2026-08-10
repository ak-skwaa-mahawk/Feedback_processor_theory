"""
Synara Auto-Tune Listener v1.3
-------------------------------
Adds multi-dimensional input for adaptive decay tuning:
- Stability deviations
- Chunk latency
- Throughput
- CPU load / Memory load
- Error rates

Weights each input, computes a weighted EMA, applies auto-lock
when oscillations are detected.

Author: John Carroll / Two Mile Solutions LLC
License: Open Collaboration with Attribution (FPT)
"""

import json, os, time, math
from datetime import datetime, timedelta

# --- Configurable Paths & Parameters ---
STABILITY_LOG_PATH = "data/stability_log.json"
SYSTEM_METRICS_PATH = "data/system_metrics.json"
TUNE_CONFIG_PATH = "data/autotune_state.json"

MAX_LOOKBACK_MINUTES = 15
STABILITY_THRESHOLD = 0.15
DECAY_TUNE_STEP = 0.05
MIN_DECAY = 0.05
MAX_DECAY = 0.35
EMA_ALPHA = 0.25

# Auto-lock
OSCILLATION_THRESHOLD = 0.08
LOCK_DURATION = 180  # seconds

# Sensor Weights (sum ≤ 1)
SENSOR_WEIGHTS = {
    "stability": 0.4,
    "latency": 0.25,
    "throughput": 0.15,
    "cpu_load": 0.1,
    "error_rate": 0.1
}

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def exponential_moving_average(values, alpha=EMA_ALPHA):
    if not values:
        return 0
    ema = values[0]
    for v in values[1:]:
        ema = alpha * v + (1 - alpha) * ema
    return ema

def compute_weighted_deviation(stability_dev, metrics):
    """Combine all metrics into a weighted deviation score"""
    w = SENSOR_WEIGHTS
    weighted = (
        stability_dev * w["stability"] +
        metrics.get("latency", 0) * w["latency"] +
        (1 - metrics.get("throughput", 1)) * w["throughput"] +
        metrics.get("cpu_load", 0) * w["cpu_load"] +
        metrics.get("error_rate", 0) * w["error_rate"]
    )
    return weighted

def compute_new_decay(current_decay, weighted_dev):
    if weighted_dev > STABILITY_THRESHOLD:
        new_decay = max(current_decay - DECAY_TUNE_STEP, MIN_DECAY)
    else:
        new_decay = min(current_decay + DECAY_TUNE_STEP, MAX_DECAY)
    return round(new_decay, 3)

def autotune_decay(current_decay=0.12):
    now = datetime.utcnow()
    tune_state = load_json(TUNE_CONFIG_PATH)

    # --- Lock Check ---
    if "lock_until" in tune_state:
        lock_until = datetime.fromisoformat(tune_state["lock_until"])
        if now < lock_until:
            print(f"[AutoTune] Locked until {lock_until.isoformat()} – holding decay at {current_decay:.3f}")
            return current_decay

    # --- Load Logs ---
    stability_log = load_json(STABILITY_LOG_PATH)
    system_metrics = load_json(SYSTEM_METRICS_PATH)

    cutoff = now - timedelta(minutes=MAX_LOOKBACK_MINUTES)
    recent_devs = [
        e["deviation"]
        for chunk, entries in stability_log.items()
        for e in entries[-10:]
        if datetime.fromisoformat(e["time"]) >= cutoff
    ]
    stability_dev = exponential_moving_average(recent_devs) if recent_devs else 0

    # --- Compute Weighted Deviation ---
    weighted_dev = compute_weighted_deviation(stability_dev, system_metrics)
    new_decay = compute_new_decay(current_decay, weighted_dev)

    # --- Oscillation Detection ---
    last_decay = tune_state.get("previous_decay", current_decay)
    decay_change = abs(new_decay - last_decay)
    lock_triggered = decay_change > OSCILLATION_THRESHOLD

    if lock_triggered:
        lock_until = now + timedelta(seconds=LOCK_DURATION)
        tune_state["lock_until"] = lock_until.isoformat()
        print(f"[AutoTune] ⚠️ Oscillation detected (Δ={decay_change:.3f}) → Locking until {lock_until.isoformat()}")

    # --- Update State ---
    tune_state.update({
        "timestamp": now.isoformat(),
        "weighted_deviation": round(weighted_dev, 4),
        "previous_decay": current_decay,
        "new_decay": new_decay,
        "ema_alpha": EMA_ALPHA,
        "decay_change": decay_change,
        "locked": lock_triggered
    })

    save_json(TUNE_CONFIG_PATH, tune_state)

    if not lock_triggered:
        print(f"[AutoTune] Multi-sensor EMA-tuned decay: {current_decay:.3f} → {new_decay:.3f} (weighted_dev={weighted_dev:.3f})")

    return new_decay if not lock_triggered else current_decay

if __name__ == "__main__":
    decay = 0.12
    while True:
        decay = autotune_decay(decay)
        time.sleep(60)