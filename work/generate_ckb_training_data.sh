#!/bin/bash

# Kurdish Training Data Generation - All Fonts (Improved)
# - Normalizes corpus to Kurdish forms and NFC
# - Generates multiple exposures per font
# - Supports env overrides for corpus/fonts/output and font params
# - Sets fontconfig to prefer local fonts
# - Supports parallel processing with PARALLEL_JOBS env variable

set -uo pipefail
shopt -s nullglob

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Parallel processing support (set PARALLEL_JOBS=0 to disable, or number of jobs)
PARALLEL_JOBS="${PARALLEL_JOBS:-0}"
if [ "$PARALLEL_JOBS" -gt 0 ] && ! command -v parallel >/dev/null 2>&1; then
    echo "⚠️  GNU Parallel not found. Install with: sudo apt-get install parallel"
    echo "Falling back to sequential processing..."
    PARALLEL_JOBS=0
fi

echo "Kurdish Training Data Generation - Comprehensive"
echo "=============================================="
if [ "$PARALLEL_JOBS" -gt 0 ]; then
    echo "🚀 PARALLEL MODE: Using $PARALLEL_JOBS worker jobs"
else
    echo "🐌 Sequential processing (set PARALLEL_JOBS=<num> for parallel)"
fi
echo ""

# Configuration (allow overrides from environment)
LANG_CODE="ckb"
CORPUS_FILE_DEFAULT="corpus/ckb.training_text"
# Optional Latin-based Kurdish corpus for mixed-script exposure
LATIN_CORPUS_DEFAULT="corpus/ckb_latin.training_text"
# Optional mixed-script corpus (Arabic + Latin in the same line)
MIXED_CORPUS_DEFAULT="corpus/ckb_mixed.training_text"
FONTS_DIR_DEFAULT="fonts"
OUTPUT_DIR_DEFAULT="training_output"

CORPUS_FILE="${CORPUS_FILE_OVERRIDE:-$CORPUS_FILE_DEFAULT}"
FONTS_DIR="${FONTS_DIR_OVERRIDE:-$FONTS_DIR_DEFAULT}"
OUTPUT_DIR="${OUTPUT_DIR_OVERRIDE:-$OUTPUT_DIR_DEFAULT}"
LATIN_CORPUS_FILE="$LATIN_CORPUS_DEFAULT"
MIXED_CORPUS_FILE="$MIXED_CORPUS_DEFAULT"

# Allow custom ground-truth directory override (if not set, use OUTPUT_DIR/ground_truth)
GROUND_TRUTH_DIR="${GROUND_TRUTH_DIR:-$OUTPUT_DIR/ground_truth}"
TMP_DIR="$OUTPUT_DIR/tmp"

# Prefer repo fontconfig (root) to ensure local fonts are used; fallback to work/fonts.conf if needed.
# Note: Script charset files (Arabic/Latin/Common) come from tesseract-ocr/langdata (with fallback to langdata_lstm).
if [ -f "/mnt/c/tesseract/fonts.conf" ]; then
    export FONTCONFIG_FILE="/mnt/c/tesseract/fonts.conf"
elif [ -f "./fonts.conf" ]; then
    # When running from work/, prefer the local fonts.conf
    export FONTCONFIG_FILE="$(pwd)/fonts.conf"
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
FONT_SIZE="${FONT_SIZE:-16}"
# Default DPI lowered for faster generation; DPI_LIST provides diversity when set
DPI="${DPI:-200}"
MARGIN="${MARGIN:-15}"
LEADING="${LEADING:-22}"
# Default char spacing (used if CHAR_SPACING_LIST not set)
CHAR_SPACING="${CHAR_SPACING:-0.8}"
# Enable augmentation by default for robustness, but allow override via ENABLE_AUG=0
ENABLE_AUG="${ENABLE_AUG:-1}"
# Optimized parameter lists (keep compact but diverse)
# - FONT_SIZE_LIST: two values (small, medium-large)
# - DPI_LIST: two values (low, high)
# - CHAR_SPACING_LIST: tighter and looser spacing
FONT_SIZE_LIST="${FONT_SIZE_LIST:-16,20}"
DPI_LIST="${DPI_LIST:-200,400}"
LEADING_LIST="${LEADING_LIST:-22,26}"
CHAR_SPACING_LIST="${CHAR_SPACING_LIST:-0.8,1.2}"
# Keep augmentation variants small to reduce runtime but keep utility
AUG_VARIANTS="${AUG_VARIANTS:-2}"

