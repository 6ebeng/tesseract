#!/bin/bash
# Create synthetic test images from Kurdish news corpus for validation
# This will help determine if mgk.tif is an outlier or representative

cd /mnt/c/tesseract/work

echo "======================================================================"
echo "Creating Synthetic Test Images from Batch 2 News Corpus"
echo "======================================================================"

# Create output directory
mkdir -p real_gt/eval_synthetic

echo ""
echo "📝 Extracting sample texts from Batch 2 corpus..."

# Extract 5 different samples (20 lines each) from different parts of corpus
# Sample 1: Lines 1-20 (beginning)
head -20 corpus/kurdish_news_batch2.txt | grep -v '^#' | grep -v '^$' > real_gt/eval_synthetic/sample1.gt.txt

# Sample 2: Lines 300-320 (middle-early)
sed -n '300,320p' corpus/kurdish_news_batch2.txt | grep -v '^#' | grep -v '^$' > real_gt/eval_synthetic/sample2.gt.txt

# Sample 3: Lines 700-720 (middle)
sed -n '700,720p' corpus/kurdish_news_batch2.txt | grep -v '^#' | grep -v '^$' > real_gt/eval_synthetic/sample3.gt.txt

# Sample 4: Lines 1100-1120 (middle-late)
sed -n '1100,1120p' corpus/kurdish_news_batch2.txt | grep -v '^#' | grep -v '^$' > real_gt/eval_synthetic/sample4.gt.txt

# Sample 5: Last 20 lines (end)
tail -20 corpus/kurdish_news_batch2.txt | grep -v '^#' | grep -v '^$' > real_gt/eval_synthetic/sample5.gt.txt

echo "✅ Created 5 sample ground truth files"
echo ""

# Count lines in each
for i in {1..5}; do
    lines=$(wc -l < real_gt/eval_synthetic/sample${i}.gt.txt)
    chars=$(wc -c < real_gt/eval_synthetic/sample${i}.gt.txt)
    echo "  sample${i}.gt.txt: ${lines} lines, ${chars} chars"
done

echo ""
echo "📷 Generating images using text2image..."
echo ""

# Use Tesseract's text2image to create synthetic test images
# Using NotoNaskhArabic-Bold font at 18pt, 300 DPI
FONT="NotoNaskhArabic-Bold"
FONT_SIZE=18
DPI=300

for i in {1..5}; do
    echo "  Generating sample${i}.tif..."
    
    text2image \
        --text=real_gt/eval_synthetic/sample${i}.gt.txt \
        --outputbase=real_gt/eval_synthetic/sample${i} \
        --font="${FONT}" \
        --fonts_dir=/mnt/c/tesseract/work/fonts \
        --ptsize=${FONT_SIZE} \
        --resolution=${DPI} \
        --char_spacing=1.0 \
        --leading=22 \
        --exposure=0 \
        --unicharset_file=charsets/Arabic.unicharset \
        2>&1 | grep -v "Warning"
    
    if [ -f "real_gt/eval_synthetic/sample${i}.tif" ]; then
        size=$(du -h real_gt/eval_synthetic/sample${i}.tif | cut -f1)
        echo "    ✅ Created (${size})"
    else
        echo "    ❌ Failed"
    fi
done

echo ""
echo "======================================================================"
echo "✅ Test Image Generation Complete"
echo "======================================================================"
echo ""
echo "Created synthetic test images:"
ls -lh real_gt/eval_synthetic/*.tif 2>/dev/null

echo ""
echo "These images represent modern Kurdish news text (Batch 2 corpus)"
echo "They should test whether the model performs better on this style"
echo "vs the traditional dense paragraph style of mgk.tif"
echo ""
