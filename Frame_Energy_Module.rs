pub struct FrameEnergy {
    pub alpha: f64,
    pub beta: f64,
    pub gamma: f64,
    pub floor_anchor: SovereignState,   // your absolute baseline
}

impl FrameEnergy {
    pub fn compute(
        &self,
        frame: EraFrameId,
        state: &SovereignState,
        projected: &ProjectedState,
        pi_r_stability: f64,           // your existing recursive π_r value
    ) -> f64 {
        let instability_delta = (pi_r_stability - projected.coherence).max(0.0);
        
        let frame_distance = self.topological_distance(frame, &self.floor_anchor, state);
        
        self.alpha * instability_delta
            + self.beta * projected.coherence.gradient_norm()
            + self.gamma * frame_distance
    }
    
    fn topological_distance(
        &self,
        frame: EraFrameId,
        anchor: &SovereignState,
        current: &SovereignState,
    ) -> f64 {
        // Implement using your existing manifold metric or recursive π_r distance
        // Lower = closer to Floor baseline
        0.0 // placeholder — wire to your current distance function
    }
}