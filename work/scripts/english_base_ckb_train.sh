#!/bin/bash

# Kurdish OCR Training with English Base Model (UTF-8 Enabled)
# This script ensures proper UTF-8 encoding for Kurdish characters

set -e

# Enable UTF-8 encoding
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8

echo "=== CKB Training with UTF-8 Encoding (CTC Fix) ==="

# Set up environment with UTF-8 support
export TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"
cd /mnt/c/tesseract/work

# Create output directory
mkdir -p output

echo "=== Preparing training data with English base model ==="

# Generate training image using first available Sarchia font
FONT_NAME=$(fc-list | grep -i sarchia | head -1 | cut -d: -f2 | cut -d, -f1 | xargs)
if [ -z "$FONT_NAME" ]; then
    echo "Error: No Sarchia fonts found"
    exit 1
fi

echo "Using font: $FONT_NAME"

# Generate training image with UTF-8 encoding
text2image \
    --text=corpus/ckb.training_text \
    --outputbase=output/ckb.eng_base \
    --font="$FONT_NAME" \
    --fonts_dir=/usr/share/fonts \
    --fontconfig_tmpdir=/tmp \
    --unicharset_file=output/ckb.unicharset \
    --char_spacing=1.0 \
    --leading=12 \
    --resolution=300

# Create box file using English OCR (temporary step for alignment)
tesseract output/ckb.eng_base.tif output/ckb.eng_base -l eng --psm 6 lstm.train

echo "=== Starting LSTM training with English base model ==="

# Download English base model if not present
if [ ! -f "eng.traineddata" ]; then
    echo "Downloading English base model..."
    wget -q https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata -O eng.traineddata
fi

# Extract LSTM model from English base
lstmtraining \
    --model_output output/ckb_eng_base \
    --continue_from eng.traineddata \
    --traineddata eng.traineddata \
    --train_listfile <(echo "output/ckb.eng_base.lstmf") \
    --max_iterations 400 \
    --learning_rate 0.002 \
    --net_spec '[1,36,0,1 Ct3,3,16 Mp3,3 Lfys48 Lfx96 Lrx96 Lfx256 O1c85]'

echo "=== Creating final model ==="

# Create final traineddata file
lstmtraining \
    --stop_training \
    --continue_from output/ckb_eng_base_checkpoint \
    --traineddata eng.traineddata \
    --model_output ../tessdata/ckb_fixed.traineddata

echo "=== Training completed successfully ==="
echo "New model saved as: ckb_fixed.traineddata"
echo "Test with: tesseract image.png output -l ckb_fixed"