import time, socket, hashlib, json, os

def handshake_message(seed: str, entity: str = "TwoMileSolutionsLLC", version: str = "1.1", log_file="handshake_log.json"):
    """
    Generates a sovereign handshake receipt for node and entity verification.
    
    Args:
        seed (str): Context string or transaction key.
        entity (str): Entity or system name.
        version (str): Protocol version tag.
        log_file (str): Path to append JSON logs.
    
    Returns:
        dict: Receipt containing entity, timestamps, digest, and node ID.
    """
    # High-resolution clock (milliseconds)
    ts_unix = str(int(time.time() * 1000))
    
    # Human-readable ISO-8601 timestamp
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Anchor to local system identity
    hostname = socket.gethostname()
    
    # Combine into a payload string
    payload = f"{entity}|{seed.strip()}|{ts_unix}|{hostname}"
    
    # SHA-256 digest = cryptographic signature
    digest = hashlib.sha256(payload.encode()).hexdigest()
    
    # Sovereign receipt (JSON object)
    receipt = {
        "entity": entity,
        "version": version,
        "timestamp_unix_ms": ts_unix,
        "timestamp_iso": ts_iso,
        "seed": seed.strip(),
        "digest": digest,
        "node": hostname
    }
    
    # Append to rolling ledger
    if log_file:
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(receipt) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write handshake log: {e}")
    
    return receipt