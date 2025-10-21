#!/bin/bash
# Create clean test images using Tesseract's text2image (same as training)

cd /mnt/c/tesseract/work

echo "======================================================================"
echo "Creating Clean Test Images Using text2image"
echo "======================================================================"

mkdir -p real_gt/eval_clean

export FONTCONFIG_FILE=/mnt/c/tesseract/fonts.conf

echo ""
echo "📋 Processing ground truth files..."
echo ""

for gt_file in real_gt/eval_multi/*.gt.txt; do
    base=$(basename "$gt_file" .gt.txt)
    echo "  Rendering ${base}..."
    
    # Copy GT file
    cp "$gt_file" "real_gt/eval_clean/${base}.gt.txt"
    
    # Use text2image with same settings as training
    text2image \
        --text="real_gt/eval_clean/${base}.gt.txt" \
        --outputbase="real_gt/eval_clean/${base}" \
        --font="Noto Naskh Arabic" \
        --fonts_dir=/usr/share/fonts \
        --ptsize=18 \
        --resolution=300 \
        --char_spacing=1.0 \
        --leading=22 \
        --exposure=0 \
        --unicharset_file=charsets/Arabic.unicharset \
        2>&1 | grep -E "(Error|Warning)" | head -2 || echo "    ✅ Success"
    
    # Check if created
    if [ -f "real_gt/eval_clean/${base}.tif" ]; then
        size=$(du -h "real_gt/eval_clean/${base}.tif" | cut -f1)
        echo "       Size: ${size}"
    fi
done

echo ""
echo "======================================================================"
echo "📁 Created Test Images"
echo "======================================================================"
ls -lh real_gt/eval_clean/*.tif

echo ""
