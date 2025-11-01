#!/bin/bash
# Test Batch 2 model on clean test images

cd /mnt/c/tesseract/work

echo "======================================================================"
echo "🧪 Testing Batch 2 Model on Clean Kurdish News Images"
echo "======================================================================"

export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Ensure using Batch 2 model
echo 'tishko' | sudo -S cp training_output/model/ckb_from_fas.traineddata \
    /usr/share/tesseract-ocr/5/tessdata/ckb.traineddata 2>&1 | grep -v "sudo"

echo ""
echo "Testing 4 news article images..."
echo ""

# Clear previous results
rm -f /tmp/multi_test_results.csv

for tif in real_gt/eval_clean/*.tif; do
    base=$(basename "$tif" .tif)
    gt_file="real_gt/eval_clean/${base}.gt.txt"
    
    if [ ! -f "$gt_file" ]; then
        echo "⚠️  Skipping ${base} - no ground truth"
        continue
    fi
    
    echo "--- ${base} ---"
    
    # Run Tesseract with PSM 6
    tesseract "$tif" "output/${base}_clean" -l ckb --psm 6 2>&1 | grep -v "Warning"
    
    # Calculate accuracy using Python
    python3 << PYTHON_SCRIPT
try:
    with open('${gt_file}', 'r', encoding='utf-8') as f:
        gt = f.read().strip()
    with open('output/${base}_clean.txt', 'r', encoding='utf-8') as f:
        ocr = f.read().strip()
    
    # Character-level comparison
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, gt, ocr)
    
    # Calculate character matches
    matches = sum(block.size for block in matcher.get_matching_blocks())
    total = len(gt)
    cer = 1 - (matches / total) if total > 0 else 1.0
    accuracy = (1 - cer) * 100
    
    # Word count
    gt_words = len(gt.split())
    ocr_words = len(ocr.split())
    
    print(f"  GT:  {len(gt):4d} chars, {gt_words:3d} words")
    print(f"  OCR: {len(ocr):4d} chars, {ocr_words:3d} words")
    print(f"  Accuracy: {accuracy:.2f}% (CER: {cer:.4f})")
    
    # Save results
    with open('/tmp/multi_test_results.csv', 'a') as f:
        f.write(f"${base},{accuracy:.2f},{cer:.4f},{len(gt)},{len(ocr)}\n")
    
except Exception as e:
    print(f"  ❌ Error: {e}")
PYTHON_SCRIPT

    echo ""
done

echo "======================================================================"
echo "📊 FINAL RESULTS - Multi-Image Validation"
echo "======================================================================"

python3 << 'PYTHON_SCRIPT'
import statistics

if not __import__('os').path.exists('/tmp/multi_test_results.csv'):
    print("No results found")
    exit()

with open('/tmp/multi_test_results.csv', 'r') as f:
    lines = [l.strip() for l in f if l.strip()]

if not lines:
    print("No results to analyze")
    exit()

results = []
for line in lines:
    parts = line.split(',')
    if len(parts) >= 3:
        name, acc, cer = parts[0], float(parts[1]), float(parts[2])
        results.append((name, acc, cer))

print("\n📋 Individual Test Results:")
print("-" * 70)
for name, acc, cer in results:
    print(f"  {name:15s}: {acc:6.2f}% accuracy  (CER: {cer:.4f})")

if len(results) > 1:
    accuracies = [acc for _, acc, _ in results]
    avg_acc = statistics.mean(accuracies)
    min_acc = min(accuracies)
    max_acc = max(accuracies)
    stdev = statistics.stdev(accuracies) if len(accuracies) > 1 else 0
    
    print(f"\n📊 Summary Statistics:")
    print(f"  Average:  {avg_acc:.2f}% ± {stdev:.2f}%")
    print(f"  Range:    {min_acc:.2f}% - {max_acc:.2f}%")
    print(f"  Count:    {len(results)} test images")
    
    # Compare to mgk.tif baseline
    mgk_baseline = 71.69
    diff = avg_acc - mgk_baseline
    
    print(f"\n🎯 Comparison to mgk.tif baseline ({mgk_baseline}%):")
    if diff > 1.0:
        print(f"  ✅ NEWS IMAGES: {diff:+.2f}% BETTER")
        print(f"     → Model performs BETTER on modern news!")
        print(f"     → mgk.tif is likely an OUTLIER (dense traditional text)")
    elif diff < -1.0:
        print(f"  ⚠️  NEWS IMAGES: {diff:+.2f}% WORSE")
        print(f"     → Model trained better for traditional text")
    else:
        print(f"  ➡️  NEWS IMAGES: {diff:+.2f}% (Similar)")
        print(f"     → Model performs consistently across text types")
    
    # Verdict
    print(f"\n💡 VERDICT:")
    if avg_acc > 75:
        print(f"  ✅ Model is GOOD ({avg_acc:.1f}% average)")
        print(f"     The 71.69% on mgk.tif is due to that specific image")
    elif avg_acc > 70:
        print(f"  ➡️  Model is CONSISTENT (~{avg_acc:.1f}%)")
        print(f"     Performance similar across different text types")
    else:
        print(f"  ⚠️  Model accuracy is LOW ({avg_acc:.1f}%)")
        print(f"     Fundamental training issues need addressing")

PYTHON_SCRIPT

echo ""
echo "======================================================================"
echo "✅ Multi-Image Validation Complete"
echo "======================================================================"
