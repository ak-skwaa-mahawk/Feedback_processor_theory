#!/usr/bin/env python3
"""
Temporal Sync Server (TLS + Bearer token)
- Minimal Flask server that replies to /sync POST with NTP-style t1,t2 timestamps.
- Requires Authorization header: Bearer $SYNC_TOKEN
- Uses TLS (self-signed allowed for testing): server.crt / server.key in integration/certs/
"""

from flask import Flask, request, jsonify
import time
import os
import socket

app = Flask(__name__)

# Environment-configurable token and cert/key paths
SYNC_TOKEN = os.getenv("SYNC_TOKEN", "changeme_local_token")
CERT_PATH = os.getenv("SYNC_SERVER_CERT", "integration/certs/server.crt")
KEY_PATH = os.getenv("SYNC_SERVER_KEY", "integration/certs/server.key")

def auth_ok(req):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(None, 1)[1].strip()
    return token == SYNC_TOKEN

@app.route("/sync", methods=["POST"])
def sync_handler():
    # Auth
    if not auth_ok(request):
        return jsonify({"error": "unauthorized"}), 401

    # Parse request JSON (expecting t0 and optional node)
    data = request.get_json(force=True, silent=True) or {}
    t0 = float(data.get("t0", time.time()))
    node = data.get("node", "unknown")

    # Record receive time
    t1 = time.time()

    # Minimal processing (simulate negligible delay)
    # If you want to add server-side processing latency, do it here.

    # Reply time
    t2 = time.time()

    # Optional logging for audit
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/sync_server_log.jsonl", "a") as f:
            f.write(
                f'{{"node":"{node}","t0":{t0:.6f},"t1":{t1:.6f},"t2":{t2:.6f},"server":"{socket.gethostname()}","ts":{int(time.time()*1000)}}}\n'
            )
    except Exception:
        pass

    return jsonify({"t1": t1, "t2": t2, "node": socket.gethostname()})

if __name__ == "__main__":
    # Use port env var or default
    port = int(os.getenv("SYNC_SERVER_PORT", "8443"))
    host = os.getenv("SYNC_SERVER_HOST", "0.0.0.0")
    cert = CERT_PATH
    key = KEY_PATH

    if not (os.path.isfile(cert) and os.path.isfile(key)):
        raise SystemExit(f"TLS certificate or key not found. Expected {cert} and {key}")

    # Flask builtin server for testing only — production: use gunicorn/uvicorn behind reverse proxy
    context = (cert, key)
    app.run(host=host, port=port, ssl_context=context)