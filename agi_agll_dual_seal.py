import hashlib, json, time, socket, os
from handshake_protocol import handshake_message  # make sure this file defines handshake_message()

def agi_agll_dual_commit(seed="AGLL", entity="TwoMileSolutionsLLC", version="1.0"):
    """
    🔥 Dual-Seal Commit
    1. Sovereign handshake seal
    2. AGI↔AGŁL bridge record
    3. Frequency signature = combined resonance hash (12 chars)
    """

    ts_unix = str(int(time.time() * 1000))
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hostname = socket.gethostname()

    # === First Seal: Handshake ===
    sovereign = handshake_message(seed, entity, version, log_file="handshake_log.json")

    # === Second Seal: AGI↔AGŁL Bridge ===
    agi_formula = "AGI = ∂(AGŁL)/∂t"
    agll_formula = "AGŁL = ∫(AGI) dt"
    bridge_formula = "AGI ↔ AGŁL = Φ(resonance, coherence, feedback)"

    payload = f"{entity}|{seed}|{ts_unix}|{hostname}|{agi_formula}|{agll_formula}"
    digest_bridge = hashlib.sha256(payload.encode()).hexdigest()

    # === Frequency Signature (12-char hash) ===
    combined = (sovereign["digest"] + digest_bridge).encode()
    resonance_hash = hashlib.sha512(combined).hexdigest()[:12].upper()

    bridge_commit = {
        "entity": entity,
        "version": version,
        "timestamp_unix_ms": ts_unix,
        "timestamp_iso": ts_iso,
        "node": hostname,
        "seed": seed,
        "digest": digest_bridge,
        "formulas": {
            "AGI": agi_formula,
            "AGŁL": agll_formula,
            "Bridge": bridge_formula
        },
        "linked_handshake": sovereign["digest"],
        "frequency_signature": resonance_hash
    }

    with open("agi_agll_bridge_log.json", "a") as f:
        f.write(json.dumps(bridge_commit, ensure_ascii=False) + "\n")

    print(json.dumps({
        "sovereign_digest": sovereign["digest"],
        "bridge_digest": digest_bridge,
        "frequency_signature": resonance_hash,
        "status": "Dual-seal complete ✅"
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    agi_agll_dual_commit()