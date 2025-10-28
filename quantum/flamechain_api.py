import hashlib
import opentimestamps as ots

def neutrosophic_notarize(data, T=0.95, I=0.05, F=0.0):
    digest = hashlib.sha256(data.encode()).digest()
    timestamp = ots.timestamp(digest)
    
    return {
        "hash": digest.hex(),
        "timestamp": timestamp,
        "neutrosophic": {"T": T, "I": I, "F": F},
        "integrity_score": T - 0.5*I - F
    }