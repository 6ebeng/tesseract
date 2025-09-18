#!/bin/bash

# Kurdish OCR Training Data Preparation Script V2
# Improved version that handles font installation

set -e  # Exit on error

# Configuration
WORK_DIR=/mnt/c/tesseract/work
FONTS_DIR=$WORK_DIR/fonts
CORPUS_FILE=$WORK_DIR/corpus/ckb.training_text
OUTPUT_DIR=$WORK_DIR/output
TRAINING_DIR=$WORK_DIR/training
GROUND_TRUTH_DIR=$WORK_DIR/ground-truth-custom

# Create necessary directories
mkdir -p $OUTPUT_DIR
mkdir -p $TRAINING_DIR
mkdir -p $GROUND_TRUTH_DIR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to install fonts temporarily
install_fonts() {
    print_message "$YELLOW" "Installing Kurdish fonts for training..."
    
    # Create temporary font directory
    TEMP_FONT_DIR=/tmp/kurdish_fonts
    mkdir -p $TEMP_FONT_DIR
    
    # Copy fonts to temp directory
    cp $FONTS_DIR/*.ttf $TEMP_FONT_DIR/ 2>/dev/null || true
    cp $FONTS_DIR/*.TTF $TEMP_FONT_DIR/ 2>/dev/null || true
    
    # Create fonts.conf for fontconfig
    cat > /tmp/fonts.conf << EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
    <dir>$TEMP_FONT_DIR</dir>
    <dir>/usr/share/fonts</dir>
    <cachedir>/tmp/fontconfig-cache</cachedir>
</fontconfig>
EOF
    
    # Set fontconfig environment
    export FONTCONFIG_FILE=/tmp/fonts.conf
    export FONTCONFIG_PATH=/tmp
    
    # Update font cache
    fc-cache -f $TEMP_FONT_DIR 2>/dev/null || true
    
    # Count available fonts
    font_count=$(ls -1 $TEMP_FONT_DIR/*.ttf 2>/dev/null | wc -l)
    print_message "$GREEN" "Prepared $font_count fonts for training"
}

# Function to generate training data with a specific font
generate_with_font() {
    local font_file=$1
    local font_name=$(basename "$font_file" .ttf)
    local clean_name=$(echo "$font_name" | sed 's/[^a-zA-Z0-9_-]/_/g' | cut -c1-50)
    
    # Generate training image
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_name}" \
        --font="$font_name" \
        --fonts_dir="$TEMP_FONT_DIR" \
        --lang=ara \
        --linedata_only \
        --char_spacing=0.0 \
        --exposure=0 \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=1 2>/dev/null
    
    return $?
}

# Function to generate training images
generate_training_images() {
    print_message "$YELLOW" "Generating training images with Kurdish fonts..."
    
    local success_count=0
    local fail_count=0
    local total_fonts=$(ls -1 $TEMP_FONT_DIR/*.ttf 2>/dev/null | wc -l)
    local current=0
    
    # Process each font
    for font in $TEMP_FONT_DIR/*.ttf; do
        if [ -f "$font" ]; then
            ((current++))
            font_name=$(basename "$font" .ttf)
            
            # Show progress
            printf "\rProcessing font %d/%d: %-50s" "$current" "$total_fonts" "$font_name"
            
            # Try to generate with this font
            if generate_with_font "$font"; then
                ((success_count++))
            else
                ((fail_count++))
            fi
            
            # Limit to reasonable number for initial training
            if [ $success_count -ge 50 ]; then
                echo ""
                print_message "$BLUE" "Generated sufficient training data (50 fonts)"
                break
            fi
        fi
    done
    
    echo ""  # New line after progress
    print_message "$GREEN" "Successfully processed $success_count fonts"
    if [ $fail_count -gt 0 ]; then
        print_message "$YELLOW" "Failed to process $fail_count fonts (this is normal for some fonts)"
    fi
}

# Function to generate LSTMF files
generate_lstmf_files() {
    print_message "$YELLOW" "Generating LSTMF files for training..."
    
    local lstmf_count=0
    
    # Create list file for LSTMF files
    > $OUTPUT_DIR/all-lstmf.txt
    
    # Process each ground truth file
    for gt_file in $GROUND_TRUTH_DIR/*.gt.txt; do
        if [ -f "$gt_file" ]; then
            base_name=$(basename "$gt_file" .gt.txt)
            
            # Check if corresponding tif exists
            if [ -f "$GROUND_TRUTH_DIR/${base_name}.tif" ]; then
                echo -n "."
                
                # Generate LSTMF file using Arabic as base (better for RTL)
                tesseract "$GROUND_TRUTH_DIR/${base_name}.tif" \
                    "$GROUND_TRUTH_DIR/${base_name}" \
                    --psm 6 \
                    -l ara \
                    lstm.train 2>/dev/null || {
                        # Try with English if Arabic fails
                        tesseract "$GROUND_TRUTH_DIR/${base_name}.tif" \
                            "$GROUND_TRUTH_DIR/${base_name}" \
                            --psm 6 \
                            -l eng \
                            lstm.train 2>/dev/null || continue
                    }
                
                # If LSTMF was created, add to list
                if [ -f "$GROUND_TRUTH_DIR/${base_name}.lstmf" ]; then
                    echo "$GROUND_TRUTH_DIR/${base_name}.lstmf" >> $OUTPUT_DIR/all-lstmf.txt
                    ((lstmf_count++))
                fi
            fi
        fi
    done
    
    echo ""  # New line after dots
    print_message "$GREEN" "Generated $lstmf_count LSTMF files"
    print_message "$BLUE" "LSTMF list saved to: $OUTPUT_DIR/all-lstmf.txt"
}

# Function to verify generated data
verify_data() {
    print_message "$YELLOW" "Verifying generated data..."
    
    local gt_count=$(ls -1 $GROUND_TRUTH_DIR/*.gt.txt 2>/dev/null | wc -l)
    local tif_count=$(ls -1 $GROUND_TRUTH_DIR/*.tif 2>/dev/null | wc -l)
    local lstmf_count=$(ls -1 $GROUND_TRUTH_DIR/*.lstmf 2>/dev/null | wc -l)
    local list_count=$(wc -l < $OUTPUT_DIR/all-lstmf.txt 2>/dev/null || echo 0)
    
    print_message "$BLUE" "Data Summary:"
    echo "  Ground truth files: $gt_count"
    echo "  TIF images: $tif_count"
    echo "  LSTMF files: $lstmf_count"
    echo "  Files in training list: $list_count"
    
    if [ $lstmf_count -gt 0 ]; then
        print_message "$GREEN" "✓ Training data ready!"
        return 0
    else
        print_message "$RED" "✗ No LSTMF files generated. Check for errors."
        return 1
    fi
}

# Main execution
main() {
    print_message "$GREEN" "╔════════════════════════════════════════════════════════╗"
    print_message "$GREEN" "║     Kurdish OCR Training Data Preparation V2          ║"
    print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"
    
    # Clean previous data
    print_message "$YELLOW" "Cleaning previous training data..."
    rm -rf $GROUND_TRUTH_DIR/*
    rm -f $OUTPUT_DIR/all-lstmf.txt
    
    # Step 1: Install fonts
    install_fonts
    
    # Step 2: Generate training images
    generate_training_images
    
    # Step 3: Generate LSTMF files
    generate_lstmf_files
    
    # Step 4: Verify data
    if verify_data; then
        print_message "$GREEN" "╔════════════════════════════════════════════════════════╗"
        print_message "$GREEN" "║     DATA PREPARATION COMPLETE!                        ║"
        print_message "$GREEN" "║     Ready to run training with master_training.sh     ║"
        print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"
    else
        print_message "$RED" "Data preparation encountered issues. Please check the logs."
    fi
}

# Run main function
main
