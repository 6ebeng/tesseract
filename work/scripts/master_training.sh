#!/bin/bash

# Master Kurdish OCR Training Script
# This script provides all training functionality in one place

set -e  # Exit on error

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
# Resolve script directory -> work dir
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR=$WORK_DIR/output
TRAINING_DIR=$WORK_DIR/training
TEST_DIR=$WORK_DIR/test-images

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

# Function to print header
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     Kurdish (ckb) OCR Model Training System           ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
}

# Function to show menu
show_menu() {
    print_header
    print_message "$BLUE" "Please select an option:"
    echo "1) Start new training from scratch"
    echo "2) Continue training from checkpoint"
    echo "3) Extended training (5000 iterations)"
    echo "4) Finalize model from checkpoint"
    echo "5) Test current model"
    echo "6) Clean training data"
    echo "7) Exit"
    echo ""
    read -p "Enter your choice [1-7]: " choice
}

# Function to find latest checkpoint
find_checkpoint() {
    local checkpoint=""
    
    # Try to find extended checkpoint first
    if ls $OUTPUT_DIR/ckb_extended_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
        checkpoint=$(ls -t $OUTPUT_DIR/ckb_extended_*.checkpoint 2>/dev/null | head -n 1)
    # Then try improved checkpoint
    elif [ -f "$OUTPUT_DIR/ckb_improved_checkpoint" ]; then
        checkpoint="$OUTPUT_DIR/ckb_improved_checkpoint"
    # Finally try basic checkpoint
    elif [ -f "$OUTPUT_DIR/ckb_checkpoint" ]; then
        checkpoint="$OUTPUT_DIR/ckb_checkpoint"
    fi
    
    echo "$checkpoint"
}

# Function to start new training
start_new_training() {
    print_message "$YELLOW" "Starting new training from scratch..."
    
    # Check for training data
    if [ ! -f "$OUTPUT_DIR/all-lstmf.txt" ]; then
        print_message "$RED" "Error: Training data not found. Please prepare LSTMF files first."
        return 1
    fi
    
    # Start training
    lstmtraining \
        --model_output $OUTPUT_DIR/ckb \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --train_listfile $OUTPUT_DIR/all-lstmf.txt \
        --max_iterations 1000 \
        --target_error_rate 0.01 \
        --debug_interval 100 2>&1 | while read line; do
            if [[ $line == *"At iteration"* ]]; then
                echo "$line"
            fi
        done
    
    print_message "$GREEN" "Initial training complete!"
}

# Function to continue training
continue_training() {
    local checkpoint=$(find_checkpoint)
    
    if [ -z "$checkpoint" ]; then
        print_message "$RED" "Error: No checkpoint found to continue from."
        return 1
    fi
    
    print_message "$YELLOW" "Continuing training from: $checkpoint"
    read -p "Enter number of additional iterations (default 1000): " iterations
    iterations=${iterations:-1000}
    
    lstmtraining \
        --continue_from "$checkpoint" \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --model_output $OUTPUT_DIR/ckb_continued \
        --train_listfile $OUTPUT_DIR/all-lstmf.txt \
        --max_iterations $iterations \
        --target_error_rate 0.01 2>&1 | while read line; do
            if [[ $line == *"At iteration"* ]] && [[ $line == *"00/"* ]]; then
                echo "$line"
            fi
        done
    
    print_message "$GREEN" "Continued training complete!"
}

# Function for extended training
extended_training() {
    local checkpoint=$(find_checkpoint)
    
    if [ -z "$checkpoint" ]; then
        print_message "$RED" "Error: No checkpoint found for extended training."
        return 1
    fi
    
    print_message "$YELLOW" "Starting extended training (5000 iterations)..."
    print_message "$YELLOW" "Starting from: $checkpoint"
    print_message "$YELLOW" "This will take considerable time..."
    
    # Run extended training
    lstmtraining \
        --continue_from "$checkpoint" \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --model_output $OUTPUT_DIR/ckb_extended \
        --train_listfile $OUTPUT_DIR/all-lstmf.txt \
        --max_iterations 5000 \
        --target_error_rate 0.01 2>&1 | while read line; do
            if [[ $line == *"At iteration"* ]] && [[ $line == *"00/"* ]]; then
                echo "$line"
            elif [[ $line == *"Finished"* ]]; then
                echo "$line"
            fi
        done
    
    # Finalize after extended training
    finalize_model
}

