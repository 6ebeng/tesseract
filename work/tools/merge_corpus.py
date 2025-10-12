#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge Wikipedia corpus with existing training data, removing duplicates.
Preserves ZWNJ and ensures quality.
"""

import sys
from pathlib import Path
import shutil


def load_corpus(file_path: str) -> set:
    """Load corpus as set of unique lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = set()
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    lines.add(line)
            return lines
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
        return set()


def analyze_corpus(lines: set) -> dict:
    """Analyze corpus statistics."""
    all_text = '\n'.join(lines)
    
    words = []
    for line in lines:
        words.extend(line.split())
    
    zwnj_count = all_text.count('\u200c')
    total_chars = len(all_text)
    
    return {
        'lines': len(lines),
        'words': len(words),
        'chars': total_chars,
        'zwnj': zwnj_count,
        'zwnj_pct': (zwnj_count / total_chars * 100) if total_chars > 0 else 0,
    }


def merge_corpora(existing_file: str, wikipedia_file: str, output_file: str, backup=True):
    """
    Merge two corpora, removing duplicates.
    
    Args:
        existing_file: Path to existing corpus
        wikipedia_file: Path to Wikipedia extracted corpus
        output_file: Path to write merged corpus
        backup: Create backup of existing file
    """
    
    print("="*70)
    print("📚 CORPUS MERGER")
    print("="*70)
    
    # Load existing corpus
    print(f"\n📖 Loading existing corpus: {existing_file}")
    existing = load_corpus(existing_file)
    existing_stats = analyze_corpus(existing)
    
    print(f"   Lines: {existing_stats['lines']:,}")
    print(f"   Words: {existing_stats['words']:,}")
    print(f"   ZWNJ: {existing_stats['zwnj']:,} ({existing_stats['zwnj_pct']:.2f}%)")
    
    # Load Wikipedia corpus
    print(f"\n📖 Loading Wikipedia corpus: {wikipedia_file}")
    wikipedia = load_corpus(wikipedia_file)
    wiki_stats = analyze_corpus(wikipedia)
    
    print(f"   Lines: {wiki_stats['lines']:,}")
    print(f"   Words: {wiki_stats['words']:,}")
    print(f"   ZWNJ: {wiki_stats['zwnj']:,} ({wiki_stats['zwnj_pct']:.2f}%)")
    
    # Find new lines
    new_lines = wikipedia - existing
    duplicates = wikipedia & existing
    
    print(f"\n🔍 Deduplication:")
    print(f"   Unique to existing: {len(existing - wikipedia):,}")
    print(f"   Unique to Wikipedia: {len(new_lines):,}")
    print(f"   Duplicates removed: {len(duplicates):,}")
    
    # Merge
    merged = existing | wikipedia
    merged_stats = analyze_corpus(merged)
    
    print(f"\n📦 Merged corpus:")
    print(f"   Total lines: {merged_stats['lines']:,}")
    print(f"   Total words: {merged_stats['words']:,}")
    print(f"   Total ZWNJ: {merged_stats['zwnj']:,} ({merged_stats['zwnj_pct']:.2f}%)")
    
    # Check ZWNJ percentage
    if merged_stats['zwnj_pct'] < 5.0:
        print(f"\n⚠️ WARNING: ZWNJ percentage is low ({merged_stats['zwnj_pct']:.2f}%)")
        print(f"   Expected: 6-10% for proper Kurdish text")
        print(f"   Consider filtering Wikipedia corpus more strictly")
    elif 6.0 <= merged_stats['zwnj_pct'] <= 10.0:
        print(f"\n✅ ZWNJ percentage is good ({merged_stats['zwnj_pct']:.2f}%)")
    else:
        print(f"\n⚠️ ZWNJ percentage unusual: {merged_stats['zwnj_pct']:.2f}%")
    
    # Backup existing
    if backup and Path(existing_file).exists():
        backup_file = existing_file + '.backup_phase2'
        shutil.copy2(existing_file, backup_file)
        print(f"\n💾 Backup created: {backup_file}")
    
    # Write merged corpus
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Sort for consistency and reproducibility
        for line in sorted(merged):
            f.write(line + '\n')
    
    print(f"✅ Merged corpus saved: {output_file}")
    
    # Growth summary
    print(f"\n📈 Growth Summary:")
    print(f"   Words: {existing_stats['words']:,} → {merged_stats['words']:,} (+{merged_stats['words'] - existing_stats['words']:,}, +{((merged_stats['words'] / existing_stats['words']) - 1) * 100:.1f}%)")
    print(f"   ZWNJ: {existing_stats['zwnj']:,} → {merged_stats['zwnj']:,} (+{merged_stats['zwnj'] - existing_stats['zwnj']:,})")
    
    print("="*70)
    print("✅ MERGE COMPLETE")
    print("="*70)
    
    return merged_stats


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 merge_corpus.py <existing.txt> <wikipedia.txt> <output.txt>")
        print()
        print("Example:")
        print("  python3 merge_corpus.py ckb.training_text ckb_wikipedia.txt ckb.training_text")
        print()
        print("Options:")
        print("  - Creates backup automatically (existing.txt.backup_phase2)")
        print("  - Removes duplicate lines")
        print("  - Sorts output for consistency")
        print("  - Validates ZWNJ percentage")
        sys.exit(1)
    
    existing_file = sys.argv[1]
    wikipedia_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Verify input files exist
    if not Path(existing_file).exists():
        print(f"❌ Error: Existing corpus not found: {existing_file}")
        sys.exit(1)
    
    if not Path(wikipedia_file).exists():
        print(f"❌ Error: Wikipedia corpus not found: {wikipedia_file}")
        sys.exit(1)
    
    # Merge
    try:
        merge_corpora(existing_file, wikipedia_file, output_file)
    except Exception as e:
        print(f"\n❌ Error during merge: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
