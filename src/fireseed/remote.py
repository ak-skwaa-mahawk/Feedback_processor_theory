# src/fireseed/remote.py
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any

REMOTE_URL = os.getenv("FIRESEED_WEBHOOK_URL", "")
REMOTE_TOKEN = os.getenv("FIRESEED_AUTH_TOKEN", "")


def post_record(record: Dict[str, Any]) -> None:
    """
    Minimal default remote sender.
    Safe_post() will wrap this, so errors here won't crash the engine.
    """
    if not REMOTE_URL:
        return  # no-op if not configured

    body = json.dumps(record).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if REMOTE_TOKEN:
        headers["Authorization"] = f"Bearer {REMOTE_TOKEN}"

    req = urllib.request.Request(REMOTE_URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=5.0) as resp:
        # read to ensure connection closes cleanly
        _ = resp.read()