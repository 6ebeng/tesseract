#!/usr/bin/env python3
"""
Analyze OCR errors to identify patterns and improvement opportunities
"""

from collections import Counter, defaultdict
import difflib

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def analyze_errors(ocr_text, gt_text):
    """Analyze character-level errors between OCR and ground truth"""
    
    # Remove ZWNJ from ground truth for fair comparison
    ZWNJ = '\u200c'
    gt_no_zwnj = gt_text.replace(ZWNJ, '')
    
    # Use difflib to align texts
    sm = difflib.SequenceMatcher(None, gt_no_zwnj, ocr_text)
    
    substitutions = Counter()  # gt_char -> ocr_char
    insertions = Counter()     # chars inserted by OCR
    deletions = Counter()      # chars deleted/missed by OCR
    
    total_chars = 0
    correct_chars = 0
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            correct_chars += (i2 - i1)
            total_chars += (i2 - i1)
        elif tag == 'replace':
            # Character substitution
            gt_segment = gt_no_zwnj[i1:i2]
            ocr_segment = ocr_text[j1:j2]
            
            # For single char replacements
            if len(gt_segment) == 1 and len(ocr_segment) == 1:
                substitutions[(gt_segment, ocr_segment)] += 1
            else:
                # Multi-char replacement (alignment issue)
                for c in gt_segment:
                    deletions[c] += 1
                for c in ocr_segment:
                    insertions[c] += 1
            
            total_chars += len(gt_segment)
            
        elif tag == 'delete':
            # Chars in GT but not in OCR (deletion/miss)
            for c in gt_no_zwnj[i1:i2]:
                deletions[c] += 1
            total_chars += (i2 - i1)
            
        elif tag == 'insert':
            # Chars in OCR but not in GT (insertion/hallucination)
            for c in ocr_text[j1:j2]:
                insertions[c] += 1
    
    accuracy = correct_chars / total_chars if total_chars > 0 else 0
    
    return {
        'substitutions': substitutions,
        'insertions': insertions,
        'deletions': deletions,
        'total_chars': total_chars,
        'correct_chars': correct_chars,
        'accuracy': accuracy
    }


def main():
    print("=" * 70)
    print("OCR ERROR ANALYSIS - Phase 4")
    print("=" * 70)
    print()
    
    # Load texts
    ocr = read_file('mgk_phase4.txt')
    gt = read_file('real_gt/eval/mgk.gt.txt')
    
    print(f"Ground truth length: {len(gt)} chars")
    print(f"OCR output length: {len(ocr)} chars")
    print()
    
    # Analyze errors
    results = analyze_errors(ocr, gt)
    
    print(f"Alignment-based accuracy: {results['accuracy']:.2%}")
    print(f"Correct characters: {results['correct_chars']}/{results['total_chars']}")
    print()
    
    # Top substitution errors
    print("TOP 30 SUBSTITUTION ERRORS (GT → OCR):")
    print("-" * 70)
    for (gt_char, ocr_char), count in results['substitutions'].most_common(30):
        gt_name = f"U+{ord(gt_char):04X}" if gt_char else "SPACE"
        ocr_name = f"U+{ord(ocr_char):04X}" if ocr_char else "SPACE"
        print(f"  '{gt_char}' → '{ocr_char}'  ({gt_name} → {ocr_name}): {count}x")
    
    print()
    print("TOP 20 DELETION ERRORS (GT chars missed by OCR):")
    print("-" * 70)
    for char, count in results['deletions'].most_common(20):
        char_name = f"U+{ord(char):04X}" if char else "SPACE"
        print(f"  '{char}' ({char_name}): {count}x")
    
    print()
    print("TOP 20 INSERTION ERRORS (OCR hallucinated chars):")
    print("-" * 70)
    for char, count in results['insertions'].most_common(20):
        char_name = f"U+{ord(char):04X}" if char else "SPACE"
        print(f"  '{char}' ({char_name}): {count}x")
    
    # Error type summary
    total_substitutions = sum(results['substitutions'].values())
    total_deletions = sum(results['deletions'].values())
    total_insertions = sum(results['insertions'].values())
    total_errors = total_substitutions + total_deletions + total_insertions
    
    print()
    print("ERROR TYPE SUMMARY:")
    print("-" * 70)
    print(f"Substitutions: {total_substitutions} ({100*total_substitutions/total_errors:.1f}%)")
    print(f"Deletions:     {total_deletions} ({100*total_deletions/total_errors:.1f}%)")
    print(f"Insertions:    {total_insertions} ({100*total_insertions/total_errors:.1f}%)")
    print(f"Total errors:  {total_errors}")
    print()
    
    # Character-specific accuracy
    print("CHARACTER-SPECIFIC ERRORS (ه analysis):")
    print("-" * 70)
    he_substitutions = [(gt, ocr, cnt) for (gt, ocr), cnt in results['substitutions'].items() if gt == 'ه']
    he_deletions = results['deletions']['ه']
    
    if he_substitutions:
        print(f"'ه' (he) substitution errors:")
        for gt, ocr, count in sorted(he_substitutions, key=lambda x: x[2], reverse=True):
            print(f"  'ه' → '{ocr}': {count}x")
    if he_deletions:
        print(f"'ه' (he) deletion errors: {he_deletions}x")
    
    # Count ه in both texts
    he_in_gt = gt.replace('\u200c', '').count('ه')
    he_in_ocr = ocr.count('ه')
    he_errors = sum(cnt for _, _, cnt in he_substitutions) + he_deletions
    
    print()
    print(f"'ه' in ground truth: {he_in_gt}")
    print(f"'ه' correctly recognized: {he_in_gt - he_errors} (~{100*(he_in_gt - he_errors)/he_in_gt:.1f}%)")
    print(f"'ه' errors: {he_errors} (~{100*he_errors/he_in_gt:.1f}%)")


if __name__ == "__main__":
    main()
