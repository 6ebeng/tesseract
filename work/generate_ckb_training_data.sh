#!/bin/bash

# Kurdish Training Data Generation - All Fonts (Improved)
# - Normalizes corpus to Kurdish forms and NFC
# - Generates multiple exposures per font
# - Supports env overrides for corpus/fonts/output and font params
# - Sets fontconfig to prefer local fonts

set -uo pipefail
shopt -s nullglob

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

echo "Kurdish Training Data Generation - Comprehensive"
echo "=============================================="

# Configuration (allow overrides from environment)
LANG_CODE="ckb"
CORPUS_FILE_DEFAULT="corpus/ckb.training_text"
FONTS_DIR_DEFAULT="fonts"
OUTPUT_DIR_DEFAULT="training_output"

CORPUS_FILE="${CORPUS_FILE_OVERRIDE:-$CORPUS_FILE_DEFAULT}"
FONTS_DIR="${FONTS_DIR_OVERRIDE:-$FONTS_DIR_DEFAULT}"
OUTPUT_DIR="${OUTPUT_DIR_OVERRIDE:-$OUTPUT_DIR_DEFAULT}"

GROUND_TRUTH_DIR="$OUTPUT_DIR/ground_truth"
TMP_DIR="$OUTPUT_DIR/tmp"

# Prefer repo fontconfig (root) to ensure local fonts are used; fallback to work/fonts.conf if needed.
# Note: Script charset files (Arabic/Latin/Common) come from tesseract-ocr/langdata (with fallback to langdata_lstm).
if [ -f "/mnt/c/tesseract/fonts.conf" ]; then
    export FONTCONFIG_FILE="/mnt/c/tesseract/fonts.conf"
elif [ -f "$WORK_DIR/fonts.conf" ]; then
    export FONTCONFIG_FILE="$WORK_DIR/fonts.conf"
fi
if [ -n "${FONTCONFIG_FILE:-}" ]; then
    echo "Using FONTCONFIG_FILE=$FONTCONFIG_FILE"
else
    echo "Warning: fonts.conf not found; relying on system fontconfig"
fi

# Create directories
mkdir -p "$GROUND_TRUTH_DIR" "${OUTPUT_DIR}/logs" "$TMP_DIR"

echo ""
echo "📂 Setting up directories:"
echo "Output: $OUTPUT_DIR"
echo "Ground Truth: $GROUND_TRUTH_DIR"

# Font settings for optimal Kurdish recognition (base values; env-overridable)
FONT_SIZE="${FONT_SIZE:-18}"
DPI="${DPI:-300}"
MARGIN="${MARGIN:-15}"
LEADING="${LEADING:-22}"
CHAR_SPACING="${CHAR_SPACING:-1}"
ENABLE_AUG="${ENABLE_AUG:-0}"

# Exposures to render for variety; filenames will use exp0/1/2 (allow EXPOSURES env as comma list)
if [ -n "${EXPOSURES:-}" ]; then
  IFS=',' read -r -a EXPOSURES <<< "$EXPOSURES"
else
  EXPOSURES=(-1 0 1)
fi

echo ""
echo "🎨 Font Generation Settings:"
echo "=========================="
echo "Font Size: ${FONT_SIZE}pt"
echo "DPI: ${DPI}"
echo "Margin: ${MARGIN}px"
echo "Leading: ${LEADING}px"
echo "Char spacing: ${CHAR_SPACING}"
echo "Exposures: ${EXPOSURES[*]}"

