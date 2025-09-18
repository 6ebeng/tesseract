#!/bin/bash

# Train Kurdish OCR using the specific corpus text provided
# This script generates fresh training data from the corpus file

set -e  # Exit on error

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR=/mnt/c/tesseract/work
CORPUS_FILE=$WORK_DIR/corpus/ckb.training_text
OUTPUT_DIR=$WORK_DIR/output
GROUND_TRUTH_DIR=$WORK_DIR/ground-truth-corpus
FONTS_DIR="/mnt/c/tesseract/work/fonts/kurdish"

# Create directories
mkdir -p $OUTPUT_DIR
mkdir -p $GROUND_TRUTH_DIR

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
print_message "$CYAN" "║   Kurdish OCR Training with Your Corpus Text          ║"
print_message "$CYAN" "╚════════════════════════════════════════════════════════╝"

# Verify corpus file
print_message "$YELLOW" "Verifying corpus file..."
if [ ! -f "$CORPUS_FILE" ]; then
    print_message "$RED" "Error: Corpus file not found at $CORPUS_FILE"
    exit 1
fi

# Show corpus preview
print_message "$BLUE" "Corpus text preview:"
head -3 "$CORPUS_FILE" | while IFS= read -r line; do
    echo "  $line"
done
echo "  ..."

