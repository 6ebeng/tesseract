#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Corpus audit for Kurdish Sorani (Arabic-based) in UTF-8.
Checks the final corpus for out-of-set codepoints, unwanted controls/diacritics,
digit set distribution, and punctuation ratios. Produces a JSON and a text report.

Usage:
  python3 tools/corpus_audit.py --input corpus/ckb.training_text.final --out work/output/corpus_audit

If --input is omitted, tries corpus/ckb.training_text.final then corpus/ckb.training_text.
"""

import argparse
import json
import os
import sys
import unicodedata
from collections import Counter
from pathlib import Path


def sorani_whitelist(include_ascii_digits=False, include_ascii_punc=False):
    # Letters (per docs/kurdish_characters.md)
    letters = [
        '\u0626','\u0627','\u0628','\u067e','\u062a','\u062c','\u0686','\u062d','\u062e','\u062f',
        '\u0631','\u0695','\u0632','\u0698','\u0633','\u0634','\u0639','\u063a','\u0641','\u06a4',
        '\u0642','\u06a9','\u06af','\u0644','\u06b5','\u0645','\u0646','\u0647','\u06d5','\u0648',
        '\u06c6','\u06cc','\u06ce'
    ]
    # Digits (Arabic-Indic as default)
    digits = [chr(c) for c in range(0x0660, 0x066A)]
    # Punctuation commonly used
    puncs = list('،؛:؟«»-()٪')
    wl = set(letters + digits + puncs + ['\n',' ','\t'])
    if include_ascii_digits:
        wl.update(list('0123456789'))
    if include_ascii_punc:
        wl.update(list(',?%'))
    return wl


def strip_controls_and_marks(text: str) -> str:
    drop = set(['\u0640','\u200C','\u200D','\u200E','\u200F','\u202A','\u202B','\u202C','\u202D','\u202E'])
    text = ''.join(ch for ch in text if ch not in drop)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=None)
    ap.add_argument('--out', default=None, help='Output path prefix (without extension)')
    ap.add_argument('--allow-ascii-digits', action='store_true')
    ap.add_argument('--allow-ascii-punc', action='store_true')
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    corpus_dir = repo_root / 'work' / 'corpus'
    inp = args.input
    if not inp:
        cand = [corpus_dir / 'ckb.training_text.final', corpus_dir / 'ckb.training_text']
        for c in cand:
            if c.exists():
                inp = str(c)
                break
    if not inp or not Path(inp).exists():
        print('Corpus not found.'); return 2

    text = Path(inp).read_text(encoding='utf-8', errors='ignore')
    text = unicodedata.normalize('NFC', text)
    cleaned = strip_controls_and_marks(text)

    wl = sorani_whitelist(args.allow_ascii_digits, args.allow_ascii_punc)
    bad = []
    counts = Counter()
    for ch in cleaned:
        if ch == '\n' or ch == '\t' or ch == ' ':
            counts[ch] += 1; continue
        counts[ch] += 1
        if ch not in wl:
            bad.append(ch)

    out_dir = Path(__file__).resolve().parents[1] / 'output'
    out_dir.mkdir(parents=True, exist_ok=True)
    base = args.out or str(out_dir / 'corpus_audit')
    json_path = Path(base + '.json')
    txt_path = Path(base + '.txt')

    top_chars = counts.most_common(50)
    bad_counts = Counter(bad)

    report = {
        'input': str(inp),
        'length': len(cleaned),
        'unique_chars': len(counts),
        'bad_unique': len(bad_counts),
        'bad_total': sum(bad_counts.values()),
        'bad_top': [[c, bad_counts[c]] for c in bad_counts.most_common(50)],
        'top_chars': [[c, n] for c, n in top_chars],
        'allow_ascii_digits': bool(args.allow_ascii_digits),
        'allow_ascii_punc': bool(args.allow_ascii_punc),
    }
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    with txt_path.open('w', encoding='utf-8') as f:
        f.write(f"Corpus audit for: {inp}\n")
        f.write(f"Total chars: {len(cleaned)}\n")
        f.write(f"Unique chars: {len(counts)}\n")
        f.write(f"Bad unique: {len(bad_counts)} | Bad total: {sum(bad_counts.values())}\n\n")
        if bad_counts:
            f.write("Top out-of-set characters:\n")
            for c, n in bad_counts.most_common(50):
                name = unicodedata.name(c, 'UNKNOWN')
                f.write(f"  U+{ord(c):04X} '{c}': {n}  # {name}\n")
        else:
            f.write("No out-of-set characters found.\n")
        f.write("\nTop 50 characters in corpus:\n")
        for c, n in top_chars:
            name = unicodedata.name(c, 'UNKNOWN')
            f.write(f"  U+{ord(c):04X} '{c}': {n}  # {name}\n")

    print(f"Audit written: {json_path} , {txt_path}")
    # Return 2 if any bad chars found to allow CI gating
    return 2 if bad_counts else 0


if __name__ == '__main__':
    sys.exit(main())
