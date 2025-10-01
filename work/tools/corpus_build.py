#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build a balanced Kurdish Sorani corpus:
- Scans work/corpus/*.txt (excluding *final*), normalizes (NFC) and optionally applies fixer.
- Deduplicates lines and boosts lines containing rarer Kurdish letters.
- Writes work/corpus/ckb.training_text.final and stats to work/output/.

Usage (from work/):
  python3 tools/corpus_build.py [--min-count 1000] [--fixer]

Notes:
- --min-count is a soft target for minimum character occurrences across target letters.
- If --fixer is set and kurdish_character_fixer.py is present, apply it first.
"""

import argparse
import os
import re
import unicodedata as ud
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
CORPUS_DIR = WORK / 'corpus'
OUT_DIR = WORK / 'output'
TARGET_FINAL = CORPUS_DIR / 'ckb.training_text.final'
FIXER_PATH = WORK / 'kurdish_character_fixer.py'

# Target Kurdish Arabic-based letters (Sorani)
TARGET_CHARS = set("\u0626\u0627\u0628\u067e\u062a\u062c\u0686\u062d\u062e\u062f\u0631\u0695\u0632\u0698\u0633\u0634\u0639\u063a\u0641\u06a4\u0642\u06a9\u06af\u0644\u06b5\u0645\u0646\u0647\u06d5\u0648\u06c6\u06cc\u06ce")

RE_SPACES = re.compile(r"\s+")


def nfc(s: str) -> str:
    try:
        return ud.normalize('NFC', s)
    except Exception:
        return s


def apply_fixer(text: str) -> str:
    # Import fixer dynamically if present
    import importlib.util
    spec = importlib.util.spec_from_file_location('kfix', str(FIXER_PATH))
    if spec and spec.loader:
        kfix = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kfix)
        fixer = getattr(kfix, 'KurdishCharacterFixer', None)
        if fixer:
            return fixer().fix_kurdish_text(text)
    return text


def line_contains_targets(line: str) -> set:
    return set(ch for ch in line if ch in TARGET_CHARS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-count', type=int, default=2000,
                    help='Desired minimum total count for each target char (soft target)')
    ap.add_argument('--fixer', action='store_true', help='Apply kurdish_character_fixer.py if present')
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Gather input files
    if not CORPUS_DIR.exists():
        print(f"Corpus dir missing: {CORPUS_DIR}")
        return 2
    sources = [p for p in CORPUS_DIR.glob('*.txt') if 'final' not in p.name.lower()]
    # Ensure shaping coverage is included first if available
    shaping = CORPUS_DIR / 'shaping_augment.txt'
    if shaping.exists():
        sources = [shaping] + [p for p in sources if p != shaping]
    if not sources:
        print(f"No source corpus files found in {CORPUS_DIR}")
        return 2

    # Load lines
    lines = []
    for p in sources:
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if args.fixer and FIXER_PATH.exists():
            txt = apply_fixer(txt)
        txt = nfc(txt)
        # Normalize whitespace to single spaces and split into lines
        for L in txt.splitlines():
            L = RE_SPACES.sub(' ', L.strip())
            if L:
                lines.append(L)

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for L in lines:
        if L not in seen:
            seen.add(L)
            deduped.append(L)

    # Character histogram
    char_hist = Counter()
    for L in deduped:
        char_hist.update(L)

    # Identify deficits for target chars
    deficits = {}
    for ch in TARGET_CHARS:
        cnt = char_hist.get(ch, 0)
        if cnt < args.min_count:
            deficits[ch] = args.min_count - cnt

    # If no deficits, just write deduped
    balanced = list(deduped)

    if deficits:
        # Index lines by contained target chars
        idx = defaultdict(list)
        for i, L in enumerate(deduped):
            chars = line_contains_targets(L)
            for ch in chars:
                idx[ch].append(i)
        # Greedy oversampling: repeatedly append lines containing most-deficit chars
        # until deficits are reduced or a safety cap is hit
        safety_cap = len(deduped) * 5
        appended = 0
        while deficits and appended < safety_cap:
            # pick char with largest remaining deficit
            ch = max(deficits.items(), key=lambda kv: kv[1])[0]
            candidates = idx.get(ch, [])
            if not candidates:
                # cannot fix this char; drop it from deficits
                deficits.pop(ch, None)
                continue
            # choose the next candidate round-robin
            pos = appended % max(len(candidates), 1)
            L = deduped[candidates[pos]]
            balanced.append(L)
            # update hist/deficits for all chars in this line (approximate)
            for c in line_contains_targets(L):
                char_hist[c] += L.count(c)
                if c in deficits and char_hist[c] >= args.min_count:
                    deficits.pop(c, None)
            appended += 1

    # Write final corpus
    text = '\n'.join(balanced) + '\n'
    TARGET_FINAL.write_text(text, encoding='utf-8')

    # Stats
    (OUT_DIR / 'char_histogram.csv').write_text(
        'char,codepoint,count\n' + '\n'.join(
            f"{ch},{ord(ch):04X},{char_hist.get(ch,0)}" for ch in sorted(TARGET_CHARS)
        ) + '\n', encoding='utf-8'
    )
    (OUT_DIR / 'corpus_stats.txt').write_text(
        f"Sources: {len(sources)} files\n" \
        f"Lines (raw): {len(lines)}\n" \
        f"Lines (deduped): {len(deduped)}\n" \
        f"Lines (final): {len(balanced)}\n",
        encoding='utf-8'
    )

    print(f"Wrote {TARGET_FINAL}")
    print(f"Char histogram -> {OUT_DIR / 'char_histogram.csv'}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
