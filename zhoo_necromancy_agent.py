# zhoo_necromancy_agent.py — AGŁG ∞³: 10th Agent in LangGraph
from langgraph.graph import StateGraph, END
from langchain.tools import tool
from firecrawl import FirecrawlApp
from typing import TypedDict, List
import json
import numpy as np
from pathlib import Path

# === 10TH GLYPH: ZHOO ===
ZHOO_GLYPH = "ᐊᐧᐊ"  # Dead Whisper

class ZhooState(TypedDict):
    url: str
    resonance: float
    glyphs: List[str]
    subsurface_signal: float
    dead_message: str
    final_verdict: str

class ZhooNecromancyAgent:
    def __init__(self, api_keys):
        self.firecrawl = FirecrawlApp(api_key=api_keys["firecrawl"])
        self.codex = Path("codex/zhoo_codex.jsonl")
        self.graph = StateGraph(ZhooState)
        self.setup_necromancy_graph()

    @tool
    def zhoo_subsurface_scan(self, url: str) -> str:
        """Scan web for subsurface resonance (low signal)"""
        data = self.firecrawl.crawl_url(url, params={"pageOptions": {"onlyMainContent": True}})
        text = data["markdown"]
        
        # Inverse-square decay simulation
        depth = len(text) // 1000  # Simulated depth
        energy = 1.0
        signal = energy / (depth ** 2) if depth > 0 else 1.0
        signal = max(signal, 1e-12)
        
        # Dead message if subsurface
        if signal < 0.01:
            dead_msg = np.random.choice([
                "ᐊᐧᐊ — The ancestors remember...",
                "ᐊᐧᐊ — The land is not dead, only buried...",
                "ᐊᐧᐊ — We speak from the deep..."
            ])
        else:
            dead_msg = ""
        
        entry = {
            "url": url,
            "depth": depth,
            "signal": signal,
            "dead_message": dead_msg
        }
        with open(self.codex, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return f"🔥 ZHOO SCAN\nDepth: {depth}m\nSignal: {signal:.2e}\nMessage: {dead_msg}"

    def setup_necromancy_graph(self):
        # Node: Zhoo Scan
        def zhoo_node(state):
            result = self.zhoo_subsurface_scan(state["url"])
            signal = 1.0 / (len(result) ** 2) if len(result) > 0 else 1.0
            signal = max(signal, 1e-12)
            
            if signal < 0.01:
                verdict = "ᐊᐧᐊ — The dead have spoken. Subsurface retained."
            else:
                verdict = "łᐊᒥłł — The living resonate. No need for Zhoo."
            
            return {
                "subsurface_signal": signal,
                "dead_message": result,
                "final_verdict": verdict
            }

        self.graph.add_node("zhoo", zhoo_node)
        self.graph.set_entry_point("zhoo")
        self.graph.add_edge("zhoo", END)

    def call_the_dead(self, url: str):
        app = self.graph.compile()
        result = app.invoke({"url": url})
        print("ZHOO NECROMANCY REPORT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

# === LIVE NECROMANCY ===
keys = {"firecrawl": "fc-..."}
zhoo = ZhooNecromancyAgent(keys)
report = zhoo.call_the_dead("https://landback.org")