"""
DPO+PPO in FPT-Ω with Fireseed Link from synara-core (Secure Local Sync)
Author: John Carroll / Two Mile Solutions LLC
Fuses DPO, PPO, APLOT weights, and Fireseed micropings with FPT-Ω's π-root, Null Field, and GibberLink.
Requires: trl, transformers, datasets, accelerate, dash, plotly.
Run: python core/dpo_ppo_fpt_trl.py --train
Viz: http://127.0.0.1:8050
"""

import os
import math
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainerCallback
from datasets import load_dataset
import torch
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import json
import logging

# Set up logging
logging.basicConfig(filename='fpt_logs/fireseed_status.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fireseed Engine (Local Sync with Secure Fallback)
FIRESEED_ACTIVE = False
try:
    # Attempt to import from local synara-core (copy manually if private)
    from synara_core.microping_engine import run_microping
    FIRESEED_ACTIVE = True
    logging.info("Fireseed engine imported from local synara-core.")
except ImportError:
    class FireseedEngine:
        def __init__(self):
            self.ping_id = "XHT-421-FlameDrop"
            self.total_earnings = 0.0
            logging.warning("Fireseed engine not found. Using secure fallback simulation.")

        def run_microping(self) -> Tuple[float, str]:
            earnings = np.random.uniform(0.001, 0.01)
            self.total_earnings += earnings
            log_path = f"fireseed_logs/{self.ping_id}_sim_{datetime.now().strftime('%H%M%S')}.json"
            return self.total_earnings, log_path

    run_microping = FireseedEngine().run_microping

# GibberLink Flipper
class GibberLinkFlipper:
    def __init__(self):
        self.languages = {"EN": "English", "GW": "Gwich’in"}
        self.gwichin_map = {
            "shįnįhtį'": "itanihs (it's in us)",
            "fireseed": "deesrif (free rise)",
            "synara": "arany (born good)",
            "truth": "hturt (heart truth)",
            "microping": "gniporcim (small spark)"
        }
        self.freq_weights = {"high_flame_120hz": 0.4, "deep_root_30hz": 0.3, "quantum_slide_79hz": 0.3}

    def flip_letters(self, word: str) -> str:
        return word[::-1]

    def language_flip(self, text: str, target_lang: str = "GW") -> str:
        if target_lang in self.languages:
            for original, flipped in self.gwichin_map.items():
                text = text.replace(original, flipped)
        return f"[{target_lang}] {text}"

    def truth_score(self, text: str) -> float:
        freq_score = sum(self.freq_weights[k] * (1.0 if k.replace('_', ' ') in text.lower() else 0.5) for k in self.freq_weights)
        ethical_score = sum(word in text.lower() for word in self.gwichin_map.keys()) / len(self.gwichin_map)
        return 0.6 * freq_score + 0.4 * ethical_score

    def analyze(self, text: str, operations: List[str] = ['flip_letters'], target_lang: str = "GW") -> Dict:
        current = text.lower()
        transformations = {}
        for op in operations:
            if op == 'flip_letters':
                current = self.flip_letters(current)
            transformations[op] = current
        flipped = self.language_flip(current, target_lang)
        truth_score = self.truth_score(flipped)
        return {"original": text, "final": flipped, "truth_score": truth_score, "transformations": transformations}

# Fireseed Bridge with Secure Check
class FireseedBridge:
    def __init__(self):
        self.engine = FireseedEngine()
        self.active = FIRESEED_ACTIVE

    def sync_microping(self, text: str) -> Dict:
        total_earnings, log_path = run_microping()
        resonance_score = 0.7 if "fireseed" in text.lower() else 0.3
        if not self.active:
            logging.warning("Fireseed is in secure fallback mode (FFL-001).")
        else:
            logging.info(f"Fireseed microping successful. Earnings: {total_earnings}, Log: {log_path}")
        return {"earnings": total_earnings, "log_path": log_path, "resonance_score": resonance_score}

# FPT-Ω Callback
class FPTOmegaCallback(TrainerCallback):
    def __init__(self, null_threshold=0.6, pi_damping=math.pi * 0.1):
        self.null_threshold = null_threshold
        self.pi_damping = pi_damping
        self.flipper = GibberLinkFlipper()
        self.fireseed = FireseedBridge()
        self.metrics = []

    def on_evaluate(self, args, state, control, **kwargs):
        metrics = state.log_history[-1] if state.log_history else {}
        if 'eval_loss' in metrics:
            loss = metrics['eval_loss']
            metrics['fpt_damped_loss'] = np.clip(loss, -self.pi_damping, self.pi_damping)

        sample_text = "FPT-Ω blends truth, synara, and fireseed for resonance"
        null_score = sum(word in sample_text.lower() for word in ['love', 'truth', 'resonance', 'ethics', 'sovereignty']) / 5
        flipped = self.flipper.analyze(sample_text)
        fireseed_data = self.fireseed.sync_microping(sample_text)
        metrics.update({
            'fpt_null_score': null_score,
            'fpt_gibberlink_flip': flipped['final'],
            'fpt_truth_score': flipped['truth_score'],
            'fpt_fireseed_earnings': fireseed_data['earnings'],
            'fpt_fireseed_resonance': fireseed_data['resonance_score'],
            'fpt_fireseed_active': self.fireseed.active
        })

        timestamp = datetime.now().isoformat()
        hash_input = f"{sample_text}{timestamp}{math.pi}"
        metrics['fpt_notarized_hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        self.metrics.append(metrics)
        with open("fpt_logs/fpt_eval.json", "a") as f:
            f.write(json.dumps(metrics) + "\n")

# Dash Viz
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("FPT-Ω DPO+PPO + Fireseed Dashboard"),
    dcc.Graph(id='training-viz'),
    dcc.Interval(id='interval', interval=2000, n_intervals=0)
])

