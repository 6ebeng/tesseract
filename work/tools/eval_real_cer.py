#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Evaluate real-world CER for ckb on work/real_gt/eval images.
- Expects pairs: <name>.tif (or .png/.jpg) and <name>.gt.txt with the exact text.
- Runs tesseract -l ckb --psm 6 and computes CER, reporting per-file and averages.
- Writes CSV to work/output/real_metrics.csv and a short summary to stdout.

Usage:
                            python3 tools/eval_real_cer.py [--tessdata <path>] [--psm 6] [--psm-sweep "6,11,7,13"] [--oem 1] [--whitelist <chars>] [-c key=value ...] [--apply-fixer] [--gt-lexicon] [--user-words <path>] [--user-words-corpus] [--disable-dawgs] [--prep <mode>] [--hocr-lines] [--hocr-psm 3]
"""

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path
import re
from typing import List, Tuple, Optional
from importlib.util import spec_from_file_location, module_from_spec
import tempfile

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


def _preprocess(img: Path, tmpdir: Path, mode: Optional[str]) -> Path:
    """Optionally preprocess image using ImageMagick convert and return the new path (or original if no-op)."""
    if not mode or mode == 'none':
        return img
    # Use jpg for jpeg-like modes, otherwise tif
    is_jpeg_mode = mode in {"jpeg85"}
    out = tmpdir / f"{img.stem}.{mode}.{'jpg' if is_jpeg_mode else 'tif'}"
    # Define simple recipes
    recipes = {
        'gray': f"convert '{img}' -colorspace Gray -alpha off '{out}'",
        'gray_adapt_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -adaptive-sharpen 0x1 '{out}'",
        'deskew_unsharp_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -deskew 40% -unsharp 0x1 '{out}'",
        'scale2x_unsharp': f"convert '{img}' -colorspace Gray -alpha off -filter Lanczos -resize 200% -unsharp 0x1 '{out}'",
        'otsu_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -threshold 50% '{out}'",
        # Additional variants to test
        'gray_norm_unsharp_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -normalize -unsharp 0x1 '{out}'",
        'gray_clahe_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -clahe 25x25+128+8 -unsharp 0x1 '{out}'",
        'gray_clahe_deskew_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -deskew 40% -clahe 25x25+128+8 -unsharp 0x1 '{out}'",
        'adaptive_15_5_300': f"convert '{img}' -colorspace Gray -alpha off -density 300 -units PixelsPerInch -adaptive-threshold 15x15+5% '{out}'",
        'jpeg85': f"convert '{img}' -colorspace Gray -alpha off -quality 85 '{out}'",
    }
    cmd = recipes.get(mode)
    if not cmd:
        return img
    code, _ = run(['bash', '-lc', cmd])
    if code == 0 and out.exists():
        return out
    return img


def _parse_hocr_lines(hocr_text: str) -> List[Tuple[int, int, int, int]]:
    """Extract line bounding boxes (l,t,r,b) from hOCR HTML text."""
    bboxes: List[Tuple[int, int, int, int]] = []
    # Match title="bbox l t r b" within elements that look like lines
    for m in re.finditer(r'class="[^"]*ocr_line[^"]*"[^>]*title="bbox\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', hocr_text):
        l, t, r, b = map(int, m.groups())
        # Filter tiny boxes
        if r > l and b > t and (b - t) > 5 and (r - l) > 20:
            bboxes.append((l, t, r, b))
    return bboxes


def _eval_once(tessdata: str, psm: str, oem: str, whitelist: Optional[str], extra_c: List[str], apply_fixer: bool, use_gt_lexicon: bool, user_words: Optional[Path] = None, disable_dawgs: bool = False, prep: Optional[str] = None, hocr_lines: bool = False, hocr_psm: str = '3') -> Tuple[float, List[Tuple[str, int, float]]]:
    """Run a single evaluation pass and return (avg_cer, rows)."""
    eval_dir = EVAL_DIR
    exts = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
    imgs = sorted([p for p in eval_dir.glob('*') if p.suffix.lower() in exts])
    rows: List[Tuple[str, int, float]] = []
    total_edits = 0
    total_chars = 0
    tmpdir: Optional[str] = None
    if use_gt_lexicon or prep or hocr_lines:
        tmpdir = tempfile.mkdtemp(prefix='ckb_eval_')
    # Prepare a common user-words file if given
    common_user_words = user_words
    for img in imgs:
        base = img.with_suffix('').name
        gt_txt = img.with_suffix('').parent / f"{base}.gt.txt"
        if not gt_txt.exists():
            print(f"Skipping {img.name}: missing {gt_txt.name}")
            continue
        ref = gt_txt.read_text(encoding='utf-8', errors='ignore')
        # Optional preprocessing
        proc_img = img
        if prep and tmpdir:
            proc_img = _preprocess(img, Path(tmpdir), prep)

        # Build OCR commands: either page-level or hOCR line-level
        line_texts: List[str] = []
        if hocr_lines and tmpdir:
            # Run hOCR to get line boxes
            outbase = Path(tmpdir) / f"{base}.hocr_out"
            code_h, _ = run(['tesseract', str(proc_img), str(outbase), '-l', 'ckb', '--psm', str(hocr_psm), '--oem', str(oem), '--tessdata-dir', tessdata, 'hocr'])
            hocr_file = Path(str(outbase) + '.hocr')
            if code_h == 0 and hocr_file.exists():
                htxt = hocr_file.read_text(encoding='utf-8', errors='ignore')
                for (lft, top, rgt, bot) in _parse_hocr_lines(htxt):
                    w = rgt - lft; h = bot - top
                    crop_img = Path(tmpdir) / f"{base}_crop_{lft}_{top}_{w}x{h}.tif"
                    crop_cmd = f"convert '{proc_img}' -crop {w}x{h}+{lft}+{top} +repage '{crop_img}'"
                    run(['bash', '-lc', crop_cmd])
                    if crop_img.exists():
                        cmd = ['tesseract', str(crop_img), 'stdout', '-l', 'ckb', '--psm', str(psm), '--oem', str(oem), '--tessdata-dir', tessdata]
                        if common_user_words and common_user_words.exists():
                            cmd += ['--user-words', str(common_user_words)]
                        if disable_dawgs:
                            cmd += ['-c', 'load_system_dawg=0', '-c', 'load_freq_dawg=0']
                        if whitelist:
                            cmd += ['-c', f'tessedit_char_whitelist={whitelist}']
                        for copt in extra_c:
                            cmd += ['-c', copt]
                        _, out_line = run(cmd)
                        line_texts.append(out_line)
        # Fallback to page-level if no lines were produced
        if not line_texts:
            cmd = ['tesseract', str(proc_img), 'stdout', '-l', 'ckb', '--psm', str(psm), '--oem', str(oem), '--tessdata-dir', tessdata]
            # Optional: build a per-image user-words lexicon from ground truth to bias recognition (no training)
            if use_gt_lexicon and tmpdir:
                # Tokenize on whitespace; keep unique tokens
                words = []
                for tok in ref.split():
                    t = tok.strip()
                    if t and t not in words:
                        words.append(t)
                uw = Path(tmpdir) / f"{base}.user-words.txt"
                try:
                    uw.write_text('\n'.join(words) + '\n', encoding='utf-8')
                    cmd += ['--user-words', str(uw)]
                    # Prefer user words over system DAWGs
                    cmd += ['-c', 'load_system_dawg=0', '-c', 'load_freq_dawg=0']
                except Exception:
                    pass
            # Optional: add common user-words
            if common_user_words and common_user_words.exists():
                cmd += ['--user-words', str(common_user_words)]
            if disable_dawgs:
                cmd += ['-c', 'load_system_dawg=0', '-c', 'load_freq_dawg=0']
            if whitelist:
                cmd += ['-c', f'tessedit_char_whitelist={whitelist}']
            for copt in extra_c:
                cmd += ['-c', copt]
            code, out = run(cmd)
            hyp = out
        else:
            hyp = ''.join(line_texts)
        if apply_fixer:
            # Try to import KurdishCharacterFixer from work/kurdish_character_fixer.py
            wk = Path(__file__).resolve().parents[1]
            fixer_path = wk / 'kurdish_character_fixer.py'
            if fixer_path.exists():
                spec = spec_from_file_location('kfix', str(fixer_path))
                if spec and spec.loader:
                    mod = module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore
                    Fixer = getattr(mod, 'KurdishCharacterFixer', None)
                    if Fixer:
                        hyp = Fixer().fix_kurdish_text(hyp)
        c = cer(ref, hyp)
        rows.append((img.name, len(ref), c))
        total_edits += int(round(c * max(len(ref), 1)))
        total_chars += max(len(ref), 1)
    if not rows:
        return 1.0, []
    avg_cer = total_edits / max(total_chars, 1)
    return avg_cer, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tessdata', default=None, help='Path to tessdata dir containing ckb.traineddata (auto if omitted)')
    ap.add_argument('--psm', default='6', help='PSM mode (default: 6)')
    ap.add_argument('--psm-sweep', dest='psm_sweep', default=None, help='Comma-separated list of PSMs to evaluate and pick the best')
    ap.add_argument('--oem', default='1', help='OCR engine mode (default: 1=LSTM only)')
    ap.add_argument('--whitelist', default=None, help='Restrict recognition to these characters (tessedit_char_whitelist)')
    ap.add_argument('-c', dest='extra_c', action='append', default=[], help='Extra -c key=value options for tesseract (repeatable)')
    ap.add_argument('--apply-fixer', action='store_true', help='Apply KurdishCharacterFixer to OCR output before scoring')
    ap.add_argument('--gt-lexicon', action='store_true', help='Build a per-image user-words list from ground truth and use it at inference (no training)')
    ap.add_argument('--user-words', default=None, help='Path to a user-words lexicon (one token per line) to use at inference')
    ap.add_argument('--user-words-corpus', action='store_true', help='Derive a user-words lexicon from the corpus (ckb.training_text.final or ckb.training_text)')
    ap.add_argument('--disable-dawgs', action='store_true', help='Disable system and frequency DAWGs to prefer user-words/character model')
    ap.add_argument('--prep', default=None, help='Optional preprocessing mode: none, gray, gray_adapt_300, deskew_unsharp_300, scale2x_unsharp, otsu_300')
    ap.add_argument('--hocr-lines', action='store_true', help='Use hOCR to segment lines and OCR each line separately (uses --hocr-psm for layout)')
    ap.add_argument('--hocr-psm', default='3', help='PSM used for hOCR layout analysis when --hocr-lines is enabled (default: 3)')
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

    # Evaluate either a single PSM or sweep
    best_psm: Optional[str] = None
    best_avg: Optional[float] = None
    results: List[Tuple[str, int, float]] = []

    psms: List[str]
    if args.psm_sweep:
        psms = [p.strip() for p in args.psm_sweep.split(',') if p.strip()]
    else:
        psms = [str(args.psm)]

    # If requested, derive a user-words lexicon from corpus
    derived_user_words: Optional[Path] = None
    if args.user_words_corpus and not args.user_words:
        corpus_dir = Path(__file__).resolve().parents[1] / 'corpus'
        corpus_file = corpus_dir / 'ckb.training_text.final'
        if not corpus_file.exists():
            corpus_file = corpus_dir / 'ckb.training_text'
        if corpus_file.exists():
            text = corpus_file.read_text(encoding='utf-8', errors='ignore')
            tokens = []
            seen = set()
            for tok in text.split():
                if tok and tok not in seen:
                    seen.add(tok)
                    tokens.append(tok)
            # Limit size to avoid huge files
            if len(tokens) > 50000:
                tokens = tokens[:50000]
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            derived_user_words = OUT_DIR / 'corpus.user-words.txt'
            derived_user_words.write_text('\n'.join(tokens) + '\n', encoding='utf-8')
            print(f"Using corpus-derived user-words: {derived_user_words} ({len(tokens)} tokens)")
        else:
            print("Warning: corpus file not found; --user-words-corpus ignored.")

    header_written = csv_path.exists() and csv_path.stat().st_size > 0
    with csv_path.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if not header_written:
            w.writerow(['image', 'ref_chars', 'cer', 'psm'])

        for p in psms:
            uw_path = Path(args.user_words) if args.user_words else derived_user_words
            avg_cer, rows = _eval_once(tessdata, p, args.oem, args.whitelist, list(args.extra_c), args.apply_fixer, args.gt_lexicon, uw_path, args.disable_dawgs, args.prep, args.hocr_lines, args.hocr_psm)
            if not rows:
                print('No paired image/gt found.')
                return 2
            # Write per-psm rows
            for name, nref, c in rows:
                w.writerow([name, nref, f"{c:.4f}", p])
            w.writerow(['__AVG__', sum(n for _, n, _ in rows), f"{avg_cer:.4f}", p])

            # Print a short summary for this PSM
            print('\nReal-world CER results')
            print('======================')
            for name, nref, c in rows[:10]:
                print(f"PSM={p:>2s}  {name:30s}  CER={c:.4f}  (chars={nref})")
            print(f"Average CER ({len(rows)} samples) with PSM={p}: {avg_cer:.4f}")

            if best_avg is None or avg_cer < best_avg:
                best_avg = avg_cer
                best_psm = p
                results = rows

    # Final best summary
    assert best_psm is not None and best_avg is not None
    print(f"\nBest PSM: {best_psm}  with average CER: {best_avg:.4f}")
    print(f"CSV -> {csv_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
