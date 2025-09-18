#!/bin/bash

# Quick Test Script for Kurdish OCR
# This script provides a quick way to test the OCR model

export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

echo "╔════════════════════════════════════════════════════════╗"
echo "║           Kurdish OCR Quick Test                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

TEST_DIR=/mnt/c/tesseract/work/test-images

if [ ! -d "$TEST_DIR" ]; then
    echo "Error: Test directory not found!"
    exit 1
fi

cd $TEST_DIR

# Get first test image
TEST_IMAGE=$(ls *.tif 2>/dev/null | head -n 1)

if [ -z "$TEST_IMAGE" ]; then
    echo "Error: No test images found!"
    exit 1
fi

echo "Testing with: $TEST_IMAGE"
echo "----------------------------------------"

# Run OCR
echo "OCR Output:"
tesseract "$TEST_IMAGE" stdout -l ckb --psm 6 2>/dev/null

echo ""
echo "----------------------------------------"

# Show original text if available
BASE_NAME="${TEST_IMAGE%.tif}"
if [ -f "${BASE_NAME}.txt" ]; then
    echo "Original Text:"
    cat "${BASE_NAME}.txt"
else
    echo "No ground truth text file found for comparison"
fi

echo ""
echo "Test complete!"
echo ""
echo "To test all images, run:"
echo "  bash /mnt/c/tesseract/work/scripts/master_training.sh"
echo "  Then select option 5"
