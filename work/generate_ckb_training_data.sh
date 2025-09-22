#!/bin/bash

# Kurdish Training Data Generation - All Fonts (Clean)
# Generates training images/box files using text2image for all TTF fonts in fonts/

echo "Kurdish Training Data Generation - Comprehensive"
echo "=============================================="

# Configuration
LANG_CODE="ckb"
CORPUS_FILE="corpus/ckb.training_text"
FONTS_DIR="fonts"
OUTPUT_DIR="training_output"
GROUND_TRUTH_DIR="$OUTPUT_DIR/ground_truth"

# Create directories
mkdir -p "$GROUND_TRUTH_DIR"

echo ""
echo "📂 Setting up directories:"
echo "Output: $OUTPUT_DIR"
echo "Ground Truth: $GROUND_TRUTH_DIR"

# Font settings for optimal Kurdish recognition
FONT_SIZE=18
DPI=300
MARGIN=15
LEADING=22

echo ""
echo "🎨 Font Generation Settings:"
echo "=========================="
echo "Font Size: ${FONT_SIZE}pt"
echo "DPI: ${DPI}"
echo "Margin: ${MARGIN}px"
echo "Leading: ${LEADING}px"

# Count available fonts
FONT_COUNT=$(ls $FONTS_DIR/*.ttf 2>/dev/null | wc -l)
echo "Available Fonts: $FONT_COUNT"

if [ $FONT_COUNT -eq 0 ]; then
    echo "❌ Error: No TTF fonts found in $FONTS_DIR"
    exit 1
fi

echo ""
echo "🔤 Generating training data for all fonts..."
echo "============================================"

GENERATED_COUNT=0
ERROR_COUNT=0

# Process each font
for font_file in $FONTS_DIR/*.ttf; do
    if [ ! -f "$font_file" ]; then
        continue
    fi
    
    font_name=$(basename "$font_file" .ttf)
    echo -n "Processing font: $font_name ... "
    
    # Generate image and box file
    output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp0"
    
    # Generate training image using text2image
    # Use font family name; provide fonts_dir so text2image can discover TTFs
    if text2image \
        --text="$CORPUS_FILE" \
        --outputbase="$output_base" \
        --font="$font_name" \
        --fonts_dir="$(pwd)/$FONTS_DIR" \
        --ptsize=$FONT_SIZE \
        --resolution=$DPI \
        --margin=$MARGIN \
        --leading=$LEADING \
        --char_spacing=1 \
        --exposure=0 \
        2>/dev/null; then
        
        # Verify files were created
        if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
            echo "✅ Success"
            ((GENERATED_COUNT++))
            
            # Create corresponding .gt.txt file for ground truth
            cp "$CORPUS_FILE" "${output_base}.gt.txt"
            
        else
            echo "❌ Failed (missing files)"
            ((ERROR_COUNT++))
        fi
    else
        echo "❌ Failed (text2image error)"
        ((ERROR_COUNT++))
    fi
done

echo ""
echo "📊 Generation Summary:"
echo "===================="
echo "Successfully generated: $GENERATED_COUNT font variations"
echo "Failed: $ERROR_COUNT font variations"
echo "Total processed: $FONT_COUNT fonts"

if [ $GENERATED_COUNT -eq 0 ]; then
    echo ""
    echo "❌ No training data generated! Checking common issues..."
    
    # Check if text2image is available
    if ! command -v text2image &> /dev/null; then
        echo "   - text2image command not found"
        echo "   - Install: sudo apt-get install tesseract-ocr-dev"
    fi
    
    # Check corpus file
    if [ ! -f "$CORPUS_FILE" ]; then
        echo "   - Corpus file missing: $CORPUS_FILE"
    fi
    
    # Check fonts directory
    if [ ! -d "$FONTS_DIR" ]; then
        echo "   - Fonts directory missing: $FONTS_DIR"
    fi
    
    exit 1
fi

echo ""
echo "🔍 Verifying generated data..."
echo "============================="

# List generated files
TIF_COUNT=$(ls $GROUND_TRUTH_DIR/*.tif 2>/dev/null | wc -l)
BOX_COUNT=$(ls $GROUND_TRUTH_DIR/*.box 2>/dev/null | wc -l)
GT_COUNT=$(ls $GROUND_TRUTH_DIR/*.gt.txt 2>/dev/null | wc -l)

echo "Generated .tif files: $TIF_COUNT"
echo "Generated .box files: $BOX_COUNT"
echo "Generated .gt.txt files: $GT_COUNT"

if [ $TIF_COUNT -gt 0 ] && [ $BOX_COUNT -gt 0 ]; then
    echo ""
    echo "✅ Training data generation successful!"
    echo "   Ready for model training"
    
    # Show sample of what was generated
    echo ""
    echo "📝 Sample generated files:"
    ls $GROUND_TRUTH_DIR/*.tif | head -3
    
    # Check file sizes
    echo ""
    echo "📏 File size verification:"
    for sample_file in $(ls $GROUND_TRUTH_DIR/*.tif | head -3); do
        size=$(stat -c%s "$sample_file")
        echo "   $(basename $sample_file): ${size} bytes"
    done
    
else
    echo ""
    echo "❌ Training data generation incomplete!"
    echo "   Missing required files for training"
    exit 1
fi

echo ""
echo "🎯 Next Step: Run ./execute_ckb_training.sh to start model training"