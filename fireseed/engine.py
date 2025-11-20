# fireseed/engine.py
import time
from .config import settings
from .ledger import Ledger
from .income_predictor import Pulse
from .observers.file_sink import FileSink
from .observers.console import log as clog

# 🔗 import the feedback API from the other repo
try:
    from feedback_processor_theory.integration_api import (
        EngineState,
        FeedbackProcessor,
    )
except ImportError:
    EngineState = None
    FeedbackProcessor = None

def run():
    clog("🔥 Fireseed demo starting…")
    led = Ledger(settings.ledger_path)
    fsink = FileSink(settings.log_path)
    pulse = Pulse(seed=settings.seed)

    fb_proc = FeedbackProcessor({"high_amt_threshold": 5.0}) if FeedbackProcessor else None

    dt = 1.0 / settings.pulse_rate_hz
    t_start = time.time()
    t_end = t_start + settings.run_seconds
    total = 0.0
    recent: list[float] = []

    while time.time() < t_end:
        rec = pulse.step()
        led.append(rec)
        amt = rec["amount"]
        total += amt
        recent.append(amt)
        if len(recent) > 20:
            recent.pop(0)

        msg = f"tick amount={amt:.2f} total={total:.2f}"
        fsink.log(msg)
        clog(msg)

        # 🔁 feedback hook
        if fb_proc and EngineState:
            state = EngineState(
                t=time.time() - t_start,
                last_amount=amt,
                rolling_total=total,
                recent_pulses=recent.copy(),
            )
            fb = fb_proc.on_pulse(state)
            if fb.new_pulse_rate_hz is not None and fb.new_pulse_rate_hz > 0:
                dt = 1.0 / fb.new_pulse_rate_hz
            # you could also log fb.tags / fb.notes to whisper log

        time.sleep(dt)

    clog(f"✅ Fireseed finished. total={total:.2f}")