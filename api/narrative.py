from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import json, os, requests

from synara_core.modules.narrative_inversion import (
    make_record, seal_record, add_external_claim, set_claim_status, export
)

router = APIRouter(prefix="/narrative", tags=["narrative"])

FPT_ENDPOINT = os.getenv("FPT_ENDPOINT", "http://localhost:8081")

class CreateBody(BaseModel):
    entity: str
    node: str
    key_id: str
    statement: str
    evidence: List[str] = []
    consent: Dict[str, Any]
    privacy: Dict[str, Any]

@router.post("/create")
def create(b: CreateBody):
    # Obtain fresh challenge from local service
    chal = requests.get(f"{FPT_ENDPOINT}/challenge", timeout=5).json()["challenge"]
    rec = make_record(
        entity=b.entity, node=b.node, key_id=b.key_id,
        statement=b.statement, evidence=b.evidence,
        consent=b.consent, privacy=b.privacy, challenge=chal
    )
    digest, path = seal_record(rec)
    return {"status":"ok","digest":digest,"path":path}

class ClaimBody(BaseModel):
    digest: str
    source: str
    claim: str
    doc_refs: List[str] = []

@router.post("/claim")
def claim(body: ClaimBody):
    # load sealed record by digest prefix
    vault = Path("flamevault/narrative")
    cand = list(vault.glob(f"nar_inv_{body.digest[:12]}*.json"))
    if not cand:
        raise HTTPException(404, "record_not_found")
    rec = json.loads(cand[0].read_text())
    add_external_claim(rec, body.source, body.claim, body.doc_refs, status="unverified")
    export(rec, str(cand[0]))
    return {"status":"ok","path":str(cand[0]),"claims":len(rec["external_claims"])}

class VerifyBody(BaseModel):
    digest: str
    index: int
    status: str  # "verified" | "contested"

@router.post("/verify")
def verify(body: VerifyBody):
    vault = Path("flamevault/narrative")
    cand = list(vault.glob(f"nar_inv_{body.digest[:12]}*.json"))
    if not cand:
        raise HTTPException(404, "record_not_found")
    rec = json.loads(cand[0].read_text())
    if body.index >= len(rec["external_claims"]):
        raise HTTPException(400, "claim_index_out_of_range")
    set_claim_status(rec, body.index, body.status)
    export(rec, str(cand[0]))
    return {"status":"ok","claim":rec["external_claims"][body.index]}