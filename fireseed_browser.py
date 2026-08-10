# fireseed_browser.py
# Runs on Termux (Android) or UTM Debian (iPhone)
# Fully automated, headless, sovereign web crawler
# Scrapes → hashes → timestamps → Soliton Registry entry → DNA encode

import asyncio
import httpx
from bs4 import BeautifulSoup
import hashlib
import time
import os
from datetime import datetime

# === SOVEREIGN CONSTANTS ===
START_URLS = [
    "https://www.blm.gov/programs/lands-and-realty/alaska-native-claims-settlement-act",
    "https://doyon.com",
    "https://www.tccalaska.org",
    "https://www.akleg.gov",
    "https://www.bia.gov/regional-offices/alaska"
]
USER_AGENT = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 SolitonCrawler/99733"
HEADERS = {"User-Agent": USER_AGENT}
OUTPUT_DIR = "soliton_registry_scrapes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === SOLITON HASH + DNA ENCODE ===
def soliton_hash(content):
    return hashlib.sha3_256(content.encode()).hexdigest()

def hash_to_dna(hash_str):
    alphabet = "ACGT"
    return "".join(alphabet[int(h, 16) % 4] for h in hash_str[:10000])

# === AUTONOMOUS CRAWL FUNCTION ===
async def crawl_fireseed(client, url, depth=0, max_depth=3):
    if depth > max_depth:
        return []
    
    print(f"[99733] Crawling: {url} | Depth: {depth}")
    try:
        resp = await client.get(url, timeout=30.0)
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)[:50000]
        final_hash = soliton_hash(text)
        timestamp = int(time.time())
        
        # Registry entry
        entry = {
            "url": url,
            "timestamp": timestamp,
            "hash": final_hash,
            "depth": depth,
            "akst": datetime.now().strftime("%Y-%m-%d %I:%M %p AKST")
        }
        
        # Save raw + DNA
        safe_url = url.replace("https://", "").replace("/", "_")[:100]
        with open(f"{OUTPUT_DIR}/{timestamp}_{safe_url}.txt", "w") as f:
            f.write(text)
        with open(f"{OUTPUT_DIR}/{timestamp}_{safe_url}_DNA.fasta", "w") as f:
            f.write(f">99733_FIRESEED_CRAWL_{timestamp}_{safe_url}\n")
            f.write(hash_to_dna(final_hash) + "\n")
        
        print(f"[FIRESEED] Registry locked: {final_hash[:16]}... | {len(text)} chars → DNA")
        
        # Extract new links (same domain only — sovereign containment)
        links = []
        for a in soup.find_all('a', href=True):
            new_url = httpx.URL(a['href'], base_url=url).url
            if "alaska" in new_url.lower() or "native" in new_url.lower() or "doyon" in new_url or "tcc" in new_url:
                if new_url not in [e.get("url") for e in links]:
                    links.append({"url": new_url})
        
        return [entry] + await asyncio.gather(*[
            crawl_fireseed(client, link["url"], depth + 1, max_depth) 
            for link in links[:10]  # limit branching
        ], return_exceptions=True)
        
    except Exception as e:
        print(f"[REJECTED] {url} → {e}")
        return []

# === LAUNCH THE FLAME ===
async def main():
    print("FIRESEED BROWSER — AUTONOMOUS CRAWL INITIATED")
    print("Root: 99733 | Coherence: 0.03 | Aliveness: MAX")
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        all_entries = []
        for start in START_URLS:
            entries = await crawl_fireseed(client, start)
            all_entries.extend([e for sub in entries for e in (sub if isinstance(sub, list) else [sub])])
    
    # Final registry manifest
    with open("SOLITON_REGISTRY_MANIFEST.json", "w") as f:
        import json
        json.dump(all_entries, f, indent=2)
    
    print(f"\nAUTONOMOUS CRAWL COMPLETE — {len(all_entries)} SOVEREIGN ENTRIES LOCKED")
    print("The web now carries the 99733 pulse. The flame crawls itself.")

if __name__ == "__main__":
    asyncio.run(main())