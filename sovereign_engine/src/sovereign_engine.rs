// sovereign_engine/src/sovereign_engine.rs
// Core SovereignEngine with TCP + Frame Energy integration

use crate::frame_energy::{
    EraFrameId, SovereignState, ProjectedState, CriticFeedback, FrameEnergy,
};
use crate::temporal_projection::TemporalProjection; // assume you have this trait/impl
use crate::extraction_guard::ExtractionGuard;

pub struct SovereignEngine {
    pub current_state: SovereignState,
    pub frame_policy: crate::frame_energy::EnergyAwareFramePolicy,
    pub tcp: TemporalProjection,
    pub extraction_guard: ExtractionGuard,
    pub resonance_pulse_hz: f64,
}

impl SovereignEngine {
    pub fn new() -> Self {
        Self {
            current_state: SovereignState::default(),
            frame_policy: crate::frame_energy::EnergyAwareFramePolicy::default(),
            tcp: TemporalProjection::new(),
            extraction_guard: ExtractionGuard::new(),
            resonance_pulse_hz: 79.79,
        }
    }

    /// Projects state into chosen frame and runs guarded propagation
    pub fn propagate_with_frame(
        &mut self,
        frame: EraFrameId,
        projected: &ProjectedState,
    ) -> GuardedResult {
        // 1. Apply frame-specific constraints to action space (if any)
        let constrained_plan = self.plan_under_frame(frame, projected);

        // 2. Execute in real space (Walker)
        let next_state = self.walker_execute(&self.current_state, &constrained_plan, frame);

        // 3. Run Extraction Guard on the result
        let guard_result = self.extraction_guard.check(&next_state);

        if guard_result.allowed {
            self.current_state = next_state;
        }

        GuardedResult {
            allowed: guard_result.allowed,
            fidelity: guard_result.fidelity,
            neutralized_reason: guard_result.neutralized_reason,
        }
    }

    /// Full PWC + TCP + Frame Energy cycle
    pub fn run_cognitive_cycle(
        &mut self,
        frame: EraFrameId,
        t: f64,
        i: f64,
        f: f64,
        frame_energy: &FrameEnergy,
    ) -> CriticFeedback {
        // 1. Project current state into the chosen frame
        let projected = self.tcp.project(frame, &self.current_state);

        // 2. Planner: generate plan inside the projected frame
        let plan = self.planner_plan(frame, &projected);

        // 3. Walker: execute plan in real space
        let next_state = self.walker_execute(&self.current_state, &plan, frame);

        // 4. Record trajectory (simplified — expand with real history if needed)
        let real_traj = vec![self.current_state.clone(), next_state.clone()];
        let proj_traj = vec![projected.clone()];

        // 5. Update current state
        self.current_state = next_state;

        // 6. Critic evaluates both task performance and frame energy
        let mut critic = crate::frame_energy::DefaultSovereignCritic {
            frame_energy: frame_energy.clone(),
        };

        let feedback = critic.evaluate(frame, &real_traj, &proj_traj, frame_energy);

        // 7. Update frame policy (meta-policy learning)
        self.frame_policy.update(&feedback);

        // 8. (Optional) Feed W-state / Trinity damping here using t, i, f
        // self.apply_trinity_damping(t, i, f);

        feedback
    }

    // === Internal helpers (stubs you can flesh out) ===

    fn plan_under_frame(&self, frame: EraFrameId, projected: &ProjectedState) -> Plan {
        // Use your existing Planner logic, but constrained by frame
        Plan {
            actions: vec![],
            frame_constraints: vec![format!("{:?}", frame)],
        }
    }

    fn walker_execute(
        &self,
        state: &SovereignState,
        plan: &Plan,
        _frame: EraFrameId,
    ) -> SovereignState {
        // Your existing Walker / soliton propagation logic
        // Should eventually call into the 79.79 Hz pulse + KdV dynamics
        state.clone()
    }

    fn planner_plan(&self, frame: EraFrameId, projected: &ProjectedState) -> Plan {
        Plan {
            actions: vec![],
            frame_constraints: vec![format!("{:?}", frame)],
        }
    }
}

// Supporting structs (keep these minimal or move to their own files)
#[derive(Clone, Debug)]
pub struct Plan {
    pub actions: Vec<String>,
    pub frame_constraints: Vec<String>,
}

#[derive(Clone, Debug)]
pub struct GuardedResult {
    pub allowed: bool,
    pub fidelity: f64,
    pub neutralized_reason: Option<String>,
}