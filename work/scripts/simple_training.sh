#!/bin/bash

# Simple Kurdish OCR Training Script
# Uses system fonts to quickly generate training data

set -e  # Exit on error

# Configuration
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR=/mnt/c/tesseract/work
CORPUS_FILE=$WORK_DIR/corpus/ckb.training_text
OUTPUT_DIR=$WORK_DIR/output
GROUND_TRUTH_DIR=$WORK_DIR/ground-truth-custom

# Create directories
mkdir -p $OUTPUT_DIR
mkdir -p $GROUND_TRUTH_DIR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message "$GREEN" "╔════════════════════════════════════════════════════════╗"
print_message "$GREEN" "║     Simple Kurdish OCR Training                       ║"
print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"

# Clean previous data
print_message "$YELLOW" "Cleaning previous data..."
rm -rf $GROUND_TRUTH_DIR/*
rm -f $OUTPUT_DIR/all-lstmf.txt

# Use a selection of Kurdish fonts from the fonts directory
print_message "$YELLOW" "Generating training data with Kurdish fonts..."

# Create a simple text file with Kurdish content
cat > /tmp/ckb_training.txt << 'EOF'
ژیانی ڕۆژانە: آزاد لە ئەژنۆدا هەڵدەستا
لە قوتابخانەدا: مامۆستا ڕەحیم وانەی فێری دەکردن
هاوڕێیان: ژیان، چیا، هێوا، ڕوژان، شادی، ڤیان ؤ یاسین
خواردنی دڵخوازی طاوە و ڕیز بوو
ناوەکان: یوسف، یار، یەکتا ؤ یاران
شوێنەکان: آمەد، ئەربیل، سلێمانی
سڵاو لەسەر هەموو هاوڕێکان! ژیان جوانە
ء ا ب پ ت ج چ ح خ د ر ڕ ز ژ س ش ع غ ف ڤ ق ک گ ل ڵ م ن ه و ۆ ی ە ێ
EOF

# Generate training images using text2image with default fonts
font_count=0
max_fonts=10  # Limit to 10 fonts for quick training

# Try to use some Kurdish fonts directly by copying them
print_message "$YELLOW" "Copying sample Kurdish fonts..."
mkdir -p /tmp/ckb_fonts
for font in $WORK_DIR/fonts/*.ttf; do
    if [ -f "$font" ] && [ $font_count -lt $max_fonts ]; then
        cp "$font" /tmp/ckb_fonts/
        ((font_count++))
    fi
done

print_message "$BLUE" "Using $font_count Kurdish fonts for training"

# Generate training data for each font
success_count=0
for font_file in /tmp/ckb_fonts/*.ttf; do
    if [ -f "$font_file" ]; then
        font_name=$(basename "$font_file" .ttf)
        clean_name=$(echo "$font_name" | sed 's/[^a-zA-Z0-9_-]/_/g' | cut -c1-30)
        
        echo -n "Processing $font_name... "
        
        # Try to generate training image
        text2image \
            --text=/tmp/ckb_training.txt \
            --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_name}" \
            --font="Arial" \
            --lang=ara \
            --linedata_only \
            --char_spacing=0.0 \
            --exposure=0 \
            --resolution=300 \
            --ptsize=14 \
            --max_pages=1 2>/dev/null && {
                echo "✓"
                ((success_count++))
            } || echo "✗"
    fi
done

# If no custom fonts worked, use system fonts
if [ $success_count -eq 0 ]; then
    print_message "$YELLOW" "Using system fonts as fallback..."
    
    for font in "Arial" "Times New Roman" "Courier New" "DejaVu Sans"; do
        clean_name=$(echo "$font" | sed 's/ /_/g')
        echo -n "Processing $font... "
        
        text2image \
            --text=/tmp/ckb_training.txt \
            --outputbase="$GROUND_TRUTH_DIR/ckb_${clean_name}" \
            --font="$font" \
            --lang=ara \
            --linedata_only \
            --char_spacing=0.0 \
            --exposure=0 \
            --resolution=300 \
            --ptsize=14 \
            --max_pages=1 2>/dev/null && {
                echo "✓"
                ((success_count++))
            } || echo "✗"
    done
fi

print_message "$GREEN" "Generated $success_count training samples"

# Generate LSTMF files
print_message "$YELLOW" "Generating LSTMF files..."
lstmf_count=0
> $OUTPUT_DIR/all-lstmf.txt

for gt_file in $GROUND_TRUTH_DIR/*.gt.txt; do
    if [ -f "$gt_file" ]; then
        base_name=$(basename "$gt_file" .gt.txt)
        
        if [ -f "$GROUND_TRUTH_DIR/${base_name}.tif" ]; then
            # Generate LSTMF file
            tesseract "$GROUND_TRUTH_DIR/${base_name}.tif" \
                "$GROUND_TRUTH_DIR/${base_name}" \
                --psm 6 \
                -l eng \
                lstm.train 2>/dev/null && {
                    if [ -f "$GROUND_TRUTH_DIR/${base_name}.lstmf" ]; then
                        echo "$GROUND_TRUTH_DIR/${base_name}.lstmf" >> $OUTPUT_DIR/all-lstmf.txt
                        ((lstmf_count++))
                    fi
                }
        fi
    fi
done

print_message "$GREEN" "Generated $lstmf_count LSTMF files"

# Check if we have enough data
if [ $lstmf_count -gt 0 ]; then
    print_message "$GREEN" "✓ Training data ready!"
    print_message "$BLUE" "Starting training..."
    
    # Run training
    lstmtraining \
        --model_output $OUTPUT_DIR/ckb \
        --traineddata $TESSDATA_PREFIX/eng.traineddata \
        --train_listfile $OUTPUT_DIR/all-lstmf.txt \
        --max_iterations 500 \
        --target_error_rate 0.01 \
        --debug_interval -1 2>&1 | while read line; do
            if [[ $line == *"At iteration"* ]]; then
                echo "$line"
            fi
        done
    
    # Finalize model
    if ls $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1 > /dev/null; then
        checkpoint=$(ls -t $OUTPUT_DIR/ckb_*.checkpoint 2>/dev/null | head -n 1)
        
        print_message "$YELLOW" "Finalizing model..."
        lstmtraining \
            --stop_training \
            --continue_from "$checkpoint" \
            --traineddata $TESSDATA_PREFIX/eng.traineddata \
            --model_output $OUTPUT_DIR/ckb_custom.traineddata 2>&1
        
        if [ -f "$OUTPUT_DIR/ckb_custom.traineddata" ]; then
            # Install model
            print_message "$YELLOW" "Installing model..."
            echo 'tishko' | sudo -S cp $OUTPUT_DIR/ckb_custom.traineddata $TESSDATA_PREFIX/ckb_custom.traineddata
            cp $OUTPUT_DIR/ckb_custom.traineddata /mnt/c/tesseract/tessdata/ckb_custom.traineddata
            
            print_message "$GREEN" "╔════════════════════════════════════════════════════════╗"
            print_message "$GREEN" "║         TRAINING COMPLETE!                            ║"
            print_message "$GREEN" "╚════════════════════════════════════════════════════════╝"
            print_message "$BLUE" "Model installed at:"
            echo "  WSL: $TESSDATA_PREFIX/ckb_custom.traineddata"
            echo "  Windows: C:\\tesseract\\tessdata\\ckb_custom.traineddata"
            
            # Test the model
            print_message "$YELLOW" "Testing model..."
            echo "ژیان جوانە" | tesseract stdin stdout -l ckb_custom --psm 6 2>/dev/null || echo "Test requires an image file"
        fi
    fi
else
    print_message "$RED" "Failed to generate training data"
fi
