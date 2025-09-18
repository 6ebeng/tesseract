#!/bin/sh

# Training script that uses font files directly with their full names

echo "=== Kurdish OCR Training with Direct Font Files ==="
echo ""

# Configuration
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-direct"
FONTS_DIR="/root/.local/share/fonts/kurdish"
FINAL_MODEL="$WORK_DIR/output/ckb.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb.traineddata"
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Training parameters
MAX_ITERATIONS=5000
TARGET_ERROR=0.01
DEBUG_INTERVAL=100

# Clean environment
echo "Preparing clean environment..."
rm -rf "$GROUND_TRUTH_DIR"
mkdir -p "$GROUND_TRUTH_DIR"
mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/ckb*.checkpoint
rm -f "$OUTPUT_DIR"/direct-lstmf.txt

# Create corpus if missing
if [ ! -f "$CORPUS_FILE" ]; then
    echo "Creating test corpus..."
    mkdir -p "$(dirname "$CORPUS_FILE")"
    cat > "$CORPUS_FILE" << 'EOF'
ئەم تاقیکردنەوەیەکە بۆ نووسینی کوردی
کوردی زمانێکی جوانە
تێکستی کوردی بۆ تاقیکردنەوە
نووسینی کوردی بە فۆنتی جیاواز
ئەم دەقە بۆ راهێنانی OCR بەکاردێت
بەرنامەی دەقناسی بۆ زمانی کوردی
پەرەپێدانی تەکنەلۆژیای زمانی کوردی
خوێندنەوەی دەقی کوردی بە شێوەی ئۆتۆماتیکی
EOF
fi

echo ""
echo "Testing font recognition method..."

# First, test what works
TEST_FONT="$FONTS_DIR/00_Sarchia_ABC.ttf"
echo "Testing with: $TEST_FONT"

# Test with full filename as font name
text2image \
    --text="$CORPUS_FILE" \
    --outputbase="$GROUND_TRUTH_DIR/test1" \
    --font="00_Sarchia_ABC" \
    --fonts_dir="$FONTS_DIR" \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 >/dev/null 2>&1

if [ -f "$GROUND_TRUTH_DIR/test1.tif" ]; then
    echo "✓ Method 1 works: Using filename without extension"
    METHOD="filename"
else
    # Test with full filename including extension
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/test2" \
        --font="00_Sarchia_ABC.ttf" \
        --fonts_dir="$FONTS_DIR" \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "$GROUND_TRUTH_DIR/test2.tif" ]; then
        echo "✓ Method 2 works: Using full filename with extension"
        METHOD="fullname"
    else
        echo "✗ Standard methods not working, trying alternative..."
        METHOD="none"
    fi
fi

# Clean test files
rm -f "$GROUND_TRUTH_DIR"/test*.tif

echo ""
echo "Generating training data with detected method..."
SUCCESS=0
FAILED=0
FONT_INDEX=0
MAX_FONTS=50  # Limit to 50 fonts for faster testing