# Exposures to render for variety; filenames will use exp0/1/2 (allow EXPOSURES env as comma list)
if [ -n "${EXPOSURES:-}" ]; then
  IFS=',' read -r -a EXPOSURES <<< "$EXPOSURES"
else
  EXPOSURES=(-1 0 1)
fi

echo ""
echo "🎨 Font Generation Settings:"
echo "=========================="
echo "Font Size: ${FONT_SIZE}pt${FONT_SIZE_LIST:+ (list: $FONT_SIZE_LIST)}"
echo "DPI: ${DPI}${DPI_LIST:+ (list: $DPI_LIST)}"
echo "Margin: ${MARGIN}px"
echo "Leading: ${LEADING}px${LEADING_LIST:+ (list: $LEADING_LIST)}"
echo "Char spacing: ${CHAR_SPACING}${CHAR_SPACING_LIST:+ (list: $CHAR_SPACING_LIST)}"
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
    echo "Refreshing font cache (system + repo fonts) ..."
    fc-cache -f || true
fi

# Build a combined Arabic-script corpus from available pieces, then normalize
# Prefer a final built corpus if present
BASE_CKB="$CORPUS_FILE"
if [ -f "corpus/ckb.training_text.final" ]; then BASE_CKB="corpus/ckb.training_text.final"; fi
COMBINED_CKB="$TMP_DIR/ckb.corpus_combined.txt"
{
    [ -f "$BASE_CKB" ] && cat "$BASE_CKB" || true
    # Pull in curated coverage and extra sentences if present
    [ -f "corpus/ckb_core_coverage.txt" ] && cat "corpus/ckb_core_coverage.txt" || true
    [ -f "corpus/ckb_extra_sentences.txt" ] && cat "corpus/ckb_extra_sentences.txt" || true
    [ -f "corpus/ckb_formats_ner.txt" ] && cat "corpus/ckb_formats_ner.txt" || true
    # Shaping augment is small but helpful
    [ -f "corpus/shaping_augment.txt" ] && cat "corpus/shaping_augment.txt" || true
} > "$COMBINED_CKB"

# Normalize corpus to Kurdish letter forms (best-effort) and NFC
CORPUS_SRC="$COMBINED_CKB"
CORPUS_NORM="$TMP_DIR/ckb.training_text.norm"
CORPUS_NFC="$TMP_DIR/ckb.training_text.norm.nfc"
if command -v python3 >/dev/null 2>&1 && [ -f "kurdish_character_fixer.py" ]; then
  echo "Normalizing corpus with kurdish_character_fixer.py ..."
    if python3 kurdish_character_fixer.py "$CORPUS_SRC" "$CORPUS_NORM" 2>>"${OUTPUT_DIR}/logs/corpus_norm.log"; then
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

