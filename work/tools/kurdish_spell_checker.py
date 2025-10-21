#!/usr/bin/env python3
"""
Kurdish Word-Level Spell Checker
Conservative approach: only fix clear errors using dictionary
"""

import json
import re
from difflib import get_close_matches

class KurdishSpellChecker:
    def __init__(self, dictionary_file='corpus/kurdish_dictionary.json'):
        """Load Kurdish dictionary"""
        import os
        # Handle both relative and absolute paths
        if not os.path.isabs(dictionary_file) and not os.path.exists(dictionary_file):
            # Try from work directory
            dictionary_file = os.path.join(os.path.dirname(__file__), '..', dictionary_file)
        
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        
        # Convert to set for fast lookup
        self.word_set = set(self.dictionary.keys())
        
        print(f"✅ Loaded {len(self.dictionary):,} Kurdish words")
    
    def is_valid_word(self, word):
        """Check if word is in dictionary"""
        return word in self.word_set
    
    def suggest_correction(self, word, max_suggestions=3):
        """
        Find close matches for misspelled word
        
        Args:
            word: Possibly misspelled word
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of (suggestion, frequency) tuples
        """
        
        # Use difflib to find close matches (cutoff=0.8 for similarity)
        matches = get_close_matches(word, self.word_set, n=max_suggestions, cutoff=0.8)
        
        # Return with frequencies
        return [(match, self.dictionary[match]) for match in matches]
    
    def correct_word(self, word, min_frequency=10):
        """
        Correct a single word if confident
        
        Args:
            word: Word to correct
            min_frequency: Minimum frequency for correction candidate
        
        Returns:
            Corrected word or original if no confident correction
        """
        
        # Already correct
        if self.is_valid_word(word):
            return word
        
        # Find suggestions
        suggestions = self.suggest_correction(word, max_suggestions=5)
        
        if not suggestions:
            return word  # No matches found
        
        # Only use high-frequency corrections
        high_freq = [s for s in suggestions if s[1] >= min_frequency]
        
        if not high_freq:
            return word  # No high-frequency matches
        
        # If there's a clear best match (much higher frequency), use it
        best = high_freq[0]
        
        if len(high_freq) == 1:
            # Only one match - use it
            return best[0]
        
        # Multiple matches - only use if best is significantly more frequent
        second_best = high_freq[1]
        if best[1] >= second_best[1] * 2:  # Best is 2x more frequent
            return best[0]
        
        # Ambiguous - keep original
        return word
    
    def correct_text(self, text, min_frequency=10):
        """
        Correct spelling in full text
        
        Args:
            text: Input text
            min_frequency: Minimum frequency for corrections
        
        Returns:
            Corrected text
        """
        
        # Kurdish word pattern (preserve punctuation)
        word_pattern = re.compile(r'([\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u200C]+)')
        
        def replace_word(match):
            word = match.group(1)
            return self.correct_word(word, min_frequency)
        
        return word_pattern.sub(replace_word, text)

def main():
    """Test spell checker"""
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 kurdish_spell_checker.py <ocr_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize spell checker
    checker = KurdishSpellChecker()
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Input: {len(text):,} chars, {len(text.split()):,} words")
    
    # Correct spelling
    corrected = checker.correct_text(text, min_frequency=10)
    
    print(f"Output: {len(corrected):,} chars, {len(corrected.split()):,} words")
    
    # Calculate changes
    original_words = text.split()
    corrected_words = corrected.split()
    changes = sum(1 for o, c in zip(original_words, corrected_words) if o != c)
    
    print(f"Changed: {changes:,} words ({100*changes/len(original_words):.1f}%)")
    
    # Save output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(corrected)
        print(f"✅ Saved to: {output_file}")
    else:
        print("\nFirst 500 chars:")
        print(corrected[:500])

if __name__ == '__main__':
    main()
