#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Sorani shaping coverage lines to help text2image render contextual forms
(isolated/initial/medial/final). This doesn't use presentation forms; it relies on
OpenType shaping via Pango/HarfBuzz in text2image.

Writes: work/corpus/shaping_augment.txt
"""
from pathlib import Path

# Sorani letters per docs (Arabic-based Kurdish)
LETTERS = [
    'ئ','ا','ب','پ','ت','ج','چ','ح','خ','د','ر','ڕ','ز','ژ','س','ش','ع','غ','ف','ڤ','ق','ک','گ','ل','ڵ','م','ن','ه','ە','و','ۆ','ی','ێ'
]

# Non-joiners to the right (do not connect to following letter)
NON_JOINERS = set(['ا','د','ر','ڕ','ز','ژ','و','ۆ'])

# A generic joining letter for context (dual-joining)
J = 'ب'

def build_lines():
    lines = []
    for ch in LETTERS:
        # Isolated form context
        lines.append(ch)
        # Final-ish: join from left (J + ch)
        lines.append(J + ch)
        # Initial-ish: join to right (ch + J)
        lines.append(ch + J)
        # Medial-ish: join both sides (J + ch + J)
        lines.append(J + ch + J)
    # Pair each letter with common vowels and connectors to create varied neighborhoods
    VOWELS = ['ا','ە','و','ۆ','ی','ێ']
    for v in VOWELS:
        for ch in LETTERS:
            lines.append(f"{v}{ch}{J}")
            lines.append(f"{J}{ch}{v}")
    # Dedup while preserving order
    seen = set()
    dedup = []
    for L in lines:
        if L not in seen:
            seen.add(L)
            dedup.append(L)
    return dedup

def main():
    work = Path(__file__).resolve().parents[1]
    out_path = work / 'corpus' / 'shaping_augment.txt'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = build_lines()
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Wrote shaping augment: {out_path} ({len(lines)} lines)")

if __name__ == '__main__':
    main()
