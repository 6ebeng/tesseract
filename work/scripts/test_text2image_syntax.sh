#!/bin/sh

# Test script to find the correct text2image syntax

echo "=== Testing text2image Syntax ==="
echo ""

WORK_DIR="$(pwd)/work"
FONTS_PATH="$WORK_DIR/fonts"
TEST_DIR="$WORK_DIR/syntax-test"

# Clean test directory
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# Create simple test text
cat > "$TEST_DIR/test.txt" << 'EOF'
test
ئەم تاقیکردنەوەیەکە
کوردی
EOF

echo "Step 1: Check text2image help for correct syntax"
echo "----------------------------------------"
text2image --help 2>&1 | grep -E "(lang|font|output)" | head -20
echo "----------------------------------------"
echo ""

echo "Step 2: Test different syntax variations"
echo ""

FIRST_FONT="$FONTS_PATH/00_Sarchia_ABC.ttf"

# Test 1: Without --lang flag
echo "Test 1: Without --lang flag"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/test1" \
    --font="$FIRST_FONT" \
    --fonts_dir="$FONTS_PATH" \
    --linedata_only \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$TEST_DIR/test1.tif" ]; then
    echo "✓ SUCCESS - Works without --lang flag"
else
    echo "✗ Failed"
fi
echo ""

# Test 2: With -l instead of --lang
echo "Test 2: With -l flag"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/test2" \
    --font="$FIRST_FONT" \
    --fonts_dir="$FONTS_PATH" \
    -l ara \
    --linedata_only \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$TEST_DIR/test2.tif" ]; then
    echo "✓ SUCCESS - Works with -l ara"
else
    echo "✗ Failed"
fi
echo ""

# Test 3: Without linedata_only
echo "Test 3: Without --linedata_only"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/test3" \
    --font="$FIRST_FONT" \
    --fonts_dir="$FONTS_PATH" \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$TEST_DIR/test3.tif" ]; then
    echo "✓ SUCCESS - Works without --linedata_only"
else
    echo "✗ Failed"
fi
echo ""

# Test 4: Minimal command
echo "Test 4: Minimal command"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/test4" \
    --font="$FIRST_FONT" >/dev/null 2>&1

if [ -f "$TEST_DIR/test4.tif" ]; then
    echo "✓ SUCCESS - Works with minimal options"
else
    echo "✗ Failed"
fi
echo ""

# Test 5: With font name only (not full path)
echo "Test 5: With font name from fonts_dir"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/test5" \
    --font="Sarchia ABC" \
    --fonts_dir="$FONTS_PATH" >/dev/null 2>&1

if [ -f "$TEST_DIR/test5.tif" ]; then
    echo "✓ SUCCESS - Works with font name"
else
    echo "✗ Failed"
fi
echo ""

# Test 6: Show actual error message
echo "Step 3: Show actual error with verbose output"
echo "Command being run:"
echo "text2image --text=\"$TEST_DIR/test.txt\" --outputbase=\"$TEST_DIR/verbose\" --font=\"$FIRST_FONT\" --fonts_dir=\"$FONTS_PATH\""
echo ""
echo "Output:"
text2image \
    --text="$TEST_DIR/test.txt" \
    --outputbase="$TEST_DIR/verbose" \
    --font="$FIRST_FONT" \
    --fonts_dir="$FONTS_PATH" 2>&1

echo ""
echo "=== Summary ==="
ls -la "$TEST_DIR"/*.tif 2>/dev/null || echo "No .tif files generated"
echo ""

# Check if any test succeeded
if ls "$TEST_DIR"/*.tif >/dev/null 2>&1; then
    echo "✓ At least one syntax variation worked!"
    echo "The working syntax should be used in the training script."
else
    echo "✗ All syntax variations failed."
    echo "There may be an issue with the font files or text2image installation."
fi
