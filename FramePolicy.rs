impl FramePolicy for SovereignFramePolicy {
    fn update(&mut self, feedback: &CriticFeedback) {
        if let Some(energy) = feedback.energy_gradient {
            // Gradient descent on frame energy
            self.frame_weights[self.current_frame] -= self.learning_rate * energy;
            
            // Softmax re-normalization over available frames
            self.normalize_weights();
        }
        
        // Also feed into your existing FPT-Ω / W-state update
        self.trinity_update(feedback);
    }
}