#!/bin/bash

# Cleanup Script - Remove test files and unnecessary outputs
# Keeps only essential files for Kurdish OCR training

# Enable UTF-8 support
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

echo "=== Kurdish Training Workspace Cleanup ==="

cd /mnt/c/tesseract/work

echo "=== Current workspace status ==="
echo "Output files: $(ls -1 output/ | wc -l)"
echo "Total size: $(du -sh output/ | cut -f1)"

echo ""
echo "=== Files to keep (essential) ==="
# List essential files to preserve
essential_files=(
    "ckb.unicharset"
    "ckb_base.lstm"
    "ckb_base.lstm-unicharset" 
    "ckb_base.lstm-recoder"
    "training_files.txt"
)

echo "Essential training files:"
cd output
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file ($(ls -lh $file | awk '{print $5}'))"
    fi
done

echo ""
echo "=== Removing test files ==="

# Remove all test files
rm -f *test* 2>/dev/null && echo "  ✅ Removed test files" || echo "  ℹ️  No test files found"

# Remove temporary files
rm -f *tmp* *temp* 2>/dev/null && echo "  ✅ Removed temporary files" || echo "  ℹ️  No temporary files found"

# Remove experimental training files (exp0-exp4)
rm -f ckb.exp*.* 2>/dev/null && echo "  ✅ Removed experimental files (exp0-exp4)" || echo "  ℹ️  No experimental files found"

# Remove redundant training attempts
rm -f ckb.ara.* 2>/dev/null && echo "  ✅ Removed Arabic base attempts" || echo "  ℹ️  No Arabic base files found"
rm -f ckb.final.* 2>/dev/null && echo "  ✅ Removed final training attempts" || echo "  ℹ️  No final training files found"
rm -f ckb.enhanced.* 2>/dev/null && echo "  ✅ Removed enhanced training attempts" || echo "  ℹ️  No enhanced files found"

# Remove Sarchia experiment files
rm -f ckb.sarchia.* 2>/dev/null && echo "  ✅ Removed Sarchia experiments" || echo "  ℹ️  No Sarchia files found"

# Remove UTF-8 test files
rm -f ckb.utf8.* utf8_*.* 2>/dev/null && echo "  ✅ Removed UTF-8 test files" || echo "  ℹ️  No UTF-8 test files found"

# Remove simple test files
rm -f ckb.simple.* ckb.fixed.* ckb.minimal.* 2>/dev/null && echo "  ✅ Removed simple test files" || echo "  ℹ️  No simple test files found"

# Remove LSTM test files
rm -f ckb.lstm.* 2>/dev/null && echo "  ✅ Removed LSTM test files" || echo "  ℹ️  No LSTM test files found"

# Remove misc files
rm -f all.txt ckb.charset 2>/dev/null && echo "  ✅ Removed miscellaneous files" || echo "  ℹ️  No misc files found"

echo ""
echo "=== Cleaning up corpus directory ==="
cd /mnt/c/tesseract/work

# Remove test corpus files
rm -f corpus/ckb.minimal.txt corpus/ckb.simple*.txt corpus/ckb.lstm_train.txt 2>/dev/null && echo "  ✅ Removed test corpus files" || echo "  ℹ️  No test corpus files found"

echo ""
echo "=== Cleanup complete ==="
cd output
echo "Remaining files: $(ls -1 | wc -l)"
echo "New size: $(du -sh . | cut -f1)"

echo ""
echo "=== Remaining files summary ==="
if [ $(ls -1 | wc -l) -gt 0 ]; then
    echo "Essential files kept:"
    ls -lh | head -10
    if [ $(ls -1 | wc -l) -gt 10 ]; then
        echo "... and $(($(ls -1 | wc -l) - 10)) more files"
    fi
else
    echo "Output directory is now clean"
fi

echo ""
echo "=== Workspace Status ==="
echo "✅ Test files removed"
echo "✅ Experimental files cleaned"
echo "✅ Temporary files removed"
echo "✅ Essential training files preserved"
echo ""
echo "Your working CKB models remain at:"
echo "  📁 /mnt/c/tesseract/tessdata/ckb.traineddata (15MB)"
echo "  📁 /mnt/c/tesseract/tessdata/ckb_custom.traineddata (15MB)"