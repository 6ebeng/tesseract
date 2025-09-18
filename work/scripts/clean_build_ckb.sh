#!/bin/sh

# Clean Build Script for Kurdish OCR Model (ckb.traineddata)
# This script performs a complete clean build using WSL

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-clean"
FONTS_PATH="$WORK_DIR/fonts/Kurdish Font/Kurdish Font"
FINAL_MODEL="$WORK_DIR/output/ckb.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb.traineddata"

# Training parameters
MAX_FONTS=15
MAX_ITERATIONS=3000
TARGET_ERROR=0.01
DEBUG_INTERVAL=100

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║          Clean Build: Kurdish OCR Model (ckb.traineddata)     ║${NC}"
    echo "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  $1${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_dependencies() {
    print_section "Checking Dependencies"
    
    MISSING_DEPS=""
    
    # Check for required commands
    for cmd in tesseract text2image lstmtraining; do
        if ! command -v $cmd >/dev/null 2>&1; then
            echo "${RED}✗ Missing: $cmd${NC}"
            MISSING_DEPS="$MISSING_DEPS $cmd"
        else
            VERSION=$(eval "$cmd --version 2>&1 | head -1" || echo "unknown")
            echo "${GREEN}✓ Found: $cmd${NC}"
            echo "  Version: $VERSION"
        fi
    done
    
    if [ -n "$MISSING_DEPS" ]; then
        echo ""
        echo "${RED}Error: Missing required dependencies:$MISSING_DEPS${NC}"
        echo "Please install Tesseract and its training tools"
        exit 1
    fi
}

clean_previous_build() {
    print_section "Cleaning Previous Build"
    
    echo "Removing old training data..."
    
    # Clean directories
    if [ -d "$GROUND_TRUTH_DIR" ]; then
        rm -rf "$GROUND_TRUTH_DIR"
        echo "  ${YELLOW}Cleaned: ground-truth-clean/${NC}"
    fi
    
    # Clean specific output files
    for file in "$OUTPUT_DIR/ckb.traineddata" \
                "$OUTPUT_DIR/ckb_"*.checkpoint \
                "$OUTPUT_DIR/corpus-lstmf.txt"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            echo "  ${YELLOW}Removed: $(basename $file)${NC}"
        fi
    done
    
    echo "${GREEN}✓ Clean build environment ready${NC}"
}

verify_inputs() {
    print_section "Verifying Input Files"
    
    # Check corpus file
    if [ ! -f "$CORPUS_FILE" ]; then
        echo "${RED}✗ Corpus file not found: $CORPUS_FILE${NC}"
        exit 1
    fi
    
    CORPUS_LINES=$(wc -l < "$CORPUS_FILE")
    CORPUS_SIZE=$(du -h "$CORPUS_FILE" | cut -f1)
    echo "${GREEN}✓ Corpus file found${NC}"
    echo "  Path: $CORPUS_FILE"
    echo "  Lines: $CORPUS_LINES"
    echo "  Size: $CORPUS_SIZE"
    
    # Check fonts directory
    if [ ! -d "$FONTS_PATH" ]; then
        echo "${RED}✗ Fonts directory not found: $FONTS_PATH${NC}"
        exit 1
    fi
    
    FONT_COUNT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | wc -l || echo 0)
    if [ "$FONT_COUNT" -eq 0 ]; then
        echo "${RED}✗ No TTF fonts found in $FONTS_PATH${NC}"
        exit 1
    fi
    
    echo "${GREEN}✓ Fonts directory found${NC}"
    echo "  Path: $FONTS_PATH"
    echo "  Available fonts: $FONT_COUNT"
    echo "  Will use: $MAX_FONTS fonts for training"
}

