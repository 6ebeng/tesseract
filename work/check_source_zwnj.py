#!/usr/bin/env python3
# Check ZWNJ in source corpus
ckb_text = open('/mnt/c/tesseract/work/corpus/ckb.training_text', 'r', encoding='utf-8').read()
zwnj_count = ckb_text.count('\u200c')
total_chars = len(ckb_text)

print(f"Source: ckb.training_text")
print(f"ZWNJ count: {zwnj_count}")
print(f"Total characters: {total_chars}")
print(f"Percentage: {(zwnj_count/total_chars*100):.2f}%")
print(f"Expected: ~8,309 (7.77%)")
