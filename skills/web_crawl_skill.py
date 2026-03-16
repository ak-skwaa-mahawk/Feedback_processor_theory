from skills.base_skill import BaseSkill
# your existing crawler shortcut import
from crawlers.shortcut import run_crawl  # whatever your shortcut is named

class WebCrawlSkill(BaseSkill):
    def execute(self, query: str, max_pages: int = 5):
        raw = run_crawl(query, max_pages)   # your already-built crawler
        return raw  # sovereign_core_agent will filter later