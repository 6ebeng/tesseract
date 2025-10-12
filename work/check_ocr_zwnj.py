#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check ZWNJ in OCR output vs ground truth"""

import sys

# Read OCR output
with open('/tmp/ocr_output.txt', 'r', encoding='utf-8') as f:
    ocr_text = f.read()

# Read ground truth
with open('/mnt/c/tesseract/work/real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt_text = f.read()

# Count ZWNJ
ocr_zwnj = ocr_text.count('\u200c')
gt_zwnj = gt_text.count('\u200c')

print("="*60)
print("ZWNJ Analysis")
print("="*60)
print(f"\nOCR Output:")
print(f"  Total chars: {len(ocr_text):,}")
print(f"  ZWNJ count: {ocr_zwnj}")
print(f"  ZWNJ %: {ocr_zwnj/len(ocr_text)*100:.2f}%" if len(ocr_text) > 0 else "  ZWNJ %: N/A")

print(f"\nGround Truth:")
print(f"  Total chars: {len(gt_text):,}")
print(f"  ZWNJ count: {gt_zwnj}")
print(f"  ZWNJ %: {gt_zwnj/len(gt_text)*100:.2f}%")

print(f"\nComparison:")
print(f"  ZWNJ gap: {gt_zwnj - ocr_zwnj} missing")
print(f"  Recovery rate: {ocr_zwnj/gt_zwnj*100:.1f}%")
print("="*60)
