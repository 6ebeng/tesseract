#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verify ckb.traineddata unicharset covers Kurdish Arabic-based characters
========================================================================
Unpacks a traineddata using `combine_tessdata -u`, parses the resulting
`.unicharset`, and verifies that the required Kurdish Arabic letters and
Arabic-Indic digits are present.

Exit codes:
  0: All required characters are present
  1: Usage or environment error (missing tools/files)
  2: Verification failed (missing characters)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Optional, Set

# Required Kurdish Arabic-based letters (Sorani)
REQUIRED_KURDISH_ARABIC_LETTERS = [
    'ئ', 'ا', 'ب', 'پ', 'ت', 'ج', 'چ', 'ح', 'خ', 'د', 'ر', 'ڕ', 'ز', 'ژ',
    'س', 'ش', 'ع', 'غ', 'ف', 'ڤ', 'ق', 'ک', 'گ', 'ل', 'ڵ', 'م', 'ن', 'ه',
    'ە', 'و', 'ۆ', 'ی', 'ێ'
]

# Arabic-Indic digits
REQUIRED_ARABIC_INDIC_DIGITS = list('٠١٢٣٤٥٦٧٨٩')


def run(cmd: list, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def find_unicharset(unpack_dir: str, base_name: str) -> Optional[str]:
    """Return path to the extracted unicharset file if found (supports Tesseract 5 lstm-unicharset)."""
    candidates = [
        os.path.join(unpack_dir, f"{base_name}.unicharset"),
        os.path.join(unpack_dir, f"{base_name}.lstm-unicharset"),
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    # Fallback: scan directory for any file that ends with 'unicharset'
    for f in os.listdir(unpack_dir):
        if f.endswith('unicharset'):
            return os.path.join(unpack_dir, f)
    return None


def parse_unicharset(unicharset_path: str) -> Set[str]:
    """Parse Tesseract unicharset file into a set of characters."""
    chars: Set[str] = set()
    with open(unicharset_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if not line:
                continue
            # First line may be a count integer
            if i == 0 and line.isdigit():
                continue
            token = line.split(' ', 1)[0]
            if token and token.upper() != 'NULL':
                if token.strip():
                    chars.add(token)
    return chars


def main() -> int:
    ap = argparse.ArgumentParser(description='Verify ckb.traineddata unicharset covers Kurdish Arabic-based characters and digits')
    ap.add_argument('--traineddata', '-t', default=None, help='Path to ckb.traineddata (default: auto-detect common locations)')
    ap.add_argument('--out', default=os.path.join('output', 'verify_report.json'), help='Path to write JSON report')
    ap.add_argument('--include-digits', action='store_true', default=True, help='Also verify Arabic-Indic digits (default: true)')
    args = ap.parse_args()

    # Resolve traineddata path
    candidates: list[str] = []
    if args.traineddata:
        candidates.append(args.traineddata)
    candidates.extend([
        os.path.join('..', 'tessdata', 'ckb.traineddata'),
        os.path.join('hybrid_build', 'ckb.traineddata'),
        os.path.join('..', 'work', 'hybrid_build', 'ckb.traineddata'),
    ])

    traineddata_path: Optional[str] = None
    for c in candidates:
        if c and os.path.isfile(c):
            traineddata_path = c
            break

    if not traineddata_path:
        print('Error: ckb.traineddata not found. Provide with --traineddata or place in tessdata/ or work/hybrid_build/.', file=sys.stderr)
        return 1

    # Ensure combine_tessdata is available
    test = run(['combine_tessdata', '-v'])
    if test.returncode != 0:
        print('Error: combine_tessdata is not available in PATH. Install tesseract training tools.', file=sys.stderr)
        return 1

    # Prepare temp unpack dir
    tmp_root = os.path.join('tmp', 'verify_unicharset')
    os.makedirs(tmp_root, exist_ok=True)
    unpack_dir = tempfile.mkdtemp(prefix='ckb_', dir=tmp_root)
    base_name = os.path.splitext(os.path.basename(traineddata_path))[0]

    # Copy traineddata into unpack_dir
    local_trained = os.path.join(unpack_dir, os.path.basename(traineddata_path))
    shutil.copy2(traineddata_path, local_trained)

    print(f"Unpacking: {traineddata_path}")
    out_prefix = os.path.join(unpack_dir, base_name + '.')
    out = run(['combine_tessdata', '-u', local_trained, out_prefix])
    if out.returncode != 0:
        print(out.stdout)
        print('Error: combine_tessdata -u failed.', file=sys.stderr)
        return 1

    unicharset_path = find_unicharset(unpack_dir, base_name)
    if not unicharset_path:
        print(out.stdout)
        print(f"Error: .unicharset not found after unpacking in {unpack_dir}", file=sys.stderr)
        return 1

    present = parse_unicharset(unicharset_path)

    required = set(REQUIRED_KURDISH_ARABIC_LETTERS)
    if args.include_digits:
        required.update(REQUIRED_ARABIC_INDIC_DIGITS)

    missing = sorted(ch for ch in required if ch not in present)

    def cp(ch: str) -> str:
        return "U+%04X" % ord(ch)

    print('\nVerification Summary')
    print('====================')
    print(f"Total present in model: {len(present)}")
    print(f"Required Kurdish chars: {len(REQUIRED_KURDISH_ARABIC_LETTERS)}")
    print(f"Required digits:        {len(REQUIRED_ARABIC_INDIC_DIGITS)} (included={args.include_digits})")

    if missing:
        print(f"\nMissing required characters ({len(missing)}):")
        print('  ' + ' '.join(f"{c}({cp(c)})" for c in missing))
    else:
        print('\nAll required Kurdish Arabic-based letters and digits are present. ✅')

    # Write JSON report
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    report = {
        'traineddata': os.path.abspath(traineddata_path),
        'unicharset': unicharset_path,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'present_count': len(present),
        'required_letters': REQUIRED_KURDISH_ARABIC_LETTERS,
        'required_digits': REQUIRED_ARABIC_INDIC_DIGITS if args.include_digits else [],
        'missing': missing,
        'ok': len(missing) == 0,
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nJSON report written to: {args.out}")

    return 0 if not missing else 2


if __name__ == '__main__':
    sys.exit(main())
