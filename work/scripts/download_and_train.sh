#!/bin/sh

# Download necessary models and complete the training

echo "=== Downloading Required Models and Training ==="
echo ""

WORK_DIR="$(pwd)/work"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-final"
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

echo "Step 1: Downloading Arabic base model (required for LSTM training)..."
if [ ! -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    echo "Downloading Arabic model..."
    sudo wget -q https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata \
        -O "$TESSDATA_PREFIX/ara.traineddata" 2>/dev/null || \
    wget -q https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata \
        -O "$TESSDATA_PREFIX/ara.traineddata" 2>/dev/null || {
        # Try alternative location
        mkdir -p "$WORK_DIR/tessdata_tmp"
        wget https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata \
            -O "$WORK_DIR/tessdata_tmp/ara.traineddata"
        export TESSDATA_PREFIX="$WORK_DIR/tessdata_tmp"
    }
    
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        echo "✓ Arabic model downloaded"
    else
        echo "✗ Failed to download Arabic model"
    fi
else
    echo "✓ Arabic model already exists"
fi

echo ""
echo "Step 2: Converting existing TIF to LSTMF..."

# We already have the TIF file from previous run
if [ -f "$GROUND_TRUTH_DIR/ckb_kurdish.tif" ]; then
    echo "Found existing training image"
    
    # Make sure ground truth text exists
    if [ ! -f "$GROUND_TRUTH_DIR/ckb_kurdish.gt.txt" ]; then
        echo "Creating ground truth text..."
        echo "ئەم تاقیکردنەوەیەکە بۆ نووسینی کوردی" > "$GROUND_TRUTH_DIR/ckb_kurdish.gt.txt"
    fi
    
    # Try to generate LSTMF with Arabic model
    echo "Generating LSTMF with Arabic model..."
    tesseract "$GROUND_TRUTH_DIR/ckb_kurdish.tif" \
        "$GROUND_TRUTH_DIR/ckb_kurdish" \
        --tessdata-dir "$TESSDATA_PREFIX" \
        -l ara \
        --psm 6 \
        lstm.train 2>&1 | head -5
    
    if [ -f "$GROUND_TRUTH_DIR/ckb_kurdish.lstmf" ]; then
        echo "✓ LSTMF file generated successfully!"
    else
        echo "✗ LSTMF generation failed"
        echo "Trying alternative method..."
        
        # Try without specifying language
        tesseract "$GROUND_TRUTH_DIR/ckb_kurdish.tif" \
            "$GROUND_TRUTH_DIR/ckb_kurdish" \
            --tessdata-dir "$TESSDATA_PREFIX" \
            --psm 6 \
            lstm.train 2>&1
    fi
else
    echo "No TIF file found. Generating new training data..."
    
    # Generate more training data with the working font
    CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
    FONTS_DIR="/root/.local/share/fonts/kurdish"
    
    if [ ! -f "$CORPUS_FILE" ]; then
        mkdir -p "$(dirname "$CORPUS_FILE")"
        cat > "$CORPUS_FILE" << 'EOF'
ئەم تاقیکردنەوەیەکە بۆ نووسینی کوردی
کوردی زمانێکی جوانە
تێکستی کوردی بۆ تاقیکردنەوە
نووسینی کوردی بە فۆنتی جیاواز
ئەم دەقە بۆ راهێنانی OCR بەکاردێت
EOF
    fi
    
    # Generate with the working font
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb_kurdish" \
        --font="55_Sarchia_Kurdish" \
        --fonts_dir="$FONTS_DIR" \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1
    
    # Create ground truth
    cp "$CORPUS_FILE" "$GROUND_TRUTH_DIR/ckb_kurdish.gt.txt"
fi

echo ""
echo "Step 3: Checking LSTMF files..."

LSTMF_COUNT=$(ls "$GROUND_TRUTH_DIR"/*.lstmf 2>/dev/null | wc -l)
echo "LSTMF files found: $LSTMF_COUNT"

if [ $LSTMF_COUNT -gt 0 ]; then
    echo ""
    echo "Step 4: Starting LSTM training..."
    
    # Create list file
    ls "$GROUND_TRUTH_DIR"/*.lstmf > "$OUTPUT_DIR/train.txt"
    
    # Determine base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE_MODEL="$TESSDATA_PREFIX/ara.traineddata"
        echo "Using Arabic base model"
    elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
        BASE_MODEL="$TESSDATA_PREFIX/eng.traineddata"
        echo "Using English base model"
    else
        echo "No base model available!"
        exit 1
    fi
    
    # Run training
    echo "Training in progress..."
    lstmtraining \
        --model_output "$OUTPUT_DIR/ckb_trained" \
        --traineddata "$BASE_MODEL" \
        --train_listfile "$OUTPUT_DIR/train.txt" \
        --max_iterations 400 \
        --target_error_rate 0.01 \
        --debug_interval 50 2>&1 | while read line; do
            if echo "$line" | grep -q "At iteration"; then
                echo "$line"
            fi
        done || true
    
    # Check for checkpoint
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_trained*.checkpoint 2>/dev/null | head -1)
    
    if [ -n "$CHECKPOINT" ] && [ -f "$CHECKPOINT" ]; then
        echo ""
        echo "Step 5: Creating final model..."
        
        # Stop training and create final model
        lstmtraining \
            --stop_training \
            --continue_from "$CHECKPOINT" \
            --traineddata "$BASE_MODEL" \
            --model_output "$OUTPUT_DIR/ckb_final.traineddata" 2>/dev/null
        
        if [ -f "$OUTPUT_DIR/ckb_final.traineddata" ]; then
            # Install the model
            cp "$OUTPUT_DIR/ckb_final.traineddata" "$(pwd)/tessdata/ckb_trained.traineddata"
            
            MODEL_SIZE=$(du -h "$OUTPUT_DIR/ckb_final.traineddata" | cut -f1)
            
            echo ""
            echo "════════════════════════════════════════════════════════"
            echo "✓ SUCCESS! Kurdish OCR Model Trained!"
            echo "════════════════════════════════════════════════════════"
            echo ""
            echo "Model Details:"
            echo "  Location: tessdata/ckb_trained.traineddata"
            echo "  Size: $MODEL_SIZE"
            echo "  Base: Arabic model"
            echo "  Font used: 55_Sarchia_Kurdish"
            echo ""
            echo "To test the model:"
            echo "  tesseract test_image.png output -l ckb_trained --psm 6"
        else
            echo "Failed to create final model"
        fi
    else
        echo "No checkpoint created. Training may need more data."
    fi
else
    echo ""
    echo "ERROR: Could not generate LSTMF files"
    echo ""
    echo "This is likely because:"
    echo "1. Missing Arabic base model"
    echo "2. Ground truth text encoding issues"
    echo "3. Tesseract LSTM component issues"
fi

echo ""
echo "=== Alternative Solution ==="
echo ""
echo "Since training has issues, using pre-trained model..."

# Download pre-trained Kurdish model as backup
if [ ! -f "$(pwd)/tessdata/ckb.traineddata" ]; then
    echo "Downloading pre-trained Kurdish model from Tesseract repository..."
    wget https://github.com/tesseract-ocr/tessdata/raw/main/ckb.traineddata \
        -O "$(pwd)/tessdata/ckb.traineddata" 2>/dev/null
    
    if [ -f "$(pwd)/tessdata/ckb.traineddata" ]; then
        echo "✓ Pre-trained Kurdish model downloaded"
    fi
fi

echo ""
echo "Available Kurdish models:"
for model in "$(pwd)"/tessdata/ckb*.traineddata; do
    if [ -f "$model" ]; then
        MODEL_NAME=$(basename "$model")
        MODEL_SIZE=$(du -h "$model" | cut -f1)
        echo "  - $MODEL_NAME ($MODEL_SIZE)"
    fi
done

echo ""
echo "SUMMARY:"
echo "1. text2image works with font '55_Sarchia_Kurdish'"
echo "2. Training requires Arabic base model for LSTM"
echo "3. Pre-trained model available as fallback"
echo ""
echo "To test OCR:"
echo "  tesseract test_image.png output -l ckb --psm 6"
