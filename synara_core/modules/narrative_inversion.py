from __future__ import annotations
import json, hashlib, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .whisper_handshake_v13 import client_build_response  # signer
from .seal_sigil_generator import stamp_sigil            # existing seal

VERSION = "1.0"

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def make_record(
    entity: str,
    node: str,
    key_id: str,
    statement: str,
    evidence: List[str],
    consent: Dict[str, Any],
    privacy: Dict[str, Any],
    challenge: str,
    aud: str = "narrative",
    scope: str = "inversion",
) -> Dict[str, Any]:
    receipt = client_build_response(entity, node, key_id, challenge, aud=aud, scope=scope)
    base = {
        "version": VERSION,
        "subject": {"entity": entity, "node": node, "key_id": key_id},
        "self_record": {
            "statement": statement,
            "evidence": evidence,
            "timestamp": _utc(),
        },
        "external_claims": [],
        "provenance": {
            "handshake_id": f"FLM-NAR-INV::{hashlib.sha256(challenge.encode()).hexdigest()}",
            "challenge": challenge,
            "receipt": receipt,
        },
        "consent": consent,
        "privacy": privacy,
        "seals": {"self_hash": "", "self_sig": "", "transparency_log": []},
    }
    return base

def seal_record(rec: Dict[str, Any], out_dir="flamevault/narrative") -> Tuple[str, str]:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    raw = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    rec["seals"]["self_hash"] = f"SHA256:{digest}"
    rec["seals"]["self_sig"]  = stamp_sigil({"digest": digest, "kind":"NarrativeInversion"}, out_dir=out_dir, label=f"nar_inv_{int(time.time())}")
    rec["seals"]["transparency_log"].append({"ts": _utc(), "event":"sealed", "actor": rec["subject"]["entity"]})
    path = Path(out_dir) / f"nar_inv_{digest[:12]}.json"
    path.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return digest, str(path)

def add_external_claim(rec: Dict[str, Any], source: str, claim: str, doc_refs: List[str], status="unverified"):
    rec["external_claims"].append({
        "source": source,
        "claim": claim,
        "doc_refs": doc_refs,
        "timestamp": _utc(),
        "status": status
    })
    rec["seals"]["transparency_log"].append({"ts": _utc(), "event":"external_claim_added", "actor": source})

def set_claim_status(rec: Dict[str, Any], idx: int, status: str):
    rec["external_claims"][idx]["status"] = status
    rec["seals"]["transparency_log"].append({"ts": _utc(), "event":f"claim_{idx}_status_{status}", "actor":"verifier"})

def export(rec: Dict[str, Any], path: str) -> str:
    Path(path).write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return path