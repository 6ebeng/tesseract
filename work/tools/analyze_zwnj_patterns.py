#!/usr/bin/env python3
"""
Kurdish ZWNJ Pattern Analyzer
Analyzes where ZWNJ appears in Kurdish text to inform rule development
"""

import re
from collections import Counter

def analyze_zwnj_patterns(text):
    """Analyze ZWNJ usage patterns in Kurdish text"""
    
    zwnj = '\u200c'
    
    # Overall stats
    total_zwnj = text.count(zwnj)
    total_chars = len(text)
    
    print("=" * 60)
    print("KURDISH ZWNJ PATTERN ANALYSIS")
    print("=" * 60)
    print(f"Total characters: {total_chars:,}")
    print(f"Total ZWNJs: {total_zwnj}")
    print(f"ZWNJ density: {total_zwnj/total_chars*100:.2f}%")
    print()
    
    # 1. Prefix patterns (دە‌, بە‌, لە‌, etc.)
    print("=== 1. PREFIX PATTERNS (verb prefixes) ===")
    prefix_patterns = [
        (r'دە' + zwnj, 'دە‌ (present tense)'),
        (r'بە' + zwnj, 'بە‌ (with/by)'),
        (r'لە' + zwnj, 'لە‌ (in/at)'),
        (r'بۆ' + zwnj, 'بۆ‌ (for)'),
    ]
    for pattern, desc in prefix_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            print(f"  {desc}: {count}x")
    
    # 2. Ezafe patterns (‌ی, ‌ە)
    print("\n=== 2. EZAFE PATTERNS (possessive/descriptive) ===")
    ezafe_patterns = [
        (zwnj + r'ی', '‌ی (ezafe)'),
        (zwnj + r'ە', '‌ە (ezafe -e)'),
    ]
    for pattern, desc in ezafe_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            print(f"  {desc}: {count}x")
    
    # 3. Suffix patterns (‌تر, ‌ترین, ‌ان, ‌ەکان)
    print("\n=== 3. SUFFIX PATTERNS ===")
    suffix_patterns = [
        (zwnj + r'تر\b', '‌تر (comparative)'),
        (zwnj + r'ترین\b', '‌ترین (superlative)'),
        (zwnj + r'ان\b', '‌ان (plural)'),
        (zwnj + r'ەکان\b', '‌ەکان (definite plural)'),
        (zwnj + r'یش\b', '‌یش (also)'),
        (zwnj + r'دا\b', '‌دا (in/at)'),
    ]
    for pattern, desc in suffix_patterns:
        count = len(re.findall(pattern, text))
        if count > 0:
            print(f"  {desc}: {count}x")
    
    # 4. Compound words (word‌word)
    print("\n=== 4. COMPOUND WORD PATTERNS ===")
    # Find compound words (Kurdish letter + ZWNJ + Kurdish letter)
    kurdish_letter = r'[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهەیێ]'
    compound = re.findall(f'{kurdish_letter}{{2,}}' + zwnj + f'{kurdish_letter}{{2,}}', text)
    print(f"  Total compound words: {len(compound)}")
    
    if compound:
        # Show most common compounds
        counter = Counter(compound)
        print("  Most frequent compounds:")
        for word, count in counter.most_common(15):
            print(f"    {word}: {count}x")
    
    # 5. Word boundary patterns
    print("\n=== 5. WORD BOUNDARY PATTERNS ===")
    # ZWNJ after space (start of word)
    after_space = len(re.findall(r' ' + zwnj, text))
    # ZWNJ before space (end of word)
    before_space = len(re.findall(zwnj + r' ', text))
    # ZWNJ surrounded by letters
    within_word = len(re.findall(kurdish_letter + zwnj + kurdish_letter, text))
    
    print(f"  After space (word start): {after_space}")
    print(f"  Before space (word end): {before_space}")
    print(f"  Within word (letter‌letter): {within_word}")
    
    # 6. Context analysis (3 chars before and after)
    print("\n=== 6. DETAILED CONTEXT SAMPLES (first 20) ===")
    contexts = []
    for match in re.finditer(r'.{0,5}' + zwnj + r'.{0,5}', text):
        contexts.append(match.group())
    
    for i, ctx in enumerate(contexts[:20], 1):
        # Highlight ZWNJ
        highlighted = ctx.replace(zwnj, '‌⟨ZWNJ⟩‌')
        print(f"  {i:2d}. {highlighted}")
    
    print("\n" + "=" * 60)
    print(f"TOTAL ZWNJ INSTANCES ANALYZED: {total_zwnj}")
    print("=" * 60)

if __name__ == "__main__":
    # Read ground truth
    with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    analyze_zwnj_patterns(text)
