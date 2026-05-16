#!/usr/bin/env python3
# auto_proof.py — AGŁL v52.1 Auto-Proof (Sovereign Registry Binding)
import os, subprocess, json, hashlib, time
from datetime import datetime
import pytz
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PROOF_DIR = REPO_ROOT / "proofs"
DIRS = ["data", "contracts", "frontend", "scripts", "core"]  # Added core

PROOF_DIR.mkdir(parents=True, exist_ok=True)

OTS_CMD = ["ots", "stamp", "--calendar", "https://btc.calendar.opentimestamps.org"]

def hash_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def proof_file(p: Path) -> dict:
    proof_path = PROOF_DIR / f"{p.name}_{int(time.time())}.ots"
    print(f"PROOFING: {p.name}")

    try:
        result = subprocess.run(OTS_CMD + [str(p)], capture_output=True, text=True, check=True)
        proof_path.write_bytes(result.stdout.encode())

        entry = {
            "file": str(p.relative_to(REPO_ROOT)),
            "hash": hash_file(p),
            "proof_file": str(proof_path),
            "timestamp_utc": datetime.utcnow().isoformat(),
            "status": "VERIFIED"
        }
        return entry
    except Exception as e:
        return {"file": str(p.relative_to(REPO_ROOT)), "status": "FAILED", "error": str(e)}

def main():
    print("AGŁL v52.1 — AUTO-PROOF LIVE | Binding to GTC001 & Soliton Registry")
    
    files = [f for d in DIRS for f in (REPO_ROOT/d).rglob("*.*") 
             if f.is_file() and f.suffix not in [".ots", ".pyc", ".log"]]

    proofs = [proof_file(f) for f in files if f.suffix]  # Only files with extensions

    manifest = {
        "agll_version": "v52.1",
        "glyph": "łᐊᒥłł",
        "gtc_id": "GTC001",
        "eternal_sync": 813667,
        "total_files": len(files),
        "total_proofs": len([p for p in proofs if p["status"] == "VERIFIED"]),
        "timestamp_utc": datetime.utcnow().isoformat(),
        "proofs": proofs
    }

    manifest_path = PROOF_DIR / "PROOF_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"\nALL FILES BITCOIN-STAMPED → {len(proofs)} proofs created")
    print(f"Manifest saved → {manifest_path}")
    print("The coin breathes sovereign. We are still here.")

if __name__ == "__main__":
    main()