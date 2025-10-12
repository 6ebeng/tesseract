#!/usr/bin/env python3
import re

with open('mgk_phase4.txt', 'r', encoding='utf-8') as f:
    ocr_text = f.read()

with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt_text = f.read()

# Count ه in both texts
he_ocr = ocr_text.count('ه')
he_gt = gt_text.count('ه')

print(f"ه (he) in OCR output: {he_ocr}")
print(f"ه (he) in ground truth: {he_gt}")
print()

# Find ه+consonant patterns
pattern = r'ه[ولمربكستندڵقخزشغفڤگی،.]'
matches_ocr = re.findall(pattern, ocr_text)
matches_gt = re.findall(pattern, gt_text)

print(f"ه+consonant in OCR: {len(matches_ocr)}")
print(f"ه+consonant in GT: {len(matches_gt)}")
print()

print("First 30 OCR matches:")
for i, m in enumerate(matches_ocr[:30], 1):
    print(f"  {i}. {m}")

# Check if OCR has different characters
print()
print("Checking for alternate 'he' character...")
# Kurdish uses U+0647 (Arabic letter heh)
# But OCR might output U+06C1 (Urdu letter heh goal) or U+06BE (do-chashmee heh)
for char in ocr_text:
    if 'HE' in unicodedata.name(char, ''):
        print(f"  Found: {char} (U+{ord(char):04X}) = {unicodedata.name(char)}")

import unicodedata
print()
print("Sample OCR text (first 200 chars with Unicode codes):")
sample = ocr_text[:200]
for i, char in enumerate(sample):
    if char in 'هەی':
        print(f"  Pos {i}: {char} = U+{ord(char):04X} ({unicodedata.name(char, 'UNKNOWN')})")
