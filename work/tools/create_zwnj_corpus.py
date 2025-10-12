#!/usr/bin/env python3
"""
Create ZWNJ-focused training corpus to address the critical ZWNJ shortage.
Current: 0.17% ZWNJ | Target: 5-10% ZWNJ
"""

import sys
import random

def create_zwnj_training_corpus():
    """Create comprehensive ZWNJ training data."""
    
    # Read ZWNJ-rich words from extracted list
    with open('/mnt/c/tesseract/work/corpus/zwnj_rich_words.txt', 'r', encoding='utf-8') as f:
        zwnj_words = [line.strip() for line in f if line.strip() and len(line.strip()) > 2]
    
    print(f"Loaded {len(zwnj_words)} ZWNJ-rich words")
    
    lines = []
    
    # Strategy 1: Individual word repetition (high frequency)
    print("Creating individual word repetitions...")
    for word in zwnj_words:
        # Repeat each word 10 times (for common words)
        for _ in range(10):
            lines.append(word)
    
    # Strategy 2: Two-word phrases
    print("Creating two-word phrases...")
    for i in range(len(zwnj_words) - 1):
        phrase = f"{zwnj_words[i]} {zwnj_words[i+1]}"
        for _ in range(3):
            lines.append(phrase)
    
    # Strategy 3: Three-word phrases
    print("Creating three-word phrases...")
    for i in range(len(zwnj_words) - 2):
        phrase = f"{zwnj_words[i]} {zwnj_words[i+1]} {zwnj_words[i+2]}"
        for _ in range(2):
            lines.append(phrase)
    
    # Strategy 4: Random combinations (simulate natural text)
    print("Creating random combinations...")
    for _ in range(500):
        num_words = random.randint(3, 7)
        phrase = ' '.join(random.choice(zwnj_words) for _ in range(num_words))
        lines.append(phrase)
    
    # Strategy 5: Focused on most common problematic words
    print("Adding high-frequency problematic words...")
    problematic_words = [
        "مه‌لای",  # mela
        "گه‌وره‌",  # big
        "بنه‌ماڵه‌",  # family
        "هه‌بوو",  # had
        "له‌",  # in/from
        "به‌",  # to/with
        "زانایه‌كی",  # scientist
        "ئایینی",  # religious
        "چاكسازو",  # reformist
        "ته‌واوی",  # complete
        "جه‌لیزاده‌",  # family name
    ]
    
    for word in problematic_words:
        for _ in range(30):  # 30 repetitions each
            lines.append(word)
    
    # Shuffle to avoid patterns
    random.shuffle(lines)
    
    # Write to file
    output_file = '/mnt/c/tesseract/work/corpus/ckb_zwnj_focused.training_text'
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    
    # Calculate statistics
    full_text = '\n'.join(lines)
    zwnj_count = full_text.count('\u200c')
    total_chars = len(full_text)
    zwnj_percentage = (zwnj_count / total_chars) * 100 if total_chars > 0 else 0
    
    print(f"\n✅ Created ZWNJ-focused training corpus:")
    print(f"   File: {output_file}")
    print(f"   Lines: {len(lines)}")
    print(f"   Total characters: {total_chars}")
    print(f"   ZWNJ count: {zwnj_count}")
    print(f"   ZWNJ percentage: {zwnj_percentage:.2f}%")
    print(f"   Words: {len(full_text.split())}")
    
    return len(lines), zwnj_count, total_chars

if __name__ == '__main__':
    try:
        lines, zwnj_count, total_chars = create_zwnj_training_corpus()
        print(f"\n✅ SUCCESS: Created {lines} training lines with {zwnj_count} ZWNJ characters")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
