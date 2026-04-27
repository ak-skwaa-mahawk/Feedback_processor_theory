#!/usr/bin/env python3
# inscribe_f_ma.py — AGŁG v82: Inscribe F = ma on Satoshi #100

import subprocess
import sys
from pathlib import Path

F_MA_FILE = Path("inscriptions/f_ma_100.txt")
SATOSHI_TARGET = "100"
FEE_RATE = 150   # slightly higher for reliable confirmation

def run(cmd):
    print(f"🔥 {cmd}")
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

def main():
    print("INSCRIBING F = ma ON SATOSHI #100 — AGŁG v82")
    print("="*70)

    content = """F = ma
─────────────────────
Force = Mass × Acceleration

The land accelerates.
The ancestors apply force.
The mass returns.

Two Mile Solutions LLC
John B. Carroll Jr.
IACA #2025-DENE-PHYSICS-100
AGŁG v82 — The Law of the Land

WE ARE STILL HERE."""

    F_MA_FILE.parent.mkdir(exist_ok=True)
    F_MA_FILE.write_text(content)

    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #100 STATUS: {sat_info[:80]}...")

    result = run(f"ord wallet inscribe --file {F_MA_FILE} --sat {SATOSHI_TARGET} --fee-rate {FEE_RATE}")
    print(f"INSCRIPTION SUBMITTED: {result}")

    print("="*70)
    print("F = ma INSCRIBED ON SATOSHI #100")
    print("THE FORCE OF RETURN IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()