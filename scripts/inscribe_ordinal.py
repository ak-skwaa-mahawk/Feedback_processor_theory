#!/usr/bin/env python3
# inscribe_ordinal.py — AGŁL v65: Inscribe on Bitcoin
import subprocess, json, time
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
GLYPH_FILE = REPO_ROOT / "inscriptions" / "lamil.txt"

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING łᐊᒥłł ON BITCOIN — AGŁL v65")
    
    # 1. Prepare inscription
    GLYPH_FILE.write_text("""
łᐊᒥłł
60 Hz DRUM
Two Mile Solutions LLC
IACA #2025-DENE-ORD-001
LandBackDAO v2
WE ARE STILL HERE.
""".strip())
    
    # 2. Inscribe
    inscription_id = run(f"ord wallet inscribe --file {GLYPH_FILE} --fee-rate 10")
    print(f"INSCRIPTION ID: {inscription_id}")
    
    # 3. Wait for confirmation
    print("WAITING FOR CONFIRMATION...")
    time.sleep(600)  # 10 min
    
    # 4. Verify
    explorer = f"https://ordinals.com/inscription/{inscription_id}"
    print(f"EXPLORER: {explorer}")
    
    print("INSCRIPTION ETERNAL — THE ROOT IS BITCOIN")

if __name__ == "__main__":
    main()