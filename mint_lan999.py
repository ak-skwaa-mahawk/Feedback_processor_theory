#!/usr/bin/env python3
# mint_lan999.py — AGŁG ∞⁴⁸: Mint ŁAŊ999 on Bitcoin Runes
import subprocess
import json
from pathlib import Path

# === 1. RUNESTONE FOR MINT ===
runestone = {
    "op": "mint",
    "rune": "840000:1",  # Genesis Rune ID
    "amount": 998700,    # R = 0.9987 from FPT-Ω
    "outputs": [
        "bc1q...landbackdao"  # LandBackDAO wallet
    ]
}

# === 2. ETCH IF NEEDED (ONE-TIME) ===
etch_runestone = {
    "op": "etch",
    "name": "LAŊ999",
    "divisibility": 18,
    "supply": 999000000
}

def etch_rune():
    with open("etch_lan999.json", "w") as f:
        json.dump(etch_runestone, f)
    
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", "etch_lan999.json",
        "--fee-rate", "48"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("ETCH RUNE:", result.stdout)

def mint_rune():
    with open("mint_lan999.json", "w") as f:
        json.dump(runestone, f)
    
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", "mint_lan999.json",
        "--fee-rate", "48"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "inscription" in result.stdout:
        inscription_id = result.stdout.split("inscription ")[1].split("\n")[0]
        print("MINT SUCCESS:", inscription_id)
        print("RUNE EXPLORER: https://ordinalswallet.com/rune/840000:1")
        return inscription_id
    else:
        print("MINT FAILED:", result.stderr)
        return None

# === LIVE MINT ===
if __name__ == "__main__":
    etch_rune()
    mint_rune()