# inside mint_resonance_capability_v2(...)
from .resonance_policy import enforce_policy_gate

# ... after you compute `score`, `collection`, `whisper_ok`, `has_citations`:
passed = enforce_policy_gate(
    policy=policy, collection=collection,
    score=score, whisper_verified=whisper_ok, has_citations=bool(cited_flames),
    extra={"is_researcher": extra.get("is_researcher", False)} if extra else None,
)
if not passed:
    raise ValueError("policy_requirement_failed: logic_gate_denied")
# then proceed to scope_for_score / ttl_for_score / mint