import time, socket, hashlib, json, os, threading

_DEFAULT_LOG = "logs/handshake_log.json"
_LOCK = threading.Lock()

def handshake_message(seed: str, entity: str = "TwoMileSolutionsLLC", version: str = "1.1", log_file: str = _DEFAULT_LOG):
    ts_unix = str(int(time.time() * 1000))
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hostname = socket.gethostname()
    payload = f"{entity}|{seed.strip()}|{ts_unix}|{hostname}"
    digest = hashlib.sha256(payload.encode()).hexdigest()
    receipt = {
        "entity": entity, "version": version,
        "timestamp_unix_ms": ts_unix, "timestamp_iso": ts_iso,
        "seed": seed.strip(), "digest": digest, "node": hostname
    }
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    with _LOCK:
        exists = os.path.isfile(log_file)
        with open(log_file, "a" if exists else "w", encoding="utf-8") as f:
            if exists: f.write("\n")
            f.write(json.dumps(receipt, ensure_ascii=False))
    return receipt

def verify_handshake(receipt: dict, seed: str | None = None, entity: str | None = None) -> bool:
    try:
        payload = f"{receipt['entity']}|{receipt['seed']}|{receipt['timestamp_unix_ms']}|{receipt['node']}"
        digest = hashlib.sha256(payload.encode()).hexdigest()
        ok = (digest == receipt.get("digest"))
        if seed is not None: ok = ok and (receipt.get("seed") == seed.strip())
        if entity is not None: ok = ok and (receipt.get("entity") == entity)
        return ok
    except Exception:
        return False