# Function to finalize model
finalize_model() {
    local checkpoint=$(find_checkpoint)
    
    if [ -z "$checkpoint" ]; then
        print_message "$RED" "Error: No checkpoint found to finalize."
        return 1
    fi
    
    print_message "$YELLOW" "Finalizing model from: $checkpoint"
    
    # Stop training and create final model
    lstmtraining \
        --stop_training \
        --continue_from "$checkpoint" \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --model_output $OUTPUT_DIR/ckb_final.traineddata 2>&1
    
    if [ -f "$OUTPUT_DIR/ckb_final.traineddata" ]; then
        # Install the model
        print_message "$YELLOW" "Installing model..."
        echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_final.traineddata $TESSDATA_PREFIX/ckb.traineddata
        cp $OUTPUT_DIR/ckb_final.traineddata /mnt/c/tesseract/tessdata/ckb.traineddata
        
        print_message "$GREEN" "╔════════════════════════════════════════════════════════╗"
        print_message "$GREEN" "║         MODEL FINALIZED SUCCESSFULLY!                 ║"
        print_message "$GREEN" "╠════════════════════════════════════════════════════════╣"
        print_message "$GREEN" "║  Final model: ckb_final.traineddata                   ║"
        print_message "$GREEN" "║  Installed to both WSL and Windows                    ║"
        print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"
    else
        print_message "$RED" "Error: Failed to create final model"
        return 1
    fi
}

# Function to test model
test_model() {
    print_message "$YELLOW" "Testing Kurdish OCR model..."
    
    # Check if model exists
    if [ ! -f "$TESSDATA_PREFIX/ckb.traineddata" ]; then
        print_message "$RED" "Error: Kurdish model not found. Please train and install first."
        return 1
    fi
    
    # Test with available images
    if [ -d "$TEST_DIR" ]; then
        cd $TEST_DIR
        
        # Find first test image
        test_image=$(ls *.tif 2>/dev/null | head -n 1)
        
        if [ -n "$test_image" ]; then
            base_name="${test_image%.tif}"
            
            print_message "$BLUE" "Testing with: $test_image"
            
            # Run OCR
            print_message "$YELLOW" "OCR Output:"
            tesseract "$test_image" stdout -l ckb --psm 6 2>/dev/null
            
            # Show original if available
            if [ -f "${base_name}.txt" ]; then
                echo ""
                print_message "$YELLOW" "Original text:"
                cat "${base_name}.txt"
            fi
            
            # Test all images and calculate accuracy
            echo ""
            print_message "$BLUE" "Testing all images in test folder..."
            total=0
            for img in *.tif; do
                if [ -f "$img" ]; then
                    ((total++))
                    echo "Processing: $img"
                    tesseract "$img" "${img%.tif}_output" -l ckb --psm 6 2>/dev/null
                fi
            done
            print_message "$GREEN" "Tested $total images. Output files created."
        else
            print_message "$RED" "No test images found in $TEST_DIR"
        fi
    else
        print_message "$RED" "Test directory not found: $TEST_DIR"
    fi
}

# Function to clean training data
clean_training() {
    print_message "$YELLOW" "This will remove temporary training files. Continue? (y/n)"
    read -p "> " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        print_message "$YELLOW" "Cleaning training data..."
        
        # Remove temporary files but keep important ones
        rm -f $TRAINING_DIR/*.tr 2>/dev/null
        rm -f $TRAINING_DIR/*.txt 2>/dev/null
        rm -f $OUTPUT_DIR/*checkpoint* 2>/dev/null
        
        print_message "$GREEN" "Training data cleaned. Models preserved."
    else
        print_message "$BLUE" "Cleaning cancelled."
    fi
}

# Main script
main() {
    while true; do
        show_menu
        
        case $choice in
            1)
                start_new_training
                ;;
            2)
                continue_training
                ;;
            3)
                extended_training
                ;;
            4)
                finalize_model
                ;;
            5)
                test_model
                ;;
            6)
                clean_training
                ;;
            7)
                print_message "$BLUE" "Exiting..."
                exit 0
                ;;
            *)
                print_message "$RED" "Invalid option. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
