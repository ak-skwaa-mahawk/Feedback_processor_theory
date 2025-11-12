# ... existing imports ...
from fastapi import FastAPI, HTTPException, Request
from backend.config import WHISPER_HARDENING_ENABLED
from backend.security.stream_shield import StreamShieldMiddleware
from backend.security.ratelimit import allow

# existing: app = FastAPI(...)
app = FastAPI(title="Whisper Synara Handshake", version=VERSION)

if WHISPER_HARDENING_ENABLED:
    app.add_middleware(StreamShieldMiddleware)

# --- existing endpoints ---

@app.get("/health")
def health():
    return {"ok": True, "version": VERSION}

@app.get("/challenge")
def challenge(prefix: str = "whisper", request: Request = None):
    ip = request.client.host if request and request.client else "unknown"
    if not allow(ip, "/challenge"):
        raise HTTPException(status_code=429, detail="rate_limited")
    chal = server_mk_challenge(prefix=prefix)
    return {"challenge": chal, "version": VERSION}

@app.post("/verify")
async def verify(req: VerifyRequest, request: Request):
    ip = request.client.host if request and request.client else "unknown"
    if not allow(ip, "/verify"):
        raise HTTPException(status_code=429, detail="rate_limited")

    if request.headers.get("content-length"):
        if int(request.headers["content-length"]) > 4096:
            raise HTTPException(status_code=413, detail="Payload too large")

    ok, reason = server_verify(req.receipt, expected_challenge=req.expected_challenge)
    if not ok:
        raise HTTPException(status_code=401, detail=reason)

    return {
        "status": "ok",
        "version": VERSION,
        "reason": reason,
        "kid": str(req.receipt.get("key_id", "")),
        "aud": str(req.receipt.get("aud", "-")),
        "scope": str(req.receipt.get("scope", "-")),
        "receipt_compact": to_compact_json({k:v for k,v in req.receipt.items() if k != "sig"}),
    }