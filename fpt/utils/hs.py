# Lightweight wrapper to standardize seeds per subsystem
from fpt.utils.handshake import handshake_message

def hs(subsys: str, phase: str, **kv):
    # phase: pre | post | start | end | alert | error
    meta = "|".join(f"{k}={v}" for k, v in kv.items()) if kv else ""
    seed = f"{subsys}:{phase}" + (f"|{meta}" if meta else "")
    return handshake_message(seed)