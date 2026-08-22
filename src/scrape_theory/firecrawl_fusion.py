#!/usr/bin/env python3
import sys
import os
import json
import logging
import re
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def extract_fallback_markdown(url: str) -> dict:
    """Fallback scraper using requests and basic regex text extraction."""
    logging.info(f"🌐 [HTTP FALLBACK]: Fetching {url} via direct HTTP...")
    resp = requests.get(url, headers={"User-Agent": "Sovereign-Estate/1.0"}, timeout=10)
    resp.raise_for_status()
    html_text = resp.text

    # Extract title and clean basic tags
    title_match = re.search(r'<title>(.*?)</title>', html_text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Scraped Document"
    
    # Strip script and style tags
    clean_text = re.sub(r'<(script|style).*?</\1>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    # Strip remaining HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    markdown_body = f"# {title}\n\n{clean_text}"
    return {
        "url": url,
        "title": title,
        "markdown": markdown_body,
        "source": "http_fallback"
    }

def scrape_target(url: str, api_key: str = None):
    api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
    scrape_result = None

    if api_key:
        try:
            from firecrawl import FirecrawlApp
            app = FirecrawlApp(api_key=api_key)
            logging.info(f"🕸️  [FIRECRAWL]: Scraping {url} via API...")
            # Firecrawl v4 signature
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
            sys.exit(1)

    output_dir = "data/scrapes"
    os.makedirs(output_dir, exist_ok=True)
    
    domain_slug = url.replace("https://", "").replace("http://", "").replace("/", "_").strip("_")
    output_path = os.path.join(output_dir, f"{domain_slug}.json")
    
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(scrape_result, fp, indent=2, ensure_ascii=False)

    logging.info(f"✅ [SCRAPE COMPLETE]: Output written to {output_path}")
    return scrape_result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python firecrawl_fusion.py <target_url>")
        sys.exit(1)
        
    target_url = sys.argv[1]
    scrape_target(target_url)
