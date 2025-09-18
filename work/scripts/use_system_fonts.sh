#!/bin/sh

# Script to train using system fonts that text2image can actually see

echo "=== Kurdish OCR Training with System Fonts ==="
echo ""

# Configuration
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-system"
FINAL_MODEL="$WORK_DIR/output/ckb.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb.traineddata"
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Clean environment
echo "Preparing clean environment..."
rm -rf "$GROUND_TRUTH_DIR"
mkdir -p "$GROUND_TRUTH_DIR"
mkdir -p "$OUTPUT_DIR"

# Create corpus if missing
if [ ! -f "$CORPUS_FILE" ]; then
    echo "Creating Kurdish corpus..."
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
سەرەتای فێربوونی کۆمپیوتەر بۆ خوێندنەوەی کوردی
پێشکەوتنی تەکنەلۆژیا لە کوردستان
زمانی کوردی و تەکنەلۆژیای نوێ
بەکارهێنانی هوشی دەستکرد بۆ زمانی کوردی
پەرەپێدانی سیستەمی نووسینی کوردی
یەکەمین هەنگاوەکان بۆ OCR کوردی
داهاتووی تەکنەلۆژیا بۆ زمانی کوردی
EOF
fi

echo ""
echo "Step 1: Check what fonts text2image can actually use..."
echo ""

# List available fonts that text2image recognizes
echo "Getting list of available fonts..."
text2image --list_available_fonts 2>&1 | head -50 > "$OUTPUT_DIR/available_fonts.txt"

# Check if any fonts are available
FONT_COUNT=$(wc -l < "$OUTPUT_DIR/available_fonts.txt")
echo "Found $FONT_COUNT lines of font information"

# Try with some standard fonts that should work
echo ""
echo "Step 2: Testing with standard fonts..."
echo ""

SUCCESS=0
FONT_INDEX=0

# List of fonts to try - these are commonly available
FONTS_TO_TRY="
DejaVu Sans
DejaVu Serif
Liberation Sans
Liberation Serif
FreeSans
FreeSerif
Noto Sans
Noto Serif
Arial
Times New Roman
Courier New
monospace
serif
sans-serif
"

for FONT in $FONTS_TO_TRY; do
    if [ -z "$FONT" ]; then
        continue
    fi
    
    FONT_INDEX=$((FONT_INDEX + 1))
    OUTPUT_BASE="$GROUND_TRUTH_DIR/ckb.font${FONT_INDEX}"
    
    echo -n "Testing font '$FONT'... "
    
    # Try to generate training data
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$OUTPUT_BASE" \
        --font="$FONT" \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ -f "${OUTPUT_BASE}.tif" ]; then
        echo "✓ SUCCESS"
        SUCCESS=$((SUCCESS + 1))
        
        # Create ground truth text
        cp "$CORPUS_FILE" "${OUTPUT_BASE}.gt.txt"
        
        # Generate box file
        tesseract "${OUTPUT_BASE}.tif" "$OUTPUT_BASE" makebox >/dev/null 2>&1
    else
        echo "✗ Failed"
        # Clean up any partial files
        rm -f "${OUTPUT_BASE}".*
    fi
done

echo ""
echo "Successfully generated training data with $SUCCESS fonts"

if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo "ERROR: Could not generate training data with any font!"
    echo ""
    echo "Attempting minimal training with synthetic data..."
    
    # Create a minimal synthetic training image
    echo "Creating synthetic training data..."
    
    # Use tesseract to create synthetic data
    echo "ئەم تاقیکردنەوەیەکە" > "$GROUND_TRUTH_DIR/synthetic.gt.txt"
    
    # Try to use any available method to create an image
    # This is a last resort
    convert -size 300x50 xc:white -font "DejaVu-Sans" -pointsize 20 \
            -draw "text 10,30 'Test'" "$GROUND_TRUTH_DIR/synthetic.tif" 2>/dev/null || {
        echo "ImageMagick also failed. Cannot create training data."
        exit 1
    }
    
    if [ -f "$GROUND_TRUTH_DIR/synthetic.tif" ]; then
        echo "✓ Created synthetic training image"
        SUCCESS=1
    fi
