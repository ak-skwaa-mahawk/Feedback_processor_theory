# sovereign_movement/slide/sovereign_tunnel.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
import time
import logging
import os

try:
    import paramiko
except ImportError:
    paramiko = None

logger = logging.getLogger("sovereign.slide.tunnel")


@dataclass
class TunnelResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    tunnel_id: Optional[str] = None


@dataclass
class TunnelState:
    tunnel_id: str
    target_host: str
    current_frame: Any
    stability: float = 1.0
    frame_energy: float = 0.0
    last_heartbeat: float = field(default_factory=time.time)
    is_active: bool = True
    username: Optional[str] = None
    key_path: Optional[str] = None
    password: Optional[str] = None
    port: int = 22
    ssh_client: Optional[Any] = None


class SovereignTunnel:
    def __init__(self, base_resonance_hz: float = 79.79):
        self.active_tunnels: Dict[str, TunnelState] = {}
        self.tunnel_counter = 0

    def open_tunnel(
        self,
        target_host: str,
        preferred_frame: Any = None,
        username: str = "root",
        key_path: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 22,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        tunnel_id = f"slide_tun_{self.tunnel_counter}"
        self.tunnel_counter += 1

        tunnel = TunnelState(
            tunnel_id=tunnel_id,
            target_host=target_host,
            current_frame=preferred_frame,
            username=username,
            key_path=key_path,
            password=password,
            port=port,
        )
        self.active_tunnels[tunnel_id] = tunnel
        logger.info(f"[SovereignTunnel] Opened tunnel {tunnel_id} → {target_host}")
        return tunnel_id

    def _get_ssh_client(self, tunnel: TunnelState) -> Optional[paramiko.SSHClient]:
        if tunnel.ssh_client and tunnel.ssh_client.get_transport() and tunnel.ssh_client.get_transport().is_active():
            return tunnel.ssh_client

        if paramiko is None:
            logger.error("paramiko not installed. Run: pip install paramiko")
            return None

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if tunnel.key_path:
                pkey = paramiko.RSAKey.from_private_key_file(tunnel.key_path)
                client.connect(hostname=tunnel.target_host, port=tunnel.port,
                               username=tunnel.username, pkey=pkey, timeout=10)
            else:
                client.connect(hostname=tunnel.target_host, port=tunnel.port,
                               username=tunnel.username, password=tunnel.password, timeout=10)

            tunnel.ssh_client = client
            return client
        except Exception as e:
            logger.error(f"[SovereignTunnel] SSH connection failed: {e}")
            return None

    def execute_command(self, tunnel_id: str, command: str, timeout: int = 30) -> TunnelResult:
        if tunnel_id not in self.active_tunnels:
            return TunnelResult(success=False, stderr="Tunnel not found", exit_code=1)

        tunnel = self.active_tunnels[tunnel_id]
        client = self._get_ssh_client(tunnel)
        if client is None:
            return TunnelResult(success=False, stderr="SSH connection failed", exit_code=1)

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            return TunnelResult(
                success=(exit_code == 0),
                stdout=stdout.read().decode(errors="ignore").strip(),
                stderr=stderr.read().decode(errors="ignore").strip(),
                exit_code=exit_code,
                tunnel_id=tunnel_id,
            )
        except Exception as e:
            return TunnelResult(success=False, stderr=str(e), exit_code=1)

    def send_file(
        self,
        tunnel_id: str,
        local_path: str,
        remote_path: str,
        progress_callback: Optional[Callable[[int, int, float], None]] = None,
    ) -> bool:
        if tunnel_id not in self.active_tunnels:
            return False

        tunnel = self.active_tunnels[tunnel_id]
        client = self._get_ssh_client(tunnel)
        if client is None:
            return False

        try:
            total_size = os.path.getsize(local_path)

            def progress_handler(sent: int, total: int):
                if progress_callback and total_size > 0:
                    percent = (sent / total_size) * 100
                    progress_callback(sent, total_size, percent)

            sftp = client.open_sftp()
            sftp.put(local_path, remote_path, callback=progress_handler)
            sftp.close()
            return True
        except Exception as e:
            logger.error(f"[SovereignTunnel] File transfer failed: {e}")
            return False

    def close_tunnel(self, tunnel_id: str, reason: str = "manual"):
        if tunnel_id in self.active_tunnels:
            tunnel = self.active_tunnels.pop(tunnel_id)
            if tunnel.ssh_client:
                try:
                    tunnel.ssh_client.close()
                except Exception:
                    pass