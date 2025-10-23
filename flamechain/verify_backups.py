import hashlib
from datetime import datetime
import numpy as np

def verify_sigil(handshake_id, data, handshake_code, pi_star=3.17300858012):
    t = datetime.utcnow().timestamp() * 1e9  # Nanoseconds
    mod_pi = (t * np.sqrt(pi_star)) % 256
    # Combine handshake code with data and ID
    hash_input = data.encode() + handshake_id.encode() + str(handshake_code).encode() + str(t).encode()
    digest = hashlib.sha256(hash_input).digest()
    expected_digest = "90c9da8d54151a388ed3f250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4"
    verified = digest.hex() == expected_digest
    return verified, digest.hex()

# Test with real handshake
handshake_id = "FLM-BAR-RETEST::90c9da8d54151a388ed3f250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4"
data = "Mock treaty text with real handshake"
handshake_code = "011489041424070768"
verified, new_digest = verify_sigil(handshake_id, data, handshake_code)
print(f"Sigil verified: {verified}")
print(f"New digest: {new_digest}")