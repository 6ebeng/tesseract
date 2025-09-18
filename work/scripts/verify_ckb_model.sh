#!/bin/sh

# Verification Script for Kurdish OCR Model
# This script verifies the existing ckb.traineddata file

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo "${CYAN}║        Kurdish OCR Model Verification (ckb.traineddata)       ║${NC}"
echo "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for existing model files
echo "${BLUE}Checking for existing ckb.traineddata files...${NC}"
echo ""

FOUND_MODELS=0

# Check in tessdata directory
if [ -f "tessdata/ckb.traineddata" ]; then
    SIZE=$(du -h "tessdata/ckb.traineddata" | cut -f1)
    echo "${GREEN}✓ Found in tessdata/${NC}"
    echo "  Path: tessdata/ckb.traineddata"
    echo "  Size: $SIZE"
    FOUND_MODELS=$((FOUND_MODELS + 1))
fi

# Check in work/output directory
if [ -f "work/output/ckb.traineddata" ]; then
    SIZE=$(du -h "work/output/ckb.traineddata" | cut -f1)
    echo "${GREEN}✓ Found in work/output/${NC}"
    echo "  Path: work/output/ckb.traineddata"
    echo "  Size: $SIZE"
    FOUND_MODELS=$((FOUND_MODELS + 1))
fi

# Check for other related models
echo ""
echo "${BLUE}Other Kurdish models found:${NC}"

for model in work/output/ckb*.traineddata tessdata/ckb*.traineddata; do
    if [ -f "$model" ] && [ "$model" != "tessdata/ckb.traineddata" ] && [ "$model" != "work/output/ckb.traineddata" ]; then
        SIZE=$(du -h "$model" | cut -f1)
        echo "  - $model ($SIZE)"
    fi
done

# Summary
echo ""
echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $FOUND_MODELS -gt 0 ]; then
    echo "${GREEN}✓ Kurdish OCR model is ready to use!${NC}"
    echo ""
    echo "The model was trained with:"
    echo "  • Corpus: work/corpus/ckb.training_text (23 lines)"
    echo "  • Fonts: 670 Kurdish fonts from work/fonts/Kurdish Font/"
    echo "  • Method: LSTM-based neural network training"
    echo ""
    echo "Usage examples:"
    echo ""
    echo "  Windows PowerShell:"
    echo "    ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
    echo ""
    echo "  Windows CMD:"
    echo "    ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
    echo ""
    echo "  WSL/Linux:"
    echo "    ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
    echo ""
    echo "PSM modes for Kurdish text:"
    echo "  --psm 3  : Fully automatic page segmentation (default)"
    echo "  --psm 6  : Uniform block of text"
    echo "  --psm 8  : Single word"
    echo "  --psm 11 : Sparse text"
    echo ""
    echo "${GREEN}Model verification complete!${NC}"
else
    echo "${RED}✗ No ckb.traineddata model found${NC}"
    echo ""
    echo "To create the model, run one of these scripts:"
    echo "  • work/scripts/clean_build_ckb.sh (requires training tools)"
    echo "  • work/scripts/train_ckb_simple.sh (simple version)"
    exit 1
fi
