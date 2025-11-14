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
    def __init__(self, preserve_arabic_words=True, preserve_latin_digits=False, verbose=False):
        """
        Initialize Kurdish character fixer.
        
        Args:
            preserve_arabic_words: If True, preserves Arabic-only characters (ص، ض، ط، ظ، ذ)
                                   in words that appear to be Arabic loanwords/proper nouns.
                                   If False, always converts to Kurdish phonetic equivalents.
                                   Default: True (recommended for mixed Kurdish-Arabic text)
            preserve_latin_digits: If True, keeps Latin digits (0-9) unchanged.
                                   If False, converts to Arabic-Indic (default Sorani style).
                                   Default: False (convert to Arabic-Indic)
            verbose: If True, tracks and reports normalization statistics.
                     Default: False
        """
        self.preserve_arabic_words = preserve_arabic_words
        self.preserve_latin_digits = preserve_latin_digits
        self.verbose = verbose
        self.stats = {'changes': 0, 'arabic_preserved': 0, 'digits_converted': 0} if verbose else None
        
        # Basic normalization mappings (codepoint-level) for Sorani
        self.letter_map = {
            # Arabic to Kurdish codepoint unification
            '\u0643': '\u06A9',  # ك -> ک (KEHEH)
            '\u064A': '\u06CC',  # ي -> ی (FARSI YEH)
            '\u0649': '\u06D5',  # ى -> ە (AE) when misused as alef maksura
            '\u0629': '\u06D5',  # ة -> ە (AE) teh marbuta
            # Additional Arabic characters with hamza variants
            '\u0622': '\u0626\u0627',  # آ (ALEF WITH MADDA ABOVE) -> ئا
            '\u0623': '\u0626\u0627',  # أ (ALEF WITH HAMZA ABOVE) -> ئا
            '\u0625': '\u0626\u06CC', # إ (ALEF WITH HAMZA BELOW) -> ئی
            '\u0624': '\u0626\u0648',  # ؤ (WAW WITH HAMZA ABOVE) -> ئو
            '\u06c0': '\u0647\u06d5',  # ۀ (HEH WITH YEH ABOVE) -> هە
            # Special: ه + ZWNJ -> ە (Kurdish-specific normalization)
            # In Kurdish, "ه" + ZWNJ is often used instead of "ە" (AE)
            '\u0647\u200c': '\u06d5',  # ه‌ -> ە
            # NOTE: Removed ه‌ -> ه mapping - ZWNJ is essential!
        }
        # Persian digits -> Arabic-Indic digits (Sorani default)
        self.persian_digit_map = {
            '\u06F0': '\u0660', '\u06F1': '\u0661', '\u06F2': '\u0662', '\u06F3': '\u0663',
            '\u06F4': '\u0664', '\u06F5': '\u0665', '\u06F6': '\u0666', '\u06F7': '\u0667',
            '\u06F8': '\u0668', '\u06F9': '\u0669',
        }
        # Latin digits -> Arabic-Indic (optional, based on preserve_latin_digits)
        self.latin_digit_map = {
            '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
            '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
        }
        # Punctuation normalization
        self.punc_map = {
            ',': '،',   # ARABIC COMMA
            '?': '؟',   # ARABIC QUESTION MARK
            '%': '٪',   # ARABIC PERCENT SIGN
            ';': '؛',   # ARABIC SEMICOLON
        }
        # Quotation mark normalization (optional - may vary by preference)
        self.quote_map = {
            '"': '"',   # Straight quote -> Arabic quote (or use „ for Kurdish)
            "'": "'",   # Straight apostrophe -> right single quote
            '`': "'",   # Backtick -> apostrophe
            '``': '"',  # Double backtick -> opening quote
            "''": '"',  # Double apostrophe -> closing quote
        }
        # Characters to drop entirely
        # NOTE: ZWNJ (U+200C) is ESSENTIAL for Kurdish - DO NOT drop it!
        # It controls character joining and word boundaries in Arabic script.
        self.drop_chars = set([
            '\u0640',             # tatweel (Arabic kashida)
            '\u200D',            # ZWJ (keep ZWNJ, remove ZWJ)
            '\u200E', '\u200F',  # LRM, RLM (left-to-right/right-to-left marks)
            '\u202A', '\u202B', '\u202C', '\u202D', '\u202E', # bidi embeddings/override/PDF
            '\u00AD',            # soft hyphen
            '\u200B',            # zero-width space (distinct from ZWNJ!)
            '\u2009',            # thin space
            '\uFEFF',            # zero-width no-break space (BOM when not at start)
        ])
        # Extra Arabic/Persian characters not used in Kurdish Sorani
        # These appear in Arabic loanwords/proper nouns
        # Only apply if preserve_arabic_words=False, otherwise keep these in Arabic words
        self.extra_arabic_chars = set([
            '\u0635',  # ص (SAD)
            '\u0636',  # ض (DAD)
            '\u0637',  # ط (TAH)
            '\u0638',  # ظ (ZAH)
            '\u0630',  # ذ (THAL)
        ])
        
        # Phonetic mappings for extra Arabic chars (only if not preserving Arabic words)
        self.extra_arabic_map = {
            '\u0635': '\u0633',  # ص (SAD) -> س (SEEN)
            '\u0636': '\u062F',  # ض (DAD) -> د (DAL)
            '\u0637': '\u062A',  # ط (TAH) -> ت (TEH)
            '\u0638': '\u0632',  # ظ (ZAH) -> ز (ZAIN)
            '\u0630': '\u062F',  # ذ (THAL) -> د (DAL)
        }
        
        # Common Arabic words/patterns to always preserve (religious, formal terms)
        # These are kept as-is even if preserve_arabic_words=False
        self.arabic_word_patterns = [
            r'\bالله\b',           # Allah
            r'\bمحمد\b',          # Muhammad
            r'\bالقرآن\b',        # Quran
            r'\bالصلاة\b',        # Prayer
            r'\bالصوم\b',         # Fasting
            r'\bالحج\b',          # Hajj
            r'\bالزكاة\b',        # Zakat
            r'\bصلى الله عليه وسلم\b',  # PBUH
            r'\bرضي الله عنه\b',  # May Allah be pleased with him
            r'\bرحمة الله\b',     # Allah's mercy
            r'\bإن شاء الله\b',   # Inshallah
            r'\bمشاء الله\b',     # Mashallah
            r'\bبسم الله\b',      # Bismillah
            r'\bالحمد لله\b',     # Alhamdulillah
            r'\bسبحان الله\b',    # Subhanallah
        ]
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

    def get_stats(self):
        """Return normalization statistics (only if verbose=True)"""
        return self.stats.copy() if self.stats else None
    
    def reset_stats(self):
        """Reset statistics counter (only if verbose=True)"""
        if self.stats:
            self.stats = {'changes': 0, 'arabic_preserved': 0, 'digits_converted': 0}
    
    def fix_kurdish_text(self, text):
        """Apply comprehensive Kurdish character fixes"""
        if self.verbose:
            self.stats['changes'] += 1
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
    
    def _is_latin_word(self, word):
        """
        Check if a word is Latin/English (common in Kurdish text).
        
        Examples: "COVID-19", "iPhone", "Internet", "Windows"
        """
        # Remove punctuation for checking
        word_clean = re.sub(r'[^\w]', '', word)
        if not word_clean:
            return False
        
        # If predominantly Latin characters, it's a Latin word
        latin_chars = sum(1 for c in word_clean if ord(c) < 128)  # ASCII range
        total_chars = len(word_clean)
        
        # If >50% Latin characters, consider it a Latin word
        return latin_chars > total_chars * 0.5
    
    def _is_arabic_word(self, word):
        """
        Check if a word appears to be an Arabic loanword/proper noun.
        
        Heuristics:
        1. Contains Arabic-only characters (ص، ض، ط، ظ، ذ)
        2. Matches known Arabic word patterns
        3. Has Arabic morphological markers
        """
        # Check for Arabic-only characters
        has_arabic_chars = any(c in word for c in self.extra_arabic_chars)
        if not has_arabic_chars:
            return False
        
        # Check known Arabic patterns
        for pattern in self.arabic_word_patterns:
            if re.search(pattern, word):
                return True
        
        # Check for common Arabic prefixes/suffixes
        arabic_markers = [
            r'^ال',      # Definite article "al-"
            r'ة$',       # Teh marbuta ending (feminine)
            r'^مُ',      # Prefix "mu-"
            r'ون$',      # Plural ending "-oon"
            r'ين$',      # Plural ending "-een"
        ]
        
        for marker in arabic_markers:
            if re.search(marker, word):
                return True
        
        return False
    
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
        
        # Map extra Arabic/Persian chars (smart mode)
        if self.preserve_arabic_words:
            # Word-by-word processing to preserve Arabic AND Latin/English words
            words = re.split(r'(\s+)', text)  # Split but keep delimiters
            processed_words = []
            
            for word in words:
                if word.strip():  # Non-whitespace word
                    # Check if it's a Latin/English word (preserve as-is)
                    if self._is_latin_word(word):
                        processed_words.append(word)
                    # Check if it's an Arabic word (preserve as-is)
                    elif self._is_arabic_word(word):
                        # Keep Arabic word as-is
                        processed_words.append(word)
                        if self.verbose:
                            self.stats['arabic_preserved'] += 1
                    else:
                        # Apply Kurdish phonetic normalization
                        normalized_word = word
                        for src, dst in self.extra_arabic_map.items():
                            normalized_word = normalized_word.replace(src, dst)
                        processed_words.append(normalized_word)
                else:
                    # Preserve whitespace
                    processed_words.append(word)
            
            text = ''.join(processed_words)
        else:
            # Aggressive mode: always convert to Kurdish phonetics
            for src, dst in self.extra_arabic_map.items():
                text = text.replace(src, dst)
        
        # Map Persian digits to Arabic-Indic
        for src, dst in self.persian_digit_map.items():
            if src in text:
                text = text.replace(src, dst)
                if self.verbose:
                    self.stats['digits_converted'] += text.count(dst)
        
        # Map Latin digits to Arabic-Indic (unless preserving)
        if not self.preserve_latin_digits:
            for src, dst in self.latin_digit_map.items():
                if src in text:
                    count = text.count(src)
                    text = text.replace(src, dst)
                    if self.verbose and count > 0:
                        self.stats['digits_converted'] += count
        
        # Normalize punctuation
        for src, dst in self.punc_map.items():
            text = text.replace(src, dst)
        
        # Normalize quotation marks
        for src, dst in self.quote_map.items():
            text = text.replace(src, dst)
        # Collapse multiple spaces/newlines gently (PRESERVE newlines!)
        text = re.sub(r'[\t\x0b\x0c\r]', ' ', text)
        # Clean up spaces on each line but preserve line breaks
        text = re.sub(r'[ \t]+', ' ', text)          # collapse spaces/tabs only
        text = re.sub(r' *\n *', '\n', text)         # trim spaces around newlines
        text = re.sub(r'\n\n+', '\n', text)          # collapse multiple newlines to single
        return text.strip()

    def _apply_general_fixes(self, text):
        """Apply general Kurdish text fixes"""
        # Additional conservative substitutions after normalization
        # Note: Most of these are now in letter_map, but kept here as backup
        basic_fixes = {
            'ث': 'ت',   # Arabic THEH rarely appears; map to TEH if present
            # Removed 'ؤ': 'ۆ' - now correctly mapped to 'ئو' in letter_map
            # Removed 'أ': 'ئا' - now in letter_map
            # Removed 'إ': 'ئی' - now in letter_map
        }
        for old, new in basic_fixes.items():
            text = text.replace(old, new)
        # Final whitespace tidy (preserve newlines!)
        text = re.sub(r'[ \t]+', ' ', text)          # collapse spaces/tabs only
        text = re.sub(r' *\n *', '\n', text)         # trim spaces around newlines  
        return text.strip()

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