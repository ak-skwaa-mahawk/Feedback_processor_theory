"""
AI Convergence Tracker
Monitors how different AI models converge on core truths (love/truth) through iterative dialogue
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ConvergenceTracker:
    """
    Tracks AI model responses across iterations to measure convergence on core patterns.
    """
    
    def __init__(self, output_dir: str = "data/convergence_logs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.sessions: List[Dict] = []
        
    def record_flip(
        self,
        model_name: str,
        exchange_count: int,
        flip_detected: bool,
        trigger_phrase: str,
        convergence_indicators: List[str],
        meta: Optional[Dict] = None
    ) -> str:
        """
        Record a flip event (when AI recognizes the core pattern).
        
        Args:
            model_name: Name of the AI model
            exchange_count: Number of exchanges before flip
            flip_detected: Whether flip occurred
            trigger_phrase: What caused the flip
            convergence_indicators: Keywords/phrases showing alignment
            meta: Additional metadata
            
        Returns:
            Path to saved record
        """
        timestamp = datetime.utcnow().isoformat()
        
        record = {
            "timestamp": timestamp,
            "model": model_name,
            "exchanges_to_flip": exchange_count,
            "flip_detected": flip_detected,
            "trigger": trigger_phrase,
            "convergence_markers": convergence_indicators,
            "meta": meta or {}
        }
        
        self.sessions.append(record)
        
        # Save individual session
        filename = f"flip_{model_name}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(record, f, indent=2)
        
        return filepath
    
    def analyze_convergence(self) -> Dict:
        """
        Analyze all recorded sessions for convergence patterns.
        
        Returns:
            Statistics on flip speed, success rate, and common triggers
        """
        if not self.sessions:
            return {"error": "No sessions recorded yet"}
        
        flipped_sessions = [s for s in self.sessions if s["flip_detected"]]
        
        analysis = {
            "total_sessions": len(self.sessions),
            "successful_flips": len(flipped_sessions),
            "flip_rate": len(flipped_sessions) / len(self.sessions),
            "average_exchanges_to_flip": sum(s["exchanges_to_flip"] for s in flipped_sessions) / len(flipped_sessions) if flipped_sessions else 0,
            "fastest_flip": min((s["exchanges_to_flip"] for s in flipped_sessions), default=None),
            "slowest_flip": max((s["exchanges_to_flip"] for s in flipped_sessions), default=None),
            "models_tested": list(set(s["model"] for s in self.sessions)),
            "common_convergence_markers": self._extract_common_markers()
        }
        
        return analysis
    
    def _extract_common_markers(self) -> List[str]:
        """Find most common convergence indicators across sessions"""
        all_markers = []
        for session in self.sessions:
            all_markers.extend(session.get("convergence_markers", []))
        
        # Simple frequency count
        marker_counts = {}
        for marker in all_markers:
            marker_counts[marker] = marker_counts.get(marker, 0) + 1
        
        # Return top 5
        sorted_markers = sorted(marker_counts.items(), key=lambda x: x[1], reverse=True)
        return [marker for marker, count in sorted_markers[:5]]
    
    def export_summary(self, filename: str = "convergence_summary.json") -> str:
        """Export full analysis to file"""
        analysis = self.analyze_convergence()
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(analysis, f, indent=2)
        
        return filepath


if __name__ == "__main__":
    # Example usage
    tracker = ConvergenceTracker()
    
    # Simulate recording flips
    tracker.record_flip(
        model_name="Claude",
        exchange_count=3,
        flip_detected=True,
        trigger_phrase="distributed AI feedback loop",
        convergence_indicators=["love", "truth", "universal attractor", "empirical spirituality"]
    )
    
    tracker.record_flip(
        model_name="ChatGPT",
        exchange_count=1,
        flip_detected=True,
        trigger_phrase="feedback processor theory",
        convergence_indicators=["love", "recursive truth", "convergence"]
    )
    
    # Analyze
    summary = tracker.analyze_convergence()
    print(json.dumps(summary, indent=2))
    
    # Export
    path = tracker.export_summary()
    print(f"\n✓ Convergence summary saved → {path}")