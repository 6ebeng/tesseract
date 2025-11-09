#!/bin/bash
# Parallel font processor - processes one font with all its variations
# Usage: parallel_font_processor.sh <font_file> <font_index> <total_fonts>

# Unbuffer stderr for immediate output and disable buffering
exec 2>&1
set -o pipefail
export PYTHONUNBUFFERED=1

FONT_FILE="$1"
FONT_IDX="$2"
TOTAL_FONTS="$3"
WORKER_SLOT="${SLOT:-1}"  # Job slot from GNU Parallel {%}

# Display configuration (matches Python scraper approach)
HEADER_LINES=4
FOOTER_LINES=4
# Logs scroll in middle section (lines 5 to terminal_height - 4)

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
corrupted_count=0
update_count=0
last_update_time=0

# Check if this font is already completely processed (early exit optimization)
existing_count=$(find "$GROUND_TRUTH_DIR" -name "ckb.${font_name}.*.tif" 2>/dev/null | wc -l)
if [ "$existing_count" -ge "$total_images" ]; then
    printf "[Slot%d W%d/%d] %-20s => Already Complete (%d files)\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$total_images"
    exit 0
fi

if [ "$existing_count" -gt 0 ]; then
    printf "[Slot%d W%d/%d] %-20s => Resume (has %d, need %d)\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$existing_count" "$((total_images - existing_count))"
else
    printf "[Slot%d W%d/%d] %-20s => Start (generating %d files)\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$total_images"
fi

# Progress bar function with 2-second heartbeat
# Writes to scrolling middle section (like Python scraper logs)
show_progress() {
    local current="$1"
    local total="$2"
    local percent=$(( current * 100 / total ))
    local filled=$(( percent / 5 ))
    local empty=$(( 20 - filled ))
    local current_time
    current_time=$(date +%s)
    
    local bar="$(printf "%${filled}s" | tr ' ' '#')$(printf "%${empty}s" | tr ' ' '-')"
    
    # Update every 2 seconds or when complete
    # Logs scroll naturally in the middle section (no fixed positioning)
    if [ $((current_time - last_update_time)) -ge 2 ] || [ "$current" -eq "$total" ]; then
        
        if [ "$corrupted_count" -gt 0 ]; then
            printf "[Slot%d W%d/%d] %-20s [%s] %3d%% (%d/%d) New:%d Skip:%d Bad:%d\n" \
                "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$bar" \
                "$percent" "$current" "$total" "$success_count" "$skipped_count" "$corrupted_count"
        else
            printf "[Slot%d W%d/%d] %-20s [%s] %3d%% (%d/%d) New:%d Skip:%d\n" \
                "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$bar" \
                "$percent" "$current" "$total" "$success_count" "$skipped_count"
        fi
        
        last_update_time="$current_time"
    fi
    
    # Mark complete
    if [ "$current" -eq "$total" ]; then
        printf "[Slot%d W%d/%d] %-20s COMPLETE\n" \
            "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name"
    fi
}

# File validation function - checks if files exist and are not corrupted
validate_files() {
    local base="$1"
    local tif_file="${base}.tif"
    local box_file="${base}.box"
    
    # Check if both files exist
    if [ ! -f "$tif_file" ] || [ ! -f "$box_file" ]; then
        return 1
    fi
    
    # Check if files are not empty (corrupted files are often 0 bytes)
    local tif_size=$(stat -f%z "$tif_file" 2>/dev/null || stat -c%s "$tif_file" 2>/dev/null || echo "0")
    local box_size=$(stat -f%z "$box_file" 2>/dev/null || stat -c%s "$box_file" 2>/dev/null || echo "0")
    
    if [ "$tif_size" -lt 100 ] || [ "$box_size" -lt 10 ]; then
        # Files are too small, likely corrupted - delete them
        rm -f "$tif_file" "$box_file" 2>/dev/null
        ((corrupted_count++))
        return 1
    fi
    
    # Validate TIFF header (should start with "II*" or "MM*")
    local tif_header=$(head -c 4 "$tif_file" 2>/dev/null | od -An -tx1 | tr -d ' \n')
    if [[ ! "$tif_header" =~ ^(49492a00|4d4d002a) ]]; then
        # Invalid TIFF header - delete corrupted files
        rm -f "$tif_file" "$box_file" 2>/dev/null
        ((corrupted_count++))
        return 1
    fi
    
    # Files are valid
    return 0
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
    printf "[Slot%d W%d/%d] %-20s => FAILED (font validation)\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name"
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
                    
                    # Skip if exists and valid (resumability with corruption check)
                    if validate_files "$output_base"; then
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
                        
                        # Verify the generated files are valid
                        if validate_files "$output_base"; then
                            ((success_count++))
                        fi
                    fi
                    
                    ((processed++))
                    show_progress "$processed" "$total_images"
                    
                    # Generate augmented variants
                    if [ "$ENABLE_AUG" -eq 1 ] && [ -f "${output_base}.tif" ]; then
                        for variant in $(seq 1 $AUG_VARIANTS); do
                            aug_base="${output_base}_aug${variant}"
                            
                            # Skip if exists and valid (resumability with corruption check)
                            if validate_files "$aug_base"; then
                                ((processed++))
                                ((skipped_count++))
                                show_progress "$processed" "$total_images"
                                continue
                            fi
                            
                            # Apply augmentation (simplified - just copy for now)
                            cp "${output_base}.tif" "${aug_base}.tif" 2>/dev/null
                            cp "${output_base}.box" "${aug_base}.box" 2>/dev/null
                            
                            # Verify the copied files are valid
                            if validate_files "$aug_base"; then
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

# Final status
new_count=$((success_count))
if [ "$corrupted_count" -gt 0 ]; then
    printf "[Slot%d W%d/%d] %-20s => DONE: New:%d Skip:%d Fixed:%d Total:%d\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$new_count" "$skipped_count" "$corrupted_count" "$total_images"
else
    printf "[Slot%d W%d/%d] %-20s => DONE: New:%d Skip:%d Total:%d\n" \
        "$WORKER_SLOT" "$FONT_IDX" "$TOTAL_FONTS" "$font_name" "$new_count" "$skipped_count" "$total_images"
fi
exit 0
