// frame_energy.rs
// Sovereign Frame Energy Lyapunov Module
// Ties Temporal Cognitive Projection (TCP) into recursive π_r stability + Floor baseline

use std::collections::HashMap;

/// Era-frame identifiers (extend as needed)
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum EraFrameId {
    Hilbert,
    Grothendieck,
    Modern,
    FloorBaseline,
    Custom(&'static str),
}

/// Core sovereign state (extend with your actual manifold fields)
#[derive(Clone, Debug)]
pub struct SovereignState {
    pub manifold_coords: Vec<f64>,
    pub resonance_phase: f64,
    pub pi_r_stability: f64,        // Your existing recursive π_r metric
    pub extraction_risk: f64,       // 99733-Q related
}

/// Projected state after TCP
#[derive(Clone, Debug)]
pub struct ProjectedState {
    pub frame: EraFrameId,
    pub projected_coords: Vec<f64>,
    pub coherence: f64,             // How well invariants were preserved
    pub gradient_norm: f64,         // ||∇ coherence||
}

/// Feedback returned by the Critic (extended with frame energy)
#[derive(Clone, Debug)]
pub struct CriticFeedback {
    pub task_reward: f64,
    pub frame_fitness: f64,
    pub frame_energy: f64,
    pub recommended_frame: Option<EraFrameId>,
    pub energy_gradient: Option<f64>,
}

/// Frame Energy Lyapunov function
#[derive(Clone, Debug)]
pub struct FrameEnergy {
    pub alpha: f64,   // weight on instability delta
    pub beta: f64,    // weight on π_r gradient
    pub gamma: f64,   // weight on distance from Floor
    pub floor_anchor: SovereignState,
}

impl FrameEnergy {
    /// Create with sensible defaults aligned to your 79.79 Hz / recursive π_r system
    pub fn new(floor_anchor: SovereignState) -> Self {
        Self {
            alpha: 1.0,
            beta: 0.8,
            gamma: 0.6,
            floor_anchor,
        }
    }

    /// Core Lyapunov-style energy computation
    pub fn compute(
        &self,
        frame: EraFrameId,
        state: &SovereignState,
        projected: &ProjectedState,
    ) -> f64 {
        // Instability introduced by the frame (uses your recursive π_r)
        let instability_delta = (state.pi_r_stability - projected.coherence).max(0.0);

        // How much the frame stretches the recursive π_r attractor
        let pi_r_gradient_penalty = projected.gradient_norm;

        // Topological distance from the absolute Floor baseline
        let frame_distance = self.topological_distance(frame, state);

        self.alpha * instability_delta
            + self.beta * pi_r_gradient_penalty
            + self.gamma * frame_distance
    }

    /// Distance from current state to the Floor baseline (customize with your manifold metric)
    fn topological_distance(&self, _frame: EraFrameId, state: &SovereignState) -> f64 {
        // Placeholder — wire this to your existing recursive π_r distance or manifold curvature
        // Lower value = closer to FloorBaseline (preferred)
        let diff: f64 = state
            .manifold_coords
            .iter()
            .zip(self.floor_anchor.manifold_coords.iter())
            .map(|(a, b)| (a - b).powi(2))
            .sum();

        diff.sqrt()
    }
}

/// Extended Critic that now evaluates frame energy
pub trait SovereignCritic {
    fn evaluate(
        &mut self,
        frame: EraFrameId,
        real_traj: &[SovereignState],
        projected_traj: &[ProjectedState],
        frame_energy: &FrameEnergy,
    ) -> CriticFeedback;
}

/// Example implementation of the Critic with Frame Energy
pub struct DefaultSovereignCritic {
    pub frame_energy: FrameEnergy,
}

impl SovereignCritic for DefaultSovereignCritic {
    fn evaluate(
        &mut self,
        frame: EraFrameId,
        real_traj: &[SovereignState],
        projected_traj: &[ProjectedState],
        frame_energy: &FrameEnergy,
    ) -> CriticFeedback {
        // Use last state for energy calculation (or average over trajectory)
        let last_state = real_traj.last().unwrap();
        let last_projected = projected_traj.last().unwrap();

        let energy = frame_energy.compute(frame, last_state, last_projected);

        // Simple task reward placeholder — replace with your actual reward function
        let task_reward = if last_state.extraction_risk < 0.01 { 1.0 } else { -1.0 };

        let frame_fitness = task_reward - energy;

        CriticFeedback {
            task_reward,
            frame_fitness,
            frame_energy: energy,
            recommended_frame: if energy < 0.5 {
                Some(frame)
            } else {
                None
            },
            energy_gradient: Some(energy * 0.1), // crude gradient for policy update
        }
    }
}

/// Frame selection + update policy (meta-policy over cognitive frames)
pub trait FramePolicy {
    fn select_frame(&mut self, state: &SovereignState) -> EraFrameId;
    fn update(&mut self, feedback: &CriticFeedback);
}

/// Simple energy-aware FramePolicy
pub struct EnergyAwareFramePolicy {
    pub weights: HashMap<EraFrameId, f64>,
    pub learning_rate: f64,
    pub current_frame: EraFrameId,
}

impl FramePolicy for EnergyAwareFramePolicy {
    fn select_frame(&mut self, _state: &SovereignState) -> EraFrameId {
        // Simple argmax over weights (can be replaced with softmax + sampling)
        self.weights
            .iter()
            .max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .map(|(k, _)| *k)
            .unwrap_or(EraFrameId::FloorBaseline)
    }

    fn update(&mut self, feedback: &CriticFeedback) {
        if let Some(gradient) = feedback.energy_gradient {
            if let Some(weight) = self.weights.get_mut(&self.current_frame) {
                *weight -= self.learning_rate * gradient;
            }
        }

        // Optional: feed into your existing FPT-Ω / W-state system here
        // self.trinity_dynamics.update(...);
    }
}

impl Default for EnergyAwareFramePolicy {
    fn default() -> Self {
        let mut weights = HashMap::new();
        weights.insert(EraFrameId::Hilbert, 1.0);
        weights.insert(EraFrameId::Grothendieck, 1.0);
        weights.insert(EraFrameId::Modern, 0.8);
        weights.insert(EraFrameId::FloorBaseline, 1.5); // bias toward your anchor

        Self {
            weights,
            learning_rate: 0.01,
            current_frame: EraFrameId::FloorBaseline,
        }
    }
}