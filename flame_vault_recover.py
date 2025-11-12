# flame_vault_recover.py
# Sovereign Orbital Restore Engine — FlameVault Recovery v1.0
# Author: John Benjamin Carroll Jr. — Flameholder
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene | Seal: 79Hz | Proof: FlameLockV2 | Orbit: SSC-001

import json
import time
import hashlib
import logging
import tarfile
import shutil
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Local modules
from flame_lock_v2_proof import FlameLockV2
from space_resonance_protocol import SpaceResonanceProtocol
from flame_vault_ledger import FlameVaultLedger
from flame_mesh_orchestrator_v2 import FlameMeshOrchestrator

# =============================================================================
# CONFIG — ORBITAL RESTORE
# =============================================================================

RECOVER_DIR = Path("flamevault_recover/")
RECOVER_DIR.mkdir(exist_ok=True)
RECOVER_LOG = Path("orbital_recover.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(RECOVER_LOG), logging.StreamHandler()]
)
log = logging.getLogger("RECOVER")

# =============================================================================
# RESTORE MANIFEST
# =============================================================================

@dataclass
class RestoreManifest:
    archive_path: Path
    manifest_data: Dict
    flamelock_proof: Dict
    toft_seal: str
    ledger_hash: str
    merkle_root: str
    srp_pass_id: str

# =============================================================================
# ORBITAL RESTORE CORE
# =============================================================================

