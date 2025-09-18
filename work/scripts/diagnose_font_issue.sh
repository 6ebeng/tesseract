#!/bin/sh

# Diagnostic script to identify why fonts are failing

echo "=== Font Diagnostic Script ==="
echo ""

WORK_DIR="$(pwd)/work"
FONTS_PATH="$WORK_DIR/fonts"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
TEST_DIR="$WORK_DIR/font-test"

# Clean test directory
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# Create simple test text
cat > "$TEST_DIR/test.txt" << 'EOF'
test
ئەم تاقیکردنەوەیەکە
کوردی
EOF

echo "Step 1: Checking text2image availability"
if command -v text2image >/dev/null 2>&1; then
    echo "✓ text2image found"
    text2image --version 2>&1 | head -1
else
    echo "✗ text2image not found"
    exit 1
fi
echo ""

echo "Step 2: List available fonts that text2image can see"
echo "Running: text2image --list_available_fonts --fonts_dir=$FONTS_PATH"
echo "----------------------------------------"
text2image --list_available_fonts --fonts_dir="$FONTS_PATH" 2>&1 | head -20
echo "----------------------------------------"
echo ""

echo "Step 3: Test with system fonts (should work)"
echo "Testing with 'Arial' (system font)..."
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/arial_test" \
    --font="Arial" \
    --lang=ara \
    --linedata_only \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$TEST_DIR/arial_test.tif" ]; then
    echo "✓ System font test successful"
else
    echo "✗ System font test failed - text2image may have issues"
fi
echo ""

echo "Step 4: Test specific Kurdish fonts with different methods"
echo ""

# Test a few specific fonts
TEST_FONTS="00_Sarchia_ABC.ttf abdakre.ttf KGoran.ttf UniQAIDAR_Ali.ttf"
SUCCESS_COUNT=0

for font_file in $TEST_FONTS; do
    if [ ! -f "$FONTS_PATH/$font_file" ]; then
        continue
    fi
    
    FONT_BASE=$(basename "$font_file" .ttf)
    echo "Testing font: $FONT_BASE"
    
    # Method 1: Full path to font file
    echo -n "  Method 1 (full path): "
    text2image \
        --text="$TEST_DIR/test.txt" \
        --outputbase="$TEST_DIR/test1" \
        --font="$FONTS_PATH/$font_file" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "$TEST_DIR/test1.tif" ]; then
        echo "✓ SUCCESS"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        rm -f "$TEST_DIR/test1"*
    else
        echo "✗ Failed"
    fi
    
    # Method 2: Font name without extension
    echo -n "  Method 2 (name only): "
    text2image \
        --text="$TEST_DIR/test.txt" \
        --outputbase="$TEST_DIR/test2" \
        --font="$FONT_BASE" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "$TEST_DIR/test2.tif" ]; then
        echo "✓ SUCCESS"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        rm -f "$TEST_DIR/test2"*
    else
        echo "✗ Failed"
    fi
    
    # Method 3: Clean name (remove prefix and underscores)
    CLEAN_NAME=$(echo "$FONT_BASE" | sed 's/^[0-9]*_//' | sed 's/_/ /g')
    echo -n "  Method 3 (clean name '$CLEAN_NAME'): "
    text2image \
        --text="$TEST_DIR/test.txt" \
        --outputbase="$TEST_DIR/test3" \
        --font="$CLEAN_NAME" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "$TEST_DIR/test3.tif" ]; then
        echo "✓ SUCCESS"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        rm -f "$TEST_DIR/test3"*
    else
        echo "✗ Failed"
    fi
    
    echo ""
done

echo "Step 5: Test with explicit font list file"
# Create a font list file
ls "$FONTS_PATH"/*.ttf > "$TEST_DIR/fontlist.txt" 2>/dev/null
FONT_COUNT=$(wc -l < "$TEST_DIR/fontlist.txt")
echo "Created font list with $FONT_COUNT fonts"
echo ""

echo "Step 6: Check font file permissions"
FIRST_FONT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | head -1)
if [ -n "$FIRST_FONT" ]; then
    ls -la "$FIRST_FONT"
fi
echo ""

echo "Step 7: Test with verbose output to see actual error"
echo "Testing with verbose output..."
VERBOSE_FONT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | head -1)
if [ -n "$VERBOSE_FONT" ]; then
    VERBOSE_BASE=$(basename "$VERBOSE_FONT" .ttf)
    echo "Font: $VERBOSE_BASE"
    echo "Command output:"
    text2image \
        --text="$TEST_DIR/test.txt" \
        --outputbase="$TEST_DIR/verbose_test" \
        --font="$VERBOSE_FONT" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 2>&1 | head -10
fi
echo ""

echo "=== Diagnostic Summary ==="
echo "Successful font tests: $SUCCESS_COUNT"
echo ""

if [ $SUCCESS_COUNT -eq 0 ]; then
    echo "ISSUE IDENTIFIED: Fonts cannot be loaded by text2image"
    echo ""
    echo "Possible solutions:"
    echo "1. Install fonts to system: sudo cp $FONTS_PATH/*.ttf /usr/share/fonts/truetype/"
    echo "2. Update font cache: sudo fc-cache -fv"
    echo "3. Use full paths to font files instead of font names"
    echo "4. Check if fonts are corrupted"
else
    echo "Some fonts are working. The issue may be with specific font files or naming."
fi

echo ""
echo "Next steps:"
echo "1. Try installing fonts to system directory"
echo "2. Or modify the training script to use full font paths"
