#!/usr/bin/env python3
import asyncio, hashlib, json, math, time
from typing import Dict, Any, List, Tuple

class LatticePQCValidator:
    Q_MODULUS: int = 8380417
    GAMMA1: int = 524288
    BETA_BOUND: float = 0.25

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        seed = f"OCTAGON_BIO_PQC_{agent_id}".encode("utf-8")
        self.pub_matrix = [
            [int.from_bytes(hashlib.shake_256(seed + f"A_{i}_{j}".encode()).digest(4), "big") % self.Q_MODULUS for j in range(4)]
            for i in range(4)
        ]

    def sign(self, payload_hash: str, phase_slip: float) -> Dict[str, Any]:
        mu = hashlib.sha256(f"{self.agent_id}|{payload_hash}|{phase_slip:.6f}".encode()).digest()
        y_vec = [int.from_bytes(hashlib.sha256(mu + bytes([i])).digest()[:4], "big") % self.GAMMA1 for i in range(4)]
        w_sample = sum((self.pub_matrix[i][i] * y_vec[i]) % self.Q_MODULUS for i in range(4)) % self.Q_MODULUS
        c_hash = hashlib.sha256(mu + str(w_sample).encode()).hexdigest()
        z_norm = math.sqrt(sum(v**2 for v in y_vec)) + (phase_slip * 1e4)
        return {"agent_id": self.agent_id, "challenge_c": c_hash, "z_norm": z_norm, "valid": bool(phase_slip <= self.BETA_BOUND)}

    def verify(self, sig: Dict[str, Any], phase_slip: float) -> bool:
        return phase_slip <= self.BETA_BOUND and sig.get("valid", False)

class BiologicalSubstrate:
    def __init__(self, node_idx: int):
        self.atp_pool = 5.0 + (node_idx * 0.1)
        self.adp_pool = 0.5 + (node_idx * 0.02)
        self.proton_motive_force_mv = -180.0

    def compute_energy_charge(self) -> float:
        total = self.atp_pool + self.adp_pool
        return (self.atp_pool + 0.5 * self.adp_pool) / total if total > 0 else 0.0

    def step_metabolism(self, workload: float) -> Tuple[float, float]:
        hydrolysis = 0.12 * workload
        atp_consumed = min(self.atp_pool, hydrolysis)
        self.atp_pool -= atp_consumed
        self.adp_pool += atp_consumed
        phosphorylation = 0.15 * (abs(self.proton_motive_force_mv) / 180.0) * self.adp_pool
        self.atp_pool += phosphorylation
        self.adp_pool -= min(self.adp_pool, phosphorylation)
        ec = self.compute_energy_charge()
        metabolic_gamma = 0.05 / (1.0 + math.exp(-ec))
        return ec, metabolic_gamma

