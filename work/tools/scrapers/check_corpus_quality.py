import sys
import os
from pathlib import Path
import re

def analyze_corpus(corpus_dir):
    total_sentences = 0
    total_chars = 0
    total_words = 0
    zwnj_count = 0
    sentences_by_length = {'short': 0, 'medium': 0, 'long': 0, 'very_long': 0}
    kurdish_chars = 0
    latin_chars = 0
    
    for txt_file in Path(corpus_dir).rglob('*.txt'):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                total_sentences += 1
                total_chars += len(line)
                
                # Count ZWNJ (U+200C)
                zwnj_count += line.count('\u200c')
                
                # Count words
                words = line.split()
                word_count = len(words)
                total_words += word_count
                
                # Categorize by length
                if word_count < 5:
                    sentences_by_length['short'] += 1
                elif word_count < 15:
                    sentences_by_length['medium'] += 1
                elif word_count < 30:
                    sentences_by_length['long'] += 1
                else:
                    sentences_by_length['very_long'] += 1
                
                # Count Kurdish vs Latin characters
                for char in line:
                    if '\u0600' <= char <= '\u06FF':  # Arabic/Kurdish range
                        kurdish_chars += 1
                    elif char.isalpha():
                        latin_chars += 1
    
    print(f'Total Sentences: {total_sentences:,}')
    print(f'Total Characters: {total_chars:,}')
    print(f'Total Words: {total_words:,}')
    print(f'Avg Words/Sentence: {total_words/total_sentences:.2f}')
    print(f'Avg Chars/Sentence: {total_chars/total_sentences:.2f}')
    print(f'')
    print(f'ZWNJ Statistics:')
    print(f'  Total ZWNJ: {zwnj_count:,}')
    print(f'  ZWNJ Density: {(zwnj_count/total_chars)*100:.2f}%')
    print(f'  ZWNJ per Sentence: {zwnj_count/total_sentences:.2f}')
    print(f'')
    print(f'Sentence Length Distribution:')
    short_pct = sentences_by_length['short']/total_sentences*100
    medium_pct = sentences_by_length['medium']/total_sentences*100
    long_pct = sentences_by_length['long']/total_sentences*100
    vlong_pct = sentences_by_length['very_long']/total_sentences*100
    print(f'  Short (<5 words): {sentences_by_length["short"]:,} ({short_pct:.1f}%)')
    print(f'  Medium (5-14 words): {sentences_by_length["medium"]:,} ({medium_pct:.1f}%)')
    print(f'  Long (15-29 words): {sentences_by_length["long"]:,} ({long_pct:.1f}%)')
    print(f'  Very Long (30+ words): {sentences_by_length["very_long"]:,} ({vlong_pct:.1f}%)')
    print(f'')
    print(f'Script Purity:')
    total_alpha = kurdish_chars + latin_chars
    if total_alpha > 0:
        kurdish_pct = (kurdish_chars/total_alpha)*100
        latin_pct = (latin_chars/total_alpha)*100
        print(f'  Kurdish Script: {kurdish_pct:.2f}%')
        print(f'  Latin Script: {latin_pct:.2f}%')

if __name__ == '__main__':
    analyze_corpus('corpus')