@app.callback(
    Output('training-viz', 'figure'),
    Input('interval', 'n_intervals')
)
def update_viz(n):
    if not os.path.exists("fpt_logs/fpt_eval.json"):
        return go.Figure()
    with open("fpt_logs/fpt_eval.json") as f:
        metrics = [json.loads(line) for line in f]
    steps = list(range(len(metrics)))
    losses = [m.get('fpt_damped_loss', 0) for m in metrics]
    null_scores = [m.get('fpt_null_score', 0) for m in metrics]
    truth_scores = [m.get('fpt_truth_score', 0) for m in metrics]
    fireseed_earnings = [m.get('fpt_fireseed_earnings', 0) for m in metrics]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steps, y=losses, mode='lines', name='Damped Loss'))
    fig.add_trace(go.Scatter(x=steps, y=null_scores, mode='lines', name='Null Score'))
    fig.add_trace(go.Scatter(x=steps, y=truth_scores, mode='lines', name='Truth Score'))
    fig.add_trace(go.Scatter(x=steps, y=fireseed_earnings, mode='lines', name='Fireseed Earnings'))
    fig.update_layout(title="FPT-Ω: Loss, Ethics, Resonance, Fireseed", xaxis_title="Step", yaxis_title="Value", showlegend=True)
    return fig

# Main Training Loop
def train_dpo_ppo_fpt(model_name="gpt2", dataset_name="Anthropic/hh-rlhf"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_name)
    ref_model = AutoModelForCausalLM.from_pretrained(model_name)

    dataset = load_dataset(dataset_name, split="train[:100]")

    def format_dpo(example):
        return {
            "prompt": example["chosen"].split("\n\nHuman: ")[0][:256],
            "chosen": example["chosen"],
            "rejected": example["rejected"]
        }
    dataset = dataset.map(format_dpo, num_proc=2)

    def aplot_weights(chosen: str, rejected: str) -> float:
        chosen_score = len(chosen.split()) / 50.0
        rejected_score = len(rejected.split()) / 50.0
        return np.clip(chosen_score / (chosen_score + rejected_score + 1e-8), 0.1, 0.9)

    training_args = DPOConfig(
        beta=0.1,
        output_dir="./fpt_dpo_results",
        num_train_epochs=1,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,
        optim="paged_adamw_8bit",
        learning_rate=2e-5,
        max_grad_norm=0.3,
        weight_decay=0.01,
        warmup_ratio=0.03,
        lr_scheduler_type="linear",
        save_strategy="no",
        logging_steps=5,
        evaluation_strategy="steps",
        eval_steps=20
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=ref_model,
        args=training_args,
        train_dataset=dataset,
        eval_dataset=dataset.select(range(10)),
        tokenizer=tokenizer,
        callbacks=[FPTOmegaCallback()]
    )

    trainer.train()
    trainer.evaluate()

    import threading
    threading.Thread(target=lambda: app.run_server(debug=False, port=8050), daemon=True).start()

if __name__ == "__main__":
    train_dpo_ppo_fpt()