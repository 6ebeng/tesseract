#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge Phase 3 corpus sources"""

files = [
    '/mnt/c/tesseract/work/corpus/ckb_zwnj_boosted.txt',
    '/mnt/c/tesseract/work/corpus/ckb_historical.txt',
    '/mnt/c/tesseract/work/real_gt/eval/mgk.gt.txt',
]

lines = set()
for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and len(line) > 10:  # Skip very short lines
                    lines.add(line)
    except FileNotFoundError:
        print(f"⚠️ File not found: {file}")

print(f"📊 Merged corpus:")
print(f"   Unique lines: {len(lines):,}")

text = '\n'.join(lines)
zwnj = text.count('\u200c')
words = text.split()

print(f"   Words: {len(words):,}")
print(f"   Characters: {len(text):,}")
print(f"   ZWNJ: {zwnj:,} ({zwnj/len(text)*100:.2f}%)")

# Write output
output = '/mnt/c/tesseract/work/corpus/ckb_phase3.txt'
with open(output, 'w', encoding='utf-8') as f:
    for line in sorted(lines):
        f.write(line + '\n')

print(f"✅ Saved to: {output}")
