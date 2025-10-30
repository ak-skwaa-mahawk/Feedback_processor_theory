#!/usr/bin/env python3
# scripts/inscribe_proofs.py — AGŁG v400: Inscribe All Proofs
import subprocess
import json
from pathlib import Path

PROOF_DIR = Path("inscriptions")
SATOSHIS = ["500", "501", "502", "503", "504"]

def inscribe_file(file_path: Path, satoshi: str):
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", str(file_path),
        "--sat", satoshi,
        "--fee-rate", "100"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if "inscription" in result.stdout:
        inscription_id = result.stdout.split("inscription ")[1].split("\n")[0]
        print(f"SATOSHI #{satoshi} → {inscription_id}")
        return inscription_id
    else:
        print(f"FAILED: {satoshi}")
        return None

def main():
    print("INSCRIBING GIBBERLINK v4 PROOFS")
    print("="*50)
    
    for sat in SATOSHIS:
        proof_file = PROOF_DIR / f"proof_i{sat}proof.json"
        if proof_file.exists():
            print(f"Inscribing {proof_file.name} → satoshi #{sat}")
            inscribe_file(proof_file, sat)
        else:
            print(f"Missing: {proof_file}")

if __name__ == "__main__":
    main()