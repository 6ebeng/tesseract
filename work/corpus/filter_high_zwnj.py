#!/usr/bin/env python3
"""
Filter corpus for high-ZWNJ sentences to match mgk.tif distribution.
Target: 9-11% ZWNJ density (mgk.tif has 11.17%)
"""

import os
from pathlib import Path

def calculate_zwnj_density(text):
    """Calculate ZWNJ (U+200C) density in text."""
    if not text:
        return 0.0
    zwnj_count = text.count('\u200c')
    return (zwnj_count / len(text)) * 100

def is_high_quality_kurdish(text):
    """Check if sentence is high-quality Kurdish text."""
    # Count Kurdish-specific characters
    kurdish_chars = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهەوۆیێ')
    kurdish_count = sum(1 for c in text if c in kurdish_chars)
    
    # Total alphabetic characters (approximate)
    alpha_count = sum(1 for c in text if c.isalpha() or c in kurdish_chars)
    
    if alpha_count == 0:
        return False
    
    # Require >85% Kurdish script
    kurdish_ratio = kurdish_count / alpha_count
    return kurdish_ratio > 0.85

def filter_high_zwnj_corpus(input_file, output_file, min_zwnj=9.0, max_zwnj=15.0, 
                            min_length=8, max_length=40):
    """
    Filter corpus for sentences with high ZWNJ density.
    
    Args:
        input_file: Path to input corpus file
        output_file: Path to output filtered corpus
        min_zwnj: Minimum ZWNJ density % (default: 9.0)
        max_zwnj: Maximum ZWNJ density % (default: 15.0)
        min_length: Minimum word count (default: 8)
        max_length: Maximum word count (default: 40)
    """
    print(f"\n{'='*60}")
    print(f"High-ZWNJ Corpus Filter")
    print(f"{'='*60}")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"ZWNJ range: {min_zwnj:.1f}% - {max_zwnj:.1f}%")
    print(f"Word length: {min_length}-{max_length}")
    print()
    
    # Read input corpus
    with open(input_file, 'r', encoding='utf-8') as f:
        sentences = [line.strip() for line in f if line.strip()]
    
    print(f"Total input sentences: {len(sentences):,}")
    
    # Filter sentences
    filtered = []
    stats = {
        'too_short': 0,
        'too_long': 0,
        'low_zwnj': 0,
        'high_zwnj': 0,
        'not_kurdish': 0,
        'accepted': 0
    }
    
    zwnj_densities = []
    
    for sentence in sentences:
        # Check word length
        words = sentence.split()
        if len(words) < min_length:
            stats['too_short'] += 1
            continue
        if len(words) > max_length:
            stats['too_long'] += 1
            continue
        
        # Check Kurdish purity
        if not is_high_quality_kurdish(sentence):
            stats['not_kurdish'] += 1
            continue
        
        # Check ZWNJ density
        zwnj_pct = calculate_zwnj_density(sentence)
        
        if zwnj_pct < min_zwnj:
            stats['low_zwnj'] += 1
            continue
        
        if zwnj_pct > max_zwnj:
            stats['high_zwnj'] += 1
            continue
        
        # Accepted
        filtered.append(sentence)
        zwnj_densities.append(zwnj_pct)
        stats['accepted'] += 1
    
    # Write filtered corpus
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in filtered:
            f.write(sentence + '\n')
    
    # Calculate statistics
    if zwnj_densities:
        avg_zwnj = sum(zwnj_densities) / len(zwnj_densities)
        min_zwnj_found = min(zwnj_densities)
        max_zwnj_found = max(zwnj_densities)
    else:
        avg_zwnj = 0
        min_zwnj_found = 0
        max_zwnj_found = 0
    
    # Calculate average word length
    avg_words = sum(len(s.split()) for s in filtered) / len(filtered) if filtered else 0
    
    # Print results
    print(f"\n{'='*60}")
    print("Filtering Results")
    print(f"{'='*60}")
    print(f"Accepted: {stats['accepted']:,} sentences ({stats['accepted']/len(sentences)*100:.1f}%)")
    print(f"\nRejection reasons:")
    print(f"  Too short (<{min_length} words): {stats['too_short']:,}")
    print(f"  Too long (>{max_length} words): {stats['too_long']:,}")
    print(f"  Low ZWNJ (<{min_zwnj:.1f}%): {stats['low_zwnj']:,}")
    print(f"  High ZWNJ (>{max_zwnj:.1f}%): {stats['high_zwnj']:,}")
    print(f"  Not Kurdish (<85% Kurdish script): {stats['not_kurdish']:,}")
    
    print(f"\n{'='*60}")
    print("Output Corpus Statistics")
    print(f"{'='*60}")
    print(f"Total sentences: {len(filtered):,}")
    print(f"Average ZWNJ density: {avg_zwnj:.2f}%")
    print(f"ZWNJ range: {min_zwnj_found:.2f}% - {max_zwnj_found:.2f}%")
    print(f"Average words per sentence: {avg_words:.1f}")
    print(f"\nOutput file: {output_file}")
    
    # Calculate total ZWNJ in output
    output_text = '\n'.join(filtered)
    output_zwnj = output_text.count('\u200c')
    print(f"Total characters: {len(output_text):,}")
    print(f"Total ZWNJ: {output_zwnj:,}")
    
    return stats, filtered

