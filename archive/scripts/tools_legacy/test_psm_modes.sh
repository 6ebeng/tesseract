#!/bin/bash
# Test different PSM modes for Batch 2 model

cd /mnt/c/tesseract/work
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

echo "======================================================================"
echo "Testing Different PSM Modes - Batch 2 Model"
echo "======================================================================"

for psm in 3 4 6 7 11 13; do
    echo ""
    echo "--- Testing PSM $psm ---"
    tesseract real_gt/eval/mgk.tif output/mgk_psm${psm} -l ckb --psm $psm 2>&1 | grep -v "Warning"
    
    # Evaluate
    python3 << 'PYEND'
import re
with open('real_gt/eval/mgk.gt.txt', 'r', encoding='utf-8') as f:
    gt = f.read()
with open('output/mgk_psm${psm}.txt', 'r', encoding='utf-8') as f:
    ocr = f.read()

# Simple character error rate
errors = sum(1 for a, b in zip(gt, ocr) if a != b)
errors += abs(len(gt) - len(ocr))
cer = errors / len(gt)
accuracy = (1 - cer) * 100

print(f"  CER: {cer:.4f} ({accuracy:.2f}% accuracy)")
print(f"  GT length: {len(gt)}, OCR length: {len(ocr)}")
PYEND

done

echo ""
echo "======================================================================"
echo "Summary: Best PSM mode for this image"
echo "======================================================================"
