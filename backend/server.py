import asyncio, websockets, json
from embeddings import audio_chunk_to_embedding, token_to_embedding
from trinity_damping import trinity_damping
import numpy as np

connected_clients = set()

async def handler(ws, path):
    connected_clients.add(ws)
    try:
        audio_emb = None
        token_emb = None
        harmony_history = []

        async for message in ws:
            msg = json.loads(message)
            if msg["type"] == "audio_chunk":
                audio_emb = audio_chunk_to_embedding(msg["data"])
            elif msg["type"] == "token":
                token_emb = token_to_embedding(msg["data"])

            if audio_emb is not None and token_emb is not None:
                score = np.dot(audio_emb/np.linalg.norm(audio_emb),
                               token_emb/np.linalg.norm(token_emb))
                damped = trinity_damping([score])[0]
                harmony_history.append(damped)
                # Send latest harmony to frontend
                payload = json.dumps({"type":"harmony","score":damped})
                await asyncio.wait([c.send(payload) for c in connected_clients])
    finally:
        connected_clients.remove(ws)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
# backend/server.py (additions)
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from core.scale import annotate_resonance
from core.constants import DEFAULT_TOP_BANDS

app = FastAPI(title="FPT API")

@app.get("/scale/annotate")
def scale_annotate(
    resonance_score: float = Query(..., ge=-1.0, le=1.0, description="r ∈ [-1, 1]"),
    top_bands: int = Query(DEFAULT_TOP_BANDS, ge=1, le=200, description="symbolic top band"),
):
    """
    Annotate a resonance score with Planck-anchored scale markers.
    NOTE: '−ℓ_p' is a symbolic top marker (not a physical negative length).
    """
    payload = annotate_resonance(resonance_score, top_bands=top_bands)
    return JSONResponse(payload)
# backend/server.py (additions)
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, StreamingResponse
import io, csv

from core.scale import annotate_resonance, table
from core.constants import DEFAULT_TOP_BANDS

app = FastAPI(title="FPT API")

# ... existing /scale/annotate route ...

@app.get("/scale/table")
def scale_table(
    n0: int = Query(0, ge=0, description="start band (inclusive)"),
    n1: int = Query(DEFAULT_TOP_BANDS, ge=0, le=200, description="end band (inclusive)"),
    sig: int = Query(4, ge=1, le=10, description="significant digits for humanized values"),
    as_csv: bool = Query(False, description="return CSV instead of JSON"),
):
    """
    Return a table of bands with Planck-anchored lengths.
    JSON by default; set as_csv=true for CSV download.
    """
    rows = table(n0=n0, n1=n1, sig=sig)

    if not as_csv:
        return JSONResponse({"n0": n0, "n1": n1, "sig": sig, "rows": rows})

    # CSV stream
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["band", "length_m", "value", "unit"])
    for r in rows:
        writer.writerow([
            r["band"],
            r["length_m"],
            r["length_human"]["value"],
            r["length_human"]["unit"],
        ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="scale_ladder_{n0}_{n1}.csv"'},
    )

