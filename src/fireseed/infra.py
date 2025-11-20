# src/fireseed/infra.py
"""
Infrastructure mode + safe outbound calls for Fireseed / Synara.

Modes:
- online   : normal behavior, try remote calls
- degraded : remote calls failing; queue locally and avoid spamming
- offline  : deliberate isolation; log only to local storage
"""

from __future__ import annotations

import os
import json
import time
import threading
from pathlib import Path
from typing import Callable, Dict, Any, Optional
import urllib.request
import urllib.error

# ---------------------------------------------------------------------
# Mode management
# ---------------------------------------------------------------------

_INFRA_MODE_LOCK = threading.Lock()
_INFRA_MODE = os.getenv("INFRA_MODE", "online").lower().strip() or "online"

VALID_MODES = {"online", "degraded", "offline"}


def get_mode() -> str:
    with _INFRA_MODE_LOCK:
        return _INFRA_MODE


def set_mode(mode: str) -> None:
    mode = (mode or "").lower().strip()
    if mode not in VALID_MODES:
        return
    global _INFRA_MODE
    with _INFRA_MODE_LOCK:
        _INFRA_MODE = mode


def set_mode_degraded() -> None:
    if get_mode() != "offline":
        set_mode("degraded")


# ---------------------------------------------------------------------
# Local queue for deferred outbound records
# ---------------------------------------------------------------------

_DEFAULT_QUEUE_PATH = os.getenv("FIRESEED_OUTBOUND_QUEUE", "fireseed_outbound_queue.jsonl")
_QUEUE_LOCK = threading.Lock()


def queue_locally(record: Dict[str, Any]) -> None:
    """
    Append a record to a local JSONL queue for later replay.
    Never raises.
    """
    try:
        path = Path(_DEFAULT_QUEUE_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        with _QUEUE_LOCK, path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), **record}) + "\n")
    except Exception:
        # Intentionally swallow; local queue failure must not kill the engine
        pass


# ---------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------

def _probe(url: str, timeout: float = 2.0) -> bool:
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            return 200 <= code < 400
    except Exception:
        return False


def infra_health() -> Dict[str, bool]:
    """
    Basic infra health snapshot.

    Configure these URLs via env; if unset, results may all be False.
    """
    self_url = os.getenv("FIRESEED_HEALTH_SELF_URL", "")
    vendor_url = os.getenv("FIRESEED_HEALTH_VENDOR_URL", "")

    return {
        "self": _probe(self_url),
        "vendor": _probe(vendor_url),
    }


def auto_adjust_mode_from_health() -> str:
    """
    Inspect current health snapshot and adjust INFRA_MODE if needed.
    Returns the resulting mode.
    """
    health = infra_health()
    self_ok = health.get("self", False)
    vendor_ok = health.get("vendor", False)

    if not self_ok and not vendor_ok:
        set_mode("offline")
    elif self_ok and not vendor_ok:
        set_mode_degraded()
    elif self_ok and vendor_ok and get_mode() != "offline":
        set_mode("online")

    return get_mode()


# ---------------------------------------------------------------------
# Safe outbound wrapper
# ---------------------------------------------------------------------

def safe_post(
    record: Dict[str, Any],
    post_func: Callable[[Dict[str, Any]], None],
    on_error: Optional[Callable[[Exception], None]] = None,
) -> None:
    """
    Wrap outbound call with infra mode awareness and local queuing.

    - If mode == offline  : do NOT attempt remote, just queue locally.
    - If mode == degraded : try once; on failure, queue + stay degraded.
    - If mode == online   : try; on failure, queue + switch to degraded.
    """
    mode = get_mode()

    # Always ensure we at least capture the record locally
    # (but do it AFTER the main ledger has written its own copy).
    if mode == "offline":
        queue_locally(record)
        return

    try:
        post_func(record)
    except Exception as e:  # noqa: BLE001 (broad on purpose here)
        queue_locally(record)
        set_mode_degraded()
        if on_error:
            try:
                on_error(e)
            except Exception:
                pass