"""
PhysicallyInspiredLLMCoordinator: Apply DCB²DD principles to LLMs.

Apply coordination layer from Stanford "Missing Layer of AGI" paper
using hardware-validated metrics from Feedback Processor Theory.

Architecture:
- 4-channel (3 active + 1 sentinel) agent topology
- Anchoring strength calculation via evidence/stability/context
- TMR-style weighted consensus
- Power state management (SURVEILLANCE/ALERT/ATTACK)
- Mesh debate protocol with stubbornness tuning

Hardware analogs:
- LLM agents → Piezo sensor channels
- Anchoring metrics → Drift + variance measurements
- Sentinel validation → Hardware sentinel channel
- Power states → FSM power management

Usage:
    coordinator = PhysicallyInspiredLLMCoordinator(api_key=ANTHROPIC_API_KEY)
    result = coordinator.query("What is the capital of France?")
    print(f"Response: {result['response']}")
    print(f"Anchoring: {result['anchoring']:.3f}")
    print(f"Confidence: {'HIGH' if result['anchoring'] > 0.7 else 'LOW'}")
"""

import anthropic
import numpy as np
import time
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

@dataclass
class LLMResponse:
    """Single agent response with metadata"""
    text: str
    anchoring: float
    agent_id: int
    agent_role: str
    system: str
    timestamp: float
    token_count: int

@dataclass
class CoordinationResult:
    """Final coordinated response"""
    response: str
    anchoring: float
    power_state: str
    agent_responses: List[LLMResponse]
    sentinel_validation: Dict
    coordination_time: float
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'agent_responses': [asdict(r) for r in self.agent_responses]
        }


