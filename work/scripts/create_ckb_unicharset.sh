#!/bin/bash

# Kurdish Unicharset Generator with UTF-8 Support
# This script creates a proper unicharset for Kurdish (CKB) characters

# Enable UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

echo "=== Creating Kurdish (CKB) Unicharset with UTF-8 Support ==="

cd /mnt/c/tesseract/work
mkdir -p output

# Create comprehensive Kurdish character list
cat > output/ckb.charset << 'EOF'
ئ
ا
ب
پ
ت
ج
چ
ح
خ
د
ر
ڕ
ز
ژ
س
ش
ع
غ
ف
ڤ
ق
ک
گ
ل
ڵ
م
ن
ه
ھ
و
ۆ
ووو
ی
ێ
ە
.
،
؟
!
:
;
"
'
(
)
-
0
1
2
3
4
5
6
7
8
9
 
EOF

echo "=== Generating Unicharset File ==="

# Create proper unicharset with UTF-8 encoding
cat > output/ckb.unicharset << 'EOF'
##
# Unicharset file for Kurdish (Central Kurdish - Sorani)
# Generated with UTF-8 encoding support
##

NULL 0 NULL 0
JOIN 1 NULL 0
SPACE 2 NULL 0

# Kurdish letters
ئ 3 NULL 0
ا 4 NULL 0
ب 5 NULL 0
پ 6 NULL 0
ت 7 NULL 0
ج 8 NULL 0
چ 9 NULL 0
ح 10 NULL 0
خ 11 NULL 0
د 12 NULL 0
ر 13 NULL 0
ڕ 14 NULL 0
ز 15 NULL 0
ژ 16 NULL 0
س 17 NULL 0
ش 18 NULL 0
ع 19 NULL 0
غ 20 NULL 0
ف 21 NULL 0
ڤ 22 NULL 0
ق 23 NULL 0
ک 24 NULL 0
گ 25 NULL 0
ل 26 NULL 0
ڵ 27 NULL 0
م 28 NULL 0
ن 29 NULL 0
ه 30 NULL 0
ھ 31 NULL 0
و 32 NULL 0
ۆ 33 NULL 0
ووو 34 NULL 0
ی 35 NULL 0
ێ 36 NULL 0
ە 37 NULL 0

# Punctuation
. 38 NULL 0
، 39 NULL 0
؟ 40 NULL 0
! 41 NULL 0
: 42 NULL 0
; 43 NULL 0
" 44 NULL 0
' 45 NULL 0
( 46 NULL 0
) 47 NULL 0
- 48 NULL 0

# Numbers
0 49 NULL 0
1 50 NULL 0
2 51 NULL 0
3 52 NULL 0
4 53 NULL 0
5 54 NULL 0
6 55 NULL 0
7 56 NULL 0
8 57 NULL 0
9 58 NULL 0
EOF

echo "✅ Kurdish unicharset created with UTF-8 support"
echo "   File: output/ckb.unicharset"
echo "   Characters: $(wc -l < output/ckb.charset) Kurdish characters"
echo ""
echo "Usage in training:"
echo "   --unicharset_file=output/ckb.unicharset"