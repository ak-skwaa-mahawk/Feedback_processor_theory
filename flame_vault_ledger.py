# flame_vault_ledger.py
# Sovereign Immutable Ledger — FlameVault Ledger v1.0
# Author: John Benjamin Carroll Jr. — Flameholder
# Root: Vadzaih Zhoo, 99733
# Fuel: Spruce Plastolene | Seal: 79Hz | Proof: FlameLockV2 | Orbit: SSC

import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

# Local modules
from rmp_core import sign_receipt, verify_receipt
from flame_lock_v2_proof import FlameLockV2
from orbital_relay import OrbitalRelay

# =============================================================================
# CONFIG — FLAMEVAULT LEDGER
# =============================================================================

LEDGER_PATH = Path("flamevault_ledger.jsonl")
LEDGER_PATH.touch(exist_ok=True)
MERKLE_PATH = Path("flamevault_merkle.json")
MERKLE_PATH.touch(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler("flamevault_ledger.log"), logging.StreamHandler()]
)
log = logging.getLogger("LEDGER")

# =============================================================================
# LEDGER ENTRY
# =============================================================================

@dataclass
class LedgerEntry:
    index: int
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    prev_hash: str
    merkle_root: str
    rmp_receipt: str
    toft_seal: str
    ssc_stamp: str
    gtc_handshake: bool
    flameholder: str = "John Benjamin Carroll Jr."

    def to_jsonl(self) -> str:
        entry = {
            "index": self.index,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "rmp_receipt": self.rmp_receipt,
            "toft_seal": self.toft_seal,
            "ssc_stamp": self.ssc_stamp,
            "gtc_handshake": self.gtc_handshake,
            "flameholder": self.flameholder
        }
        return json.dumps(entry, separators=(',', ':')) + "\n"

# =============================================================================
# MERKLE TREE
# =============================================================================

class MerkleTree:
    def __init__(self, leaves: List[str]):
        self.leaves = [hashlib.sha256(l.encode()).hexdigest() for l in leaves]
        self.root = self._build_tree()

    def _build_tree(self) -> str:
        if not self.leaves:
            return hashlib.sha256(b"genesis").hexdigest()
        nodes = self.leaves[:]
        while len(nodes) > 1:
            new_level = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                new_level.append(hashlib.sha256((left + right).encode()).hexdigest())
            nodes = new_level
        return nodes[0]

# =============================================================================
# FLAMEVAULT LEDGER CORE
# =============================================================================

