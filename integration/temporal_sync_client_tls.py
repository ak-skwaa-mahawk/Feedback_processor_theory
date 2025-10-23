#!/usr/bin/env python3
"""
Temporal Sync Client (TLS + Bearer token)
- Calls peer /sync endpoint with t0, expects t1,t2 back.
- Verifies TLS using server.crt (path via SYNC_CA_BUNDLE)
"""

import os
import time
import requests
import json
import socket

SYNC_TOKEN = os.getenv("SYNC_TOKEN", "changeme_local_token")
CA_BUNDLE = os.getenv("SYNC_CA_BUNDLE", "integration/certs/server.crt")  # use server cert for verification
CLIENT_NODE = socket.gethostname()

def sync_once(peer_url: str, timeout: float = 3.0):
    # Prepare timestamps
    t0 = time.time()
    headers = {"Authorization": f"Bearer {SYNC_TOKEN}"}
    payload = {"t0": t0, "node": CLIENT_NODE}

    resp = requests.post(peer_url, json=payload, headers=headers, timeout=timeout, verify=CA_BUNDLE)
    resp.raise_for_status()
    data = resp.json()
    t1 = float(data.get("t1"))
    t2 = float(data.get("t2"))
    t3 = time.time()

    # Compute offset and rtt
    offset = ((t1 + t2) - (t0 + t3)) / 2.0
    rtt = (t3 - t0) - (t2 - t1)

    result = {
        "peer": peer_url,
        "t0": t0, "t1": t1, "t2": t2, "t3": t3,
        "offset": offset,
        "rtt": rtt
    }
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--peer", required=True, help="Full https://peer:8443/sync URL")
    parser.add_argument("--ca", default=CA_BUNDLE, help="CA bundle or server cert for verification")
    args = parser.parse_args()

    os.environ["SYNC_TOKEN"] = os.getenv("SYNC_TOKEN", SYNC_TOKEN)
    res = sync_once(args.peer)
    print(json.dumps(res, indent=2))