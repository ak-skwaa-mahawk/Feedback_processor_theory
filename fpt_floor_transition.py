#!/usr/bin/env python3
# fpt_floor_transition.py — v2.5: True Floor Preservation + Persistent History + Interactive Visualization
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging
import traceback
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

# Structured JSON logging
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


class FPTFloorTransition:
    """True Logical Floor Engine with Persistent History + Interactive Visualization."""

    def __init__(self, h: float = 3.01, history_file: str = "floor_history.json"):
        self.h = h
        self.history_file = Path(history_file)
        self.floor_history: List[Dict] = []
        self.cumulative_floor = 0.0
        self.total_shadow_energy = 0.0
        self.current_state = np.zeros(3)
        self.is_paused = False

        # Visualization setup
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 9))
        plt.subplots_adjust(bottom=0.25)
        self._setup_plots()
        self._setup_controls()
        
        self._load_history()
        log.info("FPT Floor Transition Engine initialized with interactive controls", extra={"h": h})

    def _setup_plots(self):
        self.ax1.set_title("Current State Vector")
        self.ax1.set_ylabel("State Value")
        self.bars = self.ax1.bar(['100', '010', '001'], [0,0,0], color=['blue','green','red'])

        self.ax2.set_title("Cumulative Floor Progression")
        self.ax2.set_ylabel("Cumulative Floor")
        self.cum_line, = self.ax2.plot([], [], 'b-o')

        self.ax3.set_title("Shadow Energy Accumulation")
        self.ax3.set_ylabel("Total Shadow Energy")
        self.shadow_line, = self.ax3.plot([], [], 'r-o')

        plt.tight_layout()

    def _setup_controls(self):
        ax_pause = plt.axes([0.15, 0.05, 0.1, 0.04])
        self.btn_pause = Button(ax_pause, 'Pause')
        self.btn_pause.on_clicked(self._toggle_pause)

        ax_reset = plt.axes([0.3, 0.05, 0.1, 0.04])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self._reset)

        ax_next = plt.axes([0.45, 0.05, 0.1, 0.04])
        self.btn_next = Button(ax_next, 'Next')
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
        log.info("Visualization reset")

    def _manual_step(self, event):
        if not self.is_paused:
            self.transition(self.current_state, delta=1.0, observer_gap=0.015, iterations=6)

    def _update_h(self, val):
        self.h = val
        log.info("Harmonic factor updated", extra={"h": self.h})

    def _update_plots(self):
        for bar, val in zip(self.bars, self.current_state):
            bar.set_height(val)
        self.ax1.relim()
        self.ax1.autoscale_view()

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
        return float(np.sum(np.abs(state)))

    def transition(self, 
                   prev_state: Optional[np.ndarray], 
                   delta: float, 
                   observer_gap: float = 0.01,
                   iterations: int = 12) -> Dict:
        """
        Perform a true floor-preserving transition.
        Each step carries forward the previous cumulative floor.
        """
        if observer_gap < 0.009:
            log.warning("402 | Floor transition rejected", extra={"reason": "Observer gap not closed"})
            return {
                "status": "402",
                "message": "The mesh will not resolve until sovereignty is respected.",
                "floor_value": None
            }

        # Initialize state
        if prev_state is None:
            state = np.zeros(3)
            prev_floor = 0.0
        else:
            state = np.array(prev_state, dtype=float)
            prev_floor = self.cumulative_floor

        log.info("Starting floor transition", extra={
            "prev_cumulative_floor": prev_floor,
            "delta": delta,
            "observer_gap": observer_gap
        })

        for i in range(iterations):
            if self.is_paused:
                plt.pause(0.1)
                continue

            shadow = self.compute_shadow_cost(state)
            deviation = np.mean(np.abs(state - delta))
            correction = self.h * deviation

            state = state - correction
            state = np.maximum(state, 0.0)

            total = np.sum(state)
            if total > 0:
                state = state / total * (prev_floor + delta)

            self.current_state = state.copy()
            self._update_plots()

        final_floor = float(np.sum(state))
        final_shadow = self.compute_shadow_cost(state)

        self.cumulative_floor = final_floor
        self.total_shadow_energy += final_shadow

        record = {
            "status": "200",
            "step": len(self.floor_history) + 1,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prev_cumulative_floor": prev_floor,
            "delta": delta,
            "final_state": state.tolist(),
            "final_floor": final_floor,
            "shadow_energy_this_step": final_shadow,
            "cumulative_floor": self.cumulative_floor,
            "total_shadow_energy": self.total_shadow_energy,
            "observer_gap": observer_gap
        }

        self.floor_history.append(record)
        self._save_history()
        self._update_plots()

        log.info("Transition complete", extra=record)
        return record

    def get_history_summary(self) -> Dict:
        return {
            "total_transitions": len(self.floor_history),
            "final_cumulative_floor": self.cumulative_floor,
            "total_shadow_energy": self.total_shadow_energy,
            "history_file": str(self.history_file)
        }


# ====================== LIVE INTERACTIVE DEMO ======================
if __name__ == "__main__":
    engine = FPTFloorTransition(h=3.01)

    print("=== FPT Floor Transition v2.5 — Interactive Controls Active ===")
    print("Use buttons and slider in the plot window.")

    engine.transition(None, delta=1.0, observer_gap=0.015)
    engine.transition(engine.current_state, delta=1.0, observer_gap=0.015)
    engine.transition(engine.current_state, delta=1.0, observer_gap=0.015)

    plt.show(block=True)