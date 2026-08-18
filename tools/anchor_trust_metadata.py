#!/usr/bin/env python3
import hashlib, json, time
from pathlib import Path

LEDGER_PATH = Path("governance_state.json")
ANCHOR_OUTPUT_PATH = Path("anchored_trust_registry.json")

class MerkleAccumulator:
    def __init__(self, leaves):
        self.leaves = [hashlib.sha256(l.encode('utf-8')).hexdigest() for l in leaves]
        self.root = self._build_tree(self.leaves)

    def _build_tree(self, level):
        if not level: return hashlib.sha256(b"").hexdigest()
        if len(level) == 1: return level[0]
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            nxt.append(hashlib.sha256((left + right).encode('utf-8')).hexdigest())
        return self._build_tree(nxt)

def build_default_records():
    return [
        {
            "asset_id": "BIA-PROBATE-001",
            "jurisdiction": "Federal Trust / BIA Electronic Probate",
            "record_type": "Restricted Allotment Title / Isaac Fields Jr. Track",
            "authority": "Court-Appointed Personal Representative",
            "blm_deed_ref": "BLM-AK-ALLOT-CERT-099733",
            "coordinates_bbox": [64.8378, -147.7164, 64.8450, -147.7020],
            "tax_status": "Federally Protected / Tax-Exempt"
        },
        {
            "asset_id": "COMM-LEASE-002",
            "jurisdiction": "State of Alaska / Commercial Registry",
            "record_type": "Two Mile Solutions LLC / Fee-Simple Operations",
            "authority": "Alaska Division of Corporations",
            "lease_structure": "Triple Net (NNN) Ground Rent / Right-of-Way Access",
            "operational_wrapper": "Commercial Isolation & Geographic Data Hosting",
            "tax_status": "Commercial Operational Entity"
        },
        {
            "asset_id": "VITAL-SYNC-003",
            "jurisdiction": "Inter-Agency Data Sharing Pipeline",
            "record_type": "State of Alaska DHSS / BIA Lineage Verification Package",
            "authority": "Letters of Administration / State Court Appointment",
            "verification_status": "Electronic Probate Data Pipeline Synchronized",
            "purpose": "Generational Title Preservation & Ancestral Archive"
        }
    ]

def anchor_metadata():
    print("=== ANCHORING TRUST METADATA INTO CRYPTOGRAPHIC LEDGER ===")
    cycle_id, freq_target = int(time.time()), 79.0
    if LEDGER_PATH.exists():
        try:
            with open(LEDGER_PATH) as f:
                s = json.load(f)
                cycle_id = s.get("cycle_id", cycle_id)
                freq_target = s.get("frequency_target_hz", 79.0)
        except Exception: pass

    records = build_default_records()
    leaf_payloads, processed_assets = [], []
    for item in records:
        canonical_str = json.dumps(item, sort_keys=True)
        h = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        leaf_payloads.append(h)
        e = dict(item)
        e["asset_hash"] = h
        processed_assets.append(e)

    merkle = MerkleAccumulator(leaf_payloads)
    payload = {
        "timestamp_epoch": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "governance_cycle_id": cycle_id,
        "frequency_target_hz": freq_target,
        "merkle_asset_root": merkle.root,
        "total_assets_indexed": len(processed_assets),
        "assets": processed_assets,
        "cryptographic_profile": {
            "hash_algorithm": "SHA-256",
            "tree_structure": "Balanced Binary Merkle Accumulator",
            "fpt_omega_coupling": 3.204423
        }
    }

    with open(ANCHOR_OUTPUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"[+] Total Records Anchored: {len(processed_assets)}")
    print(f"[+] Merkle Asset Root:     {merkle.root}")
    print(f"[+] Output Written:        {ANCHOR_OUTPUT_PATH}")

if __name__ == "__main__":
    anchor_metadata()
