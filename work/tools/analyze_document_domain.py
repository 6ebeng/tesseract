#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze ground truth text to identify domain and style.
This helps us find matching corpus content.
"""

import re
from collections import Counter

def analyze_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("="*70)
    print("DOCUMENT DOMAIN ANALYSIS")
    print("="*70)
    
    # Basic stats
    words = text.split()
    lines = text.split('\n')
    
    print(f"\n📊 Basic Statistics:")
    print(f"   Lines: {len(lines):,}")
    print(f"   Words: {len(words):,}")
    print(f"   Characters: {len(text):,}")
    print(f"   ZWNJ: {text.count(chr(0x200c)):,} ({text.count(chr(0x200c))/len(text)*100:.2f}%)")
    
    # Word frequency analysis
    word_freq = Counter(words)
    
    print(f"\n📝 Most Common Words (Top 30):")
    for i, (word, count) in enumerate(word_freq.most_common(30), 1):
        print(f"   {i:2d}. {word:20s} ({count:3d}x)")
    
    # Religious/classical indicators
    religious_keywords = [
        'خوا', 'الله', 'قورئان', 'پێغەمبەر', 'نوێژ', 'ڕۆژوو',
        'ئایەت', 'سوورە', 'موحەممەد', 'ئیسلام', 'موسڵمان',
        'خودا', 'دین', 'ئیمان', 'شەریعەت'
    ]
    
    classical_keywords = [
        'وتی', 'گوت', 'فەرموو', 'بووە', 'کرا', 'کراوە',
        'بە‌', 'له‌', 'کە‌', 'دا‌'  # Old-style spacing
    ]
    
    religious_count = sum(text.count(kw) for kw in religious_keywords)
    classical_count = sum(text.count(kw) for kw in classical_keywords)
    
    print(f"\n🔍 Domain Indicators:")
    print(f"   Religious keywords: {religious_count}")
    print(f"   Classical style markers: {classical_count}")
    
    # ZWNJ usage patterns
    zwnj_words = [w for w in words if '\u200c' in w]
    print(f"\n📌 ZWNJ Usage:")
    print(f"   Words with ZWNJ: {len(zwnj_words):,} ({len(zwnj_words)/len(words)*100:.1f}%)")
    print(f"   Sample ZWNJ words:")
    for word in zwnj_words[:15]:
        print(f"      {word}")
    
    # Character distribution
    kurdish_specific = ['ڕ', 'ڵ', 'ێ', 'ۆ', 'ە']
    char_counts = {char: text.count(char) for char in kurdish_specific}
    
    print(f"\n🔤 Kurdish-Specific Characters:")
    for char, count in sorted(char_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {char}: {count:,}x ({count/len(text)*100:.2f}%)")
    
    print("="*70)

if __name__ == '__main__':
    analyze_document('/mnt/c/tesseract/work/real_gt/eval/mgk.gt.txt')
