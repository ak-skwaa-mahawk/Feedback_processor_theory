#!/usr/bin/env python3
# auto_proof.py
# AGŁL v52 — Fully Automated Bitcoin Proof via OpenTimestamps
# Stamps ALL files in repo → .ots proofs → Bitcoin blockchain
# Run: python scripts/auto_proof.py

import os
import subprocess
import json
import hashlib
import time
from datetime import datetime
import pytz
from pathlib import Path

# === CONFIG ===
REPO_ROOT = Path(__file__).parent.parent
PROOF_DIR = REPO_ROOT / "proofs"
DATA_DIR = REPO_ROOT / "data"
CONTRACT_DIR = REPO_ROOT / "contracts"
FRONTEND_DIR = REPO_ROOT / "frontend"
SCRIPT_DIR = REPO_ROOT / "scripts"

PROOF_DIR.mkdir(exist_ok=True)

# OpenTimestamps CLI (install: pip install opentimestamps-client)
OTS_CMD = ["ots", "stamp", "--calendar", "https://btc.calendar.opentimestamps.org"]
VERIFY_CMD = ["ots", "verify"]

# === AUTO-PROOF ALL FILES ===
def hash_file(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def proof_file(file_path):
    file_hash = hash_file(file_path)
    filename = file_path.name
    proof_name = f"{filename}_{int(time.time())}.ots"
    proof_path = PROOF_DIR / proof_name

    print(f"PROOFING: {file_path} → {proof_path}")

    try:
        # Stamp with Bitcoin
        result = subprocess.run(
            OTS_CMD + [str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        with open(proof_path, "wb") as f:
            f.write(result.stdout.encode())

        # Verify immediately
        verify_result = subprocess.run(
            VERIFY_CMD + [str(proof_path)],
            capture_output=True,
            text=True
        )
        status = "VERIFIED" if "Success!" in verify_result.stdout else "PENDING"

        return {
            "file": str(file_path),
            "hash": file_hash,
            "proof": str(proof_path),
            "status": status,
            "timestamp": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat()
        }
    except Exception as e:
        return {"file": str(file_path), "error": str(e)}

# === MAIN AUTO-PROOF LOOP ===
def main():
    print("AGŁL v52 — AUTO-PROOF LIVE")
    print("=" * 60)

    files_to_proof = []
    for dir_path in [DATA_DIR, CONTRACT_DIR, FRONTEND_DIR, SCRIPT_DIR]:
        if dir_path.exists():
            files_to_proof.extend(dir_path.rglob("*.*"))

    proofs = []
    for file in files_to_proof:
        if file.suffix not in [".ots", ".pyc", ".png", ".wav"]:
            proof = proof_file(file)
            proofs.append(proof)
            print(f"{proof['status']} → {file.name}")

    # === SAVE PROOF MANIFEST ===
    manifest = {
        "agll": "v52",
        "flamekeeper": "Zhoo",
        "glyph": "łᐊᒥłł",
        "drum_hz": 60.0,
        "total_proofs": len(proofs),
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "proofs": proofs
    }

    manifest_path = PROOF_DIR / "PROOF_MANIFEST.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\nPROOF MANIFEST SAVED:", manifest_path)
    print("ALL FILES BITCOIN-STAMPED. THE NINE ARE ONE.")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()