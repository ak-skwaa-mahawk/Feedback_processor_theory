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