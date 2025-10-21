#!/usr/bin/env python3
"""
Detailed OCR Error Analysis
Identify top error patterns to create targeted correction rules
"""

import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

def analyze_errors(gt_file, ocr_file):
    """
    Perform detailed character-level error analysis
    
    Returns:
        Dictionary with error statistics and patterns
    """
    
    with open(gt_file, 'r', encoding='utf-8') as f:
        gt = f.read()
    
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr = f.read()
    
    # Use SequenceMatcher for alignment
    matcher = SequenceMatcher(None, gt, ocr)
    
    # Track error types
    deletions = Counter()  # GT char that OCR missed
    insertions = Counter()  # OCR char that wasn't in GT
    substitutions = Counter()  # GT char → OCR char
    deletion_contexts = []  # Context around deletions
    insertion_contexts = []  # Context around insertions
    substitution_contexts = []  # Context around substitutions
    
    # Track positions for context
    gt_pos = 0
    ocr_pos = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            gt_pos = i2
            ocr_pos = j2
            continue
        
        if tag == 'delete':
            # GT has chars that OCR doesn't
            for i in range(i1, i2):
                char = gt[i]
                deletions[char] += 1
                # Get context (3 chars before/after)
                ctx_start = max(0, i-3)
                ctx_end = min(len(gt), i+4)
                context = gt[ctx_start:i] + '[' + char + ']' + gt[i+1:ctx_end]
                deletion_contexts.append((char, context))
            gt_pos = i2
        
        elif tag == 'insert':
            # OCR has chars that GT doesn't
            for j in range(j1, j2):
                char = ocr[j]
                insertions[char] += 1
                ctx_start = max(0, j-3)
                ctx_end = min(len(ocr), j+4)
                context = ocr[ctx_start:j] + '[' + char + ']' + ocr[j+1:ctx_end]
                insertion_contexts.append((char, context))
            ocr_pos = j2
        
        elif tag == 'replace':
            # Characters differ
            gt_str = gt[i1:i2]
            ocr_str = ocr[j1:j2]
            
            # Simple case: same length
            if len(gt_str) == len(ocr_str):
                for k in range(len(gt_str)):
                    gt_char = gt_str[k]
                    ocr_char = ocr_str[k]
                    substitutions[(gt_char, ocr_char)] += 1
                    ctx_start = max(0, i1+k-3)
                    ctx_end = min(len(gt), i1+k+4)
                    context = gt[ctx_start:i1+k] + '[' + gt_char + '→' + ocr_char + ']' + gt[i1+k+1:ctx_end]
                    substitution_contexts.append((gt_char, ocr_char, context))
            else:
                # Complex replacement - treat as delete + insert
                for char in gt_str:
                    deletions[char] += 1
                for char in ocr_str:
                    insertions[char] += 1
            
            gt_pos = i2
            ocr_pos = j2
    
    # Calculate statistics
    total_errors = sum(deletions.values()) + sum(insertions.values()) + sum(substitutions.values())
    
    return {
        'deletions': deletions,
        'insertions': insertions,
        'substitutions': substitutions,
        'deletion_contexts': deletion_contexts,
        'insertion_contexts': insertion_contexts,
        'substitution_contexts': substitution_contexts,
        'total_errors': total_errors,
        'gt_length': len(gt),
        'ocr_length': len(ocr)
    }

def print_report(analysis, image_name):
    """Print detailed error report"""
    
    print("=" * 80)
    print(f"OCR ERROR ANALYSIS: {image_name}")
    print("=" * 80)
    print()
    
    print(f"Ground Truth Length: {analysis['gt_length']:,} chars")
    print(f"OCR Output Length:   {analysis['ocr_length']:,} chars")
    print(f"Total Errors:        {analysis['total_errors']:,} chars")
    print(f"Character Accuracy:  {100 * (1 - analysis['total_errors']/analysis['gt_length']):.2f}%")
    print()
    
    # Error breakdown
    del_count = sum(analysis['deletions'].values())
    ins_count = sum(analysis['insertions'].values())
    sub_count = sum(analysis['substitutions'].values())
    
    print("ERROR BREAKDOWN:")
    print(f"  Deletions:     {del_count:5,} ({100*del_count/analysis['total_errors']:5.1f}%)")
    print(f"  Insertions:    {ins_count:5,} ({100*ins_count/analysis['total_errors']:5.1f}%)")
    print(f"  Substitutions: {sub_count:5,} ({100*sub_count/analysis['total_errors']:5.1f}%)")
    print()
    
    # Top deletions
    print("=" * 80)
    print("TOP 30 DELETED CHARACTERS (GT has, OCR missing)")
    print("=" * 80)
    for i, (char, count) in enumerate(analysis['deletions'].most_common(30), 1):
        char_display = repr(char) if char in [' ', '\n', '\t', '\u200c'] else char
        print(f"{i:2d}. {char_display:10s} : {count:5,} times")
    print()
    
    # Top insertions
    print("=" * 80)
    print("TOP 30 INSERTED CHARACTERS (OCR has, GT doesn't)")
    print("=" * 80)
    for i, (char, count) in enumerate(analysis['insertions'].most_common(30), 1):
        char_display = repr(char) if char in [' ', '\n', '\t', '\u200c'] else char
        print(f"{i:2d}. {char_display:10s} : {count:5,} times")
    print()
    
    # Top substitutions
    print("=" * 80)
    print("TOP 30 CHARACTER SUBSTITUTIONS (GT → OCR)")
    print("=" * 80)
    for i, ((gt_char, ocr_char), count) in enumerate(analysis['substitutions'].most_common(30), 1):
        gt_display = repr(gt_char) if gt_char in [' ', '\n', '\t', '\u200c'] else gt_char
        ocr_display = repr(ocr_char) if ocr_char in [' ', '\n', '\t', '\u200c'] else ocr_char
        print(f"{i:2d}. {gt_display:8s} → {ocr_display:8s} : {count:5,} times")
    print()
    
    # Sample contexts for top errors
    print("=" * 80)
    print("SAMPLE CONTEXTS (Top 10 deletions)")
    print("=" * 80)
    top_deletions = [char for char, count in analysis['deletions'].most_common(10)]
    shown = set()
    for char, context in analysis['deletion_contexts']:
        if char in top_deletions and char not in shown and len(shown) < 10:
            print(f"{char}: {context}")
            shown.add(char)
    print()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 detailed_error_analysis.py <ocr_file> <gt_file>")
        sys.exit(1)
    
    ocr_file = sys.argv[1]
    gt_file = sys.argv[2]
    
    # Extract image name from file path
    import os
    image_name = os.path.basename(ocr_file).replace('_clean.txt', '').replace('.txt', '')
    
    print(f"Analyzing: {image_name}")
    print(f"OCR file:  {ocr_file}")
    print(f"GT file:   {gt_file}")
    print()
    
    analysis = analyze_errors(gt_file, ocr_file)
    print_report(analysis, image_name)
    
    print("=" * 80)
    print("✅ Analysis complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