class FlameVaultLedger:
    def __init__(self):
        self.entries: List[LedgerEntry] = []
        self.merkle_leaves: List[str] = []
        self.flamelock = FlameLockV2()
        self.orbital = OrbitalRelay()
        self._load_ledger()
        log.info("FLAMEVAULT LEDGER INITIALIZED — IMMUTABLE")

    def _load_ledger(self):
        if not LEDGER_PATH.exists():
            self._write_genesis()
            return
        with LEDGER_PATH.open() as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.entries.append(LedgerEntry(**entry))
                    self.merkle_leaves.append(json.dumps(entry["data"], sort_keys=True))

    def _write_genesis(self):
        genesis = {
            "event_type": "GENESIS",
            "data": {
                "flameholder": "John Benjamin Carroll Jr.",
                "root": "Gwitchyaa Zhee",
                "ssc_compliant": True,
                "gtc_active": True,
                "message": "The flame is lit. The ledger begins."
            }
        }
        self._append_entry(genesis)

    def _get_prev_hash(self) -> str:
        return "0" * 64 if not self.entries else self.entries[-1].merkle_root

    def _generate_toft_seal(self) -> str:
        t = np.linspace(0, 0.1266, 5567)
        pulse = np.sin(2 * np.pi * 79 * t)
        return hashlib.sha256(pulse.tobytes()).hexdigest()[:32]

    def _append_entry(self, event: Dict[str, Any]):
        index = len(self.entries)
        prev_hash = self._get_prev_hash()
        toft_seal = self._generate_toft_seal()

        # RMP receipt
        receipt_data = {
            "index": index,
            "event_type": event["event_type"],
            "timestamp": time.time()
        }
        rmp_receipt = sign_receipt(receipt_data)

        # Merkle root
        self.merkle_leaves.append(json.dumps(event["data"], sort_keys=True))
        merkle = MerkleTree(self.merkle_leaves)
        merkle_root = merkle.root

        # Create entry
        entry = LedgerEntry(
            index=index,
            timestamp=time.time(),
            event_type=event["event_type"],
            data=event["data"],
            prev_hash=prev_hash,
            merkle_root=merkle_root,
            rmp_receipt=rmp_receipt,
            toft_seal=toft_seal,
            ssc_stamp="SSC Commons",
            gtc_handshake=True
        )

        # Append to ledger
        line = entry.to_jsonl()
        LEDGER_PATH.open("a").write(line)
        self.entries.append(entry)

        # Save merkle
        MERKLE_PATH.write_text(json.dumps({"root": merkle_root, "leaves": self.merkle_leaves[-10:]}, indent=2))

        # Broadcast
        self._broadcast_entry(entry)

        log.info(f"LEDGER ENTRY {index} — {event['event_type']} — SEALED")

    def _broadcast_entry(self, entry: LedgerEntry):
        payload = {
            "type": "ledger_entry",
            "entry": json.loads(entry.to_jsonl()),
            "ssc_compliant": True,
            "gtc_handshake": True
        }
        line = json.dumps(payload, separators=(',', ':')) + "\n"
        # RMP Mesh
        self.orbital.rmp.udp_sock.sendto(line.encode(), ('<broadcast>', 7979))
        # Orbital Uplink
        self.orbital.udp_sock.sendto(line.encode(), ('<broadcast>', 7980))
        log.info(f"LEDGER ENTRY BROADCAST — INDEX {entry.index}")

    def log_event(self, event_type: str, data: Dict[str, Any]):
        event = {"event_type": event_type, "data": data}
        self._append_entry(event)

    def verify_ledger(self) -> bool:
        prev_hash = "0" * 64
        leaves = []
        with LEDGER_PATH.open() as f:
            for i, line in enumerate(f):
                if not line.strip(): continue
                entry = json.loads(line)
                if entry["prev_hash"] != prev_hash:
                    log.error(f"LEDGER CORRUPTED AT INDEX {i}")
                    return False
                leaves.append(json.dumps(entry["data"], sort_keys=True))
                if not verify_receipt(entry, entry["rmp_receipt"]):
                    log.error(f"INVALID RMP RECEIPT AT INDEX {i}")
                    return False
                prev_hash = entry["merkle_root"]
        merkle = MerkleTree(leaves)
        if merkle.root != prev_hash:
            log.error("MERKLE ROOT MISMATCH")
            return False
        log.info("FLAMEVAULT LEDGER VERIFIED — IMMUTABLE")
        return True

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("     FLAMEVAULT LEDGER v1.0 — IMMUTABLE SOVEREIGN CHAIN")
    print("     Vadzaih Zhoo, 99733 | November 11, 2025 01:15 PM AKST")
    print("="*70 + "\n")

    ledger = FlameVaultLedger()

    # Example events
    ledger.log_event("FLAMEHOLDER_NAMED", {
        "node_id": "vadzaih_flame_001",
        "name": "Vadzaih Flame",
        "autopathy": 3
    })
    ledger.log_event("GAMMA_ORBITAL_ACTIVE", {
        "frequency": 160.0,
        "beat": 40.0,
        "toft_seal": ledger._generate_toft_seal()
    })
    ledger.log_event("FLAMELOCK_V2_PROOF", {
        "proof_id": "flamelock_v2_1731349800",
        "status": "BROADCAST"
    })

    # Verify
    ledger.verify_ledger()

    print(f"LEDGER: {LEDGER_PATH}")
    print(f"MERKLE: {MERKLE_PATH}")
    print("\nJust say the word. The ledger is already written.")
    print("SKODEN — THE FLAME REMEMBERS")