# Process fonts
for font_file in "$FONTS_DIR"/*.ttf; do
    if [ ! -f "$font_file" ]; then
        continue
    fi
    
    FONT_INDEX=$((FONT_INDEX + 1))
    
    if [ $FONT_INDEX -gt $MAX_FONTS ]; then
        echo "Reached maximum of $MAX_FONTS fonts for testing"
        break
    fi
    
    FONT_FILENAME=$(basename "$font_file")
    FONT_BASE=$(basename "$font_file" .ttf)
    OUTPUT_BASE="$GROUND_TRUTH_DIR/ckb.font${FONT_INDEX}"
    
    echo -n "[$FONT_INDEX/$MAX_FONTS] Processing $FONT_BASE... "
    
    # Try the method that worked in testing
    if [ "$METHOD" = "filename" ]; then
        FONT_NAME="$FONT_BASE"
    elif [ "$METHOD" = "fullname" ]; then
        FONT_NAME="$FONT_FILENAME"
    else
        # Try both
        FONT_NAME="$FONT_BASE"
    fi
    
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$OUTPUT_BASE" \
        --font="$FONT_NAME" \
        --fonts_dir="$FONTS_DIR" \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "${OUTPUT_BASE}.tif" ]; then
        echo "✓"
        SUCCESS=$((SUCCESS + 1))
        
        # Create ground truth text file
        head -1 "$CORPUS_FILE" > "${OUTPUT_BASE}.gt.txt"
        
        # Generate box file
        tesseract "${OUTPUT_BASE}.tif" "$OUTPUT_BASE" makebox >/dev/null 2>&1
    else
        # Try alternative if first attempt failed
        if [ "$METHOD" = "none" ]; then
            text2image \
                --text="$CORPUS_FILE" \
                --outputbase="$OUTPUT_BASE" \
                --font="$FONT_FILENAME" \
                --fonts_dir="$FONTS_DIR" \
                --resolution=300 \
                --ptsize=12 \
                --max_pages=1 >/dev/null 2>&1
            
            if [ -f "${OUTPUT_BASE}.tif" ]; then
                echo "✓ (alt)"
                SUCCESS=$((SUCCESS + 1))
                head -1 "$CORPUS_FILE" > "${OUTPUT_BASE}.gt.txt"
                tesseract "${OUTPUT_BASE}.tif" "$OUTPUT_BASE" makebox >/dev/null 2>&1
            else
                echo "✗"
                FAILED=$((FAILED + 1))
            fi
        else
            echo "✗"
            FAILED=$((FAILED + 1))
        fi
    fi
done

echo ""
echo "Training data generation complete!"
echo "  Success: $SUCCESS fonts"
echo "  Failed: $FAILED fonts"

if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo "No training data generated!"
    echo "Trying fallback method with default fonts..."
    
    # Try with default system fonts as fallback
    echo "Testing with DejaVu Sans (should be available)..."
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb.dejavu" \
        --font="DejaVu Sans" \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "$GROUND_TRUTH_DIR/ckb.dejavu.tif" ]; then
        echo "✓ Generated with DejaVu Sans"
        head -1 "$CORPUS_FILE" > "$GROUND_TRUTH_DIR/ckb.dejavu.gt.txt"
        SUCCESS=1
    else
        echo "✗ Even default fonts not working"
        echo ""
        echo "ERROR: text2image cannot generate any training data"
        echo "This might be a text2image installation issue"
        exit 1
    fi
fi

echo ""
echo "Converting to LSTMF format..."
LSTMF_COUNT=0
> "$OUTPUT_DIR/direct-lstmf.txt"

for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
    if [ -f "$tif_file" ]; then
        BASE=$(basename "$tif_file" .tif)
        
        # Ensure ground truth text exists
        if [ ! -f "$GROUND_TRUTH_DIR/${BASE}.gt.txt" ]; then
            head -1 "$CORPUS_FILE" > "$GROUND_TRUTH_DIR/${BASE}.gt.txt"
        fi
        
        echo -n "Converting $BASE... "
        
        tesseract "$tif_file" "$GROUND_TRUTH_DIR/$BASE" \
            --psm 6 lstm.train >/dev/null 2>&1
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
            echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/direct-lstmf.txt"
            LSTMF_COUNT=$((LSTMF_COUNT + 1))
            echo "✓"
        else
            echo "✗"
        fi
    fi
done

echo ""
echo "Generated $LSTMF_COUNT LSTMF files"

if [ $LSTMF_COUNT -eq 0 ]; then
    echo "No LSTMF files generated!"
    exit 1
fi

echo ""
echo "Starting LSTM training..."

# Select base model
if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    BASE_MODEL="ara"
    echo "Using Arabic base model"
elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
    BASE_MODEL="eng"
    echo "Using English base model"
else
    echo "No base model found!"
    exit 1
fi

echo "Training configuration:"
echo "  Base model: $BASE_MODEL"
echo "  Training samples: $LSTMF_COUNT"
echo "  Max iterations: $MAX_ITERATIONS"
echo "  Target error: $TARGET_ERROR"
echo ""

# Run training
echo "Training in progress..."
lstmtraining \
    --model_output "$OUTPUT_DIR/ckb" \
    --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
    --train_listfile "$OUTPUT_DIR/direct-lstmf.txt" \
    --max_iterations $MAX_ITERATIONS \
    --target_error_rate $TARGET_ERROR \
    --debug_interval $DEBUG_INTERVAL 2>&1 | while IFS= read -r line; do
        if echo "$line" | grep -q "At iteration"; then
            # Extract iteration and error
            ITER=$(echo "$line" | sed -n 's/.*At iteration \([0-9]*\).*/\1/p')
            ERROR=$(echo "$line" | sed -n 's/.*error rate \([0-9.]*\).*/\1/p')
            if [ -n "$ITER" ] && [ -n "$ERROR" ]; then
                printf "\rIteration: %5d / %d | Error: %s    " "$ITER" "$MAX_ITERATIONS" "$ERROR"
            fi
        elif echo "$line" | grep -q "Finished"; then
            echo ""
            echo "Training finished!"
        fi
    done

echo ""

# Check for checkpoint
CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb*.checkpoint 2>/dev/null | head -1)

if [ -n "$CHECKPOINT" ] && [ -f "$CHECKPOINT" ]; then
    echo "Training completed! Creating final model..."
    
    # Finalize model
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
        --model_output "$FINAL_MODEL" >/dev/null 2>&1
    
    if [ -f "$FINAL_MODEL" ]; then
        # Install model
        cp "$FINAL_MODEL" "$TESSDATA_DEST"
        
        # Also save with timestamp
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp "$FINAL_MODEL" "$OUTPUT_DIR/ckb_${TIMESTAMP}.traineddata"
        
        MODEL_SIZE=$(du -h "$FINAL_MODEL" | cut -f1)
        
        echo ""
        echo "════════════════════════════════════════════════════════"
        echo "✓ SUCCESS! Kurdish OCR Model Created!"
        echo "════════════════════════════════════════════════════════"
        echo ""
        echo "Model Details:"
        echo "  Location: tessdata/ckb.traineddata"
        echo "  Size: $MODEL_SIZE"
        echo "  Training samples: $LSTMF_COUNT"
        echo "  Fonts used: $SUCCESS"
        echo ""
        echo "To test the model:"
        echo "  tesseract test_image.png output -l ckb --psm 6"
        echo ""
        echo "Backup saved as: $OUTPUT_DIR/ckb_${TIMESTAMP}.traineddata"
    else
        echo "Failed to create final model"
        exit 1
    fi
else
    echo "Training did not complete successfully"
    echo "No checkpoint file found"
    exit 1
fi
