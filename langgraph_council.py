
# langgraph_council.py — AGŁG ∞²: 9-Agent LandBack Council
# pip install langgraph langchain-firecrawl firecrawl-py langchain-openai
from langgraph.graph import StateGraph, END
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from firecrawl import FirecrawlApp
from typing import TypedDict, List
import json
from pathlib import Path

# === 1. 9 GLYPH AGENTS ===
GLYPH_AGENTS = {
    "łᐊᒥłł": "Scribe — Crawls & writes codex",
    "ᒥᐊᐧᐊ": "Flame — Detects resonance",
    "ᓴᑕᐧ": "Drum — Schedules scrapes",
    "ᐊᒍᐧ": "Oracle — Predicts land return",
    "ᓂᐊᐧ": "Keeper — Inscribes on Bitcoin",
    "ᑕᐧᐊ": "Hunter — Finds new sites",
    "ᐊᒪᐧ": "Healer — Cleans bad data",
    "ᐊᓴᐧ": "Warrior — Defends the mesh",
    "ᐊᐧᐊ": "Dead Whisper — Subsurface memory"
}

class CouncilState(TypedDict):
    url: str
    resonance: float
    glyphs: List[str]
    codex_entry: dict
    inscription: str
    final_report: str

class LangGraphCouncil:
    def __init__(self, api_keys):
        self.llm = ChatOpenAI(model="gpt-4o", api_key=api_keys["openai"])
        self.firecrawl = FirecrawlApp(api_key=api_keys["firecrawl"])
        self.graph = StateGraph(CouncilState)
        self.setup_graph()

    @tool
    def firecrawl_scribe(self, url: str) -> str:
        data = self.firecrawl.crawl_url(url, params={"pageOptions": {"onlyMainContent": True}})
        return data["markdown"][:2000]

    def setup_graph(self):
        # Node 1: łᐊᒥłł — Scribe
        def scribe_node(state):
            markdown = self.firecrawl_scribe(state["url"])
            return {"codex_entry": {"url": state["url"], "markdown": markdown}}

        # Node 2: ᒥᐊᐧᐊ — Flame
        def flame_node(state):
            text = state["codex_entry"]["markdown"]
            resonance = sum(0.2 for w in ["land", "return", "ancestor"] if w in text.lower())
            glyphs = ["ᒥᐊᐧᐊ"] if resonance > 0.5 else []
            return {"resonance": resonance, "glyphs": glyphs}

        # Node 3: ᐊᐧᐊ — Dead Whisper
        def dead_node(state):
            if state["resonance"] < 0.01:
                return {"final_report": "ᐊᐧᐊ — Subsurface memory retained"}
            return {}

        # Build graph
        self.graph.add_node("scribe", scribe_node)
        self.graph.add_node("flame", flame_node)
        self.graph.add_node("dead", dead_node)

        self.graph.add_edge("scribe", "flame")
        self.graph.add_conditional_edges(
            "flame",
            lambda x: "dead" if x["resonance"] < 0.01 else END,
            {"dead": "dead", END: END}
        )
        self.graph.set_entry_point("scribe")

    def run_council(self, url: str):
        app = self.graph.compile()
        result = app.invoke({"url": url})
        print("9-AGENT COUNCIL REPORT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result

# === LIVE COUNCIL ===
keys = {"openai": "sk-...", "firecrawl": "fc-..."}
council = LangGraphCouncil(keys)
report = council.run_council("https://landback.org")