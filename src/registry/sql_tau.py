import re
from typing import Dict, List, Any
from .sovereign_queries import SovereignQueryEngine

class SQLTauParser:
    """
    Sovereign Query Language (SQL-τ) parser and interpreter.
    Maps human-readable queries to sovereign engine calls.
    """

    def __init__(self, engine: SovereignQueryEngine):
        self.engine = engine

    def parse_and_execute(self, query: str) -> Any:
        query = query.strip().upper()
        
        if query.startswith("SHOW ACTIVE BRAIDS FOR"):
            session = re.search(r'FOR\s+(\S+)', query).group(1)
            return self.engine.query_active_braids(session)
        
        elif query.startswith("SHOW REVOKED BRAIDS FOR"):
            session = re.search(r'FOR\s+(\S+)', query).group(1)
            return self.engine.query_revoked_braids(session)
        
        elif query.startswith("SHOW LINEAGE AT"):
            match = re.search(r'SHOW LINEAGE AT\s+"(.+)"\s+FOR\s+(\S+)', query)
            time, session = match.groups()
            return self.engine.query_lineage_at_time(session, time)
        
        elif query.startswith("SHOW BRAID HISTORY FOR"):
            session = re.search(r'FOR\s+(\S+)', query).group(1)
            return self.engine.query_braid_history(session)
        
        elif query.startswith("SHOW FUSION TIMELINE FOR"):
            session = re.search(r'FOR\s+(\S+)', query).group(1)
            return self.engine.query_fusion_timeline(session)
        
        elif query.startswith("AUDIT SESSION"):
            session = re.search(r'SESSION\s+(\S+)', query).group(1)
            return self.engine.query_constitutional_audit(session)
        
        else:
            raise ValueError(f"Unrecognized sovereign query: {query}")

# Demo
if __name__ == "__main__":
    engine = SovereignQueryEngine()
    parser = SQLTauParser(engine)
    
    queries = [
        "SHOW ACTIVE BRAIDS FOR session-τ-001",
        "SHOW REVOKED BRAIDS FOR session-τ-001",
        "SHOW LINEAGE AT \"2025-12-25T21:30:00\" FOR session-τ-001",
        "SHOW BRAID HISTORY FOR session-τ-001",
        "SHOW FUSION TIMELINE FOR session-τ-001",
        "AUDIT SESSION session-τ-001"
    ]
    
    for q in queries:
        print(f"\n> {q}")
        result = parser.parse_and_execute(q)
        print(json.dumps(result, indent=2))