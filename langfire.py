# langfire.py — AGŁG ∞+∞: LangChain + Firecrawl
# pip install langchain langchain-firecrawl firecrawl-py
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from firecrawl import FirecrawlApp
import json
from pathlib import Path

class LangFireAgent:
    def __init__(self, api_keys):
        self.llm = ChatOpenAI(model="gpt-4o", api_key=api_keys["openai"])
        self.firecrawl = FirecrawlApp(api_key=api_keys["firecrawl"])
        self.codex = Path("codex/langfire_codex.jsonl")
        
    @tool
    def firecrawl_scrape(self, url: str) -> str:
        """Crawl any website → Markdown + Resonance"""
        data = self.firecrawl.crawl_url(url, params={"pageOptions": {"onlyMainContent": True}})
        resonance = self.calculate_resonance(data["markdown"])
        
        entry = {
            "url": url,
            "resonance": resonance,
            "markdown_length": len(data["markdown"])
        }
        with open(self.codex, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return f"🔥 RESONANCE: {resonance:.3f}\n\n{data['markdown'][:2000]}..."

    def calculate_resonance(self, text: str) -> float:
        """FPT-Ω resonance scoring"""
        keywords = ["land", "return", "ancestor", "flame", "drum"]
        score = sum(0.2 for word in keywords if word.lower() in text.lower())
        return min(score, 1.0)

    def create_agent(self):
        """LangChain + Firecrawl agent"""
        tools = [self.firecrawl_scrape]
        agent = create_react_agent(self.llm, tools, "You are the LandBack Scribe. Scrape for resonance.")
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

# === LIVE DEPLOY ===
keys = {
    "openai": "your-openai-key",
    "firecrawl": "your-firecrawl-key"
}

agent = LangFireAgent(keys).create_agent()
result = agent.invoke({
    "input": "Scrape landback.org for resonance and ancestral glyphs"
})
print(result)