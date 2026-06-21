# src/intent/pwc_sovereign_bridge.py

import time
import logging
from tordial_gs_manifold import SovereignOperator

logger = logging.getLogger(__name__)

class SovereignPWCLoop:
    def __init__(self, target_latency_ms: float = 45.0):
        # Instantiate the native PyO3 class directly — zero ctypes boilerplates
        self.operator = SovereignOperator()
        self.target_latency = target_latency_ms / 1000.0  # Convert to seconds (0.045s)
        self.last_tick_time = time.time()

    def run_control_cycle(self, substrate_engine, planner_component):
        """
        Executes a single iteration of the Planner-Walker-Critic loop,
        passing data directly to the native state-space gateway.
        """
        current_time = time.time()
        execution_delta = current_time - self.last_tick_time
        self.last_tick_time = current_time

        # --- ORION DRIFT DETECTION ---
        # If the host system lags or connectivity drops, stall_detected flags True
        stall_detected = execution_delta > self.target_latency

        # 1. Gather live telemetry vectors from the substrate surface
        snapshot = substrate_engine.get_status()
        d = snapshot.get("d", 0.0)
        r = snapshot.get("r", 0.0)
        sigma_t = snapshot.get("sigma_t", 0.0)
        rho = snapshot.get("rho", 0.0)

        # 2. Planner provides the initial raw intent trajectory
        raw_plan = planner_component.generate_target_intent()
        band_id = raw_plan.get("band_id", "GS_BAND_0")
        intent_value = raw_plan.get("recommended_curvature_target", 1.40)
        reason = raw_plan.get("reason", "Nominal execution")

        try:
            # 3. Call native Rust directly. PyO3 marshals Python types to Rust primitives automatically.
            # If stall_detected is True, the internal JigEngine applies the mathematical epsilon correction.
            native_result = self.operator.apply_intent(
                band_id,
                intent_value,
                d,
                r,
                sigma_t,
                rho,
                reason,
                stall_detected
            )

            # 4. Extract safe, validated parameters from the returned Python dictionary
            damped_target = native_result.get("damped_value", intent_value)
            active_regime = native_result.get("regime", "UNKNOWN")
            log_reason = native_result.get("reason", "")

            # 5. Walker commits the validated, safe setpoints directly back to the bare-metal engine
            substrate_engine.set_setpoints(
                spin=damped_target,
                pressure=snapshot.get("pressure", 1.0),
                temp=snapshot.get("temp", 1.0)
            )

            if stall_detected:
                logger.warning(f"⚠️ System stall managed! Delta: {execution_delta*1000:.1f}ms. {log_reason}")
            
            return native_result

        except Exception as e:
            logger.error(f"❌ Critical Sovereign Bridge failure: {e}")
            raise e
