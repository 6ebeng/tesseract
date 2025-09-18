#!/bin/bash

# WSL-friendly fast & robust Kurdish (ckb) training using local fonts and Sorani corpus
set -e

# =============================
# Config
# =============================
export TESSDATA_PREFIX=${TESSDATA_PREFIX:-/usr/share/tesseract-ocr/5/tessdata}
# Resolve repo root from this script location (work/scripts -> repo_root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORK_DIR="$REPO_DIR/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-wsl"
FONTS_PATH="$WORK_DIR/fonts"   # Use your fonts folder directly
TESSDATA_TMP="$WORK_DIR/tessdata_tmp"
LOG_DIR="$WORK_DIR/output/logs"

# Speed/quality knobs
MAX_FONTS=${MAX_FONTS:-60}            # cap fonts for fast but strong results
MAX_ITER=${MAX_ITER:-5000}
TARGET_ERR=${TARGET_ERR:-0.005}
DEBUG_INTERVAL=${DEBUG_INTERVAL:--1}

# Base text2image variations (safe augmentations supported by text2image)
EXPOSURES="-1 0 1"
CHAR_SPACING="0.0 0.15"
PTSIZES="10 12 16"
RESOLUTIONS="200 300"

# Augmentation (ImageMagick-based + text2image options)
SHEAR_ANGLES=""
ROT_ANGLES=""
ADD_NOISE=false
ADD_BLUR=false

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   WSL Fast & Robust Kurdish (ckb) Training from Fonts + Corpus    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo -e "${BLUE}Working dir: $(pwd)${NC}"

# =============================
# Helpers
# =============================
need_cmd() { command -v "$1" >/dev/null 2>&1; }

ensure_dirs() {
    rm -rf "$GROUND_TRUTH_DIR"
    mkdir -p "$GROUND_TRUTH_DIR" "$OUTPUT_DIR" "$LOG_DIR"
}

check_env() {
    local ok=true
    for c in tesseract text2image lstmtraining; do
        if ! need_cmd "$c"; then
            echo -e "${RED}✗ Missing: $c${NC}"; ok=false
        else
            echo -e "${GREEN}✓ Found: $c${NC}"
        fi
    done
    if ! $ok; then
        echo -e "${RED}Install missing tools inside WSL and retry.${NC}"; exit 1
    fi

    if [ ! -f "$CORPUS_FILE" ]; then
        echo -e "${RED}Corpus not found: $CORPUS_FILE${NC}"; exit 1
    fi

    if [ ! -d "$FONTS_PATH" ]; then
        echo -e "${RED}Fonts folder not found: $FONTS_PATH${NC}"; exit 1
    fi

    if ! need_cmd convert; then
        echo -e "${YELLOW}ImageMagick 'convert' not found -> shear/blur/noise limited${NC}"
        IMAGEMAGICK=false
    else
        IMAGEMAGICK=true
    fi

    # Refresh font cache for our fonts directory (best-effort)
    fc-cache -f -v "$FONTS_PATH" >/dev/null 2>&1 || true
}

# Install fonts into user font directory for reliable discovery
install_fonts_local() {
    local usr_fonts="$HOME/.local/share/fonts/ckb"
    mkdir -p "$usr_fonts"
    find "$FONTS_PATH" -maxdepth 1 -type f -iname "*.ttf" -exec cp -u {} "$usr_fonts/" \; 2>/dev/null || true
    fc-cache -f -v "$HOME/.local/share/fonts" >/dev/null 2>&1 || true
}

# Prepare a minimal fontconfig that explicitly includes our fonts folder.
setup_fontconfig() {
    FC_TMP="$OUTPUT_DIR/fonts.conf.tmp"
    cat > "$FC_TMP" <<EOF
<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>
    <dir>$FONTS_PATH</dir>
    <config>
        <match target="scan">
            <test compare="contains" name="family">
                <string>Sarchia</string>
            </test>
            <edit mode="assign" name="lang">
                <string>ar</string>
            </edit>
        </match>
    </config>
</fontconfig>
EOF
    export FONTCONFIG_FILE="$FC_TMP"
    fc-cache -f -v "$FONTS_PATH" >/dev/null 2>&1 || true
}

