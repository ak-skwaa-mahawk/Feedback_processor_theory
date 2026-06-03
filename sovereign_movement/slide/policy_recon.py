# sovereign_movement/slide/policy_recon.py

from __future__ import annotations
from typing import List, Optional
import subprocess
import logging
import ipaddress

logger = logging.getLogger("sovereign.slide.policy_recon")


class PolicyAwareRecon:
    """Discovers targets the current host is already allowed to reach."""

    def __init__(self, max_targets: int = 15):
        self.max_targets = max_targets

    def discover(self) -> List[str]:
        targets: set[str] = set()
        targets.update(self._get_existing_outbound_connections())
        targets.update(self._get_recent_ssh_targets())
        return list(targets)[: self.max_targets]

    def _get_existing_outbound_connections(self) -> set[str]:
        targets: set[str] = set()
        try:
            with open("/proc/net/tcp", "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        remote = parts[2]
                        if remote != "00000000:0000":
                            ip = self._hex_to_ip(remote.split(":")[0])
                            if ip and not ip.startswith(("127.", "169.254.")):
                                targets.add(ip)
        except Exception:
            pass
        return targets

    def _get_recent_ssh_targets(self) -> set[str]:
        targets: set[str] = set()
        try:
            result = subprocess.run(
                ["last", "-n", "30", "-i"],
                capture_output=True, text=True, timeout=6
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) > 2 and self._is_valid_ip(parts[2]):
                    targets.add(parts[2])
        except Exception:
            pass
        return targets

    def _hex_to_ip(self, hex_ip: str) -> Optional[str]:
        try:
            ip_int = int(hex_ip, 16)
            return ".".join(str((ip_int >> (i * 8)) & 0xFF) for i in range(4))
        except Exception:
            return None

    def _is_valid_ip(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False