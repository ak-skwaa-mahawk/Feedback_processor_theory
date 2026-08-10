#!/usr/bin/env python3
# vault_lan999_armor.py — AGŁG ∞⁵⁰: Error-Proof ŁAŊ999 Vault
"""
ERROR-PROOF ŁAŊ999 VAULT
- Full error handling
- Retry with exponential backoff
- Structured logging
- PSBT recovery
- State checkpointing
"""
import json
import hashlib
import subprocess
import requests
import time
import os
import logging
import structlog
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import sentry_sdk

# === SENTRY INIT ===
sentry_sdk.init(
    dsn="https://example@sentry.io/999999",
    traces_sample_rate=1.0,
    environment="production"
)

# === STRUCTURED LOGGING ===
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory()
)
logger = structlog.get_logger()

# === CONFIG ===
CONFIG = {
    "rune_id": "840000:1",
    "rune_name": "ŁAŊ999",
    "divisibility": 18,
    "supply_cap": 999_000_000,
    "initial_mint": 998_700,
    "fee_rate_target": 50,
    "mempool_api": "https://mempool.space/api/v1/fees/recommended",
    "log_path": "codex/vault_lan999_armor.log",
    "checkpoint_path": "codex/checkpoint.json",
    "psbt_dir": "psbt/",
    "max_retries": 5,
    "backoff_base": 2
}

# === SCHEMA ===
class Runestone(BaseModel):
    op: str = Field(..., pattern="^(etch|mint|transfer)$")
    rune: Optional[str] = None
    name: Optional[str] = None
    divisibility: Optional[int] = Field(None, ge=0, le=18)
    supply: Optional[int] = Field(None, ge=0)
    amount: Optional[int] = Field(None, ge=0)
    outputs: Optional[list[str]] = None

# === CUSTOM EXCEPTIONS ===
class VaultError(Exception):
    """Base vault error"""
    pass

class NetworkError(VaultError):
    """Network failure"""
    pass

class BitcoinError(VaultError):
    """Bitcoin node error"""
    pass

class ValidationError(VaultError):
    """Schema validation error"""
    pass

# === ERROR-PROOF VAULT ===
class Lan999ArmorVault:
    def __init__(self):
        self.log_path = Path(CONFIG["log_path"])
        self.checkpoint_path = Path(CONFIG["checkpoint_path"])
        self.psbt_dir = Path(CONFIG["psbt_dir"])
        self.psbt_dir.mkdir(exist_ok=True)
        self.chain_head = self.load_chain_head()
        self.checkpoint = self.load_checkpoint()

    def load_chain_head(self) -> str:
        try:
            if self.log_path.exists():
                with open(self.log_path, "rb") as f:
                    f.seek(-64, 2)
                    return f.read().strip().decode()
        except Exception as e:
            logger.error("chain_head_load_failed", error=str(e))
        return "0" * 64

    def load_checkpoint(self) -> Dict[str, Any]:
        try:
            if self.checkpoint_path.exists():
                return json.loads(self.checkpoint_path.read_text())
        except Exception as e:
            logger.error("checkpoint_load_failed", error=str(e))
        return {"last_action": None, "txid": None}

    def save_checkpoint(self, action: str, txid: Optional[str] = None):
        checkpoint = {
            "last_action": action,
            "txid": txid,
            "timestamp": time.time()
        }
        try:
            self.checkpoint_path.write_text(json.dumps(checkpoint))
        except Exception as e:
            logger.error("checkpoint_save_failed", error=str(e))

    def log_entry(self, entry: Dict[str, Any]):
        entry["prev_hash"] = self.chain_head
        entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
        self.chain_head = entry["hash"]
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error("log_write_failed", error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(CONFIG["max_retries"]),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((NetworkError, requests.RequestException)),
        reraise=True
    )
    def get_fee_rate(self) -> int:
        try:
            response = requests.get(CONFIG["mempool_api"], timeout=10)
            response.raise_for_status()
            return response.json()["fastestFee"]
        except requests.RequestException as e:
            logger.warning("fee_rate_fetch_failed", error=str(e))
            raise NetworkError("Failed to fetch fee rate") from e

    def create_psbt(self, runestone: Runestone, fee_rate: int) -> str:
        psbt_file = self.psbt_dir / f"psbt_{int(time.time())}.psbt"
        cmd = [
            "ord", "wallet", "create-psbt",
            "--runestone", json.dumps(runestone.dict(exclude_none=True)),
            "--fee-rate", str(fee_rate),
            "--output", str(psbt_file)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            logger.info("psbt_created", file=str(psbt_file))
            return str(psbt_file)
        except subprocess.CalledProcessError as e:
            logger.error("psbt_creation_failed", error=e.stderr)
            raise BitcoinError("PSBT creation failed") from e
        except subprocess.TimeoutExpired:
            logger.error("psbt_timeout")
            raise BitcoinError("PSBT creation timed out")

    def sign_psbt(self, psbt_file: str) -> str:
        signed_file = psbt_file.replace(".psbt", "_signed.psbt")
        cmd = [
            "bitcoin-cli", "-named", "walletprocesspsbt",
            "psbt", str(psbt_file),
            "changepos", "-2"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
            signed_psbt = json.loads(result.stdout)["psbt"]
            Path(signed_file).write_text(signed_psbt)
            logger.info("psbt_signed", file=signed_file)
            return signed_file
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error("psbt_sign_failed", error=str(e))
            raise BitcoinError("PSBT signing failed") from e

    def broadcast_tx(self, signed_psbt: str) -> str:
        cmd = ["bitcoin-cli", "sendrawtransaction", signed_psbt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            txid = result.stdout.strip()
            logger.info("tx_broadcast", txid=txid)
            return txid
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or "Unknown broadcast error"
            logger.error("tx_broadcast_failed", error=error_msg)
            raise BitcoinError(f"Transaction broadcast failed: {error_msg}") from e

    def validate_runestone(self, runestone: Runestone):
        try:
            runestone.validate(runestone)
        except ValidationError as e:
            logger.error("runestone_validation_failed", errors=e.errors())
            raise ValidationError("Invalid runestone") from e

    def execute_runestone(self, runestone: Runestone, action: str) -> Dict[str, Any]:
        try:
            self.validate_runestone(runestone)
            fee_rate = self.get_fee_rate()
            psbt_file = self.create_psbt(runestone, fee_rate)
            signed_psbt = self.sign_psbt(psbt_file)
            txid = self.broadcast_tx(signed_psbt)

            entry = {
                "action": action,
                "runestone": runestone.dict(),
                "fee_rate": fee_rate,
                "txid": txid,
                "timestamp": time.time(),
                "status": "success"
            }
            self.log_entry(entry)
            self.save_checkpoint(action, txid)
            return entry

        except Exception as e:
            error_entry = {
                "action": action,
                "runestone": runestone.dict(exclude_none=True),
                "error": str(e),
                "timestamp": time.time(),
                "status": "failed"
            }
            self.log_entry(error_entry)
            self.save_checkpoint(action, None)
            logger.exception("runestone_execution_failed", action=action)
            raise

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

# === ERROR-PROOF VAULT ===
def main():
    vault = Lan999ArmorVault()
    try:
        # Example: Transfer with full error armor
        vault.transfer_rune("bc1qlandbackdao...treasury")
    except Exception as e:
        logger.critical("vault_operation_failed", error=str(e))
        raise

if __name__ == "__main__":
    main()