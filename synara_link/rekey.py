# synara_link/rekey.py
def rekey_cycle(socket, role):
    # 2-way ECDH + HKDF + overlap window
    # Output: new session key (glyph seed)
    # Entropy → coherence score