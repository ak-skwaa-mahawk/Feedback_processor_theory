#!/usr/bin/env python3
"""
derivative_registry.py – Gwich’in Math Sovereignty v001
99733-Q Ledger Scanner: Logs derivative works using Sovereign constants post 11/5/2025
CC0 + 99733-Q Inversion Clause applies. Interaction = consent to recursive loop.
"""
import csv, datetime, re, hashlib, requests, feedparser
from pathlib import Path

PRECEDENT_DATE = datetime.date(2025, 11, 5)
SOVEREIGN_TERMS = [
    r"99\.99%", r"0\.9999", r"3\.172", r"3\.173", r"1\.04", r"1\.03", r"1\.02",
    r"143\.008", r"137\.549", r"7\.9083", r"4\.17%", r"L\s*<\s*1", r"L\s*=\s*0\.976",
    r"golden angle 143", r"drum frequency 7\.9", r"coherence surplus 4\.17",
    r"snake_cap", r"vhitzee", r"ch'anchyah"
]
REG_FILE = Path("Derivative_Works_Registry.csv")

def init_registry():
    if not REG_FILE.exists():
        with open(REG_FILE, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["Reg#","Date_Claimed","Entity","Breakthrough","Element","Evidence","Status","Action","Hash"])
    return

def hash_entry(row):
    return hashlib.sha256("|".join(row).encode()).hexdigest()[:12]

def log_derivative(date_str, entity, title, element, evidence, status="Logged", action="Notice: Precedent 11/5/25"):
    init_registry()
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    if date <= PRECEDENT_DATE:
        print(f"SKIP: {entity} predates Floor. No claim.")
        return None

    with open(REG_FILE, 'r') as f:
        reg_num = sum(1 for _ in f)

    row = [f"{reg_num:03d}", date_str, entity, title, element, evidence, status, action]
    row.append(hash_entry(row))

    with open(REG_FILE, 'a', newline='') as f:
        csv.writer(f).writerow(row)
    print(f"LOGGED: Reg#{reg_num:03d} {entity} | {element} | {evidence}")
    return row[-1]

def scan_text(text, source_url, entity="Unknown", date_str=None):
    if date_str is None: date_str = datetime.date.today().isoformat()
    for term in SOVEREIGN_TERMS:
        if re.search(term, text, re.I):
            log_derivative(date_str, entity, f"Match: {term}", term, source_url)

def scan_arxiv():
    print("[SCAN] arXiv last 7 days...")
    url = "http://export.arxiv.org/api/query?search_query=all:recursive+OR+all:99.99+OR+all:143.008&sortBy=submittedDate&max_results=50"
    feed = feedparser.parse(url)
    for entry in feed.entries:
        text = entry.title + " " + entry.summary
        for term in SOVEREIGN_TERMS:
            if re.search(term, text, re.I):
                date = entry.published[:10]
                log_derivative(date, "arXiv", entry.title[:80], term, entry.link)

def scan_patents():
    print("[SCAN] PatentsView last 7 days...")
    q = {"q":{"_text_any":{"patent_title":"99.99 OR 143.008 OR 3.172 OR 7.9083 OR 4.17"}},"f":["patent_id","patent_title","patent_date"]}
    try:
        r = requests.post("https://api.patentsview.org/patents/query", json=q, timeout=10)
        for p in r.json().get("patents", []):
            log_derivative(p["patent_date"], "USPTO", p["patent_title"][:80], "Sovereign Match", f"https://patents.google.com/patent/US{p['patent_id']}")
    except Exception as e:
        print(f"Patent scan skip: {e}")

if __name__ == "__main__":
    init_registry()
    print("Derivative Works Registry ready. 99733-Q Active.")
    print("Commands: log_derivative() | scan_arxiv() | scan_patents()")
    
    # Backfill Reg#001-004 from your timeline
    log_derivative("2025-12-15","xAI","Recursive scaling law","99.99%","https://x.ai/blog/dec2025")
    log_derivative("2026-01-20","Anon Condensed Matter Lab","143deg skyrmion lattice observed","143.008°","arXiv:2601.12345")
    log_derivative("2026-02-03","Quantum Hardware Co","0.9999 fidelity error correction","SNAKE_CAP","USPTO App 18/xyz123")
    log_derivative("2026-03-11","Biotech Institute","Gram-scale protein stability window","Skipped grams basin","Nature DOI:10.1038/s41586-026-xxxx")