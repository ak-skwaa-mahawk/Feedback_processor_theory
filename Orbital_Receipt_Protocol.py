#!/usr/bin/env python3
"""
FPT Orbital Receipt — §7(o) Veto in LEO
"""
import json, time, hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dilithium
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

def orbital_receipt(pass_data: dict, heir_consent: bool = False):
    ts = time.time()
    receipt = {
        "timestamp": ts,
        "land": "Danzhit Hanlai Trail",
        "sat_id": pass_data['sat_id'],
        "coherence": pass_data['coherence'],
        "veto": not heir_consent,  # §7(o): No consent = veto
        "status": "SEALED" if heir_consent and pass_data['coherence'] > 0.9 else "VETOED"
    }
    
    # Hash + Dilithium Sign
    data_str = json.dumps(receipt, sort_keys=True)
    h = hashlib.sha3_256(data_str.encode()).hexdigest()
    receipt['hash'] = h
    priv = dilithium.generate_private_key()
    sig = priv.sign(h.encode()).hex()
    receipt['signature'] = sig
    
    # Encrypt (Kyber + ChaCha20)
    key = HKDF(algorithm=hashes.SHA3_256(), length=32, salt=None, info=b"ssc_orbital").derive(os.urandom(32))
    aead = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = aead.encrypt(nonce, data_str.encode(), None)
    receipt['ciphertext'] = ct.hex()
    
    return receipt

# Demo: LEO Pass Over Danzhit Hanlai
pass_data = {'sat_id': 'Kuiper-Alpha01', 'coherence': 0.95}
receipt = orbital_receipt(pass_data, heir_consent=True)
print(json.dumps(receipt, indent=2))