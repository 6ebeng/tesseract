#!/usr/bin/env python3
"""
Build Kurdish word frequency dictionary from training corpus
For use in spell-checking and post-processing
"""

import sys
import re
from collections import Counter
import json

def extract_words(corpus_file):
    """
    Extract all words from corpus with frequency counts
    
    Returns:
        Counter with word frequencies
    """
    
    word_freq = Counter()
    total_lines = 0
    
    # Kurdish word pattern (letters, digits, some punctuation)
    word_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u200C]+')
    
    with open(corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            total_lines += 1
            
            # Extract Kurdish words
            words = word_pattern.findall(line)
            
            # Normalize and count
            for word in words:
                # Skip very short words (1-2 chars)
                if len(word) < 3:
                    continue
                
                # Normalize spaces/ZWNJ
                word = word.strip()
                if word:
                    word_freq[word] += 1
    
    return word_freq, total_lines

def build_dictionary(corpus_file, output_file, min_frequency=2, max_words=50000):
    """
    Build Kurdish dictionary from corpus
    
    Args:
        corpus_file: Input training corpus
        output_file: Output JSON dictionary file
        min_frequency: Minimum word frequency to include
        max_words: Maximum words in dictionary
    """
    
    print(f"Building Kurdish dictionary from: {corpus_file}")
    print(f"Minimum frequency: {min_frequency}")
    print(f"Maximum words: {max_words}")
    print()
    
    # Extract words
    word_freq, total_lines = extract_words(corpus_file)
    
    print(f"Analyzed {total_lines:,} lines")
    print(f"Found {len(word_freq):,} unique words")
    print()
    
    # Filter by frequency
    filtered = {word: count for word, count in word_freq.items() 
                if count >= min_frequency}
    
    print(f"After filtering (≥{min_frequency}): {len(filtered):,} words")
    
    # Sort by frequency and limit
    sorted_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_words) > max_words:
        sorted_words = sorted_words[:max_words]
    
    final_dict = dict(sorted_words)
    
    print(f"Final dictionary: {len(final_dict):,} words")
    print()
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dictionary saved to: {output_file}")
    print()
    
    # Report top words
    print("Top 30 most frequent words:")
    print("="*50)
    for i, (word, count) in enumerate(sorted_words[:30], 1):
        print(f"{i:2d}. {word:20s} : {count:4,} occurrences")
    
    return final_dict

def load_dictionary(dict_file):
    """Load Kurdish dictionary from JSON"""
    with open(dict_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == '__main__':
    corpus_file = '../corpus/ckb_phase6_batch2.training_text'
    output_file = '../corpus/kurdish_dictionary.json'
    
    if len(sys.argv) > 1:
        corpus_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    try:
        dictionary = build_dictionary(corpus_file, output_file, min_frequency=2)
        
        print("\n" + "="*70)
        print("DICTIONARY STATISTICS")
        print("="*70)
        print(f"Total unique words: {len(dictionary):,}")
        print(f"Total occurrences:  {sum(dictionary.values()):,}")
        print(f"Average frequency:  {sum(dictionary.values())/len(dictionary):.1f}")
        print()
        
    except FileNotFoundError:
        print(f"Error: Corpus file not found: {corpus_file}")
        sys.exit(1)