# Build a combined Latin-script corpus if present, then NFC it
LATIN_SRC="$LATIN_CORPUS_FILE"
LATIN_NFC="$TMP_DIR/ckb_latin.training_text.nfc"
if [ -f "$LATIN_CORPUS_FILE" ]; then
    LATIN_COMBINED="$TMP_DIR/ckb_latin.corpus_combined.txt"
    {
        [ -f "$LATIN_CORPUS_FILE" ] && cat "$LATIN_CORPUS_FILE" || true
        [ -f "corpus/ckb_latin_core_coverage.txt" ] && cat "corpus/ckb_latin_core_coverage.txt" || true
        [ -f "corpus/ckb_latin_extra_sentences.txt" ] && cat "corpus/ckb_latin_extra_sentences.txt" || true
        [ -f "corpus/ckb_latin_formats_ner.txt" ] && cat "corpus/ckb_latin_formats_ner.txt" || true
    } > "$LATIN_COMBINED"
    if command -v python3 >/dev/null 2>&1; then
        python3 - "$LATIN_COMBINED" "$LATIN_NFC" << 'PY'
import sys, unicodedata
src, dst = sys.argv[1], sys.argv[2]
with open(src, 'r', encoding='utf-8', errors='ignore') as f:
        txt = f.read()
txt = unicodedata.normalize('NFC', txt)
with open(dst, 'w', encoding='utf-8') as g:
        g.write(txt)
PY
        LATIN_SRC="$LATIN_NFC"
    fi
fi

# Normalize optional mixed-script corpus (if present)
MIXED_SRC="$MIXED_CORPUS_FILE"
MIXED_NFC="$TMP_DIR/ckb_mixed.training_text.nfc"
if [ -f "$MIXED_CORPUS_FILE" ]; then
    if command -v python3 >/dev/null 2>&1; then
        python3 - "$MIXED_CORPUS_FILE" "$MIXED_NFC" << 'PY'
import sys, unicodedata
src, dst = sys.argv[1], sys.argv[2]
with open(src, 'r', encoding='utf-8', errors='ignore') as f:
    txt = f.read()
txt = unicodedata.normalize('NFC', txt)
with open(dst, 'w', encoding='utf-8') as g:
    g.write(txt)
PY
        MIXED_SRC="$MIXED_NFC"
    fi
fi

# Optionally split corpus into multiple pages to increase training diversity
MAX_PAGES="${MAX_PAGES:-1}"
CHARS_PER_PAGE="${CHARS_PER_PAGE:-3000}"
PAGE_LIST=()
PAGES_DIR="$TMP_DIR/pages"
mkdir -p "$PAGES_DIR"
if [ "$MAX_PAGES" -gt 1 ]; then
    python3 - "$CORPUS_SRC" "$PAGES_DIR" "$MAX_PAGES" "$CHARS_PER_PAGE" << 'PY'
