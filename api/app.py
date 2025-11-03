from api.tunnel import router as tunnel_router
app.include_router(tunnel_router)
# api/app.py (or your main service)
from fastapi import FastAPI
from api.tunnel import router as tunnel_router
# ... existing imports/routers ...
app = FastAPI(title="Resonance Mesh API", version="1.0")
app.include_router(tunnel_router, prefix="/tunnel")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.arc import router as arc_router

# NEW: rate limiter
from slowapi.middleware import SlowAPIMiddleware
from api.ratelimit import limiter, rate_limit_handler, RateLimitExceeded

app = FastAPI(title="Resonance Mesh API", version="1.0")

# Optional, restrict in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# NEW: SlowAPI middleware + exception handler
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.get("/health")
def health():
    return {"ok": True, "service": "resonance-mesh"}

app.include_router(arc_router, prefix="/arc")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.arc import router as arc_router

app = FastAPI(title="Resonance Mesh API", version="1.0")

# Optional, restrict in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "service": "resonance-mesh"}

app.include_router(arc_router, prefix="/arc")