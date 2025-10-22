"""
Temporal Synchronization Loop
Author: John B. Carroll Jr.
Purpose: Software-level clock synchronization using PI_R as phase regulator.
Notes:
 - Default behavior adjusts only a software offset (safe).
 - Optionally set_system_clock=True to actually modify OS clock (requires privileges).
"""

import time
import socket
import json
import hashlib
import requests   # used only if broadcasting/handshake -> optional
from typing import Tuple, Optional

# Recursive pi constant (phase regulator)
PI_R = 3.17300858012

# --- Utility: software time accessor (applies offset) ---
class SoftwareClock:
    def __init__(self):
        self.offset = 0.0  # seconds, positive means local clock lags remote
    def now(self) -> float:
        return time.time() + self.offset
    def apply_offset(self, delta_seconds: float):
        self.offset += delta_seconds

# --- Lightweight NTP-style calculation helpers ---
def compute_offset_and_rtt(t0: float, t1: float, t2: float, t3: float) -> Tuple[float, float]:
    """
    t0 = client send (A sends to B)
    t1 = server receive (B receives)
    t2 = server send (B replies)
    t3 = client receive (A receives)
    Standard formulas:
      offset = ((t1 - t0) + (t2 - t3)) / 2  [same as ((t1+t2)-(t0+t3))/2]
      rtt    = (t3 - t0) - (t2 - t1)
    We return (offset, rtt)
    """
    offset = ((t1 + t2) - (t0 + t3)) / 2.0
    rtt = (t3 - t0) - (t2 - t1)
    return offset, rtt

# --- Adaptive smoothing gain derived from PI_R ---
def smoothing_alpha(pi_r: float = PI_R) -> float:
    """
    Determine smoothing factor alpha ∈ (0,1).
    We want moderate responsiveness but not oscillation.
    Use a mapping: alpha = min(0.5, 1 / (pi_r * scale))
    scale choice: 50 -> alpha ≈ 1/(PI_R*50) ≈ 0.0063
    This is intentionally small for stability. Users can tune scale.
    """
    scale = 50.0
    alpha = 1.0 / (pi_r * scale)
    if alpha > 0.5:
        alpha = 0.5
    return float(alpha)

# --- Handshake logging hook (optional) ---
def record_sync_receipt(seed: str, receipt_sink: str = "data/handshake_log.jsonl") -> dict:
    """
    Minimal local receipt for a sync event. This can be fed into the handshake ledger.
    """
    ts_ms = str(int(time.time() * 1000))
    entry = {
        "entity": "TemporalSyncService",
        "seed": seed,
        "timestamp_unix_ms": ts_ms,
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "node": socket.gethostname()
    }
    # append safely
    try:
        import os
        os.makedirs(os.path.dirname(receipt_sink), exist_ok=True)
        with open(receipt_sink, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    return entry

# --- Core: run a single sync exchange with a peer ---
def sync_with_peer(peer_endpoint: str,
                   clock: SoftwareClock,
                   timeout: float = 2.0,
                   handshake_sink: Optional[str] = None,
                   set_system_clock: bool = False) -> dict:
    """
    Do a single sync round with peer_endpoint (HTTP POST expected).
    peer_endpoint should accept {'t0': float} and reply with JSON:
       {'t1': <server_recv_time>, 't2': <server_send_time>}
    Returns dict containing measured offset, rtt, applied_delta, etc.
    """
    # Prepare times
    t0 = clock.now()
    payload = {"t0": t0, "node": socket.gethostname()}
    try:
        resp = requests.post(peer_endpoint, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        t1 = float(data.get("t1"))
        t2 = float(data.get("t2"))
        t3 = clock.now()

        offset, rtt = compute_offset_and_rtt(t0, t1, t2, t3)

        # Smoothing using PI_R-derived alpha
        alpha = smoothing_alpha(PI_R)
        applied_delta = alpha * offset  # incremental change

        # Update software clock
        clock.apply_offset(applied_delta)

        # Optional: set system clock (admin only)
        if set_system_clock:
            try:
                # requires privileges; call system tools carefully (not enabled by default)
                import subprocess
                new_time = time.time() + clock.offset
                # Example (POSIX): date -s @<seconds>
                subprocess.run(["sudo", "date", "-s", "@{}".format(int(new_time))], check=True)
            except Exception:
                # do not crash on failure; log externally
                pass

        # Optionally record handshake/sync event
        receipt = None
        if handshake_sink:
            seed = f"temporal_sync:{socket.gethostname()}:{int(time.time()*1000)}"
            receipt = record_sync_receipt(seed, receipt_sink)

        return {
            "status": "ok",
            "peer": peer_endpoint,
            "t0": t0, "t1": t1, "t2": t2, "t3": t3,
            "offset_estimate": offset,
            "rtt": rtt,
            "alpha": alpha,
            "applied_delta": applied_delta,
            "software_offset": clock.offset,
            "handshake": receipt
        }
    except Exception as e:
        return {"status": "error", "peer": peer_endpoint, "error": str(e)}

# --- Example server endpoint to handle peer sync requests ---
# Minimal Flask-style handler (user can adapt to their web framework)
def peer_sync_handler(request_json) -> dict:
    """
    Peer receives t0 from requester, records receive time t1, and replies with t1 and t2.
    Expected input JSON: {'t0': <float>, 'node': <str>}
    Reply: {'t1': <server_receive>, 't2': <server_send>}
    """
    # In a web handler you would parse request.body -> request_json
    t1 = time.time()
    # (perform minimal processing)
    t2 = time.time()  # nearly immediate reply
    return {"t1": t1, "t2": t2, "node": socket.gethostname()}

# --- Sync loop orchestration ---
def run_sync_loop(peers: list,
                  interval_base: float = 30.0,
                  clock: Optional[SoftwareClock] = None,
                  handshake_sink: Optional[str] = "data/handshake_log.jsonl",
                  set_system_clock: bool = False):
    """
    Continuously sync against a list of peers.
    interval_base: base seconds between rounds; actual interval modulated by PI_R.
    Using PI_R to set interval: interval = interval_base * (PI_R / 3.0) roughly.
    """
    if clock is None:
        clock = SoftwareClock()
    # derive interval modulated by PI_R (keeps it in practical range)
    interval = max(5.0, interval_base * (PI_R / 3.0))
    try:
        while True:
            for peer in peers:
                result = sync_with_peer(peer, clock, handshake_sink=handshake_sink, set_system_clock=set_system_clock)
                # you may route result to logger, handshake ledger, or monitoring
                print(json.dumps(result))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Sync loop terminated by user.")