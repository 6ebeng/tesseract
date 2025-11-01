#!/usr/bin/env python3
"""
Filter scraped corpus for high-quality Kurdish OCR training sentences.

Quality Criteria:
- ZWNJ density: 3-15% (looser than 8-12% to capture more)
- Sentence length: 8-30 words (focus on medium-long sentences)
- Kurdish script purity: >90%
- Remove duplicates
"""

import sys
from pathlib import Path
from collections import defaultdict
import hashlib

def calculate_zwnj_density(text):
    """Calculate ZWNJ density as percentage of total characters."""
    if not text:
        return 0.0
    zwnj_count = text.count('\u200c')
    return (zwnj_count / len(text)) * 100

def calculate_kurdish_purity(text):
    """Calculate Kurdish script percentage vs Latin."""
    kurdish_chars = 0
    latin_chars = 0
    
    for char in text:
        if '\u0600' <= char <= '\u06FF':  # Arabic/Kurdish range
            kurdish_chars += 1
        elif char.isalpha():
            latin_chars += 1
    
    total_alpha = kurdish_chars + latin_chars
    if total_alpha == 0:
        return 0.0
    return (kurdish_chars / total_alpha) * 100

def normalize_sentence(text):
    """Normalize sentence for duplicate detection."""
    # Remove extra whitespace and normalize
    normalized = ' '.join(text.split())
    return normalized.strip()

def hash_sentence(text):
    """Create hash for duplicate detection."""
    normalized = normalize_sentence(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def filter_corpus(input_dir, output_file, 
                  zwnj_min=3.0, zwnj_max=15.0,
                  length_min=8, length_max=30,
                  purity_min=90.0):
    """Filter corpus based on quality criteria."""
    
    seen_hashes = set()
    filtered_sentences = []
    stats = defaultdict(int)
    
    # Process all text files
    for txt_file in Path(input_dir).rglob('*.txt'):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                stats['total'] += 1
                
                # Check for duplicates
                sent_hash = hash_sentence(line)
                if sent_hash in seen_hashes:
                    stats['duplicate'] += 1
                    continue
                
                # Check word count
                words = line.split()
                word_count = len(words)
                if word_count < length_min or word_count > length_max:
                    stats['bad_length'] += 1
                    continue
                
                # Check ZWNJ density
                zwnj_density = calculate_zwnj_density(line)
                if zwnj_density < zwnj_min or zwnj_density > zwnj_max:
                    stats['bad_zwnj'] += 1
                    continue
                
                # Check script purity
                purity = calculate_kurdish_purity(line)
                if purity < purity_min:
                    stats['bad_purity'] += 1
                    continue
                
                # Passed all filters
                seen_hashes.add(sent_hash)
                filtered_sentences.append((line, word_count, zwnj_density, purity))
                stats['accepted'] += 1
    
    # Sort by ZWNJ density (highest first) to prioritize quality
    filtered_sentences.sort(key=lambda x: x[2], reverse=True)
    
    # Write filtered corpus
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sentence, word_count, zwnj_density, purity in filtered_sentences:
            f.write(sentence + '\n')
    
    # Print statistics
    print(f'Corpus Filtering Results:')
    print(f'=' * 60)
    print(f'Total sentences processed: {stats["total"]:,}')
    print(f'  Duplicates removed: {stats["duplicate"]:,}')
    print(f'  Bad length (not {length_min}-{length_max} words): {stats["bad_length"]:,}')
    print(f'  Bad ZWNJ density (not {zwnj_min}-{zwnj_max}%): {stats["bad_zwnj"]:,}')
    print(f'  Bad purity (<{purity_min}%): {stats["bad_purity"]:,}')
    print(f'  ACCEPTED: {stats["accepted"]:,}')
    print(f'')
    print(f'Acceptance rate: {(stats["accepted"]/stats["total"]*100):.2f}%')
    print(f'')
    print(f'Output written to: {output_path}')
    
    if filtered_sentences:
        avg_words = sum(s[1] for s in filtered_sentences) / len(filtered_sentences)
        avg_zwnj = sum(s[2] for s in filtered_sentences) / len(filtered_sentences)
        avg_purity = sum(s[3] for s in filtered_sentences) / len(filtered_sentences)
        print(f'')
        print(f'Filtered Corpus Quality:')
        print(f'  Avg Words/Sentence: {avg_words:.2f}')
        print(f'  Avg ZWNJ Density: {avg_zwnj:.2f}%')
        print(f'  Avg Kurdish Purity: {avg_purity:.2f}%')

if __name__ == '__main__':
    filter_corpus(
        input_dir='corpus',
        output_file='../../corpus/ckb_scraped_filtered.training_text',
        zwnj_min=2.0,   # More lenient to capture more sentences
        zwnj_max=15.0,
        length_min=6,   # Shorter for variety
        length_max=35,  # Longer sentences OK
        purity_min=90.0
    )
