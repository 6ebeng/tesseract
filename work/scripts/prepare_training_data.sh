#!/bin/bash

# Kurdish OCR Training Data Preparation Script
# Generates training data from fonts and corpus text

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

# Function to count fonts
count_fonts() {
    local count=$(ls -1 $FONTS_DIR/*.ttf 2>/dev/null | wc -l)
    echo $count
}

# Function to generate training text files
generate_text_files() {
    print_message "$YELLOW" "Generating training text files..."
    
    # Create multiple text files with variations of the corpus
    local text_count=0
    
    # Read the corpus file
    if [ ! -f "$CORPUS_FILE" ]; then
        print_message "$RED" "Error: Corpus file not found at $CORPUS_FILE"
        exit 1
    fi
    
    # Generate text files for each font (we'll create one text file per font for variety)
    for font in $FONTS_DIR/*.ttf; do
        if [ -f "$font" ]; then
            font_basename=$(basename "$font" .ttf)
            text_file="$TRAINING_DIR/ckb_${text_count}.txt"
            
            # Copy corpus to text file (you can add variations here)
            cp "$CORPUS_FILE" "$text_file"
            
            ((text_count++))
            
            # Limit to reasonable number of text files
            if [ $text_count -ge 100 ]; then
                break
            fi
        fi
    done
    
    print_message "$GREEN" "Generated $text_count text files"
}

# Function to generate training images and box files
generate_training_images() {
    print_message "$YELLOW" "Generating training images with fonts..."
    
    local font_count=0
    local total_fonts=$(count_fonts)
    
    print_message "$BLUE" "Found $total_fonts fonts to process"
    
    # Process each font
    for font in $FONTS_DIR/*.ttf; do
        if [ -f "$font" ]; then
            font_basename=$(basename "$font" .ttf)
            # Clean font name (remove spaces and special characters)
            clean_font_name=$(echo "$font_basename" | sed 's/[^a-zA-Z0-9_-]/_/g')
            
            ((font_count++))
            
            # Show progress
            echo -ne "\rProcessing font $font_count/$total_fonts: $font_basename"
            
            # Generate training image using text2image
            text2image \
                --text="$CORPUS_FILE" \
                --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_font_name}" \
                --font="$font_basename" \
                --fonts_dir="$FONTS_DIR" \
                --lang=ckb \
                --linedata_only \
                --char_spacing=0.0 \
                --exposure=0 \
                --resolution=300 \
                --ptsize=12 \
                --max_pages=1 2>/dev/null || {
                    # If font fails, skip it
                    continue
                }
        fi
    done
    
    echo ""  # New line after progress
    print_message "$GREEN" "Processed $font_count fonts"
}

# Function to extract unicharset
extract_unicharset() {
    print_message "$YELLOW" "Extracting unicharset from box files..."
    
    # Combine all box files to extract unicharset
    unicharset_extractor $GROUND_TRUTH_DIR/*.box 2>/dev/null || {
        print_message "$RED" "Warning: unicharset extraction had issues"
    }
    
    if [ -f "unicharset" ]; then
        mv unicharset $OUTPUT_DIR/
        print_message "$GREEN" "Unicharset extracted successfully"
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
                # Generate LSTMF file
                tesseract "$GROUND_TRUTH_DIR/${base_name}.tif" \
                    "$GROUND_TRUTH_DIR/${base_name}" \
                    --psm 6 \
                    -l eng \
                    lstm.train 2>/dev/null || {
                        continue
                    }
                
                # If LSTMF was created, add to list
                if [ -f "$GROUND_TRUTH_DIR/${base_name}.lstmf" ]; then
                    echo "$GROUND_TRUTH_DIR/${base_name}.lstmf" >> $OUTPUT_DIR/all-lstmf.txt
                    ((lstmf_count++))
                fi
            fi
        fi
    done
    
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
    print_message "$GREEN" "║     Kurdish OCR Training Data Preparation             ║"
    print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"
    
    # Clean previous data
    print_message "$YELLOW" "Cleaning previous training data..."
    rm -rf $GROUND_TRUTH_DIR/*
    rm -f $OUTPUT_DIR/all-lstmf.txt
    
    # Step 1: Generate text files
    generate_text_files
    
    # Step 2: Generate training images
    generate_training_images
    
    # Step 3: Extract unicharset
    extract_unicharset
    
    # Step 4: Generate LSTMF files
    generate_lstmf_files
    
    # Step 5: Verify data
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
