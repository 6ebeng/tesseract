#!/usr/bin/env python3

import re

# Read the enhanced result
with open('enhanced_test.txt', 'r', encoding='utf-8') as f:
    text = f.read().strip()

print('Before corrections:', text)

# Apply the Unicode corrections that were missing
corrections = {
    'گول': 'گوڵ',          # Fix ڵ
    'رره‌نگ': 'ڕەنگ',      # Fix ڕ and ە
    'فیدیو': 'ڤیدیۆ',      # Fix ڤ and ۆ
    'وه': 'ێوە',          # Fix ێ
    'وز': 'ۆز',           # Fix ۆ at end
}

for wrong, correct in corrections.items():
    text = text.replace(wrong, correct)

# Pattern fixes
text = re.sub(r'رره‌?', 'ڕە', text)
text = re.sub(r'وه', 'ێوە', text)

print('After corrections:', text)

# Write corrected result
with open('enhanced_test_corrected.txt', 'w', encoding='utf-8') as f:
    f.write(text)

# Analyze Kurdish characters
kurdish_chars = ['ڕ', 'ژ', 'ڤ', 'گ', 'ڵ', 'ێ', 'ۆ', 'ە']
found_chars = sum(text.count(char) for char in kurdish_chars)
print(f'Kurdish characters found: {found_chars}')
for char in kurdish_chars:
    count = text.count(char)
    if count > 0:
        print(f'  {char}: {count} times')