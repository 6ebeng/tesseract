#!/usr/bin/env python3
# Quick check for ZWNJ in normalized corpus
text = open("/mnt/c/tesseract/work/training_output/tmp/ckb.training_text.norm", "r", encoding="utf-8").read()
zwnj_count = text.count('\u200c')
total = len(text)
pct = (zwnj_count / total * 100) if total > 0 else 0

print(f"ZWNJ in normalized corpus: {zwnj_count}")
print(f"Total characters: {total}")
print(f"Percentage: {pct:.2f}%")
print(f"Expected: ~8,000 ZWNJs (7-8%)")

if zwnj_count > 7000:
    print("Status: ✅ EXCELLENT - ZWNJ preserved!")
elif zwnj_count > 1000:
    print("Status: ⚠️ LOW - Some ZWNJs present but not enough")
else:
    print("Status: ❌ PROBLEM - ZWNJ still being stripped!")
