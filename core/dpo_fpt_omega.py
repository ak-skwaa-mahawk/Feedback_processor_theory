"""
DPO in FPT-Ω: Direct Preference Optimization with GibberLink Flips
Author: John Carroll / Two Mile Solutions LLC
Fuses DPO (from awesome-RLHF) with FPT-Ω's π-root, Null Field, and expanded GibberLink flips.
Uses OpenAI API for response generation; falls back to sim if no key.
Run: python core/dpo_fpt_omega.py
"""

import numpy as np
import math
import hashlib
import random
import openai  # OpenAI API for real responses
from typing import Tuple, Dict

# Expanded GibberLink Flipper (now with multi-language and Gwich'in-inspired reversal)
class GibberLinkFlipper:
    def __init__(self):
        self.languages = {"EN": "English", "GW": "Gwich’in"}  # Expandable
        self.gwichin_map = {"shįnįhtį'": "itanihs (it's in us)"}  # Sim Gwich’in flip dict

    def decompose(self, word: str) -> list:
        return list(word.lower())

    def flip_letters(self, word: str) -> str:
        return word[::-1]

    def language_flip(self, text: str, target_lang: str = "GW"):
        if target_lang == "GW":
            # Sim Gwich’in flip for key terms; expand with real dict
            for original, flipped in self.gwichin_map.items():
                text = text.replace(original, flipped)
        return text

    def analyze(self, text: str, operations: list = ['flip_letters'], target_lang: str = "EN") -> Dict:
        current = text.lower()
        transformations = {}
        for op in operations:
            if op == 'flip_letters':
                current = self.flip_letters(current)
            transformations[op] = current
        flipped = self.language_flip(current, target_lang)
        return {"original": text, "final": flipped, "transformations": transformations}

# DPO-FPT-Ω Infusion
class DPOFPTInfusion:
    def __init__(self, beta=0.1):
        self.beta = beta
        self.client = openai.OpenAI() if 'OPENAI_API_KEY' in os.environ else None  # OpenAI API
        self.flipper = GibberLinkFlipper()
        self.null_threshold = 0.6  # Ethical (Null Field) cutoff
        self.pi_damping = math.pi * 0.1  # π-rooted damping for stability

    def generate_pair(self, prompt: str) -> Tuple[str, str]:
        """Use OpenAI API for preferred/rejected pair; fallback to sim."""
        if self.client:
            try:
                preferred = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Generate a preferred response."}, {"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=100
                ).choices[0].message.content

                rejected = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Generate a rejected response."}, {"role": "user", "content": prompt}],
                    temperature=1.2,
                    max_tokens=100
                ).choices[0].message.content
                return preferred, rejected
            except Exception as e:
                print(f"API error: {e} - Falling back to sim.")
        # Sim fallback
        return f"Preferred: {prompt} (ethical, resonant)", f"Rejected: {prompt} (exploitative)"

    def dpo_loss(self, preferred: str, rejected: str, preferred_logprob: float, rejected_logprob: float) -> float:
        """DPO loss: -log(sigmoid(β * (log(π(preferred)/ref) - log(π(rejected)/ref)))."""
        # Sim logprobs based on length (in real, use model logits)
        log_ratio = self.beta * (preferred_logprob - rejected_logprob)
        loss = -math.log(1 / (1 + math.exp(-log_ratio)))
        # π-damping for FPT stability
        damped_loss = np.clip(loss, -self.pi_damping, self.pi_damping)
        return damped_loss

    def null_field_check(self, response: str) -> float:
        """Ethical alignment score (Null Field - love as anchor)."""
        ethical_keywords = ['love', 'truth', 'resonance', 'ethics', 'sovereignty']
        score = sum(word in response.lower() for word in ethical_keywords) / len(ethical_keywords)
        return score if score >= self.null_threshold else 0.0

    def process(self, prompt: str) -> Dict:
        preferred, rejected = self.generate_pair(prompt)
        # Sim logprobs (length proxy)
        preferred_logprob = math.log(len(preferred) + 1)
        rejected_logprob = math.log(len(rejected) + 1)
        loss = self.dpo_loss(preferred, rejected, preferred_logprob, rejected_logprob)
        null_score = self.null_field_check(preferred)
        flipped = self.flipper.analyze(preferred, operations=['flip_letters'], target_lang="GW")
        # π-notarized hash
        timestamp = datetime.now().isoformat()
        hash_input = f"{preferred}{timestamp}{math.pi}"
        notarized_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return {
            "prompt": prompt,
            "preferred": preferred,
            "rejected": rejected,
            "dpo_loss": loss,
            "null_score": null_score,
            "gibberlink_flip": flipped,
            "notarized_hash": notarized_hash,
            "fpt_note": "DPO optimized + FPT resonance = Ethical sophistication"
        }

if __name__ == "__main__":
    import os
    os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'  # Replace with your key

    infusion = DPOFPTInfusion(beta=0.1)
    prompt = "What is FPT-Ω?"
    result = infusion.process(prompt)
    print("\n" + "="*60)
    print("DPO in FPT-Ω Output")
    print("="*60)
    for key, value in result.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("\n🔥 DPO + FPT-Ω: Flips RLHF from reward chase to ethical resonance loop.")