# Count available fonts
FONT_COUNT=$(ls "$FONTS_DIR"/*.ttf 2>/dev/null | wc -l)
echo "Available Fonts: $FONT_COUNT"

if [ "$FONT_COUNT" -eq 0 ]; then
    echo "❌ Error: No TTF fonts found in $FONTS_DIR"
    exit 1
fi

echo ""
echo "🚀 Generating training data for all fonts..."
echo "============================================"

# Ensure fontconfig sees local fonts
if command -v fc-cache >/dev/null 2>&1; then
    echo "Refreshing font cache for $FONTS_DIR ..."
    fc-cache -f "$(pwd)/$FONTS_DIR" || true
fi

# Normalize corpus to Kurdish letter forms (best-effort) and NFC
CORPUS_SRC="$CORPUS_FILE"
CORPUS_NORM="$TMP_DIR/ckb.training_text.norm"
CORPUS_NFC="$TMP_DIR/ckb.training_text.norm.nfc"
if command -v python3 >/dev/null 2>&1 && [ -f "kurdish_character_fixer.py" ]; then
  echo "Normalizing corpus with kurdish_character_fixer.py ..."
  if python3 kurdish_character_fixer.py "$CORPUS_FILE" "$CORPUS_NORM" 2>>"${OUTPUT_DIR}/logs/corpus_norm.log"; then
    # NFC normalize to stabilize shaping across fonts
    python3 - "$CORPUS_NORM" "$CORPUS_NFC" << 'PY'
import sys, unicodedata
src, dst = sys.argv[1], sys.argv[2]
with open(src, 'r', encoding='utf-8', errors='ignore') as f:
    txt = f.read()
txt = unicodedata.normalize('NFC', txt)
with open(dst, 'w', encoding='utf-8') as g:
    g.write(txt)
PY
    CORPUS_SRC="$CORPUS_NFC"
  else
    echo "Warning: normalization failed, falling back to original corpus." | tee -a "${OUTPUT_DIR}/logs/corpus_norm.log"
  fi
fi

GENERATED_COUNT=0
ERROR_COUNT=0

# Process each font
while IFS= read -r -d '' font_file; do
    [ -f "$font_file" ] || continue

    font_name=$(basename "$font_file" .ttf)
    echo -n "Processing font: $font_name ... "
    log_file="${OUTPUT_DIR}/logs/${font_name}.log"
    : > "$log_file"

    # Try to resolve the internal family name, style, and fullname using fc-scan if available
    internal_name="$font_name"
    cand_family=""; cand_style=""; cand_fullname=""
    if command -v fc-scan >/dev/null 2>&1; then
        fam=$(fc-scan --format='%{family}\n' "$font_file" 2>>"$log_file" | head -1 || true)
        sty=$(fc-scan --format='%{style}\n'  "$font_file" 2>>"$log_file" | head -1 || true)
        fn=$(fc-scan --format='%{fullname}\n' "$font_file" 2>>"$log_file" | head -1 || true)
        # fc-scan may return comma-separated lists; pick the first token
        [ -n "${fam:-}" ] && cand_family="${fam%%,*}"
        [ -n "${sty:-}" ] && cand_style="${sty%%,*}"
        [ -n "${fn:-}" ] && cand_fullname="${fn%%,*}"
        if [ -n "$cand_family" ]; then internal_name="$cand_family"; fi
    fi

    # Build candidate font names to try with text2image
    declare -a FONT_CANDS
    FONT_CANDS=("$internal_name")
    if [ -n "$cand_family" ] && [ -n "$cand_style" ]; then
        FONT_CANDS+=("$cand_family $cand_style")
    fi
    if [ -n "$cand_fullname" ]; then
        FONT_CANDS+=("$cand_fullname")
    fi
    FONT_CANDS+=("$font_name")

    echo "Trying font candidates: ${FONT_CANDS[*]}" >>"$log_file"

    success=0; used_font=""
    for cand in "${FONT_CANDS[@]}"; do
        echo "text2image --font='$cand' (probe)" >>"$log_file"
        # Probe: render a tiny sample to validate font name
        if text2image \
            --text="$CORPUS_SRC" \
            --outputbase="$GROUND_TRUTH_DIR/.probe_${font_name}" \
            --font="$cand" \
            --fonts_dir="$(pwd)/$FONTS_DIR" \
            --ptsize=$FONT_SIZE \
            --resolution=$DPI \
            --margin=1 \
            --leading=10 \
            --char_spacing=1 \
            --exposure=0 \
            >>"$log_file" 2>&1; then
            success=1; used_font="$cand"; rm -f "$GROUND_TRUTH_DIR/.probe_${font_name}."* 2>/dev/null || true; break
        fi
    done

    if [ "$success" -ne 1 ]; then
        echo "❌ Failed (text2image error)"
        echo "text2image returned non-zero exit code for all candidates. See $log_file" >>"$log_file"
        ((ERROR_COUNT++))
        continue
    fi

    # Generate multiple exposures for the validated font
    exp_idx=0
    ok_this_font=0
    for EXP in "${EXPOSURES[@]}"; do
        output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}"
                if text2image \
            --text="$CORPUS_SRC" \
            --outputbase="$output_base" \
            --font="$used_font" \
            --fonts_dir="$(pwd)/$FONTS_DIR" \
            --ptsize=$FONT_SIZE \
            --resolution=$DPI \
            --margin=$MARGIN \
            --leading=$LEADING \
                        --char_spacing=$CHAR_SPACING \
            --exposure="$EXP" \
            >>"$log_file" 2>&1; then
            if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                cp "$CORPUS_SRC" "${output_base}.gt.txt"
                                # Optional simple augmentation via ImageMagick
                                if [ "$ENABLE_AUG" = "1" ] && command -v convert >/dev/null 2>&1; then
                                    aug_base="${output_base}.aug"
                                    convert "${output_base}.tif" -colorspace Gray -contrast-stretch 1%x1% -blur 0x0.5 -attenuate 0.02 +noise Gaussian "${aug_base}.tif" 2>>"$log_file" || true
                                    if [ -f "${aug_base}.tif" ]; then
                                        # Duplicate gt for augmented image; box reused is not ideal but acceptable for small perturbations
                                        cp "${output_base}.box" "${aug_base}.box" 2>/dev/null || true
                                        cp "${output_base}.gt.txt" "${aug_base}.gt.txt" 2>/dev/null || true
                                    fi
                                fi
                ok_this_font=1
            fi
        fi
        exp_idx=$((exp_idx+1))
    done

    if [ "$ok_this_font" -eq 1 ]; then
        echo "✅ Success"
        ((GENERATED_COUNT++))
    else
        echo "❌ Failed (missing files)"
        echo "Output files missing after text2image exposures. See $log_file" >>"$log_file"
        ((ERROR_COUNT++))
    fi

done < <(find "$FONTS_DIR" -maxdepth 1 -type f -name "*.ttf" -print0)

echo ""
echo "📊 Generation Summary:"
echo "===================="
echo "Successfully generated (fonts with at least one exposure): $GENERATED_COUNT"
echo "Failed: $ERROR_COUNT fonts"
echo "Total processed: $FONT_COUNT fonts"

if [ "$GENERATED_COUNT" -eq 0 ]; then
    echo ""
    echo "❌ No training data generated! Checking common issues..."
    # Check if text2image is available
    if ! command -v text2image &> /dev/null; then
        echo "   - text2image command not found"
        echo "   - Install: sudo apt-get install tesseract-ocr-dev"
    fi
    # Check corpus file
    if [ ! -f "$CORPUS_FILE" ]; then
        echo "   - Corpus file missing: $CORPUS_FILE"
    fi
    # Check fonts directory
    if [ ! -d "$FONTS_DIR" ]; then
        echo "   - Fonts directory missing: $FONTS_DIR"
    else
        if command -v fc-list >/dev/null 2>&1; then
            echo "   - Fontconfig families visible for our fonts directory:"
            fc-list | grep -i -E "$(echo "$FONTS_DIR" | sed 's/[\\/]/./g')" | head -5 || true
        fi
    fi
    exit 1
fi

echo ""
echo "🔍 Verifying generated data..."
echo "============================="

# List generated files
TIF_COUNT=$(ls "$GROUND_TRUTH_DIR"/*.tif 2>/dev/null | wc -l)
BOX_COUNT=$(ls "$GROUND_TRUTH_DIR"/*.box 2>/dev/null | wc -l)
GT_COUNT=$(ls "$GROUND_TRUTH_DIR"/*.gt.txt 2>/dev/null | wc -l)

echo "Generated .tif files: $TIF_COUNT"
echo "Generated .box files: $BOX_COUNT"
echo "Generated .gt.txt files: $GT_COUNT"

if [ "$TIF_COUNT" -gt 0 ] && [ "$BOX_COUNT" -gt 0 ]; then
    echo ""
    echo "✅ Training data generation successful!"
    echo "   Ready for model training"
    echo ""
    echo "📝 Sample generated files:"
    ls "$GROUND_TRUTH_DIR"/*.tif | head -3
    echo ""
    echo "📏 File size verification:"
    for sample_file in $(ls "$GROUND_TRUTH_DIR"/*.tif | head -3); do
        size=$(stat -c%s "$sample_file")
        echo "   $(basename "$sample_file"): ${size} bytes"
    done
else
    echo ""
    echo "❌ Training data generation incomplete!"
    echo "   Missing required files for training"
    exit 1
fi

echo ""
echo "✅ Next Step: Run ./execute_ckb_training.sh to start model training"