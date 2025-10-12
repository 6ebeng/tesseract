#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boost ZWNJ percentage in corpus by:
1. Filtering existing lines for high ZWNJ content
2. Augmenting text by adding ZWNJs where appropriate
3. Duplicating ZWNJ-rich lines
"""

import sys
from pathlib import Path

def analyze_zwnj(text):
    """Return ZWNJ statistics"""
    if not text:
        return 0, 0.0
    zwnj_count = text.count('\u200c')
    zwnj_pct = (zwnj_count / len(text)) * 100 if len(text) > 0 else 0
    return zwnj_count, zwnj_pct

def add_zwnj_after_prefix(text):
    """
    Add ZWNJ after common Kurdish prefixes where missing.
    Common prefixes: به‌ بۆ له‌ تا له‌
    """
    # Patterns: prefix + character (but not already with ZWNJ)
    replacements = [
        # به + letter → به‌ + letter
        ('به([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'به\u200c\\1'),
        # بۆ + letter → بۆ + letter (less common, but sometimes needed)
        # له + letter → له‌ + letter
        ('له([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'له\u200c\\1'),
        # تا + letter → تا + letter
        ('تا([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'تا\u200c\\1'),
        # می + letter → می + letter  
        ('می([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'می\u200c\\1'),
        # نا + letter → نا + letter
        ('نا([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'نا\u200c\\1'),
        # دا + letter → دا + letter
        ('دا([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'دا\u200c\\1'),
        # نه‌ + letter → نه‌ + letter
        ('نه([ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەویێۆ])', 'نه\u200c\\1'),
    ]
    
    import re
    modified = text
    changes = 0
    for pattern, replacement in replacements:
        # Only replace if not already has ZWNJ
        pattern_no_zwnj = pattern.replace('\\u200c', '')
        before = modified
        modified = re.sub(pattern_no_zwnj, replacement, modified)
        if modified != before:
            changes += 1
    
    return modified, changes

def filter_and_boost_corpus(input_file, output_file, target_zwnj_pct=8.0, min_line_zwnj=5.0):
    """
    Filter corpus for ZWNJ-rich content and boost ZWNJ percentage.
    
    Args:
        input_file: Source corpus
        output_file: Enhanced corpus  
        target_zwnj_pct: Target ZWNJ percentage (8-10%)
        min_line_zwnj: Minimum ZWNJ% to keep a line
    """
    
    print("="*70)
    print("ZWNJ CORPUS BOOSTER")
    print("="*70)
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Target ZWNJ: {target_zwnj_pct:.1f}%")
    print(f"   Min line ZWNJ: {min_line_zwnj:.1f}%")
    print()
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    print(f"📖 Loaded {len(lines):,} lines")
    
    # Analyze input
    input_text = '\n'.join(lines)
    input_zwnj, input_pct = analyze_zwnj(input_text)
    print(f"   Input ZWNJ: {input_zwnj:,} ({input_pct:.2f}%)")
    
    # Process lines
    high_zwnj_lines = []
    medium_zwnj_lines = []
    low_zwnj_lines = []
    augmented_lines = []
    
    for line in lines:
        _, line_pct = analyze_zwnj(line)
        
        # Augment line by adding ZWNJs
        augmented, changes = add_zwnj_after_prefix(line)
        aug_zwnj, aug_pct = analyze_zwnj(augmented)
        
        if aug_pct >= 10.0:  # Very high ZWNJ
            high_zwnj_lines.append(augmented)
            if changes > 0:
                augmented_lines.append(augmented)
        elif aug_pct >= min_line_zwnj:  # Good ZWNJ
            medium_zwnj_lines.append(augmented)
            if changes > 0:
                augmented_lines.append(augmented)
        elif aug_pct >= 3.0:  # Low but acceptable
            low_zwnj_lines.append(augmented)
        # else: skip lines with <3% ZWNJ
    
    print(f"\n📊 Line Classification:")
    print(f"   High ZWNJ (≥10%): {len(high_zwnj_lines):,}")
    print(f"   Medium ZWNJ (5-10%): {len(medium_zwnj_lines):,}")
    print(f"   Low ZWNJ (3-5%): {len(low_zwnj_lines):,}")
    print(f"   Augmented: {len(augmented_lines):,}")
    
    # Build output corpus
    output_lines = []
    
    # Add all high ZWNJ lines (with duplicates for emphasis)
    output_lines.extend(high_zwnj_lines)
    output_lines.extend(high_zwnj_lines)  # Duplicate
    
    # Add medium ZWNJ lines
    output_lines.extend(medium_zwnj_lines)
    
    # Add some low ZWNJ for variety
    output_lines.extend(low_zwnj_lines[:len(low_zwnj_lines)//2])
    
    # Add augmented variations
    output_lines.extend(augmented_lines)
    
    # Deduplicate
    output_lines = list(set(output_lines))
    
    # Analyze output
    output_text = '\n'.join(output_lines)
    output_zwnj, output_pct = analyze_zwnj(output_text)
    output_words = sum(len(line.split()) for line in output_lines)
    
    print(f"\n📦 Output Corpus:")
    print(f"   Lines: {len(output_lines):,}")
    print(f"   Words: {output_words:,}")
    print(f"   Characters: {len(output_text):,}")
    print(f"   ZWNJ: {output_zwnj:,} ({output_pct:.2f}%)")
    
    # Check if we hit target
    if output_pct >= target_zwnj_pct:
        print(f"\n✅ Target achieved: {output_pct:.2f}% ≥ {target_zwnj_pct:.1f}%")
    else:
        print(f"\n⚠️ Below target: {output_pct:.2f}% < {target_zwnj_pct:.1f}%")
        print(f"   Consider adding more ZWNJ-rich source material")
    
    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in sorted(output_lines):  # Sort for consistency
            f.write(line + '\n')
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Growth summary
    print(f"\n📈 Changes:")
    print(f"   Lines: {len(lines):,} → {len(output_lines):,} ({len(output_lines)-len(lines):+,})")
    print(f"   Words: {len(input_text.split()):,} → {output_words:,} ({output_words-len(input_text.split()):+,})")
    print(f"   ZWNJ%: {input_pct:.2f}% → {output_pct:.2f}% ({output_pct-input_pct:+.2f} pp)")
    
    print("="*70)
    print("✅ BOOST COMPLETE")
    print("="*70)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 boost_zwnj.py <input.txt> <output.txt> [target_pct] [min_line_pct]")
        print()
        print("Example:")
        print("  python3 boost_zwnj.py ckb.training_text ckb_zwnj_boosted.txt 8.0 5.0")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    target_pct = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
    min_line_pct = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
    
    filter_and_boost_corpus(input_file, output_file, target_pct, min_line_pct)

if __name__ == '__main__':
    main()
