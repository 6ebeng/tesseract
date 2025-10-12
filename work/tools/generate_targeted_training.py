#!/usr/bin/env python3
"""
Generate targeted training data based on OCR error patterns
Creates synthetic training examples focusing on problematic character combinations
"""

import sys
import unicodedata
from collections import Counter

def normalize_text(text):
    """Normalize Kurdish text (remove ZWNJ, etc.)"""
    # Remove Zero-Width Non-Joiner (U+200C)
    text = text.replace('\u200c', '')
    # Normalize Unicode
    text = unicodedata.normalize('NFC', text)
    return text

def extract_character_ngrams(text, n=2):
    """Extract character n-grams from text"""
    ngrams = []
    for i in range(len(text) - n + 1):
        ngram = text[i:i+n]
        ngrams.append(ngram)
    return ngrams

def generate_training_data_from_errors(gt_file, ocr_file, output_file):
    """Generate targeted training data based on errors"""
    
    # Load files
    with open(gt_file, 'r', encoding='utf-8') as f:
        gt = normalize_text(f.read())
    
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr = normalize_text(f.read())
    
    print(f"Ground truth: {len(gt)} chars, {len(gt.split())} words")
    print(f"OCR output: {len(ocr)} chars, {len(ocr.split())} words")
    
    # Extract all bigrams and trigrams from ground truth
    bigrams = extract_character_ngrams(gt, 2)
    trigrams = extract_character_ngrams(gt, 3)
    
    # Count occurrences
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)
    
    # Get ground truth words
    gt_words = gt.split()
    word_counts = Counter(gt_words)
    
    # Extract problematic patterns
    # These are characters that commonly get confused
    problem_chars = {
        'ه': ['ە', 'ة'],  # heh vs kurdish heh
        'ك': ['ک'],       # arabic kaf vs kurdish kaf  
        'ی': ['ي', 'ى'],  # kurdish yeh vs arabic yeh
        'و': ['ۆ', 'وو'], # waw vs Kurdish oo/o
        'ئ': ['ا'],       # hamza on ya vs alef
        'گ': ['ك', 'ک'],  # gaf vs kaf
        'ڕ': ['ر'],       # reh with small v vs reh
        'ڵ': ['ل'],       # lam with small v vs lam
        'ێ': ['ی', 'ي'],  # yeh with hamza vs yeh
        'چ': ['ج'],       # tcheh vs jeem
        'پ': ['ب'],       # peh vs beh
        'ژ': ['ز'],       # jeh vs zain
        'ۆ': ['و'],       # Kurdish o vs waw
    }
    
    # Generate training lines
    training_lines = []
    
    # 1. Most common trigrams (these capture common patterns)
    print("\n=== Generating training data from common patterns ===")
    for trigram, count in trigram_counts.most_common(100):
        # Repeat based on frequency
        repeats = min(10, max(1, count // 5))
        for _ in range(repeats):
            # Generate a line with this trigram repeated
            line = ' '.join([trigram] * 5)
            training_lines.append(line)
    
    # 2. Common words (repeated based on frequency)
    print("=== Generating training data from common words ===")
    for word, count in word_counts.most_common(200):
        if len(word) >= 2:  # Skip single characters
            repeats = min(15, max(1, count // 2))
            for _ in range(repeats):
                training_lines.append(word)
    
    # 3. Problem character combinations
    print("=== Generating training data for confusable characters ===")
    for main_char, confusables in problem_chars.items():
        # Find all trigrams containing this character
        relevant_trigrams = [tg for tg in trigrams if main_char in tg]
        
        # Get top 20 most common
        relevant_counts = Counter(relevant_trigrams)
        for trigram, _ in relevant_counts.most_common(20):
            # Repeat many times to emphasize
            for _ in range(20):
                training_lines.append(trigram * 3)
                # Also add the trigram with spaces
                training_lines.append(f"{trigram} {trigram} {trigram}")
    
    # 4. All unique words from ground truth
    print("=== Adding all unique words ===")
    for word in set(gt_words):
        if len(word) >= 2:
            training_lines.append(word)
    
    # 5. Common phrases (consecutive words)
    print("=== Extracting common phrases ===")
    for i in range(len(gt_words) - 2):
        phrase = ' '.join(gt_words[i:i+3])
        if len(phrase) >= 10:  # Reasonable length
            training_lines.append(phrase)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_lines = []
    for line in training_lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in unique_lines:
            f.write(line + '\n')
    
    print(f"\n=== Summary ===")
    print(f"Generated {len(unique_lines)} training lines")
    print(f"Total words: {sum(len(line.split()) for line in unique_lines)}")
    print(f"Output: {output_file}")
    
    return unique_lines

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 generate_targeted_training.py <gt.txt> <ocr.txt> <output.txt>")
        sys.exit(1)
    
    gt_file = sys.argv[1]
    ocr_file = sys.argv[2]
    output_file = sys.argv[3]
    
    generate_training_data_from_errors(gt_file, ocr_file, output_file)

if __name__ == '__main__':
    main()
