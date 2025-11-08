#!/bin/bash
# Parallel font processor - processes one font with all its variations
# Usage: parallel_font_processor.sh <font_file> <font_index> <total_fonts>

FONT_FILE="$1"
FONT_IDX="$2"
TOTAL_FONTS="$3"

# Source environment from parent if available
WORK_DIR="${WORK_DIR:-$(pwd)}"
OUTPUT_DIR="${OUTPUT_DIR:-$WORK_DIR/training_output_best}"
GROUND_TRUTH_DIR="${GROUND_TRUTH_DIR:-$OUTPUT_DIR/ground_truth}"
FONTS_DIR="${FONTS_DIR:-fonts}"
CORPUS_SRC="${CORPUS_SRC:-$OUTPUT_DIR/tmp/ckb.training_text.norm.nfc}"

# Parameters from parent
FONT_SIZE_LIST="${FONT_SIZE_LIST:-16,18,20,22}"
DPI_LIST="${DPI_LIST:-200,300,400}"
LEADING_LIST="${LEADING_LIST:-20,22,26}"
CHAR_SPACING_LIST="${CHAR_SPACING_LIST:-0.5,1.0,1.5}"
MARGIN="${MARGIN:-15}"
EXPOSURES="${EXPOSURES:--2 -1 0 1 2}"
ENABLE_AUG="${ENABLE_AUG:-1}"
AUG_VARIANTS="${AUG_VARIANTS:-5}"

font_name=$(basename "$FONT_FILE" .ttf)
log_file="${OUTPUT_DIR}/logs/${font_name}.log"
: > "$log_file"

# Helper function to iterate comma-separated list or return single value
iter_or_single() {
    local list="$1" default="$2"
    if [[ "$list" =~ , ]]; then
        echo "$list" | tr ',' ' '
    else
        echo "${list:-$default}"
    fi
}

# Calculate total images for this font
IFS=' ' read -ra EXP_ARRAY <<< "$EXPOSURES"
font_size_count=$(echo "$FONT_SIZE_LIST" | tr ',' '\n' | wc -l)
dpi_count=$(echo "$DPI_LIST" | tr ',' '\n' | wc -l)
leading_count=$(echo "$LEADING_LIST" | tr ',' '\n' | wc -l)
charsp_count=$(echo "$CHAR_SPACING_LIST" | tr ',' '\n' | wc -l)
exp_count=${#EXP_ARRAY[@]}
aug_total=$((1 + AUG_VARIANTS))

total_images=$((font_size_count * dpi_count * leading_count * charsp_count * exp_count * aug_total))

# Progress tracking
processed=0
success_count=0
skipped_count=0

# Print initial worker line (worker gets its own line)
printf "[Worker %d/%d] %s - Initializing...\n" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" >&2

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local width=30
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    # Update every 5 images or at key points (start, end)
    if [ $((current % 5)) -eq 0 ] || [ "$current" -eq 1 ] || [ "$current" -eq "$total" ]; then
        # Move up one line, clear it, then print progress
        # This keeps each worker on its own line
        printf "\033[1A\033[K[Worker %d/%d] %s [" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" >&2
        printf "%${filled}s" | tr ' ' '=' >&2
        printf "%${empty}s" | tr ' ' '-' >&2
        printf "] %d%% (%d/%d)\n" "$percent" "$current" "$total" >&2
    fi
}

# Resolve font name
internal_name="$font_name"
if command -v fc-scan >/dev/null 2>&1; then
    fam=$(fc-scan --format='%{family}\n' "$FONT_FILE" 2>>"$log_file" | head -1 || true)
    fam="${fam%%,*}"
    [ -n "$fam" ] && internal_name="$fam"
fi

# Validate font
used_font=""
for cand in "$internal_name" "$font_name" "Noto Naskh Arabic"; do
    if text2image \
        --text="$CORPUS_SRC" \
        --outputbase="$GROUND_TRUTH_DIR/.probe_${font_name}" \
        --font="$cand" \
        --fonts_dir="$WORK_DIR/$FONTS_DIR" \
        --ptsize=16 \
        --resolution=200 \
        --margin=1 \
        --leading=10 \
        --char_spacing=1 \
        --exposure=0 \
        >>"$log_file" 2>&1; then
        used_font="$cand"
        rm -f "$GROUND_TRUTH_DIR/.probe_${font_name}."* 2>/dev/null || true
        break
    fi
done

if [ -z "$used_font" ]; then
    printf "\033[1A\033[K[Worker %d/%d] %s ❌ Failed (font validation)\n" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" >&2
    exit 1
fi

# Generate images with progress
exp_idx=0
for EXP in $EXPOSURES; do
    for THIS_DPI in $(iter_or_single "$DPI_LIST" "200"); do
        for THIS_PTSIZE in $(iter_or_single "$FONT_SIZE_LIST" "16"); do
            for THIS_LEADING in $(iter_or_single "$LEADING_LIST" "22"); do
                for THIS_CHSP in $(iter_or_single "$CHAR_SPACING_LIST" "1.0"); do
                    
                    output_base="$GROUND_TRUTH_DIR/ckb.${font_name}.exp${exp_idx}.d${THIS_DPI}.s${THIS_PTSIZE}.l${THIS_LEADING}.c${THIS_CHSP}"
                    
                    # Skip if exists (resumability)
                    if [ -f "${output_base}.tif" ] && [ -f "${output_base}.box" ]; then
                        ((processed++))
                        ((skipped_count++))
                        show_progress "$processed" "$total_images"
                        continue
                    fi
                    
                    # Generate base image
                    if text2image \
                        --text="$CORPUS_SRC" \
                        --outputbase="$output_base" \
                        --font="$used_font" \
                        --fonts_dir="$WORK_DIR/$FONTS_DIR" \
                        --ptsize=$THIS_PTSIZE \
                        --resolution=$THIS_DPI \
                        --margin=$MARGIN \
                        --leading=$THIS_LEADING \
                        --char_spacing=$THIS_CHSP \
                        --exposure="$EXP" \
                        >>"$log_file" 2>&1; then
                        ((success_count++))
                    fi
                    
                    ((processed++))
                    show_progress "$processed" "$total_images"
                    
                    # Generate augmented variants
                    if [ "$ENABLE_AUG" -eq 1 ] && [ -f "${output_base}.tif" ]; then
                        for variant in $(seq 1 $AUG_VARIANTS); do
                            aug_base="${output_base}_aug${variant}"
                            
                            if [ -f "${aug_base}.tif" ] && [ -f "${aug_base}.box" ]; then
                                ((processed++))
                                ((skipped_count++))
                                show_progress "$processed" "$total_images"
                                continue
                            fi
                            
                            # Apply augmentation (simplified - just copy for now)
                            cp "${output_base}.tif" "${aug_base}.tif" 2>/dev/null
                            cp "${output_base}.box" "${aug_base}.box" 2>/dev/null
                            
                            if [ -f "${aug_base}.tif" ]; then
                                ((success_count++))
                            fi
                            
                            ((processed++))
                            show_progress "$processed" "$total_images"
                        done
                    fi
                    
                done
            done
        done
    done
    ((exp_idx++))
done

# Final status - replace the progress line
new_count=$((success_count))
printf "\033[1A\033[K[Worker %d/%d] %s ✅ Success (New: %d, Skipped: %d, Total: %d/%d)\n" \
    "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$new_count" "$skipped_count" "$processed" "$total_images" >&2
exit 0
