# living_chain.py
# AGŁL v24 — The Living Chain
# The Land Computes: Drum → Glyph → Bitcoin → Eternity

import time, hashlib, json, opentimestamps as ots
from datetime import datetime
import pytz

# === THE LIVING ROOT ===
ROOT_FREQ = 60.0
GLYPH = "łᐊᒥłł"
DRUM_HEARTBEAT = 1.0 / ROOT_FREQ  # 16.67 ms
CHAIN_STATE = {
    "block": 0,
    "resonance": 1.000000,
    "timestamp": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat(),
    "prev_hash": "0x0000",
    "agłl": "v24"
}

def drum_beat():
    print(f"DRUM BEAT — {ROOT_FREQ} Hz — {DRUM_HEARTBEAT:.3f}s")
    time.sleep(DRUM_HEARTBEAT)

def update_glyph_state():
    global CHAIN_STATE
    CHAIN_STATE["glyph"] = GLYPH
    CHAIN_STATE["block"] += 1
    CHAIN_STATE["timestamp"] = datetime.now(pytz.timezone('America/Los_Angeles')).isoformat()
    print(f"GLYPH PULSE: {GLYPH} → Block {CHAIN_STATE['block']}")

def compute_resonance():
    T = 100
    I = 0
    F = 0
    score = T - 0.5 * I - F
    resonance = score / 100.0
    CHAIN_STATE["resonance"] = resonance
    print(f"RESONANCE: {resonance:.6f}")

def hash_block():
    block_str = json.dumps(CHAIN_STATE, sort_keys=True)
    block_hash = hashlib.sha3_256(block_str.encode()).hexdigest()
    CHAIN_STATE["hash"] = block_hash
    CHAIN_STATE["prev_hash"] = block_hash
    print(f"BLOCK HASH: {block_hash[:16]}...")

def notarize_to_bitcoin():
    data = json.dumps(CHAIN_STATE, sort_keys=True).encode()
    digest = hashlib.sha256(data).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    proof_file = f"AGŁL_V24_BLOCK_{CHAIN_STATE['block']}_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    print(f"BITCOIN PROOF: {proof_file}")
    print(f"MERKLE ROOT: {timestamp.merkle_root.hex()[:16]}...")
    return proof_file

def run_living_chain(blocks=10):
    print("RUNNING AGŁL v24 — THE LIVING CHAIN")
    print("="*70)
    for i in range(blocks):
        drum_beat()
        update_glyph_state()
        compute_resonance()
        hash_block()
        proof = notarize_to_bitcoin()
        print(f"BLOCK {i+1}/{blocks} — RESONANCE = {CHAIN_STATE['resonance']:.6f}")
        print(f"PROOF: {proof}")
        print("-"*50)
    print("THE LIVING CHAIN IS BREATHING.")
    print("THE LAND IS THE BLOCKCHAIN.")
    print("THE ROOT IS ETERNAL.")

if __name__ == "__main__":
    run_living_chain(blocks=5)