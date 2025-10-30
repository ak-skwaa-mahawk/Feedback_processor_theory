#!/usr/bin/env python3
# inscribe_f_ma.py — AGŁG v82: Inscribe F = ma on Satoshi #100
import subprocess, time
from pathlib import Path

F_MA_FILE = Path(__file__).parent.parent / "inscriptions" / "f_ma_100.txt"
SATOSHI_TARGET = "100"

def run(cmd):
    print(f"🔥 {cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING F = ma ON SATOSHI #100 — AGŁG v82")
    print("="*60)
    
    # 1. Prepare file
    with open(F_MA_FILE, "w") as f:
        f.write("""F = ma
─────────────────────
Force = Mass × Acceleration

The land accelerates.
The ancestors apply force.
The mass returns.

Two Mile Solutions LLC
IACA #2025-DENE-PHYSICS-100
AGŁG v82 — The Law of the Land

WE ARE STILL HERE.""")
    
    # 2. Find satoshi #100
    sat = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #100 FOUND: {sat[:32]}...")
    
    # 3. Inscribe
    inscription_id = run(f"ord wallet inscribe --file {F_MA_FILE} --sat {SATOSHI_TARGET} --fee-rate 50")
    print(f"INSCRIPTION ID: {inscription