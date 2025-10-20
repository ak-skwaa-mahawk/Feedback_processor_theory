#!/usr/bin/env python3
"""
Latest Precedence Entry Viewer
===============================
Display the most recent entry from the precedence log.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0

Usage:
    python latest_entry.py
    python latest_entry.py --count 5    # Show last 5 entries
"""

import json
from pathlib import Path
import sys


# Configuration
REPO_ROOT = Path(__file__).resolve().parent.parent
HASH_INDEX_PATH = REPO_ROOT / "precedence_hashes.json"


def load_hash_index() -> dict:
    """Load hash index if it exists."""
    if HASH_INDEX_PATH.exists():
        with open(HASH_INDEX_PATH, 'r') as f:
            return json.load(f)
    return {"entries": [], "metadata": {}}


def print_entry(entry: dict, index: int = None, total: int = None):
    """Print a single entry in formatted style."""
    print("=" * 70)
    
    if index and total:
        print(f"PRECEDENCE ENTRY #{index} of {total}")
    else:
        print("LATEST PRECEDENCE ENTRY")
    
    print("=" * 70)
    print()
    print(f"Timestamp:   {entry['timestamp']}")
    print(f"Description: {entry['description']}")
    
    if entry.get('keyphrase'):
        print(f"Key Phrase:  {entry['keyphrase']}")
    
    print(f"Commit:      {entry['commit']}")
    print(f"SHA-256:     {entry['hash']}")
    
    print()
    print("=" * 70)


def show_latest(count: int = 1):
    """Display the latest N entries."""
    index = load_hash_index()
    
    if not index.get('entries'):
        print("=" * 70)
        print("NO ENTRIES FOUND")
        print("=" * 70)
        print()
        print("The precedence log is empty.")
        print(f"Expected index file: {HASH_INDEX_PATH}")