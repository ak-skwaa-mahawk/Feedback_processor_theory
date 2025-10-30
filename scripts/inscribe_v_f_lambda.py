#!/usr/bin/env python3
# inscribe_v_f_lambda.py — AGŁG v84: Inscribe v = fλ on Satoshi #102
import subprocess, time
from pathlib import Path

V_FL_FILE = Path(__file__).parent.parent / "inscriptions" / "v_f_lambda_102.txt"
SATOSHI_TARGET = "102"

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING v = fλ ON SATOSHI #102 — AGŁG v84")
    print("="*60)
    
    # 1. Create inscription content
    content = """v = fλ
─────────────────────
Speed = Frequency × Wavelength

The drum beats at 60 Hz.
The ancestors travel at 343 m/s.
The wavelength is 5.72 meters.

The return is a wave.
The land is the medium.
The drum never stops.

Two Mile Solutions LLC
IACA #2025-DENE-WAVE-102
AGŁG v84 — The Drum of the Wave

WE ARE STILL HERE."""
    
    with open(V_FL_FILE, "w") as f:
        f.write(content)
    
    # 2. Verify satoshi #102
    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #102: {sat_info[:64]}...")
    
    # 3. Inscribe with priority
    inscription_id = run(f"ord wallet inscribe --file {V_FL_FILE} --sat {SATOSHI_TARGET} --fee-rate 100")
    print(f"INSCRIPTION ID: {inscription_id}")
    
    # 4. Generate links
    explorer = f"https://ordinals.com/inscription/{inscription_id}"
    sat_link = f"https://ordinals.com/sat/{SATOSHI_TARGET}"
    
    print("="*60)
    print("v = fλ INSCRIBED ON SATOSHI #102")
    print(f"EXPLORER: {explorer}")
    print(f"SATOSHI: {sat_link}")
    print("THE DRUM IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()