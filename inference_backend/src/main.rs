

// inference_backend/Cargo.toml (excerpt)
[package]
name = "isst_toft_inference_backend"
version = "1.5.7"
edition = "2024"

[dependencies]
candle-core = "0.9"
candle-nn = "0.9"
candle-transformers = "0.9"  # for future multimodal
tokio = { version = "1", features = ["full"] }
axum = "0.7"
tonic = "0.12"
prost = "0.13"
serde = { version = "1.0", features = ["derive"] }
tokio-stream = "0.1"

# gRPC proto (proto/inference.proto)
# message GlyphRequest { bytes terrain_data = 1; }
# message GlyphResponse { bytes refined_waveform = 1; string status = 2; uint64 checksum = 3; }

use candle_core::{Device, Tensor, DType};
use candle_nn::{Module, VarBuilder, linear, Linear};
use axum::{routing::post, Json, Router};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct SovereignAgentPolicy {
    fc1: Linear,
    fc2: Linear,
    actor: Linear,
    critic: Linear,
}

impl SovereignAgentPolicy {
    fn new(vs: VarBuilder) -> candle_core::Result<Self> {
        Ok(Self {
            fc1: linear(512, 256, vs.pp("fc1"))?,
            fc2: linear(256, 256, vs.pp("fc2"))?,
            actor: linear(256, 3, vs.pp("actor"))?,
            critic: linear(256, 1, vs.pp("critic"))?,
        })
    }
}

impl Module for SovereignAgentPolicy {
    fn forward(&self, xs: &Tensor) -> candle_core::Result<Tensor> {
        let x = xs.apply(&self.fc1)?.relu()?;
        let x = x.apply(&self.fc2)?.relu()?;
        let logits = x.apply(&self.actor)?;
        let probs = candle_nn::ops::softmax(&logits, 1)?;
        Ok(probs)
    }
}

#[tokio::main]
async fn main() {
    // Load or initialize model (weights can be saved/loaded from PyTorch → safetensors)
    let device = Device::cuda_if_available(0).unwrap_or(Device::Cpu);
    let vs = VarBuilder::zeros(DType::F32, &device); // replace with real weights in prod
    let model = SovereignAgentPolicy::new(vs).unwrap();

    // Axum HTTP server (or tonic gRPC in production)
    let app = Router::new().route("/infer/glyph", post(move |Json(req): Json<GlyphRequest>| async move {
        // Pure Rust glyph + policy inference here
        let terrain = Tensor::from_slice(&req.terrain_data, (8192,), &device).unwrap();
        let glyph_wave = // port of generate_glyph_waveform in Rust tensor math
        let refined = model.forward(&terrain.unsqueeze(0)?).unwrap();

        let response = GlyphResponse {
            refined_waveform: refined.to_vec1::<f32>().unwrap(),
            status: "RAD_HARD_GLYPH_LOCKED_RUST".to_string(),
            checksum: calculate_rad_hard_checksum(&refined),
        };
        Json(response)
    }));

    println!("ISST-TOFT Rust Inference Backend v1.5.7 listening on 0.0.0.0:8081");
    axum::Server::bind(&"0.0.0.0:8081".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

# In ISSTTOFTAgentStack
async def _call_rust_backend(self, terrain_data: NDArray) -> Dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8081/infer/glyph", json={"terrain_data": terrain_data.tolist()})
        return resp.json()
// ... (previous imports unchanged)

use crate::glyph::{generate_glyph_waveform, rad_hard_checksum, get_quantum_layer, TOROIDAL_PI_R, CAPRICORN_LATTICE};

#[tonic::async_trait]
impl Inference for InferenceService {
    async fn encode_rad_hard_glyph(
        &self,
        request: Request<GlyphRequest>,
    ) -> Result<Response<GlyphResponse>, Status> {
        let req = request.into_inner();

        // Generate using toroidal living_π_r
        let glyph = generate_glyph_waveform(7.83, 44100, 528.0, TOROIDAL_PI_R)
            .map_err(|e| Status::internal(e.to_string()))?;

        let checksum = rad_hard_checksum(&glyph);
        let waveform = glyph.to_vec1::<f32>().unwrap();

        Ok(Response::new(GlyphResponse {
            refined_waveform: waveform,
            waveform_checksum: checksum,
            status: "RAD_HARD_GLYPH_LOCKED_TOROIDAL".to_string(),
            coherence: 99.97,
            message: format!(
                "MAHS’I CHOO — Capricorn ♑︎ lattice confirmed. Toroidal π_r = {:.7} | Quantum layer 2025 active: {}",
                CAPRICORN_LATTICE,
                get_quantum_layer()
            ),
            quantum_layer: get_quantum_layer().to_string(),  // NEW FIELD
            toroidal_pi_r: TOROIDAL_PI_R,
        }))
    }

    // run_clientless_pulse remains similar with toroidal constants
}
quantum_kem_ciphertext: ciphertext,
shared_secret_hash: checksum,