#!/bin/sh

# Auto-detect Build Script for Kurdish OCR Model
# This script automatically finds the correct fonts directory and builds ckb.traineddata

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

# Base paths (robust to CWD)
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-auto"
FINAL_MODEL="$WORK_DIR/output/ckb.traineddata"
PROJECT_ROOT="$(cd "$WORK_DIR/.." && pwd)"
TESSDATA_DEST="$PROJECT_ROOT/tessdata/ckb.traineddata"

# Training parameters
MAX_FONTS=15
MAX_ITERATIONS=3000
TARGET_ERROR=0.01
DEBUG_INTERVAL=100

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# ============================================================================
# AUTO-DETECT FONTS DIRECTORY
# ============================================================================

find_fonts_directory() {
    echo "${BLUE}Auto-detecting fonts directory...${NC}"
    
    # List of possible font paths to check - ORDER MATTERS (most specific first)
    POSSIBLE_PATHS="
    $WORK_DIR/fonts/Kurdish Font/Kurdish Font
    $WORK_DIR/fonts/Kurdish Font
    $WORK_DIR/fonts/kurdish
    $WORK_DIR/fonts
    "
    
    FONTS_PATH=""
    
    for path in $POSSIBLE_PATHS; do
        if [ -d "$path" ]; then
            # Check if this directory contains TTF files
            TTF_COUNT=$(ls "$path"/*.ttf 2>/dev/null | wc -l)
            if [ "$TTF_COUNT" -gt 0 ]; then
                FONTS_PATH="$path"
                echo "${GREEN}✓ Found fonts directory: $FONTS_PATH${NC}"
                echo "  Contains $TTF_COUNT TTF files"
                break
            fi
        fi
    done
    
    if [ -z "$FONTS_PATH" ]; then
        echo "${RED}✗ Could not find fonts directory${NC}"
        echo ""
        echo "Searched in:"
        for path in $POSSIBLE_PATHS; do
            echo "  - $path"
        done
        echo ""
        echo "Please ensure Kurdish fonts are placed in one of these locations"
        exit 1
    fi
}

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║     Auto-Build: Kurdish OCR Model (ckb.traineddata)           ║${NC}"
    echo "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_dependencies() {
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Checking Dependencies${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    MISSING=""
    
    for cmd in tesseract text2image lstmtraining; do
        if command -v $cmd >/dev/null 2>&1; then
            echo "${GREEN}✓ $cmd found${NC}"
        else
            echo "${RED}✗ $cmd missing${NC}"
            MISSING="$MISSING $cmd"
        fi
    done
    
    if [ -n "$MISSING" ]; then
        echo ""
        echo "${RED}Missing tools:$MISSING${NC}"
        echo "${YELLOW}Run: wsl sh work/scripts/setup_and_build_ckb.sh${NC}"
        echo "This will install dependencies and build the model"
        exit 1
    fi
}

verify_corpus() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Verifying Corpus${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ ! -f "$CORPUS_FILE" ]; then
        echo "${RED}✗ Corpus file not found: $CORPUS_FILE${NC}"
        exit 1
    fi
    
    LINES=$(wc -l < "$CORPUS_FILE")
    SIZE=$(du -h "$CORPUS_FILE" | cut -f1)
    
    echo "${GREEN}✓ Corpus file found${NC}"
    echo "  Path: $CORPUS_FILE"
    echo "  Lines: $LINES"
    echo "  Size: $SIZE"
}

clean_build() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Cleaning Previous Build${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    rm -rf "$GROUND_TRUTH_DIR"
    mkdir -p "$GROUND_TRUTH_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    echo "${GREEN}✓ Clean environment ready${NC}"
}

generate_training() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Generating Training Data${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo "Using fonts from: $FONTS_PATH"
    echo "Generating with $MAX_FONTS fonts..."
    echo ""
    
    SUCCESS=0
    INDEX=0
    
    for font in $(ls "$FONTS_PATH"/*.ttf 2>/dev/null | head -$MAX_FONTS); do
        FONT_NAME=$(basename "$font" .ttf)
        CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
        
        printf "[%2d/%2d] %-30s " "$((INDEX+1))" "$MAX_FONTS" "${FONT_NAME:0:30}"
        
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.exp${INDEX}" \
            --font="$FONT_NAME" \
            --fonts_dir="$FONTS_PATH" \
            --lang=ara \
            --resolution=300 \
            --ptsize=12 \
            --max_pages=2 >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "${GREEN}✓${NC}"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "${RED}✗${NC}"
        fi
        
        INDEX=$((INDEX + 1))
    done
    
    echo ""
    echo "${GREEN}Generated $SUCCESS training samples${NC}"
    
    if [ $SUCCESS -eq 0 ]; then
        echo "${RED}No training data generated!${NC}"
        exit 1
    fi
}

generate_lstmf() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Converting to LSTMF${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    > "$OUTPUT_DIR/auto-lstmf.txt"
    COUNT=0
    
    for gt in "$GROUND_TRUTH_DIR"/*.gt.txt; do
        if [ -f "$gt" ]; then
            BASE=$(basename "$gt" .gt.txt)
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
                printf "Converting: %-40s " "${BASE:0:40}"
                
                tesseract "$GROUND_TRUTH_DIR/${BASE}.tif" \
                    "$GROUND_TRUTH_DIR/${BASE}" \
                    --psm 6 -l ara lstm.train >/dev/null 2>&1
                
                if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
                    echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/auto-lstmf.txt"
                    COUNT=$((COUNT + 1))
                    echo "${GREEN}✓${NC}"
                else
                    echo "${RED}✗${NC}"
                fi
            fi
        fi
    done
    
    echo ""
    echo "${GREEN}Created $COUNT LSTMF files${NC}"
    
    if [ $COUNT -eq 0 ]; then
        echo "${RED}No LSTMF files created!${NC}"
        exit 1
    fi
}

train_model() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Training Model${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Select base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE="ara"
    elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
        BASE="eng"
    else
        echo "${RED}No base model found!${NC}"
        exit 1
    fi
    
    echo "Base model: $BASE"
    echo "Max iterations: $MAX_ITERATIONS"
    echo ""
    echo "${BLUE}Training in progress...${NC}"
    
    lstmtraining \
        --model_output "$OUTPUT_DIR/ckb_auto" \
        --traineddata "$TESSDATA_PREFIX/${BASE}.traineddata" \
        --train_listfile "$OUTPUT_DIR/auto-lstmf.txt" \
        --max_iterations $MAX_ITERATIONS \
        --target_error_rate $TARGET_ERROR \
        --debug_interval -1 >/dev/null 2>&1 &
    
    PID=$!
    
    # Progress indicator
    while kill -0 $PID 2>/dev/null; do
        printf "."
        sleep 2
    done
    echo ""
    
    # Check for checkpoint
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_auto*.checkpoint 2>/dev/null | head -1)
    
    if [ -z "$CHECKPOINT" ]; then
        echo "${RED}Training failed!${NC}"
        exit 1
    fi
    
    echo "${GREEN}✓ Training complete${NC}"
    echo "Checkpoint: $(basename "$CHECKPOINT")"
}

finalize() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Finalizing Model${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_auto*.checkpoint 2>/dev/null | head -1)
    
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE="ara"
    else
        BASE="eng"
    fi
    
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$TESSDATA_PREFIX/${BASE}.traineddata" \
        --model_output "$FINAL_MODEL" >/dev/null 2>&1
    
    if [ ! -f "$FINAL_MODEL" ]; then
        echo "${RED}Failed to create model!${NC}"
        exit 1
    fi
    
    # Install
    cp "$FINAL_MODEL" "$TESSDATA_DEST"
    
    SIZE=$(du -h "$TESSDATA_DEST" | cut -f1)
    
    echo ""
    echo "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo "${GREEN}✓ SUCCESS! ckb.traineddata created (${SIZE})${NC}"
    echo "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Location: tessdata/ckb.traineddata"
    echo ""
    echo "Usage:"
    echo "  ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_header
    find_fonts_directory
    check_dependencies
    verify_corpus
    clean_build
    generate_training
    generate_lstmf
    train_model
    finalize
}

# Run
main
