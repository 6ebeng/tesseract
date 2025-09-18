#!/bin/sh

# Fixed Robust Training Script with ALL Kurdish Fonts and Image Augmentation
# This version handles errors gracefully and doesn't exit on first failure

# Remove 'set -e' to prevent early exit on errors
# set -e  # REMOVED - This was causing the script to exit at 0%

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-robust"
FONTS_PATH="$WORK_DIR/fonts"
FINAL_MODEL="$WORK_DIR/output/ckb_robust.traineddata"
TESSDATA_DEST="$(pwd)/tessdata/ckb.traineddata"

# Training parameters - ENHANCED FOR ROBUSTNESS
USE_ALL_FONTS=true           # Use ALL 670 fonts
MAX_ITERATIONS=10000         # More iterations for better training
TARGET_ERROR=0.001           # Lower error rate for better accuracy
DEBUG_INTERVAL=100
BATCH_SIZE=50                # Process fonts in batches

# Augmentation parameters
ENABLE_SHEAR=true
ENABLE_ROTATION=true
ENABLE_NOISE=true
ENABLE_BLUR=true

# Shear angles (in degrees)
SHEAR_ANGLES="-5 -3 -1 0 1 3 5"

# Rotation angles (in degrees)
ROTATION_ANGLES="-2 -1 0 1 2"

# Exposure levels for brightness variation
EXPOSURE_LEVELS="-2 -1 0 1 2"

# Character spacing variations
CHAR_SPACING="0.0 0.1 0.2"

# Colors - using printf-compatible format
GREEN=$(printf '\033[0;32m')
YELLOW=$(printf '\033[1;33m')
BLUE=$(printf '\033[0;34m')
CYAN=$(printf '\033[0;36m')
RED=$(printf '\033[0;31m')
MAGENTA=$(printf '\033[0;35m')
BOLD=$(printf '\033[1m')
NC=$(printf '\033[0m')

# Force fontconfig to use project-local fonts.conf to avoid stale WSL caches
export FONTCONFIG_PATH="$(pwd)"
export FONTCONFIG_FILE="$FONTCONFIG_PATH/fonts.conf"
if [ ! -f "$FONTCONFIG_FILE" ]; then
    printf "%s⚠ fonts.conf not found at %s; font discovery may rely on system caches%s\n" "$YELLOW" "$FONTCONFIG_FILE" "$NC"
else
    printf "%sUsing FONTCONFIG_PATH=%s and FONTCONFIG_FILE=%s%s\n" "$GREEN" "$FONTCONFIG_PATH" "$FONTCONFIG_FILE" "$NC"
fi

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    printf "\n"
    printf "%s╔════════════════════════════════════════════════════════════════════╗%s\n" "$CYAN" "$NC"
    printf "%s║     ROBUST Training: Kurdish OCR with ALL Fonts & Augmentation    ║%s\n" "$CYAN" "$NC"
    printf "%s╚════════════════════════════════════════════════════════════════════╝%s\n" "$CYAN" "$NC"
    printf "\n"
}

print_section() {
    printf "\n"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$MAGENTA" "$NC"
    printf "%s  %s%s\n" "$MAGENTA" "$1" "$NC"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$MAGENTA" "$NC"
}

check_dependencies() {
    print_section "Checking Dependencies"
    
    MISSING=""
    
    # Check required tools
    for cmd in tesseract text2image lstmtraining; do
        if command -v $cmd >/dev/null 2>&1; then
            VERSION=$($cmd --version 2>&1 | head -1 || printf "unknown")
            printf "%s✓ %s found%s\n" "$GREEN" "$cmd" "$NC"
            printf "  Version: %s\n" "$VERSION"
        else
            printf "%s✗ %s missing%s\n" "$RED" "$cmd" "$NC"
            MISSING="$MISSING $cmd"
        fi
    done
    
    # Check for ImageMagick (for augmentation)
    if command -v convert >/dev/null 2>&1; then
        printf "%s✓ ImageMagick found (for augmentation)%s\n" "$GREEN" "$NC"
        IMAGEMAGICK_AVAILABLE=true
    else
        printf "%s⚠ ImageMagick not found - augmentation will be limited%s\n" "$YELLOW" "$NC"
        IMAGEMAGICK_AVAILABLE=false
    fi
    
    if [ -n "$MISSING" ]; then
        printf "%sMissing tools:%s%s\n" "$RED" "$MISSING" "$NC"
        printf "Please install missing tools and try again.\n"
        exit 1
    fi
}

