import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core Routing Architecture Ingress Ports
from api.arc import router as arc_router
from api.tunnel import router as tunnel_router

# Core Traffic Governance & Security Interceptors
from slowapi.middleware import SlowAPIMiddleware
from api.ratelimit import limiter, rate_limit_handler, RateLimitExceeded

# Initialize a single, consolidated app instance
app = FastAPI(
    title="Resonance Mesh API", 
    version="1.0.0",
    description="Sovereign mesh orchestration substrate gating local hardware, tunneling configurations, and policy matrices."
)

# --- 1. GLOBAL GOVERNANCE MIDDLEWARE PLUMBING ---

# Configure SlowAPI Rate Limiting Interceptors
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Cross-Origin Resource Sharing (CORS) Configuration Parameters
# Highly critical for stabilizing secure Iframe canvas embeddings on portals like Google Sites
PRODUCTION_ORIGINS = [
    "https://sites.google.com",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
]

# Pull environment flag to check if wide-open wildcard CORS debugging matches target configuration
ALLOW_ALL = os.getenv("ENV_MODE", "development") == "development"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if ALLOW_ALL else PRODUCTION_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- 2. BASELINE Telemetry SENSORS ---

@app.get("/health", tags=["Telemetry Monitoring"])
def health_check():
    """
    Empirical trace sensor node tracking connectivity.
    """
    return {
        "ok": True, 
        "service": "resonance-mesh",
        "governance_membrane": "ACTIVE",
        "rate_limiting": "ENFORCED"
    }


# --- 3. PIPELINE GATEWAY ROUTER MOUNTING ---

# Mount the localized Arc configuration controller routes
app.include_router(
    arc_router, 
    prefix="/arc", 
    tags=["Arc Core Logic Layers"]
)

# Mount the asynchronous hardware and remote tunneling layout paths
app.include_router(
    tunnel_router, 
    prefix="/tunnel", 
    tags=["Dynamic Network Tunneling Channels"]
)
