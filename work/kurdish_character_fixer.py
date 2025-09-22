#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Kurdish Character Recognition Fixer
Specifically addresses the problematic Kurdish characters: ڵ، ڕ، ژ، ڤ، گ، ێ، ۆ
"""

import sys
import re
import unicodedata

class KurdishCharacterFixer:
    def __init__(self):
        # Mapping of commonly misrecognized patterns to Kurdish characters
        self.character_patterns = {
            # گ (gaf) recognition patterns
            'گ': [
                (r'[جحخ]([وەاۆیێ])', r'گ\1'),    # ج، ح، خ before vowels → گ
                (r'([وەاۆیێ])[جحخ]', r'\1گ'),    # ج، ح، خ after vowels → گ
                (r'[كک]ل', 'گڵ'),               # كل or کل → گڵ
                (r'[؛،]', 'گ'),                # punctuation marks → گ
                (r'وول', 'گوڵ'),               # وول → گوڵ
                (r'جوڵ', 'گوڵ'),               # جوڵ → گوڵ
                (r'حوڵ', 'گوڵ'),               # حوڵ → گوڵ
                (r'که ل', 'گەڵ'),             # که ل → گەڵ
                (r'جەڵ', 'گەڵ'),               # جەڵ → گەڵ
                (r'رذق', 'گرنگ'),              # رذق → گرنگ
                (r'جرنج', 'گرنگ'),             # جرنج → گرنگ
            ],
            
            # ڕ (rra) recognition patterns  
            'ڕ': [
                (r'ره\s*ن[کگج]', 'ڕەنگ'),      # ره نک → ڕەنگ
                (r'را\s*س[تد]', 'ڕاست'),       # را ست → ڕاست
                (r'[إر]\s*[اە]س[تد]', 'ڕاست'), # إ است or ر است → ڕاست
                (r'[زذ]([اە][نس][تگج])', r'ڕ\1'), # ز or ذ before certain patterns → ڕ
                (r'([دتن])ر', r'\1ڕ'),          # ر after د، ت، ن → ڕ
            ],
            
            # ژ (jha) recognition patterns
            'ژ': [
                (r'زیان', 'ژیان'),              # زیان → ژیان
                (r'زن', 'ژن'),                 # زن → ژن  
                (r'[زذض]([یا][انو])', r'ژ\1'),  # ز، ذ، ض before یا، ان، و → ژ
                (r'([ای])ز([انو])', r'\1ژ\2'), # ز between vowels and ان، و → ژ
            ],
            
            # ڤ (v) recognition patterns
            'ڤ': [
                (r'[فق]یدیو', 'ڤیدیو'),         # فیدیو or قیدیو → ڤیدیو
                (r'یدیو', 'ڤیدیو'),            # یدیو → ڤیدیو
                (r'[فق]ان', 'ڤان'),            # فان or قان → ڤان
                (r'[فق]یک', 'ڤیک'),            # فیک or قیک → ڤیک
                (r'[فق]([یاو][دنک])', r'ڤ\1'), # ف or ق before ید، ان، وک → ڤ
            ],
            
            # ێ (î) recognition patterns
            'ێ': [
                (r'ئی([وە])', r'ئێ\1'),         # ئی before و، ە → ئێ
                (r'573', 'ئێوە'),              # 573 → ئێوە (common OCR mistake)
                (r'ذی[وە]ه', 'ئێوە'),          # ذیوه → ئێوە
                (r'ری\s*سید', 'ئێستا'),       # ری سید → ئێستا
                (r'([ائ])ی([وەس])', r'\1ێ\2'), # ی between ا/ئ and و/ە/س → ێ
                (r'([تدر])ی([وەا])', r'\1ێ\2'), # ی between consonants and vowels → ێ
            ],
            
            # ۆ (o) recognition patterns  
            'ۆ': [
                (r'نو[ٍْ]ت[ةە]', 'ئۆتۆ'),      # نوْتة → ئۆتۆ
                (r'تو([رتن])', r'ۆ\1'),         # تو before ر، ت، ن → ۆ
                (r'وو([رتن])', r'ۆ\1'),         # وو before ر، ت، ن → ۆ
                (r'([بپم])و([رتن])', r'\1ۆ\2'), # و between ب/پ/م and ر/ت/ن → ۆ
                (r'٠ه‏\s*وز', 'ۆز'),           # ٠ه‏ وز → ۆز
                (r'بو', 'بۆ'),                 # بو → بۆ
                (r'چو([نر])', r'چۆ\1'),         # چو before ن، ر → چۆ
            ],
            
            # ڵ (ll) recognition patterns
            'ڵ': [
                (r'([گک])ل', r'\1ڵ'),           # گل or کل → گڵ or کڵ
                (r'([مک])ا([لڵ])', r'\1ا\2'),   # Preserve ماڵ، کاڵ
                (r'وول', 'گوڵ'),               # وول → گوڵ
                (r'([ماک])ل([^ی])', r'\1ڵ\2'), # مل، کل not before ی → مڵ، کڵ
            ]
        }
        
        # Common Kurdish words that are frequently misrecognized
        self.word_corrections = {
            'کوردی': ['كوردي', 'کوردى', 'کوردی'],
            'گوڵ': ['وول', 'جوڵ', 'حوڵ', 'کول', 'گول'],
            'ڕەنگ': ['ره نک', 'رنگ', 'رەنگ', 'ره نگ'],
            'ژیان': ['زیان', 'ذیان', 'زيان'],
            'ڤیدیو': ['فیدیو', 'یدیو', 'قیدیو'],
            'ئێوە': ['ئیوە', '573', 'ذیوه', 'ایوه'],
            'ۆز': ['وز', '٠ه‏ وز', 'ووز'],
            'گرنگ': ['جرنج', 'رذق', 'گرنج', 'جرنگ'],
            'گەڵ': ['جەڵ', 'که ل', 'گدڵ'],
            'ڕاست': ['راست', 'إ است', 'ر است'],
            'ژن': ['زن', 'ذن'],
            'ڤان': ['فان', 'قان', 'وان'],
            'ئۆتۆ': ['نوْتة', 'تۆتۆ', 'اتو'],
            'بۆ': ['بو', 'بوو'],
            'ماڵ': ['مال', 'ماڵ'],
            'ڵام': ['لام', 'ڵام'],
        }

    def fix_kurdish_text(self, text):
        """Apply comprehensive Kurdish character fixes"""
        fixed_text = text.strip()
        
        # Apply character-specific pattern fixes
        for char, patterns in self.character_patterns.items():
            for pattern, replacement in patterns:
                fixed_text = re.sub(pattern, replacement, fixed_text)
        
        # Apply word-level corrections
        for correct_word, variants in self.word_corrections.items():
            for variant in variants:
                fixed_text = fixed_text.replace(variant, correct_word)
        
        # Additional cleanup
        fixed_text = self._apply_general_fixes(fixed_text)
        
        return fixed_text.strip()
    
    def _apply_general_fixes(self, text):
        """Apply general Kurdish text fixes"""
        # Basic character substitutions
        basic_fixes = {
            'ك': 'ک',   # Arabic kaf → Kurdish kaf
            'ي': 'ی',   # Arabic ya → Kurdish ya
            'ث': 'ت',   # Arabic tha → Kurdish ta
            'ة': 'ە',   # Arabic ta marbuta → Kurdish schwa
            'أ': 'ئا',  # Arabic alif hamza → Kurdish hamza alif
            'إ': 'ئی',  # Arabic alif hamza kasra → Kurdish hamza ya
            'ؤ': 'ۆ',   # Arabic waw hamza → Kurdish o
        }
        
        for old, new in basic_fixes.items():
            text = text.replace(old, new)
        
        # Clean up extra spaces and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

def main():
    fixer = KurdishCharacterFixer()
    
    if len(sys.argv) > 1:
        # Read from file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        fixed_text = fixer.fix_kurdish_text(text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        
        print(f"Fixed text saved to: {output_file}")
    else:
        # Read from stdin
        text = sys.stdin.read()
        fixed_text = fixer.fix_kurdish_text(text)
        print(fixed_text, end='')

if __name__ == "__main__":
    main()