#!/usr/bin/env python3
# inscribe_codex.py — AGŁG v105: The Dené Codex on Satoshi #110

import subprocess
import sys
from pathlib import Path

CODEX_FILE = Path("inscriptions/codex_110.txt")
SATOSHI_TARGET = "110"
FEE_RATE = 1000

def run(cmd):
    print(f"→ {cmd}")
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

def main():
    print("INSCRIBING THE ENTIRE CODEX ON SATOSHI #110 — AGŁG v105")
    print("="*70)

    content = """THE DENÉ CODEX
AGŁG v105 — The Complete Truth

1. F = ma — The force of return
2. E = mc² — The energy of ancestors
3. v = fλ — The wave of the drum
4. λ = h/p — The duality of land
5. Δx·Δp ≥ ℏ/2 — The mystery of ownership
6. Schrödinger’s Cat — The land is both stolen and returned
7. Entanglement — The families are one
8. Tunneling — The ancestors pass through any fence
9. GlyphVehicle — Every vote is explained
10. FPT-Ω — The truth self-corrects

Two Mile Solutions LLC
John B. Carroll Jr.
IACA #2025-DENE-CODEX-110
AGŁG v105 — The Eternal Codex

WE ARE STILL HERE."""

    CODEX_FILE.parent.mkdir(exist_ok=True)
    CODEX_FILE.write_text(content)

    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #110 STATUS: {sat_info[:80]}...")

    result = run(f"ord wallet inscribe --file {CODEX_FILE} --sat {SATOSHI_TARGET} --fee-rate {FEE_RATE}")
    print(f"INSCRIPTION SUBMITTED: {result}")

    print("="*70)
    print("THE ENTIRE CODEX IS INSCRIBED ON SATOSHI #110")
    print("THE TRUTH IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()