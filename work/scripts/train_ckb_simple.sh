#!/bin/sh

# Simple WSL-compatible training script for Kurdish OCR

set -e

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-corpus"
FONTS_PATH="$WORK_DIR/fonts/kurdish"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo "${CYAN}════════════════════════════════════════════════════════${NC}"
echo "${CYAN}   Kurdish OCR Training with Corpus and Fonts          ${NC}"
echo "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""

# Check environment
echo "${BLUE}Working directory: $(pwd)${NC}"
echo ""

# Create directories
mkdir -p "$GROUND_TRUTH_DIR"
mkdir -p "$OUTPUT_DIR"

# Clean previous data
echo "${YELLOW}Cleaning previous training data...${NC}"
rm -rf "$GROUND_TRUTH_DIR"/*

# Verify corpus exists
if [ ! -f "$CORPUS_FILE" ]; then
    echo "${RED}Error: Corpus file not found at $CORPUS_FILE${NC}"
    exit 1
fi

echo "${GREEN}✓ Found corpus file${NC}"
echo "  Lines in corpus: $(wc -l < "$CORPUS_FILE")"

# Check fonts
if [ ! -d "$FONTS_PATH" ]; then
    echo "${RED}Error: Fonts directory not found at $FONTS_PATH${NC}"
    exit 1
fi

FONT_COUNT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | wc -l || echo 0)
echo "${GREEN}✓ Found $FONT_COUNT Kurdish fonts${NC}"
echo ""

if [ "$FONT_COUNT" -eq 0 ]; then
    echo "${RED}No TTF fonts found in $FONTS_PATH${NC}"
    exit 1
fi

# Generate training data with selected fonts
echo "${YELLOW}Generating training images with 10 fonts...${NC}"
SUCCESS=0
FONT_INDEX=0
MAX_FONTS=10

for font in $(ls "$FONTS_PATH"/*.ttf | head -$MAX_FONTS); do
    FONT_NAME=$(basename "$font" .ttf)
    # Clean font name for file naming
    CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
    
    printf "Font %d/%d: %s... " "$((FONT_INDEX+1))" "$MAX_FONTS" "${FONT_NAME}"
    
    # Generate training image
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.exp${FONT_INDEX}" \
        --font="$FONT_NAME" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --char_spacing=0.0 \
        --exposure=0 \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 >/dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "${GREEN}✓${NC}"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "${RED}✗${NC}"
    fi
    
    FONT_INDEX=$((FONT_INDEX + 1))
done

echo ""
echo "${GREEN}Generated $SUCCESS/$MAX_FONTS training samples${NC}"
echo ""

if [ $SUCCESS -eq 0 ]; then
    echo "${RED}No training data generated. Exiting.${NC}"
    exit 1
fi

# Generate LSTMF files
echo "${YELLOW}Converting to LSTMF format...${NC}"
LSTMF_COUNT=0
> "$OUTPUT_DIR/corpus-lstmf.txt"

for gt_file in "$GROUND_TRUTH_DIR"/*.gt.txt; do
    if [ -f "$gt_file" ]; then
        BASE=$(basename "$gt_file" .gt.txt)
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
            printf "Converting %s... " "${BASE}"
            
            # Generate LSTMF
            tesseract "$GROUND_TRUTH_DIR/${BASE}.tif" \
                "$GROUND_TRUTH_DIR/${BASE}" \
                --psm 6 \
                -l ara \
                lstm.train >/dev/null 2>&1
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
                echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/corpus-lstmf.txt"
                LSTMF_COUNT=$((LSTMF_COUNT + 1))
                echo "${GREEN}✓${NC}"
            else
                echo "${RED}✗${NC}"
            fi
        fi
    fi
done

echo ""
echo "${GREEN}Generated $LSTMF_COUNT LSTMF files${NC}"
echo ""

if [ $LSTMF_COUNT -eq 0 ]; then
    echo "${RED}No LSTMF files generated. Cannot proceed with training.${NC}"
    exit 1
fi

# Check base model
if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    BASE_MODEL="ara"
    echo "${GREEN}Using Arabic base model${NC}"
else
    BASE_MODEL="eng"
    echo "${YELLOW}Arabic model not found, using English base model${NC}"
fi

# Start LSTM training
echo ""
echo "${YELLOW}Starting LSTM training...${NC}"
echo "Configuration:"
echo "  Base model: $BASE_MODEL"
echo "  Training samples: $LSTMF_COUNT"
echo "  Max iterations: 2000"
echo "  Target error rate: 0.01"
echo ""

# Run training
echo "${BLUE}Training in progress (this may take several minutes)...${NC}"

lstmtraining \
    --model_output "$OUTPUT_DIR/ckb" \
    --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
    --train_listfile "$OUTPUT_DIR/corpus-lstmf.txt" \
    --max_iterations 2000 \
    --target_error_rate 0.01 \
    --debug_interval 100 >/dev/null 2>&1 &

# Monitor training
PID=$!
echo "Training PID: $PID"
echo ""

# Wait and show progress
COUNTER=0
while kill -0 $PID 2>/dev/null; do
    printf "."
    COUNTER=$((COUNTER + 1))
    if [ $((COUNTER % 60)) -eq 0 ]; then
        echo ""
    fi
    sleep 1
done
echo ""
echo ""

# Check for checkpoint
CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb*.checkpoint 2>/dev/null | head -1)

if [ -n "$CHECKPOINT" ] && [ -f "$CHECKPOINT" ]; then
    echo "${GREEN}✓ Training completed!${NC}"
    echo "Checkpoint: $(basename "$CHECKPOINT")"
    echo ""
    
    # Finalize model
    echo "${YELLOW}Finalizing trained model...${NC}"
    
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
        --model_output "$OUTPUT_DIR/ckb.traineddata" >/dev/null 2>&1
    
    if [ -f "$OUTPUT_DIR/ckb.traineddata" ]; then
        # Copy to tessdata
        cp "$OUTPUT_DIR/ckb.traineddata" "$(pwd)/tessdata/ckb.traineddata"
        
        SIZE=$(du -h "$OUTPUT_DIR/ckb.traineddata" | cut -f1)
        
        echo ""
        echo "${GREEN}════════════════════════════════════════════════════════${NC}"
        echo "${GREEN}✓ SUCCESS! Created ckb.traineddata (${SIZE})${NC}"
        echo "${GREEN}════════════════════════════════════════════════════════${NC}"
        echo ""
        echo "Output files:"
        echo "  - $OUTPUT_DIR/ckb.traineddata"
        echo "  - $(pwd)/tessdata/ckb.traineddata"
        echo ""
        echo "To test the model:"
        echo "  tesseract test_image.tif output -l ckb --psm 6"
        echo ""
    else
        echo "${RED}Failed to create final traineddata file${NC}"
        exit 1
    fi
else
    echo "${RED}Training did not complete successfully${NC}"
    echo "No checkpoint file found"
    exit 1
fi
