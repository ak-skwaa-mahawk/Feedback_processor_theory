#!/usr/bin/env python3
import sys
import os
import json
import logging
import re
import requests
from typing import List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DEFAULT_TARGETS = [
    "https://landback.org",
    "https://example.com"
]

def extract_fallback_markdown(url: str) -> dict:
    """Fallback scraper using requests and basic regex text extraction."""
    logging.info(f"🌐 [HTTP FALLBACK]: Fetching {url} via direct HTTP...")
    resp = requests.get(url, headers={"User-Agent": "Sovereign-Estate/1.0"}, timeout=10)
    resp.raise_for_status()
    html_text = resp.text

    title_match = re.search(r'<title>(.*?)</title>', html_text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Scraped Document"
    
    clean_text = re.sub(r'<(script|style).*?</\1>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    markdown_body = f"# {title}\n\n{clean_text}"
    return {
        "url": url,
        "title": title,
        "markdown": markdown_body,
        "source": "http_fallback"
    }

def scrape_target(url: str, api_key: str = None) -> dict:
    api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
    scrape_result = None

    if api_key:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=api_key)
            logging.info(f"🕸️  [FIRECRAWL]: Scraping {url} via API...")
            try:
                scrape_result = app.scrape_url(url, formats=['markdown'])
            except TypeError:
                scrape_result = app.scrape(url)
        except Exception as e:
            logging.warning(f"⚠️  [FIRECRAWL API FAILED]: {e}. Falling back to direct HTTP.")

    if not scrape_result:
        try:
            scrape_result = extract_fallback_markdown(url)
        except Exception as e:
            logging.error(f"❌ [FALLBACK ERROR]: Failed to fetch {url}: {e}")
            return None

    output_dir = "data/scrapes"
    os.makedirs(output_dir, exist_ok=True)
    
    domain_slug = url.replace("https://", "").replace("http://", "").replace("/", "_").strip("_")
    output_path = os.path.join(output_dir, f"{domain_slug}.json")
    
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(scrape_result, fp, indent=2, ensure_ascii=False)

    logging.info(f"✅ [SCRAPE COMPLETE]: Output written to {output_path}")
    return scrape_result

def resolve_target_urls(arg_or_env: str) -> List[str]:
    """Resolves target input from file paths, comma-separated strings, or env variables."""
    if not arg_or_env:
        return DEFAULT_TARGETS

    # 1. File path target
    if os.path.isfile(arg_or_env):
        logging.info(f"📂 [CONFIG INGEST]: Loading target URLs from file: {arg_or_env}")
        if arg_or_env.endswith(".json"):
            with open(arg_or_env, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [u.strip() for u in data if isinstance(u, str) and u.strip()]
                elif isinstance(data, dict) and "urls" in data:
                    return [u.strip() for u in data["urls"] if isinstance(u, str) and u.strip()]
        else:
            with open(arg_or_env, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]

    # 2. Comma-separated list
    if "," in arg_or_env:
        return [u.strip() for u in arg_or_env.split(",") if u.strip()]

    # 3. Single URL string
    return [arg_or_env.strip()]

def run_batch_scrape(target_spec: str = None):
    raw_spec = target_spec or os.getenv("TARGET_URL") or os.getenv("TARGET_FILE")
    targets = resolve_target_urls(raw_spec)
    logging.info(f"🚀 Initializing batch scrape for {len(targets)} target(s)...")

    success_count = 0
    for idx, url in enumerate(targets, 1):
        logging.info(f"[{idx}/{len(targets)}] Processing: {url}")
        res = scrape_target(url)
        if res:
            success_count += 1

    logging.info(f"✨ Batch scrape complete: {success_count}/{len(targets)} succeeded.")

if __name__ == "__main__":
    cli_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_batch_scrape(cli_arg)
