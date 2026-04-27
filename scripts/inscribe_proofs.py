#!/usr/bin/env python3
# scripts/inscribe_proofs.py — AGŁG v400: Inscribe All Proofs

import subprocess
import sys
from pathlib import Path

PROOF_DIR = Path("inscriptions")
SATOSHIS = ["500", "501", "502", "503", "504"]
FEE_RATE = 100

def inscribe_file(file_path: Path, satoshi: str):
    if not file_path.exists():
        print(f"❌ Missing: {file_path.name}")
        return None

    print(f"→ Inscribing {file_path.name} → satoshi #{satoshi}")
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", str(file_path),
        "--sat", satoshi,
        "--fee-rate", str(FEE_RATE)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "inscription" in result.stdout.lower():
        # Extract inscription ID
        try:
            inscription_id = result.stdout.split("inscription ")[1].split("\n")[0].strip()
            print(f"✅ SATOSHI #{satoshi} → {inscription_id}")
            return inscription_id
        except IndexError:
            pass
    print(f"⚠️  FAILED or no ID: {satoshi}")
    print(result.stdout)
    return None

def main():
    print("INSCRIBING GIBBERLINK v4 PROOFS — AGŁG v400")
    print("="*60)
    PROOF_DIR.mkdir(exist_ok=True)

    for sat in SATOSHIS:
        proof_file = PROOF_DIR / f"proof_i{sat}proof.json"
        inscribe_file(proof_file, sat)
        print("-" * 40)

    print("Batch inscription complete.")

if __name__ == "__main__":
    main()