// === Core Types ===
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum EraFrameId {
    Hilbert,
    Grothendieck,
    Modern,
    FloorBaseline,      // your absolute anchor
    Custom(&'static str),
}

#[derive(Clone, Debug)]
pub struct SovereignState { /* your existing manifold state */ }

#[derive(Clone, Debug)]
pub struct ProjectedState {
    pub frame: EraFrameId,
    pub projected: Vec<f64>,   // coordinates in the chosen frame
    pub coherence: f64,        // how well the projection preserved invariants
}

#[derive(Clone, Debug)]
pub struct Plan {
    pub actions: Vec<Action>,
    pub frame_constraints: Vec<Constraint>,
}

#[derive(Clone, Debug)]
pub struct CriticFeedback {
    pub task_reward: f64,
    pub frame_fitness: f64,
    pub recommended_frame: Option<EraFrameId>,
}

// === Traits (now wired to your existing components) ===
pub trait TemporalProjection {
    fn project(&self, frame: EraFrameId, state: &SovereignState) -> ProjectedState;
    fn inverse_project(&self, frame: EraFrameId, projected: &ProjectedState) -> SovereignState;
}

pub trait FrameAwarePlanner {
    fn plan(&mut self, frame: EraFrameId, projected: &ProjectedState) -> Plan;
}

pub trait FrameAwareWalker {
    fn execute(
        &mut self,
        state: &SovereignState,
        plan: &Plan,
        frame: EraFrameId,
    ) -> SovereignState;
}

pub trait SovereignCritic {
    fn evaluate(
        &mut self,
        frame: EraFrameId,
        real_traj: &[SovereignState],
        projected_traj: &[ProjectedState],
    ) -> CriticFeedback;
}

pub trait FramePolicy {
    fn select_frame(&mut self, state: &SovereignState) -> EraFrameId;
    fn update(&mut self, feedback: &CriticFeedback);
}