#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Evaluate real-world CER for ckb on work/real_gt/eval images.
- Expects pairs: <name>.tif (or .png/.jpg) and <name>.gt.txt with the exact text.
- Runs tesseract -l ckb --psm 6 and computes CER, reporting per-file and averages.
- Writes CSV to work/output/real_metrics.csv and a short summary to stdout.

Usage:
  python3 tools/eval_real_cer.py [--tessdata <path>] [--psm 6]
"""

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

EVAL_DIR = Path(__file__).resolve().parents[1] / 'real_gt' / 'eval'
OUT_DIR = Path(__file__).resolve().parents[1] / 'output'


def run(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def cer(ref: str, hyp: str) -> float:
    # Simple character-level Levenshtein CER (pure Python, no numpy)
    r = list(ref)
    h = list(hyp)
    R, H = len(r), len(h)
    # initialize 2 rows to save memory
    prev = list(range(H + 1))
    curr = [0] * (H + 1)
    for i in range(1, R + 1):
        curr[0] = i
        for j in range(1, H + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            curr[j] = min(
                prev[j] + 1,       # deletion
                curr[j - 1] + 1,   # insertion
                prev[j - 1] + cost # substitution
            )
        prev, curr = curr, prev
    edits = prev[H]
    denom = max(R, 1)
    return edits / denom


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tessdata', default=None, help='Path to tessdata dir containing ckb.traineddata (auto if omitted)')
    ap.add_argument('--psm', default='6', help='PSM mode (default: 6)')
    args = ap.parse_args()

    eval_dir = EVAL_DIR
    if not eval_dir.exists():
        print(f"Eval dir missing: {eval_dir}")
        return 2

    # Choose tessdata dir (prefer repo tessdata/best, then tessdata/fast, then tessdata)
    repo_root = Path(__file__).resolve().parents[2]
    tessdata = args.tessdata
    cand = [
        repo_root / 'tessdata' / 'best',
        repo_root / 'tessdata' / 'fast',
        repo_root / 'tessdata',
    ]
    if tessdata is None:
        for c in cand:
            if (c / 'ckb.traineddata').exists():
                tessdata = str(c)
                break
    if tessdata is None:
        print('ckb.traineddata not found in tessdata/best, tessdata/fast, or tessdata. Train first.')
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / 'real_metrics.csv'

    # Gather images
    exts = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
    imgs = sorted([p for p in eval_dir.glob('*') if p.suffix.lower() in exts])
    if not imgs:
        print(f"No eval images found under {eval_dir}")
        return 2

    rows = []
    total_edits = 0
    total_chars = 0

    for img in imgs:
        base = img.with_suffix('').name
        gt_txt = img.with_suffix('').parent / f"{base}.gt.txt"
        if not gt_txt.exists():
            print(f"Skipping {img.name}: missing {gt_txt.name}")
            continue
        ref = gt_txt.read_text(encoding='utf-8', errors='ignore')

        code, out = run(['tesseract', str(img), 'stdout', '-l', 'ckb', '--psm', args.psm, '--tessdata-dir', tessdata])
        hyp = out
        c = cer(ref, hyp)
        rows.append((img.name, len(ref), c))
        # accumulate Levenshtein ops indirectly using c*len(ref)
        total_edits += int(round(c * max(len(ref), 1)))
        total_chars += max(len(ref), 1)

    if not rows:
        print('No paired image/gt found.')
        return 2

    avg_cer = total_edits / max(total_chars, 1)

    # Write CSV
    with csv_path.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if f.tell() == 0:
            w.writerow(['image', 'ref_chars', 'cer'])
        for name, nref, c in rows:
            w.writerow([name, nref, f"{c:.4f}"])
        w.writerow(['__AVG__', total_chars, f"{avg_cer:.4f}"])

    print('\nReal-world CER results')
    print('======================')
    for name, nref, c in rows[:10]:  # print a few
        print(f"{name:30s}  CER={c:.4f}  (chars={nref})")
    print(f"\nAverage CER over {len(rows)} samples: {avg_cer:.4f}")
    print(f"CSV -> {csv_path}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
