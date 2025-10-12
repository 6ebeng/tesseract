#!/usr/bin/env python3
"""
Align OCR output with ground truth to see where characters match/mismatch
"""

with open('mgk_phase4.txt', 'r', encoding='utf-8') as f:
    ocr = f.read()

with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt = f.read()

ZWNJ = '\u200c'

# Remove ZWNJs from ground truth for character-level comparison
gt_no_zwnj = gt.replace(ZWNJ, '')

print(f"Ground truth length (with ZWNJ): {len(gt)}")
print(f"Ground truth length (without ZWNJ): {len(gt_no_zwnj)}")
print(f"OCR output length: {len(ocr)}")
print()

# Simple character-by-character comparison (first N chars)
max_len = min(len(ocr), len(gt_no_zwnj), 500)

print("Character-by-character comparison (first 500):")
print("=" * 70)

matches = 0
mismatches = 0
he_in_gt = 0
he_in_ocr = 0
he_matches = 0

for i in range(max_len):
    gt_char = gt_no_zwnj[i] if i < len(gt_no_zwnj) else ''
    ocr_char = ocr[i] if i < len(ocr) else ''
    
    if gt_char == 'ه':
        he_in_gt += 1
        if ocr_char == 'ه':
            he_matches += 1
        else:
            if he_in_gt <= 20:  # Show first 20 mismatches
                print(f"Pos {i}: GT='ه' → OCR='{ocr_char}' (U+{ord(ocr_char):04X})")
    
    if gt_char == ocr_char:
        matches += 1
    else:
        mismatches += 1

print()
print(f"Overall matches: {matches}/{max_len} ({100*matches/max_len:.1f}%)")
print(f"Overall mismatches: {mismatches}/{max_len}")
print()
print(f"ه (he) in ground truth: {he_in_gt}")
print(f"ه (he) correctly recognized: {he_matches}")
print(f"ه (he) recognition rate: {100*he_matches/he_in_gt if he_in_gt > 0 else 0:.1f}%")
print()

# Now count ه in full texts
full_he_gt = gt.count('ه')
full_he_ocr = ocr.count('ه')
print(f"Full text - ه in GT: {full_he_gt}")
print(f"Full text - ه in OCR: {full_he_ocr}")
print(f"ه recognition estimate: {100*full_he_ocr/full_he_gt if full_he_gt > 0 else 0:.1f}%")
