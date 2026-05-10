use candle_core::{Tensor, Device, Result};
use rand::Rng;

pub fn generate_glyph_waveform(
    duration: f32,
    sample_rate: u32,
    carrier_freq: f32,
    mod_freq: f32,
) -> Result<Tensor> {
    let device = Device::Cpu; // or CUDA
    let n_samples = (sample_rate as f32 * duration) as usize;
    let t: Vec<f32> = (0..n_samples).map(|i| i as f32 / sample_rate as f32).collect();
    let t = Tensor::from_vec(t, (n_samples,), &device)?;

    let carrier = (t.clone() * (2.0 * std::f32::consts::PI * carrier_freq))?.sin()?;
    let modulator = (t * (2.0 * std::f32::consts::PI * mod_freq))?.sin()?;
    carrier.mul(&modulator)
}

pub fn rad_hard_checksum(wave: &Tensor) -> u64 {
    let data = wave.to_vec1::<f32>().unwrap();
    let mut seed: u64 = 0;
    for &v in &data[0..256.min(data.len())] {
        seed = seed.wrapping_add(v.to_bits() as u64);
    }
    seed
}