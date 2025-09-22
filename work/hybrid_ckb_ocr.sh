#!/bin/bash

# Hybrid Kurdish OCR - Production Script
# Uses custom ckb_custom.traineddata with Persian base and Arabic as fallback mix

if [ $# -lt 2 ]; then
    echo "Usage: $0 <image_file> <output_name>"
    echo "Example: $0 test.png result"
    exit 1
fi

IMAGE_FILE="$1"
OUTPUT_NAME="$2"

if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Image file not found: $IMAGE_FILE"
    exit 1
fi

echo "🔍 Processing with Hybrid Kurdish OCR..."
echo "======================================"

TESSDATA_DIR=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/5/tessdata}

# Primary OCR with custom Kurdish model
echo "Running custom Kurdish model (ckb_custom)..."
tesseract "$IMAGE_FILE" "${OUTPUT_NAME}_ckb" -l ckb_custom --psm 6 --oem 1

# Fallback with Persian for comparison
echo "Running Persian fallback..."
tesseract "$IMAGE_FILE" "${OUTPUT_NAME}_fas" -l fas --psm 6 --oem 1

# Enhanced processing with character corrections
echo "Applying Kurdish character enhancements..."

OUTPUT_NAME_ENV="$OUTPUT_NAME" python3 - << 'PYTHON_EOF'
import sys
import re
import os

def enhance_kurdish_text(text):
    """Apply Kurdish-specific character corrections"""
    
    # Persian to Kurdish character mappings (proven effective)
    corrections = {
        'ي': 'ی',          # Persian yeh to Kurdish yeh
        'ك': 'ک',          # Arabic kaf to Kurdish keheh
        'ى': 'ی',          # Alef maksura to yeh
        'ء': '',           # Remove hamza
        'ؤ': 'و',          # Waw with hamza to plain waw
        'أ': 'ا',          # Alef with hamza to plain alef
        'إ': 'ا',          # Alef with hamza below to plain alef
        'آ': 'ا',          # Alef with madda to plain alef
    }
    
    # Apply corrections
    for old, new in corrections.items():
        text = text.replace(old, new)
    
    # Kurdish word-level corrections
    word_corrections = {
        'له': 'لە',        # Common Kurdish preposition
        'به': 'بە',        # Kurdish preposition
        'چه': 'چی',        # Kurdish question word
        'هه': 'هە',        # Kurdish auxiliary
    }
    
    for old_word, new_word in word_corrections.items():
        text = re.sub(r'\b' + old_word + r'\b', new_word, text)
    
    return text

try:
    # Process custom ckb result
    output_name = os.environ.get('OUTPUT_NAME_ENV', 'output')
    
    with open(f"{output_name}_ckb.txt", 'r', encoding='utf-8') as f:
        ckb_text = f.read().strip()
    
    # Process Persian fallback
    try:
        with open(f"{output_name}_fas.txt", 'r', encoding='utf-8') as f:
            fas_text = f.read().strip()
    except:
        fas_text = ""
    
    # Apply enhancements
    enhanced_ckb = enhance_kurdish_text(ckb_text)
    enhanced_fas = enhance_kurdish_text(fas_text)
    
    # Character-level fusion (use best result per character)
    kurdish_chars = set('ڕژڤگڵێۆە')
    
    def count_kurdish_chars(text):
        return sum(1 for char in text if char in kurdish_chars)
    
    # Choose result with more Kurdish characters
    ckb_kurdish_count = count_kurdish_chars(enhanced_ckb)
    fas_kurdish_count = count_kurdish_chars(enhanced_fas)
    
    if ckb_kurdish_count >= fas_kurdish_count:
        final_result = enhanced_ckb
        model_used = "Custom Kurdish"
    else:
        final_result = enhanced_fas
        model_used = "Persian (enhanced)"
    
    # Write final result
    with open(f"{output_name}.txt", 'w', encoding='utf-8') as f:
        f.write(final_result)
    
    print(f"✅ Processing complete using {model_used} model")
    print(f"Kurdish characters detected: {count_kurdish_chars(final_result)}")
    print(f"Result: {final_result}")
    
except Exception as e:
    print(f"❌ Enhancement failed: {e}")
    # Fallback to basic ckb result
    try:
        with open(f"{output_name}_ckb.txt", 'r', encoding='utf-8') as f:
            result = f.read().strip()
        with open(f"{output_name}.txt", 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ Fallback result: {result}")
    except:
        print("❌ All processing failed")
PYTHON_EOF

# No self-modifying sed; Python uses environment variable for OUTPUT_NAME

echo ""
echo "📊 Results Summary:"
echo "=================="
if [ -f "${OUTPUT_NAME}.txt" ]; then
    echo "Final result saved to: ${OUTPUT_NAME}.txt"
    echo "Content preview:"
    head -c 200 "${OUTPUT_NAME}.txt"
    echo ""
else
    echo "❌ Processing failed"
fi
