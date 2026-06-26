use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use sha2::{Sha256, Digest};

use crate::core::actor::DecisionRecord;

#[derive(Debug, Clone)]
pub struct RichBlockPayload {
    pub timestamp: u64,
    pub source_actor_id: u64,
    pub compute: f64,
    pub distance_to_target: f64,
    pub decision_status: u32,
    pub velocity: Vec<f64>,
    pub forcing_magnitude: f64,
    pub recent_decisions: Vec<DecisionRecord>, // last N records
}

#[derive(Debug, Clone)]
pub struct MeshBlock {
    pub index: u64,
    pub previous_hash: String,
    pub nonce: u64,
    pub hash: String,
    pub payload: RichBlockPayload,
}

impl MeshBlock {
    pub fn calculate_hash(&self) -> String {
        let mut hasher = Sha256::new();
        hasher.update(self.index.to_string());
        hasher.update(&self.previous_hash);
        hasher.update(self.nonce.to_string());
        hasher.update(serde_json::to_string(&self.payload).unwrap_or_default());
        format!("{:x}", hasher.finalize())
    }
}

#[pyclass]
pub struct PySubstrateMeshBus {
    chain: Arc<Mutex<Vec<MeshBlock>>>,
    pub base_forcing_scale: f64,
    last_hash: Arc<Mutex<String>>,
}

#[pymethods]
impl PySubstrateMeshBus {
    #[new]
    pub fn new(base_forcing_scale: f64) -> Self {
        let genesis = MeshBlock {
            index: 0,
            previous_hash: "0000000000000000...".to_string(),
            nonce: 0,
            hash: "0000000000000000...".to_string(),
            payload: RichBlockPayload {
                timestamp: 0,
                source_actor_id: 0,
                compute: 0.0,
                distance_to_target: 0.0,
                decision_status: 0,
                velocity: vec![],
                forcing_magnitude: 0.0,
                recent_decisions: vec![],
            },
        };
        PySubstrateMeshBus {
            chain: Arc::new(Mutex::new(vec![genesis])),
            base_forcing_scale,
            last_hash: Arc::new(Mutex::new("0000000000000000...".to_string())),
        }
    }

    pub fn publish_rich_block(
        &self,
        timestamp: u64,
        source_actor_id: u64,
        compute: f64,
        distance_to_target: f64,
        decision_status: u32,
        velocity: Vec<f64>,
        forcing_magnitude: f64,
        recent_decisions: Vec<DecisionRecord>,
    ) {
        let mut chain = self.chain.lock().unwrap();
        let mut last_hash = self.last_hash.lock().unwrap();

        let payload = RichBlockPayload {
            timestamp,
            source_actor_id,
            compute,
            distance_to_target,
            decision_status,
            velocity,
            forcing_magnitude,
            recent_decisions,
        };

        let new_block = MeshBlock {
            index: chain.len() as u64,
            previous_hash: last_hash.clone(),
            nonce: 0, // can be incremented later for sequencing
            hash: String::new(),
            payload,
        };

        let final_hash = new_block.calculate_hash();
        let mut final_block = new_block;
        final_block.hash = final_hash.clone();

        chain.push(final_block);
        *last_hash = final_hash;
    }

    pub fn get_event_count(&self) -> usize {
        self.chain.lock().unwrap().len()
    }

    pub fn get_latest_state_for_agent(&self, actor_id: u64) -> Option<(u64, f64, f64, u32)> {
        let chain = self.chain.lock().unwrap();
        chain.iter().rev().find(|b| b.payload.source_actor_id == actor_id)
            .map(|b| (
                b.payload.timestamp,
                b.payload.compute,
                b.payload.distance_to_target,
                b.payload.decision_status,
            ))
    }

    pub fn get_rich_events_for_agent(&self, actor_id: u64, limit: usize) -> Vec<(u64, Vec<f64>, f64, f64, f64, u32)> {
        let chain = self.chain.lock().unwrap();
        chain.iter()
            .rev()
            .filter(|b| b.payload.source_actor_id == actor_id)
            .take(limit)
            .map(|b| (
                b.payload.timestamp,
                b.payload.velocity.clone(),
                b.payload.forcing_magnitude,
                b.payload.compute,
                b.payload.distance_to_target,
                b.payload.decision_status,
            ))
            .collect()
    }

    pub fn total_energy(&self) -> f64 {
        self.chain.lock().unwrap().iter().map(|b| b.payload.forcing_magnitude).sum()
    }

    pub fn verify_chain_integrity(&self) -> bool {
        let chain = self.chain.lock().unwrap();
        for i in 1..chain.len() {
            if chain[i].previous_hash != chain[i-1].hash {
                return false;
            }
        }
        true
    }
}