#!/usr/bin/env python3
"""Merge all Phase 5 corpus sources"""
import re
from pathlib import Path

ZWNJ = '\u200c'

def normalize(line):
    return re.sub(r'\s+', ' ', line.strip())

work_dir = Path(__file__).parent.parent

# Read all sources
print("Reading sources...")
phase4 = [normalize(l) for l in open(work_dir / 'corpus/ckb.training_text', 'r', encoding='utf-8') if l.strip()]
wiki1 = [normalize(l) for l in open(work_dir / 'corpus/wikipedia_phase5.txt', 'r', encoding='utf-8') if l.strip()]
wiki2 = [normalize(l) for l in open(work_dir / 'corpus/wikipedia_phase5_additional.txt', 'r', encoding='utf-8') if l.strip()]

print(f"Phase 4: {len(phase4)} lines")
print(f"Wikipedia batch 1: {len(wiki1)} lines")
print(f"Wikipedia batch 2: {len(wiki2)} lines")

# Merge and deduplicate
print("\nDeduplicating...")
seen = set()
merged = []
for source_lines in [phase4, wiki1, wiki2]:
    for line in source_lines:
        if line and line not in seen:
            merged.append(line)
            seen.add(line)

# Stats
total_words = sum(len(l.split()) for l in merged)
total_chars = sum(len(l) for l in merged)
total_zwnj = sum(l.count(ZWNJ) for l in merged)

print(f'\nFinal corpus:')
print(f'  Lines: {len(merged):,}')
print(f'  Words: {total_words:,}')
print(f'  Characters: {total_chars:,}')
print(f'  ZWNJ count: {total_zwnj:,}')
print(f'  ZWNJ density: {total_zwnj/total_chars*100:.2f}%')

# Save
output = work_dir / 'corpus/ckb_phase5.training_text'
with open(output, 'w', encoding='utf-8') as f:
    for line in merged:
        f.write(line + '\n')

print(f'\n✅ Saved to {output}')
print(f'   Size: {output.stat().st_size / 1024:.1f} KB')
