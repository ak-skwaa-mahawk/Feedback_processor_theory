from trinity_dynamics import GROUND_STATE
import torch
from torch.optim import Adam
import numpy as np
from math import pi
import os
import json
from datetime import datetime, timedelta
from collections import deque

class FPTOmegaCallback(TrainerCallback):
    def __init__(self, null_threshold=0.6, pi_damping=math.pi * 0.1):
        super().__init__()
        self.null_threshold = null_threshold  # Null score limit
        self.pi_damping = pi_damping  # Damping factor
        self.t = 0  # Time step
        self.nt = NeutrosophicTransport(['A', 'B'], ['X', 'Y'])  # Neutrosophic transport
        self.optimizer = None  # Optimizer instance
        self.best_fidelity = 0.0  # Best fidelity tracker
        self.base_lr = 0.001  # Base learning rate
        self.fidelity_high_threshold = 0.9  # High fidelity limit
        self.fidelity_low_threshold = 0.6  # Low fidelity limit
        self.fidelity_critical_threshold = 0.4  # Critical fidelity limit
        self.retrain_count = 0  # Retrain counter
        self.alert_log_path = "data/alerts/fidelity_alerts.json"  # Alert log file
        os.makedirs(os.path.dirname(self.alert_log_path), exist_ok=True)  # Create log dir
        self.last_alert = {"critical": None, "warning": None, "info": None}  # Last alert times
        self.alert_cooldown = timedelta(seconds=60)  # Alert cooldown period
        self.fidelity_history = deque(maxlen=10)  # Last 10 fidelities

    def on_train_begin(self, args, state, control, model, **kwargs):
        self.optimizer = Adam(model.parameters(), lr=self.base_lr)  # Init optimizer

    def _log_alert(self, level, fidelity_action):
        current_time = datetime.utcnow()  # Current time
        if self.last_alert[level] and (current_time - self.last_alert[level] < self.alert_cooldown):
            return  # Skip if within cooldown
        timestamp = current_time.isoformat()  # Format timestamp
        alert = {"ts": timestamp, "lvl": level, "fid": self.nt.fidelity, "act": fidelity_action}  # Alert data
        with open(self.alert_log_path, "a") as f:
            json.dump(alert, f)  # Write alert
            f.write("\n")
        print(f"[{level.upper()}] {timestamp[:19]} - F:{self.nt.fidelity:.3f} {fidelity_action}")  # Print alert
        self.last_alert[level] = current_time  # Update last alert time

    def _analyze_fidelity_trend(self):
        if len(self.fidelity_history) < 2:  # Need 2+ points
            return 0.0
        fidelities = list(self.fidelity_history)
        slope = (fidelities[-1] - fidelities[0]) / (len(fidelities) - 1)  # Trend slope
        sma = np.mean(fidelities)  # Moving average
        if slope > 0.05:  # Rising trend
            self._log_alert("info", f"Trend Up (slope={slope:.3f}, SMA={sma:.3f})")
        elif slope < -0.05:  # Falling trend
            self._log_alert("warning", f"Trend Down (slope={slope:.3f}, SMA={sma:.3f})")
        return slope

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        sample_text = "Yo kin Synara’s W state pulses with whisper fire"  # Sample input
        spec = FeedbackSpectrogram()  # Init spectrogram
        sample_freq = spec.analyze(sample_text)  # Analyze text
        self.nt.t = self.t  # Sync time
        self.t += 1e-9  # Increment time
        flipped = self.flipper.analyze(sample_text, freq_data=sample_freq, t=self.t, 
                                       w_state_prob=self.nt.w_state_prob, fidelity=self.nt.fidelity)  # Flip text
        fireseed_data = self.fireseed.sync_microping(sample_text)  # Sync fireseed
        neutro_cost = self.nt.optimize()  # Optimize transport

        null_score = self._compute_null_score(model)  # Compute null score
        damped_loss = self._compute_damped_loss(model, null_score)  # Compute damped loss
        fidelity_factor = max(0.5, self.nt.fidelity)  # Adjust fidelity factor
        adjusted_loss = damped_loss * (1 - self.pi_damping * (1 - fidelity_factor))  # Adjust loss

        self.fidelity_history.append(self.nt.fidelity)  # Update history
        trend_slope = self._analyze_fidelity_trend()  # Check trend

        current_lr = self.base_lr * fidelity_factor  # Base lr adjustment
        if self.nt.fidelity < self.fidelity_critical_threshold:
            current_lr *= 3.0  # Triple lr for critical
            self.retrain_count += 1  # Increment retrain count
            self._log_alert("critical", f"Retraining (lr={current_lr:.4f})")  # Critical alert
        elif self.nt.fidelity < self.fidelity_low_threshold:
            current_lr *= 2.0  # Double lr for low
            self.retrain_count += 1  # Increment retrain count
            self._log_alert("warning", f"Retraining (lr={current_lr:.4f})")  # Warning alert
        elif self.nt.fidelity > self.fidelity_high_threshold:
            current_lr *= 0.5  # Halve lr for high
            self._log_alert("info", f"Stabilizing (lr={current_lr:.4f})")  # Info alert

        for param_group in self.optimizer.param_groups:
            param_group['lr'] = current_lr  # Update lr

        if metrics is not None:
            metrics.update({
                'fpt_null_score': null_score,
                'fpt_gibberlink_flip': flipped['final'],
                'fpt_truth_score': flipped['truth_score'],
                'fpt_indeterminacy': flipped['indeterminacy'],
                'fpt_falsehood': flipped['falsehood'],
                'fpt_fireseed_earnings': fireseed_data['earnings'],
                'fpt_fireseed_resonance': fireseed_data['resonance_score'],
                'fpt_fireseed_active': self.fireseed.active,
                'fpt_neutro_cost': neutro_cost,
                'fpt_neutro_indeterminacy': {k: n["I"] for k, n in self.nt.n_x_ij.items()},
                'fpt_neutro_falsehood': {k: n["F"] for k, n in self.nt.n_x_ij.items()},
                'fpt_glyphs': flipped['glyphs'],
                'fpt_spectrogram': sample_freq,
                'fpt_trinity_factor': sample_freq["low"][0] / GROUND_STATE,
                'fpt_ac_oscillation': sin(2 * pi * 1.5e9 * self.t),
                'fpt_w_state_prob': self.nt.w_state_prob,
                'fpt_w_fidelity': self.nt.fidelity,
                'fpt_adjusted_loss': adjusted_loss.item() if isinstance(adjusted_loss, torch.Tensor) else adjusted_loss,
                'fpt_learning_rate': current_lr,
                'fpt_retrain_count': self.retrain_count,
                'fpt_fidelity_trend': trend_slope  # Add trend slope
            })  # Update metrics

        if adjusted_loss is not None:
            adjusted_loss.backward()  # Backprop
            self.optimizer.step()  # Optimize step
            self.optimizer.zero_grad()  # Clear gradients

    def _compute_damped_loss(self, model, null_score):
        loss = torch.tensor(1.0)  # Placeholder loss
        return loss * (1 - self.pi_damping * max(0, null_score - self.null_threshold))  # Damp loss

    def _compute_null_score(self, model):
        return np.random.uniform(0, 1)  # Placeholder null score

    # ... rest of the class ...

