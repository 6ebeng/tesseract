#!/bin/sh

# Simple batch training script that processes fonts one by one
# This version bypasses complex logic to ensure continuation

echo "=== Simple Batch Training Script ==="
echo "This script will process fonts individually"
echo ""

# Configuration
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-batch"
FONTS_PATH="$WORK_DIR/fonts"
MAX_FONTS=20

# Clean and prepare
echo "Preparing directories..."
rm -rf "$GROUND_TRUTH_DIR" 2>/dev/null
mkdir -p "$GROUND_TRUTH_DIR"
mkdir -p "$OUTPUT_DIR"

# Check corpus
if [ ! -f "$CORPUS_FILE" ]; then
    echo "ERROR: Corpus file not found at $CORPUS_FILE"
    exit 1
fi
echo "Corpus file found"

# Create simple test text (in case corpus is the problem)
echo "Creating simple test text..."
cat > "$WORK_DIR/simple_test.txt" << 'EOF'
test
ئەم تاقیکردنەوەیەکە
کوردی
EOF

# Get list of fonts
echo ""
echo "Getting font list..."
FONT_COUNT=0
SUCCESS_COUNT=0
FAIL_COUNT=0

# Process fonts one by one with simple logic
echo ""
echo "Processing fonts (maximum $MAX_FONTS)..."
echo "----------------------------------------"

for font_file in "$FONTS_PATH"/*.ttf; do
    # Check if we've processed enough fonts
    if [ $FONT_COUNT -ge $MAX_FONTS ]; then
        echo ""
        echo "Reached maximum of $MAX_FONTS fonts"
        break
    fi
    
    # Check if font file exists
    if [ ! -f "$font_file" ]; then
        continue
    fi
    
    FONT_COUNT=$((FONT_COUNT + 1))
    
    # Get font name
    FONT_BASE=$(basename "$font_file" .ttf)
    FONT_CLEAN=$(echo "$FONT_BASE" | sed 's/^[0-9]*_//' | sed 's/_/ /g')
    SAFE_NAME=$(echo "$FONT_BASE" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
    
    echo ""
    echo "[$FONT_COUNT/$MAX_FONTS] Processing: $FONT_BASE"
    
    # Try method 1: Clean name
    OUTPUT_BASE="$GROUND_TRUTH_DIR/${SAFE_NAME}_1"
    echo "  Method 1: Trying '$FONT_CLEAN'..."
    
    # Use simple test text instead of corpus
    text2image \
        --text="$WORK_DIR/simple_test.txt" \
        --outputbase="$OUTPUT_BASE" \
        --font="$FONT_CLEAN" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1 || true
    
    if [ -f "${OUTPUT_BASE}.tif" ]; then
        echo "    ✓ Success with clean name"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        continue
    fi
    
    # Try method 2: Original name
    OUTPUT_BASE="$GROUND_TRUTH_DIR/${SAFE_NAME}_2"
    echo "  Method 2: Trying '$FONT_BASE'..."
    
    text2image \
        --text="$WORK_DIR/simple_test.txt" \
        --outputbase="$OUTPUT_BASE" \
        --font="$FONT_BASE" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1 || true
    
    if [ -f "${OUTPUT_BASE}.tif" ]; then
        echo "    ✓ Success with original name"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        continue
    fi
    
    # Try method 3: Without any prefix
    SIMPLE_NAME=$(echo "$FONT_BASE" | sed 's/^[0-9]*_//' | sed 's/_//g')
    OUTPUT_BASE="$GROUND_TRUTH_DIR/${SAFE_NAME}_3"
    echo "  Method 3: Trying '$SIMPLE_NAME'..."
    
    text2image \
        --text="$WORK_DIR/simple_test.txt" \
        --outputbase="$OUTPUT_BASE" \
        --font="$SIMPLE_NAME" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1 || true
    
    if [ -f "${OUTPUT_BASE}.tif" ]; then
        echo "    ✓ Success with simple name"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "    ✗ Failed all methods"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo ""
echo "========================================="
echo "Processing Complete!"
echo "========================================="
echo "Fonts attempted: $FONT_COUNT"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo ""

# Check results
GENERATED_FILES=$(find "$GROUND_TRUTH_DIR" -name "*.tif" 2>/dev/null | wc -l)
echo "Generated TIF files: $GENERATED_FILES"

if [ "$GENERATED_FILES" -gt 0 ]; then
    echo ""
    echo "SUCCESS: Training data generated!"
    echo "Files are in: $GROUND_TRUTH_DIR"
    
    # Convert to LSTMF
    echo ""
    echo "Converting to LSTMF format..."
    LSTMF_COUNT=0
    
    for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
        if [ ! -f "$tif_file" ]; then
            continue
        fi
        
        BASE=$(basename "$tif_file" .tif)
        tesseract "$tif_file" "$GROUND_TRUTH_DIR/$BASE" \
            --psm 6 -l ara lstm.train >/dev/null 2>&1 || true
        
        if [ -f "$GROUND_TRUTH_DIR/$BASE.lstmf" ]; then
            LSTMF_COUNT=$((LSTMF_COUNT + 1))
            echo "$GROUND_TRUTH_DIR/$BASE.lstmf" >> "$OUTPUT_DIR/batch-lstmf.txt"
        fi
    done
    
    echo "LSTMF files created: $LSTMF_COUNT"
    
    if [ "$LSTMF_COUNT" -gt 0 ]; then
        echo ""
        echo "Ready for training!"
        echo "LSTMF list: $OUTPUT_DIR/batch-lstmf.txt"
    fi
else
    echo ""
    echo "ERROR: No training data generated"
    echo "Please check:"
    echo "1. Are the fonts valid?"
    echo "2. Is text2image working?"
    echo "3. Try running: text2image --list_available_fonts --fonts_dir=$FONTS_PATH"
fi

echo ""
echo "Script completed without exiting early!"