ensure_best_base() {
    mkdir -p "$TESSDATA_TMP"
    BASE_MODEL="ara"
    BEST_PATH=""

    # Prefer installed *_best models; avoid network fetches
    if [ -f "$TESSDATA_PREFIX/ara_best.traineddata" ]; then
        BEST_PATH="$TESSDATA_PREFIX/ara_best.traineddata"; BASE_MODEL="ara"
        echo -e "${GREEN}✓ Using best base model: $(basename "$BEST_PATH")${NC}"
        BASE_TRAINEDDATA="$BEST_PATH"
        return
    fi
    # Prefer language match over eng_best
    if [ -f "$TESSDATA_PREFIX/ara.traineddata" ]; then
        BASE_TRAINEDDATA="$TESSDATA_PREFIX/ara.traineddata"; BASE_MODEL="ara"
        echo -e "${GREEN}✓ Using base: $(basename "$BASE_TRAINEDDATA")${NC}"
        return
    fi
    if [ -f "$TESSDATA_PREFIX/eng_best.traineddata" ]; then
        BEST_PATH="$TESSDATA_PREFIX/eng_best.traineddata"; BASE_MODEL="eng"
        echo -e "${YELLOW}Using eng_best base (language fallback): $(basename "$BEST_PATH")${NC}"
        BASE_TRAINEDDATA="$BEST_PATH"
        return
    fi
    # Last resort
    BASE_TRAINEDDATA="$TESSDATA_PREFIX/eng.traineddata"; BASE_MODEL="eng"
    echo -e "${YELLOW}Using base: $(basename "$BASE_TRAINEDDATA") (fallback)${NC}"
}

