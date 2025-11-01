#!/bin/bash
# Test Batch 2 model on multiple real Kurdish news images

cd /mnt/c/tesseract/work

echo "======================================================================"
echo "Testing Batch 2 Model on Multiple Real Kurdish News Images"
echo "======================================================================"

echo ""
echo "📷 Step 1: Convert PNGs to TIFFs..."
for png in real_gt/eval_multi/*.png; do
    base=$(basename "$png" .png)
    echo "  Converting ${base}.png → ${base}.tif..."
    convert "$png" "real_gt/eval_multi/${base}.tif" 2>/dev/null
done

echo ""
echo "✅ Converted images:"
ls -lh real_gt/eval_multi/*.tif

echo ""
echo "======================================================================"
echo "🧪 Step 2: Run OCR on Each Test Image (PSM 6)"
echo "======================================================================"

export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Make sure using Batch 2 model
echo 'tishko' | sudo -S cp training_output/model/ckb_from_fas.traineddata \
    /usr/share/tesseract-ocr/5/tessdata/ckb.traineddata 2>/dev/null

total_cer=0
count=0

for tif in real_gt/eval_multi/*.tif; do
    base=$(basename "$tif" .tif)
    echo ""
    echo "--- Testing ${base} ---"
    
    # Run Tesseract
    tesseract "$tif" "output/${base}_batch2" -l ckb --psm 6 2>&1 | grep -v "Warning"
    
    # Calculate CER if ground truth exists
    if [ -f "real_gt/eval_multi/${base}.gt.txt" ]; then
        python3 << PYTHON_SCRIPT
import sys

try:
    with open('real_gt/eval_multi/${base}.gt.txt', 'r', encoding='utf-8') as f:
        gt = f.read().strip()
    with open('output/${base}_batch2.txt', 'r', encoding='utf-8') as f:
        ocr = f.read().strip()
    
    # Simple CER calculation
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, gt, ocr)
    matches = sum(block.size for block in matcher.get_matching_blocks())
    cer = 1 - (matches / len(gt))
    accuracy = (1 - cer) * 100
    
    print(f"  GT:  {len(gt)} chars, {len(gt.split())} words")
    print(f"  OCR: {len(ocr)} chars, {len(ocr.split())} words")
    print(f"  CER: {cer:.4f} ({accuracy:.2f}% accuracy)")
    
    # Write to file for summary
    with open('/tmp/cer_results.txt', 'a') as f:
        f.write(f"{base},{cer:.4f},{accuracy:.2f}\n")
    
except FileNotFoundError as e:
    print(f"  ❌ File not found: {e}")
except Exception as e:
    print(f"  ❌ Error: {e}")
PYTHON_SCRIPT
    else
        echo "  ⚠️  No ground truth file found"
    fi
done

echo ""
echo "======================================================================"
echo "📊 SUMMARY - Batch 2 Model Performance on Real News Images"
echo "======================================================================"

if [ -f /tmp/cer_results.txt ]; then
    python3 << 'PYTHON_SCRIPT'
import statistics

results = []
with open('/tmp/cer_results.txt', 'r') as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) == 3:
                name, cer, acc = parts
                results.append((name, float(cer), float(acc)))

if results:
    print("\n📋 Individual Results:")
    for name, cer, acc in results:
        print(f"  {name:12s}: {acc:6.2f}% accuracy (CER: {cer:.4f})")
    
    accuracies = [acc for _, _, acc in results]
    avg_acc = statistics.mean(accuracies)
    
    print(f"\n📊 Average Accuracy: {avg_acc:.2f}%")
    print(f"   Min: {min(accuracies):.2f}%")
    print(f"   Max: {max(accuracies):.2f}%")
    
    # Compare to mgk.tif baseline
    mgk_acc = 71.69
    diff = avg_acc - mgk_acc
    if diff > 0:
        print(f"\n✅ Model performs {diff:+.2f}% BETTER on news vs mgk.tif!")
    elif diff < -2:
        print(f"\n⚠️  Model performs {diff:+.2f}% WORSE on news vs mgk.tif")
    else:
        print(f"\n➡️  Model performs similarly ({diff:+.2f}%) on news vs mgk.tif")
    
else:
    print("No results to summarize")

PYTHON_SCRIPT

    # Clean up temp file
    rm /tmp/cer_results.txt
else
    echo "No results file created"
fi

echo ""
echo "======================================================================"
echo "✅ Multi-Image Testing Complete"
echo "======================================================================"
