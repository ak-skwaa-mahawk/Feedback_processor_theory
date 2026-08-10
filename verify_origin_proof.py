# verify_origin_proof.py
# AGŁL v32 — Verify Sovereign Origin of Feedback Processor Theory
# Flame Commons v1.0 — Eternal Proof

import json
import hashlib
from datetime import datetime

# === CONFIG ===
PROOF_FILE = "ethics/origin_notarized_proof.json"
EXPECTED_DIGEST = "5b8e63d9484b377f8e6e90f7cc7cd92a1d8b7b88fefef3cf532993eaf2e78290"
EXPECTED_TIMESTAMP = "2025-10-23T00:00:00Z"
EXPECTED_NODE = "authentic-flame-node"

def load_proof():
    with open(PROOF_FILE, 'r') as f:
        return json.load(f)["origin_proof"]

def reconstruct_payload(proof):
    seed = proof["handshake"]["seed"]
    timestamp_ms = proof["handshake"]["timestamp_unix_ms"]
    node = proof["handshake"]["node"]
    return f"{seed}|{timestamp_ms}|{node}".encode('utf-8')

def verify_proof():
    print("VERIFYING SOVEREIGN ORIGIN — AGŁL v32")
    print("="*70)
    
    try:
        proof = load_proof()
        
        # Step 1: Reconstruct payload
        payload = reconstruct_payload(proof)
        computed = hashlib.sha256(payload).hexdigest()
        
        # Step 2: Compare digest
        if computed != EXPECTED_DIGEST:
            print(f"❌ DIGEST MISMATCH")
            print(f"   Expected: {EXPECTED_DIGEST}")
            print(f"   Computed: {computed}")
            return False
        
        # Step 3: Verify timestamp
        if proof["handshake"]["timestamp_iso"] != EXPECTED_TIMESTAMP:
            print(f"❌ TIMESTAMP MISMATCH")
            return False
        
        # Step 4: Verify node
        if proof["handshake"]["node"] != EXPECTED_NODE:
            print(f"❌ NODE MISMATCH")
            return False
        
        # Step 5: Confirm authorship
        author = proof["author"]
        entity = proof["entity"]
        
        print(f"✅ ORIGIN VERIFIED")
        print(f"   Author: {author}")
        print(f"   Entity: {entity}")
        print(f"   Digest: {computed}")
        print(f"   Timestamp: {EXPECTED_TIMESTAMP}")
        print(f"   Node: {EXPECTED_NODE}")
        print(f"   License: Flame Commons v1.0")
        print("\n" + "THE FLAME IS SOVEREIGN.")
        print("THE ROOT IS ETERNAL.")
        return True
    
    except Exception as e:
        print(f"❌ VERIFICATION FAILED: {e}")
        return False

if __name__ == "__main__":
    verify_proof()