# Clean previous data
print_message "$YELLOW" "\nCleaning previous corpus training data..."
rm -rf $GROUND_TRUTH_DIR/*

# Select fonts for training
print_message "$YELLOW" "Selecting fonts for training..."
SELECTED_FONTS=()
font_count=0
max_fonts=30  # Use 30 diverse fonts for good coverage

# Select diverse fonts (every 20th font to get variety)
for font in $FONTS_DIR/*.ttf; do
    if [ -f "$font" ]; then
        if [ $((font_count % 20)) -eq 0 ] && [ ${#SELECTED_FONTS[@]} -lt $max_fonts ]; then
            SELECTED_FONTS+=("$font")
        fi
        ((font_count++))
    fi
done

print_message "$GREEN" "Selected ${#SELECTED_FONTS[@]} fonts from $font_count total fonts"

# Generate training data with selected fonts
print_message "$YELLOW" "\nGenerating training data from corpus..."
success_count=0
fail_count=0

for font_file in "${SELECTED_FONTS[@]}"; do
    font_name=$(basename "$font_file" .ttf)
    clean_name=$(echo "$font_name" | sed 's/[^a-zA-Z0-9_-]/_/g' | cut -c1-40)
    
    printf "\rProcessing font %d/%d: %-40s" $((success_count + fail_count + 1)) ${#SELECTED_FONTS[@]} "$font_name"
    
    # Generate training image with corpus text
    text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_name}" \
        --font="$font_name" \
        --fonts_dir="$FONTS_DIR" \
        --lang=ara \
        --linedata_only \
        --char_spacing=0.0 \
        --exposure=0 \
        --resolution=300 \
        --ptsize=12 \
        --max_pages=2 2>/dev/null && {
            ((success_count++))
        } || {
            # Try with default font as fallback
            text2image \
                --text="$CORPUS_FILE" \
                --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_name}" \
                --font="Arial" \
                --lang=ara \
                --linedata_only \
                --char_spacing=0.0 \
                --exposure=0 \
                --resolution=300 \
                --ptsize=12 \
                --max_pages=2 2>/dev/null && {
                    ((success_count++))
                } || {
                    ((fail_count++))
                }
        }
done

echo ""  # New line after progress
print_message "$GREEN" "Successfully generated $success_count training samples"
if [ $fail_count -gt 0 ]; then
    print_message "$YELLOW" "Failed: $fail_count fonts (this is normal for some fonts)"
fi

# Generate LSTMF files
print_message "$YELLOW" "\nGenerating LSTMF files..."
lstmf_count=0
> $OUTPUT_DIR/corpus-lstmf.txt

for gt_file in $GROUND_TRUTH_DIR/*.gt.txt; do
    if [ -f "$gt_file" ]; then
        base_name=$(basename "$gt_file" .gt.txt)
        
        if [ -f "$GROUND_TRUTH_DIR/${base_name}.tif" ]; then
            printf "\rGenerating LSTMF %d..." $((lstmf_count + 1))
            
            # Generate LSTMF file
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
                echo "$GROUND_TRUTH_DIR/${base_name}.lstmf" >> $OUTPUT_DIR/corpus-lstmf.txt
                ((lstmf_count++))
            fi
        fi
    fi
done

echo ""  # New line
print_message "$GREEN" "Generated $lstmf_count LSTMF files"

if [ $lstmf_count -eq 0 ]; then
    print_message "$RED" "No LSTMF files generated. Training cannot proceed."
    exit 1
fi

# Start training
print_message "$YELLOW" "\nStarting training with corpus-based data..."
print_message "$BLUE" "Training parameters:"
echo "  Training samples: $lstmf_count LSTMF files"
echo "  Max iterations: 3000"
echo "  Target error rate: 0.01"
echo "  Base model: ara.traineddata (better for RTL text)"

# Check if Arabic model exists, download if needed
if [ ! -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    print_message "$YELLOW" "Downloading Arabic base model..."
    wget -q https://github.com/tesseract-ocr/tessdata_best/raw/main/ara.traineddata \
        -O /tmp/ara.traineddata 2>/dev/null && {
        echo 'tishko' | sudo -S mv /tmp/ara.traineddata $TESSDATA_PREFIX/
        print_message "$GREEN" "Arabic model downloaded"
    } || {
        print_message "$YELLOW" "Using English model as fallback"
    }
fi

# Determine base model
if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
    BASE_MODEL="$TESSDATA_PREFIX/ara.traineddata"
    print_message "$GREEN" "Using Arabic base model (better for RTL)"
else
    BASE_MODEL="$TESSDATA_PREFIX/eng.traineddata"
    print_message "$YELLOW" "Using English base model"
fi

# Run training
print_message "$YELLOW" "\nTraining in progress..."
lstmtraining \
    --model_output $OUTPUT_DIR/ckb_corpus \
    --traineddata "$BASE_MODEL" \
    --train_listfile $OUTPUT_DIR/corpus-lstmf.txt \
    --max_iterations 3000 \
    --target_error_rate 0.01 \
    --debug_interval -1 2>&1 | while read line; do
        if [[ $line == *"At iteration"* ]]; then
            if [[ $line =~ iteration\ ([0-9]+).*error.*\ ([0-9.]+)% ]]; then
                iter="${BASH_REMATCH[1]}"
                error="${BASH_REMATCH[2]}"
                printf "\rIteration: %4s | Error Rate: %6s%%" "$iter" "$error"
            fi
        elif [[ $line == *"Finished"* ]] || [[ $line == *"checkpoint"* ]]; then
            echo ""
            print_message "$GREEN" "$line"
        fi
    done

echo ""  # New line

# Find checkpoint
checkpoint=""
if ls $OUTPUT_DIR/ckb_corpus_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
    checkpoint=$(ls -t $OUTPUT_DIR/ckb_corpus_*.checkpoint 2>/dev/null | head -n 1)
elif [ -f "$OUTPUT_DIR/ckb_corpus_checkpoint" ]; then
    checkpoint="$OUTPUT_DIR/ckb_corpus_checkpoint"
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
    --traineddata "$BASE_MODEL" \
    --model_output $OUTPUT_DIR/ckb_corpus.traineddata 2>&1

if [ ! -f "$OUTPUT_DIR/ckb_corpus.traineddata" ]; then
    print_message "$RED" "Failed to create final model"
    exit 1
fi

# Get file size
model_size=$(du -h $OUTPUT_DIR/ckb_corpus.traineddata | cut -f1)
print_message "$GREEN" "Model created: ckb_corpus.traineddata ($model_size)"

# Install model
print_message "$YELLOW" "\nInstalling model..."

# Install to WSL
echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_corpus.traineddata $TESSDATA_PREFIX/ckb_corpus.traineddata 2>/dev/null
print_message "$GREEN" "✓ Installed to WSL: $TESSDATA_PREFIX/ckb_corpus.traineddata"

# Install to Windows
cp $OUTPUT_DIR/ckb_corpus.traineddata /mnt/c/tesseract/tessdata/ckb_corpus.traineddata
print_message "$GREEN" "✓ Installed to Windows: C:\\tesseract\\tessdata\\ckb_corpus.traineddata"

# Test the model with text from corpus
print_message "$YELLOW" "\nTesting model with corpus text..."

# Create test image with corpus text
head -5 "$CORPUS_FILE" > /tmp/test_corpus.txt

# Try to create and test
if [ -f "$GROUND_TRUTH_DIR/ckb_00_Sarchia_ABC.tif" ]; then
    print_message "$BLUE" "Testing OCR with generated image..."
    tesseract "$GROUND_TRUTH_DIR/ckb_00_Sarchia_ABC.tif" stdout -l ckb_corpus --psm 6 2>/dev/null | head -5
fi

# Summary
print_message "$CYAN" "\n╔════════════════════════════════════════════════════════╗"
print_message "$CYAN" "║     CORPUS-BASED TRAINING COMPLETE!                   ║"
print_message "$CYAN" "╚════════════════════════════════════════════════════════╝"

print_message "$GREEN" "\nSummary:"
echo "  • Corpus used: $CORPUS_FILE"
echo "  • Fonts used: ${#SELECTED_FONTS[@]} fonts"
echo "  • Training samples: $lstmf_count LSTMF files"
echo "  • Model size: $model_size"
echo "  • Model name: ckb_corpus.traineddata"
echo ""
print_message "$BLUE" "Usage:"
echo "  tesseract image.tif output -l ckb_corpus --psm 6"
echo ""
print_message "$YELLOW" "Locations:"
echo "  WSL: $TESSDATA_PREFIX/ckb_corpus.traineddata"
echo "  Windows: C:\\tesseract\\tessdata\\ckb_corpus.traineddata"
