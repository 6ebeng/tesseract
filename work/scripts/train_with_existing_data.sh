#!/bin/bash

# Train Kurdish OCR using existing LSTMF files
# This script uses previously generated training data

set -e  # Exit on error

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR=/mnt/c/tesseract/work
OUTPUT_DIR=$WORK_DIR/output
TRAINING_DIR=$WORK_DIR/training

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message "$CYAN" "╔════════════════════════════════════════════════════════╗"
print_message "$CYAN" "║     Kurdish OCR Training with Existing Data           ║"
print_message "$CYAN" "╚════════════════════════════════════════════════════════╝"

# Create output directory
mkdir -p $OUTPUT_DIR

# Find all existing LSTMF files
print_message "$YELLOW" "Finding existing LSTMF files..."
find $TRAINING_DIR -name "*.lstmf" -type f > $OUTPUT_DIR/all-lstmf.txt

lstmf_count=$(wc -l < $OUTPUT_DIR/all-lstmf.txt)
print_message "$GREEN" "Found $lstmf_count LSTMF files"

if [ $lstmf_count -eq 0 ]; then
    print_message "$RED" "No LSTMF files found. Please generate training data first."
    exit 1
fi

# Show sample of files found
print_message "$BLUE" "Sample LSTMF files:"
head -5 $OUTPUT_DIR/all-lstmf.txt | while read file; do
    echo "  - $(basename $file)"
done
if [ $lstmf_count -gt 5 ]; then
    echo "  ... and $(($lstmf_count - 5)) more files"
fi

# Start training
print_message "$YELLOW" "\nStarting training with $lstmf_count LSTMF files..."
print_message "$BLUE" "Training parameters:"
echo "  Max iterations: 2000"
echo "  Target error rate: 0.01"
echo "  Base model: eng.traineddata"

# Run training
print_message "$YELLOW" "\nTraining in progress..."
lstmtraining \
    --model_output $OUTPUT_DIR/ckb \
    --traineddata $TESSDATA_PREFIX/eng.traineddata \
    --train_listfile $OUTPUT_DIR/all-lstmf.txt \
    --max_iterations 2000 \
    --target_error_rate 0.01 \
    --debug_interval -1 2>&1 | while read line; do
        if [[ $line == *"At iteration"* ]]; then
            # Extract iteration and error rate
            if [[ $line =~ iteration\ ([0-9]+).*error.*\ ([0-9.]+)% ]]; then
                iter="${BASH_REMATCH[1]}"
                error="${BASH_REMATCH[2]}"
                printf "\rIteration: %4s | Error Rate: %6s%%" "$iter" "$error"
            else
                echo "$line"
            fi
        elif [[ $line == *"Finished"* ]] || [[ $line == *"checkpoint"* ]]; then
            echo ""
            print_message "$GREEN" "$line"
        fi
    done

echo ""  # New line after progress

# Check if checkpoint was created
checkpoint=""
if ls $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
    checkpoint=$(ls -t $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1)
elif [ -f "$OUTPUT_DIR/ckb_checkpoint" ]; then
    checkpoint="$OUTPUT_DIR/ckb_checkpoint"
fi

if [ -z "$checkpoint" ]; then
    print_message "$RED" "Training failed - no checkpoint created"
    exit 1
fi

print_message "$GREEN" "Training complete! Checkpoint: $(basename $checkpoint)"

# Finalize model
print_message "$YELLOW" "\nFinalizing model..."
lstmtraining \
    --stop_training \
    --continue_from "$checkpoint" \
    --traineddata $TESSDATA_PREFIX/eng.traineddata \
    --model_output $OUTPUT_DIR/ckb_custom.traineddata 2>&1

if [ ! -f "$OUTPUT_DIR/ckb_custom.traineddata" ]; then
    print_message "$RED" "Failed to create final model"
    exit 1
fi

# Get file size
model_size=$(du -h $OUTPUT_DIR/ckb_custom.traineddata | cut -f1)
print_message "$GREEN" "Model created: ckb_custom.traineddata ($model_size)"

# Install model
print_message "$YELLOW" "\nInstalling model..."

# Install to WSL
echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_custom.traineddata $TESSDATA_PREFIX/ckb_custom.traineddata 2>/dev/null
if [ $? -eq 0 ]; then
    print_message "$GREEN" "✓ Installed to WSL: $TESSDATA_PREFIX/ckb_custom.traineddata"
else
    print_message "$YELLOW" "⚠ Could not install to WSL (may need sudo password)"
fi

# Install to Windows
cp $OUTPUT_DIR/ckb_custom.traineddata /mnt/c/tesseract/tessdata/ckb_custom.traineddata
print_message "$GREEN" "✓ Installed to Windows: C:\\tesseract\\tessdata\\ckb_custom.traineddata"

# Test the model
print_message "$YELLOW" "\nTesting model..."

# Create a test image with Kurdish text
cat > /tmp/test_kurdish.txt << 'EOF'
ژیانی ڕۆژانە
سڵاو لەسەر هەموو هاوڕێکان
ئەربیل، سلێمانی، دهۆک
EOF

# Try to create a test image
if command -v convert &> /dev/null; then
    convert -size 400x200 xc:white -font "Arial" -pointsize 20 \
        -fill black -annotate +50+50 @/tmp/test_kurdish.txt \
        /tmp/test_image.tif 2>/dev/null && {
        
        print_message "$BLUE" "Running OCR test..."
        tesseract /tmp/test_image.tif stdout -l ckb_custom --psm 6 2>/dev/null
    }
else
    print_message "$YELLOW" "ImageMagick not installed, skipping visual test"
fi

# Summary
print_message "$CYAN" "\n╔════════════════════════════════════════════════════════╗"
print_message "$CYAN" "║              TRAINING COMPLETE!                       ║"
print_message "$CYAN" "╚════════════════════════════════════════════════════════╝"

print_message "$GREEN" "\nSummary:"
echo "  • Training data: $lstmf_count LSTMF files"
echo "  • Model size: $model_size"
echo "  • Model name: ckb_custom.traineddata"
echo ""
print_message "$BLUE" "Usage:"
echo "  tesseract image.tif output -l ckb_custom --psm 6"
echo ""
print_message "$YELLOW" "Locations:"
echo "  WSL: $TESSDATA_PREFIX/ckb_custom.traineddata"
echo "  Windows: C:\\tesseract\\tessdata\\ckb_custom.traineddata"
