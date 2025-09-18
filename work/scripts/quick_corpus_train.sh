#!/bin/bash

# Quick training script using your specific corpus text with existing fonts

set -e

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR=/mnt/c/tesseract/work
CORPUS_FILE=$WORK_DIR/corpus/ckb.training_text
OUTPUT_DIR=$WORK_DIR/output
GROUND_TRUTH_DIR=$WORK_DIR/ground-truth-quick
FONTS_PATH="/mnt/c/tesseract/work/fonts/kurdish"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Quick Kurdish OCR Training with Your Corpus         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"

# Create directories
mkdir -p $GROUND_TRUTH_DIR
mkdir -p $OUTPUT_DIR

# Clean previous data
echo -e "${YELLOW}Cleaning previous data...${NC}"
rm -rf $GROUND_TRUTH_DIR/*

# Verify corpus
echo -e "${BLUE}Using corpus from: $CORPUS_FILE${NC}"
echo "First line of corpus:"
head -1 "$CORPUS_FILE"
echo ""

# Count fonts
FONT_COUNT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | wc -l)
echo -e "${GREEN}Found $FONT_COUNT fonts${NC}"

# Select 20 fonts evenly distributed
echo -e "${YELLOW}Selecting 20 representative fonts...${NC}"
SELECTED_FONTS=()
STEP=$((FONT_COUNT / 20))
INDEX=0

ls "$FONTS_PATH"/*.ttf | while read font; do
    if [ $((INDEX % STEP)) -eq 0 ] && [ ${#SELECTED_FONTS[@]} -lt 20 ]; then
        SELECTED_FONTS+=("$font")
        echo "Selected: $(basename "$font")"
    fi
    ((INDEX++))
done | head -20

# Generate training data with first 10 fonts
echo -e "${YELLOW}\nGenerating training data...${NC}"
SUCCESS=0
FONT_INDEX=0

ls "$FONTS_PATH"/*.ttf | head -20 | while read font; do
    FONT_NAME=$(basename "$font" .ttf)
    CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-30)
    
    echo "Processing: $FONT_NAME"
    
    # Generate training image
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb_${CLEAN_NAME}" \
        --font="$FONT_NAME" \
        --fonts_dir="$FONTS_PATH" \
        --lang=ara \
        --linedata_only \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 2>/dev/null && ((SUCCESS++)) || true
    
    ((FONT_INDEX++))
done

echo -e "${GREEN}Generated $SUCCESS training samples${NC}"

# Generate LSTMF files
echo -e "${YELLOW}\nGenerating LSTMF files...${NC}"
LSTMF_COUNT=0
> $OUTPUT_DIR/quick-lstmf.txt

for gt_file in $GROUND_TRUTH_DIR/*.gt.txt; do
    if [ -f "$gt_file" ]; then
        BASE=$(basename "$gt_file" .gt.txt)
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
            # Generate LSTMF
            tesseract "$GROUND_TRUTH_DIR/${BASE}.tif" \
                "$GROUND_TRUTH_DIR/${BASE}" \
                --psm 6 \
                -l eng \
                lstm.train 2>/dev/null || continue
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
                echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> $OUTPUT_DIR/quick-lstmf.txt
                ((LSTMF_COUNT++))
            fi
        fi
    fi
done

echo -e "${GREEN}Generated $LSTMF_COUNT LSTMF files${NC}"

if [ $LSTMF_COUNT -eq 0 ]; then
    echo -e "${YELLOW}No LSTMF files generated. Checking existing training data...${NC}"
    
    # Use existing LSTMF files if available
    if ls $WORK_DIR/training/*.lstmf 2>/dev/null | head -1 > /dev/null; then
        ls $WORK_DIR/training/*.lstmf > $OUTPUT_DIR/quick-lstmf.txt
        LSTMF_COUNT=$(wc -l < $OUTPUT_DIR/quick-lstmf.txt)
        echo -e "${GREEN}Found $LSTMF_COUNT existing LSTMF files${NC}"
    fi
fi

if [ $LSTMF_COUNT -eq 0 ]; then
    echo "No training data available. Exiting."
    exit 1
fi

# Start training
echo -e "${YELLOW}\nStarting training...${NC}"
echo "Parameters:"
echo "  Iterations: 2000"
echo "  Target error: 0.01"
echo "  LSTMF files: $LSTMF_COUNT"

# Run training
lstmtraining \
    --model_output $OUTPUT_DIR/ckb_corpus \
    --traineddata $TESSDATA_PREFIX/eng.traineddata \
    --train_listfile $OUTPUT_DIR/quick-lstmf.txt \
    --max_iterations 2000 \
    --target_error_rate 0.01 \
    --debug_interval -1 &

# Monitor progress
PID=$!
while kill -0 $PID 2>/dev/null; do
    sleep 5
    echo -n "."
done
echo ""

# Check for checkpoint
if ls $OUTPUT_DIR/ckb_corpus*.checkpoint 2>/dev/null | head -1 > /dev/null; then
    CHECKPOINT=$(ls -t $OUTPUT_DIR/ckb_corpus*.checkpoint 2>/dev/null | head -1)
    echo -e "${GREEN}Training complete! Checkpoint: $(basename $CHECKPOINT)${NC}"
    
    # Finalize model
    echo -e "${YELLOW}Finalizing model...${NC}"
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --model_output $OUTPUT_DIR/ckb_corpus.traineddata 2>/dev/null
    
    if [ -f "$OUTPUT_DIR/ckb_corpus.traineddata" ]; then
        # Install model
        echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_corpus.traineddata $TESSDATA_PREFIX/ckb_corpus.traineddata
        cp $OUTPUT_DIR/ckb_corpus.traineddata /mnt/c/tesseract/tessdata/ckb_corpus.traineddata
        
        SIZE=$(du -h $OUTPUT_DIR/ckb_corpus.traineddata | cut -f1)
        echo -e "${GREEN}✓ Model created: ckb_corpus.traineddata ($SIZE)${NC}"
        echo -e "${GREEN}✓ Installed to WSL and Windows${NC}"
        echo ""
        echo "Usage: tesseract image.tif output -l ckb_corpus --psm 6"
    fi
else
    echo "Training did not complete successfully."
fi
