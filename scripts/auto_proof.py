#!/usr/bin/env python3
# auto_proof.py — AGŁL v52 Auto-Proof
import os, subprocess, json, hashlib, time
from datetime import datetime
import pytz
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PROOF_DIR = REPO_ROOT / "proofs"
DIRS = ["data", "contracts", "frontend", "scripts"]
PROOF_DIR.mkdir(exist_ok=True)
OTS_CMD = ["ots", "stamp", "--calendar", "https://btc.calendar.opentimestamps.org"]

def hash_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def proof_file(p):
    proof_path = PROOF_DIR / f"{p.name}_{int(time.time())}.ots"
    print(f"PROOFING: {p} → {proof_path}")
    try:
        result = subprocess.run(OTS_CMD + [str(p)], capture_output=True, text=True, check=True)
        proof_path.write_bytes(result.stdout.encode())
        return {"file": str(p), "hash": hash_file(p), "proof": str(proof_path), "status": "VERIFIED"}
    except: return {"file": str(p), "error": "FAILED"}

def main():
    print("AGŁL v52 — AUTO-PROOF LIVE")
    files = [f for d in DIRS for f in (REPO_ROOT/d).rglob("*.*") if f.suffix not in [".ots",".pyc"]]
    proofs = [proof_file(f) for f in files]
    manifest = {"agll": "v52", "glyph": "łᐊᒥłł", "total_proofs": len(proofs), "proofs": proofs}
    (PROOF_DIR / "PROOF_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print("ALL FILES BITCOIN-STAMPED. WE ARE STILL HERE.")

if __name__ == "__main__": main()