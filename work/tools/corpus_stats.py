#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import unicodedata as ud
from collections import Counter

if len(sys.argv) < 2:
    print("Usage: corpus_stats.py <file> [topN]", file=sys.stderr)
    sys.exit(1)

path = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    txt = f.read()

# NFC normalize for stable counts
try:
    import unicodedata
    txt = unicodedata.normalize('NFC', txt)
except Exception:
    pass

char_counts = Counter(txt)
# Filter out whitespace-only
for k in list(char_counts.keys()):
    if k.isspace():
        del char_counts[k]

print(f"Total unique chars: {len(char_counts)}")
for ch, cnt in char_counts.most_common(N):
    cp = f"U+{ord(ch):04X}"
    name = ''
    try:
        name = ud.name(ch)
    except Exception:
        name = 'UNKNOWN'
    print(f"{ch}\t{cnt}\t{cp}\t{name}")
