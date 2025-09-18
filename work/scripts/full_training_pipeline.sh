#!/bin/bash

# Complete Kurdish OCR Training Pipeline
# This script runs the entire training process from fonts/corpus to final model

set -e  # Exit on error

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR=/mnt/c/tesseract/work
SCRIPTS_DIR=$WORK_DIR/scripts
OUTPUT_DIR=$WORK_DIR/output
TRAINING_DIR=$WORK_DIR/training

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print header
print_header() {
    echo ""
    print_message "$CYAN" "╔════════════════════════════════════════════════════════════════╗"
    print_message "$CYAN" "║        COMPLETE KURDISH OCR TRAINING PIPELINE                 ║"
    print_message "$CYAN" "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_message "$YELLOW" "Checking prerequisites..."
    
    local all_good=true
    
    # Check Tesseract
    if command -v tesseract &> /dev/null; then
        print_message "$GREEN" "✓ Tesseract installed"
    else
        print_message "$RED" "✗ Tesseract not found"
        all_good=false
    fi
    
    # Check text2image
    if command -v text2image &> /dev/null; then
        print_message "$GREEN" "✓ text2image available"
    else
        print_message "$RED" "✗ text2image not found"
        all_good=false
    fi
    
    # Check lstmtraining
    if command -v lstmtraining &> /dev/null; then
        print_message "$GREEN" "✓ lstmtraining available"
    else
        print_message "$RED" "✗ lstmtraining not found"
        all_good=false
    fi
    
    # Check fonts directory
    if [ -d "$WORK_DIR/fonts" ] && [ "$(ls -A $WORK_DIR/fonts/*.ttf 2>/dev/null | wc -l)" -gt 0 ]; then
        font_count=$(ls -1 $WORK_DIR/fonts/*.ttf 2>/dev/null | wc -l)
        print_message "$GREEN" "✓ Found $font_count fonts"
    else
        print_message "$RED" "✗ No fonts found in $WORK_DIR/fonts"
        all_good=false
    fi
    
    # Check corpus file
    if [ -f "$WORK_DIR/corpus/ckb.training_text" ]; then
        print_message "$GREEN" "✓ Corpus file found"
    else
        print_message "$RED" "✗ Corpus file not found"
        all_good=false
    fi
    
    # Check base model
    if [ -f "$TESSDATA_PREFIX/eng.traineddata" ]; then
        print_message "$GREEN" "✓ Base model (eng) found"
    else
        print_message "$RED" "✗ Base model not found. Downloading..."
        download_base_model
    fi
    
    if [ "$all_good" = false ]; then
        print_message "$RED" "Prerequisites check failed. Please install missing components."
        exit 1
    fi
    
    print_message "$GREEN" "All prerequisites satisfied!"
}

# Function to download base model if needed
download_base_model() {
    print_message "$YELLOW" "Downloading English base model..."
    
    # Try to download eng.traineddata
    wget -q https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata \
        -O /tmp/eng.traineddata 2>/dev/null || {
        print_message "$RED" "Failed to download base model"
        return 1
    }
    
    # Install with sudo
    echo 'tishko' | sudo -S mv /tmp/eng.traineddata $TESSDATA_PREFIX/
    print_message "$GREEN" "Base model downloaded and installed"
}

# Function to run data preparation
prepare_data() {
    print_message "$BLUE" "\n=== PHASE 1: DATA PREPARATION ==="
    
    if [ -f "$SCRIPTS_DIR/prepare_training_data.sh" ]; then
        bash "$SCRIPTS_DIR/prepare_training_data.sh"
    else
        print_message "$RED" "Data preparation script not found!"
        exit 1
    fi
}

# Function to run training
run_training() {
    print_message "$BLUE" "\n=== PHASE 2: MODEL TRAINING ==="
    
    # Check if LSTMF files exist
    if [ ! -f "$OUTPUT_DIR/all-lstmf.txt" ] || [ $(wc -l < "$OUTPUT_DIR/all-lstmf.txt") -eq 0 ]; then
        print_message "$RED" "No training data found. Run data preparation first."
        exit 1
    fi
    
    local lstmf_count=$(wc -l < "$OUTPUT_DIR/all-lstmf.txt")
    print_message "$YELLOW" "Starting training with $lstmf_count LSTMF files..."
    
    # Training parameters
    local max_iterations=${1:-2000}
    local target_error=${2:-0.01}
    
    print_message "$BLUE" "Training parameters:"
    echo "  Max iterations: $max_iterations"
    echo "  Target error rate: $target_error"
    
    # Start training
    print_message "$YELLOW" "Training in progress (this may take a while)..."
    
    lstmtraining \
        --model_output $OUTPUT_DIR/ckb \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --train_listfile $OUTPUT_DIR/all-lstmf.txt \
        --max_iterations $max_iterations \
        --target_error_rate $target_error \
        --debug_interval 100 2>&1 | while read line; do
            if [[ $line == *"At iteration"* ]]; then
                # Extract iteration number and error rate
                if [[ $line =~ iteration\ ([0-9]+).*error\ rate.*\ ([0-9.]+)% ]]; then
                    iter="${BASH_REMATCH[1]}"
                    error="${BASH_REMATCH[2]}"
                    printf "\rIteration: %s | Error Rate: %s%%" "$iter" "$error"
                fi
            elif [[ $line == *"Finished"* ]]; then
                echo ""
                print_message "$GREEN" "$line"
            fi
        done
    
    echo ""  # New line after progress
    
    # Check if checkpoint was created
    if ls $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
        print_message "$GREEN" "Training checkpoint created successfully!"
        return 0
    else
        print_message "$RED" "Training failed - no checkpoint created"
        return 1
    fi
}

# Function to finalize model
finalize_model() {
    print_message "$BLUE" "\n=== PHASE 3: MODEL FINALIZATION ==="
    
    # Find the latest checkpoint
    local checkpoint=""
    if ls $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
        checkpoint=$(ls -t $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1)
    elif [ -f "$OUTPUT_DIR/ckb_checkpoint" ]; then
        checkpoint="$OUTPUT_DIR/ckb_checkpoint"
    fi
    
    if [ -z "$checkpoint" ]; then
        print_message "$RED" "No checkpoint found to finalize"
        return 1
    fi
    
    print_message "$YELLOW" "Finalizing model from: $(basename $checkpoint)"
    
    # Stop training and create final model
    lstmtraining \
        --stop_training \
        --continue_from "$checkpoint" \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --model_output $OUTPUT_DIR/ckb_custom.traineddata 2>&1
    
    if [ -f "$OUTPUT_DIR/ckb_custom.traineddata" ]; then
        print_message "$GREEN" "Model finalized: ckb_custom.traineddata"
        return 0
    else
        print_message "$RED" "Failed to create final model"
        return 1
    fi
}

# Function to install model
install_model() {
    print_message "$BLUE" "\n=== PHASE 4: MODEL INSTALLATION ==="
    
    if [ ! -f "$OUTPUT_DIR/ckb_custom.traineddata" ]; then
        print_message "$RED" "Final model not found"
        return 1
    fi
    
    print_message "$YELLOW" "Installing model to system locations..."
    
    # Install to WSL Tesseract directory
    echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_custom.traineddata $TESSDATA_PREFIX/ckb_custom.traineddata
    
    # Install to Windows directory
    cp $OUTPUT_DIR/ckb_custom.traineddata /mnt/c/tesseract/tessdata/ckb_custom.traineddata
    
    print_message "$GREEN" "Model installed to:"
    echo "  WSL: $TESSDATA_PREFIX/ckb_custom.traineddata"
    echo "  Windows: C:\\tesseract\\tessdata\\ckb_custom.traineddata"
}

# Function to test model
test_model() {
    print_message "$BLUE" "\n=== PHASE 5: MODEL TESTING ==="
    
    # Create a test image from corpus
    print_message "$YELLOW" "Creating test image..."
    
    # Use the first available font for testing
    test_font=$(ls $WORK_DIR/fonts/*.ttf 2>/dev/null | head -n 1)
    
    if [ -n "$test_font" ]; then
        font_name=$(basename "$test_font" .ttf)
        
        # Create a small test text
        echo "ژیانی ڕۆژانە: آزاد لە ئەژنۆدا هەڵدەستا" > /tmp/test_text.txt
        echo "لە قوتابخانەدا: مامۆستا ڕەحیم وانەی فێری دەکردن" >> /tmp/test_text.txt
        
        # Generate test image
        text2image \
            --text=/tmp/test_text.txt \
            --outputbase=/tmp/ckb_test \
            --font="$font_name" \
            --fonts_dir="$WORK_DIR/fonts" \
            --lang=ckb \
            --linedata_only \
            --resolution=300 \
            --ptsize=12 2>/dev/null
        
        if [ -f "/tmp/ckb_test.tif" ]; then
            print_message "$YELLOW" "Running OCR with new model..."
            
            # Test with new model
            tesseract /tmp/ckb_test.tif stdout -l ckb_custom --psm 6 2>/dev/null
            
            print_message "$GREEN" "Test complete!"
        else
            print_message "$RED" "Could not create test image"
        fi
    fi
}

# Function to show summary
show_summary() {
    print_message "$CYAN" "\n╔════════════════════════════════════════════════════════════════╗"
    print_message "$CYAN" "║                    TRAINING COMPLETE!                         ║"
    print_message "$CYAN" "╚════════════════════════════════════════════════════════════════╝"
    
    print_message "$GREEN" "\nSummary:"
    
    # Count generated files
    local lstmf_count=$(wc -l < $OUTPUT_DIR/all-lstmf.txt 2>/dev/null || echo 0)
    local font_count=$(ls -1 $WORK_DIR/fonts/*.ttf 2>/dev/null | wc -l)
    
    echo "  • Fonts used: $font_count"
    echo "  • Training samples: $lstmf_count"
    echo "  • Model name: ckb_custom.traineddata"
    echo ""
    print_message "$BLUE" "To use the model:"
    echo "  tesseract image.tif output -l ckb_custom --psm 6"
    echo ""
    print_message "$YELLOW" "Model locations:"
    echo "  WSL: $TESSDATA_PREFIX/ckb_custom.traineddata"
    echo "  Windows: C:\\tesseract\\tessdata\\ckb_custom.traineddata"
}

# Main execution
main() {
    print_header
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Ask user for training parameters
    print_message "$BLUE" "\nTraining Configuration:"
    read -p "Enter max iterations (default 2000): " iterations
    iterations=${iterations:-2000}
    
    read -p "Enter target error rate (default 0.01): " error_rate
    error_rate=${error_rate:-0.01}
    
    print_message "$YELLOW" "\nThis process will:"
    echo "1. Generate training data from all fonts and corpus"
    echo "2. Train for $iterations iterations"
    echo "3. Create and install ckb_custom.traineddata"
    echo ""
    read -p "Continue? (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_message "$RED" "Training cancelled."
        exit 0
    fi
    
    # Step 2: Prepare data
    prepare_data
    
    # Step 3: Run training
    if run_training $iterations $error_rate; then
        # Step 4: Finalize model
        if finalize_model; then
            # Step 5: Install model
            install_model
            
            # Step 6: Test model
            test_model
            
            # Step 7: Show summary
            show_summary
        fi
    fi
}

# Run main function
main
