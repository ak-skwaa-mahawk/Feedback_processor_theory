#!/usr/bin/env python3
# assign_glyphs.py — AGŁG v69: Assign 9 Glyphs to DAO Members
import subprocess, time
from pathlib import Path

ASSIGNMENTS = [
    ("01_łᐊᒥłł_stillhere.json", "bc1q...ahtna"),
    ("02_ᒥᐊᐧᐊ_land.json", "bc1q...gwichin"),
    # ... all 9
]

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("ASSIGNING 9 GLYPHS TO DAO MEMBERS — AGŁG v69")
    print("="*60)
    
    for token_file, address in ASSIGNMENTS:
        path = f"inscriptions/glyph_tokens/{token_file}"
        print(f"TRANSFERRING {token_file} → {address[:8]}...")
        txid = run(f"ord wallet send {address} {path}")
        print(f"TXID: {txid}")
        time.sleep(30)
    
    print("="*60)
    print("ALL 9 GLYPHS ASSIGNED")
    print("THE REPUBLIC IS ALIVE")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()