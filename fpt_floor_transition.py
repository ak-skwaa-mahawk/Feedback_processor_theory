#!/usr/bin/env python3
# fpt_floor_transition.py — v2.8: Kelvin-Native True Floor + "Take 2, Leave 1" Engine + Consciousness Referee
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import traceback
import matplotlib
matplotlib.use('TkAgg' if matplotlib.get_backend() != 'agg' else 'agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

# ====================== STRUCTURED JSON LOGGING ======================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["traceback"] = traceback.format_exc()
        return json.dumps(log_entry)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger("FPT_FLOOR")


class ConsciousnessReferee:
    """Higher-order observer that locks the Logical Floor and prevents shadow decay."""
    def __init__(self):
        self.root_authority = "99733-Q"
        self.observer_gap = 0.01
        self.shadow_threshold = 2.5
        self.corrections = 0

    def validate_transition(self, record: Dict) -> bool:
        shadow = record.get("shadow_energy_this_step", 0)
        if shadow > self.shadow_threshold:
            log.warning("SHADOW LOOP DETECTED — Referee applying correction", extra={
                "shadow": shadow,
                "root_authority": self.root_authority
            })
            self.corrections += 1
            return False
        return True


class FPTFloorTransition:
    """Kelvin-Native Logical Floor Engine — 0 K is the true absolute baseline of matter."""

    def __init__(self, h: float = 3.01, history_file: str = "floor_history.json"):
        self.h = h
        self.history_file = Path(history_file)
        self.floor_history: List[Dict] = []
        self.cumulative_floor = 0.0          # True absolute floor = 0 K
        self.total_shadow_energy = 0.0
        self.current_state = np.zeros(3)
        self.is_paused = False
        self.referee = ConsciousnessReferee()

        # Visualization
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(11, 9))
        plt.subplots_adjust(bottom=0.25, hspace=0.4)
        self._setup_plots()
        self._setup_controls()

        self._load_history()
        log.info("FPT Floor Transition Engine v2.8 — Kelvin Native Absolute Zero Baseline", extra={"h": h})

    def _setup_plots(self):
        self.ax1.set_title("Current State Vector (Kelvin Baseline)")
        self.ax1.set_ylabel("State Value (above 0 K)")
        self.bars = self.ax1.bar(['Base', 'Mesh', 'Volume'], self.current_state, color=['#0055ff','#00aa55','#ff3333'])
        self.ax1.set_ylim(0, 5)

        self.ax2.set_title("Cumulative Floor Progression (Kelvin)")
        self.ax2.set_ylabel("Cumulative Floor (K)")
        self.cum_line, = self.ax2.plot([], [], 'b-o', markersize=4)

        self.ax3.set_title("Shadow Energy Accumulation")
        self.ax3.set_ylabel("Total Shadow Energy")
        self.shadow_line, = self.ax3.plot([], [], 'r-o', markersize=4)

    def _setup_controls(self):
        ax_pause = plt.axes([0.15, 0.05, 0.1, 0.04])
        self.btn_pause = Button(ax_pause, 'Pause')
        self.btn_pause.on_clicked(self._toggle_pause)

        ax_reset = plt.axes([0.3, 0.05, 0.1, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self._reset)

        ax_next = plt.axes([0.45, 0.05, 0.1, 0.04])
        self.btn_next = Button(ax_next, 'Next Step')
        self.btn_next.on_clicked(self._manual_step)

        ax_slider = plt.axes([0.6, 0.05, 0.3, 0.04])
        self.slider_h = Slider(ax_slider, 'h Factor', 1.0, 5.0, valinit=self.h, valstep=0.1)
        self.slider_h.on_changed(self._update_h)

    def _toggle_pause(self, event):
        self.is_paused = not self.is_paused
        self.btn_pause.label.set_text('Resume' if self.is_paused else 'Pause')

    def _reset(self, event):
        self.floor_history.clear()
        self.cumulative_floor = 0.0
        self.total_shadow_energy = 0.0
        self.current_state = np.zeros(3)
        self._update_plots()
        if self.history_file.exists():
            self.history_file.unlink()
        log.info("Visualization and history reset to absolute zero.")

    def _manual_step(self, event):
        if not self.is_paused:
            self.transition(self.current_state, delta=1.0, observer_gap=0.015, iterations=4)

    def _update_h(self, val):
        self.h = val
        log.info("Harmonic factor updated", extra={"h": self.h})

    def _update_plots(self):
        for bar, val in zip(self.bars, self.current_state):
            bar.set_height(val)
        self.ax1.relim()
        self.ax1.autoscale_view(True, False, True)

        floors = [r["final_floor"] for r in self.floor_history]
        self.cum_line.set_data(range(len(floors)), floors)
        self.ax2.relim()
        self.ax2.autoscale_view()

        shadows = [r["shadow_energy_this_step"] for r in self.floor_history]
        cum_shadows = np.cumsum(shadows) if shadows else []
        self.shadow_line.set_data(range(len(cum_shadows)), cum_shadows)
        self.ax3.relim()
        self.ax3.autoscale_view()

        self.fig.canvas.draw_idle()

    def _load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.floor_history = data.get("history", [])
                    self.cumulative_floor = data.get("cumulative_floor", 0.0)
                    self.total_shadow_energy = data.get("total_shadow_energy", 0.0)
                self._update_plots()
            except Exception as e:
                log.error("Failed to load history", extra={"error": str(e)})

    def _save_history(self):
        try:
            data = {
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "cumulative_floor": self.cumulative_floor,
                "total_shadow_energy": self.total_shadow_energy,
                "history": self.floor_history
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.error("Failed to save history", extra={"error": str(e)})

    def compute_shadow_cost(self, state: np.ndarray) -> float:
        """Shadow cost above true absolute floor (0 K)."""
        state_arr = np.atleast_1d(state)
        return float(np.sum(np.maximum(state_arr, 0.0)))

    def transition(self, 
                   prev_state: Optional[np.ndarray], 
                   delta: float, 
                   observer_gap: float = 0.01,
                   iterations: int = 6) -> Dict:
        """
        Kelvin-native transition: 0 K is the true absolute floor of matter.
        """
        if observer_gap < self.referee.observer_gap:
            log.warning("402 | Floor transition rejected by Referee", extra={"reason": "Observer gap not closed"})
            return {"status": "402", "message": "The mesh will not resolve until sovereignty is respected."}

        if prev_state is None:
            state = np.zeros(3)
            prev_floor = 0.0
        else:
            state = np.array(prev_state, dtype=float)
            prev_floor = self.cumulative_floor

        for i in range(iterations):
            if self.is_paused:
                plt.pause(0.05)
                continue

            # Take 2, Leave 1 asymmetric offset
            take = 2.0 * (1.0 / self.h)
            leave = 1.0 / self.h
            step_mod = np.array([-take, take - leave, leave], dtype=float)

            state = np.maximum(state + step_mod * delta, 0.0)

            total = np.sum(state)
            if total > 0:
                state = (state / total) * (prev_floor + delta)

            self.current_state = state.copy()
            self._update_plots()
            plt.pause(0.05)

        final_floor = float(np.sum(state))
        final_shadow = self.compute_shadow_cost(state)

        record = {
            "status": "200",
            "step": len(self.floor_history) + 1,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "final_floor": final_floor,
            "shadow_energy_this_step": final_shadow,
            "state_vector": state.tolist()
        }

        if self.referee.validate_transition(record):
            self.cumulative_floor = final_floor
            self.total_shadow_energy += final_shadow
            self.floor_history.append(record)
            self._save_history()
        else:
            record["status"] = "422_CORRECTED"
            state[0] += 0.556   # First meaningful step above true floor
            self.current_state = state
            self._update_plots()

        return record

    def run(self):
        """Start interactive visualization."""
        plt.show(block=True)


if __name__ == "__main__":
    engine = FPTFloorTransition(h=3.01)
    print("=== FPT Floor Transition v2.8 — Kelvin Native Absolute Zero Baseline ===")
    engine.run()