import sys, os
src, outdir, max_pages, chars_per = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
with open(src, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
tokens = text.split()
pages = []
curr = []
count = 0
for tok in tokens:
        if count + len(tok) + (1 if count else 0) > chars_per and pages and len(pages) < max_pages:
                pages.append(' '.join(curr))
                curr = [tok]
                count = len(tok)
        else:
                if count:
                        curr.append(tok)
                        count += 1 + len(tok)
                else:
                        curr = [tok]
                        count = len(tok)
if curr:
        pages.append(' '.join(curr))
pages = pages[:max_pages]
os.makedirs(outdir, exist_ok=True)
for i, p in enumerate(pages):
        with open(os.path.join(outdir, f'page_{i:03d}.txt'), 'w', encoding='utf-8') as g:
                g.write(p)
print(len(pages))
PY
    # Build PAGE_LIST in bash
    while IFS= read -r -d '' pf; do PAGE_LIST+=("$pf"); done < <(find "$PAGES_DIR" -maxdepth 1 -type f -name 'page_*.txt' -print0 | sort -z)
    echo "Using corpus split into ${#PAGE_LIST[@]} pages (MAX_PAGES=$MAX_PAGES, CHARS_PER_PAGE=$CHARS_PER_PAGE)"
fi

GENERATED_COUNT=0
ERROR_COUNT=0

# Helper to iterate a list env or fallback to single value
iter_or_single() {
    local list="$1"; local single="$2"
    if [ -n "$list" ]; then echo "$list" | tr ',' ' '; else echo "$single"; fi
}

# Function to generate a single training image (used in parallel mode)
generate_single_image() {
    local font_file="$1"
    local used_font="$2"
    local exp_idx="$3"
    local THIS_DPI="$4"
    local THIS_PTSIZE="$5"
    local THIS_LEADING="$6"
    local THIS_CHSP="$7"
    local EXP="$8"
    local page_file="${9:-}"
    local page_i="${10:-0}"
    
    local font_name=$(basename "$font_file" .ttf)
    local log_file="${OUTPUT_DIR}/logs/${font_name}.log"
    
    # Build output base name
    if [ -n "$page_file" ]; then
        output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}.p${page_i}.d${THIS_DPI}.s${THIS_PTSIZE}.l${THIS_LEADING}.c${THIS_CHSP}"
        text_src="$page_file"
    else
        output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}.d${THIS_DPI}.s${THIS_PTSIZE}.l${THIS_LEADING}.c${THIS_CHSP}"
        text_src="$CORPUS_SRC"
    fi
    
    # Skip if already generated (resumability)
    if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
        return 0
    fi
    
    # Generate base image
    if text2image \
        --text="$text_src" \
        --outputbase="$output_base" \
        --font="$used_font" \
        --fonts_dir="$(pwd)/$FONTS_DIR" \
        --ptsize=$THIS_PTSIZE \
        --resolution=$THIS_DPI \
        --margin=$MARGIN \
        --leading=$THIS_LEADING \
        --char_spacing=$THIS_CHSP \
        --exposure="$EXP" \
        >>"$log_file" 2>&1; then
        
        if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
            cp "$text_src" "${output_base}.gt.txt" 2>/dev/null || true
            
            # Apply augmentation if enabled
            if [ "$ENABLE_AUG" = "1" ] && command -v convert >/dev/null 2>&1; then
                for k in $(seq 1 "$AUG_VARIANTS"); do
                    aug_base="${output_base}.aug${k}"
                    
                    # Skip if augmented file exists
                    [ -f "${aug_base}.tif" ] && continue
                    
                    case $k in
                        1) convert "${output_base}.tif" -colorspace Gray \
                            \( +clone -contrast-stretch 1%x1% -attenuate 0.02 +noise Gaussian -blur 0x0.4 \) \
                            -compose over -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                        2) convert "${output_base}.tif" -colorspace Gray -quality 85 "${aug_base}.jpg" 2>>"$log_file" || true
                            if [ -f "${aug_base}.jpg" ]; then convert "${aug_base}.jpg" "${aug_base}.tif" 2>>"$log_file" || true; fi ;;
                        3) convert "${output_base}.tif" -colorspace Gray -ordered-dither o8x8 -blur 0x0.3 "${aug_base}.tif" 2>>"$log_file" || true ;;
                        4) convert "${output_base}.tif" -colorspace Gray \( -size 2000x2000 xc:white -attenuate 0.02 +noise Multiplicative -colorspace Gray -resize "@" \) \
                            -compose multiply -composite -contrast-stretch 2%x2% "${aug_base}.tif" 2>>"$log_file" || true ;;
                        5) convert "${output_base}.tif" -colorspace Gray \( +clone -radial-blur 0.2 \) -compose overlay -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                        *) convert "${output_base}.tif" -colorspace Gray -attenuate 0.01 +noise Gaussian "${aug_base}.tif" 2>>"$log_file" || true ;;
                    esac
                    
                    if [ -f "${aug_base}.tif" ]; then
                        cp "${output_base}.box" "${aug_base}.box" 2>/dev/null || true
                        cp "${output_base}.gt.txt" "${aug_base}.gt.txt" 2>/dev/null || true
                    fi
                done
            fi
            return 0
        fi
    fi
    return 1
}

export -f generate_single_image