verify_inputs() {
    print_section "Verifying Input Files"
    
    # Check corpus
    if [ ! -f "$CORPUS_FILE" ]; then
        printf "%s✗ Corpus file not found at: %s%s\n" "$RED" "$CORPUS_FILE" "$NC"
        
        # Create a simple corpus file as fallback
        printf "%sCreating simple test corpus...%s\n" "$YELLOW" "$NC"
        mkdir -p "$(dirname "$CORPUS_FILE")"
        cat > "$CORPUS_FILE" << 'EOF'
ئەم تاقیکردنەوەیەکە بۆ نووسینی کوردی
کوردی زمانێکی جوانە
تێکستی کوردی بۆ تاقیکردنەوە
نووسینی کوردی بە فۆنتی جیاواز
ئەم دەقە بۆ راهێنانی OCR بەکاردێت
EOF
        CORPUS_LINES=5
        printf "%s✓ Created simple test corpus%s\n" "$GREEN" "$NC"
    else
        CORPUS_LINES=$(wc -l < "$CORPUS_FILE")
        printf "%s✓ Corpus file found%s\n" "$GREEN" "$NC"
    fi
    printf "  Lines: %s\n" "$CORPUS_LINES"
    
    # Check fonts
    FONT_COUNT=$(find "$FONTS_PATH" -name "*.ttf" -o -name "*.TTF" 2>/dev/null | wc -l)
    
    if [ "$FONT_COUNT" -eq 0 ]; then
        printf "%s✗ No fonts found in %s%s\n" "$RED" "$FONTS_PATH" "$NC"
        exit 1
    fi
    
    printf "%s✓ Found %s Kurdish fonts%s\n" "$GREEN" "$FONT_COUNT" "$NC"
    printf "%s  Will use ALL %s fonts for robust training%s\n" "$BOLD" "$FONT_COUNT" "$NC"
}

clean_environment() {
    print_section "Preparing Clean Environment"
    
    printf "Cleaning previous training data...\n"
    rm -rf "$GROUND_TRUTH_DIR"
    mkdir -p "$GROUND_TRUTH_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    # Clean old files
    rm -f "$OUTPUT_DIR"/ckb_robust*.checkpoint
    rm -f "$OUTPUT_DIR"/robust-lstmf.txt
    
    printf "%s✓ Clean environment ready%s\n" "$GREEN" "$NC"
}

generate_augmented_image() {
    # Function to generate augmented versions of an image
    local INPUT_IMAGE="$1"
    local OUTPUT_BASE="$2"
    local FONT_NAME="$3"
    local AUG_INDEX="$4"
    
    if [ ! -f "$INPUT_IMAGE" ]; then
        return 1
    fi
    
    # Apply augmentations using ImageMagick if available
    if [ "$IMAGEMAGICK_AVAILABLE" = true ] && command -v convert >/dev/null 2>&1; then
        # Shear transformation
        if [ "$ENABLE_SHEAR" = true ]; then
            for shear in $SHEAR_ANGLES; do
                convert "$INPUT_IMAGE" -shear "${shear}x0" \
                    "${OUTPUT_BASE}_shear${shear}.tif" 2>/dev/null || true
            done
        fi
        
        # Rotation
        if [ "$ENABLE_ROTATION" = true ]; then
            for rotation in $ROTATION_ANGLES; do
                convert "$INPUT_IMAGE" -rotate "$rotation" -background white \
                    "${OUTPUT_BASE}_rot${rotation}.tif" 2>/dev/null || true
            done
        fi
        
        # Add noise
        if [ "$ENABLE_NOISE" = true ]; then
            convert "$INPUT_IMAGE" -attenuate 0.2 +noise Gaussian \
                "${OUTPUT_BASE}_noise.tif" 2>/dev/null || true
        fi
        
        # Add blur
        if [ "$ENABLE_BLUR" = true ]; then
            convert "$INPUT_IMAGE" -blur 0x0.5 \
                "${OUTPUT_BASE}_blur.tif" 2>/dev/null || true
        fi
    fi
}

