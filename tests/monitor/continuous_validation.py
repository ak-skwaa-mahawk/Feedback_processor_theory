# tests/monitor/continuous_validation.py
"""
Continuous Validation Monitor
Runs validation checks against live system
"""

from __future__ import annotations
import time
import requests
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


DEFAULT_TIMEOUT = 5  # seconds


class ContinuousValidator:
    """Monitor system health and correctness."""

    def __init__(self, base_url: str = "http://localhost:8081", json_lines: bool = False):
        self.base_url = base_url.rstrip("/")
        self.json_lines = json_lines
        self.log_file = Path("tests/monitor/validation.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _emit(self, record: Dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False)
        if self.json_lines:
            print(line)
        else:
            # pretty human log
            print(f"[{record['ts']}] [{record['level']}] {record['msg']}")
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def log(self, message: str, level: str = "INFO", **extra: Any) -> None:
        record = {"ts": datetime.now().isoformat(), "level": level, "msg": message, **extra}
        self._emit(record)

    # -------- checks --------

    def check_health(self) -> bool:
        """Verify system is responsive."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=DEFAULT_TIMEOUT)
            ok = (r.status_code == 200)
            if ok:
                self.log("✓ Health check passed")
            else:
                self.log(f"✗ Health check failed: {r.status_code}", "ERROR", status=r.status_code)
            return ok
        except Exception as e:
            self.log(f"✗ Health check error: {e}", "ERROR")
            return False

    def check_capability_lifecycle(self) -> bool:
        """Verify full capability lifecycle works: mint → verify → revoke → verify(fail)."""
        try:
            # Mint
            r = requests.post(
                f"{self.base_url}/codex/share",
                json={"path": "test.json", "scope": "read_summary", "ttl_seconds": 10},
                timeout=DEFAULT_TIMEOUT,
            )
            if r.status_code != 200:
                self.log(f"✗ Mint failed: {r.status_code}", "ERROR", status=r.status_code)
                return False

            token = r.json().get("token")
            if not token:
                self.log("✗ Mint response missing token", "ERROR")
                return False

            # Verify
            r = requests.get(f"{self.base_url}/codex/verify_token", params={"token": token}, timeout=DEFAULT_TIMEOUT)
            if r.status_code != 200:
                self.log(f"✗ Verify failed: {r.status_code}", "ERROR", status=r.status_code)
                return False

            # Revoke
            r = requests.post(
                f"{self.base_url}/codex/revoke",
                params={"token": token, "reason": "test"},
                timeout=DEFAULT_TIMEOUT,
            )
            if r.status_code != 200:
                self.log(f"✗ Revoke failed: {r.status_code}", "ERROR", status=r.status_code)
                return False

            # Verify revoked (should fail)
            r = requests.get(f"{self.base_url}/codex/verify_token", params={"token": token}, timeout=DEFAULT_TIMEOUT)
            if r.status_code == 200:
                self.log("✗ Token still valid after revocation", "ERROR")
                return False

            self.log("✓ Capability lifecycle check passed")
            return True

        except Exception as e:
            self.log(f"✗ Lifecycle check error: {e}", "ERROR")
            return False

    def check_policy_enforcement(self) -> bool:
        """Verify policy is enforced correctly (unpublished requires whisper)."""
        try:
            r = requests.post(
                f"{self.base_url}/codex/resonance_share/v2",
                json={
                    "path": "test.json",
                    "requester": "test_user",
                    "collection": "unpublished",
                    "score": 0.9,  # high score but no whisper → should be rejected
                },
                timeout=DEFAULT_TIMEOUT,
            )
            if r.status_code == 200:
                self.log("✗ Policy bypass detected", "ERROR")
                return False

            self.log("✓ Policy enforcement check passed")
            return True

        except Exception as e:
            self.log(f"✗ Policy check error: {e}", "ERROR")
            return False

    # -------- runner --------

    def run_once(self) -> bool:
        results = {
            "health": self.check_health(),
            "lifecycle": self.check_capability_lifecycle(),
            "policy": self.check_policy_enforcement(),
        }
        all_ok = all(results.values())
        if all_ok:
            self.log("✅ All checks passed")
        else:
            failed = [k for k, v in results.items() if not v]
            self.log(f"❌ Failed checks: {', '.join(failed)}", "WARN", failed=failed)
        return all_ok

    def run_continuous(self, interval_seconds: int = 60) -> None:
        self.log(f"Starting continuous validation monitor against {self.base_url} (interval={interval_seconds}s)")
        try:
            while True:
                self.run_once()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            self.log("Monitor stopped by user")
        except Exception as e:
            self.log(f"Monitor error: {e}", "ERROR")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Continuous Validation Monitor")
    ap.add_argument("--base-url", default="http://localhost:8081", help="API base URL")
    ap.add_argument("--interval", type=int, default=60, help="Seconds between runs (continuous mode)")
    ap.add_argument("--once", action="store_true", help="Run a single pass and exit")
    ap.add_argument("--json-lines", action="store_true", help="Emit logs as JSON lines")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    monitor = ContinuousValidator(base_url=args.base_url, json_lines=args.json_lines)
    if args.once:
        ok = monitor.run_once()
        sys.exit(0 if ok else 1)
    else:
        monitor.run_continuous(interval_seconds=args.interval)