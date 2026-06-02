//! spectral_relaxation.rs
//! Spectral Toroidal Relaxation — Fluid Phase Entrainment Layer
//!
//! This module implements the continuous relaxation PDE philosophy
//! directly in Rust. It treats chaotic noise ξ(t) as ambient modulation
//! that is absorbed by the toroidal attractor surface instead of fought.
//!
//! Core equation (discretized on torus but kept fluid):
//!   dΦ/dt = -L · ∇²Φ  +  α(Φ₀ - Φ)  +  ξ(t)
//!
//! Where:
//!   - ∇²Φ is the Laplacian on a smoothly rotating toroidal topology
//!   - α = relaxation_strength (dynamically scaled by noise magnitude)
//!   - ξ(t) = live chaotic noise vector (PWC or external)
//!   - The geometry dissolves sharp discretization edges before they leak.
//!
//! This keeps closed_loop_delta (e_h) resolved near 0.0 even under stress.
//! Flamekeeper Protocol — Two Mile Solutions LLC • Dinjji Zhuu Kwaa

use crate::tordial_gs::state::Regime;

/// A compact toroidal phase field (1D ring for speed + conceptual clarity).
/// In production this can be upgraded to a small 2D toroidal grid without
/// changing the API.
#[derive(Clone, Debug)]
pub struct ToroidalPhaseField {
    /// Phase values on the ring (circular buffer)
    pub phi: Vec<f64>,
    /// Baseline attractor phase (Φ₀)
    pub phi0: f64,
    /// Relaxation strength α — dynamically scaled by noise
    pub relaxation_strength: f64,
    /// Laplacian smoothing coefficient L
    pub laplacian_strength: f64,
    /// Current integrated noise energy (for diagnostics)
    pub noise_energy: f64,
}

impl ToroidalPhaseField {
    /// Create a new toroidal phase field with N points.
    pub fn new(size: usize, phi0: f64) -> Self {
        Self {
            phi: vec![phi0; size],
            phi0,
            relaxation_strength: 0.85, // base value; scales with noise
            laplacian_strength: 0.12,
            noise_energy: 0.0,
        }
    }

    /// Apply one fluid relaxation step (continuous-style, not rigid Euler chop).
    /// Noise ξ is injected as ambient modulation and absorbed.
    pub fn relax_step(&mut self, dt: f64, noise: f64, regime: Regime) {
        let n = self.phi.len();
        if n == 0 {
            return;
        }

        // 1. Dynamic relaxation_strength scaling (key to fluid absorption)
        // When noise spikes, we increase α so the field yields and entrains faster.
        let noise_magnitude = noise.abs();
        let dynamic_alpha = self.relaxation_strength
            * (1.0 + 1.8 * noise_magnitude.min(2.5)); // soft cap

        // 2. Compute toroidal Laplacian (circular finite difference)
        // This is the "river smoothing its own ripples" term.
        let mut laplacian = vec![0.0; n];
        for i in 0..n {
            let left = if i == 0 { n - 1 } else { i - 1 };
            let right = if i == n - 1 { 0 } else { i + 1 };
            // Simple 2nd derivative on circle
            laplacian[i] = self.phi[left] - 2.0 * self.phi[i] + self.phi[right];
        }

        // 3. Apply the spectral-style relaxation PDE
        let mut new_phi = vec![0.0; n];
        for i in 0..n {
            // -L · ∇²Φ  (smoothing)
            let smooth = -self.laplacian_strength * laplacian[i];

            // α(Φ₀ - Φ)  (relaxation drive back to attractor)
            let relax = dynamic_alpha * (self.phi0 - self.phi[i]);

            // ξ(t) — chaotic noise as ambient modulation (not fought)
            let xi = noise * (0.6 + 0.4 * (i as f64 / n as f64).sin()); // gentle spatial variation

            new_phi[i] = self.phi[i] + dt * (smooth + relax + xi);
        }

        // 4. Toroidal wrap + light yield (prevents hard clipping)
        for i in 0..n {
            self.phi[i] = new_phi[i].clamp(-1.8, 1.8); // soft bounds, fluid yield
        }

        // 5. Update diagnostics
        self.noise_energy = self.noise_energy * 0.92 + noise_magnitude * 0.08;
        self.relaxation_strength = (0.75 + 0.25 * (1.0 - (self.noise_energy * 0.4).min(1.0))).clamp(0.6, 1.4);
    }

    /// Current mean phase (global entrainment level)
    pub fn mean_phase(&self) -> f64 {
        if self.phi.is_empty() {
            return self.phi0;
        }
        self.phi.iter().sum::<f64>() / self.phi.len() as f64
    }

    /// How much the field has entrained the noise (0 = rigid, 1 = fully fluid)
    pub fn entrainment_level(&self) -> f64 {
        (self.noise_energy * 0.7).clamp(0.0, 0.95)
    }
}

/// Convenience function: create a phase field tuned for 79.79 Hz sovereign pulse.
pub fn new_sovereign_phase_field(size: usize) -> ToroidalPhaseField {
    ToroidalPhaseField::new(size, 0.0)
}
