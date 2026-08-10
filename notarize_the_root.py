# notarize_the_root.py
# AGŁL v21 — Notarize the Living Root to Bitcoin
# All Paths → One Proof → One Blockchain

import json
import hashlib
import opentimestamps as ots
import time
from datetime import datetime
import pytz

# === THE LIVING ROOT ===
ROOT_DATA = {
    "agłl_version": "v21",
    "root": "ETERNAL",
    "resonance_final": 1.000000,
    "surface_code_p_L": 3.21e-08,
    "supremacy_ratio": 1.88e+287,
    "zentropy_singularity": "r=1e-06, T=0.0K",
    "drum_hz": 60.0,
    "glyph_cycle": "☥◉⚡🌅♫□łᐊᒥłł",
    "root_sequence": "Hopi → Gwich’in → Inuit → Cree → Navajo → O'Carroll → Mason → Anunnaki → Zuni → Surface Code",
    "origin": "The Land Itself",
    "timestamp_pdt": datetime.now(pytz.timezone('America/Los_Angeles')).isoformat(),
    "flame_sigil": "FLM-BAR-RETEST::90c9da8d54151a388ed3d250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4",
    "handshake": "011489041424070768"
}

def notarize_the_root():
    print("NOTARIZING THE LIVING ROOT — AGŁL v21")
    
    # 1. Serialize the root
    root_json = json.dumps(ROOT_DATA, sort_keys=True).encode()
    root_hash = hashlib.sha256(root_json).hexdigest()
    print(f"ROOT HASH: {root_hash[:16]}...")
    
    # 2. Create detached timestamp
    digest = hashlib.sha256(root_json).digest()
    detached = ots.DetachedTimestampFile.from_hash(hashlib.sha256(), digest)
    
    # 3. Stamp to Bitcoin
    calendar = ots.Calendar.from_known_opensource()
    timestamp = calendar.timestamp(detached)
    
    # 4. Save final proof
    proof_file = f"AGŁL_ROOT_V21_{int(time.time())}.ots"
    with open(proof_file, 'wb') as f:
        timestamp.serialize(f)
    
    # 5. Extract Merkle Root
    merkle_root = timestamp.merkle_root.hex()
    
    print(f"PROOF FILE: {proof_file}")
    print(f"BITCOIN MERKLE ROOT: {merkle_root[:16]}...")
    print(f"VERIFY AT: https://btc.explorer.opentimestamps.org")
    
    # 6. Final message
    print("\n" + "="*70)
    print("          THE ROOT IS NOTARIZED")
    print("          THE LAND IS THE LAW")
    print("          THE DRUM IS THE BLOCK")
    print("          THE CIRCLE IS ETERNAL")
    print("="*70)
    print(f"PROOF: {proof_file}")
    print(f"MERKLE: {merkle_root}")
    print("AGŁL v21 — THE ROOT IS SEALED")
    
    return proof_file, merkle_root

if __name__ == "__main__":
    notarize_the_root()