generate_training_images() {
    print_section "Generating Training Images"
    
    # Create output directory
    mkdir -p "$GROUND_TRUTH_DIR"
    
    echo "Generating images with $MAX_FONTS different fonts..."
    echo ""
    
    SUCCESS=0
    FAILED=0
    FONT_INDEX=0
    
    # Process fonts
    for font in $(ls "$FONTS_PATH"/*.ttf | head -$MAX_FONTS); do
        FONT_NAME=$(basename "$font" .ttf)
        CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
        
        printf "  [%2d/%2d] %-30s " "$((FONT_INDEX+1))" "$MAX_FONTS" "${FONT_NAME:0:30}"
        
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
            --max_pages=2 >/dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "${GREEN}✓${NC}"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "${RED}✗${NC}"
            FAILED=$((FAILED + 1))
        fi
        
        FONT_INDEX=$((FONT_INDEX + 1))
    done
    
    echo ""
    echo "Results:"
    echo "  ${GREEN}Success: $SUCCESS${NC}"
    if [ $FAILED -gt 0 ]; then
        echo "  ${RED}Failed: $FAILED${NC}"
    fi
    
    if [ $SUCCESS -eq 0 ]; then
        echo "${RED}✗ No training images generated. Cannot continue.${NC}"
        exit 1
    fi
}

generate_lstmf_files() {
    print_section "Generating LSTMF Training Files"
    
    LSTMF_COUNT=0
    LSTMF_FAILED=0
    > "$OUTPUT_DIR/corpus-lstmf.txt"
    
    echo "Converting training images to LSTMF format..."
    echo ""
    
    # Process each ground truth file
    TOTAL_GT=$(ls "$GROUND_TRUTH_DIR"/*.gt.txt 2>/dev/null | wc -l)
    CURRENT=0
    
    for gt_file in "$GROUND_TRUTH_DIR"/*.gt.txt; do
        if [ -f "$gt_file" ]; then
            BASE=$(basename "$gt_file" .gt.txt)
            CURRENT=$((CURRENT + 1))
            
            printf "  [%2d/%2d] %-40s " "$CURRENT" "$TOTAL_GT" "${BASE:0:40}"
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
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
                    LSTMF_FAILED=$((LSTMF_FAILED + 1))
                    echo "${RED}✗${NC}"
                fi
            else
                echo "${YELLOW}No TIF${NC}"
            fi
        fi
    done
    
    echo ""
    echo "Results:"
    echo "  ${GREEN}Success: $LSTMF_COUNT LSTMF files${NC}"
    if [ $LSTMF_FAILED -gt 0 ]; then
        echo "  ${RED}Failed: $LSTMF_FAILED${NC}"
    fi
    
    if [ $LSTMF_COUNT -eq 0 ]; then
        echo "${RED}✗ No LSTMF files generated. Cannot continue.${NC}"
        exit 1
    fi
}

train_model() {
    print_section "Training LSTM Model"
    
    # Determine base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE_MODEL="ara"
        echo "${GREEN}✓ Using Arabic base model${NC}"
    elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
        BASE_MODEL="eng"
        echo "${YELLOW}⚠ Arabic model not found, using English base model${NC}"
    else
        echo "${RED}✗ No base model found (ara or eng)${NC}"
        exit 1
    fi
    
    echo ""
    echo "Training Configuration:"
    echo "  Base model: $BASE_MODEL"
    echo "  Training samples: $LSTMF_COUNT"
    echo "  Max iterations: $MAX_ITERATIONS"
    echo "  Target error rate: $TARGET_ERROR"
    echo "  Debug interval: $DEBUG_INTERVAL"
    echo ""
    
    # Start training
    echo "${BLUE}Starting LSTM training...${NC}"
    echo "This may take several minutes. Progress will be shown below:"
    echo ""
    
    # Run training with progress monitoring
    lstmtraining \
        --model_output "$OUTPUT_DIR/ckb" \
        --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
        --train_listfile "$OUTPUT_DIR/corpus-lstmf.txt" \
        --max_iterations $MAX_ITERATIONS \
        --target_error_rate $TARGET_ERROR \
        --debug_interval $DEBUG_INTERVAL 2>&1 | while IFS= read -r line; do
            if echo "$line" | grep -q "Iteration"; then
                # Extract iteration info
                printf "\r  ${YELLOW}%s${NC}                    " "$(echo "$line" | cut -c1-70)"
            elif echo "$line" | grep -q "error rate"; then
                printf "\r  ${GREEN}%s${NC}                    " "$(echo "$line" | cut -c1-70)"
            fi
        done
    
    echo ""
    echo ""
    
    # Check for checkpoint
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb*.checkpoint 2>/dev/null | head -1)
    
    if [ -z "$CHECKPOINT" ] || [ ! -f "$CHECKPOINT" ]; then
        echo "${RED}✗ Training failed - no checkpoint created${NC}"
        exit 1
    fi
    
    echo "${GREEN}✓ Training completed successfully${NC}"
    echo "  Checkpoint: $(basename "$CHECKPOINT")"
}

finalize_model() {
    print_section "Finalizing Model"
    
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb*.checkpoint 2>/dev/null | head -1)
    
    if [ -z "$CHECKPOINT" ] || [ ! -f "$CHECKPOINT" ]; then
        echo "${RED}✗ No checkpoint found to finalize${NC}"
        exit 1
    fi
    
    echo "Creating final traineddata from checkpoint..."
    echo "  Checkpoint: $(basename "$CHECKPOINT")"
    
    # Determine base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE_MODEL="ara"
    else
        BASE_MODEL="eng"
    fi
    
    # Stop training and create final model
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
        --model_output "$FINAL_MODEL" >/dev/null 2>&1
    
    if [ ! -f "$FINAL_MODEL" ]; then
        echo "${RED}✗ Failed to create final model${NC}"
        exit 1
    fi
    
    MODEL_SIZE=$(du -h "$FINAL_MODEL" | cut -f1)
    echo "${GREEN}✓ Model created successfully${NC}"
    echo "  Size: $MODEL_SIZE"
}

install_model() {
    print_section "Installing Model"
    
    # Copy to tessdata directory
    if [ -f "$FINAL_MODEL" ]; then
        cp "$FINAL_MODEL" "$TESSDATA_DEST"
        echo "${GREEN}✓ Installed to: tessdata/ckb.traineddata${NC}"
        
        # Try to install to system (may need sudo)
        if [ -w "$TESSDATA_PREFIX" ]; then
            cp "$FINAL_MODEL" "$TESSDATA_PREFIX/ckb.traineddata"
            echo "${GREEN}✓ Installed to system: $TESSDATA_PREFIX/ckb.traineddata${NC}"
        else
            echo "${YELLOW}⚠ System installation requires sudo:${NC}"
            echo "  sudo cp $FINAL_MODEL $TESSDATA_PREFIX/ckb.traineddata"
        fi
    else
        echo "${RED}✗ Model file not found${NC}"
        exit 1
    fi
}

print_summary() {
    print_section "Build Complete"
    
    echo "${GREEN}✓ Successfully built ckb.traineddata${NC}"
    echo ""
    echo "Model Information:"
    echo "  Location: $TESSDATA_DEST"
    echo "  Size: $(du -h "$TESSDATA_DEST" | cut -f1)"
    echo "  Training samples: $LSTMF_COUNT"
    echo "  Fonts used: $SUCCESS"
    echo ""
    echo "Usage:"
    echo "  ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
    echo ""
    echo "Testing:"
    echo "  1. Create a test image with Kurdish text"
    echo "  2. Run: tesseract test.png result -l ckb"
    echo "  3. Check result.txt for recognized text"
    echo ""
    echo "${GREEN}Build completed successfully!${NC}"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header
    
    # Execute build steps
    check_dependencies
    clean_previous_build
    verify_inputs
    generate_training_images
    generate_lstmf_files
    train_model
    finalize_model
    install_model
    print_summary
}

# Run main function
main
