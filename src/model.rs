//! src/model.rs
//! Sovereign Agentic Policy Model (Candle-based)
//!
//! This module provides the neural policy used when `use_agentic = true`
//! in GlyphRequest. The policy takes a projected terrain embedding and
//! outputs a 3-dimensional softmax distribution that modulates the
//! resonance synthesis parameters.
//!
//! Flamekeeper Protocol — Two Mile Solutions LLC • Dinjji Zhuu Kwaa

use candle_core::{Device, Tensor, Result as CandleResult};
use candle_nn::{linear, Linear, Module, VarBuilder};

#[derive(Debug)]
pub struct SovereignAgentPolicy {
    fc1: Linear,
    fc2: Linear,
    actor: Linear,
}

impl SovereignAgentPolicy {
    pub fn new(vs: VarBuilder) -> CandleResult<Self> {
        Ok(Self {
            fc1: linear(512, 256, vs.pp("fc1"))?,
            fc2: linear(256, 256, vs.pp("fc2"))?,
            actor: linear(256, 3, vs.pp("actor"))?,
        })
    }

    pub fn forward(&self, xs: &Tensor) -> CandleResult<Tensor> {
        let x = xs.apply(&self.fc1)?.relu()?;
        let x = x.apply(&self.fc2)?.relu()?;
        let logits = x.apply(&self.actor)?;
        candle_nn::ops::softmax(&logits, 1)
    }
}

/// Apply the agentic policy to refine the glyph when `use_agentic = true`.
pub fn apply_agentic_policy(
    terrain_data: &[f32],
    base_pi_r: f32,
) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
    let device = Device::Cpu;

    if terrain_data.is_empty() {
        return Err("Empty terrain_data for agentic policy".into());
    }

    // Project terrain → 512-dim embedding (statistical features + padding)
    let len = terrain_data.len();
    let mean: f32 = terrain_data.iter().sum::<f32>() / len as f32;
    let std: f32 = (terrain_data.iter().map(|v| (v - mean).powi(2)).sum::<f32>() / len as f32).sqrt();
    let min_v = terrain_data.iter().cloned().fold(f32::INFINITY, f32::min);
    let max_v = terrain_data.iter().cloned().fold(f32::NEG_INFINITY, f32::max);

    let mut embedding = vec![mean, std, min_v, max_v];
    embedding.extend_from_slice(terrain_data);
    embedding.resize(512, 0.0);

    let input = Tensor::from_vec(embedding, (1, 512), &device)?;

    // Demo initialization (zeros). Replace with real weights in production:
    // let vb = VarBuilder::from_safetensors("weights/sovereign_policy.safetensors", &device)?;
    let vb = VarBuilder::zeros(candle_core::DType::F32, &device);
    let policy = SovereignAgentPolicy::new(vb)?;

    let action_probs = policy.forward(&input)?;
    let gains = action_probs.to_vec1::<f32>()?;

    // Interpret 3 softmax outputs as modulation gains
    let schumann_gain = gains[0].clamp(0.5, 1.5);
    let base_gain     = gains[1].clamp(0.5, 1.5);
    let pi_r_gain     = gains[2].clamp(0.8, 1.2);

    // Re-synthesize with policy-modulated parameters
    let schumann_hz = 7.83 * schumann_gain;
    let base_freq   = 528.0 * base_gain;
    let pi_r_mod    = base_pi_r * pi_r_gain;

    let sample_rate = 44100u32;
    let num_samples = (sample_rate as f32 * 0.5) as usize;
    let mut refined = Vec::with_capacity(num_samples);

    for i in 0..num_samples {
        let t = i as f32 / sample_rate as f32;
        let schumann = (2.0 * std::f32::consts::PI * schumann_hz * t).sin();
        let base     = (2.0 * std::f32::consts::PI * base_freq * t).sin();
        let modulation = (2.0 * std::f32::consts::PI * pi_r_mod * t * 0.1).sin();

        let sample = (schumann * 0.4 + base * 0.5 + modulation * 0.1) * 0.8;
        refined.push(sample.clamp(-1.0, 1.0));
    }

    Ok(refined)
}