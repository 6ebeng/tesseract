#!/bin/bash

# Kurdish OCR Wrapper - Uses Arabic model with character mapping
# Usage: kurdish_ocr.sh input.png output

INPUT_FILE="$1"
OUTPUT_BASE="$2"

if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_BASE" ]; then
    echo "Usage: $0 input.png output_base"
    exit 1
fi

# Set tessdata path
export TESSDATA_PREFIX="/mnt/c/tesseract/tessdata"

# Run Tesseract with Arabic model
tesseract "$INPUT_FILE" "${OUTPUT_BASE}_raw" -l ara 2>/dev/null

# Fix Kurdish characters
if [ -f "${OUTPUT_BASE}_raw.txt" ]; then
    python3 /mnt/c/tesseract/work/output/fix_kurdish_text.py "${OUTPUT_BASE}_raw.txt" "${OUTPUT_BASE}.txt"
    echo "Kurdish OCR completed: ${OUTPUT_BASE}.txt"
else
    echo "Error: Tesseract failed to process $INPUT_FILE"
    exit 1
fi