class OctagonAgent:
    PI_STATIC: float = math.pi
    PI_3D_COUPLING: float = 3.204423
    PHASE_LOCK_PHI: float = 1.292748
    LYAPUNOV_DECAY: float = -7.683965
    COUNCIL_NAMES = ["OCTA_ALPHA", "OCTA_BETA", "OCTA_GAMMA", "OCTA_DELTA", "OCTA_EPSILON", "OCTA_ZETA", "OCTA_ETA", "OCTA_THETA"]

    def __init__(self, idx: int, total_nodes: int = 8):
        self.idx = idx
        self.total_nodes = total_nodes
        self.name = self.COUNCIL_NAMES[idx % 8]
        self.agent_id = f"node_{idx:02d}_{self.name}"
        self.phase_offset = self.PHASE_LOCK_PHI + (2.0 * math.pi * idx / total_nodes)
        self.state_vector = [1.0 + (idx * 0.05), 1.0 - (idx * 0.025), 0.5 + (idx * 0.04)]
        self.accumulated_slip = 0.0
        self.bio = BiologicalSubstrate(idx)
        self.pqc = LatticePQCValidator(self.agent_id)
        self.inbox: List[Dict[str, Any]] = []

    def get_neighbors(self) -> Tuple[int, int]:
        return (self.idx - 1) % self.total_nodes, (self.idx + 1) % self.total_nodes

    def produce_proposal(self, cycle: int) -> Dict[str, Any]:
        workload = 0.5 + (0.1 * math.cos(cycle * 0.2 + self.idx))
        energy_charge, bio_gamma = self.bio.step_metabolism(workload)
        op_input = [0.08 * math.sin(cycle * 0.15 + self.idx), 0.04 * math.cos(cycle * 0.15 + (self.idx * 0.5)), 0.015 * cycle]
        step_slip = sum(abs((self.PI_3D_COUPLING - self.PI_STATIC) * u) for u in op_input)
        self.accumulated_slip += step_slip
        norm = math.sqrt(sum(v**2 for v in self.state_vector)) + 1e-12
        grad = [math.cos(self.phase_offset * norm) * (v / norm) for v in self.state_vector]
        self.state_vector = [
            (self.state_vector[a] + (self.PI_3D_COUPLING * op_input[a]) + grad[a]) * (1.0 - bio_gamma) * math.exp(self.LYAPUNOV_DECAY * 1e-3)
            for a in range(3)
        ]
        payload_hash = hashlib.sha256(f"{cycle}|{self.agent_id}|{self.state_vector}|ec:{energy_charge:.4f}".encode()).hexdigest()
        sig = self.pqc.sign(payload_hash, step_slip)
        return {"agent_id": self.agent_id, "node_idx": self.idx, "cycle": cycle, "vector": [round(v, 6) for v in self.state_vector], "energy_charge": round(energy_charge, 4), "atp_pool": round(self.bio.atp_pool, 3), "step_slip": round(step_slip, 6), "payload_hash": payload_hash, "signature": sig}

    def ingest_gossip(self, gossip_payloads: List[Dict[str, Any]]):
        self.inbox = [g for g in gossip_payloads if self.pqc.verify(g["signature"], g["step_slip"])]

    def reconcile_state(self) -> List[float]:
        if not self.inbox: return self.state_vector
        for a in range(3):
            peer_avg = sum(g["vector"][a] for g in self.inbox) / len(self.inbox)
            self.state_vector[a] = round(0.95 * self.state_vector[a] + 0.05 * peer_avg, 6)
        return self.state_vector

class BioHarmonicCouncilMesh:
    TARGET_FREQUENCY_HZ: float = 79.0
    CYCLE_LATENCY_MS: float = 12.658

    def __init__(self):
        self.nodes = [OctagonAgent(i, total_nodes=8) for i in range(8)]
        self.council_ledger: List[Dict[str, Any]] = []

    async def execute_cycle(self, cycle: int) -> Dict[str, Any]:
        t_start = asyncio.get_event_loop().time()
        proposals = [node.produce_proposal(cycle) for node in self.nodes]
        for node in self.nodes:
            l_idx, r_idx = node.get_neighbors()
            node.ingest_gossip([proposals[l_idx], proposals[r_idx]])
            node.reconcile_state()

        leaves = [p["payload_hash"] for p in proposals]
        global_root = hashlib.sha256("".join(sorted(leaves)).encode()).hexdigest()
        avg_vector = [round(sum(n.state_vector[a] for n in self.nodes) / len(self.nodes), 6) for a in range(3)]
        avg_ec = sum(p["energy_charge"] for p in proposals) / len(proposals)
        max_slip = max(p["step_slip"] for p in proposals)

        record = {
            "cycle": cycle,
            "active_nodes": len(self.nodes),
            "global_merkle_root": global_root,
            "council_vector_mean": avg_vector,
            "mean_energy_charge": round(avg_ec, 4),
            "max_slip_delta": max_slip,
            "consensus_status": "BIO_OCTAGON_LOCKED" if avg_ec >= 0.70 else "METABOLIC_DEGRADE"
        }
        self.council_ledger.append(record)
        t_exec = asyncio.get_event_loop().time() - t_start
        await asyncio.sleep(max(0.0, (self.CYCLE_LATENCY_MS / 1000.0) - t_exec))
        return record

    async def run_council(self, cycles: int = 5):
        print(f"=== Starting Bio-Harmonic Octagon Council Mesh [79.0 Hz | {self.CYCLE_LATENCY_MS} ms] ===")
        for c in range(1, cycles + 1):
            rec = await self.execute_cycle(c)
            print(f"[Council Cycle {rec['cycle']:02d}] Status: [{rec['consensus_status']}] Avg EC: {rec['mean_energy_charge']:.4f}")
            print(f"  -> Merkle State Root: {rec['global_merkle_root'][:32]}...")
            print(f"  -> State Vector Mean:  {rec['council_vector_mean']}")
            print(f"  -> Max Slip Delta:     {rec['max_slip_delta']:.6f}")
            print("-" * 70)

if __name__ == "__main__":
    asyncio.run(BioHarmonicCouncilMesh().run_council(5))
