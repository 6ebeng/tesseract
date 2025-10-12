#!/usr/bin/env python3
"""Diagnose ZWNJ insertion issues"""

# Read files
with open('mgk_phase4.txt', 'r', encoding='utf-8') as f:
    ocr_text = f.read()
with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt_text = f.read()
with open('mgk_phase4_processed.txt', 'r', encoding='utf-8') as f:
    processed = f.read()

ZWNJ = '\u200c'

# Find ZWNJ contexts in ground truth
print('GROUND TRUTH ZWNJ CONTEXTS (first 30):')
print('=' * 70)
gt_positions = [i for i, c in enumerate(gt_text) if c == ZWNJ]
for i, pos in enumerate(gt_positions[:30]):
    start = max(0, pos-5)
    end = min(len(gt_text), pos+6)
    context = gt_text[start:end]
    # Get characters before and after ZWNJ
    before = gt_text[pos-1] if pos > 0 else ''
    after = gt_text[pos+1] if pos < len(gt_text)-1 else ''
    print(f'{i+1:3d}. [{context}]  ({before}‌{after})')

print()
print('PREDICTED ZWNJ CONTEXTS (first 30):')
print('=' * 70)
pred_positions = [i for i, c in enumerate(processed) if c == ZWNJ]
for i, pos in enumerate(pred_positions[:30]):
    start = max(0, pos-5)
    end = min(len(processed), pos+6)
    context = processed[start:end]
    before = processed[pos-1] if pos > 0 else ''
    after = processed[pos+1] if pos < len(processed)-1 else ''
    print(f'{i+1:3d}. [{context}]  ({before}‌{after})')

# Analyze character patterns before/after ZWNJ in ground truth
print()
print('CHARACTER PATTERNS IN GROUND TRUTH:')
print('=' * 70)
before_chars = {}
after_chars = {}
for pos in gt_positions:
    if pos > 0:
        before = gt_text[pos-1]
        before_chars[before] = before_chars.get(before, 0) + 1
    if pos < len(gt_text)-1:
        after = gt_text[pos+1]
        after_chars[after] = after_chars.get(after, 0) + 1

print('Top 20 characters BEFORE ZWNJ:')
for char, count in sorted(before_chars.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f'  {char}: {count}x')

print()
print('Top 20 characters AFTER ZWNJ:')
for char, count in sorted(after_chars.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f'  {char}: {count}x')
