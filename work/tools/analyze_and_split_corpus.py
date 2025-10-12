#!/usr/bin/env python3
"""Analyze and split corpus by script type (Arabic vs Latin)."""
import re
import sys

def analyze_script(line):
    """Analyze script composition of a line."""
    line = line.strip()
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', line))
    latin_chars = len(re.findall(r'[A-Za-z]', line))
    return arabic_chars, latin_chars

def main():
    corpus_file = '../corpus/ckb.training_text'
    
    # Read corpus
    with open(corpus_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Classify lines
    arabic_lines = []
    latin_lines = []
    mixed_lines = []
    
    arabic_only = latin_only = mixed = empty = 0
    
    for line in lines:
        arabic, latin = analyze_script(line)
        if arabic > 0 and latin == 0:
            arabic_only += 1
            arabic_lines.append(line)
        elif latin > 0 and arabic == 0:
            latin_only += 1
            latin_lines.append(line)
        elif arabic > 0 and latin > 0:
            mixed += 1
            mixed_lines.append(line)
        else:
            empty += 1
            arabic_lines.append(line)  # Keep punct/numbers with Arabic
    
    # Print statistics
    print(f'Total lines: {len(lines)}')
    print(f'Arabic-only: {arabic_only} ({100*arabic_only/len(lines):.1f}%)')
    print(f'Latin-only: {latin_only} ({100*latin_only/len(lines):.1f}%)')
    print(f'Mixed: {mixed} ({100*mixed/len(lines):.1f}%)')
    print(f'Punct/Empty: {empty} ({100*empty/len(lines):.1f}%)')
    print()
    
    # Write split files
    with open('../corpus/ckb_arabic.training_text', 'w', encoding='utf-8') as f:
        f.writelines(arabic_lines)
    print(f'✓ Wrote {len(arabic_lines)} Arabic lines to ckb_arabic.training_text')
    
    with open('../corpus/ckb_latin.training_text', 'w', encoding='utf-8') as f:
        f.writelines(latin_lines)
    print(f'✓ Wrote {len(latin_lines)} Latin lines to ckb_latin.training_text')
    
    with open('../corpus/ckb_mixed.training_text', 'w', encoding='utf-8') as f:
        f.writelines(mixed_lines)
    print(f'✓ Wrote {len(mixed_lines)} Mixed lines to ckb_mixed.training_text')

if __name__ == '__main__':
    main()
