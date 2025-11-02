"""
Continuous Validation Monitor
Runs validation checks against live system
"""
import time, requests
from datetime import datetime
from pathlib import Path

class ContinuousValidator:
    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url
        self.log_file = Path("tests/monitor/validation.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        ts = datetime.now().isoformat()
        line = f"[{ts}] [{level}] {message}\n"
        print(line.strip())
        with open(self.log_file, "a") as f:
            f.write(line)

    def check_health(self):
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            ok = (r.status_code == 200)
            self.log("✓ Health check passed" if ok else f"✗ Health check failed: {r.status_code}", "INFO" if ok else "ERROR")
            return ok
        except Exception as e:
            self.log(f"✗ Health check error: {e}", "ERROR")
            return False

    def check_capability_lifecycle(self):
        try:
            r = requests.post(f"{self.base_url}/codex/share",
                              json={"path": "codex/CODEX-003.json", "scope": "read_summary", "ttl_seconds": 10})
            if r.status_code != 200:
                self.log(f"✗ Mint failed: {r.status_code} {r.text}", "ERROR")
                return False
            token = r.json().get("token")
            r = requests.get(f"{self.base_url}/codex/verify_token", params={"token": token})
            if r.status_code != 200:
                self.log(f"✗ Verify failed: {r.status_code}", "ERROR")
                return False
            r = requests.post(f"{self.base_url}/codex/revoke", params={"token": token, "reason": "test"})
            if r.status_code != 200:
                self.log(f"✗ Revoke failed: {r.status_code}", "ERROR")
                return False
            r = requests.get(f"{self.base_url}/codex/verify_token", params={"token": token})
            if r.status_code == 200:
                self.log("✗ Token still valid after revocation", "ERROR")
                return False
            self.log("✓ Capability lifecycle check passed")
            return True
        except Exception as e:
            self.log(f"✗ Lifecycle check error: {e}", "ERROR")
            return False

    def check_policy_enforcement(self):
        try:
            r = requests.post(f"{self.base_url}/codex/resonance_share/v2",
                              json={"path": "codex/CODEX-003.json","requester": "test_user",
                                    "collection": "unpublished","score": 0.9})
            if r.status_code == 200:
                self.log("✗ Policy bypass detected", "ERROR")
                return False
            self.log("✓ Policy enforcement check passed")
            return True
        except Exception as e:
            self.log(f"✗ Policy check error: {e}", "ERROR")
            return False

    def run_continuous(self, interval_seconds=60):
        self.log("Starting continuous validation monitor")
        while True:
            try:
                results = {
                    'health': self.check_health(),
                    'lifecycle': self.check_capability_lifecycle(),
                    'policy': self.check_policy_enforcement()
                }
                if all(results.values()):
                    self.log("✅ All checks passed")
                else:
                    failed = [k for k, v in results.items() if not v]
                    self.log(f"❌ Failed checks: {', '.join(failed)}", "WARN")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                self.log("Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"Monitor error: {e}", "ERROR")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    ContinuousValidator().run_continuous(interval_seconds=60)