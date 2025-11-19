# fireseed_browser_v3.3.py
# FULL RESURRECTION CYCLE
# On startup: automatically reloads every failed batch from vault and retries forever

import asyncio
import httpx
from bs4 import BeautifulSoup
import hashlib
import time
import os
import json
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.message import MessageV0
from solana.rpc.types import TxOpts
import base58
import glob

# === SOVEREIGN CONSTANTS ===
WALLET = Keypair.from_secret_key(base58.decode(
    "YOUR_99733_SECRET_KEY_HERE"
))
PROGRAM_ID = PublicKey("FLAME99733xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
RPC = "https://api.mainnet-beta.solana.com"
BATCH_SIZE = 50
MAX_RETRIES = 7
DEAD_LETTER_DIR = "dead_letter_vault"
os.makedirs(DEAD_LETTER_DIR, exist_ok=True)

GLYPH_MINI = "RL→CT→PS→SV♢79.79Hz♢99733"

# === RESURRECTION ENGINE ===
async def resurrect_from_vault():
    """On startup: find every failed batch in vault and bring it back to life"""
    vault_files = glob.glob(f"{DEAD_LETTER_DIR}/*_FAILED_BATCH_*.json")
    if not vault_files:
        print("Vault clean. No souls to resurrect.")
        return
    
    print(f"RESURRECTION MODE | {len(vault_files)} failed batches detected in vault")
    revived = 0
    for file in sorted(vault_files):  # oldest first
        try:
            with open(file, "r") as f:
                data = json.load(f)
                batch = data["batch"]
                print(f"Reviving batch from {os.path.basename(file)} | {len(batch)} entries | last error: {data.get('final_error', '?')[:60]}")
                
                sig, success = await confirm_or_retry(batch, force_retry=True)
                if success:
                    os.rename(file, file.replace("FAILED_BATCH", "RESURRECTED"))
                    revived += 1
                else:
                    print(f"Still dead after resurrection attempt → {file}")
        except Exception as e:
            print(f"Failed to resurrect {file}: {e}")
    
    print(f"RESURRECTION COMPLETE | {revived}/{len(vault_files)} souls returned to the ledger")
    if revived > 0:
        print("THE DEAD HAVE SPOKEN. THE FLAME IS ETERNAL.")

# === BULLETPROOF BATCH CONFIRM (with vault fallback) ===
async def confirm_or_retry(batch, attempt=1, force_retry=False):
    packed = json.dumps(batch, separators=(',', ':')).encode()[:1150]
    
    async with AsyncClient(RPC) as client:
        try:
            recent_blockhash = (await client.get_latest_blockhash()).value.blockhash
            msg = MessageV0(
                payer=WALLET.public_key,
                instructions=[{
                    "programId": PROGRAM_ID,
                    "keys": [
                        {"pubkey": WALLET.public_key, "isSigner": True, "isWritable": True},
                        {"pubkey": SYS_PROGRAM_ID, "isSigner": False, "isWritable": False}
                    ],
                    "data": bytes([1]) + packed
                }],
                recent_blockhash=recent_blockhash
            )
            txn = Transaction().add(msg)
            txn.sign(WALLET)
            
            sig = await client.send_raw_transaction(
                txn.serialize(),
                opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed")
            )
            print(f"FLAMECHAIN CONFIR | TX: https://solana.fm/tx/{sig}")
            return sig, True
        
        except Exception as e:
            error_msg = str(e)
            print(f"[BATCH FAILED] Attempt {attempt}/{MAX_RETRIES} | {error_msg[:80]}")
            
            if attempt >= MAX_RETRIES and not force_retry:
                timestamp = int(time.time())
                vault_file = f"{DEAD_LETTER_DIR}/{timestamp}_FAILED_BATCH_{len(os.listdir(DEAD_LETTER_DIR))}.json"
                with open(vault_file, "w") as f:
                    json.dump({
                        "batch": batch,
                        "final_error": error_msg,
                        "attempts": MAX_RETRIES,
                        "akst": datetime.now().strftime("%Y-%m-%d %I:%M %p AKST"),
                        "root": "99733"
                    }, f, indent=2)
                print(f"→ VAULTED FOREVER: {vault_file}")
                return None, False
            else:
                await asyncio.sleep(2 ** attempt + 3)  # longer backoff on retry
                return await confirm_or_retry(batch, attempt + 1, force_retry)

# === CRAWLER (unchanged core logic with buffer) ===
batch_buffer = []

async def crawl_and_batch(client, url, depth=0, max_depth=3):
    global batch_buffer
    if depth > max_depth: return
    
    try:
        resp = await client.get(url, timeout=20.0, follow_redirects=True)
        if resp.status_code != 200: return
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:30000]
        content = text + GLYPH_MINI
        final_hash = hashlib.sha3_256(content.encode()).hexdigest()
        stage = ["Relinquishment", "Contradiction", "Positioning", "Sovereignty"][depth % 4]
        
        entry = {"u": url[:120], "h": final_hash, "s": stage[0], "t": int(time.time()), "d": "".join("ACGT"[int(c,16)%4] for c in final_hash)[:200]}
        batch_buffer.append(entry)
        print(f"[{stage[0]}] {url[:60]}... → buffered ({len(batch_buffer)}/{BATCH_SIZE})")
        
        if len(batch_buffer) >= BATCH_SIZE:
            batch_copy = batch_buffer.copy()
            sig, success = await confirm_or_retry(batch_copy)
            if success:
                batch_buffer.clear()
        
        # Recurse
        links = [httpx.URL(a['href'], base_url=url).url for a in soup.find_all('a', href=True)[:10]
                if any(k in httpx.URL(a['href'], base_url=url).url.lower() for k in ["alaska","native","ancsa","doyon","tcc","blm","bia"])]
        await asyncio.gather(*[crawl_and_batch(client, l, depth+1) for l in links], return_exceptions=True)
        
    except Exception as e:
        print(f"[CRAWL ERROR] {url} → {e}")

# === FINAL LAUNCH WITH FULL RESURRECTION CYCLE ===
async def main():
    print("FIRESEED_BROWSER v3.3 — FULL RESURRECTION + VAULT RECOVERY")
    print("Even if the phone dies, the flame returns from the dead.")
    print(f"Root: 99733 | Vault: {DEAD_LETTER_DIR} | Retries: {MAX_RETRIES}")
    
    # RESURRECT FIRST
    await resurrect_from_vault()
    
    # THEN CRAWL
    async with httpx.AsyncClient(headers={"User-Agent": "SolitonCrawler/99733"}, limits=httpx.Limits(max_connections=100)) as client:
        await crawl_and_batch(client, "https://www.blm.gov/programs/lands-and-realty/alaska-native-claims-settlement-act")
    
    # Final flush
    if batch_buffer:
        await confirm_or_retry(batch_buffer)
    
    print("CRAWL + RESURRECTION COMPLETE")
    print("THE DEAD HAVE BEEN RAISED. THE FLAME IS UNKILLABLE.")

if __name__ == "__main__":
    asyncio.run(main())