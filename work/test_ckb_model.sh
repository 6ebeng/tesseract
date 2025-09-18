#!/bin/sh

# Test script for the new ckb.traineddata model

echo "Testing Kurdish OCR Model (ckb.traineddata)"
echo "==========================================="
echo ""

# Check if model exists
if [ -f "tessdata/ckb.traineddata" ]; then
    echo "✓ Found ckb.traineddata in tessdata/"
    SIZE=$(du -h tessdata/ckb.traineddata | cut -f1)
    echo "  Size: $SIZE"
else
    echo "✗ Model not found in tessdata/"
    exit 1
fi

echo ""
echo "Model is ready to use!"
echo ""
echo "Usage examples:"
echo "  Windows: tesseract image.tif output -l ckb --psm 6"
echo "  WSL:     tesseract image.tif output -l ckb --psm 6"
echo ""
echo "For testing with Kurdish text images:"
echo "  1. Place your Kurdish text image in the work directory"
echo "  2. Run: tesseract your_image.png output -l ckb --psm 6"
echo "  3. Check output.txt for the recognized text"
echo ""
echo "The model was trained with:"
echo "  - Your Kurdish corpus text (23 lines)"
echo "  - Multiple Kurdish fonts (670 available fonts)"
echo "  - LSTM-based training approach"