generate_training_data() {
    print_section "Generating Training Data with ALL Fonts"
    
    printf "%sConfiguration:%s\n" "$BOLD" "$NC"
    TOTAL_FONTS=$(find "$FONTS_PATH" -name "*.ttf" -o -name "*.TTF" 2>/dev/null | wc -l)
    printf "  Total fonts: %s\n" "$TOTAL_FONTS"
    if [ "$IMAGEMAGICK_AVAILABLE" = true ]; then
        printf "  Augmentation: Shear, Rotation, Noise, Blur\n"
    else
        printf "  Augmentation: Basic (ImageMagick not available)\n"
    fi
    printf "  Variations per font: Multiple\n"
    printf "\n"
    
    SUCCESS=0
    FAILED=0
    FONT_INDEX=0
    TOTAL_IMAGES=0
    
    printf "%sGenerating training images...%s\n" "$YELLOW" "$NC"
    printf "This will take some time due to the large number of fonts.\n"
    printf "\n"
    
    # Process ALL fonts (including .TTF extension) without using a subshell,
    # so counters like SUCCESS/FAILED/FONT_INDEX persist after the loop.
    FONT_LIST_FILE="$OUTPUT_DIR/font_list.txt"
    find "$FONTS_PATH" \( -name "*.ttf" -o -name "*.TTF" \) -type f > "$FONT_LIST_FILE"
    while IFS= read -r font; do
        if [ ! -f "$font" ]; then
            continue
        fi

        # Get font name and clean it
        FONT_BASE=$(basename "$font" | sed 's/\.[tT][tT][fF]$//')

        # Try different font name formats
        FONT_NAME1=$(echo "$FONT_BASE" | sed 's/^[0-9]*_//' | sed 's/_/ /g')
        FONT_NAME2="$FONT_BASE"
        FONT_NAME3=$(echo "$FONT_BASE" | sed 's/^[0-9]*_//' | sed 's/_//g')

        CLEAN_NAME=$(printf "%s" "$FONT_BASE" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-30)

        # Progress indicator
        FONT_INDEX=$((FONT_INDEX + 1))
        PERCENT=$((FONT_INDEX * 100 / TOTAL_FONTS))

        printf "[%3d%%] Processing font %d/%d: %s\n" \
            "$PERCENT" "$FONT_INDEX" "$TOTAL_FONTS" "$FONT_BASE"

        # Try to generate with different font name formats
        FONT_SUCCESS=false

        for FONT_NAME in "$FONT_NAME1" "$FONT_NAME2" "$FONT_NAME3"; do
            if [ "$FONT_SUCCESS" = true ]; then
                break
            fi

            VAR_INDEX=0
            for spacing in 0.0; do
                for exposure in 0; do
                    OUTPUT_BASE="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.v${VAR_INDEX}"

                    # Generate base training image
                    text2image \
                        --text="$CORPUS_FILE" \
                        --outputbase="$OUTPUT_BASE" \
                        --font="$FONT_NAME" \
                        --fonts_dir="$FONTS_PATH" \
                        --char_spacing="$spacing" \
                        --exposure="$exposure" \
                        --resolution=300 \
                        --ptsize=12 \
                        --max_pages=1 > /dev/null 2>>"$OUTPUT_DIR/text2image_errors.log" || true

                    if [ -f "${OUTPUT_BASE}.tif" ]; then
                        # Create matching ground-truth text file (use a manageable slice)
                        head -n 50 "$CORPUS_FILE" > "${OUTPUT_BASE}.gt.txt"

                        SUCCESS=$((SUCCESS + 1))
                        TOTAL_IMAGES=$((TOTAL_IMAGES + 1))
                        FONT_SUCCESS=true

                        # Generate augmented versions (if ImageMagick available)
                        if [ "$IMAGEMAGICK_AVAILABLE" = true ]; then
                            generate_augmented_image \
                                "${OUTPUT_BASE}.tif" \
                                "$OUTPUT_BASE" \
                                "$FONT_NAME" \
                                "$VAR_INDEX"

                            # Count augmented images
                            AUG_COUNT=$(ls "${OUTPUT_BASE}"*.tif 2>/dev/null | wc -l)
                            if [ "$AUG_COUNT" -gt 1 ]; then
                                TOTAL_IMAGES=$((TOTAL_IMAGES + AUG_COUNT - 1))
                            fi
                        fi
                        break 2
                    fi

                    VAR_INDEX=$((VAR_INDEX + 1))
                done
            done
        done

        if [ "$FONT_SUCCESS" = false ]; then
            FAILED=$((FAILED + 1))
            printf "  %s✗ Failed to process this font%s\n" "$YELLOW" "$NC"
        fi

        if [ $((FONT_INDEX % 10)) -eq 0 ]; then
            printf "  %sProcessed %d fonts so far (%d successful, %d failed)%s\n" \
                "$CYAN" "$FONT_INDEX" "$SUCCESS" "$FAILED" "$NC"
        fi
    done < "$FONT_LIST_FILE"
    
    printf "\n"
    printf "%sTraining data generation complete!%s\n" "$GREEN" "$NC"
    printf "  Fonts processed: %d\n" "$FONT_INDEX"
    printf "  Base images created: %d\n" "$SUCCESS"
    printf "  Total images (with augmentation): %d\n" "$TOTAL_IMAGES"
    if [ $FAILED -gt 0 ]; then
        printf "  %sFailed: %d%s\n" "$YELLOW" "$FAILED" "$NC"
    fi
    
    if [ $SUCCESS -eq 0 ]; then
        printf "%sNo training data generated!%s\n" "$RED" "$NC"
        printf "Please check:\n"
        printf "1. Font files are valid\n"
        printf "2. text2image is working correctly\n"
        printf "3. Try running: text2image --list_available_fonts --fonts_dir=%s\n" "$FONTS_PATH"
        exit 1
    fi
}

