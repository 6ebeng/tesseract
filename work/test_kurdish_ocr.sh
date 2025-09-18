#!/bin/sh

# Script to test the Kurdish OCR models

echo "=== Testing Kurdish OCR Models ==="
echo ""

WORK_DIR="$(pwd)/work"
TEST_DIR="$WORK_DIR/ocr-test"
FONTS_DIR="/root/.local/share/fonts/kurdish"

# Create test directory
mkdir -p "$TEST_DIR"

# Create a test image with Kurdish text
echo "Creating test image with Kurdish text..."

# Create test text
cat > "$TEST_DIR/test_text.txt" << 'EOF'
ئەم تاقیکردنەوەیەکە بۆ OCR کوردی
کوردستان وڵاتێکی جوانە
زمانی کوردی زمانێکی دەوڵەمەندە
EOF

# Generate test image using the working font
text2image \
    --text="$TEST_DIR/test_text.txt" \
    --outputbase="$TEST_DIR/kurdish_test" \
    --font="55_Sarchia_Kurdish" \
    --fonts_dir="$FONTS_DIR" \
    --resolution=300 \
    --ptsize=14 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$TEST_DIR/kurdish_test.tif" ]; then
    echo "✓ Test image created: $TEST_DIR/kurdish_test.tif"
    echo ""
    
    # Test with ckb model
    echo "Testing with ckb.traineddata model..."
    tesseract "$TEST_DIR/kurdish_test.tif" "$TEST_DIR/output_ckb" -l ckb --psm 6 2>/dev/null
    
    if [ -f "$TEST_DIR/output_ckb.txt" ]; then
        echo "OCR Output (ckb model):"
        echo "------------------------"
        cat "$TEST_DIR/output_ckb.txt"
        echo "------------------------"
    else
        echo "✗ OCR failed with ckb model"
    fi
    
    echo ""
    
    # Test with ckb_custom model if it exists
    if [ -f "$(pwd)/tessdata/ckb_custom.traineddata" ]; then
        echo "Testing with ckb_custom.traineddata model..."
        tesseract "$TEST_DIR/kurdish_test.tif" "$TEST_DIR/output_custom" -l ckb_custom --psm 6 2>/dev/null
        
        if [ -f "$TEST_DIR/output_custom.txt" ]; then
            echo "OCR Output (ckb_custom model):"
            echo "------------------------"
            cat "$TEST_DIR/output_custom.txt"
            echo "------------------------"
        else
            echo "✗ OCR failed with ckb_custom model"
        fi
    fi
    
    echo ""
    echo "Original text for comparison:"
    echo "------------------------"
    cat "$TEST_DIR/test_text.txt"
    echo "------------------------"
    
else
    echo "✗ Failed to create test image"
fi

echo ""
echo "Test complete!"
echo ""
echo "To test with your own images:"
echo "  tesseract your_image.png output -l ckb --psm 6"
echo ""
echo "Available models:"
ls -la "$(pwd)"/tessdata/ckb*.traineddata 2>/dev/null | awk '{print "  - " $9 " (" $5 " bytes)"}'
