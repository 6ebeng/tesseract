#!/bin/bash

# Cleanup unnecessary scripts and test files to prepare a clean workspace
set -e

echo "🧹 Cleaning unnecessary files and scripts..."
echo "==========================================="
if [ "${DEEP:-0}" = "1" ]; then
  echo "Mode: DEEP cleanup"
else
  echo "Mode: BASIC cleanup"
fi

ROOT="$(pwd)"

cd "$ROOT"

# Keep lists
KEEP_SCRIPTS=(
  # removed: build_hybrid_ckb_traineddata.sh
  "generate_ckb_training_data.sh"
  # keep the main training script – required by run_training.ps1 and workflow
  "execute_ckb_training.sh"
)

echo "Keeping scripts: ${KEEP_SCRIPTS[*]}"

# Remove unnecessary scripts (OCR wrappers, old trainers, validators)
for file in \
  enhanced_hybrid_ocr.sh \
  hybrid_kurdish_ocr.sh \
  hybrid_solution_summary.sh \
  kurdish_ocr_enhanced.sh \
  kurdish_ocr_final.sh \
  kurdish_ocr_summary.sh \
  kurdish_ocr_ultimate.sh \
  kurdish_persian_ocr.sh \
  ultimate_kurdish_ocr.sh \
  execute_ckb_training_optimized.sh \
  final_ckb_train.sh \
  generate_training_data_simple.sh \
  train_ckb_robust.sh \
  train_kurdish_fixed.sh \
  train_kurdish_simple.sh \
  validate_kurdish_models.sh \
  clean_build_ckb.sh \
  configure_ckb_training.sh; do
  if [ -f "$file" ] && [[ ! " ${KEEP_SCRIPTS[*]} " =~ " $file " ]]; then
    echo "Deleting script: $file"
    rm -f "$file"
  fi
done

# Remove test/output files and folders
echo "Removing test/output files..."
rm -f char_test_*.* || true
rm -f corpus_test.* || true
rm -f enhanced_test.* || true
rm -f enhanced_result*.txt || true
rm -f result_enh_*.txt result_std_*.txt || true
rm -f final_test.* final_result.txt final_enhanced.txt || true
rm -f hybrid_test*.txt hybrid_test_*.* || true
rm -f mixed_test_*.* mixed_result_*.txt || true
rm -f new_result_*.txt || true
rm -f output_ckb.txt output_custom.txt || true
rm -f persian_test.* persian_*_test*.txt persian_result.txt || true
rm -f single_test_*.* single_result_*.txt || true
rm -f ultimate_*.txt || true
rm -f verify_test_*.* || true
rm -f comprehensive_test*.txt || true
rm -f enhanced_test_analysis.txt enhanced_test_arabic.txt enhanced_test_kurdish.txt enhanced_test_persian.txt || true
rm -f hybrid_test_arabic.txt hybrid_test_kurdish.txt hybrid_test_persian.txt || true

# Generic test patterns at workspace root (safe)
find . -maxdepth 1 -type f -name "*test*.tif" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*test*.box" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*test*.txt" -delete 2>/dev/null || true

# Common OCR result .txt patterns at root (do not recurse into GT/corpus)
find . -maxdepth 1 -type f -name "out_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*_ckb.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*_fas.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*_ara.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*_ckb_plus_ara.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*result*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*analysis*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "final_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "enhanced_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "hybrid_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "mixed_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "persian_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "ultimate_*.txt" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "output*.txt" -delete 2>/dev/null || true

# Generated training/test artifacts
find . -maxdepth 1 -type f -name "*.lstmf" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*.tr" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*.unicharset" -delete 2>/dev/null || true
find . -maxdepth 1 -type f -name "*.log" -delete 2>/dev/null || true

# Remove log files (root level)
find . -maxdepth 1 -type f \( -name "*.log" -o -name "*.err" -o -name "*.out" -o -name "nohup.out" \) -delete 2>/dev/null || true

# Remove log files inside common generated directories (if they exist)
for d in training_output hybrid_build validation_out output ocr-test syntax-test final_model enhanced_training ckb_clean_build; do
  if [ -d "$d" ]; then
    find "$d" -type f \( -name "*.log" -o -name "*.err" -o -name "*.out" -o -name "nohup.out" \) -delete 2>/dev/null || true
  fi
done

# Remove test/validation directories
rm -rf hybrid_build || true
rm -rf test_results || true
rm -rf validation_tests || true
rm -rf docs || true
rm -rf validation_out || true
rm -rf scripts || true

# Remove known unnecessary root scripts if present
rm -f validate_hybrid_accuracy.sh || true
rm -f final_training_summary.sh || true

# Deep cleanup removes heavy generated directories
if [ "${DEEP:-0}" = "1" ]; then
  echo "Removing heavy generated directories (DEEP)..."
  # Temporarily disable immediate exit on errors to avoid noisy failures on missing/locked paths
  set +e
  rm -rf training_output 2>/dev/null || true
  rm -rf final_model 2>/dev/null || true
  rm -rf enhanced_training 2>/dev/null || true
  rm -rf ckb_clean_build 2>/dev/null || true
  rm -rf ground-truth-auto 2>/dev/null || true
  rm -rf ground-truth-robust 2>/dev/null || true
  rm -rf ground-truth-corpus 2>/dev/null || true
  rm -rf ground-truth-robust.old.* 2>/dev/null || true
  rm -rf ground-truth-final.old.* 2>/dev/null || true
  rm -rf ground-truth-workaround.old.* 2>/dev/null || true
  rm -rf tessdata_tmp.* 2>/dev/null || true
  # Clean up stray directories with odd suffixes (e.g., training_output\uf00d)
  find . -maxdepth 1 -type d -name 'training_output*' ! -name 'training_output' -exec rm -rf -- {} + 2>/dev/null || true

  # Also remove generic TIFF/BOX in specific generated folders if they exist
  for d in output ocr-test syntax-test; do
    if [ -d "$d" ]; then
      find "$d" -type f \( -name "*.tif" -o -name "*.box" -o -name "*.txt" \) -delete 2>/dev/null || true
    fi
  done
  # Re-enable error exit for the remainder of the script
  set -e
fi

# Remove markdown documentation files in work directory
echo "Removing markdown files..."
find . -maxdepth 1 -type f -name "*.md" -print -exec rm -f {} \; 2>/dev/null || true

echo "✅ Cleanup complete"
exit 0
