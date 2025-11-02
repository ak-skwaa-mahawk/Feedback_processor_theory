# Self-embed + vector index (FAISS if available, else SQLite cosine fallback)
from __future__ import annotations
import os, json, sqlite3, math, hashlib, threading
from pathlib import Path
from typing import List, Dict, Any, Tuple

# --- Config ---
EMBED_DIR = Path(os.getenv("EMBED_DIR", "data/embeds"))
EMBED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = EMBED_DIR / "index.sqlite"

# Backend selection:
# 1) sentence-transformers (MiniLM) if installed
# 2) huggingface "gte-small" via sentence_transformers (if available)
# 3) deterministic hashing fallback (bag-of-words) – low quality but zero deps
_backend_lock = threading.Lock()
_model = None

def _load_backend():
    global _model
    if _model is not None:
        return "transformer"

    try:
        from sentence_transformers import SentenceTransformer
        name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        _model = SentenceTransformer(name)
        return "transformer"
    except Exception:
        return "hash"

def _embed_texts(texts: List[str]) -> List[List[float]]:
    backend = _load_backend()
    if backend == "transformer":
        # noinspection PyUnresolvedReferences
        return _model.encode(texts, normalize_embeddings=True).tolist()
    # Fallback: hashed bag-of-words → 768 dims deterministic
    import random
    random.seed(907)
    dims = 384
    vecs = []
    for t in texts:
        v = [0.0]*dims
        for tok in (t.lower().split()):
            h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
            i = h % dims
            s = -1.0 if (h >> 1) & 1 else 1.0
            v[i] += s
        # L2 normalize
        norm = math.sqrt(sum(x*x for x in v)) or 1.0
        vecs.append([x/norm for x in v])
    return vecs

# --- Storage (SQLite) ---
def _init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            kind TEXT,
            file TEXT,
            digest TEXT,
            title TEXT,
            snippet TEXT,
            meta_json TEXT
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            id TEXT PRIMARY KEY,
            dim INTEGER,
            data BLOB
        );
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_items_digest ON items(digest);")
    conn.commit()
    conn.close()

_init_db()

def _to_blob(vec: List[float]) -> bytes:
    import array
    arr = array.array('f', vec)
    return arr.tobytes()

def _from_blob(b: bytes) -> List[float]:
    import array
    arr = array.array('f')
    arr.frombytes(b)
    # In case of endianness differences
    if arr.itemsize != 4:
        arr = array.array('f', arr.tolist())
    return list(arr)

def upsert_embedding(*, uid: str, kind: str, file: str, digest: str,
                     title: str, snippet: str, meta: Dict[str, Any],
                     text_for_embed: str):
    """Create/update embedding + metadata for an item."""
    vec = _embed_texts([text_for_embed])[0]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO items(id,kind,file,digest,title,snippet,meta_json)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          kind=excluded.kind, file=excluded.file, digest=excluded.digest,
          title=excluded.title, snippet=excluded.snippet, meta_json=excluded.meta_json
    """, (uid, kind, file, digest, title[:256], snippet[:512], json.dumps(meta, ensure_ascii=False)))
    c.execute("""
        INSERT INTO vectors(id,dim,data) VALUES(?,?,?)
        ON CONFLICT(id) DO UPDATE SET dim=excluded.dim, data=excluded.data
    """, (uid, len(vec), _to_blob(vec)))
    conn.commit()
    conn.close()

def _cos_sim(a: List[float], b: List[float]) -> float:
    s = sum(x*y for x,y in zip(a,b))
    # both are normalized already; return s
    return float(s)

def search(query: str, top_k: int = 8, filter_digest: str | None = None) -> List[Dict[str, Any]]:
    """Semantic search over self-embedded corpus."""
    qv = _embed_texts([query])[0]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if filter_digest:
        c.execute("SELECT i.id,i.kind,i.file,i.digest,i.title,i.snippet,i.meta_json,v.dim,v.data "
                  "FROM items i JOIN vectors v ON i.id=v.id WHERE i.digest=?", (filter_digest,))
    else:
        c.execute("SELECT i.id,i.kind,i.file,i.digest,i.title,i.snippet,i.meta_json,v.dim,v.data "
                  "FROM items i JOIN vectors v ON i.id=v.id")
    rows = c.fetchall()
    conn.close()

    scored = []
    for rid, kind, file, dig, title, snip, meta_json, dim, blob in rows:
        vec = _from_blob(blob)
        sim = _cos_sim(qv, vec)
        scored.append((sim, {
            "id": rid, "kind": kind, "file": file, "digest": dig,
            "title": title, "snippet": snip, "meta": json.loads(meta_json or "{}")
        }))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [dict(score=round(s,4), **item) for s,item in scored[:top_k]]

# --- Public bump API ---
def bump_codex_entry(*, entry: Dict[str, Any], file_path: str,
                     reason: str, actor: str, scope: str):
    """Embed a Codex/theory entry when it is 'bumped' by important activity."""
    title = entry.get("title") or entry.get("content", {}).get("title") or Path(file_path).stem
    digest = entry.get("flame_signature") or entry.get("sha256_digest") or entry.get("handshake_id") or "0x"
    text = json.dumps(entry, ensure_ascii=False)
    snippet = (entry.get("echo_phrase") or "") + " " + (entry.get("org") or "") + " " + text[:400]
    uid = hashlib.sha256(f"{file_path}::{digest}".encode()).hexdigest()[:24]
    meta = {
        "reason": reason, "actor": actor, "scope": scope, "bumped_at": __import__("time").time()
    }
    upsert_embedding(
        uid=uid, kind="codex", file=file_path, digest=digest,
        title=title, snippet=snippet, meta=meta, text_for_embed=text
    )
    return {"status": "embedded", "id": uid, "digest": digest}