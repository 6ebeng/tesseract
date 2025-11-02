#!/usr/bin/env python3
"""
Corpus Blending Tool for Kurdish OCR Training

Intelligently blends multiple corpus sources to achieve optimal ZWNJ density
and domain balance.

Usage:
    python blend_corpus.py --news news.txt --bio bio.txt --output blended.txt --target-zwnj 8.0
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import re


def count_zwnj(text: str) -> Tuple[int, float]:
    """Count ZWNJ characters and calculate density."""
    zwnj_count = text.count('\u200c')
    total_chars = len(text)
    zwnj_pct = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
    return zwnj_count, zwnj_pct


def get_sentences(text: str) -> List[str]:
    """Extract sentences from text."""
    sentences = [s.strip() for s in re.split(r'[.!?؟]+', text) if s.strip()]
    return sentences


def analyze_corpus(filepath: Path) -> Dict:
    """Analyze a corpus file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        sentences = get_sentences(text)
        zwnj_count, zwnj_pct = count_zwnj(text)
        
        # Count sentences with ZWNJ
        sentences_with_zwnj = sum(1 for s in sentences if '\u200c' in s)
        
        return {
            'filepath': filepath,
            'text': text,
            'sentences': sentences,
            'sentence_count': len(sentences),
            'total_chars': len(text),
            'zwnj_count': zwnj_count,
            'zwnj_pct': zwnj_pct,
            'sentences_with_zwnj': sentences_with_zwnj,
            'zwnj_coverage': (sentences_with_zwnj / len(sentences) * 100) if sentences else 0
        }
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return None


def calculate_blend_ratio(sources: List[Dict], target_zwnj: float) -> Dict[str, float]:
    """
    Calculate optimal blend ratio to achieve target ZWNJ density.
    
    Simple approach: Weight sources proportionally to reach target.
    """
    if not sources:
        return {}
    
    # If only one source, use it entirely
    if len(sources) == 1:
        return {sources[0]['filepath'].name: 1.0}
    
    # Calculate current weighted average
    total_sentences = sum(s['sentence_count'] for s in sources)
    current_zwnj = sum(s['zwnj_pct'] * s['sentence_count'] for s in sources) / total_sentences
    
    print(f"\n📊 Blend Analysis:")
    print(f"   Current weighted ZWNJ: {current_zwnj:.2f}%")
    print(f"   Target ZWNJ:           {target_zwnj:.2f}%")
    
    # Simple strategy: proportional weighting
    # If current is below target, favor higher-ZWNJ sources
    # If current is above target, favor lower-ZWNJ sources
    
    ratios = {}
    
    if abs(current_zwnj - target_zwnj) < 0.5:
        # Already close to target, use proportional
        for source in sources:
            ratios[source['filepath'].name] = source['sentence_count'] / total_sentences
        print(f"   Strategy: Proportional (already near target)")
    
    elif current_zwnj < target_zwnj:
        # Need to increase ZWNJ - favor high-ZWNJ sources
        print(f"   Strategy: Favor high-ZWNJ sources")
        for source in sources:
            # Weight by ZWNJ density
            weight = source['zwnj_pct'] / sum(s['zwnj_pct'] for s in sources)
            ratios[source['filepath'].name] = weight
    
    else:
        # Need to decrease ZWNJ - favor low-ZWNJ sources
        print(f"   Strategy: Favor low-ZWNJ sources")
        for source in sources:
            # Inverse weight by ZWNJ density
            inv_zwnj = (12 - source['zwnj_pct'])  # 12% is max reasonable ZWNJ
            weight = inv_zwnj / sum((12 - s['zwnj_pct']) for s in sources)
            ratios[source['filepath'].name] = weight
    
    # Normalize ratios to sum to 1.0
    total_ratio = sum(ratios.values())
    ratios = {k: v/total_ratio for k, v in ratios.items()}
    
    return ratios


