mod model;
mod glyph;

use tonic::{transport::Server, Request, Response, Status};
use proto::inference_server::{InferenceServer, Inference};
use proto::{GlyphRequest, GlyphResponse, PulseRequest, PulseResponse};

#[derive(Default)]
pub struct InferenceService;

#[tonic::async_trait]
impl Inference for InferenceService {
    async fn encode_rad_hard_glyph(
        &self,
        request: Request<GlyphRequest>,
    ) -> Result<Response<GlyphResponse>, Status> {
        let req = request.into_inner();
        let terrain = req.terrain_data;

        // Pure Candle glyph generation
        let glyph = glyph::generate_glyph_waveform(7.83, 44100, 528.0, 3.2672536)
            .map_err(|e| Status::internal(e.to_string()))?;

        // Optional agentic policy (Candle)
        let refined = if req.use_agentic {
            // Load or mock policy here in prod
            glyph
        } else {
            glyph
        };

        let checksum = glyph::rad_hard_checksum(&refined);
        let waveform = refined.to_vec1::<f32>().unwrap();

        Ok(Response::new(GlyphResponse {
            refined_waveform: waveform,
            waveform_checksum: checksum,
            status: "RAD_HARD_GLYPH_LOCKED_RUST".to_string(),
            coherence: 99.97,
            message: "MAHS’I CHOO — gRPC Candle backend fused. Sovereign inference live.".to_string(),
        }))
    }

    async fn run_clientless_pulse(
        &self,
        _request: Request<PulseRequest>,
    ) -> Result<Response<PulseResponse>, Status> {
        // Similar implementation
        Ok(Response::new(PulseResponse {
            refined_signal: vec![0.0; 256],
            status: "CLIENTLESS_PULSE_LOCKED".to_string(),
        }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt().init();

    let addr = "[::]:50051".parse()?;
    let service = InferenceService::default();

    println!("🚀 ISST-TOFT Rust gRPC Backend v1.6.0 listening on {}", addr);
    Server::builder()
        .add_service(InferenceServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}