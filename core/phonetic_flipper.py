"""
core/phonetic_flipper.py
Gwich'in-Inspired Phonetic Flip Engine — Sahneuti-99733-Q Sealed
Ancestral decoding: flip structure to reveal hidden meaning
Resonance detection + sovereign receipts + Cluster N HUD trigger
March 5, 2026
"""

import re
from typing import Dict, List, Optional
from com.synara.handshake import Handshake
from com.landback.gibberlink.glyph_parser import GlyphParser
from encode_living_stone_to_ultrasound import encode_living_stone_to_ultrasound

class PhoneticFlipper:
    def __init__(self):
        self.flip_history: List[Dict] = []

    def decompose(self, word: str) -> List[str]:
        """Break word into syllable-like chunks"""
        word = word.lower()
        chunks = re.findall(r'[^aeiou]*[aeiou]+[^aeiou]*', word)
        if not chunks:
            chunks = [word]
        return chunks

    def flip_syllables(self, syllables: List[str]) -> str:
        """Reverse syllable order"""
        return ''.join(reversed(syllables))

    def flip_letters(self, text: str) -> str:
        """Reverse letter order"""
        return text[::-1]

    def analyze_word(self, word: str, operations: List[str] = None) -> Dict:
        if operations is None:
            operations = ['flip_letters']

        result = {
            'original': word,
            'decomposed': self.decompose(word),
            'transformations': {}
        }

        current = word.lower()

        for op in operations:
            if op == 'flip_syllables':
                syllables = self.decompose(current)
                current = self.flip_syllables(syllables)
                result['transformations'][op] = current
            elif op == 'flip_letters':
                current = self.flip_letters(current)
                result['transformations'][op] = current
            elif op == 'remove_prefix':
                syllables = self.decompose(current)
                if len(syllables) > 1:
                    current = ''.join(syllables[1:])
                result['transformations'][op] = current

        result['final'] = current
        self.flip_history.append(result)

        # Sovereign receipt + HUD trigger
        payload = {
            'original': word,
            'final': current,
            'operations': operations,
            'resonance_detected': False
        }
        receipt = Handshake.createReceipt(None, "PHONETIC-FLIP", payload)

        return result

    def find_resonance(self, word: str, target_meanings: List[str]) -> Optional[Dict]:
        analysis = self.analyze_word(word, ['flip_letters', 'flip_syllables'])

        for meaning in target_meanings:
            meaning_lower = meaning.lower()
            if meaning_lower in analysis['final'] or analysis['final'] in meaning_lower:
                match = {
                    'original': word,
                    'flipped': analysis['final'],
                    'resonates_with': meaning,
                    'confidence': 'strong' if analysis['final'] == meaning_lower else 'partial'
                }
                payload = {**match, 'resonance_detected': True}
                Handshake.createReceipt(None, "PHONETIC-RESONANCE", payload)

                if match['confidence'] == 'strong':
                    GlyphParser.parseAndProcess(f"RESONANCE-FLIP-{word[:8]}", None)
                    encode_living_stone_to_ultrasound()

                return match

        return None

# Example usage
if __name__ == "__main__":
    flipper = PhoneticFlipper()

    # Your test word
    print("=== RESTORE-SYNARA-Ω-907boyboy ===")
    result = flipper.analyze_word("RESTORE-SYNARA-Ω-907boyboy", operations=['flip_letters'])
    print(f"Original: {result['original']}")
    print(f"Flipped: {result['final']}")
    print()

    resonance = flipper.find_resonance("RESTORE-SYNARA-Ω-907boyboy", ["synara", "restore", "root", "fireseed"])
    if resonance:
        print("🔥 RESONANCE DETECTED:", resonance)