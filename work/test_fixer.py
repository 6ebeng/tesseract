#!/usr/bin/env python3
# Test if the fixer preserves ZWNJ
import sys
sys.path.insert(0, '/mnt/c/tesseract/work')
from kurdish_character_fixer import KurdishCharacterFixer

# Test text with ZWNJs
test_text = "مه‌لای گه‌وره‌ ناوی ته‌واوی"  # Contains ZWNJs
print("Original text ZWNJ count:", test_text.count('\u200c'))
print("Original text:", repr(test_text))

fixer = KurdishCharacterFixer()
fixed = fixer.fix_kurdish_text(test_text)

print("\nFixed text ZWNJ count:", fixed.count('\u200c'))
print("Fixed text:", repr(fixed))

if fixed.count('\u200c') > 0:
    print("\n✅ SUCCESS: ZWNJ preserved!")
else:
    print("\n❌ PROBLEM: ZWNJ stripped by fixer!")