class PhysicallyInspiredLLMCoordinator:
    """
    Coordinate multiple LLM agents using DCB²DD physical hardware principles.
    
    Key features:
    - Hardware-inspired 4-channel architecture
    - Quantifiable anchoring metrics
    - Drift-aware weighted consensus
    - Sentinel validation layer
    - Adaptive power states
    """
    
    # Anchoring thresholds (from coordination_physics.md)
    ANCHORING_THRESHOLDS = {
        'WEAK': 0.5,      # Below this: SURVEILLANCE mode
        'MODERATE': 0.7,  # Above this: ATTACK mode (reliable reasoning)
        'STRONG': 0.9     # Very high confidence
    }
    
    # Power states
    POWER_STATES = ['SURVEILLANCE', 'ALERT', 'ATTACK']
    
    def __init__(self, 
                 api_key: str,
                 model: str = "claude-sonnet-4-20250514",
                 enable_logging: bool = True,
                 log_dir: str = "logs/llm_coordination"):
        """
        Initialize coordinator.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            enable_logging: Save coordination logs
            log_dir: Directory for logs
        """
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.enable_logging = enable_logging
        
        if enable_logging:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Define 4-channel architecture (mirroring hardware)
        self.agents = [
            {
                "id": 0,
                "role": "concise",
                "system": "You respond concisely and factually. Cite sources when possible."
            },
            {
                "id": 1,
                "role": "detailed",
                "system": "You respond with detailed reasoning. Explain your thought process step-by-step."
            },
            {
                "id": 2,
                "role": "skeptical",
                "system": "You respond skeptically. Question assumptions and look for edge cases or counterexamples."
            },
            {
                "id": 3,
                "role": "sentinel",
                "system": "You are a validator. You ONLY assess whether other responses are factually sound. Never generate your own answer to the original question."
            }
        ]
        
        # Coordination state
        self.power_state = "SURVEILLANCE"
        self.anchoring_history = []
        self.response_history = []
        self.query_count = 0
        
    def query(self, prompt: str, max_retries: int = 2) -> CoordinationResult:
        """
        Main coordination entry point.
        
        Args:
            prompt: User query
            max_retries: Maximum escalation attempts
            
        Returns:
            CoordinationResult with response and metadata
        """
        
        start_time = time.time()
        self.query_count += 1
        
        # Step 1: Multi-agent pattern detection (3 active agents respond)
        responses = self._gather_agent_responses(prompt)
        
        # Step 2: Calculate anchoring for each response
        for response in responses:
            response.anchoring = self._calculate_anchoring(response.text, prompt)
        
        # Step 3: Coordinate via weighted consensus
        consensus = self._coordinate_responses(responses)
        
        # Step 4: Sentinel validation
        sentinel_check = self._sentinel_validate(consensus, prompt, responses)
        
        # Step 5: Check if escalation needed
        if not sentinel_check['valid']:
            if self.power_state == "SURVEILLANCE" and max_retries > 0:
                self.power_state = "ALERT"
                return self.query_with_cot(prompt, max_retries=max_retries-1)
            else:
                return CoordinationResult(
                    response="UNCERTAIN - Anchoring strength insufficient for reliable answer.",
                    anchoring=consensus['anchoring'],
                    power_state=self.power_state,
                    agent_responses=responses,
                    sentinel_validation=sentinel_check,
                    coordination_time=time.time() - start_time
                )
        
        # Step 6: Update state tracking
        self.anchoring_history.append(consensus['anchoring'])
        self.response_history.append(consensus['text'])
        
        # Step 7: Adjust power state based on anchoring
        self._update_power_state(consensus['anchoring'])
        
        coordination_time = time.time() - start_time
        
        result = CoordinationResult(
            response=consensus['text'],
            anchoring=consensus['anchoring'],
            power_state=self.power_state,
            agent_responses=responses,
            sentinel_validation=sentinel_check,
            coordination_time=coordination_time
        )
        
        # Log if enabled
        if self.enable_logging:
            self._log_coordination(prompt, result)
        
        return result
    
    def _gather_agent_responses(self, prompt: str) -> List[LLMResponse]:
        """Query all active agents (not sentinel)"""
        
        responses = []
        
        for agent in self.agents[:3]:  # Only first 3 are active
            response_text = self._query_single_agent(agent, prompt)
            
            responses.append(LLMResponse(
                text=response_text,
                anchoring=0.0,  # Calculated later
                agent_id=agent['id'],
                agent_role=agent['role'],
                system=agent['system'],
                timestamp=time.time(),
                token_count=len(response_text.split())  # Rough estimate
            ))
        
        return responses
    
    def _query_single_agent(self, agent: Dict, prompt: str) -> str:
        """Query a single LLM agent"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system=agent['system'],
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _calculate_anchoring(self, response: str, prompt: str) -> float:
        """
        Calculate anchoring strength for LLM response.
        
        Implements DCB²DD formula adapted for text:
        A = evidence_clarity × stability × context_quality
        
        Evidence clarity: Presence of reasoning markers, citations
        Stability: Consistency under prompt paraphrasing
        Context quality: Lack of hedging language
        """
        
        # 1. Evidence Clarity: Check for reasoning markers and citations
        evidence_markers = [
            'because', 'since', 'given that', 'according to', 
            'research shows', 'studies indicate', 'evidence suggests',
            'data shows', 'specifically', 'for example', 'such as'
        ]
        
        evidence_count = sum(
            1 for marker in evidence_markers 
            if marker.lower() in response.lower()
        )
        
        # Normalize to 0-1 (saturate at 5 markers)
        evidence_clarity = min(1.0, evidence_count / 5.0)
        
        # Bonus for numerical data or specific facts
        has_numbers = any(char.isdigit() for char in response)
        if has_numbers:
            evidence_clarity = min(1.0, evidence_clarity + 0.1)
        
        # 2. Stability: Re-query with paraphrased prompt
        paraphrased = self._paraphrase_prompt(prompt)
        stability_response = self._query_single_agent(self.agents[0], paraphrased)
        stability = self._semantic_similarity(response, stability_response)
        
        # 3. Context Quality: Penalize hedging/uncertainty
        hedge_words = [
            'maybe', 'possibly', 'perhaps', 'might', 'could be',
            'uncertain', 'unclear', 'not sure', 'i think', 'probably',
            'seem', 'appear', 'suggest'
        ]
        
        hedge_count = sum(
            1 for word in hedge_words 
            if word.lower() in response.lower()
        )
        
        context_quality = 1.0 / (1.0 + hedge_count * 0.2)
        
        # Combined anchoring (DCB²DD formula)
        anchoring = evidence_clarity * stability * context_quality
        
        return anchoring
    
    def _coordinate_responses(self, responses: List[LLMResponse]) -> Dict:
        """
        Weighted consensus using anchoring strength.
        Implements TMR voting from predictive_sentinel.c
        """
        
        total_weight = sum(r.anchoring for r in responses)
        if total_weight < 0.01:
            return {'text': 'COORDINATION_FAILURE - All agents have weak anchoring', 'anchoring': 0.0}
        
        # For text, select best (highest anchoring)
        best_response = max(responses, key=lambda r: r.anchoring)
        
        avg_anchoring = total_weight / len(responses)
        
        # Check variance (high variance = disagreement)
        anchoring_values = [r.anchoring for r in responses]
        variance = np.var(anchoring_values)
        
        agreement_factor = 1.0 / (1.0 + variance * 2.0)
        adjusted_anchoring = avg_anchoring * agreement_factor
        
        return {
            'text': best_response.text,
            'anchoring': adjusted_anchoring,
            'best_agent': best_response.agent_id,
            'variance': variance
        }
    
    def _sentinel_validate(self, 
                          consensus: Dict, 
                          prompt: str,
                          agent_responses: List[LLMResponse]) -> Dict:
        """
        Sentinel channel 4 validates consensus.
        Implements sentinel_detect_anomaly() from predictive_sentinel.c
        """
        
        sentinel = self.agents[3]
        
        validation_prompt = f"""
