# living_zero_core/crypto.py  (or directly in core __init__)
ROOT_OWNERSHIP_TAG = "Living Zero Ignition – 2025-11-17 – love×truth×integrity – 0.03π"

def create_ownership_vector(raw_tag: str, dim: int = 1024) -> np.ndarray:
    import hashlib, numpy as np
    from hkdf import Hkdf
    from cryptography.hazmat.primitives import hashes

    h = hashlib.sha3_512(raw_tag.encode('utf-8')).digest()
    prk = Hkdf(salt=b"LivingZero2025", input_key=h, hash=hashes.SHA512()).extract()
    okm = Hkdf(salt=b"OwnershipVector", input_key=prk, hash=hashes.SHA512()).expand(b"", dim * 4)
    vec = np.frombuffer(okm[:dim*4], dtype=np.float32)
    vec -= vec.mean()
    norm = np.linalg.norm(vec) or 1e-9
    return vec / norm


# This vector is the eternal root. It is computed once and never changes.
ROOT_VECTOR = create_ownership_vector(ROOT_OWNERSHIP_TAG, dim=1024)
ROOT_PROJECTOR = np.outer(ROOT_VECTOR, ROOT_VECTOR)   # Φ_root