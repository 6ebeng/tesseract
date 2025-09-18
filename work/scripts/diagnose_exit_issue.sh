#!/bin/sh

# Diagnostic script to find why the script exits at 0%
# This will help identify the exact cause

echo "=== Diagnostic Script for Exit Issue ==="
echo ""

# Test 1: Check if we can even start
echo "Test 1: Basic script execution"
echo "Script is running..."
echo ""

# Test 2: Check environment
echo "Test 2: Environment check"
WORK_DIR="$(pwd)/work"
echo "Work directory: $WORK_DIR"
echo "Current directory: $(pwd)"
echo ""

# Test 3: Check if fonts directory exists
echo "Test 3: Fonts directory"
FONTS_PATH="$WORK_DIR/fonts"
if [ -d "$FONTS_PATH" ]; then
    echo "✓ Fonts directory exists"
    FONT_COUNT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | wc -l)
    echo "  Found $FONT_COUNT .ttf files"
else
    echo "✗ Fonts directory not found!"
fi
echo ""

# Test 4: Check first font specifically
echo "Test 4: First font check"
FIRST_FONT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | head -1)
if [ -n "$FIRST_FONT" ] && [ -f "$FIRST_FONT" ]; then
    echo "First font: $(basename "$FIRST_FONT")"
    echo "File exists: Yes"
    echo "File readable: $([ -r "$FIRST_FONT" ] && echo "Yes" || echo "No")"
else
    echo "✗ No first font found or not readable"
fi
echo ""

# Test 5: Test the for loop itself
echo "Test 5: For loop test (should show 5 fonts)"
COUNT=0
for font in "$FONTS_PATH"/*.ttf; do
    COUNT=$((COUNT + 1))
    echo "  Loop iteration $COUNT: $(basename "$font" 2>/dev/null || echo "ERROR")"
    if [ $COUNT -ge 5 ]; then
        break
    fi
done
echo "Loop completed with $COUNT iterations"
echo ""

# Test 6: Test with explicit continuation
echo "Test 6: Loop with error handling"
COUNT=0
for font in "$FONTS_PATH"/*.ttf; do
    COUNT=$((COUNT + 1))
    
    # This should not cause exit
    if [ ! -f "$font" ]; then
        echo "  Font $COUNT: File not found (continuing...)"
        continue
    fi
    
    echo "  Font $COUNT: $(basename "$font") - OK"
    
    # Simulate an error that shouldn't stop the loop
    false || true  # This command fails but we continue
    
    if [ $COUNT -ge 3 ]; then
        echo "  (Stopping at 3 for test)"
        break
    fi
done
echo "Completed $COUNT iterations without exiting"
echo ""

# Test 7: Check if the issue is with printf/echo
echo "Test 7: Output commands"
echo "  Testing echo: OK"
printf "  Testing printf: OK\n"
echo ""

# Test 8: Test percentage calculation
echo "Test 8: Percentage calculation"
FONT_INDEX=1
MAX_FONTS=670
PERCENT=$((FONT_INDEX * 100 / MAX_FONTS))
echo "  For font 1 of 670: $PERCENT%"
echo ""

# Test 9: Check corpus file
echo "Test 9: Corpus file check"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
if [ -f "$CORPUS_FILE" ]; then
    echo "✓ Corpus file exists"
    LINES=$(wc -l < "$CORPUS_FILE" 2>/dev/null || echo "0")
    echo "  Lines: $LINES"
else
    echo "✗ Corpus file not found"
fi
echo ""

# Test 10: Test text2image availability
echo "Test 10: text2image command"
if command -v text2image >/dev/null 2>&1; then
    echo "✓ text2image is available"
    # Try to get version without it hanging
    timeout 2 text2image --version 2>&1 | head -1 || echo "  (version check timed out)"
else
    echo "✗ text2image not found"
fi
echo ""

# Test 11: Create a minimal loop that definitely works
echo "Test 11: Minimal working loop"
echo "Processing mock fonts..."
for i in 1 2 3 4 5; do
    PERCENT=$((i * 100 / 5))
    echo "[$PERCENT%] Processing mock font $i/5"
    # Simulate some work
    sleep 0.1 2>/dev/null || true
done
echo "Mock loop completed successfully"
echo ""

# Test 12: Check if the issue is with the specific font name
echo "Test 12: Font name processing"
TEST_FONT="00_Sarchia_ABC.ttf"
echo "Original: $TEST_FONT"
CLEAN_NAME=$(echo "$TEST_FONT" | sed 's/\.ttf$//' | sed 's/^[0-9]*_//' | sed 's/_/ /g')
echo "Cleaned: $CLEAN_NAME"
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "If this script completes without exiting early, the issue is likely:"
echo "1. In the text2image command itself"
echo "2. With 'set -e' causing exit on first error"
echo "3. With the specific processing of the first font"
echo ""
echo "Next step: Run the simple batch script:"
echo "  wsl sh work/scripts/simple_batch_train.sh"