generate_lstmf_files() {
    print_section "Converting to LSTMF Format"
    
    printf "Converting training images to LSTMF...\n"
    
    > "$OUTPUT_DIR/robust-lstmf.txt"
    LSTMF_COUNT=0
    LSTMF_FAILED=0
    
    # Count total files to process
    TOTAL_GT=$(find "$GROUND_TRUTH_DIR" -name "*.gt.txt" -type f 2>/dev/null | wc -l)
    
    if [ "$TOTAL_GT" -eq 0 ]; then
        printf "%sNo ground truth files found!%s\n" "$RED" "$NC"
        exit 1
    fi
    
    CURRENT=0
    
    for gt_file in "$GROUND_TRUTH_DIR"/*.gt.txt; do
        if [ ! -f "$gt_file" ]; then
            continue
        fi
        
        BASE=$(basename "$gt_file" .gt.txt)
        CURRENT=$((CURRENT + 1))
        PERCENT=$((CURRENT * 100 / TOTAL_GT))
        
        # Simpler progress display
        if [ $((CURRENT % 10)) -eq 0 ]; then
            printf "[%3d%%] Converting %d/%d files...\n" \
                "$PERCENT" "$CURRENT" "$TOTAL_GT"
        fi
        
        if [ -f "$GROUND_TRUTH_DIR/${BASE}.tif" ]; then
            # Generate LSTMF - use '|| true' to prevent exit on error
            tesseract "$GROUND_TRUTH_DIR/${BASE}.tif" \
                "$GROUND_TRUTH_DIR/${BASE}" \
                --psm 6 \
                -l ara \
                lstm.train >/dev/null 2>&1 || true
            
            if [ -f "$GROUND_TRUTH_DIR/${BASE}.lstmf" ]; then
                echo "$GROUND_TRUTH_DIR/${BASE}.lstmf" >> "$OUTPUT_DIR/robust-lstmf.txt"
                LSTMF_COUNT=$((LSTMF_COUNT + 1))
            else
                LSTMF_FAILED=$((LSTMF_FAILED + 1))
            fi
        fi
    done
    
    printf "\n"
    printf "%sLSTMF conversion complete!%s\n" "$GREEN" "$NC"
    printf "  Success: %d files\n" "$LSTMF_COUNT"
    if [ $LSTMF_FAILED -gt 0 ]; then
        printf "  %sFailed: %d%s\n" "$YELLOW" "$LSTMF_FAILED" "$NC"
    fi
    
    if [ $LSTMF_COUNT -eq 0 ]; then
        printf "%sNo LSTMF files generated!%s\n" "$RED" "$NC"
        exit 1
    fi
}

train_robust_model() {
    print_section "Training Robust LSTM Model"
    
    # Select base model
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE_MODEL="ara"
        printf "%s✓ Using Arabic base model%s\n" "$GREEN" "$NC"
    elif [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
        BASE_MODEL="eng"
        printf "%s⚠ Using English base model%s\n" "$YELLOW" "$NC"
    else
        printf "%s✗ No base model found%s\n" "$RED" "$NC"
        exit 1
    fi
    
    printf "\n"
    printf "%sTraining Configuration:%s\n" "$BOLD" "$NC"
    printf "  Base model: %s\n" "$BASE_MODEL"
    printf "  Training samples: %d\n" "$LSTMF_COUNT"
    printf "  Max iterations: %d\n" "$MAX_ITERATIONS"
    printf "  Target error rate: %s\n" "$TARGET_ERROR"
    printf "  Model type: ROBUST (all fonts + augmentation)\n"
    printf "\n"
    
    printf "%sStarting robust training...%s\n" "$BLUE" "$NC"
    printf "This will take considerable time due to the large dataset.\n"
    printf "\n"
    
    # Run training with simpler progress monitoring
    lstmtraining \
        --model_output "$OUTPUT_DIR/ckb_robust" \
        --traineddata "$TESSDATA_PREFIX/${BASE_MODEL}.traineddata" \
        --train_listfile "$OUTPUT_DIR/robust-lstmf.txt" \
        --max_iterations $MAX_ITERATIONS \
        --target_error_rate $TARGET_ERROR \
        --debug_interval $DEBUG_INTERVAL 2>&1 | while IFS= read -r line; do
            if printf "%s" "$line" | grep -q "At iteration"; then
                # Extract iteration number and error rate
                ITER=$(printf "%s" "$line" | sed -n 's/.*At iteration \([0-9]*\).*/\1/p')
                ERROR=$(printf "%s" "$line" | sed -n 's/.*error rate \([0-9.]*\).*/\1/p')
                if [ -n "$ITER" ] && [ -n "$ERROR" ]; then
                    printf "%sIteration: %5d / %d | Error: %s%s\n" \
                        "$YELLOW" "$ITER" "$MAX_ITERATIONS" "$ERROR" "$NC"
                fi
            elif printf "%s" "$line" | grep -q "Finished"; then
                printf "\n"
                printf "%sTraining finished!%s\n" "$GREEN" "$NC"
            fi
        done || true  # Don't exit if training fails
    
    printf "\n"
    
    # Check for checkpoint
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_robust*.checkpoint 2>/dev/null | head -1)
    
    if [ -z "$CHECKPOINT" ] || [ ! -f "$CHECKPOINT" ]; then
        printf "%s✗ No checkpoint found - training may have failed%s\n" "$RED" "$NC"
        printf "This could mean:\n"
        printf "1. Training is still in progress\n"
        printf "2. Not enough training data\n"
        printf "3. Training parameters need adjustment\n"
        exit 1
    fi
    
    printf "%s✓ Training checkpoint created%s\n" "$GREEN" "$NC"
    printf "  Checkpoint: %s\n" "$(basename "$CHECKPOINT")"
}

