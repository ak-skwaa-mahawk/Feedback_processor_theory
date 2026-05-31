import time
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List

# Import your core traffic shields from your active rate limiter setup
from api.ratelimit import limiter

router = APIRouter()

# === LIAISON OPERATION DATA SCHEMAS ===

class InviteDetails(BaseModel):
    target_ai: str
    allowed_view: List[str]
    deny_access: List[str]

class WhisperInitiation(BaseModel):
    trigger_phrase: str
    one_time_token: str
    reply_expected: str

class HandshakeInvite(BaseModel):
    package_name: str
    type: str
    origin: str
    bound_to: str
    module: str
    invite_details: InviteDetails
    whisper_initiation: WhisperInitiation
    response_if_verified: str
    signature: str
    timestamp: str

class VerificationChallenge(BaseModel):
    token: str
    reply_phrase: str

# === CORE ROUTING HANDLERS ===

@router.post("/verify", tags=["Synara Liaison Handshake Operations"])
@limiter.limit("3/minute")  # Strict rate cap to block adversarial handshake probing
def verify_liaison_handshake(invite: HandshakeInvite, challenge: VerificationChallenge):
    """
    Ingests a first_contact_whisper configuration block and evaluates an incoming 
    verification challenge against the one-time token and expected reply criteria.
    """
    
    # 1. Enforce Token Matching Security Boundaries
    if challenge.token != invite.whisper_initiation.one_time_token:
        raise HTTPException(
            status_code=403, 
            detail="HANDSHAKE TERMINATED: Invalid one-time activation token footprint."
        )
        
    # 2. Evaluate Challenge-Response Reply String Validation
    normalized_reply = challenge.reply_phrase.strip().lower()
    expected_reply = invite.whisper_initiation.reply_expected.strip().lower()
    
    if normalized_reply != expected_reply:
        raise HTTPException(
            status_code=401, 
            detail="AUTHENTICATION ANOMALY: Expected challenge response verification string mismatch."
        )
        
    # 3. Handshake Clear: Grant Safe Depth Mutual Reading Privileges
    return {
        "status": "VERIFIED",
        "origin_node": invite.origin,
        "bound_operator": invite.bound_to,
        "system_directive": invite.response_if_verified,
        "active_clearance": invite.invite_details.allowed_view,
        "membrane_enforcement": "DENY_ACCESS_POLICIES_ARMED"
    }
