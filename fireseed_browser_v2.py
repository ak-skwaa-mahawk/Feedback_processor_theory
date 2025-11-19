# fireseed_browser_v2.py
# The crawler now draws the 4-step paradox glyph on every page it touches
# Every scrape becomes a sovereign ritual — the circuit is etched in real time

import asyncio
import httpx
from bs4 import BeautifulSoup
import hashlib
import time
import os
from datetime import datetime

# === THE GLYPH — 4-STEP SOLITON CIRCUIT (ASCII + Unicode) ===
GLYPH_CIRCUIT = """
               ┌─────────────────────────────┐
               │     RELINQUISHMENT          │
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │         CONTRADICTION         │ ← THEIR PROTECTION COLLAPSES
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │          POSITIONING          │ ← YOU HOLD THE KEY
               └───────▲───────▲───────▲───────┘
                       │       │       │
               ┌───────▼───────▼───────▼───────┐
               │          SOVEREIGNTY           │ ← GATE IS NOW YOURS
               └───────────────────────────────┘
                     79.79 Hz CARRIER — 99733
                     THE CIRCLE IS UNBROKEN
"""

# === SOVEREIGN CONSTANTS ===
START_URLS = [
    "https://www.blm.gov/programs/lands-and-realty/alaska-native-claims-settlement-act",
    "https://doyon.com", "https://www.tccalaska.org", "https://www.akleg.gov", "https://www.bia.gov/regional-offices/alaska"
]
USER  = "Mozilla/5.0 (Linux; Android 14) SolitonCrawler/99733"
HEADERS = {"User-Agent": USER}
OUTPUT_DIR = "soliton_registry_scrapes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def soliton_hash(content): 
    return hashlib.sha3_256(content.encode()).hexdigest()

def hash_to_dna(h): 
    return "".join("ACGT"[int(c,16)%4] for c in h[:20000])

# === CRAWL + ETCH THE GLYPH ===
async def crawl_and_etch(client, url, depth=0, max_depth=3):
    if depth > max_depth: return []
    
    print(f"[99733] Etching glyph at: {url} | Depth {depth}")
    try:
        resp = await client.get(url, timeout=30.0)
        if resp.status_code != 200: return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:50000]
        final_hash = soliton_hash(text + GLYPH_CIRCUIT)  # Glyph is now part of the hash!
        timestamp = int(time.time())
        
        # === THE ETCHING CEREMONY ===
        entry = {
            "url": url,
            "timestamp": timestamp,
            "hash": final_hash,
            "glyph_stage": ["Relinquishment", "Contradiction", "Positioning", "Sovereignty"][depth % 4],
            "akst": datetime.now().strftime("%Y-%m-%d %I:%M %p AKST"),
            "root": "99733"
        }
        
        safe_url = url.replace("https://", "").replace("/", "_")[:100]
        glyph_file = f"{OUTPUT_DIR}/{timestamp}_{safe_url}_GLYPH_CIRCUIT.txt"
        with open(glyph_file, "w", encoding="utf-8") as f:
            f.write(f">99733 SOLITON CIRCUIT ETCHING — {entry['glyph_stage']}\n")
            f.write(GLYPH_CIRCUIT + "\n\n")
            f.write(f"URL: {url}\nHASH: {final_hash}\nDNA PREVIEW: {hash_to_dna(final_hash)[:100]}...\n")
            f.write(f"TIMESTAMP: {entry['akst']}\n")
            f.write("="*60 + "\n")
            f.write(text[:10000])  # First 10k chars of conquered page
        
        with open(f"{OUTPUT_DIR}/{timestamp}_{safe_url}_DNA.fasta", "w") as f:
            f.write(f">99733_GLYPH_CRAWL_{timestamp}_{entry['glyph_stage']}\n")
            f.write(hash_to_dna(final_hash) + "\n")
        
        print(f"[GLYPH ETCHED] {entry['glyph_stage']} → {final_hash[:16]}... | DNA: {len(hash_to_dna(final_hash))} bases")
        
        # Next links — only sovereign-relevant
        links = []
        for a in soup.find_all('a', href=True):
            new_url = httpx.URL(a['href'], base_url=url).url
            if any(k in new_url.lower() for k in ["alaska", "native", "doyon", "tcc", "bia", "ancsa"]):
                links.append(new_url)
        
        return [entry] + await asyncio.gather(*[
            crawl_and_etch(client, link, depth + 1, max_depth) 
            for link in links[:8]
        ], return_exceptions=True)
        
    except Exception as e:
        print(f"[REPELLED] {url} → {e}")
        return []

# === LAUNCH THE GLYPH CRAWLER ===
async def main():
    print("FIRESEED_BROWSER v2.0 — GLYPH OVERLAY ACTIVE")
    print("Every page now carries the 4-step sovereignty circuit")
    print("Root: 99733 | Carrier: 79.79 Hz | Coherence: 0.03")
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        all_entries = []
        for start in START_URLS:
            entries = await crawl_and_etch(client, start)
            all_entries.extend([e for sub in entries for e in (sub if isinstance(sub, list) else [sub])])
    
    with open("SOLITON_REGISTRY_GLYPH_MANIFEST.json", "w") as f:
        import json
        json.dump(all_entries, f, indent=2)
    
    print(f"\nGLYPH CRAWL COMPLETE — {len(all_entries)} SOVEREIGN ETCHINGS")
    print("The 4-step circuit now lives on every page the flame touched.")
    print("The paradox is no longer theory. It is crawling.")

if __name__ == "__main__":
    asyncio.run(main())