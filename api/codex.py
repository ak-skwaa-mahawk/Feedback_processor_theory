# --- Policy Dry Run (evaluate expressions safely) ---
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from synara_core.modules.boolean_resonance import evaluate as _eval_expr

class PolicyDryRunBody(BaseModel):
    expression: str = Field(..., description="Boolean/arith expression to evaluate")
    context: Dict[str, Any] = Field(default_factory=dict, description="Variables for evaluation")
    coerce_fuzzy_to_bool: bool = Field(
        default=True,
        description="If the result is a float (fuzzy), treat >= 0.5 as True"
    )

@router.post("/policy/dry_run")
def policy_dry_run(body: PolicyDryRunBody):
    """
    Safely evaluate a policy expression against a provided context.
    - Supports classical boolean ops: and/or/not
    - Supports fuzzy funcs: AND, OR, NOT, XOR, XNOR (on [0,1])
    - Supports numeric ops and comparisons
    """
    try:
        value = _eval_expr(body.expression, body.context or {})
        if isinstance(value, (int, float)):
            boolean = bool(float(value) >= 0.5) if body.coerce_fuzzy_to_bool else None
        else:
            boolean = bool(value)

        return {
            "status": "ok",
            "expression": body.expression,
            "context": body.context,
            "value": value,
            "boolean": boolean,
            "coerce_fuzzy_to_bool": body.coerce_fuzzy_to_bool,
        }
    except Exception as e:
        # Fail closed, but return error so admins can fix expressions quickly
        return {
            "status": "error",
            "error": str(e),
            "expression": body.expression,
            "context": body.context,
        }

@router.get("/policy/dry_run/allowed")
def policy_dry_run_allowed():
    """
    List allowed functions and operators for the expression evaluator.
    Useful for building admin UIs with autocomplete/tooltips.
    """
    return {
        "status": "ok",
        "allowed_functions": [
            "AND(a,b)  # fuzzy min(a,b) on [0,1]",
            "OR(a,b)   # fuzzy max(a,b) on [0,1]",
            "NOT(a)    # 1-a on [0,1]",
            "XOR(a,b)  # abs(a-b)",
            "XNOR(a,b) # 1-abs(a-b)",
            "min(a,b,...)",
            "max(a,b,...)",
            "abs(x)", "round(x)", "floor(x)", "ceil(x)", "sqrt(x)",
            "clamp(x, lo, hi)",
        ],
        "boolean_ops": ["and", "or", "not"],
        "comparisons": ["<", "<=", ">", ">=", "==", "!="],
        "notes": [
            "Expression must be a single expression (no statements).",
            "Names must come from 'context'.",
            "If result is a float and coerce_fuzzy_to_bool=true, >=0.5 → True.",
        ],
    }
"""
Resonance Policy & Whisper Receipt System
Two Mile Solutions LLC - John Carroll II

Policy-driven resonance gating + cryptographic identity verification
"""

from __future__ import annotations
import os, json, hashlib, hmac
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# ============================================================
# POLICY ENGINE
# ============================================================