# Build a list of font NAMES that text2image recognizes from our folder
select_fonts() {
    echo -e "${YELLOW}Scanning available fonts...${NC}"
    # Use a temp file on the Linux filesystem to avoid permission issues on /mnt/c
    local list_file
    list_file="$(mktemp -t fonts_list.XXXXXX)"
    # Capture both legacy 'name=' and indexed 'N: Name' formats
    text2image --list_available_fonts --fonts_dir="$FONTS_PATH" 2>/dev/null | \
        awk '
            /^name=/ { sub(/^name=/, ""); print; next }
            /^[ \t]*[0-9]+:[ \t]*/ { sub(/^[ \t]*[0-9]+:[ \t]*/, ""); print; next }
        ' | sed 's/\r$//' | sort -u > "$list_file" 2>/dev/null || true

    # If nothing found, try without --fonts_dir relying on FONTCONFIG_FILE
    local count=$(wc -l < "$list_file" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
        text2image --list_available_fonts 2>/dev/null | \
            awk '
                /^name=/ { sub(/^name=/, ""); print; next }
                /^[ \t]*[0-9]+:[ \t]*/ { sub(/^[ \t]*[0-9]+:[ \t]*/, ""); print; next }
            ' | sed 's/\r$//' | sort -u > "$list_file" 2>/dev/null || true
    fi

    local count=$(wc -l < "$list_file" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
        echo -e "${YELLOW}text2image did not list custom fonts. Extracting family names via fontconfig...${NC}"
        # Use fc-scan to extract proper family names that text2image expects
        # Prefer first family entry per font file
        if command -v fc-scan >/dev/null 2>&1; then
            TMP_FAMS="$(mktemp -t fonts_fams.XXXXXX)"
            : > "$TMP_FAMS"
            while IFS= read -r ttf; do
                fam=$(fc-scan --format='%{family[0]}\n' "$ttf" 2>/dev/null | tr -d '\r' | sed 's/^\s*//;s/\s*$//')
                [ -n "$fam" ] && echo "$fam" >> "$TMP_FAMS"
            done < <(find "$FONTS_PATH" -maxdepth 1 -type f -iname "*.ttf" | sort)
            if [ -s "$TMP_FAMS" ]; then
                cat "$TMP_FAMS" | sort -u | head -$MAX_FONTS > "$list_file"
            else
                # Absolute fallback: file basenames (may or may not work)
                find "$FONTS_PATH" -maxdepth 1 -type f -iname "*.ttf" | \
                    xargs -I{} basename {} .ttf | head -$MAX_FONTS > "$list_file" || true
            fi
        else
            echo -e "${YELLOW}fc-scan not found; using basenames as a last resort.${NC}"
            find "$FONTS_PATH" -maxdepth 1 -type f -iname "*.ttf" | \
                xargs -I{} basename {} .ttf | head -$MAX_FONTS > "$list_file" || true
        fi
    else
        # Prefer Sarchia family first if present, then others
            local sel_tmp
            sel_tmp="$(mktemp -t fonts_sel.XXXXXX)"
            grep -i "Sarchia" "$list_file" | head -$MAX_FONTS > "$sel_tmp" 2>/dev/null || true
            local have
            have=$(wc -l < "$sel_tmp" 2>/dev/null || echo 0)
            grep -vi "Sarchia" "$list_file" | head -$((MAX_FONTS - have)) >> "$sel_tmp" 2>/dev/null || true
            mv "$sel_tmp" "$list_file"
    fi

    FONT_LIST="$list_file"
    FONT_COUNT=$(wc -l < "$FONT_LIST" 2>/dev/null || echo 0)
    echo -e "${GREEN}✓ Using $FONT_COUNT fonts (cap=$MAX_FONTS)${NC}"
    # Best-effort copy to output for inspection, ignore failures on /mnt/c
    cp "$FONT_LIST" "$OUTPUT_DIR/available_fonts.txt" 2>/dev/null || true
}

augment_with_imagemagick() {
    local input_img="$1"    # path.tif
    local base_noext="$2"   # path
    local gt_txt="${base_noext}.gt.txt"

    [ -f "$input_img" ] || return 0
    [ -f "$gt_txt" ] || return 0
    # Disabled to avoid box/gt misalignment with external transforms
    return 0

    # shear
    for s in $SHEAR_ANGLES; do
        local out="${base_noext}_shear${s}.tif"
        convert "$input_img" -shear "${s}x0" "$out" 2>/dev/null || true
        [ -f "$out" ] && cp "$gt_txt" "${base_noext}_shear${s}.gt.txt"
    done

    # small rotations
    for r in $ROT_ANGLES; do
        local out="${base_noext}_rot${r}.tif"
        convert "$input_img" -rotate "$r" -background white -gravity center -extent 100% "$out" 2>/dev/null || true
        [ -f "$out" ] && cp "$gt_txt" "${base_noext}_rot${r}.gt.txt"
    done

    # optional noise/blur
    if [ "$ADD_NOISE" = true ]; then
        local outn="${base_noext}_noise.tif"
        convert "$input_img" -attenuate 0.2 +noise Gaussian "$outn" 2>/dev/null || true
        [ -f "$outn" ] && cp "$gt_txt" "${base_noext}_noise.gt.txt"
    fi
    if [ "$ADD_BLUR" = true ]; then
        local outb="${base_noext}_blur.tif"
        convert "$input_img" -blur 0x0.5 "$outb" 2>/dev/null || true
        [ -f "$outb" ] && cp "$gt_txt" "${base_noext}_blur.gt.txt"
    fi
}

generate_training_data() {
    echo -e "${YELLOW}Generating training images from corpus and fonts...${NC}"
    local success=0
    local index=0

    mapfile -t FONT_NAMES < "$FONT_LIST"
    local total=${#FONT_NAMES[@]}
    echo -e "${BLUE}Fonts to process: $total${NC}"
    index=0
    for FONT_NAME in "${FONT_NAMES[@]}"; do
        index=$((index+1))
        CLEAN_NAME=$(echo "$FONT_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-40)

        VARS=0
        for p in $PTSIZES; do
          for r in $RESOLUTIONS; do
            for spacing in $CHAR_SPACING; do
              for expo in $EXPOSURES; do
                OUT_BASE="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.p${p}r${r}s${spacing//./}e${expo}"
                                                if text2image \
                  --text="$CORPUS_FILE" \
                  --outputbase="$OUT_BASE" \
                  --font="$FONT_NAME" \
                  --fonts_dir="$FONTS_PATH" \
                  --char_spacing="$spacing" \
                  --exposure="$expo" \
                  --resolution=$r \
                  --ptsize=$p \
                                                    --strip_unrenderable_words \
                                    --max_pages=1 >/dev/null 2>"$LOG_DIR/t2i_${CLEAN_NAME}.log"; then
                  success=$((success+1))
                  VARS=$((VARS+1))
                                else
                                    # Retry without --fonts_dir to let fontconfig pick it up
                                                        if text2image \
                                        --text="$CORPUS_FILE" \
                                        --outputbase="$OUT_BASE" \
                                        --font="$FONT_NAME" \
                                        --char_spacing="$spacing" \
                                        --exposure="$expo" \
                                        --resolution=$r \
                                        --ptsize=$p \
                                                            --strip_unrenderable_words \
                                        --max_pages=1 >/dev/null 2>>"$LOG_DIR/t2i_${CLEAN_NAME}.log"; then
                                        success=$((success+1))
                                        VARS=$((VARS+1))
                                    fi
                fi
                [ $VARS -ge 3 ] && break 2
              done
            done
          done
          [ $VARS -ge 3 ] && break
        done

        if [ $((index % 10)) -eq 0 ]; then
            echo -e "${GREEN}  processed $index fonts...${NC}"
        fi
    done

    echo -e "${GREEN}✓ Base samples created: $success${NC}"
        BASE_SAMPLES_CREATED=$success
}

# Fallback: try per-TTF using fc-scan family and basename when FONT_NAME attempts fail
generate_training_data_fallback_ttf() {
        echo -e "${YELLOW}Fallback: generating using TTF files (fc-scan families/basenames)...${NC}"
        local success=0
        local index=0
        mapfile -t TTF_FILES < <(find "$FONTS_PATH" -maxdepth 1 -type f -iname "*.ttf" | sort | head -$MAX_FONTS)
        local total=${#TTF_FILES[@]}
        echo -e "${BLUE}TTFs to try: $total${NC}"
        for FONT_FILE in "${TTF_FILES[@]}"; do
                index=$((index+1))
                BASENAME=$(basename "$FONT_FILE" .ttf)
                CLEAN_NAME=$(echo "$BASENAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-40)
                FAMILY=""
                if command -v fc-scan >/dev/null 2>&1; then
                        FAMILY=$(fc-scan --format='%{family[0]}\n' "$FONT_FILE" 2>/dev/null | tr -d '\r')
                fi
                VARS=0
                for p in $PTSIZES; do
                    for r in $RESOLUTIONS; do
                        for spacing in $CHAR_SPACING; do
                            for expo in $EXPOSURES; do
                                OUT_BASE="$GROUND_TRUTH_DIR/ckb.${CLEAN_NAME}.p${p}r${r}s${spacing//./}e${expo}"
                                # 1) Try FAMILY name
                                if [ -n "$FAMILY" ] && text2image \
                                    --text="$CORPUS_FILE" \
                                    --outputbase="$OUT_BASE" \
                                    --font="$FAMILY" \
                                    --fonts_dir="$FONTS_PATH" \
                                    --char_spacing="$spacing" \
                                    --exposure="$expo" \
                                    --resolution=$r \
                                    --ptsize=$p \
                                    --strip_unrenderable_words \
                                    --max_pages=1 >/dev/null 2>>"$LOG_DIR/t2i_${CLEAN_NAME}.log"; then
                                    success=$((success+1)); VARS=$((VARS+1))
                                # 2) Try BASENAME as font name
                                elif text2image \
                                    --text="$CORPUS_FILE" \
                                    --outputbase="$OUT_BASE" \
                                    --font="$BASENAME" \
                                    --fonts_dir="$FONTS_PATH" \
                                    --char_spacing="$spacing" \
                                    --exposure="$expo" \
                                    --resolution=$r \
                                    --ptsize=$p \
                                    --strip_unrenderable_words \
                                    --max_pages=1 >/dev/null 2>>"$LOG_DIR/t2i_${CLEAN_NAME}.log"; then
                                    success=$((success+1)); VARS=$((VARS+1))
                                # 3) Try FAMILY without fonts_dir (fontconfig)
                                elif [ -n "$FAMILY" ] && text2image \
                                    --text="$CORPUS_FILE" \
                                    --outputbase="$OUT_BASE" \
                                    --font="$FAMILY" \
                                    --char_spacing="$spacing" \
                                    --exposure="$expo" \
                                    --resolution=$r \
                                    --ptsize=$p \
                                    --strip_unrenderable_words \
                                    --max_pages=1 >/dev/null 2>>"$LOG_DIR/t2i_${CLEAN_NAME}.log"; then
                                    success=$((success+1)); VARS=$((VARS+1))
                                fi
                                [ $VARS -ge 3 ] && break 2
                            done
                        done
                    done
                    [ $VARS -ge 3 ] && break
                done
                if [ $((index % 10)) -eq 0 ]; then
                        echo -e "${GREEN}  fallback processed $index ttf files...${NC}"
                fi
        done
        echo -e "${GREEN}✓ Fallback base samples created: $success${NC}"
}

generate_lstmf() {
    echo -e "${YELLOW}Converting images to LSTMF...${NC}"
        LSTMF_LIST="$OUTPUT_DIR/wsl-corpus-lstmf.txt"
    : > "$LSTMF_LIST"
    LSTMF_COUNT=0

            # Choose language for .lstmf generation to match base traineddata
                # Match language to base model selection
                local lstm_lang="ara"

            for tif in "$GROUND_TRUTH_DIR"/*.tif; do
        [ -f "$tif" ] || continue
        base=${tif%.tif}
            # Use gt.txt if present, else allow BOX (text2image creates .box)
                if [ -f "${base}.gt.txt" ] || [ -f "${base}.box" ]; then
                    tesseract "$tif" "$base" --psm 6 -l "$lstm_lang" lstm.train >/dev/null 2>&1 || true
                [ -f "${base}.lstmf" ] && echo "${base}.lstmf" >> "$LSTMF_LIST" && LSTMF_COUNT=$((LSTMF_COUNT+1))
            fi
        if [ $((LSTMF_COUNT % 50)) -eq 0 ] && [ $LSTMF_COUNT -gt 0 ]; then
            echo "  LSTMF files: $LSTMF_COUNT"
        fi
    done
    echo -e "${GREEN}✓ LSTMF ready: $LSTMF_COUNT${NC}"
}

train_and_finalize() {
    echo -e "${YELLOW}Starting training...${NC}"
    local base_model="ara"
    [ -f "$TESSDATA_PREFIX/ara.traineddata" ] || base_model="eng"

            # If using *_best (LSTM) base, continue_from its extracted LSTM
            local starter=""
            if echo "$BASE_TRAINEDDATA" | grep -q "_best\.traineddata$" && command -v combine_tessdata >/dev/null 2>&1; then
                starter="$OUTPUT_DIR/starter.lstm"
                combine_tessdata -e "$BASE_TRAINEDDATA" "$starter" >/dev/null 2>&1 || starter=""
            fi

            if [ -s "$starter" ]; then
                lstmtraining \
                    --continue_from "$starter" \
                    --model_output "$OUTPUT_DIR/ckb_wsl_fast_robust" \
                    --traineddata "$BASE_TRAINEDDATA" \
                    --train_listfile "$OUTPUT_DIR/wsl-corpus-lstmf.txt" \
                    --max_iterations "$MAX_ITER" \
                    --target_error_rate "$TARGET_ERR" \
                    --debug_interval "$DEBUG_INTERVAL"
            else
                lstmtraining \
                    --model_output "$OUTPUT_DIR/ckb_wsl_fast_robust" \
                    --traineddata "$BASE_TRAINEDDATA" \
                    --train_listfile "$OUTPUT_DIR/wsl-corpus-lstmf.txt" \
                    --max_iterations "$MAX_ITER" \
                    --target_error_rate "$TARGET_ERR" \
                    --debug_interval "$DEBUG_INTERVAL"
            fi

    CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_wsl_fast_robust*.checkpoint 2>/dev/null | head -1)
    if [ -z "$CHECKPOINT" ]; then
        echo -e "${RED}Training failed (no checkpoint). See output above for errors.${NC}"; exit 1
    fi
    echo -e "${GREEN}✓ Training checkpoint: $(basename "$CHECKPOINT")${NC}"

    echo -e "${YELLOW}Finalizing model...${NC}"
    FINAL_TRAINED="$OUTPUT_DIR/ckb_wsl_fast_robust.traineddata"
    lstmtraining \
        --stop_training \
        --continue_from "$CHECKPOINT" \
        --traineddata "$BASE_TRAINEDDATA" \
        --model_output "$FINAL_TRAINED" >/dev/null 2>&1

    if [ -f "$FINAL_TRAINED" ]; then
        mkdir -p "$REPO_DIR/tessdata"
        cp "$FINAL_TRAINED" "$REPO_DIR/tessdata/"
        # Also provide the canonical name ckb.traineddata
        cp "$FINAL_TRAINED" "$REPO_DIR/tessdata/ckb.traineddata"
        SIZE=$(du -h "$FINAL_TRAINED" | cut -f1)
        echo -e "${GREEN}✓ Model created (${SIZE}) at tessdata/$(basename "$FINAL_TRAINED")${NC}"
        echo -e "${GREEN}✓ Copied as tessdata/ckb.traineddata${NC}"
        echo "Usage: tesseract image.tif out -l ckb_wsl_fast_robust --psm 6"
    else
        echo -e "${RED}Failed to create final traineddata.${NC}"; exit 1
    fi
}

# =============================
# Main
# =============================
ensure_dirs
check_env
setup_fontconfig
ensure_best_base
install_fonts_local
select_fonts
generate_training_data
if [ "${BASE_SAMPLES_CREATED:-0}" -eq 0 ]; then
    generate_training_data_fallback_ttf
fi
generate_lstmf
train_and_finalize
