#!/usr/bin/env python3
"""
Merge Phase 4 corpus with Wikipedia Phase 5 extraction
Deduplicate, balance, and create final Phase 5 corpus
"""

from pathlib import Path
from collections import Counter
import re

ZWNJ = '\u200c'

def normalize_line(line: str) -> str:
    """Normalize line for deduplication"""
    # Remove extra whitespace
    line = re.sub(r'\s+', ' ', line.strip())
    return line

def main():
    work_dir = Path(__file__).parent.parent
    
    # Input files
    phase4_corpus = work_dir / 'corpus' / 'ckb.training_text'
    wikipedia = work_dir / 'corpus' / 'wikipedia_phase5.txt'
    
    # Output file
    phase5_corpus = work_dir / 'corpus' / 'ckb_phase5.training_text'
    
    print("=" * 70)
    print("PHASE 5 CORPUS MERGER")
    print("=" * 70)
    print()
    
    # Read Phase 4 corpus
    print(f"Reading Phase 4 corpus: {phase4_corpus}")
    with open(phase4_corpus, 'r', encoding='utf-8') as f:
        phase4_lines = [normalize_line(line) for line in f if line.strip()]
    
    print(f"  Lines: {len(phase4_lines):,}")
    print(f"  Words: {sum(len(line.split()) for line in phase4_lines):,}")
    
    # Read Wikipedia
    print(f"Reading Wikipedia: {wikipedia}")
    with open(wikipedia, 'r', encoding='utf-8') as f:
        wiki_lines = [normalize_line(line) for line in f if line.strip()]
    
    print(f"  Lines: {len(wiki_lines):,}")
    print(f"  Words: {sum(len(line.split()) for line in wiki_lines):,}")
    print()
    
    # Merge and deduplicate
    print("Merging and deduplicating...")
    seen = set()
    merged = []
    
    # Keep Phase 4 lines (priority)
    for line in phase4_lines:
        if line and line not in seen:
            merged.append(line)
            seen.add(line)
    
    # Add Wikipedia lines
    wiki_added = 0
    for line in wiki_lines:
        if line and line not in seen:
            merged.append(line)
            seen.add(line)
            wiki_added += 1
    
    print(f"  Phase 4 lines kept: {len(phase4_lines):,}")
    print(f"  Wikipedia lines added: {wiki_added:,}")
    print(f"  Wikipedia duplicates removed: {len(wiki_lines) - wiki_added:,}")
    print(f"  Total unique lines: {len(merged):,}")
    print()
    
    # Calculate statistics
    total_chars = sum(len(line) for line in merged)
    total_words = sum(len(line.split()) for line in merged)
    total_zwnj = sum(line.count(ZWNJ) for line in merged)
    
    zwnj_density = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
    
    print("=" * 70)
    print("PHASE 5 CORPUS STATISTICS")
    print("=" * 70)
    print(f"Total lines: {len(merged):,}")
    print(f"Total words: {total_words:,}")
    print(f"Total characters: {total_chars:,}")
    print(f"ZWNJ count: {total_zwnj:,}")
    print(f"ZWNJ density: {zwnj_density:.2f}%")
    print(f"Avg line length: {total_chars / len(merged):.1f} chars")
    print(f"Avg words per line: {total_words / len(merged):.1f}")
    print()
    
    # Character frequency
    char_freq = Counter()
    for line in merged:
        char_freq.update(line)
    
    print("Top 20 characters:")
    for char, count in char_freq.most_common(20):
        if char == ZWNJ:
            print(f"  ZWNJ (U+200C): {count:,}")
        elif char == ' ':
            print(f"  SPACE: {count:,}")
        elif char == '\n':
            print(f"  NEWLINE: {count:,}")
        else:
            print(f"  {char} (U+{ord(char):04X}): {count:,}")
    print()
    
    # Save merged corpus
    print(f"Saving to {phase5_corpus}...")
    with open(phase5_corpus, 'w', encoding='utf-8') as f:
        for line in merged:
            f.write(line + '\n')
    
    file_size = phase5_corpus.stat().st_size / 1024
    
    print()
    print("=" * 70)
    print("✅ PHASE 5 CORPUS READY")
    print("=" * 70)
    print(f"File: {phase5_corpus}")
    print(f"Size: {file_size:.1f} KB")
    print()
    print("Comparison with Phase 4:")
    print(f"  Lines: 3,321 → {len(merged):,} (+{len(merged)-3321:,}, +{(len(merged)-3321)/3321*100:.1f}%)")
    print(f"  Words: 40,120 → {total_words:,} (+{total_words-40120:,}, +{(total_words-40120)/40120*100:.1f}%)")
    print()
    
    if len(merged) >= 6000:
        print("✅ Corpus size excellent (≥6,000 lines)")
    elif len(merged) >= 5000:
        print("✅ Corpus size good (≥5,000 lines)")
    else:
        print("⚠️  Corpus size could be larger (need more sources)")
    
    if 7.0 <= zwnj_density <= 10.0:
        print(f"✅ ZWNJ density excellent ({zwnj_density:.2f}%)")
    elif 5.0 <= zwnj_density < 7.0:
        print(f"⚠️  ZWNJ density acceptable but low ({zwnj_density:.2f}%)")
    else:
        print(f"❌ ZWNJ density out of range ({zwnj_density:.2f}%)")
    
    print()
    print("Next steps:")
    print("  1. Run corpus audit: python3 tools/corpus_audit.py corpus/ckb_phase5.training_text")
    print("  2. Start Phase 5 training with expanded corpus")


if __name__ == '__main__':
    main()
