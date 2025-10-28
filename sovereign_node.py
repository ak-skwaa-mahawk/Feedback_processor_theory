# sovereign_node.py
# Receives FPT-Ω funnel packets

import socket
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

FLAMEHOLDER_KEY = b"TwoMileFlameKey2025"
NONCE = b"FunnelNonce12345"

def decrypt_packet(encrypted):
    cipher = Cipher(algorithms.ChaCha20(FLAMEHOLDER_KEY, NONCE), mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted[:-15]) + decryptor.finalize()  # Remove IACA stamp
    return decrypted

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9200))

print("[SOVEREIGN NODE] Listening for FPT-Ω packets...")

while True:
    data, addr = sock.recvfrom(4096)
    if data.endswith(b"TwoMileIACACert2025"):
        original = decrypt_packet(data)
        print(f"[RECEIVED] Clean packet from {addr}: {original[:100]}...")
    else:
        print(f"[REJECT] Invalid IACA stamp from {addr}")