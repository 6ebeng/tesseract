#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build a balanced Kurdish Sorani corpus with advanced quality filtering:
- Scans work/corpus/*.txt (excluding *final*), normalizes (NFC) and optionally applies fixer.
- ZWNJ-aware: Prioritizes sentences with optimal ZWNJ density (6-10%) for Kurdish OCR quality.
- Quality filtering: Sentence length, character set purity, ZWNJ pattern validation.
- Writes work/corpus/ckb.training_text.final and stats to work/output/.

Usage (from work/):
  python3 tools/corpus_build.py [--min-count 1000] [--fixer] [--min-zwnj 3.0] [--target-zwnj 8.0]
                                [--min-length 10] [--max-length 200] [--max-non-kurdish 30]

Notes:
- --min-count: Minimum character occurrences for target Kurdish letters.
- --min-zwnj: Filter sentences with ZWNJ% below threshold (0=no filter).
- --target-zwnj: Oversample high-ZWNJ sentences to reach target density (0=no target).
- --min-length: Minimum sentence length in characters (default: 10).
- --max-length: Maximum sentence length in characters (default: 500).
- --max-non-kurdish: Max percentage of non-Kurdish chars allowed (default: 30%).
- --validate-zwnj-patterns: Enable ZWNJ pattern validation (experimental).
- If --fixer is set and kurdish_character_fixer.py is present, apply it first.
"""

import argparse
import os
import re
import unicodedata as ud
from collections import Counter, defaultdict
from pathlib import Path
import sys

WORK = Path(__file__).resolve().parents[1]
CORPUS_DIR = WORK / 'corpus'
OUT_DIR = WORK / 'output'
TARGET_FINAL = CORPUS_DIR / 'ckb.training_text.final'
FIXER_PATH = WORK / 'kurdish_character_fixer.py'

# Target Kurdish Arabic-based letters (Central Kurdish/Sorani standard)
TARGET_CHARS = set("\u0626\u0627\u0628\u067e\u062a\u062c\u0686\u062d\u062e\u062f\u0631\u0695\u0632\u0698\u0633\u0634\u0639\u063a\u0641\u06a4\u0642\u06a9\u06af\u0644\u06b5\u0645\u0646\u0647\u06d5\u0648\u06c6\u06cc\u06ce")
# ئ ء ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن و ۆ ه ە ی ێ

# Other Kurdish dialect characters (Southern, Hewrami)
DIALECT_CHARS = set("\u06CA\u0769\u068E\u06C9")  # ۊ ݩ ڎ ۉ

# Extended Kurdish character set (includes all Kurdish dialects, punctuation, digits)
KURDISH_EXTENDED = TARGET_CHARS | DIALECT_CHARS | set("،؛؟ـ/٠١٢٣٤٥٦٧٨٩0123456789٫٬%÷× \t\n.,;:!?-()[]{}\"'«»<>")

# ZWNJ (Zero-Width Non-Joiner) - Critical for Kurdish OCR quality
ZWNJ = '\u200C'

# Common Arabic/Persian characters (for loanwords - acceptable in Kurdish text)
# Includes: آ أ إ ث ذ ص ض ط ظ ك ؤ ة ي ى and common diacritics
ARABIC_CHARS = set("\u0622\u0623\u0625\u062B\u0630\u0635\u0636\u0637\u0638\u0643\u0624\u0629\u064A\u0649")  # Letters
ARABIC_DIACRITICS = set("\u064E\u0650\u064F\u0651\u0652\u064B\u064D\u064C\u0640")  # Diacritics: ـَـِـُـّـْ ـًـٍـٌ ـ

RE_SPACES = re.compile(r"\s+")

# ZWNJ pattern validation (common Kurdish contexts)
ZWNJ_PATTERNS = [
    # Compound words: word + ZWNJ + word
    re.compile(r'[\u0600-\u06FF]+\u200C[\u0600-\u06FF]+'),
    # Verb forms with ZWNJ
    re.compile(r'(دە|بە|ئێ|دا|نا)\u200C'),  # Prefixes with ZWNJ
]


def nfc(s: str) -> str:
    try:
        return ud.normalize('NFC', s)
    except Exception:
        return s


def apply_fixer(text: str, preserve_arabic: bool = True, preserve_latin_digits: bool = False, strip_zwnj: bool = False) -> str:
    # Import fixer dynamically if present
    import importlib.util
    spec = importlib.util.spec_from_file_location('kfix', str(FIXER_PATH))
    if spec and spec.loader:
        kfix = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kfix)
        fixer = getattr(kfix, 'KurdishCharacterFixer', None)
        if fixer:
            return fixer(preserve_arabic_words=preserve_arabic, 
                        preserve_latin_digits=preserve_latin_digits,
                        strip_zwnj=strip_zwnj).fix_kurdish_text(text)
    return text


def line_contains_targets(line: str) -> set:
    return set(ch for ch in line if ch in TARGET_CHARS)


def calculate_zwnj_density(text: str) -> float:
    """Calculate ZWNJ density as percentage of total characters."""
    if not text:
        return 0.0
    zwnj_count = text.count(ZWNJ)
    return (zwnj_count / len(text)) * 100.0


def calculate_kurdish_purity(text: str) -> float:
    """Calculate percentage of characters that are Kurdish/acceptable."""
    if not text:
        return 0.0
    
    # Count Kurdish + dialect + Arabic loanword chars + diacritics + extended chars
    acceptable_chars = sum(1 for c in text if c in KURDISH_EXTENDED or c in ARABIC_CHARS or c in ARABIC_DIACRITICS)
    total_chars = len(text)
    
    return (acceptable_chars / total_chars) * 100.0


def validate_zwnj_patterns(text: str) -> bool:
    """
    Validate that ZWNJ appears in proper Kurdish contexts.
    Returns True if ZWNJ usage looks correct or if no ZWNJ present.
    """
    if ZWNJ not in text:
        return True  # No ZWNJ is fine
    
    # Check if ZWNJ appears in recognized patterns
    for pattern in ZWNJ_PATTERNS:
        if pattern.search(text):
            return True
    
    # If ZWNJ exists but no patterns match, might be random/incorrect
    # But don't be too strict - return True if density is reasonable
    zwnj_density = calculate_zwnj_density(text)
    return zwnj_density <= 15.0  # Reject if >15% (likely corrupted)


def calculate_length_score(length: int, optimal_min: int = 30, optimal_max: int = 150) -> float:
    """
    Score sentence based on length.
    Optimal range: 30-150 chars (good for OCR training).
    """
    if optimal_min <= length <= optimal_max:
        return 10.0  # Perfect length
    elif length < optimal_min:
        # Too short - penalize more
        return max(0.0, (length / optimal_min) * 5.0)
    else:
        # Too long - gentle penalty
        excess = length - optimal_max
        penalty = min(5.0, excess / 50.0)
        return max(5.0, 10.0 - penalty)


def zwnj_quality_score(density: float, target: float = 8.0) -> float:
    """
    Score a sentence based on ZWNJ density.
    Higher score for densities near target (6-10% optimal for Kurdish).
    """
    if 6.0 <= density <= 10.0:
        # Optimal range - highest score
        return 10.0 - abs(density - target)
    elif density >= 3.0:
        # Acceptable but not optimal
        return 5.0 - abs(density - target) * 0.5
    else:
        # Low ZWNJ - lower score
        return max(0.0, density)


def calculate_overall_quality(text: str, target_zwnj: float = 8.0, 
                              validate_patterns: bool = False) -> float:
    """
    Calculate overall quality score combining multiple factors.
    Returns score 0-10 (higher is better).
    
    Note: ZWNJ scoring removed - we now use proper ە (AE) instead of ه+ZWNJ.
    ZWNJ was a workaround that hurt Kurdish Sorani; now we have the proper letter.
    """
    kurdish_purity = calculate_kurdish_purity(text)
    length = len(text)
    
    # Component scores (ZWNJ removed from scoring)
    length_score = calculate_length_score(length)
    purity_score = (kurdish_purity / 100.0) * 10.0  # Convert to 0-10
    
    # Weighted combination (redistributed weights without ZWNJ)
    overall = (
        length_score * 0.50 +     # Sentence length (increased weight)
        purity_score * 0.50       # Character set purity (increased weight)
    )
    
    return overall


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-count', type=int, default=2000,
                    help='Desired minimum total count for each target char (soft target)')
    ap.add_argument('--fixer', action='store_true', help='Apply kurdish_character_fixer.py if present')
    ap.add_argument('--strip-zwnj', action='store_true',
                    help='Remove all ZWNJ after ه‌→ە conversion (default: preserve ZWNJ)')
    ap.add_argument('--no-preserve-arabic', action='store_true', 
                    help='Convert all Arabic chars to Kurdish phonetics (default: preserve Arabic words)')
    ap.add_argument('--preserve-latin-digits', action='store_true',
                    help='Keep Latin digits (0-9) unchanged (default: convert to Arabic-Indic)')
    ap.add_argument('--min-zwnj', type=float, default=0.0,
                    help='Minimum ZWNJ density %% for accepting sentences (0=no filter)')
    ap.add_argument('--target-zwnj', type=float, default=0.0,
                    help='Target ZWNJ density %% to achieve through oversampling (0=no target)')
    ap.add_argument('--min-length', type=int, default=10,
                    help='Minimum sentence length in characters (default: 10)')
    ap.add_argument('--max-length', type=int, default=500,
                    help='Maximum sentence length in characters (default: 500)')
    ap.add_argument('--max-non-kurdish', type=float, default=30.0,
                    help='Maximum percentage of non-Kurdish characters allowed (default: 30%%)')
    ap.add_argument('--validate-zwnj-patterns', action='store_true',
                    help='Enable ZWNJ pattern validation (experimental)')
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
            txt = apply_fixer(txt, 
                            preserve_arabic=not args.no_preserve_arabic,
                            preserve_latin_digits=args.preserve_latin_digits,
                            strip_zwnj=args.strip_zwnj)
        txt = nfc(txt)
        # Normalize whitespace to single spaces and split into lines
        for L in txt.splitlines():
            L = RE_SPACES.sub(' ', L.strip())
            if L:
                lines.append(L)

    # Quality filtering and deduplication
    seen = {}  # line -> quality_score
    deduped = []
    filtered_by_zwnj = 0
    filtered_by_length = 0
    filtered_by_charset = 0
    filtered_by_pattern = 0
    
    for L in lines:
        # Length filter
        if len(L) < args.min_length or len(L) > args.max_length:
            filtered_by_length += 1
            continue
        
        # Character set purity filter
        kurdish_purity = calculate_kurdish_purity(L)
        if kurdish_purity < (100.0 - args.max_non_kurdish):
            filtered_by_charset += 1
            continue
        
        # ZWNJ density filter
        zwnj_density = calculate_zwnj_density(L)
        if args.min_zwnj > 0 and zwnj_density < args.min_zwnj:
            filtered_by_zwnj += 1
            continue
        
        # ZWNJ pattern validation (if enabled)
        if args.validate_zwnj_patterns and not validate_zwnj_patterns(L):
            filtered_by_pattern += 1
            continue
        
        # Calculate overall quality score
        quality_score = calculate_overall_quality(L, args.target_zwnj, args.validate_zwnj_patterns)
        
        # For duplicates, keep the one with higher quality score
        if L in seen:
            if quality_score > seen[L]:
                # Replace with higher-quality version
                idx = next(i for i, line in enumerate(deduped) if line == L)
                deduped[idx] = L
                seen[L] = quality_score
        else:
            seen[L] = quality_score
            deduped.append(L)

    # Calculate initial ZWNJ density
    initial_text = '\n'.join(deduped)
    initial_zwnj = calculate_zwnj_density(initial_text)
    
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

    # Start with deduped lines
    balanced = list(deduped)
    
    # Quality-based oversampling if target is specified
    zwnj_oversampled = 0
    if args.target_zwnj > 0 and initial_zwnj < args.target_zwnj:
        # Score all lines by overall quality
        scored_lines = [(L, calculate_overall_quality(L, args.target_zwnj, args.validate_zwnj_patterns)) 
                       for L in deduped]
        # Sort by score (highest first)
        scored_lines.sort(key=lambda x: x[1], reverse=True)
        
        # Oversample high-quality lines until we reach target or safety limit
        safety_cap = len(deduped) * 3
        current_zwnj = initial_zwnj
        
        while current_zwnj < args.target_zwnj and zwnj_oversampled < safety_cap:
            # Take top 20% high-quality lines for oversampling
            top_lines = [L for L, score in scored_lines[:max(1, len(scored_lines) // 5)] if score > 6.0]
            if not top_lines:
                break
            
            # Add one from top lines
            L = top_lines[zwnj_oversampled % len(top_lines)]
            balanced.append(L)
            zwnj_oversampled += 1
            
            # Recalculate ZWNJ density
            current_text = '\n'.join(balanced)
            current_zwnj = calculate_zwnj_density(current_text)
            
            # Update char histogram
            char_hist.update(L)

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

    # Calculate final ZWNJ density
    final_zwnj = calculate_zwnj_density(text)
    final_zwnj_count = text.count(ZWNJ)
    
    # Stats
    (OUT_DIR / 'char_histogram.csv').write_text(
        'char,codepoint,count\n' + '\n'.join(
            f"{ch},{ord(ch):04X},{char_hist.get(ch,0)}" for ch in sorted(TARGET_CHARS)
        ) + '\n', encoding='utf-8'
    )
    
    # Calculate average quality score
    avg_quality = sum(calculate_overall_quality(L, args.target_zwnj, args.validate_zwnj_patterns) 
                     for L in balanced[:min(100, len(balanced))]) / min(100, len(balanced))
    
    # Calculate average length
    avg_length = sum(len(L) for L in balanced) / len(balanced) if balanced else 0
    
    stats_lines = [
        f"Sources: {len(sources)} files",
        f"Lines (raw): {len(lines)}",
        f"",
        f"Quality Filtering:",
        f"  Filtered by length: {filtered_by_length}" if filtered_by_length > 0 else None,
        f"  Filtered by character set: {filtered_by_charset}" if filtered_by_charset > 0 else None,
        f"  Filtered by ZWNJ: {filtered_by_zwnj}" if args.min_zwnj > 0 else None,
        f"  Filtered by ZWNJ patterns: {filtered_by_pattern}" if args.validate_zwnj_patterns else None,
        f"  Total filtered: {filtered_by_length + filtered_by_charset + filtered_by_zwnj + filtered_by_pattern}",
        f"",
        f"Lines (after filtering): {len(deduped)}",
        f"Lines (quality oversampled): {zwnj_oversampled}" if zwnj_oversampled > 0 else None,
        f"Lines (final): {len(balanced)}",
        f"",
        f"ZWNJ Density:",
        f"  Initial: {initial_zwnj:.3f}%",
        f"  Final: {final_zwnj:.3f}%",
        f"  ZWNJ count: {final_zwnj_count:,}",
        f"  Total chars: {len(text):,}",
        f"",
        f"Quality Metrics:",
        f"  Average quality score: {avg_quality:.2f}/10.0",
        f"  Average sentence length: {avg_length:.1f} chars",
        f"  ZWNJ quality: {'✅ EXCELLENT (6-10%)' if 6 <= final_zwnj <= 10 else '⚠️  ACCEPTABLE (1-6%)' if final_zwnj >= 1 else '❌ LOW (<1%)'}",
        f"",
        f"Filter Settings:",
        f"  Min length: {args.min_length} chars",
        f"  Max length: {args.max_length} chars",
        f"  Max non-Kurdish: {args.max_non_kurdish:.1f}%",
        f"  Min ZWNJ: {args.min_zwnj:.1f}%" if args.min_zwnj > 0 else None,
        f"  Target ZWNJ: {args.target_zwnj:.1f}%" if args.target_zwnj > 0 else None,
        f"  ZWNJ pattern validation: {'Enabled' if args.validate_zwnj_patterns else 'Disabled'}",
    ]
    
    (OUT_DIR / 'corpus_stats.txt').write_text(
        '\n'.join(line for line in stats_lines if line is not None) + '\n',
        encoding='utf-8'
    )

    print(f"Wrote {TARGET_FINAL}")
    print(f"Char histogram -> {OUT_DIR / 'char_histogram.csv'}")
    print(f"ZWNJ density: {final_zwnj:.3f}% ({'✅' if 6 <= final_zwnj <= 10 else '⚠️' if final_zwnj >= 1 else '❌'})")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
