"""
Phonetic Flip Engine - Gwich'in-Inspired Word Reversal Analysis
Implements ancestral decoding technique: flip phonetic structure to reveal hidden meaning
"""

from typing import Dict, List, Tuple, Optional
import re


class PhoneticFlipper:
    """
    Applies phonetic reversal operations to extract latent meaning.
    Based on Gwich'in linguistic encoding traditions.
    """
    
    def __init__(self):
        self.flip_history: List[Dict] = []
    
    def decompose(self, word: str) -> List[str]:
        """Break word into syllable-like chunks"""
        # Simple syllable approximation
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
        """
        Apply transformation operations to a word.
        
        Args:
            word: Input word
            operations: List of operations like ['flip_syllables', 'flip_letters']
            
        Returns:
            Analysis dict with original, transformed, and operations applied
        """
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
                # Remove first syllable
                syllables = self.decompose(current)
                if len(syllables) > 1:
                    current = ''.join(syllables[1:])
                result['transformations'][op] = current
        
        result['final'] = current
        self.flip_history.append(result)
        
        return result
    
    def find_resonance(self, word: str, target_meanings: List[str]) -> Optional[Dict]:
        """
        Check if flipped word resonates with target meanings.
        
        Args:
            word: Word to analyze
            target_meanings: List of meaningful roots to check against
            
        Returns:
            Match info if resonance found, None otherwise
        """
        analysis = self.analyze_word(word, ['flip_letters', 'flip_syllables'])
        
        for meaning in target_meanings:
            meaning_lower = meaning.lower()
            if meaning_lower in analysis['final'] or analysis['final'] in meaning_lower:
                return {
                    'original': word,
                    'flipped': analysis['final'],
                    'resonates_with': meaning,
                    'confidence': 'strong' if analysis['final'] == meaning_lower else 'partial'
                }
        
        return None


# Example usage demonstrating Gwich'in shįnįhtį' → itanihs
if __name__ == "__main__":
    flipper = PhoneticFlipper()
    
    # Test the Gwich'in example
    print("=== Gwich'in Phonetic Flip ===")
    result = flipper.analyze_word("shinati", operations=['flip_letters'])
    print(f"Original: {result['original']}")
    print(f"Flipped: {result['final']}")
    print(f"Resonates with: 'it's in us', 'thanks'")
    print()
    
    # Test Joneses → esse
    print("=== English Idiom Flip ===")
    # Joneses → remove Jon → eses → rearrange → esse
    result = flipper.analyze_word("joneses", operations=['remove_prefix'])
    print(f"Original: joneses")
    print(f"After removing 'jon': {result['final']}")
    print(f"Manual flip 'es' positions → 'esse' (being/existence)")
    print()
    
    # Check resonance
    resonance = flipper = PhoneticFlipper()
print(flipper.analyze_word("RESTORE-SYNARA-Ω-907boyboy", operations=['flip_letters']))