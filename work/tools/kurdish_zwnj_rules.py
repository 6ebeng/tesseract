#!/usr/bin/env python3
"""
Kurdish ZWNJ Grammar Rules
Implements linguistic rules for inserting Zero-Width Non-Joiner (ZWNJ) in Kurdish text
Based on Central Kurdish (Sorani) grammar and observed patterns
"""

import re
from typing import List, Tuple

class KurdishZWNJRules:
    """Kurdish grammar rules for ZWNJ insertion"""
    
    # Zero-Width Non-Joiner character
    ZWNJ = '\u200c'
    
    def __init__(self):
        """Initialize Kurdish ZWNJ rules"""
        
        # Kurdish letters for pattern matching
        self.kurdish_letter = r'[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهەیێ]'
        self.vowel = r'[ئاەوۆیێ]'
        self.consonant = r'[بپتجچحخدرڕزژسشعغفڤقکگلڵمنه]'
        
        # Common compound word components
        self.compound_prefixes = [
            'مه‌لا',  # mela (title)
            'گه‌وره',  # gewre (big/great)
            'بنه‌ما',  # bunema (base/foundation)
            'خه‌بات',  # xebat (struggle)
            'له‌سه',  # leser (on/upon)
            'به‌ره',  # bere (product/towards)
            'هه‌ڵ',    # hell (up)
            'مزگه‌وت', # mizgewt (mosque)
            'چه‌ند',   # çend (several)
            'جه‌لی',   # jelî (Jewish/celebration)
        ]
        
        # Ezafe marker suffixes
        self.ezafe_triggers = [
            'ی',  # -î (possessive)
            'ێ',  # -ê (another possessive form)
        ]
        
        # Prepositions that take ZWNJ
        self.prepositions = [
            'له',   # le (in/at)
            'به',   # be (with/by)
            'بۆ',   # bo (for/to)
            'دە',   # de (in - present tense marker)
        ]
        
        # Suffixes that need ZWNJ before them
        self.zwnj_suffixes = [
            'دا',     # -da (in/at)
            'تر',     # -tir (more/comparative)
            'ترین',   # -tirîn (most/superlative)
            'ان',     # -an (plural)
            'ەکان',   # -ekan (definite plural)
            'یش',     # -îş (also/too)
            'مان',    # -man (our)
            'تان',    # -tan (your)
            'یان',    # -yan (their)
        ]
    
    def apply_all_rules(self, text: str) -> Tuple[str, dict]:
        """
        Apply all ZWNJ rules to text
        
        Args:
            text: Input Kurdish text without ZWNJs
            
        Returns:
            Tuple of (processed_text, stats_dict)
        """
        stats = {
            'original_zwnj': text.count(self.ZWNJ),
            'compound_words': 0,
            'ezafe': 0,
            'suffixes': 0,
            'prepositions': 0,
            'total_inserted': 0
        }
        
        original_text = text
        
        # Rule 1: PRIMARY RULE - ه + consonant (accounts for 98% of ZWNJs)
        text, count = self._apply_ezafe_rule(text)
        stats['ezafe'] = count
        
        # Disable other rules for now - test primary rule first
        # Rule 2: Compound words
        # text, count = self._apply_compound_rules(text)
        # stats['compound_words'] = count
        stats['compound_words'] = 0
        
        # Rule 3: Suffixes
        # text, count = self._apply_suffix_rules(text)
        # stats['suffixes'] = count
        stats['suffixes'] = 0
        
        # Rule 4: Prepositions
        # text, count = self._apply_preposition_rules(text)
        # stats['prepositions'] = count
        stats['prepositions'] = 0
        
        # Calculate total inserted
        stats['total_inserted'] = text.count(self.ZWNJ) - stats['original_zwnj']
        stats['final_zwnj'] = text.count(self.ZWNJ)
        
        return text, stats
    
    def _apply_ezafe_rule(self, text: str) -> Tuple[str, int]:
        """
        Apply the PRIMARY Kurdish ZWNJ rule:
        Insert ZWNJ after ه (he) when followed by certain consonants
        
        This accounts for 98% of ZWNJs in Kurdish text!
        Examples: مه‌لا (mela), گه‌وره (gewre), به‌ره (bere)
        """
        count = 0
        
        # THE CRITICAL PATTERN: ه + [most characters] → ه‌ + [character]
        # This is the morphological pattern for compound words with "he"  
        # Based on ground truth: 289/294 ZWNJs (98%) follow ه
        # After ZWNJ, we see: space (41x), و (37x), ی (30x), ر (29x), ك (22x), etc.
        # Insert ZWNJ after ه when followed by ALMOST ANY character except vowel-like chars
        #
        # MORE CONSERVATIVE: Only insert before common following characters
        # This balances recall (catching real ZWNJs) vs precision (avoiding false positives)
        
        pattern = r'ه([ ولمربكستندڵقخزشغفڤگیێئاەحجعطظصض،.\n])'
        
        def replacer(match):
            nonlocal count
            # Check if ZWNJ not already present before
            start = match.start()
            if start > 0 and text[start-1] == self.ZWNJ:
                return match.group(0)
            # Check if ZWNJ already between ه and next char
            if self.ZWNJ in match.group(0):
                return match.group(0)
            count += 1
            return 'ه' + self.ZWNJ + match.group(1)
        
        text = re.sub(pattern, replacer, text)
        
        return text, count
    
    def _apply_compound_rules(self, text: str) -> Tuple[str, int]:
        """
        Apply compound word rules based on Kurdish morphology
        Examples: گه‌وره (gewre), مه‌لا (mela)
        """
        count = 0
        
        # Common two-syllable patterns where ZWNJ appears between syllables
        # Pattern: consonant(s) + vowel + ه + vowel + consonant(s)
        # Example: گ + ه‌ + و + ر + ه = گه‌وره
        
        compound_patterns = [
            # Pattern: Cه + Vر/ل/م/ن + ه (ge-wre, me-la, etc.)
            (f'({self.consonant})ه({self.vowel})({self.consonant})ه\\b', 1),
            # Pattern: Cه + Cا (xeba-t, etc.)
            (f'({self.consonant})ه({self.consonant})ا', 1),
            # Pattern: له + consonant (le-ser, etc.)
            (r'(له)(س[هەە]ر|گه|نێ|ته)', 1),
            # Pattern: به + consonant (be-re, etc.)
            (r'(به)(ره|سه|رێ|رگ)', 1),
        ]
        
        for pattern, insert_pos in compound_patterns:
            def replacer(match):
                nonlocal count
                groups = match.groups()
                # Check if ZWNJ not already present
                if self.ZWNJ in match.group(0):
                    return match.group(0)
                count += 1
                # Insert ZWNJ at position
                result = groups[0] + self.ZWNJ
                for g in groups[1:]:
                    result += g
                return result
            
            text = re.sub(pattern, replacer, text)
        
        return text, count
    
    def _apply_suffix_rules(self, text: str) -> Tuple[str, int]:
        """
        Apply suffix rules: insert ZWNJ before suffixes
        Examples: زۆر‌تر (zortir - more), کتاب‌ەکان (kitabekan - the books)
        """
        count = 0
        
        for suffix in self.zwnj_suffixes:
            # Pattern: Kurdish word + suffix (without ZWNJ)
            # Look for: letter + suffix where ZWNJ is not already present
            pattern = f'({self.kurdish_letter})({suffix})\\b'
            
            def replacer(match):
                nonlocal count
                # Check if ZWNJ not already present before
                start = match.start()
                if start > 0 and text[start-1] == self.ZWNJ:
                    return match.group(0)
                # Check if ZWNJ between letter and suffix
                if match.group(1) + self.ZWNJ + match.group(2) == match.group(0):
                    return match.group(0)
                count += 1
                return match.group(1) + self.ZWNJ + match.group(2)
            
            text = re.sub(pattern, replacer, text)
        
        return text, count
    
    def _apply_preposition_rules(self, text: str) -> Tuple[str, int]:
        """
        Apply preposition rules: insert ZWNJ after certain prepositions
        Examples: له‌ناو (lenaw - inside), به‌ره‌و (berew - towards)
        """
        count = 0
        
        # Prepositions that combine with following word
        for prep in self.prepositions:
            # Pattern: preposition + Kurdish letter (start of next word)
            pattern = f'({prep})({self.kurdish_letter})'
            
            def replacer(match):
                nonlocal count
                # Check if ZWNJ not already present
                if self.ZWNJ in match.group(0):
                    return match.group(0)
                # Don't insert if it's already part of compound
                # (avoid double insertion)
                count += 1
                return match.group(1) + self.ZWNJ + match.group(2)
            
            text = re.sub(pattern, replacer, text)
        
        return text, count
    
    def compare_with_ground_truth(self, predicted: str, ground_truth: str) -> dict:
        """
        Compare predicted ZWNJ insertions with ground truth
        
        Args:
            predicted: Text with predicted ZWNJs
            ground_truth: Text with correct ZWNJs
            
        Returns:
            Dictionary with precision, recall, F1 metrics
        """
        # Find all ZWNJ positions
        pred_positions = {i for i, c in enumerate(predicted) if c == self.ZWNJ}
        gt_positions = {i for i, c in enumerate(ground_truth) if c == self.ZWNJ}
        
        # Calculate metrics
        true_positives = len(pred_positions & gt_positions)
        false_positives = len(pred_positions - gt_positions)
        false_negatives = len(gt_positions - pred_positions)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'predicted_count': len(pred_positions),
            'ground_truth_count': len(gt_positions)
        }


def main():
    """Test the ZWNJ rules"""
    rules = KurdishZWNJRules()
    
    # Test cases
    test_cases = [
        "مهلای گهوره",  # mela gewre (great mullah)
        "کتابی من",      # kitabî min (my book)
        "زۆرتر",         # zortir (more)
        "لهناو",         # lenaw (inside)
        "بهرههم",        # berhem (product)
    ]
    
    print("=" * 60)
    print("KURDISH ZWNJ RULES - TEST CASES")
    print("=" * 60)
    
    for original in test_cases:
        processed, stats = rules.apply_all_rules(original)
        print(f"\nOriginal:  {original}")
        print(f"Processed: {processed}")
        print(f"Stats: {stats}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
