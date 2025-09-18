#!/bin/bash

# Test Installation Script
# Verifies that the Kurdish OCR system is properly installed and working

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Kurdish OCR Installation Test                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Function to check if file/directory exists
check_exists() {
    local path=$1
    local type=$2
    local description=$3
    
    if [ -e "$path" ]; then
        echo -e "${GREEN}✓${NC} $description exists"
        return 0
    else
        echo -e "${RED}✗${NC} $description missing: $path"
        return 1
    fi
}

# Function to test OCR
test_ocr() {
    local test_image=$1
    local lang=$2
    
    echo -e "${YELLOW}Testing OCR with $lang language...${NC}"
    
    if tesseract "$test_image" stdout -l "$lang" --psm 6 2>/dev/null | head -n 1 > /dev/null; then
        echo -e "${GREEN}✓${NC} OCR test passed for $lang"
        return 0
    else
        echo -e "${RED}✗${NC} OCR test failed for $lang"
        return 1
    fi
}

# Set TESSDATA_PREFIX
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Check directory structure
echo -e "${BLUE}Checking directory structure...${NC}"
check_exists "/mnt/c/tesseract/work/scripts" "d" "Scripts directory"
check_exists "/mnt/c/tesseract/work/test-images" "d" "Test images directory"
check_exists "/mnt/c/tesseract/work/docs" "d" "Documentation directory"
check_exists "/mnt/c/tesseract/work/output" "d" "Output directory"

echo ""

# Check important scripts (only the 3 essential ones)
echo -e "${BLUE}Checking essential scripts...${NC}"
check_exists "/mnt/c/tesseract/work/scripts/master_training.sh" "f" "Master training script"
check_exists "/mnt/c/tesseract/work/scripts/quick_test.sh" "f" "Quick test script"
check_exists "/mnt/c/tesseract/work/scripts/test_installation.sh" "f" "Test installation script"

echo ""

# Check model installation
echo -e "${BLUE}Checking model installation...${NC}"
check_exists "/usr/share/tesseract-ocr/5/tessdata/ckb.traineddata" "f" "Kurdish model (WSL)"
check_exists "/mnt/c/tesseract/tessdata/ckb.traineddata" "f" "Kurdish model (Windows)"

echo ""

# Check for test images
echo -e "${BLUE}Checking test data...${NC}"
test_count=$(ls /mnt/c/tesseract/work/test-images/*.tif 2>/dev/null | wc -l)
if [ "$test_count" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $test_count test images"
else
    echo -e "${RED}✗${NC} No test images found"
fi

echo ""

# Test OCR functionality
echo -e "${BLUE}Testing OCR functionality...${NC}"
cd /mnt/c/tesseract/work/test-images

# Find a test image
test_image=$(ls *.tif 2>/dev/null | head -n 1)

if [ -n "$test_image" ]; then
    # Test with Kurdish model
    test_ocr "$test_image" "ckb"
    
    # Test with English for comparison
    test_ocr "$test_image" "eng"
else
    echo -e "${RED}✗${NC} No test images available for OCR test"
fi

echo ""

# Check documentation
echo -e "${BLUE}Checking documentation...${NC}"
check_exists "/mnt/c/tesseract/work/README.md" "f" "README file"
check_exists "/mnt/c/tesseract/work/QUICK_START_GUIDE.md" "f" "Quick Start Guide"
check_exists "/mnt/c/tesseract/work/docs/FINAL_TRAINING_REPORT.md" "f" "Training report"

echo ""

# Summary
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                       ║"
echo "╚════════════════════════════════════════════════════════╝"

# Count successes and failures
if [ -f "/usr/share/tesseract-ocr/5/tessdata/ckb.traineddata" ] && \
   [ -f "/mnt/c/tesseract/tessdata/ckb.traineddata" ] && \
   [ -f "/mnt/c/tesseract/work/scripts/master_training.sh" ]; then
    echo -e "${GREEN}✓ System is properly installed and ready to use${NC}"
    echo ""
    echo "To start training or testing, run:"
    echo "  bash /mnt/c/tesseract/work/scripts/master_training.sh"
    echo ""
    echo "For quick testing, run:"
    echo "  bash /mnt/c/tesseract/work/scripts/quick_test.sh"
    exit 0
else
    echo -e "${RED}✗ Some components are missing. Please check the errors above.${NC}"
    exit 1
fi
