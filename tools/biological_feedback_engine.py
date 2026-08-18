#!/usr/bin/env python3
import asyncio, hashlib, json, math, time
from typing import Dict, Any, List

class BiologicalMetabolicEngine:
    PI_STATIC: float = math.pi
    PI_3D_COUPLING: float = 3.204423
    TARGET_FREQUENCY_HZ: float = 79.0
    CYCLE_LATENCY_MS: float = 12.658
    PHASE_LOCK_PHI: float = 1.292748
    LYAPUNOV_DECAY: float = -7.683965

    def __init__(self, initial_atp_pool: float = 5.0, initial_adp_pool: float = 0.5):
        self.atp_pool = initial_atp_pool
        self.adp_pool = initial_adp_pool
        self.proton_motive_force_mv = -180.0
        self.actin_state = [1.0, 0.85, 0.5]
        self.cycle_count = 0
        self.total_phase_slip = 0.0
        self.metabolic_history: List[Dict[str, Any]] = []

    def compute_energy_charge(self) -> float:
        total = self.atp_pool + self.adp_pool
        return (self.atp_pool + 0.5 * self.adp_pool) / total if total > 0 else 0.0

    def step_metabolic_cycle(self, cellular_workload: float) -> Dict[str, Any]:
        self.cycle_count += 1
        hydrolysis = 0.15 * (1.0 + math.sin(self.cycle_count * 0.2)) * cellular_workload
        atp_consumed = min(self.atp_pool, hydrolysis)
        self.atp_pool -= atp_consumed
        self.adp_pool += atp_consumed

        phosphorylation = 0.18 * (abs(self.proton_motive_force_mv) / 180.0) * self.adp_pool
        self.atp_pool += phosphorylation
        self.adp_pool -= min(self.adp_pool, phosphorylation)
        
        energy_charge = self.compute_energy_charge()
        step_slip = abs((self.PI_3D_COUPLING - self.PI_STATIC) * cellular_workload)
        self.total_phase_slip += step_slip
        gamma = 0.05 / (1.0 + math.exp(-energy_charge))

        norm = math.sqrt(sum(v**2 for v in self.actin_state)) + 1e-12
        grad = [math.cos(self.PHASE_LOCK_PHI * norm) * (v / norm) for v in self.actin_state]

        self.actin_state = [
            (self.actin_state[a] + (self.PI_3D_COUPLING * cellular_workload * 0.1) + grad[a])
            * (1.0 - gamma)
            * math.exp(self.LYAPUNOV_DECAY * 1e-3)
            for a in range(3)
        ]

        payload_str = f"cycle:{self.cycle_count}|atp:{self.atp_pool:.4f}|ec:{energy_charge:.4f}|actin:{[round(v, 6) for v in self.actin_state]}|slip:{step_slip:.6f}"
        state_root = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        metrics = {
            "cycle": self.cycle_count,
            "atp_pool_mm": round(self.atp_pool, 4),
            "adp_pool_mm": round(self.adp_pool, 4),
            "energy_charge": round(energy_charge, 4),
            "step_phase_slip": round(step_slip, 6),
            "total_accumulated_slip": round(self.total_phase_slip, 6),
            "actin_state_vector": [round(v, 6) for v in self.actin_state],
            "state_root_hash": state_root,
            "stability_status": "HOMEOSTASIS_LOCKED" if energy_charge >= 0.70 else "METABOLIC_DECAY"
        }
        self.metabolic_history.append(metrics)
        return metrics

    async def run_metabolic_cadence(self, cycles: int = 5):
        interval_sec = self.CYCLE_LATENCY_MS / 1000.0
        print(f"=== Starting Biological Feedback Engine [79.0 Hz | {self.CYCLE_LATENCY_MS} ms] ===")
        for c in range(1, cycles + 1):
            t_start = asyncio.get_event_loop().time()
            workload = 0.5 + (0.1 * math.cos(c * 0.3))
            m = self.step_metabolic_cycle(workload)
            print(f"[Cycle {m['cycle']:02d}] Status: [{m['stability_status']}] EC Ratio: {m['energy_charge']:.4f}")
            print(f"  -> ATP / ADP Pool:  {m['atp_pool_mm']} mM / {m['adp_pool_mm']} mM")
            print(f"  -> Actin State:     {m['actin_state_vector']}")
            print(f"  -> Phase Slip Δ:    {m['step_phase_slip']:.6f} (Total: {m['total_accumulated_slip']:.6f})")
            print(f"  -> State Root:      {m['state_root_hash'][:24]}...")
            print("-" * 70)
            t_exec = asyncio.get_event_loop().time() - t_start
            await asyncio.sleep(max(0.0, interval_sec - t_exec))

if __name__ == "__main__":
    asyncio.run(BiologicalMetabolicEngine().run_metabolic_cadence(5))
