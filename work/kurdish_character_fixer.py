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
        # Basic normalization mappings (codepoint-level) for Sorani
        self.letter_map = {
            # Arabic to Kurdish codepoint unification
            '\u0643': '\u06A9',  # ك -> ک (KEHEH)
            '\u064A': '\u06CC',  # ي -> ی (FARSI YEH)
            '\u0649': '\u06D5',  # ى -> ە (AE) when misused
            '\u0629': '\u06D5',  # ة -> ە (AE)
            # NOTE: Removed ه‌ -> ه mapping - ZWNJ is essential!
        }
        # Persian digits -> Arabic-Indic digits (Sorani default)
        self.persian_digit_map = {
            '\u06F0': '\u0660', '\u06F1': '\u0661', '\u06F2': '\u0662', '\u06F3': '\u0663',
            '\u06F4': '\u0664', '\u06F5': '\u0665', '\u06F6': '\u0666', '\u06F7': '\u0667',
            '\u06F8': '\u0668', '\u06F9': '\u0669',
        }
        # Punctuation normalization
        self.punc_map = {
            ',': '،',
            '?': '؟',
            '%': '٪',
        }
        # Characters to drop entirely
        # NOTE: ZWNJ (U+200C) is ESSENTIAL for Kurdish - DO NOT drop it!
        # It controls character joining and word boundaries in Arabic script.
        self.drop_chars = set([
            '\u0640',             # tatweel
            '\u200D',            # ZWJ (keep ZWNJ, remove ZWJ)
            '\u200E', '\u200F',  # LRM, RLM
            '\u202A', '\u202B', '\u202C', '\u202D', '\u202E', # bidi embeddings/override/PDF
        ])
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
        fixed_text = self._normalize_text(text)
        
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
    
    def _normalize_text(self, text: str) -> str:
        """Systematic normalization for Sorani Kurdish corpus.
        - NFC normalize
        - remove tatweel/zero-width/bidi controls
        - strip diacritics (Mn)
        - unify Arabic vs Kurdish letter forms
        - convert Persian digits to Arabic-Indic
        - normalize common punctuation
        - collapse whitespace
        """
        # Ensure str
        if not isinstance(text, str):
            text = str(text)
        # NFC
        text = unicodedata.normalize('NFC', text)
        # Drop unwanted control chars + tatweel quickly
        text = ''.join(ch for ch in text if ch not in self.drop_chars)
        # Strip combining marks (Arabic harakat etc.)
        text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
        # Map letters (simple pass)
        for src, dst in self.letter_map.items():
            text = text.replace(src, dst)
        # Map Persian digits to Arabic-Indic
        for src, dst in self.persian_digit_map.items():
            text = text.replace(src, dst)
        # Normalize punctuation
        for src, dst in self.punc_map.items():
            text = text.replace(src, dst)
        # Collapse multiple spaces/newlines gently
        text = re.sub(r'[\t\x0b\x0c\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*\n\s*', '\n', text)
        return text.strip()

    def _apply_general_fixes(self, text):
        """Apply general Kurdish text fixes"""
        # Additional conservative substitutions after normalization
        basic_fixes = {
            'ث': 'ت',   # Arabic THEH rarely appears; map to TEH if present
            'ؤ': 'ۆ',   # WAW with hamza -> Kurdish "o"
            'أ': 'ئا',  # Alif with hamza above -> hamza + alif
            'إ': 'ئی',  # Alif with hamza below -> hamza + yeh
        }
        for old, new in basic_fixes.items():
            text = text.replace(old, new)
        # Final whitespace tidy
        text = re.sub(r'\s+', ' ', text).strip()
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