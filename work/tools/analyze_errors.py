#!/usr/bin/env python3
"""
Analyze OCR errors between ground truth and recognized text
Generate detailed error patterns and statistics
"""

import sys
from collections import Counter, defaultdict
import difflib

def load_file(filepath):
    """Load text file with UTF-8 encoding"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def calculate_cer(gt, ocr):
    """Calculate Character Error Rate"""
    # Use difflib for edit distance
    sm = difflib.SequenceMatcher(None, gt, ocr)
    total_chars = len(gt)
    matching_chars = sum(block.size for block in sm.get_matching_blocks())
    errors = total_chars - matching_chars
    cer = errors / total_chars if total_chars > 0 else 0
    return cer, errors, total_chars

def analyze_character_errors(gt, ocr):
    """Analyze character-level substitutions, insertions, deletions"""
    substitutions = Counter()
    insertions = Counter()
    deletions = Counter()
    
    # Use difflib opcodes
    sm = difflib.SequenceMatcher(None, gt, ocr)
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace':
            # Substitution
            gt_chars = gt[i1:i2]
            ocr_chars = ocr[j1:j2]
            if len(gt_chars) == 1 and len(ocr_chars) == 1:
                substitutions[(gt_chars, ocr_chars)] += 1
            elif len(gt_chars) == 1:
                # One char became multiple
                substitutions[(gt_chars, ocr_chars)] += 1
            elif len(ocr_chars) == 1:
                # Multiple chars became one
                substitutions[(gt_chars, ocr_chars)] += 1
            else:
                # Multiple to multiple
                substitutions[(gt_chars, ocr_chars)] += 1
        elif tag == 'delete':
            # Deletion (char in GT but not in OCR)
            for char in gt[i1:i2]:
                deletions[char] += 1
        elif tag == 'insert':
            # Insertion (char in OCR but not in GT)
            for char in ocr[j1:j2]:
                insertions[char] += 1
    
    return substitutions, insertions, deletions

def analyze_word_errors(gt, ocr):
    """Analyze word-level errors"""
    gt_words = gt.split()
    ocr_words = ocr.split()
    
    word_errors = Counter()
    sm = difflib.SequenceMatcher(None, gt_words, ocr_words)
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'replace':
            for gt_word, ocr_word in zip(gt_words[i1:i2], ocr_words[j1:j2]):
                word_errors[(gt_word, ocr_word)] += 1
        elif tag == 'delete':
            for word in gt_words[i1:i2]:
                word_errors[(word, '[DELETED]')] += 1
        elif tag == 'insert':
            for word in ocr_words[j1:j2]:
                word_errors[('[INSERTED]', word)] += 1
    
    return word_errors

def analyze_context_errors(gt, ocr, window=5):
    """Analyze errors in context"""
    sm = difflib.SequenceMatcher(None, gt, ocr)
    context_errors = []
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            # Get context
            context_start = max(0, i1 - window)
            context_end = min(len(gt), i2 + window)
            
            gt_context = gt[context_start:context_end]
            gt_error = gt[i1:i2]
            ocr_error = ocr[j1:j2]
            
            context_errors.append({
                'type': tag,
                'gt_context': gt_context,
                'gt_error': gt_error,
                'ocr_error': ocr_error,
                'position': i1
            })
    
    return context_errors

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 analyze_errors.py <ground_truth.txt> <recognized.txt>")
        sys.exit(1)
    
    gt_file = sys.argv[1]
    ocr_file = sys.argv[2]
    
    print("=" * 80)
    print("OCR ERROR ANALYSIS")
    print("=" * 80)
    print()
    
    # Load files
    print(f"Loading ground truth: {gt_file}")
    gt = load_file(gt_file)
    print(f"Loading OCR output: {ocr_file}")
    ocr = load_file(ocr_file)
    
    print()
    print("FILE STATISTICS:")
    print("-" * 80)
    print(f"Ground truth length: {len(gt)} characters, {len(gt.split())} words")
    print(f"OCR output length: {len(ocr)} characters, {len(ocr.split())} words")
    print()
    
    # Calculate CER
    cer, errors, total = calculate_cer(gt, ocr)
    print("CHARACTER ERROR RATE (CER):")
    print("-" * 80)
    print(f"Total characters: {total}")
    print(f"Total errors: {errors}")
    print(f"CER: {cer*100:.2f}%")
    print(f"Accuracy: {(1-cer)*100:.2f}%")
    print()
    
    # Character errors
    print("CHARACTER-LEVEL ERROR ANALYSIS:")
    print("-" * 80)
    subs, ins, dels = analyze_character_errors(gt, ocr)
    
    print(f"\nTop 20 character substitutions (GT → OCR):")
    for (gt_char, ocr_char), count in subs.most_common(20):
        print(f"  '{gt_char}' → '{ocr_char}': {count} times ({count/errors*100:.1f}% of errors)")
    
    print(f"\nTop 10 deleted characters (in GT, missing in OCR):")
    for char, count in dels.most_common(10):
        print(f"  '{char}': {count} times")
    
    print(f"\nTop 10 inserted characters (in OCR, not in GT):")
    for char, count in ins.most_common(10):
        print(f"  '{char}': {count} times")
    
    # Word errors
    print()
    print("WORD-LEVEL ERROR ANALYSIS:")
    print("-" * 80)
    word_errors = analyze_word_errors(gt, ocr)
    print(f"\nTop 20 word errors (GT → OCR):")
    for (gt_word, ocr_word), count in word_errors.most_common(20):
        if gt_word == '[INSERTED]':
            print(f"  [INSERTED] → '{ocr_word}': {count} times")
        elif ocr_word == '[DELETED]':
            print(f"  '{gt_word}' → [DELETED]: {count} times")
        else:
            print(f"  '{gt_word}' → '{ocr_word}': {count} times")
    
    # Context errors
    print()
    print("ERROR CONTEXT EXAMPLES (first 10):")
    print("-" * 80)
    context_errors = analyze_context_errors(gt, ocr, window=10)
    for i, err in enumerate(context_errors[:10], 1):
        print(f"\n{i}. {err['type'].upper()} at position {err['position']}:")
        print(f"   Context: ...{err['gt_context']}...")
        print(f"   GT:  '{err['gt_error']}'")
        print(f"   OCR: '{err['ocr_error']}'")
    
    # Summary statistics
    print()
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"Total substitutions: {sum(subs.values())}")
    print(f"Total deletions: {sum(dels.values())}")
    print(f"Total insertions: {sum(ins.values())}")
    print(f"Unique substitution patterns: {len(subs)}")
    print()
    
    # Save detailed report
    report_file = ocr_file.replace('.txt', '_error_report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DETAILED OCR ERROR REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"CER: {cer*100:.2f}%\n")
        f.write(f"Total errors: {errors}\n\n")
        
        f.write("ALL CHARACTER SUBSTITUTIONS:\n")
        f.write("-" * 80 + "\n")
        for (gt_char, ocr_char), count in subs.most_common():
            f.write(f"'{gt_char}' → '{ocr_char}': {count}\n")
        
        f.write("\n\nALL WORD ERRORS:\n")
        f.write("-" * 80 + "\n")
        for (gt_word, ocr_word), count in word_errors.most_common():
            f.write(f"'{gt_word}' → '{ocr_word}': {count}\n")
    
    print(f"Detailed report saved to: {report_file}")

if __name__ == '__main__':
    main()
