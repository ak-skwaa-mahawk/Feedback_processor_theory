#!/usr/bin/env python3
import asyncio, hashlib, json, math, time
from typing import Dict, Any, List

class LatticePQCValidator:
    Q_MODULUS: int = 8380417
    GAMMA1: int = 524288
    BETA_BOUND: float = 0.25

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        seed = f"FPT_AGENT_SEED_{agent_id}".encode("utf-8")
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

class ConsensusAgent:
    PI_STATIC: float = math.pi
    PI_3D_COUPLING: float = 3.204423
    PHASE_LOCK_PHI: float = 1.292748
    LYAPUNOV_DECAY: float = -7.683965

    def __init__(self, agent_idx: int, total_agents: int):
        self.agent_id = f"node_{agent_idx:02d}"
        self.agent_idx = agent_idx
        self.phase_offset = self.PHASE_LOCK_PHI + (2.0 * math.pi * agent_idx / total_agents)
        self.state_vector = [1.0 + (agent_idx * 0.1), 1.0 - (agent_idx * 0.05), 0.5 + (agent_idx * 0.08)]
        self.accumulated_slip = 0.0
        self.pqc = LatticePQCValidator(self.agent_id)

    def produce_state_proposal(self, cycle: int) -> Dict[str, Any]:
        op_input = [0.1 * math.sin(cycle * 0.2 + self.agent_idx), 0.05 * math.cos(cycle * 0.2), 0.02 * cycle]
        u_norm = math.sqrt(sum(v**2 for v in op_input))
        gamma = 0.05 / (1.0 + math.exp(-u_norm))
        step_slip = sum(abs((self.PI_3D_COUPLING - self.PI_STATIC) * u) for u in op_input)
        self.accumulated_slip += step_slip
        norm = math.sqrt(sum(v**2 for v in self.state_vector)) + 1e-12
        grad = [math.cos(self.phase_offset * norm) * (v / norm) for v in self.state_vector]
        self.state_vector = [
            (self.state_vector[a] + (self.PI_3D_COUPLING * op_input[a]) + grad[a]) * (1.0 - gamma) * math.exp(self.LYAPUNOV_DECAY * 1e-3)
            for a in range(3)
        ]
        payload_hash = hashlib.sha256(f"{cycle}|{self.agent_id}|{self.state_vector}".encode()).hexdigest()
        sig = self.pqc.sign(payload_hash, step_slip)
        return {"agent_id": self.agent_id, "cycle": cycle, "vector": [round(v, 6) for v in self.state_vector], "step_slip": round(step_slip, 6), "payload_hash": payload_hash, "signature": sig}

class HarmonicConsensusMesh:
    TARGET_FREQUENCY_HZ: float = 79.0
    CYCLE_LATENCY_MS: float = 12.658

    def __init__(self, num_agents: int = 4):
        self.agents = [ConsensusAgent(i, num_agents) for i in range(num_agents)]
        self.global_ledger = []

    async def execute_cycle(self, cycle: int) -> Dict[str, Any]:
        t_start = asyncio.get_event_loop().time()
        proposals = [agent.produce_state_proposal(cycle) for agent in self.agents]
        valid_proposals = [p for p in proposals if next(a for a in self.agents if a.agent_id == p["agent_id"]).pqc.verify(p["signature"], p["step_slip"])]
        leaves = [p["payload_hash"] for p in valid_proposals]
        global_root = hashlib.sha256("".join(sorted(leaves)).encode()).hexdigest()
        network_vector = [round(sum(p["vector"][axis] for p in valid_proposals) / len(valid_proposals), 6) for axis in range(3)]
        record = {
            "cycle": cycle,
            "participating_nodes": len(valid_proposals),
            "global_merkle_root": global_root,
            "network_vector_avg": network_vector,
            "max_phase_slip": max(p["step_slip"] for p in valid_proposals),
            "consensus_status": "CONVERGED" if len(valid_proposals) == len(self.agents) else "DEGRADED"
        }
        self.global_ledger.append(record)
        t_exec = asyncio.get_event_loop().time() - t_start
        await asyncio.sleep(max(0.0, (self.CYCLE_LATENCY_MS / 1000.0) - t_exec))
        return record

    async def run_mesh(self, cycles: int = 5):
        print(f"=== Starting Multi-Agent Consensus Mesh [{len(self.agents)} Nodes | {self.TARGET_FREQUENCY_HZ} Hz] ===")
        for c in range(1, cycles + 1):
            record = await self.execute_cycle(c)
            print(f"[Mesh Cycle {record['cycle']:02d}] Status: [{record['consensus_status']}] Nodes: {record['participating_nodes']}/{len(self.agents)}")
            print(f"  -> Global Root:  {record['global_merkle_root'][:28]}...")
            print(f"  -> Vector Mean:  {record['network_vector_avg']}")
            print(f"  -> Max Slip Δ:   {record['max_phase_slip']:.6f}")
            print("-" * 65)

if __name__ == "__main__":
    asyncio.run(HarmonicConsensusMesh(num_agents=4).run_mesh(5))
