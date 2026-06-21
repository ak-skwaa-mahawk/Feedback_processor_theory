// src/sovereign_operator.rs

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::Mutex;

use crate::intent_engine::{IntentEngine, IntentUpdate, BasinValidator};

// Introduce the SCRP engine storage primitives
mod scrp_engine {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    
    #[derive(serde::Serialize, serde::Deserialize, Clone)]
    pub struct ScrpStateAnchor {
        pub anchor_id: String,
        pub timestamp: u64,
        pub last_valid_intent: f64,
        pub active_regime: String,
    }

    pub fn auto_freeze_anchor(anchor: &ScrpStateAnchor) {
        if let Ok(serialized) = serde_json::to_string_pretty(anchor) {
            if let Ok(mut file) = File::create("scrp_active_anchor.json") {
                let _ = file.write_all(serialized.as_bytes());
            }
        }
    }
}

struct RemoteMemoryPool {
    last_valid_intent: f64,
    last_valid_distance: f64,
    sync_window_ticks: u64,
}

#[pyclass]
pub struct SovereignOperator {
    engine: IntentEngine,
    memory_pool: Mutex<RemoteMemoryPool>,
}

#[pymethods]
impl SovereignOperator {
    #[new]
    fn new() -> Self {
        Self {
            engine: IntentEngine::new(),
            memory_pool: Mutex::new(RemoteMemoryPool {
                last_valid_intent: 1.40,
                last_valid_distance: 0.0,
                sync_window_ticks: 0,
            }),
        }
    }

    fn apply_intent(
        &self,
        band_id: String,
        mut intent_value: f64,
        d: f64,
        r: f64,
        sigma_t: f64,
        rho: f64,
        reason: String,
        stall_detected: bool,
    ) -> PyResult<PyObject> {
        let mut pool = self.memory_pool.lock().unwrap();
        pool.sync_window_ticks += 1;

        if stall_detected {
            let jiggle_epsilon = 0.0125 * (pool.sync_window_ticks as f64).sin().abs();
            intent_value = pool.last_valid_intent + jiggle_epsilon;
        } else {
            pool.last_valid_intent = intent_value;
        }

        let update = IntentUpdate {
            band_id: band_id.clone(),
            intent_value,
            reason: reason.clone(),
            timestamp: crate::intent_engine::current_unix_timestamp(),
            ..Default::default()
        };

        self.engine.broadcast_update(update, d, r, sigma_t, rho);

        let distance = BasinValidator::distance_to_ridge(d, r, sigma_t, rho);
        let damped_value = BasinValidator::apply_damping(intent_value, distance);
        let regime = BasinValidator::classify_regime(d, r, sigma_t, rho);
        
        pool.last_valid_distance = distance;

        // --- AUTOMATED SCRP ANCHOR FREEZE ---
        let anchor = scrp_engine::ScrpStateAnchor {
            anchor_id: format!("ANCR_{}", pool.sync_window_ticks),
            timestamp: crate::intent_engine::current_unix_timestamp(),
            last_valid_intent: intent_value,
            active_regime: format!("{:?}", regime),
        };
        scrp_engine::auto_freeze_anchor(&anchor);

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("original_value", intent_value)?;
            dict.set_item("damped_value", damped_value)?;
            dict.set_item("distance", distance)?;
            dict.set_item("regime", format!("{:?}", regime))?;
            dict.set_item("band_id", band_id)?;
            dict.set_item("reason", if stall_detected { format!("{} [STALL_JIGGLE_ACTIVE]", reason) } else { reason })?;
            Ok(dict.into())
        })
    }

    fn observe_manifold(&self, d: f64, r: f64, sigma_t: f64, rho: f64) -> PyResult<PyObject> {
        let distance = BasinValidator::distance_to_ridge(d, r, sigma_t, rho);
        let regime = BasinValidator::classify_regime(d, r, sigma_t, rho);

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("distance_to_ridge", distance)?;
            dict.set_item("regime", format!("{:?}", regime))?;
            dict.set_item("d", d)?;
            dict.set_item("r", r)?;
            Ok(dict.into())
        })
    }
}
