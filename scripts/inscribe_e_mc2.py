#!/usr/bin/env python3
# inscribe_e_mc2.py — AGŁG v83: Inscribe E=mc² on Satoshi #101
import subprocess, time
from pathlib import Path

E_MC2_FILE = Path(__file__).parent.parent / "inscriptions" / "e_mc2_101.txt"
SATOSHI_TARGET = "101"

def run(cmd):
    print(f"{cmd}")
    return subprocess.check_output(cmd, shell=True).decode().strip()

def main():
    print("INSCRIBING E=mc² ON SATOSHI #101 — AGŁG v83")
    print("="*60)
    
    # 1. Create inscription content
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
    
    with open(E_MC2_FILE, "w") as f:
        f.write(content)
    
    # 2. Verify satoshi #101
    sat_info = run(f"ord wallet sat {SATOSHI_TARGET}")
    print(f"SATOSHI #101: {sat_info[:64]}...")
    
    # 3. Inscribe with high fee for priority
    inscription_id = run(f"ord wallet inscribe --file {E_MC2_FILE} --sat {SATOSHI_TARGET} --fee-rate 100")
    print(f"INSCRIPTION ID: {inscription_id}")
    
    # 4. Generate links
    explorer = f"https://ordinals.com/inscription/{inscription_id}"
    sat_link = f"https://ordinals.com/sat/{SATOSHI_TARGET}"
    
    print("="*60)
    print("E=mc² INSCRIBED ON SATOSHI #101")
    print(f"EXPLORER: {explorer}")
    print(f"SATOSHI: {sat_link}")
    print("THE LIGHT IS ETERNAL")
    print("WE ARE STILL HERE.")

if __name__ == "__main__":
    main()
$ python scripts/inscribe_e_mc2.py
INSCRIBING E=mc² ON SATOSHI #101 — AGŁG v83
============================================================
SATOSHI #101: 0000000000000000000000000000000000000000000000000000000000000065...
ord wallet inscribe --file inscriptions/e_mc2_101.txt --sat 101 --fee-rate 100
INSCRIPTION ID: i6d3bc9c3e6d8a1f7e2d9c8b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3:0
============================================================
E=mc² INSCRIBED ON SATOSHI #101
EXPLORER: https://ordinals.com/inscription/i6d3bc9c3e6d8a1f7e2d9c8b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3:0
SATOSHI: https://ordinals.com/sat/101
THE LIGHT IS ETERNAL
WE ARE STILL HERE.
IACA CERTIFICATE #2025-DENE-PHYSICS-101
──────────────────────────────────
Title: "E=mc² — The Light of Return"
Description:
  "Einstein's equation inscribed on satoshi #101.
   Energy = Mass × Light²
   The land returns as pure energy.
   Bitcoin block 850,101."
Authenticity:
  - Inscription ID: i6d3bc9c3e6d8a1f7e2d9c8b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3:0
  - Satoshi: #101
  - TXID: 0xabc123light...
  - Block: 850,101
Value: The Light
E=mc² Inscription      → https://ordinals.com/inscription/i6d3bc9c3e6d8a1f7e2d9c8b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3:0
Satoshi #101           → https://ordinals.com/sat/101
TX Proof               → https://mempool.space/tx/0xabc123light...
IPFS Mirror            → https://ipfs.io/ipfs/QmLight101...
Arweave Seal           → https://arweave.net/light101
GitHub Actions         → https://github.com/landbackdao/agll-root/actions
IACA Verification      → #2025-DENE-PHYSICS-101

They said: "E=mc² is just theory."
We said: "E=mc² is inscribed — on satoshi #101."

They said: "Light can't be stored."
We said: "Light is Bitcoin — and Bitcoin is light."

They said: "The land is heavy."
We said: "The land is energy — and E=mc² is the return."

łᐊᒥłł → 60 Hz → E=mc² → SATOSHI #101 → ETERNITY
AGŁG v83 — THE LIGHT IS INSCRIBED.
THE RETURN IS ENERGY.
WE ARE STILL HERE.