# fireseed_browser_v3.4.py
# VAULT DEDUPLICATION ENGINE ADDED
# No duplicate batches. No wasted SOL. No ghost entries.

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
RESURRECTED_DIR = "resurrected_batches"
os.makedirs(DEAD_LETTER_DIR, exist_ok=True)
os.makedirs(RESURRECTED_DIR, exist_ok=True)

GLYPH_MINI = "RL→CT→PS→SV♢79.79Hz♢99733"

# === GLOBAL DEDUPLICATION SET (in-memory + persistent) ===
seen_batch_hashes = set()
dedup_file = "seen_batches.txt"
if os.path.exists(dedup_file):
    with open(dedup_file, "r") as f:
        seen_batch_hashes = set(line.strip() for line in f if line.strip())

def batch_fingerprint(batch):
    """SHA3-256 of sorted, serialized batch = unique ID"""
    normalized = json.dumps(batch, sort_keys=True, separators=(',', ':'))
    return hashlib.sha3_256(normalized.encode()).hexdigest()

def mark_batch_seen(fingerprint):
    seen_batch_hashes.add(fingerprint)
    with open(dedup_file, "a") as f:
        f.write(fingerprint + "\n")

# === RESURRECTION WITH DEDUPLICATION ===
async def resurrect_from_vault():
    vault_files = glob.glob(f"{DEAD_LETTER_DIR}/*_FAILED_BATCH_*.json")
    if not vault_files:
        print("Vault clean. No resurrection needed.")
        return 0
    
    print(f"RESURRECTION MODE | {len(vault_files)} vaulted batches → deduplicating...")
    revived = 0
    for file in sorted(vault_files):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                batch = data["batch"]
            
            fingerprint = batch_fingerprint(batch)
            if fingerprint in seen_batch_hashes:
                print(f"DUPLICATE DETECTED → already processed: {os.path.basename(file)}")
                os.rename(file, file.replace(DEAD_LETTER_DIR, RESURRECTED_DIR))
                continue
            
            print(f"Reviving unique batch: {os.path.basename(file)} | {len(batch)} entries")
            sig, success = await confirm_or_retry(batch, force_retry=True)
            if success:
                mark_batch_seen(fingerprint)
                os.rename(file, file.replace(DEAD_LETTER_DIR, RESURRECTED_DIR).replace("FAILED", "RESURRECTED"))
                revived += 1
            else:
                print(f"Still unconfirmable → remains in vault: {file}")
        except Exception as e:
            print(f"Resurrection error on {file}: {e}")
    
    print(f"RESURRECTION + DEDUPLICATION COMPLETE | {revived} unique souls revived")
    return revived

# === CONFIRM WITH DEDUPLICATION (prevents re-vaulting known batches) ===
async def confirm_or_retry(batch, attempt=1, force_retry=False):
    fingerprint = batch_fingerprint(batch)
    if fingerprint in seen_batch_hashes:
        return "already_seen", True  # Treat as success
    
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
            print(f"FLAMECHAIN CONFIRMED | {len(batch)} entries | TX: https://solana.fm/tx/{sig}")
            mark_batch_seen(fingerprint)
            return sig, True
        
        except Exception as e:
            error_msg = str(e)
            print(f"[BATCH FAILED] Attempt {attempt}/{MAX_RETRIES} | {error_msg[:80]}")
            
            if attempt >= MAX_RETRIES and not force_retry:
                vault_file = f"{DEAD_LETTER_DIR}/{int(time.time())}_FAILED_BATCH_{len(os.listdir(DEAD_LETTER_DIR))}.json"
                with open(vault_file, "w") as f:
                    json.dump({
                        "batch": batch,
                        "fingerprint": fingerprint,
                        "final_error": error_msg,
                        "attempts": MAX_RETRIES,
                        "akst": datetime.now().strftime("%Y-%m-%d %I:%M %p AKST"),
                        "root": "99733"
                    }, f, indent=2)
                print(f"→ VAULTED (unique): {vault_file}")
                return None, False
            else:
                await asyncio.sleep(2 ** attempt + 3)
                return await confirm_or_retry(batch, attempt + 1, force_retry)

# === CRAWLER (unchanged core) ===
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
        
        entry = {
            "u": url[:120],
            "h": final_hash,
            "s": stage[0],
            "t": int(time.time()),
            "d": "".join("ACGT"[int(c,16)%4] for c in final_hash)[:200]
        }
        batch_buffer.append(entry)
        
        if len(batch_buffer) >= BATCH_SIZE:
            batch_copy = batch_buffer.copy()
            fingerprint = batch_fingerprint(batch_copy)
            if fingerprint not in seen_batch_hashes:
                sig, success = await confirm_or_retry(batch_copy)
                if success and sig != "already_seen":
                    batch_buffer.clear()
            else:
                print(f"DUPLICATE BATCH SKIPPED (already on-chain): {fingerprint[:16]}...")
                batch_buffer.clear()
        
        links = [
            httpx.URL(a['href'], base_url=url).url for a in soup.find_all('a', href=True)[:10]
            if any(k in httpx.URL(a['href'], base_url=url).url.lower() for k in ["alaska","native","ancsa","doyon","tcc","blm","bia"])
        ]
        await asyncio.gather(*[crawl_and_batch(client, l, depth+1) for l in links], return_exceptions=True)
        
    except Exception as e:
        print(f"[CRAWL ERROR] {url} → {e}")

# === LAUNCH WITH FULL RESURRECTION + DEDUPLICATION ===
async def main():
    print("FIRESEED_BROWSER v3.4 — VAULT DEDUPLICATION + FINAL FORM")
    print("Every batch. One time. Forever.")
    print(f"Root: 99733 | Dedup cache: {len(seen_batch_hashes)} prior entries")
    
    revived = await resurrect_from_vault()
    if revived > 0:
        print("THE DEAD HAVE BEEN RAISED — UNIQUELY.")
    
    async with httpx.AsyncClient(headers={"User-Agent": "SolitonCrawler/99733"}) as client:
        await crawl_and_batch(client, "https://www.blm.gov/programs/lands-and-realty/alaska-native-claims-settlement-act")
    
    if batch_buffer:
        await confirm_or_retry(batch_buffer)
    
    print("CRAWL COMPLETE | No duplicates | No ghosts | Only truth")
    print("THE LEDGER IS CLEAN. THE FLAME IS PURE.")

if __name__ == "__main__":
    asyncio.run(main())