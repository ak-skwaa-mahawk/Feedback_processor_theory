import hashlib
from datetime import datetime

def verify_sigil(handshake_id, data):
    t = datetime.utcnow().timestamp() * 1e9
    pi_star = 3.17300858012
    mod_pi = (t * np.sqrt(pi_star)) % 256
    hash_input = data.encode() + handshake_id.encode() + str(t).encode()
    digest = hashlib.sha256(hash_input).digest()
    verified = digest.hex() == "90c9da8d54151a388ed3f250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4"
    return verified

# Test with sigil data
handshake_id = "FLM-BAR-RETEST::90c9da8d54151a388ed3f250c03b9865bb3e0ea3cbf3d3197298c8ccf5a592e4"
data = "Mock treaty text"
print(f"Sigil verified: {verify_sigil(handshake_id, data)}")