# Helper to iterate a list env or fallback to single value (keep original for backward compat)
iter_or_single_original() {
    local list="$1"; local single="$2"
    if [ -n "$list" ]; then echo "$list" | tr ',' ' '; else echo "$single"; fi
}

# ============================================
# PARALLEL MODE: Process fonts in parallel
# ============================================
if [ "$PARALLEL_JOBS" -gt 0 ]; then
    echo ""
    echo "🚀 Starting parallel font processing with $PARALLEL_JOBS workers..."
    echo "============================================"
    
    # Export all variables needed by parallel workers
    export WORK_DIR OUTPUT_DIR GROUND_TRUTH_DIR FONTS_DIR CORPUS_SRC
    export FONT_SIZE_LIST DPI_LIST LEADING_LIST CHAR_SPACING_LIST MARGIN
    export EXPOSURES ENABLE_AUG AUG_VARIANTS
    
    # Build font list
    FONT_LIST=()
    while IFS= read -r -d '' font_file; do
        [ -f "$font_file" ] && FONT_LIST+=("$font_file")
    done < <(find "$FONTS_DIR" -maxdepth 1 -name '*.ttf' -print0 2>/dev/null || true)
    
    TOTAL_FONTS=${#FONT_LIST[@]}
    echo "Processing $TOTAL_FONTS fonts with $PARALLEL_JOBS parallel workers..."
    echo ""
    
    # Process fonts in parallel using GNU parallel
    # --ungroup: show output immediately (live progress bars)
    # -j: number of parallel jobs
    font_idx=0
    for font_file in "${FONT_LIST[@]}"; do
        ((font_idx++))
        printf "%s\t%d\t%d\n" "$font_file" "$font_idx" "$TOTAL_FONTS"
    done | parallel -j "$PARALLEL_JOBS" --ungroup --colsep '\t' \
        "bash $(pwd)/parallel_font_processor.sh {1} {2} {3}"
    
    echo ""
    echo "✅ Parallel processing completed!"
    echo ""
    
    # Count successful generations
    SUCCESS_COUNT=$(find "$GROUND_TRUTH_DIR" -name "*.tif" -type f 2>/dev/null | wc -l)
    ERROR_COUNT=$((TOTAL_FONTS - SUCCESS_COUNT / 1000))  # Rough estimate
    
    # Skip sequential processing
    exit 0
fi

# ============================================
# SEQUENTIAL MODE: Process fonts one by one
# ============================================
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
    # Common fallbacks to improve resolution on mixed environments
    # Fallbacks limited to Arabic-supporting families to avoid encoding failures
    FONT_CANDS+=("Noto Naskh Arabic" "Noto Naskh Arabic Medium")

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

    # Generate multiple exposures for the validated font across param lists
    exp_idx=0
    ok_this_font=0
    for EXP in "${EXPOSURES[@]}"; do
      for THIS_DPI in $(iter_or_single "$DPI_LIST" "$DPI"); do
        for THIS_PTSIZE in $(iter_or_single "$FONT_SIZE_LIST" "$FONT_SIZE"); do
          for THIS_LEADING in $(iter_or_single "$LEADING_LIST" "$LEADING"); do
            for THIS_CHSP in $(iter_or_single "$CHAR_SPACING_LIST" "$CHAR_SPACING"); do
        # Choose texts: either split pages or the whole corpus
        if [ "${#PAGE_LIST[@]}" -gt 0 ]; then
            page_i=0
            for page_file in "${PAGE_LIST[@]}"; do
                output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}.p${page_i}.d${THIS_DPI}.s${THIS_PTSIZE}.l${THIS_LEADING}.c${THIS_CHSP}"
                
                # Skip if already generated (resumability)
                if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                    page_i=$((page_i+1))
                    continue
                fi
                
                if text2image \
            --text="$page_file" \
            --outputbase="$output_base" \
            --font="$used_font" \
            --fonts_dir="$(pwd)/$FONTS_DIR" \
            --ptsize=$THIS_PTSIZE \
            --resolution=$THIS_DPI \
            --margin=$MARGIN \
            --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
            --exposure="$EXP" \
            >>"$log_file" 2>&1; then
            if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                cp "$page_file" "${output_base}.gt.txt"
                # Optionally render a Latin page alongside for mixed-script robustness
                if [ -f "$LATIN_SRC" ]; then
                    latin_base="${output_base}.latin"
                    text2image \
                        --text="$LATIN_SRC" \
                        --outputbase="$latin_base" \
                        --font="$used_font" \
                        --ptsize=$THIS_PTSIZE \
                        --resolution=$THIS_DPI \
                        --margin=$MARGIN \
                        --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
                        --exposure="$EXP" \
                        >>"$log_file" 2>&1 || true
                    if [ -f "${latin_base}.tif" ] && [ -f "${latin_base}.box" ]; then
                        cp "$LATIN_SRC" "${latin_base}.gt.txt" 2>/dev/null || true
                    else
                        # Retry with Latin-capable fallback fonts
                        for lf in "Noto Sans" "DejaVu Sans" "Liberation Sans"; do
                            text2image \
                                --text="$LATIN_SRC" \
                                --outputbase="$latin_base" \
                                --font="$lf" \
                                --ptsize=$THIS_PTSIZE \
                                --resolution=$THIS_DPI \
                                --margin=$MARGIN \
                                --leading=$THIS_LEADING \
                                --char_spacing=$THIS_CHSP \
                                --exposure="$EXP" \
                                >>"$log_file" 2>&1 || true
                            if [ -f "${latin_base}.tif" ] && [ -f "${latin_base}.box" ]; then
                                cp "$LATIN_SRC" "${latin_base}.gt.txt" 2>/dev/null || true
                                break
                            fi
                        done
                    fi
                fi
                # Optionally render mixed-script page (Arabic+Latin in same lines)
                if [ -f "$MIXED_SRC" ]; then
                    mixed_base="${output_base}.mixed"
                    text2image \
                        --text="$MIXED_SRC" \
                        --outputbase="$mixed_base" \
                        --font="$used_font" \
                        --ptsize=$THIS_PTSIZE \
                        --resolution=$THIS_DPI \
                        --margin=$MARGIN \
                        --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
                        --exposure="$EXP" \
                        >>"$log_file" 2>&1 || true
                    if [ -f "${mixed_base}.tif" ] && [ -f "${mixed_base}.box" ]; then
                        cp "$MIXED_SRC" "${mixed_base}.gt.txt" 2>/dev/null || true
                    else
                        # Retry mixed with an Arabic font plus Latin fallback family
                        for lf in "Noto Sans" "DejaVu Sans" "Liberation Sans"; do
                            text2image \
                                --text="$MIXED_SRC" \
                                --outputbase="$mixed_base" \
                                --font="$lf" \
                                --ptsize=$THIS_PTSIZE \
                                --resolution=$THIS_DPI \
                                --margin=$MARGIN \
                                --leading=$THIS_LEADING \
                                --char_spacing=$THIS_CHSP \
                                --exposure="$EXP" \
                                >>"$log_file" 2>&1 || true
                            if [ -f "${mixed_base}.tif" ] && [ -f "${mixed_base}.box" ]; then
                                cp "$MIXED_SRC" "${mixed_base}.gt.txt" 2>/dev/null || true
                                break
                            fi
                        done
                    fi
                fi
                                # Optional multi-variant photometric augmentation (box-safe)
                                                                if [ "$ENABLE_AUG" = "1" ] && command -v convert >/dev/null 2>&1; then
                                                                        for k in $(seq 1 "$AUG_VARIANTS"); do
                                                                                aug_base="${output_base}.aug${k}"
                                                                                case $k in
                                                                                    1)
                                                                                        # Gaussian noise + light blur (baseline)
                                                                                        convert "${output_base}.tif" -colorspace Gray \
                                                                                            \( +clone -contrast-stretch 1%x1% -attenuate 0.02 +noise Gaussian -blur 0x0.4 \) \
                                                                                            -compose over -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    2)
                                                                                        # JPEG-like artifacts
                                                                                        convert "${output_base}.tif" -colorspace Gray -quality 85 "${aug_base}.jpg" 2>>"$log_file" || true
                                                                                        if [ -f "${aug_base}.jpg" ]; then convert "${aug_base}.jpg" "${aug_base}.tif" 2>>"$log_file" || true; fi ;;
                                                                                    3)
                                                                                        # Halftone/dot pattern subtle
                                                                                        convert "${output_base}.tif" -colorspace Gray -ordered-dither o8x8 -blur 0x0.3 "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    4)
                                                                                        # Paper texture overlay (noise + grain)
                                                                                        convert "${output_base}.tif" -colorspace Gray \( -size 2000x2000 xc:white -attenuate 0.02 +noise Multiplicative -colorspace Gray -resize "@" \) \
                                                                                            -compose multiply -composite -contrast-stretch 2%x2% "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    5)
                                                                                        # Mild uneven illumination (vignette-ish)
                                                                                        convert "${output_base}.tif" -colorspace Gray \( +clone -radial-blur 0.2 \) -compose overlay -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    *)
                                                                                        convert "${output_base}.tif" -colorspace Gray -attenuate 0.01 +noise Gaussian "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                esac
                                                                                if [ -f "${aug_base}.tif" ]; then
                                                                                        cp "${output_base}.box" "${aug_base}.box" 2>/dev/null || true
                                                                                        cp "${output_base}.gt.txt" "${aug_base}.gt.txt" 2>/dev/null || true
                                                                                fi
                                                                        done
                                                                fi
                ok_this_font=1
            fi
            fi
                page_i=$((page_i+1))
            done
        else
            output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}.d${THIS_DPI}.s${THIS_PTSIZE}.l${THIS_LEADING}.c${THIS_CHSP}"
            
            # Skip if already generated (resumability)
            if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                ok_this_font=1
                exp_idx=$((exp_idx+1))
                continue
            fi
            
            if text2image \
            --text="$CORPUS_SRC" \
            --outputbase="$output_base" \
            --font="$used_font" \
            --fonts_dir="$(pwd)/$FONTS_DIR" \
            --ptsize=$THIS_PTSIZE \
            --resolution=$THIS_DPI \
            --margin=$MARGIN \
            --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
            --exposure="$EXP" \
            >>"$log_file" 2>&1; then
            if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                cp "$CORPUS_SRC" "${output_base}.gt.txt"
                if [ -f "$LATIN_SRC" ]; then
                    latin_base="${output_base}.latin"
                    text2image \
                        --text="$LATIN_SRC" \
                        --outputbase="$latin_base" \
                        --font="$used_font" \
                        --ptsize=$THIS_PTSIZE \
                        --resolution=$THIS_DPI \
                        --margin=$MARGIN \
                        --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
                        --exposure="$EXP" \
                        >>"$log_file" 2>&1 || true
                    if [ -f "${latin_base}.tif" ] && [ -f "${latin_base}.box" ]; then
                        cp "$LATIN_SRC" "${latin_base}.gt.txt" 2>/dev/null || true
                    else
                        for lf in "Noto Sans" "DejaVu Sans" "Liberation Sans"; do
                            text2image \
                                --text="$LATIN_SRC" \
                                --outputbase="$latin_base" \
                                --font="$lf" \
                                --ptsize=$THIS_PTSIZE \
                                --resolution=$THIS_DPI \
                                --margin=$MARGIN \
                                --leading=$THIS_LEADING \
                                --char_spacing=$THIS_CHSP \
                                --exposure="$EXP" \
                                >>"$log_file" 2>&1 || true
                            if [ -f "${latin_base}.tif" ] && [ -f "${latin_base}.box" ]; then
                                cp "$LATIN_SRC" "${latin_base}.gt.txt" 2>/dev/null || true
                                break
                            fi
                        done
                    fi
                fi
                if [ -f "$MIXED_SRC" ]; then
                    mixed_base="${output_base}.mixed"
                    text2image \
                        --text="$MIXED_SRC" \
                        --outputbase="$mixed_base" \
                        --font="$used_font" \
                        --ptsize=$THIS_PTSIZE \
                        --resolution=$THIS_DPI \
                        --margin=$MARGIN \
                        --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
                        --exposure="$EXP" \
                        >>"$log_file" 2>&1 || true
                    if [ -f "${mixed_base}.tif" ] && [ -f "${mixed_base}.box" ]; then
                        cp "$MIXED_SRC" "${mixed_base}.gt.txt" 2>/dev/null || true
                    else
                        for lf in "Noto Sans" "DejaVu Sans" "Liberation Sans"; do
                            text2image \
                                --text="$MIXED_SRC" \
                                --outputbase="$mixed_base" \
                                --font="$lf" \
                                --ptsize=$THIS_PTSIZE \
                                --resolution=$THIS_DPI \
                                --margin=$MARGIN \
                                --leading=$THIS_LEADING \
                                --char_spacing=$THIS_CHSP \
                                --exposure="$EXP" \
                                >>"$log_file" 2>&1 || true
                            if [ -f "${mixed_base}.tif" ] && [ -f "${mixed_base}.box" ]; then
                                cp "$MIXED_SRC" "${mixed_base}.gt.txt" 2>/dev/null || true
                                break
                            fi
                        done
                    fi
                fi
                                                                if [ "$ENABLE_AUG" = "1" ] && command -v convert >/dev/null 2>&1; then
                                                                        for k in $(seq 1 "$AUG_VARIANTS"); do
                                                                                aug_base="${output_base}.aug${k}"
                                                                                case $k in
                                                                                    1)
                                                                                        convert "${output_base}.tif" -colorspace Gray \
                                                                                            \( +clone -contrast-stretch 1%x1% -attenuate 0.02 +noise Gaussian -blur 0x0.4 \) \
                                                                                            -compose over -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    2)
                                                                                        convert "${output_base}.tif" -colorspace Gray -quality 85 "${aug_base}.jpg" 2>>"$log_file" || true
                                                                                        if [ -f "${aug_base}.jpg" ]; then convert "${aug_base}.jpg" "${aug_base}.tif" 2>>"$log_file" || true; fi ;;
                                                                                    3)
                                                                                        convert "${output_base}.tif" -colorspace Gray -ordered-dither o8x8 -blur 0x0.3 "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    4)
                                                                                        convert "${output_base}.tif" -colorspace Gray \( -size 2000x2000 xc:white -attenuate 0.02 +noise Multiplicative -colorspace Gray -resize "@" \) \
                                                                                            -compose multiply -composite -contrast-stretch 2%x2% "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    5)
                                                                                        convert "${output_base}.tif" -colorspace Gray \( +clone -radial-blur 0.2 \) -compose overlay -composite "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                    *)
                                                                                        convert "${output_base}.tif" -colorspace Gray -attenuate 0.01 +noise Gaussian "${aug_base}.tif" 2>>"$log_file" || true ;;
                                                                                esac
                                                                                if [ -f "${aug_base}.tif" ]; then
                                                                                        cp "${output_base}.box" "${aug_base}.box" 2>/dev/null || true
                                                                                        cp "${output_base}.gt.txt" "${aug_base}.gt.txt" 2>/dev/null || true
                                                                                fi
                                                                        done
                                                                fi
                ok_this_font=1
            fi
            fi
        fi
        exp_idx=$((exp_idx+1))
            done
          done
        done
      done
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