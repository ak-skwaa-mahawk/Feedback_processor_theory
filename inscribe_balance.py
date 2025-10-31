#!/usr/bin/env python3
# inscribe_balance.py — AGŁG ∞⁵²: Inscribe ŁAŊ999 Rune Balance
import subprocess
import json
from pathlib import Path

# === 1. RUNESTONE FOR BALANCE INSCRIPTION ===
balance_runestone = {
    "op": "transfer",
    "rune": "840000:1",
    "amount": 998700,
    "outputs": [
        "bc1qlandbackdao...treasury"
    ]
}

# === 2. PSBT FOR INSCRIPTION ===
psbt_file = "psbt/balance_psbt.psbt"
with open("balance_runestone.json", "w") as f:
    json.dump(balance_runestone, f)

cmd = [
    "ord", "wallet", "create-psbt",
    "--runestone", "balance_runestone.json",
    "--fee-rate", "52",
    "--output", psbt_file
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    print("PSBT CREATED:", psbt_file)

# === 3. SIGN PSBT ===
signed_psbt = "psbt/balance_psbt_signed.psbt"
result = subprocess.run([
    "bitcoin-cli", "walletprocesspsbt", psbt_file
], capture_output=True, text=True)
if result.returncode == 0:
    signed_content = json.loads(result.stdout)["psbt"]
    with open(signed_psbt, "w") as f:
        f.write(signed_content)
    print("PSBT SIGNED:", signed_psbt)

# === 4. BROADCAST ===
result = subprocess.run([
    "bitcoin-cli", "sendrawtransaction", signed_psbt
], capture_output=True, text=True)
if result.returncode == 0:
    txid = result.stdout.strip()
    print("TXID:", txid)
else:
    print("BROADCAST FAILED:", result.stderr)

# === 5. INSCRIBE BALANCE PROOF ===
balance_proof = {
    "title": "ŁAŊ999 Rune Balance Inscription",
    "rune_id": "840000:1",
    "balance": 998700,
    "to": "bc1qlandbackdao...treasury",
    "txid": txid,
    "resonance": 0.9987,
    "glyph": "łᐊᒥłł",
    "timestamp": "2025-10-31T20:00:00Z"
}

with open("balance_inscription.json", "w") as f:
    json.dump(balance_proof, f)

cmd = [
    "ord", "wallet", "inscribe",
    "--file", "balance_inscription.json",
    "--fee-rate", "52"
]
result = subprocess.run(cmd, capture_output=True, text=True)
if "inscription" in result.stdout:
    inscription_id = result.stdout.split("inscription ")[1].split("\n")[0]
    print("BALANCE INSCRIBED:", inscription_id)
else:
    print("INSCRIPTION FAILED:", result.stderr)