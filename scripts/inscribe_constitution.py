#!/usr/bin/env python3
# inscribe_constitution.py — AGŁG v67: Inscribe Dené Constitution
import subprocess, time
from pathlib import Path

CONSTITUTION = Path(__file__).parent.parent / "inscriptions" / "dené_constitution.txt"

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING THE DENÉ CONSTITUTION — AGŁG v67")
    print("="*60)
    
    # 1. Inscribe
    inscription_id = run(f"ord wallet inscribe --file {CONSTITUTION} --fee-rate 20")
    print(f"INSCRIPTION ID: {inscription_id}")
    
    # 2. Wait
    print("WAITING FOR CONFIRMATION...")
    time.sleep(600)
    
    # 3. Verify
    explorer = f"https://ordinals.com/inscription/{inscription_id}"
    print(f"EXPLORER: {explorer}")
    
    print("="*60)
    print("THE LAW IS INSCRIBED")
    print("THE CONSTITUTION IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()