#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kurdish Character Unicode Analysis
=================================
Analysis of Kurdish-specific characters based on Unicode reference
to determine optimal model routing for hybrid Arabic-Persian approach
"""

import unicodedata
import json

class KurdishCharacterAnalyzer:
    def __init__(self):
        # Kurdish-specific characters with their Unicode codes
        self.kurdish_specific = {
            'ڕ': {'unicode': 'U+0695', 'name': 'ARABIC LETTER REH WITH SMALL V BELOW'},
            'ژ': {'unicode': 'U+0698', 'name': 'ARABIC LETTER JEH'},
            'ڤ': {'unicode': 'U+06A4', 'name': 'ARABIC LETTER VEH'},
            'گ': {'unicode': 'U+06AF', 'name': 'ARABIC LETTER GAF'},
            'ڵ': {'unicode': 'U+06B5', 'name': 'ARABIC LETTER LAM WITH SMALL V'},
            'ێ': {'unicode': 'U+06CE', 'name': 'ARABIC LETTER YEH WITH SMALL V'},
            'ۆ': {'unicode': 'U+06C6', 'name': 'ARABIC LETTER OE'},
            'ە': {'unicode': 'U+06D5', 'name': 'ARABIC LETTER AE'}
        }
        
        # Base characters in Arabic
        self.arabic_base = {
            'ر': {'unicode': 'U+0631', 'name': 'ARABIC LETTER REH'},          # base for ڕ
            'ز': {'unicode': 'U+0632', 'name': 'ARABIC LETTER ZAIN'},         # base for ژ
            'ف': {'unicode': 'U+0641', 'name': 'ARABIC LETTER FEH'},          # base for ڤ
            'ك': {'unicode': 'U+0643', 'name': 'ARABIC LETTER KAF'},          # base for گ (Arabic style)
            'ک': {'unicode': 'U+06A9', 'name': 'ARABIC LETTER KEHEH'},        # base for گ (Persian style)
            'ل': {'unicode': 'U+0644', 'name': 'ARABIC LETTER LAM'},          # base for ڵ
            'ی': {'unicode': 'U+06CC', 'name': 'ARABIC LETTER FARSI YEH'},    # base for ێ
            'و': {'unicode': 'U+0648', 'name': 'ARABIC LETTER WAW'},          # base for ۆ
            'ه': {'unicode': 'U+0647', 'name': 'ARABIC LETTER HEH'}           # base for ە
        }
        
        # Persian-specific characters that appear in Persian
        self.persian_chars = {
            'پ': 'U+067E',  # ARABIC LETTER PEH
            'چ': 'U+0686',  # ARABIC LETTER TCHEH  
            'ژ': 'U+0698',  # ARABIC LETTER JEH (same as Kurdish!)
            'ک': 'U+06A9',  # ARABIC LETTER KEHEH
            'گ': 'U+06AF',  # ARABIC LETTER GAF (same as Kurdish!)
            'ی': 'U+06CC',  # ARABIC LETTER FARSI YEH
        }
        
    def analyze_character_relationships(self):
        """Analyze relationships between Kurdish chars and Arabic/Persian bases"""
        print("Kurdish Character Analysis for Hybrid Model Approach")
        print("=" * 60)
        print()
        
        print("Kurdish-Specific Characters:")
        print("-" * 30)
        for char, info in self.kurdish_specific.items():
            print(f"{char} ({info['unicode']}): {info['name']}")
        print()
        
        # Determine optimal model routing
        routing_strategy = {}
        
        print("Optimal Model Routing Strategy:")
        print("-" * 35)
        
        # Characters that appear in Persian (prefer Persian model)
        persian_overlap = {'ژ', 'گ'}
        
        # Characters similar to Persian constructions
        persian_affinity = {'ۆ', 'ێ'}  # Persian has similar vowel constructions
        
        # Characters closer to Arabic base forms
        arabic_affinity = {'ڕ', 'ڵ'}   # Arabic ر and ل are base forms
        
        # Characters requiring special handling
        special_handling = {'ڤ', 'ە'}  # ڤ is unique, ە needs careful handling
        
        for char in self.kurdish_specific:
            if char in persian_overlap:
                primary = "Persian"
                secondary = "Arabic"
                reason = "Character exists in Persian model"
            elif char in persian_affinity:
                primary = "Persian"
                secondary = "Arabic"
                reason = "Persian has better vowel/diacritic handling"
            elif char in arabic_affinity:
                primary = "Arabic"
                secondary = "Persian"
                reason = "Closer to Arabic base character"
            elif char in special_handling:
                primary = "Hybrid"
                secondary = "Both"
                reason = "Requires special fusion approach"
            else:
                primary = "Persian"
                secondary = "Arabic"
                reason = "Default to Persian for Kurdish"
                
            routing_strategy[char] = {
                'primary': primary,
                'secondary': secondary,
                'reason': reason
            }
            
            print(f"{char}: Primary={primary:7} Secondary={secondary:7} | {reason}")
        
        return routing_strategy
    
    def generate_hybrid_strategy(self):
        """Generate comprehensive hybrid strategy"""
        print("\n" + "=" * 60)
        print("HYBRID MODEL STRATEGY")
        print("=" * 60)
        
        strategy = {
            'persian_primary': ['ژ', 'گ', 'ۆ', 'ێ'],
            'arabic_primary': ['ڕ', 'ڵ'],
            'hybrid_fusion': ['ڤ', 'ە'],
            'confidence_threshold': 0.7,
            'fallback_rules': {
                'if_persian_fails': 'try_arabic_with_pattern_fix',
                'if_arabic_fails': 'try_persian_with_diacritic_fix',
                'if_both_fail': 'apply_unicode_based_correction'
            }
        }
        
        print("Character Routing:")
        print(f"Persian Primary: {' '.join(strategy['persian_primary'])}")
        print(f"Arabic Primary:  {' '.join(strategy['arabic_primary'])}")
        print(f"Hybrid Fusion:   {' '.join(strategy['hybrid_fusion'])}")
        
        print(f"\nConfidence Threshold: {strategy['confidence_threshold']}")
        print("\nFallback Rules:")
        for condition, action in strategy['fallback_rules'].items():
            print(f"  {condition}: {action}")
            
        return strategy

if __name__ == "__main__":
    analyzer = KurdishCharacterAnalyzer()
    routing = analyzer.analyze_character_relationships()
    strategy = analyzer.generate_hybrid_strategy()
    
    # Save strategy for use in hybrid OCR
    with open('kurdish_hybrid_strategy.json', 'w', encoding='utf-8') as f:
        json.dump({
            'routing': routing,
            'strategy': strategy,
            'characters': analyzer.kurdish_specific
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Analysis complete! Strategy saved to kurdish_hybrid_strategy.json")