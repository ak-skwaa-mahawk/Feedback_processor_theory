def verify_handshake_chain(log_file="handshake_log.jsonl"):
    last_digest = None
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line)
            payload_parts = [
                entry["entity"],
                entry["seed"],
                entry["timestamp_unix_ms"],
                entry["node"]
            ]
            if entry["previous_digest"]:
                payload_parts.append(entry["previous_digest"])
            recomputed_digest = hashlib.sha256("|".join(payload_parts).encode()).hexdigest()
            expected_chain = hashlib.sha256((recomputed_digest + (entry["previous_digest"] or "")).encode()).hexdigest()
            if expected_chain != entry["chain_digest"]:
                return False, entry
            last_digest = entry["chain_digest"]
    return True, last_digest