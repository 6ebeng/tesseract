#!/bin/bash

# This script is for debugging font issues with text2image
# It isolates the environment and provides detailed error output

set -x # Enable debugging output to see commands as they are executed

# --- CONFIGURATION ---
WORK_DIR="$(pwd)/work"
FONTS_DIR="$WORK_DIR/fonts"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_BASE="$WORK_DIR/font-test/test"
FONT_NAME="00_Sarchia_ABC" # A specific font to test

# Set FONTCONFIG_PATH to the parent directory of the fonts.conf file
# This forces fontconfig to use our local configuration
export FONTCONFIG_PATH="$(pwd)"
export FONTCONFIG_FILE="$FONTCONFIG_PATH/fonts.conf"

echo "--- Debugging Font: $FONT_NAME ---"
echo "Work Directory: $WORK_DIR"
echo "Fonts Directory: $FONTS_DIR"
echo "Corpus File: $CORPUS_FILE"
echo "Output Base: $OUTPUT_BASE"
echo "FONTCONFIG_PATH: $FONTCONFIG_PATH"

# Verify that the local fonts.conf exists
if [ ! -f "$FONTCONFIG_PATH/fonts.conf" ]; then
    echo "ERROR: fonts.conf not found in $FONTCONFIG_PATH"
    exit 1
fi

# Clean up previous test files
rm -f ${OUTPUT_BASE}.*

# Run text2image with verbose output
# We are NOT redirecting stderr to /dev/null so we can see the errors
text2image \
    --text="$CORPUS_FILE" \
    --outputbase="$OUTPUT_BASE" \
    --font="$FONT_NAME" \
    --fonts_dir="$FONTS_DIR" \
    --resolution=300 \
    --ptsize=12 \
    --max_pages=1

# Check if the image was created
if [ -f "${OUTPUT_BASE}.tif" ]; then
    echo "--- SUCCESS ---"
    echo "Successfully created ${OUTPUT_BASE}.tif"
else
    echo "--- FAILURE ---"
    echo "Failed to create image file. Please check the error messages above."
fi
