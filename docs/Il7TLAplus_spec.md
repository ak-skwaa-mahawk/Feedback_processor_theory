# Ił7 Kernel — TLA+ Specification
This document provides a TLA+‑ready formalization of the Ił7 kernel.  
It is implementation‑neutral and suitable for model checking with TLC.

---

## MODULE Il7Kernel

```tla
--------------------------- MODULE Il7Kernel ---------------------------

EXTENDS Naturals, Sequences

CONSTANT epsilon_base

VARIABLES state, vitality, epsilon_d, session_id, revocation_token_hash

States == {"UNSENSED", "SENSED", "REVOKED", "SEALED"}

Init ==
  /\ state = "UNSENSED"
  /\ vitality = 1.0
  /\ epsilon_d = epsilon_base
  /\ session_id = Null
  /\ revocation_token_hash = Null

StartSensed(session, tokenHash) ==
  /\ state \in {"UNSENSED", "REVOKED", "SEALED"}
  /\ state' = "SENSED"
  /\ session_id' = session
  /\ revocation_token_hash' = tokenHash
  /\ vitality' = 1.0
  /\ epsilon_d' = epsilon_base

EegVitality(v) ==
  /\ v >= 0.5 /\ v <= 1.5
  /\ IF state = "SENSED" THEN
        /\ state' = "SENSED"
        /\ vitality' = v
        /\ epsilon_d' = epsilon_base * v
     ELSE
        /\ state' = state
        /\ vitality' = vitality
        /\ epsilon_d' = epsilon_base

Revoke(tokenHash) ==
  /\ IF state = "SENSED" /\ tokenHash = revocation_token_hash THEN
        /\ state' = "REVOKED"
        /\ vitality' = 1.0
        /\ epsilon_d' = epsilon_base
        /\ session_id' = Null
        /\ revocation_token_hash' = Null
     ELSE
        /\ state' = state
        /\ vitality' = vitality
        /\ epsilon_d' = epsilon_d
        /\ session_id' = session_id
        /\ revocation_token_hash' = revocation_token_hash

EndSessionNormal ==
  /\ state = "SENSED"
  /\ state' = "SEALED"
  /\ vitality' = 1.0
  /\ epsilon_d' = epsilon_base
  /\ session_id' = Null
  /\ revocation_token_hash' = Null

EpsilonMove ==
  /\ state \in {"REVOKED", "SEALED"}
  /\ state' = "UNSENSED"
  /\ vitality' = 1.0
  /\ epsilon_d' = epsilon_base
  /\ session_id' = Null
  /\ revocation_token_hash' = Null

Next ==
  \/ ∃ s, t : StartSensed(s, t)
  \/ ∃ v : EegVitality(v)
  \/ ∃ t : Revoke(t)
  \/ EndSessionNormal
  \/ EpsilonMove

-----------------------------------------------------------------------

SovereignBaseline ==
  (state # "SENSED") => /\ vitality = 1.0 /\ epsilon_d = epsilon_base

VitalityBounds ==
  (state = "SENSED") => /\ vitality >= 0.5 /\ vitality <= 1.5

EpsilonBounds ==
  epsilon_d >= epsilon_base * 0.5 /\ epsilon_d <= epsilon_base * 1.65

NoEEGAffectsWhenNotSensed ==
  (state # "SENSED") => epsilon_d = epsilon_base

RevokeLeadsToBaseline ==
  []( (state = "SENSED") /\ Revoke(revocation_token_hash) => <> (state = "UNSENSED") )

NoStuckRevokedOrSealed ==
  [] (state \in {"REVOKED", "SEALED"} => <> (state = "UNSENSED"))

-----------------------------------------------------------------------