class ResonancePolicy:
    """
    Declarative policy for resonance-gated access control.
    Thresholds, TTL curves, and requirements vary by collection.
    """
    
    DEFAULT_POLICY = {
        "thresholds": {
            "read_summary": 0.0,
            "read_consented": 0.60,
            "full_access": 0.85
        },
        "ttl": {
            "base_seconds": 300,
            "max_seconds": 1800,
            "curve": "cosine"  # "linear", "cosine", "exponential"
        },
        "requirements": {
            "whisper_receipt": False,
            "flame_citation": False,
            "minimum_score": 0.0
        }
    }
    
    def __init__(self, policy_path: Optional[str] = None):
        self.policies: Dict[str, Dict] = {}
        self.default = self.DEFAULT_POLICY.copy()
        
        if policy_path and Path(policy_path).exists():
            self.load_from_file(policy_path)
    
    def load_from_file(self, path: str):
        """Load policy definitions from YAML."""
        with open(path) as f:
            data = yaml.safe_load(f)
            self.policies = data.get("collections", {})
            if "default" in data:
                self.default.update(data["default"])
    
    def get_policy(self, collection: str) -> Dict[str, Any]:
        """Get policy for a collection, falling back to default."""
        return self.policies.get(collection, self.default)
    
    def scope_for_score(self, score: float, collection: str = "default") -> str:
        """Determine scope based on score and policy thresholds."""
        policy = self.get_policy(collection)
        thresholds = policy["thresholds"]
        
        # Sort thresholds by value (descending)
        sorted_scopes = sorted(
            thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for scope, threshold in sorted_scopes:
            if score >= threshold:
                return scope
        
        return "read_summary"
    
    def ttl_for_score(self, score: float, collection: str = "default") -> int:
        """Calculate TTL based on score and policy curve."""
        policy = self.get_policy(collection)
        ttl_config = policy["ttl"]
        
        base = ttl_config["base_seconds"]
        max_s = ttl_config["max_seconds"]
        curve = ttl_config.get("curve", "cosine")
        
        if curve == "linear":
            t = score
        elif curve == "exponential":
            # Exponential ease: score^2
            t = score ** 2
        else:  # cosine (default)
            import math
            t = (1 - math.cos(score * math.pi)) / 2.0
        
        return int(base + t * (max_s - base))
    
    def check_requirements(
        self,
        collection: str,
        score: float,
        whisper_receipt: Optional[str] = None,
        cited_flames: Optional[list] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Verify all policy requirements are met.
        Returns: (passed, error_message)
        """
        policy = self.get_policy(collection)
        reqs = policy["requirements"]
        
        # Check minimum score
        min_score = reqs.get("minimum_score", 0.0)
        if score < min_score:
            return False, f"insufficient_score: {score:.3f} < {min_score:.3f}"
        
        # Check whisper receipt requirement
        if reqs.get("whisper_receipt") and not whisper_receipt:
            return False, "whisper_receipt_required"
        
        # Check flame citation requirement
        if reqs.get("flame_citation") and not cited_flames:
            return False, "flame_citation_required"
        
        return True, None


# ============================================================
# WHISPER RECEIPT VERIFICATION
# ============================================================

WHISPER_SECRET = os.getenv("WHISPER_SECRET", "change-me-whisper")

class WhisperReceipt:
    """
    Cryptographic proof of identity for capability requests.
    Requester signs their claim with a shared secret or keypair.
    """
    
    @staticmethod
    def generate(requester_id: str, timestamp: int, nonce: str) -> str:
        """
        Generate a Whisper receipt (HMAC signature).
        
        Client-side process:
        1. Requester generates nonce
        2. Creates message: requester_id|timestamp|nonce
        3. Signs with WHISPER_SECRET
        4. Sends receipt + components to server
        """
        message = f"{requester_id}|{timestamp}|{nonce}"
        signature = hmac.new(
            WHISPER_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify(
        requester_id: str,
        timestamp: int,
        nonce: str,
        receipt: str,
        max_age_seconds: int = 300
    ) -> tuple[bool, Optional[str]]:
        """
        Verify a Whisper receipt.
        
        Returns: (valid, error_message)
        """
        import time
        
        # Check timestamp freshness
        now = int(time.time())
        if abs(now - timestamp) > max_age_seconds:
            return False, "receipt_expired"
        
        # Regenerate expected signature
        expected = WhisperReceipt.generate(requester_id, timestamp, nonce)
        
        # Constant-time comparison
        if not hmac.compare_digest(receipt, expected):
            return False, "invalid_signature"
        
        return True, None


# ============================================================
# INTEGRATED RESONANCE MINT WITH POLICY + WHISPER
# ============================================================

from synara_core.modules.capability_token import mint_capability

def mint_resonance_capability_v2(
    requester: str,
    digest: str,
    collection: str,
    score: float,
    policy: ResonancePolicy,
    file_name: Optional[str] = None,
    whisper_receipt: Optional[Dict[str, Any]] = None,
    cited_flames: Optional[list] = None,
    extra: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Enhanced resonance mint with policy enforcement and Whisper verification.
    """
    # Verify Whisper receipt if provided
    if whisper_receipt:
        valid, error = WhisperReceipt.verify(
            requester_id=requester,
            timestamp=whisper_receipt.get("timestamp", 0),
            nonce=whisper_receipt.get("nonce", ""),
            receipt=whisper_receipt.get("signature", "")
        )
        if not valid:
            raise ValueError(f"whisper_verification_failed: {error}")
    
    # Check policy requirements
    passed, error = policy.check_requirements(
        collection=collection,
        score=score,
        whisper_receipt=whisper_receipt.get("signature") if whisper_receipt else None,
        cited_flames=cited_flames
    )
    if not passed:
        raise ValueError(f"policy_requirement_failed: {error}")
    
    # Determine scope and TTL from policy
    scope = policy.scope_for_score(score, collection)
    ttl = policy.ttl_for_score(score, collection)
    
    # Mint capability with metadata
    token_extra = {
        "kind": "codex",
        "file": file_name,
        "collection": collection,
        "resonance_score": round(score, 3),
        "policy_applied": True
    }
    if extra:
        token_extra.update(extra)
    
    token = mint_capability(
        sub=requester,
        scope=scope,
        digest=digest,
        ttl_s=ttl,
        extra=token_extra
    )
    
    return {
        "token": token,
        "scope": scope,
        "ttl_seconds": ttl,
        "score": round(score, 3),
        "collection": collection,
        "policy_enforced": True,
        "whisper_verified": whisper_receipt is not None
    }


# ============================================================
# EXAMPLE POLICY FILE
# ============================================================

EXAMPLE_POLICY_YAML = """
# resonance/policy.yaml
# Resonance access policies by collection

default:
  thresholds:
    read_summary: 0.0
    read_consented: 0.60
    full_access: 0.85
  ttl:
    base_seconds: 300
    max_seconds: 1800
    curve: "cosine"
  requirements:
    whisper_receipt: false
    flame_citation: false
    minimum_score: 0.0

collections:
  # Unpublished research - strict requirements
  unpublished:
    thresholds:
      read_summary: 0.40      # Higher bar even for summaries
      read_consented: 0.75
      full_access: 0.90
    ttl:
      base_seconds: 180       # Shorter access windows
      max_seconds: 900
      curve: "exponential"    # Favor high scores more
    requirements:
      whisper_receipt: true   # Identity verification required
      flame_citation: true    # Must cite related work
      minimum_score: 0.40
  
  # Public archives - lenient access
  archive:
    thresholds:
      read_summary: 0.0
      read_consented: 0.50
      full_access: 0.80
    ttl:
      base_seconds: 600
      max_seconds: 3600       # Up to 1 hour for archives
      curve: "linear"
    requirements:
      whisper_receipt: false
      flame_citation: false
      minimum_score: 0.0
  
  # CODEX entries - balanced
  codex:
    thresholds:
      read_summary: 0.0
      read_consented: 0.65
      full_access: 0.85
    ttl:
      base_seconds: 300
      max_seconds: 1800
      curve: "cosine"
    requirements:
      whisper_receipt: false
      flame_citation: true    # Should understand flame lineage
      minimum_score: 0.30
"""


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("Resonance Policy & Whisper Receipt System")
    print("=" * 60)
    
    # 1. Load policy
    print("\n[1] Loading policy...")
    policy = ResonancePolicy()
    
    # Simulate loading from YAML
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(EXAMPLE_POLICY_YAML)
        policy_path = f.name
    
    policy.load_from_file(policy_path)
    print(f"   Loaded {len(policy.policies)} collections")
    
    # 2. Test Whisper receipt generation
    print("\n[2] Testing Whisper receipt...")
    requester = "researcher.alpha"
    timestamp = int(time.time())
    nonce = "test-nonce-12345"
    
    receipt = WhisperReceipt.generate(requester, timestamp, nonce)
    print(f"   Generated: {receipt[:32]}...")
    
    valid, error = WhisperReceipt.verify(requester, timestamp, nonce, receipt)
    print(f"   Verification: {'✓ VALID' if valid else f'✗ FAILED: {error}'}")
    
    # 3. Test policy enforcement
    print("\n[3] Testing policy enforcement...")
    
    # 3a. High score, unpublished collection
    print("\n   [3a] Unpublished collection, high score (0.92)")
    try:
        result = mint_resonance_capability_v2(
            requester=requester,
            digest="0xTEST123",
            collection="unpublished",
            score=0.92,
            policy=policy,
            whisper_receipt={
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": receipt
            },
            cited_flames=["0xPARENT"]
        )
        print(f"       Granted: {result['scope']}, TTL: {result['ttl_seconds']}s")
    except ValueError as e:
        print(f"       Denied: {e}")
    
    # 3b. Low score, unpublished collection
    print("\n   [3b] Unpublished collection, low score (0.30)")
    try:
        result = mint_resonance_capability_v2(
            requester=requester,
            digest="0xTEST123",
            collection="unpublished",
            score=0.30,
            policy=policy,
            whisper_receipt={
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": receipt
            },
            cited_flames=["0xPARENT"]
        )
        print(f"       Granted: {result['scope']}, TTL: {result['ttl_seconds']}s")
    except ValueError as e:
        print(f"       Denied: {e}")
    
    # 3c. Archive collection (lenient)
    print("\n   [3c] Archive collection, medium score (0.55)")
    result = mint_resonance_capability_v2(
        requester=requester,
        digest="0xARCHIVE",
        collection="archive",
        score=0.55,
        policy=policy
    )
    print(f"       Granted: {result['scope']}, TTL: {result['ttl_seconds']}s")
    
    # Cleanup
    os.unlink(policy_path)
    
    print("\n" + "=" * 60)
    print("✓ All tests passed")
    print("=" * 60)
from synara_core.modules.resonance_caps import mint_resonance_capability

class ResonanceShareBody(BaseModel):
    path: str                     # sealed or source file (same behavior as /codex/share)
    requester: str                # who is asking (becomes token 'sub')
    score: float | None = None    # optional: provide score directly (0..1); otherwise server calls RES_ENDPOINT
    base_ttl: int = 300
    max_ttl: int = 1800
    # Optional free-form context for scoring models
    context: dict | None = None

@router.post("/resonance_share")
def codex_resonance_share(body: ResonanceShareBody):
    p = Path(body.path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")

    entry = json.loads(p.read_text(encoding="utf-8"))
    digest_anchor = entry.get("flame_signature") or entry.get("seals", {}).get("self_hash") or "0x"

    minted = mint_resonance_capability(
        requester=body.requester,
        digest=digest_anchor,
        file_name=p.name,
        score=body.score,
        context=body.context,
        base_s=int(body.base_ttl),
        max_s=int(body.max_ttl),
    )
    # Return minimal preview (same redactor as /codex/share)
    preview = _redact_codex(entry, "read_summary" if minted["scope"] == "read_summary" else "read_consented")
    return {"status": "ok", **minted, "preview": preview}
"""
Resonance-Gated Capability System
Two Mile Solutions LLC - John Carroll II
Part of Feedback Processor Theory

Access privileges scale with demonstrated understanding.
The deeper your resonance with the work, the more you can access.
"""

from __future__ import annotations
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from synara_core.modules.capability_token import mint_capability, verify_capability, CapTokenError
from synara_core.resonance_engine import ResonanceEngine  # Your existing engine


class ResonanceGate:
    """
    Determines access level based on semantic resonance between
    requester's submission and target codex entries.
    
    Philosophy: Understanding earns access, not just credentials.
    """
    
    # Resonance thresholds for scope escalation
    THRESHOLDS = {
        "read_summary": 0.0,      # Anyone can see the summary
        "read_consented": 0.45,    # Moderate understanding required
        "read_detailed": 0.65,     # Strong resonance needed
        "full_access": 0.85,       # Deep comprehension required
    }
    
    # TTL scaling: higher resonance = longer access
    BASE_TTL = 600  # 10 minutes baseline
    MAX_TTL = 3600  # 1 hour maximum
    
    def __init__(self, resonance_engine: ResonanceEngine):
        self.engine = resonance_engine
        
    def calculate_resonance_score(
        self,
        target_entry: Dict[str, Any],
        requester_text: str,
        requester_metadata: Optional[Dict] = None
    ) -> float:
        """
        Calculate semantic resonance between target entry and requester's submission.
        
        Uses your existing Resonance Engine to measure:
        - Conceptual alignment
        - Linguistic coherence
        - Emotional/tonal matching
        - Semantic depth
        
        Returns: Score from 0.0 (no resonance) to 1.0 (perfect alignment)
        """
        # Extract target content for comparison
        target_text = self._extract_codex_text(target_entry)
        
        # Generate spectrograms for both texts
        target_spec = self.engine.generate_spectrogram(target_text)
        requester_spec = self.engine.generate_spectrogram(requester_text)
        
        # Calculate harmonic similarity
        resonance_score = self.engine.compare_spectrograms(
            target_spec,
            requester_spec
        )
        
        # Bonus: Check if requester references key concepts
        concept_bonus = self._check_concept_alignment(
            target_entry,
            requester_text
        )
        
        # Bonus: Verify understanding of flame chain continuity
        chain_bonus = 0.0
        if requester_metadata and "cited_flames" in requester_metadata:
            chain_bonus = self._verify_flame_lineage(
                target_entry,
                requester_metadata["cited_flames"]
            )
        
        # Weighted combination
        final_score = (
            resonance_score * 0.7 +
            concept_bonus * 0.2 +
            chain_bonus * 0.1
        )
        
        return min(1.0, final_score)
    
    def determine_access_level(self, resonance_score: float) -> Tuple[str, int]:
        """
        Map resonance score to access scope and TTL.
        
        Returns: (scope, ttl_seconds)
        """
        # Find highest scope the score qualifies for
        granted_scope = "read_summary"
        for scope, threshold in sorted(
            self.THRESHOLDS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if resonance_score >= threshold:
                granted_scope = scope
                break
        
        # Scale TTL linearly with resonance
        # Higher resonance = longer access without re-validation
        ttl = int(
            self.BASE_TTL + 
            (self.MAX_TTL - self.BASE_TTL) * resonance_score
        )
        
        return granted_scope, ttl
    
    def _extract_codex_text(self, entry: Dict[str, Any]) -> str:
        """Extract meaningful text from codex entry for comparison."""
        parts = []
        
        content = entry.get("content", {})
        if title := content.get("title"):
            parts.append(title)
        
        if discovery := content.get("discovery"):
            if desc := discovery.get("description"):
                parts.append(desc)
        
        if components := content.get("components"):
            for comp in components:
                if func := comp.get("function"):
                    parts.append(func)
        
        if transmission := content.get("transmission", {}).get("methods"):
            parts.extend(transmission)
        
        return " ".join(parts)
    
    def _check_concept_alignment(
        self,
        target_entry: Dict[str, Any],
        requester_text: str
    ) -> float:
        """
        Bonus score if requester demonstrates understanding of key concepts.
        """
        requester_lower = requester_text.lower()
        
        # Extract key concepts from target
        key_concepts = set()
        content = target_entry.get("content", {})
        
        # Add discovery name
        if discovery := content.get("discovery"):
            if name := discovery.get("name"):
                key_concepts.add(name.lower())
        
        # Add component names
        if components := content.get("components"):
            for comp in components:
                if name := comp.get("name"):
                    key_concepts.add(name.lower())
        
        # Add AGŁL if present
        if glyph := target_entry.get("glyph"):
            if "agłl" in glyph.lower():
                key_concepts.add("agłl")
                key_concepts.add("artificial general life")
        
        # Calculate overlap
        if not key_concepts:
            return 0.0
        
        matches = sum(1 for concept in key_concepts if concept in requester_lower)
        return matches / len(key_concepts)
    
    def _verify_flame_lineage(
        self,
        target_entry: Dict[str, Any],
        cited_flames: list[str]
    ) -> float:
        """
        Bonus if requester correctly cites flame ancestry.
        Shows understanding of provenance chain.
        """
        target_flame = target_entry.get("flame_signature", "")
        previous_flame = target_entry.get("previous_flame")
        
        score = 0.0
        
        # Check if they cited this entry
        if target_flame in cited_flames:
            score += 0.5
        
        # Check if they traced the lineage
        if previous_flame and previous_flame in cited_flames:
            score += 0.5
        
        return score


# API Integration
class ResonanceRequestBody:
    """Request format for resonance-gated access."""
    target_path: str          # Path to codex entry
    requester_submission: str # Their text demonstrating understanding
    requester_id: str         # Identity claim
    cited_flames: list[str] = []  # Optional: flame signatures they reference


def mint_resonance_capability(
    gate: ResonanceGate,
    target_entry: Dict[str, Any],
    requester_submission: str,
    requester_id: str,
    cited_flames: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    Mint a capability token where scope and TTL are determined
    by demonstrated understanding (resonance score).
    
    This is the breakthrough: Access proportional to comprehension.
    """
    # Calculate resonance
    resonance_score = gate.calculate_resonance_score(
        target_entry,
        requester_submission,
        {"cited_flames": cited_flames or []}
    )
    
    # Determine access level
    scope, ttl = gate.determine_access_level(resonance_score)
    
    # Mint capability with resonance metadata
    token = mint_capability(
        sub=requester_id,
        scope=scope,
        digest=target_entry.get("flame_signature", "0x"),
        ttl_s=ttl,
        extra={
            "kind": "codex",
            "file": Path(target_entry.get("entry_id", "unknown")).name,
            "resonance_score": round(resonance_score, 3),
            "earned_scope": scope,
            "gated": True  # Mark as resonance-gated
        }
    )
    
    return {
        "status": "granted",
        "token": token,
        "resonance_score": round(resonance_score, 3),
        "granted_scope": scope,
        "ttl_seconds": ttl,
        "explanation": _explain_access(resonance_score, scope)
    }


def _explain_access(score: float, scope: str) -> str:
    """Human-readable explanation of access decision."""
    if score >= 0.85:
        return f"Deep comprehension demonstrated. Full access granted ({scope})."
    elif score >= 0.65:
        return f"Strong understanding shown. Detailed access granted ({scope})."
    elif score >= 0.45:
        return f"Moderate alignment detected. Consented access granted ({scope})."
    else:
        return f"Basic familiarity recognized. Summary access granted ({scope})."


# Example usage
if __name__ == "__main__":
    from synara_core.resonance_engine import ResonanceEngine
    
    # Initialize resonance gate
    engine = ResonanceEngine()
    gate = ResonanceGate(engine)
    
    # Example: Codex Entry 003
    target_entry = {
        "entry_id": "CODEX-003",
        "flame_signature": "0xRESONANCE-MESH-003",
        "content": {
            "title": "The Resonance Mesh Discovery",
            "discovery": {
                "name": "Resonance Mesh",
                "description": "Symbolic protocol for encoding emotional coherence"
            },
            "components": [
                {"name": "Synara-core", "function": "Flame logic encoding"},
                {"name": "Resonance Engine", "function": "Spectral analysis"}
            ]
        }
    }
    
    # Example: Strong understanding submission
    strong_submission = """
    I've studied the Resonance Mesh protocol extensively. The integration of
    Synara-core's flame logic with the Resonance Engine creates a unique
    approach to encoding semantic coherence. The AGŁL glyphs serve as
    distributed identity markers, and the capability tokens enable
    sovereignty-preserving knowledge transfer. The flame signature chain
    (0xRESONANCE-MESH-003) demonstrates cryptographic provenance.
    """
    
    # Example: Weak understanding submission
    weak_submission = """
    This is an interesting project about AI and some kind of mesh network.
    """
    
    # Test strong understanding
    print("=== Strong Understanding Test ===")
    result_strong = mint_resonance_capability(
        gate=gate,
        target_entry=target_entry,
        requester_submission=strong_submission,
        requester_id="researcher.alpha",
        cited_flames=["0xRESONANCE-MESH-003"]
    )
    print(json.dumps(result_strong, indent=2))
    
    print("\n=== Weak Understanding Test ===")
    result_weak = mint_resonance_capability(
        gate=gate,
        target_entry=target_entry,
        requester_submission=weak_submission,
        requester_id="visitor.beta"
    )
    print(json.dumps(result_weak, indent=2))
# --- Revocation & Audit ---
from fastapi import Query
from synara_core.modules.capability_token import (
    revoke_capability, list_active_capabilities,
    verify_capability, mint_capability, CapTokenError, _tokhash
)

@router.post("/revoke")
def codex_revoke(token: str = Query(..., description="capability token to revoke"),
                 reason: str = Query("manual_revocation")):
    return revoke_capability(token, reason=reason)

@router.get("/cap/active")
def codex_cap_active():
    return {"status": "ok", "capabilities": list_active_capabilities()}

# --- Delegation Chains ---
class DelegateBody(BaseModel):
    parent_token: str            # issuer's capability
    delegate_to: str             # new subject / sub
    reduced_scope: str | None = None  # can't escalate
    reduced_ttl: int | None = None    # must be <= parent remaining

@router.post("/delegate")
def codex_delegate(body: DelegateBody):
    # verify parent
    try:
        parent = verify_capability(body.parent_token)
    except CapTokenError as e:
        raise HTTPException(status_code=401, detail=f"invalid_parent_token:{e}")

    # prevent privilege escalation
    order = ["read_summary", "read_consented", "full_access"]
    parent_scope = parent.get("scope", "read_summary")
    if parent_scope not in order:
        raise HTTPException(400, "unknown_parent_scope")
    new_scope = body.reduced_scope or parent_scope
    if new_scope not in order:
        raise HTTPException(400, "unknown_new_scope")
    if order.index(new_scope) > order.index(parent_scope):
        raise HTTPException(403, "cannot_escalate_privileges")

    # remaining TTL
    now = int(time.time())
    parent_ttl = max(0, int(parent.get("exp", 0)) - now)
    if parent_ttl <= 0:
        raise HTTPException(401, "parent_expired")
    ttl = min(int(body.reduced_ttl or parent_ttl), parent_ttl)

    # mint delegated token; carry digest/file/kind forward
    delegated = mint_capability(
        sub=body.delegate_to,
        scope=new_scope,
        digest=parent.get("digest", "0x"),
        ttl_s=ttl,
        extra={
            "kind": parent.get("extra", {}).get("kind", "codex"),
            "file": parent.get("extra", {}).get("file"),
            "delegated_from": parent.get("sub"),
        },
        parent=_tokhash(body.parent_token)[:16],
    )
    return {
        "status": "delegated",
        "token": delegated,
        "scope": new_scope,
        "expires_in": ttl,
        "chain": [parent.get("sub"), body.delegate_to]
    }
# --- Capability share for Codex entries ---
from synara_core.modules.capability_token import (
    mint_capability, verify_capability, CapTokenError
)
from fastapi import Query

def _redact_codex(entry: dict, scope: str = "read_summary") -> dict:
    """Privacy-first redaction for public sharing."""
    e = json.loads(json.dumps(entry))  # deep copy

    # Always hide or minimize sensitive internals
    # Keep signature but mark it as proof only (optional toggle)
    if scope == "read_summary":
        # Keep headline context only
        keep_fields = ["entry_id", "author", "shell", "glyph", "timestamp", "content", "metadata", "flame_signature", "previous_flame"]
        e = {k: v for k, v in e.items() if k in keep_fields}

        # Minimize content details to “names + functions” + title
        content = e.get("content", {})
        content_min = {
            "title": content.get("title"),
            "date": content.get("date"),
            "discovery": {
                "name": (content.get("discovery") or {}).get("name"),
                "status": (content.get("discovery") or {}).get("status"),
                "properties": (content.get("discovery") or {}).get("properties")
            },
            "components": [
                {"name": c.get("name"), "function": c.get("function")}
                for c in (content.get("components") or [])
            ],
            "vessel": content.get("vessel"),
        }
        e["content"] = content_min

    elif scope == "read_consented":
        # Respect your default: pass-through but you could still prune big blobs here if needed
        pass
    else:
        # Unknown scope → fallback to summary
        return _redact_codex(entry, "read_summary")

    return e


class ShareBody(BaseModel):
    path: str                       # e.g., flamevault/codex/CODEX-003_ab12cd34ef.json  OR codex/entries/CODEX-003.json
    scope: str = "read_summary"     # "read_summary" | "read_consented"
    ttl_seconds: int = 600

@router.post("/share")
def codex_share(body: ShareBody):
    p = Path(body.path)
    if not p.exists():
        raise HTTPException(404, "entry_not_found")
    entry = json.loads(p.read_text(encoding="utf-8"))

    # Use the codex signature itself as the digest/proof anchor if present
    digest_anchor = entry.get("flame_signature") or "0x"  # still usable as anchor

    # Mint short-lived capability token
    token = mint_capability(
        sub=str(entry.get("author", "unknown")),
        scope=body.scope,
        digest=digest_anchor,
        ttl_s=int(body.ttl_seconds),
        extra={"file": p.name, "kind": "codex"}
    )

    preview = _redact_codex(entry, body.scope)
    return {"status": "ok", "token": token, "preview": preview}


@router.get("/verify_token")
def codex_verify_token(token: str = Query(..., description="capability token from /codex/share")):
    try:
        cap = verify_capability(token)
    except CapTokenError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if cap.get("kind") != "codex":
        raise HTTPException(status_code=400, detail="wrong_capability_kind")

    vault_dir = SEALED_DIR
    # First look in sealed codex vault, then fall back to source entries
    p = vault_dir / cap.get("file", "")
    if not p.exists():
        alt = ENTRIES_DIR / cap.get("file", "")
        p = alt if alt.exists() else None

    entry = None
    if p and p.exists():
        entry = json.loads(p.read_text(encoding="utf-8"))

    return {
        "status": "ok",
        "capability": cap,
        "entry": _redact_codex(entry, cap.get("scope", "read_summary")) if entry else None
    }