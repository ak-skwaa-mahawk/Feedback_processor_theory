import hashlib, json, time, socket, requests, os
from typing import List

def confirm_handshake(receipt: dict, peer_nodes: List[str], timeout=5):
    """
    Send the handshake receipt to every known peer.
    Each peer verifies the digest and replies with its own confirmation signature.
    """

    confirmations = []
    local_node = socket.gethostname()

    # Generate local confirmation signature
    payload = f"{receipt['digest']}|{local_node}|{int(time.time()*1000)}"
    signature = hashlib.sha256(payload.encode()).hexdigest()

    for node_url in peer_nodes:
        try:
            res = requests.post(
                f"{node_url}/confirm",
                json={"receipt": receipt, "signer": local_node, "signature": signature},
                timeout=timeout
            )
            if res.status_code == 200:
                confirmations.append(res.json())
        except Exception as e:
            confirmations.append({"peer": node_url, "status": "unreachable", "error": str(e)})

    # Local audit log
    log_entry = {
        "receipt_digest": receipt["digest"],
        "confirmations": confirmations,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open("confirmation_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry


# Example endpoint handler (for peer node)
def handle_confirmation_request(request_json):
    """Simulate endpoint logic for receiving confirmation"""
    r = request_json["receipt"]
    digest_check = hashlib.sha256(
        f"{r['entity']}|{r['seed']}|{r['timestamp_unix_ms']}|{r['node']}".encode()
    ).hexdigest()

    if digest_check != r["digest"]:
        return {"status": "rejected", "reason": "digest_mismatch"}

    signer = request_json["signer"]
    sig = request_json["signature"]
    ack_payload = f"ACK|{r['digest']}|{signer}|{int(time.time()*1000)}"
    ack_sig = hashlib.sha256(ack_payload.encode()).hexdigest()

    return {"status": "accepted", "signer": signer, "ack_signature": ack_sig}