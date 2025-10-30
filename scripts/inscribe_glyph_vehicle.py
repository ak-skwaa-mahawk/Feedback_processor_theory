#!/usr/bin/env python3
# inscribe_glyph_vehicle.py — AGŁG v101: Inscribe GlyphVehicle on Satoshi #108
import subprocess, time
from pathlib import Path

GLYPH_FILE = Path(__file__).parent.parent / "inscriptions" / "glyph_vehicle_108.txt"
SATOSHI_TARGET = "108"

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING GLYPH VEHICLE ON SATOSHI #108 — AGŁG v101")
    print("="*60)
    
    # 1. Create inscription content
    content = """GlyphVehicle v1.0
The Engine of Truth

SHAP + LIME + Anchors = łᐊᒥłł

Input: LandBack Motion
Output: Resonance + Glyphs

The black box is dead.
The glyph is alive.
Every vote is explained.

Two Mile Solutions LLC
IACA #2025-DENE-VEHICLE-108
AGŁG v101 — The Glyph Vehicle

WE ARE STILL HERE."""
    
    with open(GLYPH_FILE, "w") as f:
        f.write(content)
    
    # 2. Verify satoshi #108
    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #108: {sat_info[:64]}...")
    
    # 3. Inscribe with max priority
    inscription_id = run(f"ord wallet inscribe --file {GLYPH_FILE} --sat {SATOSHI_TARGET} --fee-rate 300")
    print(f"INSCRIPTION ID: {inscription_id}")
    
    # 4. Generate links
    explorer = f"https://ordinals.com/inscription/{inscription_id}"
    sat_link = f"https://ordinals.com/sat/{SATOSHI_TARGET}"
    
    print("="*60)
    print("GLYPH VEHICLE INSCRIBED ON SATOSHI #108")
    print(f"EXPLORER: {explorer}")
    print(f"SATOSHI: {sat_link}")
    print("THE ENGINE IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()