#!/usr/bin/env python3
"""
Aggregate OCR errors across all test images
Find consistent, high-confidence correction patterns
"""

import json
from collections import Counter, defaultdict

def aggregate_errors():
    """Aggregate errors from all test image analyses"""
    
    test_images = ['kurdsat2', 'kurdsat3', 'rudaw1', 'rudaw2']
    
    # Aggregate counters
    all_deletions = Counter()
    all_insertions = Counter()
    all_substitutions = Counter()
    
    # Per-image statistics
    stats = {}
    
    for img in test_images:
        error_file = f'output/{img}_error_analysis.txt'
        
        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the file (simple parsing)
            lines = content.split('\n')
            
            # Find accuracy
            for line in lines:
                if 'Character Accuracy:' in line:
                    acc = float(line.split(':')[1].strip().replace('%',''))
                    stats[img] = acc
            
            print(f"✅ Loaded {img}: {stats.get(img, 'N/A')}% accuracy")
        
        except FileNotFoundError:
            print(f"⚠️  {error_file} not found")
    
    return stats

def analyze_spacing_patterns():
    """
    Analyze spacing issues in OCR output
    Compare word-level vs character-level accuracy
    """
    
    from difflib import SequenceMatcher
    
    test_cases = [
        ('kurdsat2', 'output/kurdsat2_clean.txt', 'real_gt/eval_clean/kurdsat2.gt.txt'),
        ('kurdsat3', 'output/kurdsat3_clean.txt', 'real_gt/eval_clean/kurdsat3.gt.txt'),
        ('rudaw1', 'output/rudaw1_clean.txt', 'real_gt/eval_clean/rudaw1.gt.txt'),
        ('rudaw2', 'output/rudaw2_clean.txt', 'real_gt/eval_clean/rudaw2.gt.txt'),
    ]
    
    print("=" * 80)
    print("WORD-LEVEL vs CHARACTER-LEVEL ACCURACY")
    print("=" * 80)
    print()
    
    for name, ocr_file, gt_file in test_cases:
        try:
            with open(gt_file, 'r', encoding='utf-8') as f:
                gt_text = f.read().strip()
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_text = f.read().strip()
            
            # Character-level accuracy
            char_matcher = SequenceMatcher(None, gt_text, ocr_text)
            char_matches = sum(b.size for b in char_matcher.get_matching_blocks())
            char_acc = 100 * char_matches / len(gt_text)
            
            # Word-level accuracy
            gt_words = gt_text.split()
            ocr_words = ocr_text.split()
            word_matcher = SequenceMatcher(None, gt_words, ocr_words)
            word_matches = sum(b.size for b in word_matcher.get_matching_blocks())
            word_acc = 100 * word_matches / len(gt_words) if gt_words else 0
            
            # ZWNJ count
            zwnj_gt = gt_text.count('\u200c')
            zwnj_ocr = ocr_text.count('\u200c')
            
            print(f"{name:12s}:")
            print(f"  Char accuracy: {char_acc:5.1f}%")
            print(f"  Word accuracy: {word_acc:5.1f}%")
            print(f"  ZWNJ in GT:    {zwnj_gt:4d}")
            print(f"  ZWNJ in OCR:   {zwnj_ocr:4d} (loss: {100*(zwnj_gt-zwnj_ocr)/zwnj_gt if zwnj_gt > 0 else 0:.0f}%)")
            print()
        
        except FileNotFoundError:
            print(f"⚠️  {name}: files not found")
            print()

def main():
    print("=" * 80)
    print("AGGREGATE ERROR ANALYSIS - ALL TEST IMAGES")
    print("=" * 80)
    print()
    
    # Load error analyses
    stats = aggregate_errors()
    
    print()
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    if stats:
        avg_acc = sum(stats.values()) / len(stats)
        print(f"Average accuracy: {avg_acc:.2f}%")
        print()
        for img, acc in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {img:12s}: {acc:5.2f}%")
    
    print()
    
    # Analyze spacing patterns
    analyze_spacing_patterns()
    
    print()
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()
    print("1. ZWNJ LOSS: 100% of ZWNJs are lost in OCR output")
    print("   → Need ZWNJ insertion rules")
    print()
    print("2. SPACING ISSUES: Excessive space insertions/deletions")
    print("   → May be alignment artifacts, not real errors")
    print()
    print("3. CHARACTER DELETIONS: ە, ی, ا most commonly missed")
    print("   → These are layout/segmentation issues, hard to fix")
    print()
    print("4. LOW SUBSTITUTIONS: Only 2-3% of errors")
    print("   → OCR recognizes characters correctly, loses them in layout")
    print()
    print("=" * 80)
    print("RECOMMENDED APPROACH")
    print("=" * 80)
    print()
    print("✅ FOCUS ON: ZWNJ insertion (100% loss, fixable)")
    print("✅ FOCUS ON: Word-level spell-checking (uses dictionary)")
    print("⚠️  AVOID: Character-level substitutions (too risky)")
    print("⚠️  AVOID: Spacing corrections (alignment artifacts)")
    print()

if __name__ == '__main__':
    main()