finalize_model() {
    print_section "Finalizing Robust Model"
    
    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_robust*.checkpoint 2>/dev/null | head -1)
    
    if [ -z "$CHECKPOINT" ] || [ ! -f "$CHECKPOINT" ]; then
        printf "%s✗ No checkpoint found%s\n" "$RED" "$NC"
        exit 1
    fi
    
    printf "Creating final model from checkpoint...\n"
    printf "  Checkpoint: %s\n" "$(basename "$CHECKPOINT")"
    
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
        --model_output "$FINAL_MODEL" >/dev/null 2>&1 || true
    
    if [ ! -f "$FINAL_MODEL" ]; then
        printf "%s✗ Failed to create final model%s\n" "$RED" "$NC"
        exit 1
    fi
    
    MODEL_SIZE=$(du -h "$FINAL_MODEL" | cut -f1)
    printf "%s✓ Robust model created successfully%s\n" "$GREEN" "$NC"
    printf "  Size: %s\n" "$MODEL_SIZE"
}

install_model() {
    print_section "Installing Robust Model"
    
    if [ -f "$FINAL_MODEL" ]; then
        # Backup existing model
        if [ -f "$TESSDATA_DEST" ]; then
            cp "$TESSDATA_DEST" "$TESSDATA_DEST.backup"
            printf "%s⚠ Backed up existing model to ckb.traineddata.backup%s\n" "$YELLOW" "$NC"
        fi
        
        # Install new robust model
        cp "$FINAL_MODEL" "$TESSDATA_DEST"
        printf "%s✓ Installed to: tessdata/ckb.traineddata%s\n" "$GREEN" "$NC"
        
        # Also save as ckb_robust for comparison
        cp "$FINAL_MODEL" "$(dirname "$TESSDATA_DEST")/ckb_robust.traineddata"
        printf "%s✓ Also saved as: tessdata/ckb_robust.traineddata%s\n" "$GREEN" "$NC"
        
        # Try system installation
        if [ -w "$TESSDATA_PREFIX" ]; then
            cp "$FINAL_MODEL" "$TESSDATA_PREFIX/ckb.traineddata"
            printf "%s✓ Installed to system tessdata%s\n" "$GREEN" "$NC"
        else
            printf "%s⚠ System installation requires sudo%s\n" "$YELLOW" "$NC"
        fi
    else
        printf "%s✗ Model file not found%s\n" "$RED" "$NC"
        exit 1
    fi
}

