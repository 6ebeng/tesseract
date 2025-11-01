#!/usr/bin/env python3
"""Analyze ZWNJ (U+200C) and Tatweel (U+0640) usage in corpus files."""

import sys
import os

def analyze_unicode_chars(filename):
    """Analyze special Unicode character usage in a corpus file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        total_chars = len(content)
        lines = content.split('\n')
        sentence_count = len([l for l in lines if l.strip()])
        
        zwnj_count = content.count('\u200c')  # Zero Width Non-Joiner
        tatweel_count = content.count('\u0640')  # Arabic Tatweel (kashida)
        
        # Calculate percentages
        zwnj_pct = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
        tatweel_pct = (tatweel_count / total_chars * 100) if total_chars > 0 else 0
        
        # Count sentences with these characters
        zwnj_sentences = sum(1 for line in lines if '\u200c' in line)
        tatweel_sentences = sum(1 for line in lines if '\u0640' in line)
        
        print(f'📄 {os.path.basename(filename)}:')
        print(f'   Total chars: {total_chars:,}')
        print(f'   Sentences: {sentence_count:,}')
        print(f'   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'   ZWNJ (U+200C):')
        print(f'     Count: {zwnj_count:,} ({zwnj_pct:.3f}% of chars)')
        print(f'     In sentences: {zwnj_sentences:,} ({zwnj_sentences/sentence_count*100:.1f}%)')
        print(f'   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        print(f'   Tatweel (U+0640):')
        print(f'     Count: {tatweel_count:,} ({tatweel_pct:.3f}% of chars)')
        print(f'     In sentences: {tatweel_sentences:,} ({tatweel_sentences/sentence_count*100:.1f}%)')
        print()
        
        return {
            'filename': filename,
            'total_chars': total_chars,
            'sentences': sentence_count,
            'zwnj_count': zwnj_count,
            'zwnj_pct': zwnj_pct,
            'tatweel_count': tatweel_count,
            'tatweel_pct': tatweel_pct
        }
    except Exception as e:
        print(f'❌ Error reading {filename}: {e}')
        return None

def main():
    """Main analysis function."""
    corpus_dir = '/mnt/c/tesseract/work/corpus'
    
    # Analyze all batch files
    files = [
        'ckb_scraped_filtered.training_text',
        'ckb_wikipedia_bio_filtered.training_text',
        'ckb_phase6_batch3.training_text',
        'ckb_phase6_batch4.training_text'
    ]
    
    print('='*60)
    print('UNICODE CHARACTER ANALYSIS: ZWNJ vs TATWEEL')
    print('='*60)
    print()
    
    results = []
    for filename in files:
        filepath = os.path.join(corpus_dir, filename)
        if os.path.exists(filepath):
            result = analyze_unicode_chars(filepath)
            if result:
                results.append(result)
    
    # Summary
    if results:
        print('='*60)
        print('SUMMARY')
        print('='*60)
        print(f"{'Corpus':<40} {'ZWNJ %':>10} {'Tatweel %':>10}")
        print('-'*60)
        for r in results:
            basename = os.path.basename(r['filename'])
            print(f"{basename:<40} {r['zwnj_pct']:>9.3f}% {r['tatweel_pct']:>9.3f}%")

if __name__ == '__main__':
    main()
