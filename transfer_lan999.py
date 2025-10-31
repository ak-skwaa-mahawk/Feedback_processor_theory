#!/usr/bin/env python3
# transfer_lan999.py — AGŁG ∞⁴⁸: Transfer ŁAŊ999 on Bitcoin Runes
import subprocess
import json
from pathlib import Path

# === 1. RUNESTONE FOR TRANSFER ===
runestone = {
    "op": "transfer",
    "rune": "840000:1",  # Genesis Rune ID
    "amount": 998700,    # Full initial resonance
    "outputs": [
        "bc1q...landbackdao_v2_treasury"  # LandBackDAO wallet
    ]
}

# === 2. MINT IF NEEDED (FROM PRIOR) ===
# Assume etched; if not, run etch first

def transfer_rune():
    with open("transfer_lan999.json", "w") as f:
        json.dump(runestone, f)
    
    cmd = [
        "ord", "wallet", "inscribe",
        "--file", "transfer_lan999.json",
        "--fee-rate", "49"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "inscription" in result.stdout:
        inscription_id = result.stdout.split("inscription ")[1].split("\n")[0]
        print("TRANSFER SUCCESS:", inscription_id)
        print("RUNE EXPLORER: https://ordinalswallet.com/rune/840000:1")
        return inscription_id
    else:
        print("TRANSFER FAILED:", result.stderr)
        return None

# === LIVE TRANSFER ===
if __name__ == "__main__":
    transfer_rune()