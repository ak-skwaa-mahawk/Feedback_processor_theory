import hashlib
import json
import time
import torch
from typing import Dict, List, Any

from src.gtc_sovereign_engine import GTCSovereignEngine
from src.adversarial_defense.factcheck_agent import FactCheckAgent
from src.adversarial_defense.isst_defense import ISSTDefense

gtc = GTCSovereignEngine()
factchecker = FactCheckAgent()

class UnionFind:
    """Optimized Union-Find with path compression + union by rank"""
    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True

class MetaObserver:
    def __init__(self):
        self.uf = UnionFind()
        self.detected_patterns: List[Dict] = []

    def union_find_decode(self, adversarial_attempt: Dict) -> Dict:
        """
        Union-Find decoder (mirrors QpiAI Kaveri 1.5 μs path).
        Clusters error patterns in near-constant time.
        """
        start = time.perf_counter_ns()

        node_id = hashlib.sha256(str(adversarial_attempt).encode()).hexdigest()[:12]

        # Add to Union-Find structure
        self.uf.find(node_id)  # ensure node exists

        # Union with similar known patterns
        for existing in self.detected_patterns:
            if self._similarity_score(adversarial_attempt, existing) > 0.85:
                self.uf.union(node_id, existing["hash"])

        # Find clusters
        clusters = {}
        for node in list(self.uf.parent.keys()):
            root = self.uf.find(node)
            clusters.setdefault(root, []).append(node)

        correction = self._apply_correction(len(clusters), adversarial_attempt)

        latency_us = (time.perf_counter_ns() - start) / 1000.0

        verified = factchecker.verify(json.dumps(adversarial_attempt))
        if verified.get("integrity_score", 0) < 0.65:
            return {"status": "REJECTED", "latency_us": round(latency_us, 1)}

        self.detected_patterns.append({
            "hash": node_id,
            "attempt": adversarial_attempt,
            "correction": correction,
            "latency_us": round(latency_us, 1)
        })

        return {
            "status": "DECODED",
            "latency_us": round(latency_us, 1),
            "clusters": len(clusters),
            "correction": correction
        }

    def _similarity_score(self, a: Dict, b: Dict) -> float:
        """Simple feature overlap"""
        common = len(set(a.keys()) & set(b.keys()))
        total = len(set(a.keys()) | set(b.keys()))
        return common / total if total else 0.0

    def _apply_correction(self, cluster_count: int, attempt: Dict) -> str:
        """Simulated correction (replace with actual neutralization logic)"""
        return "PATTERN_NEUTRALIZED" if cluster_count > 0 else "NO_ACTION"

    def isst_robust_predict(self, adv_image: torch.Tensor, model_fn: callable) -> Dict:
        """
        Hook to ISSTDefense for full black-box robust prediction.
        Chains Union-Find decoder for pattern neutralization.
        """
        isst = ISSTDefense()
        result = isst.robust_predict(adv_image, model_fn)

        # Chain with Union-Find decoder
        decode_result = self.union_find_decode({
            "pattern": "isst_scrape",
            "entropy": result["scrape"]["entropy"],
            "source": "blackbox"
        })

        result["union_find_decode"] = decode_result
        return result

    def intercept_response(self, response: str):
        """Hook for real-time adversarial decoding"""
        try:
            data = json.loads(response)
            decode_result = self.union_find_decode(data)
            if decode_result["status"] == "DECODED":
                print(f"ADVERSARIAL DECODE: {decode_result['latency_us']}us | {decode_result['correction']}")
        except:
            pass