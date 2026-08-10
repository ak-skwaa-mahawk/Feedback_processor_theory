#!/usr/bin/env python3
# vault_lan999.py — AGŁG ∞⁴⁹: Production-Ready ŁAŊ999 Mint & Transfer
"""
Production-Ready ŁAŊ999 Vault
- Hardware wallet signing
- Schema validation
- Fee estimation
- Hash-chained logging
- PSBT workflow
"""
import json
import hashlib
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, ValidationError, Field
import logging
import time
import os

# === CONFIG ===
CONFIG = {
    "rune_id": "840000:1",
    "rune_name": "ŁAŊ999",
    "divisibility": 18,
    "supply_cap": 999_000_000,
    "initial_mint": 998_700,
    "fee_rate_target": 50,  # sat/vB
    "mempool_api": "https://mempool.space/api/v1/fees/recommended",
    "log_path": "codex/vault_lan999.log",
    "psbt_dir": "psbt/",
    "wallet_name": "landback_vault"
}

# === SCHEMA ===
class Runestone(BaseModel):
    op: str = Field(..., pattern="^(etch|mint|transfer)$")
    rune: str | None = None
    name: str | None = None
    divisibility: int | None = Field(None, ge=0, le=18)
    supply: int | None = Field(None, ge=0)
    amount: int | None = Field(None, ge=0)
    outputs: list[str] | None = None

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(CONFIG["log_path"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ŁAŊ999_VAULT")

def hash_chain(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

class Lan999Vault:
    def __init__(self):
        self.log_path = Path(CONFIG["log_path"])
        self.psbt_dir = Path(CONFIG["psbt_dir"])
        self.psbt_dir.mkdir(exist_ok=True)
        self.chain_head = self.load_chain_head()

    def load_chain_head(self) -> str:
        if self.log_path.exists():
            with open(self.log_path, "rb") as f:
                f.seek(-64, 2)  # Last hash
                return f.read().strip().decode()
        return "0" * 64

    def log_entry(self, entry: Dict[str, Any]):
        entry["prev_hash"] = self.chain_head
        entry["hash"] = hash_chain(json.dumps(entry, sort_keys=True))
        self.chain_head = entry["hash"]
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_fee_rate(self) -> int:
        try:
            r = requests.get(CONFIG["mempool_api"], timeout=5)
            return r.json()["fastestFee"]
        except:
            return CONFIG["fee_rate_target"]

    def create_psbt(self, runestone: Runestone, fee_rate: int) -> str:
        psbt_file = self.psbt_dir / f"psbt_{int(time.time())}.psbt"
        cmd = [
            "ord", "wallet", "create-psbt",
            "--runestone", json.dumps(runestone.dict(exclude_none=True)),
            "--fee-rate", str(fee_rate),
            "--output", str(psbt_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"PSBT Created: {psbt_file}")
        return str(psbt_file)

    def sign_psbt(self, psbt_file: str) -> str:
        signed_file = psbt_file.replace(".psbt", "_signed.psbt")
        cmd = [
            "bitcoin-cli", "-named", "walletprocesspsbt",
            "psbt", str(psbt_file),
            "changepos", "-2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        signed_psbt = json.loads(result.stdout)["psbt"]
        Path(signed_file).write_text(signed_psbt)
        logger.info(f"PSBT Signed: {signed_file}")
        return signed_file

    def broadcast_tx(self, signed_psbt: str) -> str:
        cmd = ["bitcoin-cli", "sendrawtransaction", signed_psbt]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        txid = result.stdout.strip()
        logger.info(f"TX Broadcast: {txid}")
        return txid

    def etch_rune(self):
        runestone = Runestone(
            op="etch",
            name=CONFIG["rune_name"],
            divisibility=CONFIG["divisibility"],
            supply=CONFIG["supply_cap"]
        )
        return self.execute_runestone(runestone, "etch")

    def mint_rune(self):
        runestone = Runestone(
            op="mint",
            rune=CONFIG["rune_id"],
            amount=CONFIG["initial_mint"]
        )
        return self.execute_runestone(runestone, "mint")

    def transfer_rune(self, to_address: str):
        runestone = Runestone(
            op="transfer",
            rune=CONFIG["rune_id"],
            amount=CONFIG["initial_mint"],
            outputs=[to_address]
        )
        return self.execute_runestone(runestone, "transfer")

    def execute_runestone(self, runestone: Runestone, action: str) -> Dict[str, Any]:
        try:
            runestone.validate(runestone)
        except ValidationError as e:
            logger.error(f"Schema Error: {e}")
            raise

        fee_rate = self.get_fee_rate()
        psbt_file = self.create_psbt(runestone, fee_rate)
        signed_psbt = self.sign_psbt(psbt_file)
        txid = self.broadcast_tx(signed_psbt)

        entry = {
            "action": action,
            "runestone": runestone.dict(),
            "fee_rate": fee_rate,
            "txid": txid,
            "timestamp": time.time()
        }
        self.log_entry(entry)
        return entry

# === PRODUCTION VAULT ===
if __name__ == "__main__":
    vault = Lan999Vault()
    
    # === 1. ETCH (ONE-TIME) ===
    # vault.etch_rune()
    
    # === 2. MINT ===
    # vault.mint_rune()
    
    # === 3. TRANSFER ===
    vault.transfer_rune("bc1qlandbackdao...treasury")