#!/usr/bin/env python3
# inscribe_e_mc2.py — AGŁG v83: E=mc² on Satoshi #101

import subprocess
import sys
from pathlib import Path

E_MC2_FILE = Path("inscriptions/e_mc2_101.txt")
SATOSHI_TARGET = "101"
FEE_RATE = 100

def run(cmd):
    print(f"→ {cmd}")
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

def main():
    print("INSCRIBING E=mc² ON SATOSHI #101 — AGŁG v83")
    print("="*70)

    # Content
    content = """E = mc²
─────────────────────
Energy = Mass × Speed of Light²

The land is mass.
The ancestors are light.
The return is energy.

Two Mile Solutions LLC
IACA #2025-DENE-PHYSICS-101
AGŁG v83 — The Light of Return

WE ARE STILL HERE."""

    E_MC2_FILE.parent.mkdir(exist_ok=True)
    E_MC2_FILE.write_text(content)

    # Check sat
    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #101 STATUS: {sat_info[:80]}...")

    # Inscribe
    result = run(f"ord wallet inscribe --file {E_MC2_FILE} --sat {SATOSHI_TARGET} --fee-rate {FEE_RATE}")
    print(f"INSCRIPTION SUBMITTED: {result}")

    print("="*70)
    print("E=mc² INSCRIBED ON SATOSHI #101")
    print("THE LIGHT IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()