def main():
    """Main function to filter high-ZWNJ sentences."""
    
    # Define paths (current directory is corpus)
    corpus_dir = Path('.')
    
    # Input files to process
    input_files = [
        'ckb_scraped_filtered.training_text',  # 9.33% ZWNJ - best source
        'ckb_phase6_batch3.training_text',     # 6.36% ZWNJ - decent
    ]
    
    # Output file
    output_file = corpus_dir / 'ckb_high_zwnj.training_text'
    
    print("\n" + "="*60)
    print("HIGH-ZWNJ CORPUS BUILDER")
    print("="*60)
    print("Target: Match mgk.tif distribution (11.17% ZWNJ)")
    print("Strategy: Extract sentences with 9-15% ZWNJ")
    print("="*60)
    
    # Collect all high-ZWNJ sentences from all sources
    all_filtered = []
    
    for input_file in input_files:
        input_path = corpus_dir / input_file
        if not input_path.exists():
            print(f"\n⚠️  Skipping {input_file} (not found)")
            continue
        
        # Create temporary output for this source
        temp_output = corpus_dir / f'temp_{input_file}'
        
        stats, filtered = filter_high_zwnj_corpus(
            input_path,
            temp_output,
            min_zwnj=9.0,  # Target range: 9-15%
            max_zwnj=15.0,
            min_length=8,
            max_length=40
        )
        
        all_filtered.extend(filtered)
        
        # Remove temp file
        if temp_output.exists():
            temp_output.unlink()
    
    # Remove duplicates (keep order)
    seen = set()
    unique_filtered = []
    for sentence in all_filtered:
        if sentence not in seen:
            seen.add(sentence)
            unique_filtered.append(sentence)
    
    # Write combined output
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in unique_filtered:
            f.write(sentence + '\n')
    
    # Final statistics
    output_text = '\n'.join(unique_filtered)
    final_zwnj = calculate_zwnj_density(output_text)
    avg_words = sum(len(s.split()) for s in unique_filtered) / len(unique_filtered)
    
    print(f"\n{'='*60}")
    print("FINAL HIGH-ZWNJ CORPUS")
    print(f"{'='*60}")
    print(f"Total sentences: {len(unique_filtered):,}")
    print(f"Average ZWNJ density: {final_zwnj:.2f}%")
    print(f"Average words/sentence: {avg_words:.1f}")
    print(f"Total characters: {len(output_text):,}")
    print(f"Total ZWNJ: {output_text.count('\u200c'):,}")
    print(f"\nOutput: {output_file}")
    
    # Compare to mgk.tif
    print(f"\n{'='*60}")
    print("COMPARISON TO mgk.tif")
    print(f"{'='*60}")
    print(f"mgk.tif ZWNJ: 11.17%")
    print(f"High-ZWNJ corpus ZWNJ: {final_zwnj:.2f}%")
    diff = abs(11.17 - final_zwnj)
    print(f"Difference: {diff:.2f}%")
    
    if diff < 1.0:
        print("✅ Excellent match - Very close to mgk.tif distribution")
    elif diff < 2.0:
        print("✅ Good match - Should improve accuracy")
    elif diff < 3.0:
        print("⚠️  Moderate match - May help but not optimal")
    else:
        print("❌ Large gap - May need more high-ZWNJ sources")

if __name__ == '__main__':
    main()
