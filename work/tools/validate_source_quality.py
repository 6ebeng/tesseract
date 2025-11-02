#!/usr/bin/env python3
"""
Source Quality Validator for Kurdish OCR Training

Validates potential training corpus sources based on:
1. ZWNJ (U+200C) density - THE critical metric (must be 6-10%)
2. Script purity (Kurdish vs Latin/Arabic)
3. Sentence length distribution
4. Overall text quality indicators

Usage:
    python validate_source_quality.py <text_file>
    python validate_source_quality.py samples/*.txt
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Unicode ranges for script detection
KURDISH_ARABIC_SCRIPT = r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'
LATIN_SCRIPT = r'[A-Za-z]'
DIGIT_LATIN = r'[0-9]'
DIGIT_ARABIC = r'[\u0660-\u0669\u06F0-\u06F9]'

# Quality thresholds
ZWNJ_MIN = 6.0      # Minimum ZWNJ% for acceptance
ZWNJ_TARGET = 8.0   # Target ZWNJ% (optimal)
ZWNJ_MAX = 12.0     # Maximum reasonable ZWNJ%
KURDISH_MIN = 85.0  # Minimum Kurdish script%
MIN_SENTENCES = 50  # Minimum sentences for valid sample
AVG_WORDS_MIN = 5   # Minimum average words per sentence
AVG_WORDS_MAX = 50  # Maximum average words per sentence


def analyze_text(text: str) -> Dict:
    """Analyze text for quality metrics."""
    
    # Basic stats
    total_chars = len(text)
    
    # Character counts
    zwnj_count = text.count('\u200c')
    tatweel_count = text.count('\u0640')
    
    # Script analysis
    kurdish_chars = len(re.findall(KURDISH_ARABIC_SCRIPT, text))
    latin_chars = len(re.findall(LATIN_SCRIPT, text))
    latin_digits = len(re.findall(DIGIT_LATIN, text))
    arabic_digits = len(re.findall(DIGIT_ARABIC, text))
    
    # Calculate script percentages
    script_total = kurdish_chars + latin_chars
    kurdish_pct = (kurdish_chars / script_total * 100) if script_total > 0 else 0
    latin_pct = (latin_chars / script_total * 100) if script_total > 0 else 0
    
    # Sentence analysis
    sentences = [s.strip() for s in re.split(r'[.!?؟]+', text) if s.strip()]
    sentence_count = len(sentences)
    
    # Word analysis (split by whitespace)
    words_per_sentence = [len(s.split()) for s in sentences]
    avg_words = sum(words_per_sentence) / len(words_per_sentence) if words_per_sentence else 0
    
    # ZWNJ density
    zwnj_pct = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
    
    # Tatweel density (should be very low for Kurdish)
    tatweel_pct = (tatweel_count / total_chars * 100) if total_chars > 0 else 0
    
    # Sentences with ZWNJ
    sentences_with_zwnj = sum(1 for s in sentences if '\u200c' in s)
    zwnj_sentence_coverage = (sentences_with_zwnj / sentence_count * 100) if sentence_count > 0 else 0
    
    return {
        'total_chars': total_chars,
        'sentence_count': sentence_count,
        'zwnj_count': zwnj_count,
        'zwnj_pct': zwnj_pct,
        'zwnj_sentence_coverage': zwnj_sentence_coverage,
        'tatweel_count': tatweel_count,
        'tatweel_pct': tatweel_pct,
        'kurdish_chars': kurdish_chars,
        'kurdish_pct': kurdish_pct,
        'latin_chars': latin_chars,
        'latin_pct': latin_pct,
        'latin_digits': latin_digits,
        'arabic_digits': arabic_digits,
        'avg_words': avg_words,
        'sentences': sentences[:5],  # First 5 for inspection
    }


def evaluate_quality(metrics: Dict) -> Tuple[str, str, List[str]]:
    """
    Evaluate text quality and return decision.
    
    Returns:
        (decision, reason, issues)
        decision: 'ACCEPT', 'REVIEW', or 'REJECT'
        reason: explanation
        issues: list of quality issues found
    """
    issues = []
    
    # Critical check: ZWNJ density
    if metrics['zwnj_pct'] < ZWNJ_MIN:
        issues.append(f"❌ CRITICAL: ZWNJ density too low ({metrics['zwnj_pct']:.2f}% < {ZWNJ_MIN}%)")
        decision = 'REJECT'
        reason = f"Unusable - ZWNJ density {metrics['zwnj_pct']:.2f}% is below minimum {ZWNJ_MIN}%"
        return decision, reason, issues
    
    if metrics['zwnj_pct'] > ZWNJ_MAX:
        issues.append(f"⚠️  WARNING: ZWNJ density unusually high ({metrics['zwnj_pct']:.2f}% > {ZWNJ_MAX}%)")
    
    # Check sample size
    if metrics['sentence_count'] < MIN_SENTENCES:
        issues.append(f"⚠️  WARNING: Sample size small ({metrics['sentence_count']} < {MIN_SENTENCES} sentences)")
    
    # Check script purity
    if metrics['kurdish_pct'] < KURDISH_MIN:
        issues.append(f"⚠️  WARNING: Kurdish script purity low ({metrics['kurdish_pct']:.1f}% < {KURDISH_MIN}%)")
    
    # Check sentence length
    if metrics['avg_words'] < AVG_WORDS_MIN:
        issues.append(f"⚠️  WARNING: Sentences too short (avg {metrics['avg_words']:.1f} words)")
    elif metrics['avg_words'] > AVG_WORDS_MAX:
        issues.append(f"⚠️  WARNING: Sentences too long (avg {metrics['avg_words']:.1f} words)")
    
    # Check ZWNJ coverage
    if metrics['zwnj_sentence_coverage'] < 50:
        issues.append(f"⚠️  WARNING: Low ZWNJ coverage ({metrics['zwnj_sentence_coverage']:.1f}% of sentences)")
    
    # Make decision
    if not issues:
        decision = 'ACCEPT'
        reason = f"Excellent quality - ZWNJ {metrics['zwnj_pct']:.2f}%, Kurdish {metrics['kurdish_pct']:.1f}%"
    elif metrics['zwnj_pct'] >= ZWNJ_MIN and metrics['kurdish_pct'] >= KURDISH_MIN:
        decision = 'ACCEPT'
        reason = f"Good quality - ZWNJ {metrics['zwnj_pct']:.2f}%, Kurdish {metrics['kurdish_pct']:.1f}%"
    else:
        decision = 'REVIEW'
        reason = "Borderline quality - manual review recommended"
    
    return decision, reason, issues


def print_report(filename: str, metrics: Dict, decision: str, reason: str, issues: List[str]):
    """Print formatted quality report."""
    
    # Decision header with color
    decision_symbols = {
        'ACCEPT': '✅',
        'REVIEW': '⚠️ ',
        'REJECT': '❌'
    }
    
    print(f"\n{'='*70}")
    print(f"Source Quality Report: {filename}")
    print(f"{'='*70}")
    
    # Decision
    print(f"\n{decision_symbols.get(decision, '?')} DECISION: {decision}")
    print(f"   {reason}")
    
    # Quality metrics
    print(f"\n📊 Quality Metrics:")
    print(f"   ZWNJ Density:        {metrics['zwnj_pct']:6.2f}% ({metrics['zwnj_count']:,} occurrences)")
    print(f"   ZWNJ Coverage:       {metrics['zwnj_sentence_coverage']:6.2f}% of sentences")
    print(f"   Kurdish Script:      {metrics['kurdish_pct']:6.2f}% ({metrics['kurdish_chars']:,} chars)")
    print(f"   Latin Script:        {metrics['latin_pct']:6.2f}% ({metrics['latin_chars']:,} chars)")
    
    # Size metrics
    print(f"\n📏 Size Metrics:")
    print(f"   Total characters:    {metrics['total_chars']:,}")
    print(f"   Sentence count:      {metrics['sentence_count']:,}")
    print(f"   Avg words/sentence:  {metrics['avg_words']:.1f}")
    
    # Other indicators
    print(f"\n🔍 Other Indicators:")
    print(f"   Tatweel (U+0640):    {metrics['tatweel_pct']:6.3f}% (should be ~0.025%)")
    print(f"   Latin digits:        {metrics['latin_digits']:,}")
    print(f"   Arabic digits:       {metrics['arabic_digits']:,}")
    
    # Issues
    if issues:
        print(f"\n⚠️  Issues Found:")
        for issue in issues:
            print(f"   {issue}")
    
    # Sample sentences
    if metrics['sentences']:
        print(f"\n📝 Sample Sentences (first 5):")
        for i, sentence in enumerate(metrics['sentences'][:5], 1):
            # Truncate long sentences
            display = sentence[:100] + '...' if len(sentence) > 100 else sentence
            zwnj_in_sentence = sentence.count('\u200c')
            print(f"   {i}. {display}")
            print(f"      (ZWNJ: {zwnj_in_sentence}, Words: {len(sentence.split())})")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if decision == 'ACCEPT':
        print(f"   ✅ Use this source for training")
        print(f"   ✅ ZWNJ density is in optimal range")
        if metrics['zwnj_pct'] < ZWNJ_TARGET:
            print(f"   💡 Consider blending with higher-ZWNJ sources (target: {ZWNJ_TARGET}%)")
    elif decision == 'REVIEW':
        print(f"   ⚠️  Manual review recommended")
        print(f"   ⚠️  Check if issues can be fixed with preprocessing")
        print(f"   ⚠️  Consider using only if no better sources available")
    else:  # REJECT
        print(f"   ❌ DO NOT use this source for training")
        print(f"   ❌ ZWNJ density too low - will degrade model quality")
        print(f"   💡 Look for sources with biographical/historical content")
    
    print(f"\n{'='*70}\n")


def validate_file(filepath: Path):
    """Validate a single file."""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            print(f"❌ ERROR: {filepath.name} is empty")
            return
        
        # Analyze
        metrics = analyze_text(text)
        
        # Evaluate
        decision, reason, issues = evaluate_quality(metrics)
        
        # Report
        print_report(filepath.name, metrics, decision, reason, issues)
        
        return decision
        
    except Exception as e:
        print(f"❌ ERROR processing {filepath.name}: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_source_quality.py <text_file> [<text_file2> ...]")
        print("\nExample:")
        print("  python validate_source_quality.py sample.txt")
        print("  python validate_source_quality.py samples/*.txt")
        sys.exit(1)
    
    # Process each file
    files = [Path(f) for f in sys.argv[1:]]
    
    if not files:
        print("❌ No files found")
        sys.exit(1)
    
    print(f"\n🔍 Validating {len(files)} file(s)...")
    
    results = {'ACCEPT': [], 'REVIEW': [], 'REJECT': [], 'ERROR': []}
    
    for filepath in files:
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            results['ERROR'].append(filepath.name)
            continue
        
        decision = validate_file(filepath)
        if decision:
            results[decision].append(filepath.name)
        else:
            results['ERROR'].append(filepath.name)
    
    # Summary
    if len(files) > 1:
        print(f"\n{'='*70}")
        print(f"SUMMARY: {len(files)} files validated")
        print(f"{'='*70}")
        print(f"✅ ACCEPT:  {len(results['ACCEPT'])} files")
        print(f"⚠️  REVIEW:  {len(results['REVIEW'])} files")
        print(f"❌ REJECT:  {len(results['REJECT'])} files")
        if results['ERROR']:
            print(f"❌ ERROR:   {len(results['ERROR'])} files")
        
        if results['ACCEPT']:
            print(f"\n✅ Accepted sources:")
            for name in results['ACCEPT']:
                print(f"   - {name}")
        
        if results['REVIEW']:
            print(f"\n⚠️  Review needed:")
            for name in results['REVIEW']:
                print(f"   - {name}")
        
        if results['REJECT']:
            print(f"\n❌ Rejected sources:")
            for name in results['REJECT']:
                print(f"   - {name}")
        
        print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
