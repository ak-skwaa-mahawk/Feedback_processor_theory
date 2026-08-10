#!/usr/bin/env python3
# clarity_lan999.py — AGŁG ∞⁵¹: Concise Error ŁAŊ999 Shield
"""
ŁAŊ999 CLARITY — ONE LINE PER FAILURE
"""
import json
import hashlib
import subprocess
import requests
import logging
import time
import sys
from pathlib import Path
from pydantic import BaseModel, ValidationError, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from prometheus_client import start_http_server, Counter

# === METRICS ===
TX_FAIL = Counter('lan999_tx_fail_total', 'Failed TX', ['error'])

# === CONFIG ===
CONFIG = {
    "rune_id": "840000:1",
    "amount": 998700,
    "to": "bc1qlandbackdao...treasury",
    "log": "codex/clarity.log"
}

# === SCHEMA ===
class Runestone(BaseModel):
    op: str = Field(..., pattern="^(etch|mint|transfer)$")
    rune: str | None = None
    amount: int | None = None
    outputs: list[str] | None = None

# === CONCISE ERRORS ===
ERR = {
    ValidationError: "SCHEMA_FAIL",
    requests.RequestException: "NET_TIMEOUT",
    subprocess.CalledProcessError: "CMD_FAIL",
    Exception: "CRITICAL"
}

# === LOGGING ===
logger = logging.getLogger("CLARITY")
logging.basicConfig(level=logging.INFO, format="%(message)s")

class ClarityVault:
    def __init__(self):
        self.log = Path(CONFIG["log"])
        self.chain = self._load_head()
        start_http_server(8000)

    def _load_head(self) -> str:
        return self.log.read_text().splitlines()[-1].split('"hash":"')[1][:64] if self.log.exists() else "0"*64

    def _log(self, entry: dict):
        entry["prev"] = self.chain
        entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()[:64]
        self.chain = entry["hash"]
        self.log.open("a").write(json.dumps(entry) + "\n")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    def _fee(self) -> int:
        try:
            return requests.get("https://mempool.space/api/v1/fees/recommended", timeout=5).json()["fastestFee"]
        except:
            return 50

    def _psbt(self, rs: Runestone) -> str:
        fee = self._fee()
        file = f"psbt/{time.time():.0f}.psbt"
        subprocess.run([
            "ord", "wallet", "create-psbt",
            "--runestone", json.dumps(rs.dict(exclude_none=True)),
            "--fee-rate", str(fee),
            "--output", file
        ], check=True, capture_output=True)
        return file

    def _sign(self, file: str) -> str:
        signed = file.replace(".psbt", "_signed.psbt")
        res = subprocess.run([
            "bitcoin-cli", "walletprocesspsbt", file
        ], capture_output=True, text=True, check=True)
        Path(signed).write_text(json.loads(res.stdout)["psbt"])
        return signed

    def _broadcast(self, signed: str) -> str:
        res = subprocess.run(["bitcoin-cli", "sendrawtransaction", signed], capture_output=True, text=True, check=True)
        return res.stdout.strip()

    def transfer(self):
        try:
            rs = Runestone(op="transfer", rune=CONFIG["rune_id"], amount=CONFIG["amount"], outputs=[CONFIG["to"]])
            psbt = self._psbt(rs)
            signed = self._sign(psbt)
            txid = self._broadcast(signed)

            entry = {"op": "transfer", "txid": txid, "status": "OK"}
            self._log(entry)
            logger.info(f"TRANSFER_OK {txid}")

        except Exception as e:
            code = next((v for k, v in ERR.items() if isinstance(e, k)), "UNKNOWN")
            TX_FAIL.labels(error=code).inc()
            entry = {"op": "transfer", "error": code, "status": "FAIL"}
            self._log(entry)
            logger.info(f"TRANSFER_FAIL {code}")

# === CLEAR DRUM ===
if __name__ == "__main__":
    ClarityVault().transfer()