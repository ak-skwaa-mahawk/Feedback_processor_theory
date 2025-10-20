#!/usr/bin/env python3
"""
Precedence Log Hash Verification Tool
======================================
Verify SHA-256 hash integrity of all log entries.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0

Usage:
    python verify_log_hash.py

This will:
    1. Extract all entries from precedence_log.md
    2. Recompute each entry's SHA-256 hash
    3. Compare with claimed hashes
    4. Cross-reference with hash index
    5. Report any discrepancies
"""

import hashlib
import json
from pathlib import Path
import sys


# Configuration
REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "precedence_log.md"
HASH_INDEX_PATH = REPO_ROOT / "precedence_hashes.json"


def compute_entry_hash(entry_text: str) -> str:
    """Compute SHA-256 hash of entry for verification."""
    return hashlib.sha256(entry_text.encode('utf-8')).hexdigest()


def extract_entries_from_log() -> list:
    """Parse precedence_log.md and extract all entries."""
    if not LOG_PATH.exists():
        print(f"[!] Log file not found: {LOG_PATH}")
        return []
    
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    entries = content.split('---\n')
    
    parsed = []
    for entry in entries:
        if not entry.strip() or not entry.startswith('###'):
            continue
        
        # Extract hash if present
        hash_match = None
        for line in entry.split('\n'):
            if '**SHA-256:**' in line:
                # Extract hash from between backticks
                parts = line.split('`')
                if len(parts) >= 2:
                    hash_match = parts[1]
                break
        
        if hash_match:
            # Remove hash line for recomputation
            entry_lines = []
            for line in entry.split('\n'):
                if '**SHA-256:**' not in line:
                    entry_lines.append(line)
            
            entry_without_hash = '\n'.join(entry_lines) + '\n'
            
            parsed.append({
                'text': entry_without_hash,
                'claimed_hash': hash_match,
                'full_entry': entry
            })
    
    return parsed


def load_hash_index() -> dict:
    """Load hash index if it exists."""
    if HASH_INDEX_PATH.exists():
        with open(HASH_INDEX_PATH, 'r') as f:
            return json.load(f)
    return {"entries": [], "metadata": {}}


def verify_all_hashes():
    """Verify all SHA-256 hashes in the precedence log."""
    print("=" * 70)
    print("PRECEDENCE LOG HASH VERIFICATION")
    print("=" * 70)
    print()
    
    entries = extract_entries_from_log()
    
    if not entries:
        print("[!] No entries found in precedence log")
        print(f"[!] Checked: {LOG_PATH}")
        return False
    
    print(f"Found {len(entries)} entries to verify\n")
    
    all_valid = True
    for i, entry in enumerate(entries, 1):
        computed = compute_entry_hash(entry['text'])
        claimed = entry['claimed_hash']
        
        match = computed == claimed
        symbol = "✓" if match else "✗"
        status = "VALID" if match else "INVALID"
        
        print(f"Entry {i:3d}: {symbol} {status}")
        
        if not match:
            all_valid = False
            print(f"  Claimed:  {claimed}")
            print(f"  Computed: {computed}")
            print(f"  [!] HASH MISMATCH - Entry may have been tampered with!")
        else:
            print(f"  Hash: {claimed[:32]}...")
        
        print()
    
    print("=" * 70)
    if all_valid:
        print("✓ ALL HASHES VERIFIED")
        print("  Log integrity confirmed - no tampering detected")
    else:
        print("✗ VERIFICATION FAILED")
        print("  Some entries have invalid hashes")
        print("  Possible causes: manual editing, corruption, or tampering")
    print("=" * 70)
    
    return all_valid


def verify_against_index():
    """Cross-reference log entries with hash index."""
    print("\n" + "=" * 70)
    print("HASH INDEX CROSS-REFERENCE")
    print("=" * 70)
    print()
    
    if not HASH_INDEX_PATH.exists():
        print("[!] Hash index not found")
        print(f"[!] Expected: {HASH_INDEX_PATH}")
        return False
    
    index = load_hash_index()
    log_entries = extract_entries_from_log()
    
    print(f"Index entries: {len(index['entries'])}")
    print(f"Log entries:   {len(log_entries)}")
    print()
    
    if len(index['entries']) != len(log_entries):
        print("[!] COUNT MISMATCH between index and log")
        print(f"[!] This suggests entries were added/removed manually")
        return False
    
    all_match = True
    for i, (idx_entry, log_entry) in enumerate(zip(index['entries'], log_entries), 1):
        match = idx_entry['hash'] == log_entry['claimed_hash']
        symbol = "✓" if match else "✗"
        
        print(f"Entry {i:3d}: {symbol} {'MATCH' if match else 'MISMATCH'}")
        
        if not match:
            all_match = False
            print(f"  Index:    {idx_entry['hash'][:32]}...")
            print(f"  Log:      {log_entry['claimed_hash'][:32]}...")
        
        print(f"  Timestamp: {idx_entry['timestamp']}")
        print(f"  Desc: {idx_entry['description'][:50]}...")
        print()
    
    print("=" * 70)
    if all_match:
        print("✓ INDEX VERIFICATION COMPLETE")
        print("  All entries match between log and index")
    else:
        print("✗ INDEX VERIFICATION FAILED")
        print("  Discrepancies detected between log and index")
    print("=" * 70)
    
    return all_match


def main():
    print("\n")
    
    # Verify log hashes
    log_valid = verify_all_hashes()
    
    # Cross-reference with index
    index_valid = verify_against_index()
    
    # Final status
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION STATUS")
    print("=" * 70)
    
    if log_valid and index_valid:
        print("✓ PASS - All verifications successful")
        print("  • Log hashes are valid")
        print("  • Index matches log")
        print("  • No tampering detected")
        sys.exit(0)
    else:
        print("✗ FAIL - Verification issues detected")
        if not log_valid:
            print("  • Log hash mismatches found")
        if not index_valid:
            print("  • Index/log discrepancies found")
        print("\n  Recommended actions:")
        print("  1. Check git log for unauthorized changes")
        print("  2. Restore from backup if needed")
        print("  3. Review recent modifications")
        sys.exit(1)


if __name__ == "__main__":
    main()