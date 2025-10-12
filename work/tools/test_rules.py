#!/usr/bin/env python3
from kurdish_zwnj_rules import KurdishZWNJRules

rules = KurdishZWNJRules()

# Test cases without ZWNJ
test_cases = [
    "مهلای گهوره",
    "بهرههم",
    "لهناو",
    "زۆرتر",
]

print("Testing ه+consonant rule:")
print("=" * 60)

for test in test_cases:
    result, stats = rules.apply_all_rules(test)
    print(f"Input:  {test}")
    print(f"Output: {result}")
    print(f"Insertions: {stats['total_inserted']}")
    print()

# Now test on actual OCR snippet
with open('mgk_phase4.txt', 'r', encoding='utf-8') as f:
    ocr_sample = f.read()[:500]

result, stats = rules.apply_all_rules(ocr_sample)
print()
print("OCR Sample Test (first 500 chars):")
print("=" * 60)
print(f"Original ZWNJs: {stats['original_zwnj']}")
print(f"Inserted ZWNJs: {stats['total_inserted']}")
print()
print("Sample output:")
print(result[:300])
