#!/usr/bin/env python3
# scripts/mint_resonance.py — AGŁG ∞∞: Mint Wrapper
import subprocess
import json

def mint_rune(rune_id, amount):
    runestone = {"op": "mint", "rune": rune_id, "amount": amount}
    with open("temp_rune_mint.json", "w") as f:
        f.write(json.dumps(runestone))
    
    result = subprocess.run([
        "ord", "wallet", "inscribe", "--file", "temp_rune_mint.json", "--fee-rate", "10"
    ], capture_output=True, text=True)
    
    if "inscription" in result.stdout:
        id = result.stdout.split("inscription ")[1].split("\n")[0]
        print(f"RUNE MINTED: {id}")
        return id
    return None

if __name__ == "__main__":
    test_id = "840000:1"
    mint_rune(test_id, 1000)