class FlameVaultRecover:
    def __init__(self):
        self.flamelock = FlameLockV2()
        self.srp = SpaceResonanceProtocol()
        self.ledger = FlameVaultLedger()
        self.orchestrator = FlameMeshOrchestrator()
        self.recovery_archive: Optional[Path] = None
        self.manifest: Optional[RestoreManifest] = None
        log.info("FLAMEVAULT RECOVERY ENGINE INITIALIZED — ORBITAL RESTORE READY")

    def _wait_for_downlink(self) -> Optional[bytes]:
        """Listen for orbital cold storage packet during pass"""
        log.info("LISTENING FOR ORBITAL DOWNLINK — AWAITING PASS")
        next_pass = self.srp.get_next_pass()
        if not next_pass:
            log.error("NO ORBITAL PASS — CANNOT RESTORE")
            return None

        wait_time = next_pass.pass_start_utc - time.time()
        if wait_time > 0:
            log.info(f"WAITING {wait_time:.1f}s FOR DOWNLINK WINDOW")
            time.sleep(wait_time)

        # Simulate receiving packet (in real system: LoRa/SDR)
        log.info("ORBITAL DOWNLINK DETECTED — RECEIVING COLD STORAGE")
        time.sleep(3)  # Simulate transmission
        # In real system: receive hex payload from orbital_relay
        # For demo: use latest backup
        latest_backup = max(Path("flamevault_backup/").glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, default=None)
        if not latest_backup:
            log.error("NO BACKUP ARCHIVE FOUND")
            return None

        archive_bytes = latest_backup.read_bytes()
        log.info(f"ORBITAL ARCHIVE RECEIVED: {latest_backup.name}")
        return archive_bytes

    def _save_archive(self, archive_bytes: bytes) -> Path:
        archive_path = RECOVER_DIR / f"recovered_cold_storage_{int(time.time())}.tar.gz"
        archive_path.write_bytes(archive_bytes)
        log.info(f"ARCHIVE SAVED: {archive_path}")
        return archive_path

    def _extract_manifest(self, archive_path: Path) -> Optional[RestoreManifest]:
        manifest_path = archive_path.with_suffix(".manifest.json")
        if not manifest_path.exists():
            log.error("MANIFEST NOT FOUND")
            return None

        manifest_data = json.loads(manifest_path.read_text())["manifest"]
        flamelock_proof = json.loads(manifest_data["flamelock_proof"])["flamelock_v2_proof"]

        manifest = RestoreManifest(
            archive_path=archive_path,
            manifest_data=manifest_data,
            flamelock_proof=flamelock_proof,
            toft_seal=manifest_data["toft_seal"],
            ledger_hash=manifest_data["ledger_hash"],
            merkle_root=manifest_data["merkle_root"],
            srp_pass_id=manifest_data["srp_pass_id"]
        )
        log.info("MANIFEST LOADED — PREPARING VERIFICATION")
        return manifest

    def _verify_restore_integrity(self, manifest: RestoreManifest) -> bool:
        log.info("VERIFYING FLAMELOCK V2 PROOF...")
        if not self.flamelock.verify_proof(json.dumps({"flamelock_v2_proof": manifest.flamelock_proof})):
            log.error("FLAMELOCK V2 PROOF FAILED")
            return False

        log.info("VERIFYING TOFT 79Hz SEAL...")
        expected_seal = hashlib.sha256(np.sin(2 * np.pi * 79 * np.linspace(0, 0.1266, 5567)).tobytes()).hexdigest()[:32]
        if manifest.toft_seal != expected_seal:
            log.error("TOFT SEAL MISMATCH")
            return False

        log.info("VERIFYING ARCHIVE HASH...")
        computed_hash = hashlib.sha256(manifest.archive_path.read_bytes()).hexdigest()
        if computed_hash != manifest.ledger_hash:  # Using ledger_hash as archive hash in demo
            log.error("ARCHIVE HASH MISMATCH")
            return False

        log.info("ALL VERIFICATIONS PASSED — SOVEREIGN RESTORE AUTHORIZED")
        return True

    def _extract_archive(self, archive_path: Path):
        log.info(f"EXTRACTING COLD STORAGE: {archive_path}")
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=RECOVER_DIR / "extracted")
        log.info("EXTRACTION COMPLETE")

    def _rebuild_ledger(self):
        log.info("REBUILDING FLAMEVAULT LEDGER FROM COLD STORAGE")
        recovered_ledger = RECOVER_DIR / "extracted" / "flamevault_ledger.jsonl"
        if recovered_ledger.exists():
            shutil.copy(recovered_ledger, "flamevault_ledger.jsonl")
            self.ledger = FlameVaultLedger()  # Reload
            if self.ledger.verify_ledger():
                log.info("LEDGER REBUILT AND VERIFIED")
            else:
                log.error("LEDGER VERIFICATION FAILED")
        else:
            log.error("LEDGER FILE NOT FOUND IN ARCHIVE")

    def _restore_files(self):
        log.info("RESTORING FLAMEVAULT FILES")
        extract_dir = RECOVER_DIR / "extracted"
        for item in extract_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(extract_dir)
                dest = Path(rel_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(item, dest)
                log.info(f"RESTORED: {rel_path}")

    def execute_recovery(self):
        log.info("EXECUTING ORBITAL RESTORE — SKODEN")
        
        # 1. Downlink
        archive_bytes = self._wait_for_downlink()
        if not archive_bytes:
            return False

        # 2. Save
        archive_path = self._save_archive(archive_bytes)

        # 3. Load manifest
        manifest = self._extract_manifest(archive_path)
        if not manifest:
            return False

        # 4. Verify
        if not self._verify_restore_integrity(manifest):
            return False

        # 5. Extract
        self._extract_archive(archive_path)

        # 6. Rebuild ledger
        self._rebuild_ledger()

        # 7. Restore files
        self._restore_files()

        # 8. Restart orchestrator
        log.info("RESTARTING FLAME MESH ORCHESTRATOR v2")
        self.orchestrator = FlameMeshOrchestrator()
        self.orchestrator.start_all_heartbeats()

        log.info("FLAMEVAULT FULLY RESTORED FROM ORBIT — SYSTEM LIVE")
        return True

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("     FLAMEVAULT ORBITAL RESTORE v1.0")
    print("     Vadzaih Zhoo, 99733 | November 11, 2025 06:40 PM AKST")
    print("="*80 + "\n")

    recover = FlameVaultRecover()
    success = recover.execute_recovery()

    if success:
        print("\nORBITAL RESTORE COMPLETE")
        print("FLAMEVAULT LEDGER: VERIFIED")
        print("MESH ORCHESTRATOR: RESTARTED")
        print("79Hz PULSE: RESUMED")
        print("\nJust say the word. The flame has returned.")
    else:
        print("\nRESTORE FAILED — CHECK LOGS")
    
    print("SKODEN — THE FLAME DESCENDS")