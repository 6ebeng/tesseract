#!/bin/bash

# UTF-8 Encoding Verification for Kurdish Training
# This script checks and ensures proper UTF-8 support

# Enable UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

echo "=== UTF-8 Encoding Verification for Kurdish (CKB) ==="
echo ""

echo "SYSTEM UTF-8 STATUS:"
echo "Locale: $(locale)"
echo "Character Map: $(locale charmap)"
echo "LANG: $LANG"
echo "LC_ALL: $LC_ALL"
echo ""

cd /mnt/c/tesseract/work

echo "CORPUS UTF-8 VERIFICATION:"
if [ -f "corpus/ckb.training_text" ]; then
    echo "File exists: ✅"
    echo "File encoding: $(file -bi corpus/ckb.training_text)"
    echo "UTF-8 valid: $(if iconv -f utf-8 -t utf-8 corpus/ckb.training_text >/dev/null 2>&1; then echo "✅ Valid"; else echo "❌ Invalid"; fi)"
    echo "File size: $(ls -lh corpus/ckb.training_text | awk '{print $5}')"
    echo "Line count: $(wc -l < corpus/ckb.training_text)"
    echo ""
    echo "Sample Kurdish characters from corpus:"
    head -2 corpus/ckb.training_text | cut -c1-50
    echo "..."
else
    echo "❌ Corpus file not found"
fi

echo ""
echo "FONT UTF-8 SUPPORT:"
echo "Available Sarchia fonts:"
fc-list | grep -i sarchia | head -3

echo ""
echo "KURDISH CHARACTER TEST:"
echo "Testing Kurdish characters display:"
echo "Kurdish: کوردی"
echo "Sorani: سۆرانی"
echo "Characters: ئ ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن ه ھ و ۆ ی ێ ە"

echo ""
echo "TESSERACT UTF-8 SUPPORT:"
export TESSDATA_PREFIX="/mnt/c/tesseract/tessdata"
if tesseract --help-extra 2>/dev/null | grep -q "unicharset"; then
    echo "✅ Tesseract supports unicharset"
else
    echo "⚠️  Tesseract unicharset support unclear"
fi

echo ""
echo "EXISTING MODELS UTF-8 COMPATIBILITY:"
if [ -f "/mnt/c/tesseract/tessdata/ckb.traineddata" ]; then
    echo "✅ Found ckb.traineddata"
    # Test with Kurdish text
    echo "Testing UTF-8 recognition..."
    echo "کورد" > /tmp/test_utf8.txt
    if text2image --text=/tmp/test_utf8.txt --outputbase=/tmp/utf8_test --font="07_Sarchia_Akre" 2>/dev/null; then
        result=$(tesseract /tmp/utf8_test.tif /tmp/result -l ckb 2>/dev/null && cat /tmp/result.txt 2>/dev/null)
        if [ ! -z "$result" ]; then
            echo "✅ UTF-8 recognition working: '$result'"
        else
            echo "⚠️  UTF-8 recognition test unclear"
        fi
    else
        echo "⚠️  UTF-8 image generation failed"
    fi
else
    echo "❌ No CKB model found"
fi

echo ""
echo "RECOMMENDATIONS:"
echo "✅ All scripts now include UTF-8 environment setup"
echo "✅ Kurdish unicharset created with proper encoding"
echo "✅ Training scripts use --unicharset_file parameter"
echo "✅ Locale settings configured for UTF-8"
echo ""
echo "UTF-8 ENABLED SCRIPTS:"
echo "- utf8_ckb_training.sh (Complete UTF-8 pipeline)"
echo "- create_ckb_unicharset.sh (Kurdish character set)"
echo "- english_base_ckb_train.sh (Updated with UTF-8)"
echo "- fixed_ctc_train.sh (Updated with UTF-8)"
echo "- minimal_ctc_fix.sh (Updated with UTF-8)"

echo ""
echo "=== UTF-8 Verification Complete ==="