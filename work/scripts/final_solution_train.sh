#!/bin/sh

# Final solution: Use the font that text2image suggests

echo "=== Final Solution: Kurdish OCR Training ==="
echo ""

WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-final"
FONTS_DIR="/root/.local/share/fonts/kurdish"
FINAL_MODEL="$WORK_DIR/output/ckb_new.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb_custom.traineddata"
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Clean environment
echo "Preparing environment..."
rm -rf "$GROUND_TRUTH_DIR"
mkdir -p "$GROUND_TRUTH_DIR"
mkdir -p "$OUTPUT_DIR"

# Create corpus
if [ ! -f "$CORPUS_FILE" ]; then
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
echo "Using the font that text2image recognizes..."

# text2image suggested '55_Sarchia_Kurdish' - let's use it
SUGGESTED_FONT="55_Sarchia_Kurdish"

echo "Testing with font: $SUGGESTED_FONT"
text2image \
    --text="$CORPUS_FILE" \
    --outputbase="$GROUND_TRUTH_DIR/ckb_kurdish" \
    --font="$SUGGESTED_FONT" \
    --fonts_dir="$FONTS_DIR" \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1 2>&1

if [ -f "$GROUND_TRUTH_DIR/ckb_kurdish.tif" ]; then
    echo "✓ SUCCESS! Generated training image with $SUGGESTED_FONT"
    SUCCESS=1
else
    echo "✗ Failed with suggested font"
    
    # Try variations
    echo "Trying variations..."
    
    # Try with the actual file in fonts directory
    for font_file in "$FONTS_DIR"/55_Sarchia_Kurdish*.ttf "$FONTS_DIR"/56_Sarchia_Kurdish*.ttf; do
        if [ -f "$font_file" ]; then
            FONT_NAME=$(basename "$font_file" .ttf)
            echo "Trying: $FONT_NAME"
            
            text2image \
                --text="$CORPUS_FILE" \
                --outputbase="$GROUND_TRUTH_DIR/ckb_$FONT_NAME" \
                --font="$FONT_NAME" \
                --fonts_dir="$FONTS_DIR" \
                --resolution=300 \
                --ptsize=12 \
                --max_pages=1 >/dev/null 2>&1
            
            if [ -f "$GROUND_TRUTH_DIR/ckb_$FONT_NAME.tif" ]; then
                echo "✓ SUCCESS with $FONT_NAME"
                SUCCESS=1
                break
            fi
        fi
    done
fi