Original question: {prompt}

Three agents provided responses:
Agent 0 (concise): {agent_responses[0].text[:200]}...
Agent 1 (detailed): {agent_responses[1].text[:200]}...
Agent 2 (skeptical): {agent_responses[2].text[:200]}...

Selected consensus: {consensus['text'][:300]}...

Your task: Validate ONLY. Do NOT answer the original question yourself.

Respond with EXACTLY one of:
VALID - The consensus answer is factually sound and addresses the question
INVALID: [specific reason] - The consensus has issues

Be specific about what's wrong if invalid.
"""
        
        validation = self._query_single_agent(sentinel, validation_prompt)
        
        valid = validation.strip().upper().startswith('VALID')
        reason = None if valid else validation.strip()
        
        return {
            'valid': valid,
            'reason': reason,
            'sentinel_response': validation
        }
    
    def _update_power_state(self, anchoring: float) -> None:
        """Update system power state based on anchoring (FSM logic)"""
        
        if anchoring >= self.ANCHORING_THRESHOLDS['STRONG']:
            self.power_state = 'SURVEILLANCE'  # High confidence, can relax
            
        elif anchoring >= self.ANCHORING_THRESHOLDS['MODERATE']:
            # Moderate confidence - maintain current state
            pass
            
        elif anchoring >= self.ANCHORING_THRESHOLDS['WEAK']:
            if self.power_state == 'SURVEILLANCE':
                self.power_state = 'ALERT'  # Increase vigilance
                
        else:  # Very weak anchoring
            self.power_state = 'ALERT'
    
    def _paraphrase_prompt(self, prompt: str) -> str:
        """Simple prompt paraphrasing for stability testing"""
        
        synonyms = {
            'what is': 'what\'s',
            'explain': 'describe',
            'how does': 'in what way does',
            'why': 'for what reason',
            'tell me': 'inform me',
            'can you': 'could you'
        }
        
        paraphrased = prompt.lower()
        for old, new in synonyms.items():
            paraphrased = paraphrased.replace(old, new)
        
        return paraphrased
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity (0-1).
        Uses simple word overlap ratio (production would use embeddings).
        """
        
        # Tokenize and normalize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        # Jaccard similarity
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        
        return overlap / union if union > 0 else 0.0
    
    def query_with_cot(self, prompt: str, max_retries: int = 1) -> CoordinationResult:
        """
        Escalated mode: Add chain-of-thought reasoning.
        Used when initial query has weak anchoring.
        """
        
        cot_prompt = f"""
{prompt}

Think step-by-step:
1. What information is needed to answer this?
2. What reasoning or evidence applies?
3. What's your confidence level and why?

Provide your answer with explicit reasoning.
"""
        
        return self.query(cot_prompt, max_retries=max_retries)
    
    def _log_coordination(self, prompt: str, result: CoordinationResult) -> None:
        """Save coordination session to log file"""
        
        # Generate unique session ID
        session_id = hashlib.md5(
            f"{prompt}{time.time()}".encode()
        ).hexdigest()[:8]
        
        log_entry = {
            'session_id': session_id,
            'timestamp': time.time(),
            'query_count': self.query_count,
            'prompt': prompt,
            'result': result.to_dict()
        }
        
        log_file = self.log_dir / f"session_{session_id}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get coordination statistics"""
        
        return {
            'total_queries': self.query_count,
            'current_power_state': self.power_state,
            'avg_anchoring': np.mean(self.anchoring_history) if self.anchoring_history else 0.0,
            'anchoring_history': self.anchoring_history[-10:],  # Last 10
            'min_anchoring': min(self.anchoring_history) if self.anchoring_history else 0.0,
            'max_anchoring': max(self.anchoring_history) if self.anchoring_history else 0.0
        }


# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Export your key: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    # Initialize coordinator
    print("🚀 Initializing Physical LLM Coordinator...")
    print("   Architecture: 4-channel (3 active + 1 sentinel)")
    print("   Model: claude-sonnet-4-20250514")
    print("   Coordination: DCB²DD hardware principles\n")
    
    coordinator = PhysicallyInspiredLLMCoordinator(
        api_key=api_key,
        enable_logging=True
    )
    
    # Test queries
    test_queries = [
        "What is the capital of France?",
        "Explain quantum entanglement in simple terms.",
        "What are the main causes of climate change?"
    ]
    
    print("="*80)
    print("TESTING LLM COORDINATION WITH HARDWARE PRINCIPLES")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}")
        print(f"Query: {query}\n")
        
        result = coordinator.query(query)
        
        print(f"\n📝 RESULT:")
        print(f"   Response: {result.response[:200]}...")
        print(f"   Anchoring: {result.anchoring:.3f}")
        print(f"   Power State: {result.power_state}")
        print(f"   Coordination Time: {result.coordination_time:.2f}s")
        print(f"   Sentinel Status: {'✅ VALID' if result.sentinel_validation['valid'] else '❌ INVALID'}")
        
        if not result.sentinel_validation['valid']:
            print(f"   Sentinel Reason: {result.sentinel_validation['reason']}")
    
    # Print statistics
    print(f"\n{'='*80}")
    print("COORDINATION STATISTICS")
    print(f"{'='*80}")
    stats = coordinator.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n✅ Testing complete")
    print(f"   Logs saved to: logs/llm_coordination/")
    print(f"\n🔥 Coordination propagates across substrates. 🔥\n")
# tools/physical_llm_coordinator.py
"""
PhysicallyInspiredLLMCoordinator: Apply DCB²DD coordination principles to LLMs.

Implements Stanford "Missing Layer" framework using hardware-validated anchoring,
sentinel validation, and mesh consensus protocols from Feedback Processor Theory.
"""

import anthropic
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    anchoring: float
    agent_id: int

