#!/bin/bash

# Simple UTF-8 Box File Creator and Validator
# This script creates and validates UTF-8 box files for Kurdish training

# Enable UTF-8 support
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LC_CTYPE=C.UTF-8

echo "=== UTF-8 Box File Creator for Kurdish ==="

cd /mnt/c/tesseract/work
mkdir -p output

echo "=== Creating simple Kurdish test set ==="
# Create simplified Kurdish corpus for better box alignment
cat > corpus/ckb.simple_utf8.txt << 'EOF'
کورد
کوردستان
نان
ئاو
ماڵ
باش
زۆر
کەم
گوڵ
ڕۆژ
شەو
مناڵ
دایک
باوک
ئەم
ئەو
هات
چوو
ڕەش
سپی
سوور
زەرد
شین
EOF

echo "=== Step 1: Generate UTF-8 Training Image ==="
text2image \
    --text=corpus/ckb.simple_utf8.txt \
    --outputbase=output/ckb.simple \
    --font="07_Sarchia_Akre" \
    --char_spacing=2.0 \
    --leading=16 \
    --resolution=300 \
    --margin=20

echo "=== Step 2: Create UTF-8 Box File ==="
export TESSDATA_PREFIX="/mnt/c/tesseract/tessdata"

# Generate box file with CKB model
tesseract output/ckb.simple.tif output/ckb.simple -l ckb --psm 6

echo "=== Step 3: Validate UTF-8 Box File ==="
if [ -f "output/ckb.simple.box" ]; then
    echo "✅ Box file created"
    echo "Box file size: $(ls -lh output/ckb.simple.box | awk '{print $5}')"
    echo "Number of characters: $(wc -l < output/ckb.simple.box)"
    
    # Show sample box content
    echo ""
    echo "Sample box file content:"
    head -10 output/ckb.simple.box
    
    # Validate UTF-8 encoding
    if iconv -f utf-8 -t utf-8 output/ckb.simple.box >/dev/null 2>&1; then
        echo "✅ Box file is valid UTF-8"
    else
        echo "⚠️  Box file encoding issue"
    fi
    
    echo "=== Step 4: Create Training File List ==="
    echo "ckb.simple" > output/training_files.txt
    echo "✅ Training list created"
    
    echo "=== Step 5: Test Recognition ==="
    # Test the recognition accuracy
    result=$(tesseract output/ckb.simple.tif output/ckb.simple_result -l ckb 2>/dev/null)
    if [ -f "output/ckb.simple_result.txt" ]; then
        echo "✅ Recognition test completed"
        echo "Original text (first 5 lines):"
        head -5 corpus/ckb.simple_utf8.txt
        echo ""
        echo "Recognition result:"
        head -5 output/ckb.simple_result.txt
    fi
    
else
    echo "❌ Box file creation failed"
fi

echo ""
echo "=== UTF-8 Box File Validation Complete ==="
echo "Files created:"
echo "- output/ckb.simple.tif (training image)"
echo "- output/ckb.simple.box (UTF-8 box file)"
echo "- output/ckb.simple.txt (recognition result)"
echo "- corpus/ckb.simple_utf8.txt (simplified corpus)"