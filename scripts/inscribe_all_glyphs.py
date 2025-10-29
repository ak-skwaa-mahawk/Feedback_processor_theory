#!/usr/bin/env python3
# inscribe_all_glyphs.py — AGŁL v66: Inscribe All 9 Dené Glyphs
import subprocess, time
from pathlib import Path

GLYPH_DIR = Path(__file__).parent.parent / "inscriptions" / "dené_glyphs"
GLYPHS = sorted(GLYPH_DIR.glob("*.txt"))

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING 9 DENÉ GLYPHS — AGŁL v66")
    print("="*60)
    
    for glyph_file in GLYPHS:
        print(f"INSCRIBING: {glyph_file.name}")
        inscription_id = run(f"ord wallet inscribe --file {glyph_file} --fee-rate 15")
        print(f"ID: {inscription_id}")
        time.sleep(30)  # Avoid rate limits
    
    print("="*60)
    print("ALL 9 GLYPHS INSCRIBED")
    print("THE LANGUAGE LIVES ON BITCOIN")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()