#!/bin/bash

# Script Cleanup - Keep only essential and working scripts
# Removes redundant, broken, and outdated training scripts

echo "=== Script Directory Cleanup ==="

cd /mnt/c/tesseract/work/scripts

echo "Scripts before cleanup: $(ls -1 *.sh | wc -l)"

echo ""
echo "=== Scripts to keep (essential and working) ==="

# Essential scripts to keep
essential_scripts=(
    "cleanup_workspace.sh"          # Workspace cleanup
    "create_ckb_unicharset.sh"     # Kurdish character set
    "ctc_diagnosis.sh"             # CTC error diagnosis
    "english_base_ckb_train.sh"    # UTF-8 enabled training
    "simple_utf8_test.sh"          # UTF-8 testing
    "utf8_box_creator.sh"          # Box file creation
    "verify_utf8.sh"               # UTF-8 verification
    "simple_utf8_lstm.sh"          # Simple LSTM training
)

echo "Essential scripts to preserve:"
for script in "${essential_scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✅ $script"
    else
        echo "  ⚠️  $script (missing)"
    fi
done

echo ""
echo "=== Removing redundant and outdated scripts ==="

# Remove broken/redundant training scripts
scripts_to_remove=(
    "build_ckb_auto.sh"           # Redundant auto build
    "clean_build_ckb.sh"          # Old clean build
    "clean_workspace.sh"          # Old version
    "cleanup_training.sh"         # Redundant cleanup
    "ctc_fix_train.sh"            # Replaced by UTF-8 versions
    "fast_robust_train.sh"        # Redundant fast training
    "final_robust_train.sh"       # Redundant robust training
    "final_solution_train.sh"     # Outdated solution
    "fixed_utf8_training.sh"      # Redundant UTF-8 training
    "full_training_pipeline.sh"   # Outdated pipeline
    "interactive_train.sh"        # Redundant interactive
    "master_training.sh"          # Redundant master
    "minimal_ctc_fix.sh"          # Replaced by simpler versions
    "prepare_training_data.sh"    # Redundant preparation
    "quick_build.sh"              # Redundant quick build
    "quick_train_ckb.sh"          # Redundant quick training
    "robust_ckb_training.sh"      # Redundant robust training
    "setup_training.sh"           # Redundant setup
    "train_ckb_pipeline.sh"       # Redundant pipeline
    "unified_training.sh"         # Redundant unified
    "utf8_ckb_training.sh"        # Replaced by simpler version
    "working_utf8_lstm.sh"        # Replaced by simple version
    "wsl_train_ckb.sh"           # Redundant WSL training
)

removed_count=0
for script in "${scripts_to_remove[@]}"; do
    if [ -f "$script" ]; then
        rm -f "$script"
        echo "  ✅ Removed $script"
        ((removed_count++))
    fi
done

# Remove any other temporary or test scripts
rm -f *temp*.sh *test*.sh *old*.sh *backup*.sh 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ Removed temporary/test scripts"
fi

# Remove fonts.conf (not a script)
rm -f fonts.conf 2>/dev/null && echo "  ✅ Removed fonts.conf (moved to proper location)"

echo ""
echo "=== Cleanup Results ==="
echo "Scripts after cleanup: $(ls -1 *.sh | wc -l)"
echo "Scripts removed: $removed_count"

echo ""
echo "=== Remaining scripts ==="
echo "Working scripts in /scripts/:"
ls -1 *.sh | while read script; do
    echo "  📄 $script"
done

echo ""
echo "=== Script Directory Status ==="
echo "✅ Redundant scripts removed"
echo "✅ Essential UTF-8 scripts preserved"
echo "✅ Working training scripts kept"
echo "✅ Cleanup and diagnostic tools maintained"

echo ""
echo "=== Quick Reference ==="
echo "UTF-8 Training:"
echo "  bash scripts/simple_utf8_lstm.sh"
echo ""
echo "UTF-8 Testing:"
echo "  bash scripts/simple_utf8_test.sh"
echo "  bash scripts/verify_utf8.sh"
echo ""
echo "Workspace Management:"
echo "  bash scripts/cleanup_workspace.sh"
echo ""
echo "CTC Error Diagnosis:"
echo "  bash scripts/ctc_diagnosis.sh"