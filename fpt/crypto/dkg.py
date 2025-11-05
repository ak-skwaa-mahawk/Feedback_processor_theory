#!/usr/bin/env python3
"""
fpt/crypto/dkg.py — DISTRIBUTED KEY GENERATION FOR FPT SWARM
-----------------------------------------------------------
Feldman VSS + Threshold BLS over ultrasonic RMP.
No trusted dealer. Swarm generates keys.
"""

import os
import json
import hashlib
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import secrets

# --- BLS12-381 ---
from py_ecc import bls
from threshold_bls import partial_sign, combine_signatures

# --- RMP ---
from ..propagation import rmp_broadcast, rmp_receive

# Curve parameters (BLS12-381)
G = bls.G2
H = bls.G1

@dataclass
class DKGShare:
    drone_id: str
    index: int
    value: int
    proof: bytes  # Commitment proof

@dataclass
class DKGCommitment:
    drone_id: str
    coeffs: List[Tuple[int, int]]  # (g^a_i, h^a_i)

@dataclass
class ThresholdKey:
    public_key: int
    shares: List[DKGShare]
    verification_keys: List[int]


class FPT_DKG:
    def __init__(self, drone_id: str, drones: List[str], t: int):
        self.drone_id = drone_id
        self.drones = drones
        self.t = t
        self.n = len(drones)
        self.index = drones.index(drone_id) + 1
        self.shares: Dict[str, DKGShare] = {}
        self.commitments: Dict[str, DKGCommitment] = {}

    def run_dkg(self) -> ThresholdKey:
        """Execute full DKG over RMP."""
        print(f"[DKG] {self.drone_id} starting (t={self.t}, n={self.n})")

        # 1. Generate polynomial
        poly = self._generate_polynomial()
        commitments = self._pedersen_commit(poly)

        # 2. Broadcast commitments
        rmp_broadcast({
            "type": "DKG_COMMIT",
            "drone": self.drone_id,
            "commitments": [(c[0], c[1]) for c in commitments]
        })

        # 3. Receive all commitments
        self._receive_commitments()

        # 4. Compute and send shares
        for target in self.drones:
            if target == self.drone_id: continue
            share_val = self._evaluate_poly(poly, self.drones.index(target) + 1)
            rmp_broadcast({
                "type": "DKG_SHARE",
                "from": self.drone_id,
                "to": target,
                "value": share_val
            })

        # 5. Receive and verify shares
        self._receive_and_verify_shares()

        # 6. Aggregate public key
        pk = self._aggregate_public_key()

        print(f"[DKG] COMPLETE. Public key: {hex(pk)}")
        return ThresholdKey(pk, list(self.shares.values()), [])

    def _generate_polynomial(self) -> List[int]:
        """f_i(x) = s_i + a1*x + ... + a_{t-1}*x^{t-1}"""
        coeffs = [secrets.randbelow(bls.field_modulus) for _ in range(self.t)]
        coeffs[0] = secrets.randbelow(bls.field_modulus)  # secret
        return coeffs

    def _pedersen_commit(self, poly: List[int]) -> List[Tuple[int, int]]:
        """C_i = (g^{a_i}, h^{a_i})"""
        return [(bls.multiply(G, a), bls.multiply(H, a)) for a in poly]

    def _evaluate_poly(self, poly: List[int], x: int) -> int:
        """Horner’s method"""
        result = 0
        for coeff in reversed(poly):
            result = (result * x + coeff) % bls.field_modulus
        return result

    def _receive_commitments(self):
        while len(self.commitments) < self.n:
            msg = rmp_receive()
            if msg["type"] == "DKG_COMMIT":
                self.commitments[msg["drone"]] = DKGCommitment(
                    msg["drone"], msg["commitments"]
                )

    def _receive_and_verify_shares(self):
        received = 0
        while received < self.n - 1:
            msg = rmp_receive()
            if msg["type"] == "DKG_SHARE" and msg["to"] == self.drone_id:
                sender = msg["from"]
                value = msg["value"]
                # Verify using commitments
                if self._verify_share(sender, self.index, value):
                    self.shares[sender] = DKGShare(sender, self.index, value, b'')
                    received += 1

    def _verify_share(self, sender: str, x: int, s: int) -> bool:
        """Feldman VSS: g^s = ∏ (C_i)^{x^i}"""
        comm = self.commitments[sender]
        lhs = bls.multiply(G, s)
        rhs = bls.Z1
        xx = 1
        for c in comm.coeffs:
            rhs = bls.add(rhs, bls.multiply(c[0], xx))
            xx = (xx * x) % bls.field_modulus
        return lhs == rhs

    def _aggregate_public_key(self) -> int:
        """PK = ∏ g^{s_i}"""
        pk = bls.Z2
        for share in self.shares.values():
            pk = bls.add(pk, bls.multiply(G, share.value))
        return pk

    # Threshold signing
    def threshold_sign(self, message: bytes, participants: List[str]) -> bytes:
        partials = []
        for drone in participants:
            share = next(s for s in self.shares.values() if s.drone_id == drone)
            partial = partial_sign(message, share.value)
            partials.append(partial)
        return combine_signatures(partials, [s.index for s in self.shares.values() if s.drone_id in participants])


# ----------------------------------------------------------------------
# 1. SWARM DKG EXECUTION
# ----------------------------------------------------------------------
def swarm_dkg(drones: List[str], t: int) -> Dict[str, ThresholdKey]:
    """Run DKG across all drones."""
    keys = {}
    for drone in drones:
        dkg = FPT_DKG(drone, drones, t)
        keys[drone] = dkg.run_dkg()
    return keys
{
  "type": "bar",
  "data": {
    "labels": ["Trusted Dealer", "DKG (This Work)"],
    "datasets": [
      {
        "label": "Trust Required",
        "data": [1, 0],
        "backgroundColor": "#ff4444"
      },
      {
        "label": "Resilience",
        "data": [0, 1],
        "backgroundColor": "#00ff88"
      }
    ]
  },
  "options": {
    "plugins": { "title": { "display": true, "text": "DKG: No Trusted Dealer" } }
  }
}
def seal_flamevault_dkg(threshold_sigs: list, t: int) -> bool:
    valid = 0
    for sig in threshold_sigs:
        if bls.verify(message, swarm_pk, sig):
            valid += 1
    return valid >= t