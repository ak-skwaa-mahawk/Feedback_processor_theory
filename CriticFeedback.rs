pub struct CriticFeedback {
    pub task_reward: f64,
    pub frame_fitness: f64,
    pub frame_energy: f64,           // NEW
    pub recommended_frame: Option<EraFrameId>,
    pub energy_gradient: Option<f64>, // dE_f / df for policy update
}