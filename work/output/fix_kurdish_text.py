#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

def fix_kurdish_characters(text):
    """Fix common Arabic-to-Kurdish character mapping issues"""
    
    # Character mappings from Arabic to Kurdish
    mappings = {
        'ك': 'ک',      # Arabic kaf to Kurdish kaf
        'ي': 'ی',      # Arabic ya to Kurdish ya  
        'ث': 'ت',      # Arabic tha to Kurdish t (common mistake)
        'ة': 'ە',      # Arabic ta marbuta to Kurdish schwa
        'أ': 'ئا',     # Arabic alif with hamza to Kurdish hamza+alif
        'إ': 'ئی',     # Arabic alif with hamza to Kurdish hamza+ya
        'ؤ': 'ۆ',      # Arabic waw with hamza to Kurdish o
        'ئ': 'ئ',      # Keep Kurdish hamza
        'ە': 'ە',      # Keep Kurdish schwa
        'ۆ': 'ۆ',      # Keep Kurdish o
        'ی': 'ی',      # Keep Kurdish ya
        'ک': 'ک',      # Keep Kurdish kaf
        # Kurdish-specific characters that need special handling
        'ل': 'ڵ',      # Arabic lam sometimes should be Kurdish ڵ
        'ر': 'ڕ',      # Arabic ra sometimes should be Kurdish ڕ  
        'ز': 'ژ',      # Arabic zain sometimes should be Kurdish ژ
        'ف': 'ڤ',      # Arabic fa sometimes should be Kurdish ڤ
        'گ': 'گ',      # Keep Kurdish gaf
        'ێ': 'ێ',      # Keep Kurdish î
        'ڵ': 'ڵ',      # Keep Kurdish ڵ
        'ڕ': 'ڕ',      # Keep Kurdish ڕ
        'ژ': 'ژ',      # Keep Kurdish ژ
        'ڤ': 'ڤ',      # Keep Kurdish ڤ
        'ج': 'گ',      # Arabic jim sometimes should be Kurdish gaf
    }
    
    # Apply mappings
    fixed_text = text
    for arabic_char, kurdish_char in mappings.items():
        fixed_text = fixed_text.replace(arabic_char, kurdish_char)
    
    # Advanced pattern-based fixes for specific Kurdish words and contexts
    pattern_fixes = [
        # Kurdish-specific letter combinations
        (r'گەژ', 'گەڵ'),          # Fix common OCR mistake
        (r'کوژ', 'کوڵ'),          # Fix ڵ recognition
        (r'کەر', 'کەڕ'),          # Fix ڕ recognition
        (r'زیان', 'ژیان'),        # Fix ژ recognition
        (r'فیک', 'ڤیک'),          # Fix ڤ recognition
        (r'دەرگا', 'دەرگە'),      # Fix ە recognition
        (r'جەرگە', 'گەرگە'),      # Fix گ recognition
        (r'ئێوە', 'ئێوە'),        # Keep ێ correct
        (r'ئۆ', 'ئۆ'),            # Keep ۆ correct
    ]
    
    for pattern, replacement in pattern_fixes:
        fixed_text = re.sub(pattern, replacement, fixed_text)
    
    # Fix common Kurdish words that often get misrecognized
    word_fixes = {
        'كورد': 'کورد',
        'نان': 'نان', 
        'ثاو': 'ئاو',
        'ماڵ': 'ماڵ',
        'باش': 'باش',
        'گوڵ': 'گوڵ',           # Rose/flower
        'ڕاست': 'ڕاست',         # Right/true
        'ژیان': 'ژیان',         # Life
        'ڤیدیو': 'ڤیدیو',       # Video
        'گەڵ': 'گەڵ',           # With
        'ڵام': 'ڵام',           # But
        'ڕەنگ': 'ڕەنگ',         # Color
        'ژن': 'ژن',             # Woman
        'ڤان': 'ڤان',           # Van
        'ئێوە': 'ئێوە',         # You (plural)
        'ئۆتۆ': 'ئۆتۆ',         # Auto
    }
    
    for arabic_word, kurdish_word in word_fixes.items():
        fixed_text = fixed_text.replace(arabic_word, kurdish_word)
    
    return fixed_text

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
        
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        fixed_text = fix_kurdish_characters(text)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
    else:
        # Read from stdin
        text = sys.stdin.read()
        fixed_text = fix_kurdish_characters(text)
        print(fixed_text, end='')
