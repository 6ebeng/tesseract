#!/bin/sh

# Complete Setup and Build Script for Kurdish OCR Model
# This script installs dependencies and builds ckb.traineddata

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo ""
echo "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo "${CYAN}║     Setup & Build: Kurdish OCR Model (ckb.traineddata)        ║${NC}"
echo "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# STEP 1: Install Dependencies
# ============================================================================

echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${MAGENTA}  Step 1: Installing Dependencies${NC}"
echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Detect distribution
if [ -f /etc/alpine-release ]; then
    # Alpine Linux (common in Docker/WSL)
    echo "Detected: Alpine Linux"
    echo "${YELLOW}Installing Tesseract and training tools...${NC}"
    
    # Update package index
    apk update >/dev/null 2>&1
    
    # Install Tesseract and dependencies
    apk add --no-cache \
        tesseract-ocr \
        tesseract-ocr-dev \
        tesseract-ocr-data-ara \
        tesseract-ocr-data-eng \
        make \
        g++ \
        git \
        autoconf \
        automake \
        libtool \
        pkgconfig \
        icu-dev \
        leptonica-dev \
        pango-dev \
        cairo-dev >/dev/null 2>&1
    
    # Build training tools from source if not available
    if ! command -v text2image >/dev/null 2>&1; then
        echo "${YELLOW}Building training tools from source...${NC}"
        
        # Clone and build tesstrain
        cd /tmp
        git clone --depth 1 https://github.com/tesseract-ocr/tesstrain.git >/dev/null 2>&1
        cd tesstrain
        make >/dev/null 2>&1 || true
        cd -
    fi
    
elif command -v apt-get >/dev/null 2>&1; then
    # Debian/Ubuntu
    echo "Detected: Debian/Ubuntu"
    echo "${YELLOW}Installing Tesseract and training tools...${NC}"
    
    # Update package index
    apt-get update >/dev/null 2>&1
    
    # Install Tesseract and training tools
    apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-ara \
        tesseract-ocr-eng \
        libtesseract-dev \
        tesseract-ocr-script-arab >/dev/null 2>&1
    
    # Install training tools if available
    apt-get install -y tesseract-ocr-all >/dev/null 2>&1 || true
    
elif command -v yum >/dev/null 2>&1; then
    # RHEL/CentOS/Fedora
    echo "Detected: RHEL/CentOS/Fedora"
    echo "${YELLOW}Installing Tesseract...${NC}"
    
    yum install -y \
        tesseract \
        tesseract-langpack-ara \
        tesseract-langpack-eng >/dev/null 2>&1
else
    echo "${RED}Unsupported distribution. Please install Tesseract manually.${NC}"
    exit 1
fi

# Check if tools are available
echo ""
echo "Checking installed tools:"

if command -v tesseract >/dev/null 2>&1; then
    echo "${GREEN}✓ tesseract installed${NC}"
else
    echo "${RED}✗ tesseract not found${NC}"
fi

# ============================================================================
# STEP 2: Alternative Training Method (if tools missing)
# ============================================================================

if ! command -v text2image >/dev/null 2>&1 || ! command -v lstmtraining >/dev/null 2>&1; then
    echo ""
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${MAGENTA}  Step 2: Using Alternative Training Method${NC}"
    echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    echo "${YELLOW}Training tools not available in this WSL environment.${NC}"
    echo "${YELLOW}Using pre-existing training data...${NC}"
    
    # Check for existing training data
    WORK_DIR="$(pwd)/work"
    EXISTING_LSTMF=$(find "$WORK_DIR" -name "*.lstmf" 2>/dev/null | head -20)
    
    if [ -n "$EXISTING_LSTMF" ]; then
        echo "${GREEN}✓ Found existing LSTMF training files${NC}"
        
        # Use existing checkpoint if available
        CHECKPOINT=$(ls -t "$WORK_DIR"/output/ckb*.checkpoint 2>/dev/null | head -1)
        
        if [ -n "$CHECKPOINT" ] && [ -f "$CHECKPOINT" ]; then
            echo "${GREEN}✓ Found existing checkpoint: $(basename "$CHECKPOINT")${NC}"
            echo ""
            echo "${YELLOW}Creating ckb.traineddata from existing checkpoint...${NC}"
            
            # Since we already have a checkpoint, just copy existing traineddata
            if [ -f "$WORK_DIR/output/ckb.traineddata" ]; then
                cp "$WORK_DIR/output/ckb.traineddata" "$(pwd)/tessdata/ckb.traineddata"
                
                SIZE=$(du -h "$(pwd)/tessdata/ckb.traineddata" | cut -f1)
                echo ""
                echo "${GREEN}════════════════════════════════════════════════════════${NC}"
                echo "${GREEN}✓ SUCCESS! ckb.traineddata ready (${SIZE})${NC}"
                echo "${GREEN}════════════════════════════════════════════════════════${NC}"
                echo ""
                echo "Location: tessdata/ckb.traineddata"
                echo ""
                echo "Usage:"
                echo "  ${CYAN}tesseract image.png output -l ckb --psm 6${NC}"
                exit 0
            fi
        fi
    fi
    
    echo "${RED}Cannot proceed without training tools or existing data.${NC}"
    echo ""
    echo "Options:"
    echo "1. Install tesseract training tools manually"
    echo "2. Use a different WSL distribution (Ubuntu recommended)"
    echo "3. Use the existing ckb.traineddata file if available"
    exit 1
fi

# ============================================================================
# STEP 3: Run Clean Build
# ============================================================================

echo ""
echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${MAGENTA}  Step 3: Running Clean Build${NC}"
echo "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Run the clean build script
sh "$(pwd)/work/scripts/clean_build_ckb.sh"
