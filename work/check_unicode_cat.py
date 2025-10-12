#!/usr/bin/env python3
import unicodedata

zwnj = '\u200c'
print(f"ZWNJ (U+200C) Unicode category: {unicodedata.category(zwnj)}")
print(f"")
print(f"Category meanings:")
print(f"  Cf = Format character")
print(f"  Mn = Nonspacing Mark")
print(f"")
print(f"Will be stripped by 'category != Mn' filter? NO (it's Cf, not Mn)")
print(f"But check drop_chars set!")
