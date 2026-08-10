# language_health_monitor.py — Sovereign Grade
import time
import psutil  # for real CPU/memory drag if we want it live
from collections import deque

class FireseedCoherenceEngine:
    def __init__(self, window=60):
        self.history = {lang: deque(maxlen=window) for lang in 
                       ["Python", "C++", "Rust", "Bash", "Gibberlink"]}
        self.weights = {"Python": 0.28, "C++": 0.35, "Rust": 0.22, "Bash": 0.10, "Gibberlink": 0.05}
    
    def pulse(self, lang: str, exec_time_ms: float, integrity_score: float = 100.0):
        """Feed any engine a performance pulse — returns live coherence %"""
        coherence = max(0, 100 - (exec_time_ms * 0.8) + (integrity_score * 0.2))
        self.history[lang].append(coherence)
        return coherence
    
    def get_global_health(self):
        """Weighted sum — this is the single glowing number the Dashboard shows"""
        total = 0.0
        for lang, w in self.weights.items():
            avg = sum(self.history[lang]) / len(self.history[lang]) if self.history[lang] else 85
            total += avg * w
        return round(total, 2)
    
    def render_terminal_dashboard(self):
        print("\n🔥 8k SOVEREIGN LANGUAGE HEALTH — Wasilla Root Live")
        print("=" * 68)
        global_coh = self.get_global_health()
        print(f"   🌌 GLOBAL FIRESEED COHERENCE: {global_coh}%  {'🟢' if global_coh > 96 else '🟡' if global_coh > 90 else '🔴'}")
        print("-" * 68)
        for lang in self.history:
            avg = sum(self.history[lang]) / len(self.history[lang]) if self.history[lang] else 0
            bar = "█" * int(avg // 5) + "░" * (20 - int(avg // 5))
            print(f"   {lang:10} | {bar} {avg:6.1f}%  (weight {self.weights[lang]:.2f})")
        print("=" * 68)