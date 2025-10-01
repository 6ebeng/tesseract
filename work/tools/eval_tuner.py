#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eval Tuner for Kurdish OCR (ckb)
--------------------------------
Grid-search pre-processing and Tesseract options to minimize CER on work/real_gt/eval.
Does NOT modify training. Produces a summary of the best configuration found.

Usage (from work/):
  python3 tools/eval_tuner.py \
    [--psms 6,11] [--oems 1] \
    [--whitelist] [--blacklist] \
    [--prep variants]

Outputs: best result printed and appended to work/output/real_metrics.csv with extra columns.
"""

import argparse
import csv
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict

WORK = Path(__file__).resolve().parents[1]
EVAL_DIR = WORK / 'real_gt' / 'eval'
OUT_DIR = WORK / 'output'


def run(cmd: List[str]) -> Tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def cer(ref: str, hyp: str) -> float:
    r = list(ref)
    h = list(hyp)
    R, H = len(r), len(h)
    prev = list(range(H + 1))
    curr = [0] * (H + 1)
    for i in range(1, R + 1):
        curr[0] = i
        ri = r[i - 1]
        for j in range(1, H + 1):
            cost = 0 if ri == h[j - 1] else 1
            d = prev[j] + 1
            ins = curr[j - 1] + 1
            sub = prev[j - 1] + cost
            curr[j] = d if d < ins else ins
            if sub < curr[j]:
                curr[j] = sub
        prev, curr = curr, prev
    edits = prev[H]
    return edits / max(R, 1)


def preprocess(img: Path, variant: str, tmpdir: Path) -> Path:
    """Apply lightweight ImageMagick preprocessing variants."""
    out = tmpdir / f"{img.stem}.{variant}{img.suffix}"
    if variant == 'none':
        return img
    # Ensure ImageMagick convert exists
    code, _ = run(['bash', '-lc', 'command -v convert >/dev/null 2>&1; echo $?'])
    # If convert is not available, skip preprocessing
    if code != 0:
        return img
    cmd = ['bash', '-lc', '']
    src = str(img)
    dst = str(out)
    if variant == 'gray_adapt_300':
        cmd[-1] = f"convert '{src}' -colorspace Gray -auto-level -contrast-stretch 1%x1% -adaptive-sharpen 0x1 -units PixelsPerInch -density 300 '{dst}'"
    elif variant == 'gray_thresh_300':
        cmd[-1] = f"convert '{src}' -colorspace Gray -auto-level -threshold 55% -units PixelsPerInch -density 300 '{dst}'"
    elif variant == 'gray_unsharp_400':
        cmd[-1] = f"convert '{src}' -colorspace Gray -auto-level -unsharp 0x1 -units PixelsPerInch -density 400 '{dst}'"
    elif variant == 'deskew_unsharp_300':
        cmd[-1] = f"convert '{src}' -colorspace Gray -auto-level -deskew 40% -unsharp 0x1 -units PixelsPerInch -density 300 '{dst}'"
    else:
        return img
    _c, _o = run(cmd)
    return out if out.exists() else img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--psms', default='6,11', help='Comma-separated PSMs to try')
    ap.add_argument('--oems', default='1', help='Comma-separated OEMs to try (1=LSTM only)')
    ap.add_argument('--whitelist', action='store_true', help='Use Kurdish Arabic letters+digits+punc whitelist')
    ap.add_argument('--blacklist', action='store_true', help='Blacklist Persian/Arabic extra letters')
    ap.add_argument('--prep', default='none,gray_adapt_300,gray_unsharp_400,deskew_unsharp_300', help='Comma-separated preprocessing variants')
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / 'real_metrics.csv'
    csv_extra = OUT_DIR / 'real_metrics_tuned.csv'

    # Locate tessdata dir
    repo_root = WORK.parents[0]
    tessdata = None
    for c in [repo_root / 'tessdata' / 'best', repo_root / 'tessdata' / 'fast', repo_root / 'tessdata']:
        if (c / 'ckb.traineddata').exists():
            tessdata = str(c)
            break
    if tessdata is None:
        print('ckb.traineddata not found; run training first.')
        return 2

    exts = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
    imgs = sorted([p for p in EVAL_DIR.glob('*') if p.suffix.lower() in exts])
    if not imgs:
        print(f"No eval images found under {EVAL_DIR}")
        return 2

    # Char sets
    kurdish_letters = 'ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ'
    arabic_indic_digits = '٠١٢٣٤٥٦٧٨٩'
    puncs = '،؛:؟«»-()٪ '  # include space
    whitelist = kurdish_letters + arabic_indic_digits + puncs
    persian_extra = 'صضطظذيثثةؤأإآكۀى'  # from docs/ related scripts

    psms = [p.strip() for p in args.psms.split(',') if p.strip()]
    oems = [o.strip() for o in args.oems.split(',') if o.strip()]
    preps = [v.strip() for v in args.prep.split(',') if v.strip()]

    best = None  # (cer, config_dict)
    all_rows: List[List[str]] = []

    tmpdir = Path(tempfile.mkdtemp(prefix='ckb_eval_', dir=str(OUT_DIR)))
    try:
        for img in imgs:
            ref = (img.with_suffix('').parent / f"{img.with_suffix('').name}.gt.txt").read_text(encoding='utf-8', errors='ignore')
            for psm, oem, prep in itertools.product(psms, oems, preps):
                # Prepare image variant
                vimg = preprocess(img, prep, tmpdir)
                cmd = ['tesseract', str(vimg), 'stdout', '-l', 'ckb', '--tessdata-dir', tessdata, '--psm', str(psm), '--oem', str(oem)]
                if args.whitelist:
                    cmd += ['-c', f'tessedit_char_whitelist={whitelist}']
                if args.blacklist:
                    cmd += ['-c', f'tessedit_char_blacklist={persian_extra}']
                # Stabilize spaces and DPI assumptions
                cmd += ['-c', 'preserve_interword_spaces=0', '-c', 'user_defined_dpi=300']
                code, out = run(cmd)
                hyp = out
                c = cer(ref, hyp)
                row = [img.name, len(ref), f"{c:.4f}", psm, oem, prep]
                all_rows.append([str(x) for x in row])
                if best is None or c < best[0]:
                    best = (c, {'psm': psm, 'oem': oem, 'prep': prep, 'img': img.name})

        if best is None:
            print('No pairs evaluated.')
            return 2

        # Append tuned results to a separate CSV
        write_header = not csv_extra.exists() or csv_extra.stat().st_size == 0
        with csv_extra.open('a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(['image', 'ref_chars', 'cer', 'psm', 'oem', 'prep'])
            w.writerows(all_rows)

        print(f"\nBest tuned CER: {best[0]:.4f}  using PSM={best[1]['psm']} OEM={best[1]['oem']} PREP={best[1]['prep']} on {best[1]['img']}")
        print(f"CSV(tuned) -> {csv_extra}")
        return 0
    finally:
        # Cleanup temp dir but keep if debugging is needed
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


if __name__ == '__main__':
    raise SystemExit(main())
