use candle_core::{Device, Tensor, Result};
use candle_nn::{Module, VarBuilder, linear, Linear};

#[derive(Debug)]
pub struct SovereignAgentPolicy {
    fc1: Linear,
    fc2: Linear,
    actor: Linear,
}

impl SovereignAgentPolicy {
    pub fn new(vs: VarBuilder) -> Result<Self> {
        Ok(Self {
            fc1: linear(512, 256, vs.pp("fc1"))?,
            fc2: linear(256, 256, vs.pp("fc2"))?,
            actor: linear(256, 3, vs.pp("actor"))?,
        })
    }

    pub fn forward(&self, xs: &Tensor) -> Result<Tensor> {
        let x = xs.apply(&self.fc1)?.relu()?;
        let x = x.apply(&self.fc2)?.relu()?;
        let logits = x.apply(&self.actor)?;
        candle_nn::ops::softmax(&logits, 1)
    }
}