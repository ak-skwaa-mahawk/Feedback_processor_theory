import time, socket, hashlib, json, os

def handshake_message(seed: str,
                      entity: str = "TwoMileSolutionsLLC",
                      version: str = "1.2",
                      log_file: str = "handshake_log.jsonl"):
    """
    Generates a chain-linked sovereign handshake for node and entity verification.
    Each entry includes a cryptographic digest of the previous entry to form a
    verifiable chronological chain.
    
    Args:
        seed (str): Context string or transaction key.
        entity (str): Entity or system name.
        version (str): Protocol version tag.
        log_file (str): Path to append JSON logs (one JSON per line).
    
    Returns:
        dict: The full handshake receipt with chain digest.
    """
    ts_unix = str(int(time.time() * 1000))
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hostname = socket.gethostname()

    # Load last digest if exists
    prev_digest = None
    if os.path.isfile(log_file):
        try:
            with open(log_file, "rb") as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
                prev_entry = json.loads(last_line)
                prev_digest = prev_entry.get("chain_digest") or prev_entry.get("digest")
        except Exception:
            prev_digest = None

    # Build payload
    payload_parts = [entity, seed.strip(), ts_unix, hostname]
    if prev_digest:
        payload_parts.append(prev_digest)
    payload = "|".join(payload_parts)

    # Cryptographic seal
    digest = hashlib.sha256(payload.encode()).hexdigest()
    chain_digest = hashlib.sha256((digest + (prev_digest or "")).encode()).hexdigest()

    # Sovereign receipt
    receipt = {
        "entity": entity,
        "version": version,
        "timestamp_unix_ms": ts_unix,
        "timestamp_iso": ts_iso,
        "seed": seed.strip(),
        "digest": digest,
        "chain_digest": chain_digest,
        "previous_digest": prev_digest,
        "node": hostname
    }

    # Append to ledger
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(receipt) + "\n")
    except Exception as e:
        print(f"⚠️ Failed to write handshake log: {e}")

    return receipt