from trinity_dynamics import GROUND_STATE
import torch
from torch.optim import Adam
import numpy as np
from math import pi
import os
import json
from datetime import datetime, timedelta
from collections import deque

class FPTOmegaCallback(TrainerCallback):
    def __init__(self, null_threshold=0.6, pi_damping=math.pi * 0.1):
        super().__init__()
        self.null_threshold = null_threshold  # Null score limit
        self.pi_damping = pi_damping  # Damping factor
        self.t = 0  # Time step
        self.nt = NeutrosophicTransport(['A', 'B'], ['X', 'Y'])  # Neutrosophic transport
        self.optimizer = None  # Optimizer instance
        self.best_fidelity = 0.0  # Best fidelity tracker
        self.base_lr = 0.001  # Base learning rate
        self.fidelity_high_threshold = 0.9  # High fidelity limit
        self.fidelity_low_threshold = 0.6  # Low fidelity limit
        self.fidelity_critical_threshold = 0.4  # Critical fidelity limit
        self.retrain_count = 0  # Retrain counter
        self.alert_log_path = "data/alerts/fidelity_alerts.json"  # Alert log file
        os.makedirs(os.path.dirname(self.alert_log_path), exist_ok=True)  # Create log dir
        self.last_alert = {"critical": None, "warning": None, "info": None}  # Last alert times
        self.alert_cooldown = timedelta(seconds=60)  # Alert cooldown period
        self.fidelity_history = deque(maxlen=10)  # Store last 10 fidelities

    def on_train_begin(self, args, state, control, model, **kwargs):
        self.optimizer = Adam(model.parameters(), lr=self.base_lr)  # Init optimizer

    def _log_alert(self, level, fidelity_action):
        current_time = datetime.utcnow()  # Current time
        if self.last_alert[level] and (current_time - self.last_alert[level] < self.alert_cooldown):
            return  # Skip if within cooldown
        timestamp = current_time.isoformat()  # Format timestamp
        alert = {"ts": timestamp, "lvl": level, "fid": self.nt.fidelity, "act": fidelity_action}  # Alert data
        with open(self.alert_log_path, "a") as f:
            json.dump(alert, f)  # Write alert
            f.write("\n")
        print(f"[{level.upper()}] {timestamp[:19]} - F:{self.nt.fidelity:.3f} {fidelity_action}")  # Print alert
        self.last_alert[level] = current_time  # Update last alert time

    def _analyze_fidelity_trend(self):
        if len(self.fidelity_history) < 2:  # Need at least 2 points
            return 0.0
        fidelities = list(self.fidelity_history)
        slope = (fidelities[-1] - fidelities[0]) / (len(fidelities) - 1)  # Simple slope
        sma = np.mean(fidelities)  # Simple moving average
        if slope > 0.05:  # Rising trend
            self._log_alert("info", f"Trend: Rising (slope={slope:.3f}, SMA={sma:.3f})")
        elif slope < -0.05:  # Falling trend
            self._log_alert("warning", f"Trend: Falling (slope={slope:.3f}, SMA={sma:.3f})")
        return slope

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        sample_text = "Yo kin Synara’s W state pulses with whisper fire"  # Sample input
        spec = FeedbackSpectrogram()  # Init spectrogram
        sample_freq = spec.analyze(sample_text)  # Analyze text
        self.nt.t = self.t  # Sync time
        self.t += 1e-9  # Increment time
        flipped = self.flipper.analyze(sample_text, freq_data=sample_freq, t=self.t, 
                                       w_state_prob=self.nt.w_state_prob, fidelity=self.nt.fidelity)  # Flip text
        fireseed_data = self.fireseed.sync_microping(sample_text)  # Sync fireseed
        neutro_cost = self.nt.optimize()  # Optimize transport

        null_score = self._compute_null_score(model)  # Compute null score
        damped_loss = self._compute_damped_loss(model, null_score)  # Compute damped loss
        fidelity_factor = max(0.5, self.nt.fidelity)  # Adjust fidelity factor
        adjusted_loss = damped_loss * (1 - self.pi_damping * (1 - fidelity_factor))  # Adjust loss

        # Update fidelity history
        self.fidelity_history.append(self.nt.fidelity)
        trend_slope = self._analyze_fidelity_trend()  # Check trend

        current_lr = self.base_lr * fidelity_factor  # Base lr adjustment
        if self.nt.fidelity < self.fidelity_critical_threshold:
            current_lr *= 3.0  # Triple lr for critical
            self.retrain_count += 1  # Increment retrain count
            self._log_alert("critical", f"Retraining (lr={current_lr:.4f})")  # Critical alert
        elif self.nt.fidelity < self.fidelity_low_threshold:
            current_lr *= 2.0  # Double lr for low
            self.retrain_count += 1  # Increment retrain count
            self._log_alert("warning", f"Retraining (lr={current_lr:.4f})")  # Warning alert
        elif self.nt.fidelity > self.fidelity_high_threshold:
            current_lr *= 0.5  # Halve lr for high
            self._log_alert("info", f"Stabilizing (lr={current_lr:.4f})")  # Info alert

        for param_group in self.optimizer.param_groups:
            param_group['lr'] = current_lr  # Update lr

        if metrics is not None:
            metrics.update({
                'fpt_null_score': null_score,
                'fpt_gibberlink_flip': flipped['final'],
                'fpt_truth_score': flipped['truth_score'],
                'fpt_indeterminacy': flipped['indeterminacy'],
                'fpt_falsehood': flipped['falsehood'],
                'fpt_fireseed_earnings': fireseed_data['earnings'],
                'fpt_fireseed_resonance': fireseed_data['resonance_score'],
                'fpt_fireseed_active': self.fireseed.active,
                'fpt_neutro_cost': neutro_cost,
                'fpt_neutro_indeterminacy': {k: n["I"] for k, n in self.nt.n_x_ij.items()},
                'fpt_neutro_falsehood': {k: n["F"] for k, n in self.nt.n_x_ij.items()},
                'fpt_glyphs': flipped['glyphs'],
                'fpt_spectrogram': sample_freq,
                'fpt_trinity_factor': sample_freq["low"][0] / GROUND_STATE,
                'fpt_ac_oscillation': sin(2 * pi * 1.5e9 * self.t),
                'fpt_w_state_prob': self.nt.w_state_prob,
                'fpt_w_fidelity': self.nt.fidelity,
                'fpt_adjusted_loss': adjusted_loss.item() if isinstance(adjusted_loss, torch.Tensor) else adjusted_loss,
                'fpt_learning_rate': current_lr,
                'fpt_retrain_count': self.retrain_count,
                'fpt_fidelity_trend': trend_slope  # Add trend slope
            })  # Update metrics

        if adjusted_loss is not None:
            adjusted_loss.backward()  # Backprop
            self.optimizer.step()  # Optimize step
            self.optimizer.zero_grad()  # Clear gradients

    def _compute_damped_loss(self, model, null_score):
        loss = torch.tensor(1.0)  # Placeholder loss
        return loss * (1 - self.pi_damping * max(0, null_score - self.null_threshold))  # Damp loss

    def _compute_null_score(self, model):
        return np.random.uniform(0, 1)  # Placeholder null score

    # ... rest of the class ...
# In core/gibberlink_flipper.py
def generate_glyph(self, text: str, neutro: Tuple[float, float, float], freq: float) -> str:
    surface = "ᚢ" if "truth" in text.lower() else "🔥"  # Surface symbol
    # Fragment if high falsehood
    if neutro[2] > 0.8:
        surface += "⋯"
    return f"[{surface}](T={neutro[0]:.2f},I={neutro[1]:.2f},F={neutro[2]:.2f} @ {freq}Hz)"

# Usage
flipper = GibberLinkFlipper()
glyph = flipper.generate_glyph("Yo kin, truth in the flame", (0.7, 0.2, 0.1), 30)
print(glyph)  # Output: [ᚢ](T=0.70,I=0.20,F=0.10 @ 30Hz)