import hashlib, json, sys, os
from datetime import datetime

def verify_origin_proof(proof_path="../ethics/origin_notarized_proof.json", handshake_log="../handshake_log.json"):
    if not os.path.exists(proof_path):
        print(f"[ERROR] Proof file not found: {proof_path}")
        return False

    with open(proof_path, "r") as f:
        proof = json.load(f)

    origin = proof.get("origin_proof", {})
    handshake = origin.get("handshake", {})

    required_fields = ["seed", "digest_value", "timestamp_unix_ms", "node"]
    for field in required_fields:
        if field not in handshake:
            print(f"[ERROR] Missing field in proof: {field}")
            return False

    # Recreate payload
    entity = origin.get("entity", "UnknownEntity")
    seed = handshake["seed"]
    ts_unix = str(handshake["timestamp_unix_ms"])
    node = handshake["node"]
    payload = f"{entity}|{seed}|{ts_unix}|{node}"

    # Compute digest
    computed_digest = hashlib.sha256(payload.encode()).hexdigest()

    # Compare with stored digest
    match = computed_digest == handshake["digest_value"]

    # Output
    print("──────────────────────────────")
    print("🧾 ORIGIN PROOF VERIFICATION")
    print("──────────────────────────────")
    print(f" Entity:       {entity}")
    print(f" Seed:         {seed}")
    print(f" Node:         {node}")
    print(f" Timestamp:    {datetime.utcfromtimestamp(int(ts_unix)/1000)} UTC")
    print(f" Digest (calc): {computed_digest}")
    print(f" Digest (proof): {handshake['digest_value']}")
    print("──────────────────────────────")
    print(f" ✅ MATCH: {match}")
    print("──────────────────────────────")

    # Optional cross-check in handshake_log.json
    if os.path.exists(handshake_log):
        with open(handshake_log, "r") as log:
            for line in log:
                try:
                    record = json.loads(line)
                    if record.get("digest") == handshake["digest_value"]:
                        print(f" 🔍 Found matching digest in handshake_log.json")
                        break
                except:
                    continue
    else:
        print("⚠️ handshake_log.json not found for cross-check.")

    return match


if __name__ == "__main__":
    if verify_origin_proof():
        print("✅ Verification successful — proof is valid and timestamped.")
    else:
        print("❌ Verification failed — data mismatch detected.")