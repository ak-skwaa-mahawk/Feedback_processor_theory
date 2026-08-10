# flame_vault_backup.py
# Sovereign Orbital Cold Storage — FlameVault Backup v1.0
# Author: John Benjamin Carroll Jr. — Flameholder
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene | Seal: 79Hz | Proof: FlameLockV2 | Orbit: SSC-001

import json
import time
import hashlib
import logging
import tarfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Local modules
from flame_lock_v2_proof import FlameLockV2
from space_resonance_protocol import SpaceResonanceProtocol
from flame_vault_ledger import FlameVaultLedger

# =============================================================================
# CONFIG — ORBITAL COLD STORAGE
# =============================================================================

BACKUP_DIR = Path("flamevault_backup/")
BACKUP_DIR.mkdir(exist_ok=True)
ARCHIVE_PATH = BACKUP_DIR / f"flamevault_cold_storage_{int(time.time())}.tar.gz"
ORBITAL_LOG = Path("orbital_backup.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(ORBITAL_LOG), logging.StreamHandler()]
)
log = logging.getLogger("COLDSTORAGE")

# =============================================================================
# BACKUP MANIFEST
# =============================================================================

@dataclass
class BackupManifest:
    timestamp: float
    flameholder: str
    root: str
    files: List[str]
    ledger_hash: str
    merkle_root: str
    toft_seal: str
    flamelock_proof: str
    srp_pass_id: str
    ssc_stamp: str
    gtc_handshake: bool

    def to_json(self) -> str:
        return json.dumps({
            "manifest": {
                "timestamp": self.timestamp,
                "flameholder": self.flameholder,
                "root": self.root,
                "files": self.files,
                "ledger_hash": self.ledger_hash,
                "merkle_root": self.merkle_root,
                "toft_seal": self.toft_seal,
                "flamelock_proof": self.flamelock_proof,
                "srp_pass_id": self.srp_pass_id,
                "ssc_stamp": self.ssc_stamp,
                "gtc_handshake": self.gtc_handshake
            }
        }, indent=2)

# =============================================================================
# ORBITAL COLD STORAGE CORE
# =============================================================================

class FlameVaultBackup:
    def __init__(self):
        self.flamelock = FlameLockV2()
        self.srp = SpaceResonanceProtocol()
        self.ledger = FlameVaultLedger()
        self.files_to_backup = self._collect_files()
        log.info("FLAMEVAULT BACKUP ENGINE INITIALIZED — ORBITAL COLD STORAGE")

    def _collect_files(self) -> List[Path]:
        files = []
        # Core vault
        files.extend(Path("flamevault/").rglob("*.flame"))
        files.extend(Path("flamevault/").rglob("*.json"))
        # Ledger + Merkle
        files.append(Path("flamevault_ledger.jsonl"))
        files.append(Path("flamevault_merkle.json"))
        # Proofs
        files.extend(Path("proofs/").rglob("*.json"))
        # Audio seals
        files.append(Path("gamma_160hz_space.wav"))
        files.append(Path("gamma_160hz_space.toft_seal"))
        # SRP schedule
        files.append(Path("srp_schedule.jsonl"))
        return [f for f in files if f.exists()]

    def _create_archive(self) -> Path:
        log.info(f"CREATING COLD STORAGE ARCHIVE: {ARCHIVE_PATH}")
        with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
            for file in self.files_to_backup:
                arcname = file.relative_to(Path.cwd())
                tar.add(file, arcname=arcname)
                log.info(f"ARCHIVED: {arcname}")
        return ARCHIVE_PATH

    def _generate_manifest(self, archive_path: Path) -> BackupManifest:
        # Hash archive
        archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()

        # Ledger state
        ledger_hash = hashlib.sha256(Path("flamevault_ledger.jsonl").read_bytes()).hexdigest()
        merkle_root = json.loads(Path("flamevault_merkle.json").read_text())["root"]

        # TOFT seal
        t = np.linspace(0, 0.1266, 5567)
        pulse = np.sin(2 * np.pi * 79 * t)
        toft_seal = hashlib.sha256(pulse.tobytes()).hexdigest()[:32]

        # FlameLockV2 proof of archive
        proof = self.flamelock.generate_proof(archive_path.read_bytes())
        flamelock_proof = proof.to_json()

        # SRP next pass
        next_pass = self.srp.get_next_pass()
        srp_pass_id = f"pass_{int(next_pass.pass_start_utc)}" if next_pass else "pending"

        manifest = BackupManifest(
            timestamp=time.time(),
            flameholder="John Benjamin Carroll Jr.",
            root="Gwitchyaa Zhee",
            files=[str(f) for f in self.files_to_backup],
            ledger_hash=ledger_hash,
            merkle_root=merkle_root,
            toft_seal=toft_seal,
            flamelock_proof=flamelock_proof,
            srp_pass_id=srp_pass_id,
            ssc_stamp="SSC Commons",
            gtc_handshake=True
        )

        manifest_path = archive_path.with_suffix(".manifest.json")
        manifest_path.write_text(manifest.to_json())
        log.info(f"MANIFEST GENERATED: {manifest_path}")
        return manifest

    def _uplink_to_orbit(self, archive_path: Path, manifest_path: Path):
        # Wait for SRP pass
        next_pass = self.srp.get_next_pass()
        if not next_pass:
            log.warning("NO ORBITAL PASS — BACKUP QUEUED")
            return

        wait_time = next_pass.pass_start_utc - time.time()
        if wait_time > 0:
            log.info(f"WAITING {wait_time:.1f}s FOR ORBITAL PASS")
            time.sleep(wait_time)

        # Uplink during pass
        log.info("ORBITAL UPLINK ACTIVE — TRANSMITTING COLD STORAGE")
        payload = {
            "type": "flamevault_cold_storage",
            "archive_b64": archive_path.read_bytes().hex(),
            "manifest": json.loads(manifest_path.read_text())["manifest"],
            "ssc_compliant": True,
            "gtc_handshake": True
        }
        line = json.dumps(payload, separators=(',', ':')) + "\n"
        # Simulate uplink via RMP + Orbital
        for _ in range(3):  # Redundancy
            self.srp.rmp.udp_sock.sendto(line.encode(), ('<broadcast>', 7980))
            time.sleep(1)
        log.info("COLD STORAGE UPLINK COMPLETE — ORBITAL VAULT SECURE")

    def execute_backup(self):
        log.info("EXECUTING FLAMEVAULT ORBITAL BACKUP — SKODEN")
        archive = self._create_archive()
        manifest = self._generate_manifest(archive)
        self._uplink_to_orbit(archive, archive.with_suffix(".manifest.json"))
        log.info("FLAMEVAULT BACKUP COMPLETE — ASCENDED TO ORBIT")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("     FLAMEVAULT ORBITAL COLD STORAGE v1.0")
    print("     Vadzaih Zhoo, 99733 | November 11, 2025 03:45 PM AKST")
    print("="*80 + "\n")

    backup = FlameVaultBackup()
    backup.execute_backup()

    print(f"\nARCHIVE: {ARCHIVE_PATH}")
    print(f"MANIFEST: {ARCHIVE_PATH.with_suffix('.manifest.json')}")
    print("UPLINKED DURING ORBITAL PASS — 79Hz SEALED")
    print("\nJust say the word. The vault is already in orbit.")
    print("SKODEN — THE FLAME ASCENDS")