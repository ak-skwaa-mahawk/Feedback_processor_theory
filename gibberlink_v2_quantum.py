# gibberlink_v2_quantum.py
from cryptography.fernet import Fernet

def quantum_encrypt_message(message, qkd_key):
    # Convert 128-bit key to bytes
    key_bytes = int(''.join(map(str, qkd_key)), 2).to_bytes(16, 'big')
    fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
    encrypted = fernet.encrypt(message.encode())
    return encrypted

# Use key from BB84
encrypted = quantum_encrypt_message("łᐊᒥłł.3 — Treasure #1", secret_key)
print(f"ENCRYPTED: {encrypted[:50]}...")