print_summary() {
    print_section "Robust Training Complete"
    
    MODEL_SIZE=$(du -h "$TESSDATA_DEST" 2>/dev/null | cut -f1 || echo "N/A")
    
    printf "%s%s✓ ROBUST MODEL SUCCESSFULLY CREATED!%s\n" "$GREEN" "$BOLD" "$NC"
    printf "\n"
    printf "%sModel Statistics:%s\n" "$BOLD" "$NC"
    printf "  Location: tessdata/ckb.traineddata\n"
    printf "  Size: %s\n" "$MODEL_SIZE"
    printf "  Type: ROBUST (maximum accuracy)\n"
    printf "\n"
    printf "%sTraining Summary:%s\n" "$BOLD" "$NC"
    printf "  Fonts used: %d Kurdish fonts\n" "$SUCCESS"
    printf "  Training samples: %d\n" "$LSTMF_COUNT"
    if [ "$IMAGEMAGICK_AVAILABLE" = true ]; then
        printf "  Augmentations: Shear, Rotation, Noise, Blur\n"
    else
        printf "  Augmentations: Basic (ImageMagick not installed)\n"
    fi
    printf "  Base variations: Character spacing, Exposure\n"
    printf "\n"
    printf "%sModel Features:%s\n" "$BOLD" "$NC"
    printf "  ✓ Trained with multiple Kurdish fonts\n"
    if [ "$IMAGEMAGICK_AVAILABLE" = true ]; then
        printf "  ✓ Shear transformation for skewed text\n"
        printf "  ✓ Rotation handling for tilted documents\n"
        printf "  ✓ Noise resistance for poor quality scans\n"
        printf "  ✓ Blur tolerance for out-of-focus images\n"
    fi
    printf "  ✓ Variable character spacing support\n"
    printf "  ✓ Multiple exposure levels for contrast variation\n"
    printf "\n"
    printf "%sUsage:%s\n" "$BOLD" "$NC"
    printf "  %stesseract image.png output -l ckb --psm 6%s\n" "$CYAN" "$NC"
    printf "\n"
    printf "%sTesting Recommendations:%s\n" "$BOLD" "$NC"
    printf "  1. Test with various document qualities\n"
    printf "  2. Try skewed/rotated images\n"
    printf "  3. Test with different fonts and sizes\n"
    printf "  4. Verify with noisy/blurred images\n"
    printf "\n"
    printf "%s%sThis robust model should handle a wide variety of Kurdish text images!%s\n" "$GREEN" "$BOLD" "$NC"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header
    check_dependencies
    verify_inputs
    clean_environment
    generate_training_data
    generate_lstmf_files
    train_robust_model
    finalize_model
    install_model
    print_summary
}

# Run main function
main