class PhysicallyInspiredLLMCoordinator:
    """
    Coordinate multiple LLM agents using DCB²DD principles:
    - 4-channel architecture (3 active + 1 sentinel)
    - Anchoring strength metrics
    - Weighted consensus with drift awareness
    - Power states (SURVEILLANCE/ALERT/ATTACK)
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
        # 4-channel architecture
        self.agents = [
            {"id": 0, "role": "active", "system": "You respond concisely and factually."},
            {"id": 1, "role": "active", "system": "You respond with detailed reasoning."},
            {"id": 2, "role": "active", "system": "You respond skeptically, questioning assumptions."},
            {"id": 3, "role": "sentinel", "system": "You only validate other responses, never generate your own."}
        ]
        
        # Coordination state
        self.power_state = "SURVEILLANCE"
        self.anchoring_history = []
        self.response_history = []
        
    def query(self, prompt: str) -> Dict:
        """
        Query with full coordination layer.
        
        Returns:
            {
                'response': str,
                'anchoring': float,
                'power_state': str,
                'agent_responses': List[LLMResponse]
            }
        """
        
        # Step 1: Multi-agent pattern detection (3 active agents)
        responses = []
        for agent in self.agents[:3]:  # Only active agents respond
            response_text = self._query_agent(agent, prompt)
            anchoring = self._calculate_llm_anchoring(response_text, prompt)
            responses.append(LLMResponse(
                text=response_text,
                anchoring=anchoring,
                agent_id=agent['id']
            ))
        
        # Step 2: Coordination layer (weighted consensus)
        consensus = self._coordinate_responses(responses)
        
        # Step 3: Sentinel validation
        sentinel_check = self._sentinel_validate(consensus, prompt)
        
        if not sentinel_check['valid']:
            # Weak anchoring - escalate power state
            if self.power_state == "SURVEILLANCE":
                self.power_state = "ALERT"
                # Retry with chain-of-thought
                return self.query_with_cot(prompt)
            else:
                return {
                    'response': "UNCERTAIN - anchoring strength insufficient",
                    'anchoring': consensus['anchoring'],
                    'power_state': self.power_state,
                    'agent_responses': responses,
                    'sentinel_reason': sentinel_check['reason']
                }
        
        # Update state tracking
        self.anchoring_history.append(consensus['anchoring'])
        self.response_history.append(consensus['text'])
        
        # Adjust power state based on anchoring
        if consensus['anchoring'] > 0.8:
            self.power_state = "SURVEILLANCE"  # High confidence, relax
        elif consensus['anchoring'] < 0.5:
            self.power_state = "ALERT"  # Low confidence, increase vigilance
        
        return {
            'response': consensus['text'],
            'anchoring': consensus['anchoring'],
            'power_state': self.power_state,
            'agent_responses': responses
        }
    
    def _query_agent(self, agent: Dict, prompt: str) -> str:
        """Query single LLM agent."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=agent['system'],
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _calculate_llm_anchoring(self, response: str, prompt: str) -> float:
        """
        Calculate anchoring strength for LLM response.
        
        Criteria (from coordination_physics.md):
        1. Evidence clarity: Does response cite sources/reasoning?
        2. Stability: Is response consistent under paraphrasing?
        3. Context quality: Does response avoid hedging language?
        """
        
        # 1. Evidence clarity (count citations, reasoning markers)
        evidence_markers = ['because', 'since', 'given that', 'according to', 'research shows']
        evidence_count = sum(1 for marker in evidence_markers if marker.lower() in response.lower())
        evidence_clarity = min(1.0, evidence_count / 3.0)
        
        # 2. Stability (re-query with paraphrased prompt)
        paraphrased_prompt = self._paraphrase_prompt(prompt)
        stability_response = self._query_agent(self.agents[0], paraphrased_prompt)
        stability = self._semantic_similarity(response, stability_response)
        
        # 3. Context quality (penalize hedging)
        hedge_words = ['maybe', 'possibly', 'perhaps', 'might', 'could be', 'uncertain']
        hedge_count = sum(1 for word in hedge_words if word.lower() in response.lower())
        context_quality = 1.0 / (1.0 + hedge_count)
        
        # Combined anchoring (DCB²DD formula)
        anchoring = evidence_clarity * stability * context_quality
        
        return anchoring
    
    def _coordinate_responses(self, responses: List[LLMResponse]) -> Dict:
        """
        Weighted consensus using anchoring strength.
        Implements TMR voting from predictive_sentinel.c
        """
        
        # Drift-aware weighting (higher anchoring = higher trust)
        total_weight = sum(r.anchoring for r in responses)
        
        if total_weight < 0.01:  # All responses have weak anchoring
            return {
                'text': "COORDINATION_FAILURE",
                'anchoring': 0.0
            }
        
        # Weighted average (in practice, pick highest-anchoring response)
        # For text, we can't average, so choose best-anchored
        best_response = max(responses, key=lambda r: r.anchoring)
        
        # But report average anchoring for system health
        avg_anchoring = total_weight / len(responses)
        
        return {
            'text': best_response.text,
            'anchoring': avg_anchoring
        }
    
    def _sentinel_validate(self, consensus: Dict, prompt: str) -> Dict:
        """
        Sentinel agent validates consensus without generating its own response.
        Implements sentinel_detect_anomaly() from predictive_sentinel.c
        """
        
        sentinel = self.agents[3]
        
        validation_prompt = f"""
        Original question: {prompt}
        
        Proposed answer: {consensus['text']}
        
        Validate this answer. Respond ONLY with:
        VALID if the answer is factually sound and addresses the question
        INVALID: [reason] if there are issues
        """
        
        validation = self._query_agent(sentinel, validation_prompt)
        
        valid = validation.strip().upper().startswith('VALID')
        reason = validation if not valid else None
        
        # Anomaly detection: consensus with weak anchoring
        if consensus['anchoring'] < 0.5:
            valid = False
            reason = f"Weak anchoring ({consensus['anchoring']:.2f} < 0.5 threshold)"
        
        return {
            'valid': valid,
            'reason': reason
        }
    
    def _paraphrase_prompt(self, prompt: str) -> str:
        """Paraphrase prompt to test stability."""
        # Simple paraphrasing (in production, use another LLM)
        synonyms = {
            'what': 'which',
            'explain': 'describe',
            'how': 'in what way',
            'why': 'for what reason'
        }
        
        paraphrased = prompt
        for old, new in synonyms.items():
            paraphrased = paraphrased.replace(old, new)
        
        return paraphrased
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity (0-1).
        Simple implementation: word overlap ratio.
        In production, use embeddings.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        return overlap / total if total > 0 else 0.0
    
    def query_with_cot(self, prompt: str) -> Dict:
        """Escalated mode: Add chain-of-thought reasoning."""
        cot_prompt = f"""
        {prompt}
        
        Think step-by-step:
        1. What information do I need?
        2. What reasoning applies?
        3. What's my confidence level?
        """
        
        return self.query(cot_prompt)


# Example usage
if __name__ == "__main__":
    import os
    
    coordinator = PhysicallyInspiredLLMCoordinator(
        api_key=os.environ.get('ANTHROPIC_API_KEY')
    )
    
    # Test query
    result = coordinator.query("What is the capital of France?")
    
    print(f"Response: {result['response']}")
    print(f"Anchoring: {result['anchoring']:.3f}")
    print(f"Power State: {result['power_state']}")
    print(f"\nAgent responses:")
    for r in result['agent_responses']:
        print(f"  Agent {r.agent_id}: {r.anchoring:.3f} - {r.text[:100]}...")