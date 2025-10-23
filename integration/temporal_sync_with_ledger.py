"""
Temporal Sync with Ledger Hook
--------------------------------
- Performs NTP-style sync with a peer.
- Automatically creates a chain-linked handshake receipt for each successful sync,
  appending it to data/handshake_log.jsonl.
- Uses the chain-linked handshake_message from `integration/handshake_ledger.py`.

Assumptions:
- Python 3.10+
- Ledger: data/handshake_log.jsonl
- Peer endpoints are simple HTTP(S) endpoints that accept {'t0': <float>, 'node': <str>}
  and reply with {'t1': <float>, 't2': <float>}
"""

import time
import socket
import json
import os
from typing import Optional
import hashlib

import requests

# Import the chain-linked handshake function previously specified.
# Ensure integration/handshake_ledger.py defines handshake_message(...) returning a dict
# with 'digest' and 'chain_digest' fields.
try:
    from integration.handshake_ledger import handshake_message, verify_handshake_chain
except Exception:
    # If module not yet present in repo, provide a fallback minimal chain writer.
    def _fallback_handshake_message(seed: str, entity: str = "TwoMileSolutionsLLC",
                                    version: str = "1.2", log_file: str = "data/handshake_log.jsonl"):
        """
        Minimal fallback chain writer: record simple JSON line if imported module missing.
        """
        ts_unix = str(int(time.time() * 1000))
        ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        hostname = socket.gethostname()
        # attempt to read previous chain_digest
        prev_digest = None
        if os.path.isfile(log_file):
            try:
                with open(log_file, "rb") as f:
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b"\n":
                        f.seek(-2, os.SEEK_CUR)
                    last_line = f.readline().decode()
                    prev_entry = json.loads(last_line)
                    prev_digest = prev_entry.get("chain_digest") or prev_entry.get("digest")
            except Exception:
                prev_digest = None

        payload_parts = [entity, seed.strip(), ts_unix, hostname]
        if prev_digest:
            payload_parts.append(prev_digest)
        payload = "|".join(payload_parts)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        chain_digest = hashlib.sha256((digest + (prev_digest or "")).encode()).hexdigest()

        receipt = {
            "entity": entity,
            "version": version,
            "timestamp_unix_ms": ts_unix,
            "timestamp_iso": ts_iso,
            "seed": seed.strip(),
            "digest": digest,
            "chain_digest": chain_digest,
            "previous_digest": prev_digest,
            "node": hostname
        }
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(receipt) + "\n")
        return receipt

    handshake_message = _fallback_handshake_message
    verify_handshake_chain = lambda log_file="data/handshake_log.jsonl": {"status": "fallback", "message": "verify unavailable in fallback"}

# Recursive pi constant (used for smoothing or seed)
PI_R = 3.17300858012

# Simple software clock
class SoftwareClock:
    def __init__(self):
        self.offset = 0.0  # seconds

    def now(self) -> float:
        return time.time() + self.offset

    def apply_offset(self, delta_seconds: float):
        self.offset += delta_seconds

# NTP-style computations
def compute_offset_and_rtt(t0: float, t1: float, t2: float, t3: float):
    offset = ((t1 + t2) - (t0 + t3)) / 2.0
    rtt = (t3 - t0) - (t2 - t1)
    return offset, rtt

# Smoothing factor derived from PI_R (conservative by default)
def smoothing_alpha(pi_r: float = PI_R, scale: float = 50.0) -> float:
    alpha = 1.0 / (pi_r * scale)
    return min(max(alpha, 1e-4), 0.5)

# --- Core: sync and ledger-hook ---
def sync_with_peer_and_record(peer_endpoint: str,
                              clock: SoftwareClock,
                              handshake_entity: str = "TemporalSyncService",
                              handshake_sink: str = "data/handshake_log.jsonl",
                              timeout: float = 3.0,
                              set_system_clock: bool = False) -> dict:
    """
    Perform a sync with peer_endpoint and record a chain-linked handshake on success.
    Returns a dict with sync details and handshake receipt (if recorded).
    """
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
        alpha = smoothing_alpha(PI_R)
        applied_delta = alpha * offset
        clock.apply_offset(applied_delta)

        # Optional system clock set (admin-only)
        if set_system_clock:
            try:
                import subprocess
                new_time = time.time() + clock.offset
                subprocess.run(["sudo", "date", "-s", "@{}".format(int(new_time))], check=True)
            except Exception:
                pass

        # --- Ledger hook: create chain-linked handshake receipt ---
        seed = f"sync::{peer_endpoint}::{int(time.time()*1000)}"
        receipt = handshake_message(seed=seed, entity=handshake_entity, version="1.2", log_file=handshake_sink)

        result = {
            "status": "ok",
            "peer": peer_endpoint,
            "t0": t0, "t1": t1, "t2": t2, "t3": t3,
            "offset_estimate": offset,
            "rtt": rtt,
            "alpha": alpha,
            "applied_delta": applied_delta,
            "software_offset": clock.offset,
            "handshake_receipt": receipt
        }
        return result

    except Exception as e:
        return {"status": "error", "peer": peer_endpoint, "error": str(e)}

# Batch run helper (records each success)
def run_sync_round(peers: list,
                   clock: Optional[SoftwareClock] = None,
                   handshake_sink: str = "data/handshake_log.jsonl",
                   set_system_clock: bool = False):
    """
    Run a one-shot sync against all peers and record receipts for successful syncs.
    Use this in cron/systemd timer or orchestrator.
    """
    if clock is None:
        clock = SoftwareClock()

    results = []
    os.makedirs(os.path.dirname(handshake_sink), exist_ok=True)

    for peer in peers:
        res = sync_with_peer_and_record(peer, clock, handshake_entity="TemporalSyncService",
                                        handshake_sink=handshake_sink, set_system_clock=set_system_clock)
        results.append(res)

    # Optional: verify chain after this round
    try:
        verify_result = verify_handshake_chain(handshake_sink)
    except Exception:
        verify_result = {"status": "verify_unavailable"}

    return {"sync_results": results, "verify": verify_result}

# CLI convenience
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run temporal sync round and record chain-linked handshake receipts.")
    parser.add_argument("--peers", nargs="+", required=True, help="Peer sync endpoints (full URL).")
    parser.add_argument("--handshake_sink", default="data/handshake_log.jsonl", help="Ledger path")
    parser.add_argument("--set_system_clock", action="store_true", help="Attempt to set system clock (requires sudo)")
    args = parser.parse_args()

    clock = SoftwareClock()
    out = run_sync_round(args.peers, clock=clock, handshake_sink=args.handshake_sink, set_system_clock=args.set_system_clock)
    print(json.dumps(out, indent=2))