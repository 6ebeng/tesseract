#!/bin/sh

# Training script using installed system fonts

echo "=== Kurdish OCR Training with Installed Fonts ==="
echo ""

# Configuration
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-installed"
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
rm -f "$OUTPUT_DIR"/installed-lstmf.txt

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
echo "Generating training data with installed fonts..."
SUCCESS=0
FAILED=0
FONT_INDEX=0

# List of font names to try (without .ttf extension)
FONT_NAMES="
Sarchia_ABC
Sarchia_Abdullah
Sarchia_Ahmad
Sarchia_Ali
Sarchia_Baran
Sarchia_Kurdish
Sarchia_Kurdistan
abdakre
abdbam
KGoran
KHana
KNali
"

for FONT_NAME in $FONT_NAMES; do
    FONT_INDEX=$((FONT_INDEX + 1))
    
    # Try different variations of the font name
    for VARIANT in "$FONT_NAME" "$(echo $FONT_NAME | sed 's/_/ /g')" "$(echo $FONT_NAME | sed 's/_//g')"; do
        OUTPUT_BASE="$GROUND_TRUTH_DIR/ckb.font${FONT_INDEX}"
        
        echo -n "Trying font '$VARIANT'... "
        
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="$OUTPUT_BASE" \
            --font="$VARIANT" \
            --resolution=300 \
            --ptsize=12 \
            --max_pages=1 >/dev/null 2>&1
        
        if [ -f "${OUTPUT_BASE}.tif" ]; then
            echo "✓"
            SUCCESS=$((SUCCESS + 1))
            
            # Generate box file
            tesseract "${OUTPUT_BASE}.tif" "$OUTPUT_BASE" makebox >/dev/null 2>&1
            break
        fi
    done
    
    if [ ! -f "${OUTPUT_BASE}.tif" ]; then
        echo "✗"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "Training data generation complete!"
echo "  Success: $SUCCESS fonts"
echo "  Failed: $FAILED fonts"

if [ $SUCCESS -eq 0 ]; then
    echo "No training data generated!"
    exit 1
fi

echo ""
echo "Converting to LSTMF format..."
LSTMF_COUNT=0
> "$OUTPUT_DIR/installed-lstmf.txt"

for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
    if [ -f "$tif_file" ]; then
        BASE=$(basename "$tif_file" .tif)
        
        # Create ground truth text if missing
        if [ ! -f "$GROUND_TRUTH_DIR/${BASE}.gt.txt" ]; then
            # Extract text from corpus for ground truth
            head -1 "$CORPUS_FILE" > "$GROUND_TRUTH_DIR/${BASE}.gt.txt"
        fi
        
        tesseract "$tif_file" "$GROUND_TRUTH_DIR/$BASE" \
            --psm 6 lstm.train >/dev/null 2>&1
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
            echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/installed-lstmf.txt"
            LSTMF_COUNT=$((LSTMF_COUNT + 1))
        fi
    fi
done

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

# Run training
lstmtraining \
    --model_output "$OUTPUT_DIR/ckb" \
    --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
    --train_listfile "$OUTPUT_DIR/installed-lstmf.txt" \
    --max_iterations $MAX_ITERATIONS \
    --target_error_rate $TARGET_ERROR \
    --debug_interval $DEBUG_INTERVAL 2>&1 | while read line; do
        if echo "$line" | grep -q "At iteration"; then
            echo "$line"
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
        echo ""
        echo "✓ SUCCESS! Model created and installed to tessdata/ckb.traineddata"
        echo "Size: $(du -h "$FINAL_MODEL" | cut -f1)"
        echo ""
        echo "To test: tesseract image.png output -l ckb"
    else
        echo "Failed to create final model"
        exit 1
    fi
else
    echo "Training did not complete successfully"
    exit 1
fi