# Try more fonts if first attempts failed
if [ "$SUCCESS" != "1" ]; then
    echo ""
    echo "Trying other Kurdish fonts..."
    
    FONT_COUNT=0
    MAX_FONTS=20
    
    for font_file in "$FONTS_DIR"/*.ttf; do
        if [ $FONT_COUNT -ge $MAX_FONTS ]; then
            break
        fi
        
        FONT_NAME=$(basename "$font_file" .ttf)
        FONT_COUNT=$((FONT_COUNT + 1))
        
        echo -n "[$FONT_COUNT/$MAX_FONTS] Trying $FONT_NAME... "
        
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="$GROUND_TRUTH_DIR/ckb_font${FONT_COUNT}" \
            --font="$FONT_NAME" \
            --fonts_dir="$FONTS_DIR" \
            --resolution=300 \
            --ptsize=12 \
            --max_pages=1 >/dev/null 2>&1
        
        if [ -f "$GROUND_TRUTH_DIR/ckb_font${FONT_COUNT}.tif" ]; then
            echo "✓"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "✗"
        fi
    done
fi

echo ""
echo "Training data generation results:"
TIF_COUNT=$(ls "$GROUND_TRUTH_DIR"/*.tif 2>/dev/null | wc -l)
echo "  Generated TIF files: $TIF_COUNT"

if [ $TIF_COUNT -eq 0 ]; then
    echo ""
    echo "ERROR: Could not generate any training data"
    echo ""
    echo "The issue is that text2image cannot use the fonts properly."
    echo ""
    echo "SOLUTION: Use the existing ckb.traineddata model"
    echo ""
    
    if [ -f "$(pwd)/tessdata/ckb.traineddata" ]; then
        MODEL_SIZE=$(du -h "$(pwd)/tessdata/ckb.traineddata" | cut -f1)
        echo "✓ Existing Kurdish model found:"
        echo "  Location: tessdata/ckb.traineddata"
        echo "  Size: $MODEL_SIZE"
        echo ""
        echo "To test the model:"
        echo "  tesseract test_image.png output -l ckb --psm 6"
    else
        echo "Downloading pre-trained Kurdish model..."
        wget -q https://github.com/tesseract-ocr/tessdata/raw/main/ckb.traineddata \
            -O "$(pwd)/tessdata/ckb.traineddata" 2>/dev/null || {
            echo "Download failed. Please download manually:"
            echo "  wget https://github.com/tesseract-ocr/tessdata/raw/main/ckb.traineddata"
            echo "  mv ckb.traineddata tessdata/"
        }
        
        if [ -f "$(pwd)/tessdata/ckb.traineddata" ]; then
            echo "✓ Downloaded pre-trained Kurdish model"
        fi
    fi
    
    exit 0
fi

# If we have training data, proceed with training
echo ""
echo "Creating ground truth files..."

for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
    if [ -f "$tif_file" ]; then
        BASE=$(basename "$tif_file" .tif)
        # Create ground truth text
        cp "$CORPUS_FILE" "$GROUND_TRUTH_DIR/${BASE}.gt.txt"
    fi
done

echo "Converting to LSTMF format..."
LSTMF_COUNT=0
> "$OUTPUT_DIR/final-lstmf.txt"

for tif_file in "$GROUND_TRUTH_DIR"/*.tif; do
    if [ -f "$tif_file" ]; then
        BASE=$(basename "$tif_file" .tif)
        
        tesseract "$tif_file" "$GROUND_TRUTH_DIR/$BASE" \
            --psm 6 lstm.train >/dev/null 2>&1
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
            echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/final-lstmf.txt"
            LSTMF_COUNT=$((LSTMF_COUNT + 1))
        fi
    fi
done

echo "Generated $LSTMF_COUNT LSTMF files"

if [ $LSTMF_COUNT -eq 0 ]; then
    echo "No LSTMF files generated. Cannot train."
    exit 1
fi

echo ""
echo "Starting LSTM training..."

# Use existing ckb model as base if available, otherwise use eng
if [ -f "$(pwd)/tessdata/ckb.traineddata" ]; then
    BASE_MODEL_PATH="$(pwd)/tessdata/ckb.traineddata"
    echo "Using existing Kurdish model as base"
elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
    BASE_MODEL_PATH="$TESSDATA_PREFIX/eng.traineddata"
    echo "Using English model as base"
else
    echo "No base model available"
    exit 1
fi

# Train
lstmtraining \
    --model_output "$OUTPUT_DIR/ckb_custom" \
    --traineddata "$BASE_MODEL_PATH" \
    --train_listfile "$OUTPUT_DIR/final-lstmf.txt" \
    --max_iterations 1000 \
    --target_error_rate 0.01 \
    --debug_interval 100 2>&1 | while read line; do
        if echo "$line" | grep -q "At iteration"; then
            echo "$line"
        fi
    done || true

# Check for checkpoint
CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_custom*.checkpoint 2>/dev/null | head -1)

if [ -n "$CHECKPOINT" ] && [ -f "$CHECKPOINT" ]; then
    echo "Creating final model..."
    
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$BASE_MODEL_PATH" \
        --model_output "$FINAL_MODEL" >/dev/null 2>&1
    
    if [ -f "$FINAL_MODEL" ]; then
        cp "$FINAL_MODEL" "$TESSDATA_DEST"
        echo ""
        echo "✓ Custom Kurdish model created!"
        echo "  Location: tessdata/ckb_custom.traineddata"
        echo ""
        echo "To test: tesseract image.png output -l ckb_custom"
    fi
else
    echo "Training did not produce a checkpoint"
fi

echo ""
echo "=== Final Status ==="
echo ""

# List all available models
echo "Available Kurdish OCR models:"
for model in "$(pwd)"/tessdata/ckb*.traineddata; do
    if [ -f "$model" ]; then
        MODEL_NAME=$(basename "$model")
        MODEL_SIZE=$(du -h "$model" | cut -f1)
        echo "  - $MODEL_NAME ($MODEL_SIZE)"
    fi
done

echo ""
echo "To use a model:"
echo "  tesseract image.png output -l ckb --psm 6"
echo "  tesseract image.png output -l ckb_custom --psm 6"
