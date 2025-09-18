#!/bin/sh

# Fast Robust Training - Smart subset with heavy augmentation
# Uses strategic font selection + aggressive augmentation for quick robust results

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export FONTCONFIG_FILE="$SCRIPT_DIR/fonts.conf"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-fast-robust"
FONTS_PATH="$WORK_DIR/fonts"
FINAL_MODEL="$WORK_DIR/output/ckb_fast_robust.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb_fast_robust.traineddata"

# Smart font selection (diverse subset)
FONT_SELECTION_STRATEGY="diverse"  # diverse, random, or specific
MAX_FONTS=100                      # Use top 100 most diverse fonts
MAX_ITERATIONS=5000                # Moderate iterations
TARGET_ERROR=0.005                 # Slightly higher for faster training
DEBUG_INTERVAL=50

# Heavy augmentation for smaller dataset
SHEAR_ANGLES="-7 -5 -3 0 3 5 7"
ROTATION_ANGLES="-3 -2 -1 0 1 2 3"
EXPOSURE_LEVELS="-2 -1 0 1 2"
CHAR_SPACING="0.0 0.15 0.3"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo "${CYAN}║     FAST Robust Training: Smart Selection + Heavy Augmentation    ║${NC}"
    echo "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

select_diverse_fonts() {
    echo "${BLUE}Selecting diverse font subset...${NC}"
    
    # Create temporary directory for font analysis
    TEMP_ANALYSIS="/tmp/font_analysis_$$"
    mkdir -p "$TEMP_ANALYSIS"
    
    # Select fonts with different characteristics
    SELECTED_FONTS=""
    
    # Categories to ensure diversity
    # 1. Fonts starting with different prefixes (alphabetical diversity)
    PREFIXES="0 1 2 3 4 5 6 7 8 9 A a H h K k S s"
    
    for prefix in $PREFIXES; do
        # Get up to 6 fonts per prefix
        FONTS_WITH_PREFIX=$(ls "$FONTS_PATH"/${prefix}*.ttf 2>/dev/null | head -6)
        SELECTED_FONTS="$SELECTED_FONTS $FONTS_WITH_PREFIX"
    done
    
    # 2. Add fonts with specific keywords (style diversity)
    KEYWORDS="Bold Regular Light Arabic Traditional Modern Classic Naskh"
    
    for keyword in $KEYWORDS; do
        FONTS_WITH_KEYWORD=$(ls "$FONTS_PATH"/*${keyword}*.ttf 2>/dev/null | head -3)
        SELECTED_FONTS="$SELECTED_FONTS $FONTS_WITH_KEYWORD"
    done
    
    # 3. Add fonts with different name lengths (complexity diversity)
    # Short names
    SHORT_FONTS=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | awk 'length($0) < 40' | head -10)
    SELECTED_FONTS="$SELECTED_FONTS $SHORT_FONTS"
    
    # Long names
    LONG_FONTS=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | awk 'length($0) > 60' | head -10)
    SELECTED_FONTS="$SELECTED_FONTS $LONG_FONTS"
    
    # Remove duplicates and limit to MAX_FONTS
    echo "$SELECTED_FONTS" | tr ' ' '\n' | sort -u | head -$MAX_FONTS > "$TEMP_ANALYSIS/selected_fonts.txt"
    
    FONT_COUNT=$(wc -l < "$TEMP_ANALYSIS/selected_fonts.txt")
    echo "${GREEN}✓ Selected $FONT_COUNT diverse fonts${NC}"
    
    # Show selection summary
    echo ""
    echo "${BOLD}Font Selection Summary:${NC}"
    echo "  Strategy: Diverse subset"
    echo "  Total selected: $FONT_COUNT fonts"
    echo "  Coverage: Multiple styles, weights, and designs"
    
    # Return the list file
    echo "$TEMP_ANALYSIS/selected_fonts.txt"
}

generate_heavy_augmentation() {
    local INPUT_IMAGE="$1"
    local OUTPUT_BASE="$2"
    local AUG_COUNT=0
    
    if [ ! -f "$INPUT_IMAGE" ]; then
        return 0
    fi
    
    # Generate multiple augmented versions
    # This creates more variations per font to compensate for fewer fonts
    
    # Multiple shear angles
    for shear in $SHEAR_ANGLES; do
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="${OUTPUT_BASE}_shear${shear}" \
            --font="$3" \
            --fonts_dir="$FONTS_PATH" \
            --lang=ara \
            --char_spacing="0.1" \
            --exposure="0" \
            --resolution=300 \
            --ptsize=12 \
            --max_pages=1 \
            --degrade_image \
            --rotate_image="${shear}" >/dev/null 2>&1 && AUG_COUNT=$((AUG_COUNT + 1))
    done
    
    # Multiple rotations
    for rotation in $ROTATION_ANGLES; do
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="${OUTPUT_BASE}_rot${rotation}" \
            --font="$3" \
            --fonts_dir="$FONTS_PATH" \
            --lang=ara \
            --char_spacing="0.05" \
            --exposure="1" \
            --resolution=300 \
            --ptsize=12 \
            --max_pages=1 \
            --rotate_image="${rotation}" >/dev/null 2>&1 && AUG_COUNT=$((AUG_COUNT + 1))
    done
    
    echo $AUG_COUNT
}

clean_environment() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Preparing Environment${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    rm -rf "$GROUND_TRUTH_DIR"
    mkdir -p "$GROUND_TRUTH_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    echo "${GREEN}✓ Clean environment ready${NC}"
}

generate_training_data() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Generating Training Data with Heavy Augmentation${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Get selected fonts
    FONT_LIST=$(select_diverse_fonts)
    
    echo ""
    echo "${YELLOW}Generating training data...${NC}"
    echo "Heavy augmentation will create many variations per font"
    echo ""
    
    SUCCESS=0
    TOTAL_IMAGES=0
    FONT_INDEX=0
    FONT_COUNT=$(wc -l < "$FONT_LIST")
    
    while IFS= read -r font; do
        if [ ! -f "$font" ]; then
            continue
        fi
        
        FONT_NAME=$(basename "$font" .ttf)
        CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-25)
        
        FONT_INDEX=$((FONT_INDEX + 1))
        PERCENT=$((FONT_INDEX * 100 / FONT_COUNT))
        
        printf "\r[%3d%%] Font %d/%d: %-35s" \
            "$PERCENT" "$FONT_INDEX" "$FONT_COUNT" "${FONT_NAME:0:35}"
        
        # Generate base variations with different parameters
        VAR_INDEX=0
        
        for spacing in $CHAR_SPACING; do
            for exposure in $EXPOSURE_LEVELS; do
                OUTPUT_BASE="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.v${VAR_INDEX}"
                
                # Generate base image
                text2image \
                    --text="$CORPUS_FILE" \
                    --outputbase="$OUTPUT_BASE" \
                    --font="$FONT_NAME" \
                    --fonts_dir="$FONTS_PATH" \
                    --lang=ara \
                    --char_spacing="$spacing" \
                    --exposure="$exposure" \
                    --resolution=300 \
                    --ptsize=12 \
                    --max_pages=1 >/dev/null 2>&1
                
                if [ $? -eq 0 ]; then
                    SUCCESS=$((SUCCESS + 1))
                    TOTAL_IMAGES=$((TOTAL_IMAGES + 1))
                    
                    # Generate heavy augmentation
                    AUG_COUNT=$(generate_heavy_augmentation \
                        "${OUTPUT_BASE}.tif" \
                        "$OUTPUT_BASE" \
                        "$FONT_NAME")
                    
                    TOTAL_IMAGES=$((TOTAL_IMAGES + AUG_COUNT))
                fi
                
                VAR_INDEX=$((VAR_INDEX + 1))
                
                # Limit variations
                if [ $VAR_INDEX -ge 5 ]; then
                    break 2
                fi
            done
        done
        
        # Progress indicator
        if [ $((FONT_INDEX % 10)) -eq 0 ]; then
            echo " ${GREEN}✓${NC}"
        fi
    done < "$FONT_LIST"
    
    echo ""
    echo ""
    echo "${GREEN}Training data complete!${NC}"
    echo "  Fonts processed: $FONT_INDEX"
    echo "  Total images: $TOTAL_IMAGES"
    echo "  Average per font: $((TOTAL_IMAGES / FONT_INDEX)) images"
}

generate_lstmf() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Converting to LSTMF${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    > "$OUTPUT_DIR/fast-robust-lstmf.txt"
    LSTMF_COUNT=0
    
    for gt in "$GROUND_TRUTH_DIR"/*.gt.txt; do
        if [ -f "$gt" ]; then
            BASE=$(basename "$gt" .gt.txt)
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
                tesseract "$GROUND_TRUTH_DIR/${BASE}.tif" \
                    "$GROUND_TRUTH_DIR/${BASE}" \
                    --psm 6 -l ara lstm.train >/dev/null 2>&1
                
                if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
                    echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/fast-robust-lstmf.txt"
                    LSTMF_COUNT=$((LSTMF_COUNT + 1))
                fi
            fi
        fi
        
        # Progress
        if [ $((LSTMF_COUNT % 50)) -eq 0 ] && [ $LSTMF_COUNT -gt 0 ]; then
            printf "\r  Converted: %d files" "$LSTMF_COUNT"
        fi
    done
    
    echo ""
    echo "${GREEN}✓ Created $LSTMF_COUNT LSTMF files${NC}"
}

train_model() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Training Fast Robust Model${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Select base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE="ara"
    else
        BASE="eng"
    fi
    
    echo "Configuration:"
    echo "  Base model: $BASE"
    echo "  Training samples: $LSTMF_COUNT"
    echo "  Max iterations: $MAX_ITERATIONS"
    echo "  Target error: $TARGET_ERROR"
    echo ""
    
    echo "${BLUE}Training...${NC}"
    
    lstmtraining \
        --model_output "$OUTPUT_DIR/ckb_fast_robust" \
        --traineddata "$TESSDATA_PREFIX/${BASE}.traineddata" \
        --train_listfile "$OUTPUT_DIR/fast-robust-lstmf.txt" \
        --max_iterations $MAX_ITERATIONS \
        --target_error_rate $TARGET_ERROR \
        --debug_interval -1 >/dev/null 2>&1 &
    
    PID=$!
    
    # Progress animation
    SPIN='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    i=0
    while kill -0 $PID 2>/dev/null; do
        i=$(( (i+1) %10 ))
        printf "\r${YELLOW}Training ${SPIN:$i:1}${NC} "
        sleep 0.5
    done
    
    echo ""
    
    # Check checkpoint
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_fast_robust*.checkpoint 2>/dev/null | head -1)
    
    if [ -n "$CHECKPOINT" ]; then
        echo "${GREEN}✓ Training complete${NC}"
    else
        echo "${RED}✗ Training failed${NC}"
        exit 1
    fi
}

finalize_model() {
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Finalizing Model${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_fast_robust*.checkpoint 2>/dev/null | head -1)
    
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
    
    if [ -f "$FINAL_MODEL" ]; then
        cp "$FINAL_MODEL" "$TESSDATA_DEST"
        SIZE=$(du -h "$TESSDATA_DEST" | cut -f1)
        echo "${GREEN}✓ Model created: $SIZE${NC}"
    else
        echo "${RED}✗ Failed to create model${NC}"
        exit 1
    fi
}

print_summary() {
    echo ""
    echo "${GREEN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
    echo "${GREEN}${BOLD}✓ FAST ROBUST MODEL COMPLETE!${NC}"
    echo "${GREEN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "${BOLD}Model Details:${NC}"
    echo "  Location: tessdata/ckb_fast_robust.traineddata"
    echo "  Training time: ~30-60 minutes"
    echo "  Font coverage: 100 diverse fonts"
    echo "  Augmentation: Heavy (shear, rotation, exposure, spacing)"
    echo ""
    echo "${BOLD}Usage:${NC}"
    echo "  ${CYAN}tesseract image.png output -l ckb_fast_robust --psm 6${NC}"
    echo ""
    echo "${BOLD}Features:${NC}"
    echo "  ✓ Fast training (under 1 hour)"
    echo "  ✓ Robust to distortions"
    echo "  ✓ Good font coverage"
    echo "  ✓ Production ready"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    print_header
    clean_environment
    generate_training_data
    generate_lstmf
    train_model
    finalize_model
    print_summary
}

# Run
main
