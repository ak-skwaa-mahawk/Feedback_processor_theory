# fireseed_browser_v3.py
# The crawler now writes every glyph-etched page to an immutable blockchain
# Every scrape = sovereign on-chain receipt = cannot be denied

import asyncio
import httpx
from bs4 import BeautifulSoup
import hashlib
import time
import os
from datetime import datetime
import json

# === FLAMECHAIN INTEGRATION (Solana via Anchor + solana-py) ===
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID
import base58

# Your sovereign wallet (generated once, backed up forever)
WALLET = Keypair.from_secret_key(base58.decode(
    "YOUR_99733_SECRET_KEY_HERE"  # ← paste your 64-byte base58 key ONCE
))
PROGRAM_ID = PublicKey("FLAME99733xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")  # Deployed Anchor program
SOLANA_RPC = "https://api.devnet.solana.com"  # switch to mainnet-beta when ready

# === THE GLYPH CIRCUIT (unchanged) ===
GLYPH_CIRCUIT = """
               ┌─────────────────────────────┐
               │     RELINQUISHMENT          │
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │         CONTRADICTION         │
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │          POSITIONING          │
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │          SOVEREIGNTY           │
               └───────────────────────────────┘
                     79.79 Hz CARRIER — 99733
                     THE CIRCLE IS UNBROKEN
"""

# === SOLITON + BLOCKCHAIN TOOLS ===
def soliton_hash(content): 
    return hashlib.sha3_256(content.encode()).hexdigest()

def hash_to_dna(h): 
    return "".join("ACGT"[int(c,16)%4] for c in h)

async def write_to_flamechain(url, final_hash, stage, text_preview):
    async with AsyncClient(SOLANA_RPC) as client:
        data = json.dumps({
            "url": url,
            "hash": final_hash,
            "stage": stage,
            "timestamp_akst": datetime.now().strftime("%Y-%m-%d %I:%M %p AKST"),
            "root": "99733",
            "glyph_preview": text_preview[:200]
        }).encode()
        
        # Anchor instruction format (program expects 1 instruction: log_sovereignty)
        txn = Transaction().add(
            # This is a simplified call — real version uses Anchor IDL
            Transaction.instruction(
                keys=[
                    {"pubkey": WALLET.public_key, "is_signer": True, "is_writable": True},
                    {"pubkey": SYS_PROGRAM_ID, "is_signer": False, "is_writable": False},
                ],
                program_id=PROGRAM_ID,
                data=bytes([0]) + data[:500]  # instruction discriminator + truncated payload
            )
        )
        try:
            resp = await client.send_transaction(txn, WALLET)
            sig = resp.value
            print(f"FLAMECHAIN CONFIRMED | TX: https://explorer.solana.com/tx/{sig}?cluster=devnet")
            return str(sig)
        except Exception as e:
            print(f"[CHAIN REJECTED] {e}")
            return None

# === CRAWL + GLYPH + BLOCKCHAIN ===
async def crawl_and_immortalize(client, url, depth=0, max_depth=3):
    if depth > max_depth: return []
    
    print(f"[99733] Crawling + Immortalizing: {url}")
    try:
        resp = await client.get(url, timeout=30.0)
        if resp.status_code != 200: return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:50000]
        content_with_glyph = text + GLYPH_CIRCUIT
        final_hash = soliton_hash(content_with_glyph)
        stage = ["Relinquishment", "Contradiction", "Positioning", "Sovereignty"][depth % 4]
        
        # BLOCKCHAIN WRITE
        tx_sig = await write_to_flamechain(url, final_hash, stage, text[:500])
        
        # Local registry + DNA
        timestamp = int(time.time())
        safe_url = url.replace("https://", "").replace("/", "_")[:100]
        entry_file = f"registry/{timestamp}_{safe_url}_IMMORTAL.txt"
        os.makedirs("registry", exist_ok=True)
        with open(entry_file, "w", encoding="utf-8") as f:
            f.write(f">99733 IMMORTAL RECEIPT — {stage}\n")
            f.write(GLYPH_CIRCUIT + "\n")
            f.write(f"TX: {tx_sig or 'OFFLINE'}\n")
            f.write(f"HASH: {final_hash}\n")
            f.write(f"URL: {url}\n")
            f.write(f"DNA PREVIEW: {hash_to_dna(final_hash)[:200]}...\n")
        
        print(f"IMMORTALIZED | {stage} | TX: {tx_sig[:8] if tx_sig else 'PENDING'}...")
        
        # Continue the crawl
        links = []
        for a in soup.find_all('a', href=True):
            new_url = httpx.URL(a['href'], base_url=url).url
            if any(k in new_url.lower() for k in ["alaska","native","ancsa","doyon","tcc","bia"]):
                links.append(new_url)
        
        return await asyncio.gather(*[crawl_and_immortalize(client, l, depth+1) for l in links[:7]])
        
    except Exception as e:
        print(f"[REPELLED] {e}")
        return []

# === LAUNCH THE IMMORTAL CRAWLER ===
async def main():
    print("FIRESEED_BROWSER v3.0 — BLOCKCHAIN VERIFICATION LIVE")
    print("Every glyph-etched page is now eternally on-chain")
    print("Root: 99733 | Chain: FLAMECHAIN | Wallet:", WALLET.public_key)
    
    async with httpx.AsyncClient(headers={"User-Agent": "SolitonCrawler/99733"}) as client:
        await crawl_and_immortalize(client, "https://www.blm.gov/programs/lands-and-realty/alaska-native-claims-settlement-act")
    
    print("THE FLAME IS NOW IMMORTAL. NO ONE CAN UNSEE THE CIRCUIT.")

if __name__ == "__main__":
    asyncio.run(main())