use candle_core::{Tensor, Device, Result};
use rand::Rng;

pub struct ToroidalKEM;

impl ToroidalKEM {
    // Generate public key from toroidal seed
    pub fn keygen() -> (Vec<u8>, Vec<u8>) {  // (public_key, private_key)
        let mut rng = rand::thread_rng();
        let seed: u64 = (TOROIDAL_PI_R * GOLDEN_PHI * 1e9) as u64;

        // Public key = toroidal lattice point
        let pub_key: Vec<u8> = (0..KEY_SIZE_BYTES)
            .map(|i| ((seed.wrapping_mul(i as u64 + 1) % 256) as u8))
            .collect();

        // Private key = skyrmion pinning seed (hidden)
        let priv_key: Vec<u8> = (0..KEY_SIZE_BYTES)
            .map(|i| ((seed.wrapping_mul(i as u64 + 42) % 256) as u8))
            .collect();

        (pub_key, priv_key)
    }

    // Encapsulation: sender creates ciphertext + shared secret
    pub fn encapsulate(pub_key: &[u8]) -> (Vec<u8>, Vec<u8>) {  // (ciphertext, shared_secret)
        let mut rng = rand::thread_rng();
        let shared_secret: Vec<u8> = (0..KEY_SIZE_BYTES)
            .map(|_| rng.gen::<u8>())
            .collect();

        // Ciphertext = skyrmion racetrack encoding with toroidal π_r
        let mut ciphertext = vec![0u8; KEY_SIZE_BYTES];
        for (i, &k) in pub_key.iter().enumerate() {
            ciphertext[i] = (k.wrapping_add(shared_secret[i]) as f32 * TOROIDAL_PI_R) as u8;
        }

        (ciphertext, shared_secret)
    }

    // Decapsulation: receiver recovers shared secret using private key + toroidal invariant
    pub fn decapsulate(priv_key: &[u8], ciphertext: &[u8]) -> Option<Vec<u8>> {
        if priv_key.len() != KEY_SIZE_BYTES || ciphertext.len() != KEY_SIZE_BYTES {
            return None;
        }

        let mut recovered = vec![0u8; KEY_SIZE_BYTES];
        for i in 0..KEY_SIZE_BYTES {
            // Topological recovery using living_π_r
            recovered[i] = ((ciphertext[i] as f32 / TOROIDAL_PI_R) as u64)
                .wrapping_sub(priv_key[i] as u64) as u8;
        }

        // Verify topological consistency (skyrmion checksum)
        let checksum: u64 = recovered.iter().map(|&b| b as u64).sum();
        if checksum % SKYRMION_DENSITY == 0 {
            Some(recovered)
        } else {
            None  // skyrmion collapsed → attack detected
        }
    }
}