def blend_corpora(sources: List[Dict], ratios: Dict[str, float], output: Path):
    """Blend corpora according to ratios."""
    
    print(f"\n🔀 Blending corpora...")
    
    # Calculate target sentence counts
    total_sentences = sum(s['sentence_count'] for s in sources)
    
    blended_sentences = []
    
    for source in sources:
        name = source['filepath'].name
        ratio = ratios.get(name, 0)
        target_count = int(source['sentence_count'] * ratio)
        
        # Take sentences up to target count
        sentences = source['sentences'][:target_count]
        blended_sentences.extend(sentences)
        
        print(f"   {name:30} {ratio*100:5.1f}% ({len(sentences):4} sentences)")
    
    # Join sentences
    blended_text = '\n'.join(blended_sentences)
    
    # Analyze blended result
    zwnj_count, zwnj_pct = count_zwnj(blended_text)
    
    # Write output
    with open(output, 'w', encoding='utf-8') as f:
        f.write(blended_text)
    
    print(f"\n✅ Blended corpus saved to: {output}")
    print(f"\n📊 Blended Corpus Metrics:")
    print(f"   Total sentences:    {len(blended_sentences):,}")
    print(f"   Total characters:   {len(blended_text):,}")
    print(f"   ZWNJ density:       {zwnj_pct:.2f}%")
    print(f"   ZWNJ count:         {zwnj_count:,}")
    
    return blended_text, zwnj_pct


def main():
    parser = argparse.ArgumentParser(description='Blend Kurdish corpus sources for optimal ZWNJ density')
    parser.add_argument('--sources', nargs='+', required=True, help='Input corpus files')
    parser.add_argument('--output', required=True, help='Output blended corpus file')
    parser.add_argument('--target-zwnj', type=float, default=8.0, help='Target ZWNJ density (default: 8.0%%)')
    parser.add_argument('--equal', action='store_true', help='Use equal proportions instead of weighted')
    
    args = parser.parse_args()
    
    # Validate inputs
    source_files = [Path(s) for s in args.sources]
    for sf in source_files:
        if not sf.exists():
            print(f"❌ File not found: {sf}")
            sys.exit(1)
    
    output_file = Path(args.output)
    
    print(f"\n{'='*70}")
    print(f"Corpus Blending Tool")
    print(f"{'='*70}")
    print(f"\nTarget ZWNJ density: {args.target_zwnj:.2f}%")
    print(f"Input sources: {len(source_files)}")
    
    # Analyze sources
    print(f"\n📖 Analyzing sources...")
    sources = []
    for sf in source_files:
        print(f"   Reading {sf.name}...")
        analysis = analyze_corpus(sf)
        if analysis:
            sources.append(analysis)
    
    if not sources:
        print("❌ No valid sources found")
        sys.exit(1)
    
    # Print source analysis
    print(f"\n📊 Source Analysis:")
    print(f"   {'Source':<30} {'Sentences':>10} {'ZWNJ%':>8} {'Coverage':>10}")
    print(f"   {'-'*30} {'-'*10} {'-'*8} {'-'*10}")
    for source in sources:
        print(f"   {source['filepath'].name:<30} {source['sentence_count']:>10,} {source['zwnj_pct']:>7.2f}% {source['zwnj_coverage']:>9.1f}%")
    
    # Calculate blend ratios
    if args.equal:
        print(f"\n⚖️  Using equal proportions")
        ratios = {s['filepath'].name: 1.0/len(sources) for s in sources}
    else:
        ratios = calculate_blend_ratio(sources, args.target_zwnj)
    
    # Print blend plan
    print(f"\n📋 Blend Plan:")
    for name, ratio in ratios.items():
        print(f"   {name:<30} {ratio*100:>5.1f}%")
    
    # Blend
    blended_text, final_zwnj = blend_corpora(sources, ratios, output_file)
    
    # Check if target achieved
    print(f"\n🎯 Target Achievement:")
    diff = abs(final_zwnj - args.target_zwnj)
    if diff < 0.5:
        print(f"   ✅ Target achieved: {final_zwnj:.2f}% (target: {args.target_zwnj:.2f}%)")
    elif diff < 1.0:
        print(f"   ⚠️  Close to target: {final_zwnj:.2f}% (target: {args.target_zwnj:.2f}%, diff: {diff:.2f}%)")
    else:
        print(f"   ⚠️  Target not achieved: {final_zwnj:.2f}% (target: {args.target_zwnj:.2f}%, diff: {diff:.2f}%)")
        print(f"   💡 Consider adjusting source ratios or finding additional sources")
    
    # Quality check
    if final_zwnj < 6.0:
        print(f"\n❌ WARNING: Final ZWNJ density ({final_zwnj:.2f}%) is below minimum (6.0%)")
        print(f"   This corpus may not be suitable for training!")
    elif final_zwnj > 12.0:
        print(f"\n⚠️  WARNING: Final ZWNJ density ({final_zwnj:.2f}%) is unusually high (>12%)")
        print(f"   Verify source quality")
    else:
        print(f"\n✅ Quality check passed: ZWNJ density in acceptable range (6-12%)")
    
    print(f"\n{'='*70}\n")


if __name__ == '__main__':
    main()