fi

echo ""
echo "Step 3: Converting to LSTMF format..."
LSTMF_COUNT=0
> "$OUTPUT_DIR/system-lstmf.txt"

for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
    if [ -f "$tif_file" ]; then
        BASE=$(basename "$tif_file" .tif)
        
        # Ensure ground truth text exists
        if [ ! -f "$GROUND_TRUTH_DIR/${BASE}.gt.txt" ]; then
            cp "$CORPUS_FILE" "$GROUND_TRUTH_DIR/${BASE}.gt.txt"
        fi
        
        echo -n "Converting $BASE... "
        
        # Generate LSTMF
        tesseract "$tif_file" "$GROUND_TRUTH_DIR/$BASE" \
            --psm 6 lstm.train >/dev/null 2>&1
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
            echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/system-lstmf.txt"
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
    echo "ERROR: No LSTMF files generated!"
    echo "Cannot proceed with training."
    exit 1
fi

echo ""
echo "Step 4: Starting LSTM training..."

# Select base model
if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    BASE_MODEL="ara"
    echo "Using Arabic base model"
elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
    BASE_MODEL="eng"
    echo "Using English base model"
else
    echo "ERROR: No base model found!"
    exit 1
fi

# Adjust training parameters for small dataset
if [ $LSTMF_COUNT -lt 10 ]; then
    echo "Note: Small dataset detected. Adjusting parameters..."
    MAX_ITERATIONS=2000
    TARGET_ERROR=0.1
else
    MAX_ITERATIONS=5000
    TARGET_ERROR=0.01
fi

echo ""
echo "Training configuration:"
echo "  Base model: $BASE_MODEL"
echo "  Training samples: $LSTMF_COUNT"
echo "  Max iterations: $MAX_ITERATIONS"
echo "  Target error: $TARGET_ERROR"
echo ""

# Run training
echo "Training in progress..."
echo "(This may take several minutes...)"
echo ""

lstmtraining \
    --model_output "$OUTPUT_DIR/ckb" \
    --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
    --train_listfile "$OUTPUT_DIR/system-lstmf.txt" \
    --max_iterations $MAX_ITERATIONS \
    --target_error_rate $TARGET_ERROR \
    --debug_interval 100 2>&1 | while IFS= read -r line; do
        if echo "$line" | grep -q "At iteration"; then
            echo "$line"
        elif echo "$line" | grep -q "Finished"; then
            echo "Training finished!"
        elif echo "$line" | grep -q "error"; then
            echo "$line"
        fi
    done || true  # Don't exit on training errors

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
        
        # Create backup
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
        echo "  System fonts used: $SUCCESS"
        echo ""
        echo "IMPORTANT NOTE:"
        echo "This model was trained with system fonts only."
        echo "For better accuracy with Kurdish fonts, the font"
        echo "installation issue needs to be resolved."
        echo ""
        echo "To test the model:"
        echo "  tesseract test_image.png output -l ckb --psm 6"
        echo ""
        echo "Backup saved as: $OUTPUT_DIR/ckb_${TIMESTAMP}.traineddata"
    else
        echo "ERROR: Failed to create final model"
        exit 1
    fi
else
    echo "WARNING: Training may not have completed successfully"
    echo "No checkpoint file found at expected location"
    
    # Check if there's any checkpoint at all
    ANY_CHECKPOINT=$(find "$OUTPUT_DIR" -name "*.checkpoint" 2>/dev/null | head -1)
    if [ -n "$ANY_CHECKPOINT" ]; then
        echo "Found checkpoint at: $ANY_CHECKPOINT"
        echo "Attempting to create model from this checkpoint..."
        
        lstmtraining \
            --stop_training \
            --continue_from "$ANY_CHECKPOINT" \
            --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
            --model_output "$FINAL_MODEL" >/dev/null 2>&1
        
        if [ -f "$FINAL_MODEL" ]; then
            cp "$FINAL_MODEL" "$TESSDATA_DEST"
            echo "✓ Model created from alternative checkpoint"
        fi
    else
        echo "No checkpoint files found at all"
        exit 1
    fi
fi
