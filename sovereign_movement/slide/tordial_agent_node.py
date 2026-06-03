"""
tordial_agent_node.py
Tordial-GS Manifold — corrected agent node implementation
Two Mile Solutions LLC / John Carroll Jr.

Fixes applied:
  - Base class defined before subclass (NameError resolved)
  - Config loaded once at module level with .get() defaults
  - GS sweep formula drives sigma_T (no clamp — allows natural negative values)
  - Fission on deep GS deficit (sigma_T < -450) — Option B, architecturally correct
  - Energy governor: drain coefficient 0.8, MAX_ENERGY_CAP 500.0 (breakeven ~15 nodes)
"""

import yaml
from pathlib import Path

# ── Config load (once at import time) ────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    t = yaml.safe_load(f)

PHI_OP        = t.get("phi_op", 1.0)
GEAR_SHIFT    = t.get("gear_shift_correction", 1.04)
GS_DENOM      = 4.0 * PHI_OP * GEAR_SHIFT   # pre-computed constant

# ── Energy governor constants ─────────────────────────────────────────────────
MIN_ENERGY_FLOOR = 50.0
MAX_ENERGY_CAP   = 500.0
ENERGY_GAIN_BASE = 12.0
ENERGY_GAIN_KAPPA_COEFF = 0.8
ENERGY_DRAIN_PER_NODE   = 0.8   # breakeven at ~15 nodes

# ── Fission threshold ─────────────────────────────────────────────────────────
FISSION_SIGMA_THRESHOLD = -450.0


# ── Energy governor (module-level, shared across all nodes) ───────────────────
def update_global_energy(global_energy: float, avg_kappa: float, node_count: int) -> float:
    """
    Computes updated global energy with a drain term strong enough
    to actually suppress spawning at realistic node counts.

    Breakeven: node_count ≈ (12 + 0.8 * avg_kappa) / 0.8
    At avg_kappa=0: breakeven ≈ 15 nodes.
    """
    energy_delta = (
        ENERGY_GAIN_BASE
        + ENERGY_GAIN_KAPPA_COEFF * avg_kappa
        - ENERGY_DRAIN_PER_NODE * node_count
    )
    new_energy = global_energy + energy_delta
    new_energy = max(MIN_ENERGY_FLOOR, min(MAX_ENERGY_CAP, new_energy))

    if new_energy <= MIN_ENERGY_FLOOR and global_energy > MIN_ENERGY_FLOOR:
        print(
            f"[GOVERNOR] Energy floor hit — spawn suppressed "
            f"(energy={new_energy:.1f}, nodes={node_count})"
        )

    return new_energy


# ═══════════════════════════════════════════════════════════════════════════════
# BASE CLASS — must be defined before any subclass
# ═══════════════════════════════════════════════════════════════════════════════
class TordialAgentNode:
    """
    Base toroidal agent node.
    Holds identity, curvature state, and the GS sweep interface.
    """

    def __init__(self, node_id: str, config: dict):
        self.node_id            = node_id
        self.config             = config
        self.curvature_pressure = 0.0
        self.sigma_T            = 1.0    # initial non-zero default
        self.energy             = 100.0
        self.drift_phase        = 0.0
        self.health             = 100.0

    def compute_and_update_gs(self, manifold_state: dict):
        """Override in subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement compute_and_update_gs"
        )

    def _trigger_fission(self):
        """
        Fission event: deep GS deficit (sigma_T < FISSION_SIGMA_THRESHOLD).
        Base implementation logs; subclasses extend with spawning logic.
        """
        print(
            f"[FISSION] Node {self.node_id} — "
            f"sigma_T={self.sigma_T:.3f} breached {FISSION_SIGMA_THRESHOLD}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SUBCLASS — open/boundary node with full GS sweep
# ═══════════════════════════════════════════════════════════════════════════════
class OpenTordialAgentNode(TordialAgentNode):
    """
    Open-boundary toroidal agent node.

    GS sweep formula (from TGS-SPEC §7.2):
        sigma_T = r - d² / (4 · phi_op · gear_shift_correction)

    where:
        r  = GS rank (manifold_state["gs_rank"])
        d  = curvature_pressure (manifold_state["curvature_pressure"])

    sigma_T is UNCLAMPED — it must be allowed to go negative so the
    fission threshold (sigma_T < -450) can trigger on GS deficit.
    """

    def __init__(self, node_id: str, config: dict):
        super().__init__(node_id, config)
        self.sigma_T            = 1.0
        self.curvature_pressure = 0.0

    def compute_and_update_gs(self, manifold_state: dict) -> float:
        """
        Runs the GS sweep and checks the fission threshold.

        Returns:
            sigma_T (float): current Golod-Shafarevich pressure value.
        """
        pressure = manifold_state.get("curvature_pressure", 0.3)
        r        = manifold_state.get("gs_rank", 1)

        self.curvature_pressure = pressure

        # GS sweep — NO max() clamp; sigma_T must reach negative values
        self.sigma_T = r - (pressure ** 2) / GS_DENOM

        # High-pressure regime: additional GS update logic
        if pressure > 0.6:
            self._apply_high_pressure_regime(manifold_state)

        # Fission on deep GS deficit
        if self.sigma_T < FISSION_SIGMA_THRESHOLD:
            self._trigger_fission()

        return self.sigma_T

    def _apply_high_pressure_regime(self, manifold_state: dict):
        """
        Placeholder for high-pressure GS update logic (fission prep,
        anyon injection, surface code syndrome escalation, etc.).
        Extend here rather than in compute_and_update_gs.
        """
        pass

    def _trigger_fission(self):
        """
        Deep GS deficit fission. Calls base logging then executes
        drift-phase child offset per TGS-SPEC §7.2:
            theta_child = (theta_parent + delta_theta_drift) mod 2π
        """
        super()._trigger_fission()

        import math
        # delta_theta_drift derived from sigma_T magnitude, not hardcoded
        delta_theta = abs(self.sigma_T) / FISSION_SIGMA_THRESHOLD * math.pi
        theta_child = (self.drift_phase + delta_theta) % (2 * math.pi)

        print(
            f"[FISSION] Child drift_phase={theta_child:.4f} rad "
            f"(parent={self.drift_phase:.4f}, delta={delta_theta:.4f})"
        )
        # Spawn logic: pass theta_child to the manifold's node registry
        # manifold.spawn_child_node(parent=self, drift_phase=theta_child)
