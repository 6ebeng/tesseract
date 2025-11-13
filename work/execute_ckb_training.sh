#!/bin/bash

# Execute LSTM fine-tuning from generated ground-truth to produce ckb.traineddata
# Flow: generate .lstmf (hybrid fas+ara seg), choose/build target ckb traineddata, fine-tune from fas and ara, finalize and install.

set -euo pipefail

WORK_DIR="/mnt/c/tesseract/work"

# Allow OUTPUT_DIR override (e.g., for Z: drive or custom locations)
if [ -n "${OUTPUT_DIR:-}" ]; then
    BASE_OUTPUT_DIR="$OUTPUT_DIR"
else
    BASE_OUTPUT_DIR="$WORK_DIR/training_output"
fi

GT_DIR="$BASE_OUTPUT_DIR/ground_truth"
TMP_DIR="$BASE_OUTPUT_DIR/tmp"
OUT_DIR="$BASE_OUTPUT_DIR/model"
LANG="ckb"

# Batch processing parameters (NEW)
USE_BATCH_PROCESSING="${USE_BATCH_PROCESSING:-0}"  # Set to 1 to enable batch mode
BATCH_SIZE="${BATCH_SIZE:-5000}"                    # Files per batch
LOCAL_BATCH_DIR="${LOCAL_BATCH_DIR:-$WORK_DIR/batch_processing}"

# Training tunables (can be overridden via environment)
MAX_ITERS="${MAX_ITERS:-1500}"
DEBUG_INTERVAL="${DEBUG_INTERVAL:-0}"
TRAINING_EXTRA_ARGS="${TRAINING_EXTRA_ARGS:-}"
LATIN_DIGITS="${LATIN_DIGITS:-0}" # 1 to include ASCII 0-9 in numbers.txt for minimal traineddata
PUNCS_EXTRA="${PUNCS_EXTRA:-}"   # extra punctuation to append to defaults
OEM="${OEM:-1}"
PSM="${PSM:-6}"

# Performance optimization: Use all CPU cores for parallel processing
# Your i9-12900KF has 16 cores (8P+8E) = 24 threads
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-24}"
export OMP_THREAD_LIMIT="${OMP_THREAD_LIMIT:-24}"

# Enable SIMD optimizations if available
export DOTPRODUCT=avx2

mkdir -p "$TMP_DIR" "$OUT_DIR" 2>/dev/null || true
# Resolve ground truth directory with fallbacks if default is missing
if [ ! -d "$GT_DIR" ]; then
  # Try alternate ground truth locations
  for cand in \
    "$BASE_OUTPUT_DIR/ground-truth" \
    "$WORK_DIR/ground-truth" \
    "$WORK_DIR/ground-truth-robust" \
    "$WORK_DIR/ground-truth-system" \
    "$WORK_DIR/ground-truth-final" \
    "$WORK_DIR/ground-truth-workaround" \
    "$WORK_DIR/ground-truth-corpus"; do
    if [ -d "$cand" ]; then GT_DIR="$cand"; break; fi
  done
fi

# Check if ground truth directory exists and has TIF files
if [ -d "$GT_DIR" ]; then
  TIF_COUNT=$(find "$GT_DIR" -maxdepth 1 -name '*.tif' -type f 2>/dev/null | wc -l)
  if [ "$TIF_COUNT" -gt 0 ]; then
    echo "✓ Found ground truth directory with $TIF_COUNT TIF files: $GT_DIR"
  else
    echo "⚠️  Ground truth directory exists but has no TIF files: $GT_DIR"
    GT_DIR=""  # Force regeneration
  fi
fi

if [ -z "$GT_DIR" ] || [ ! -d "$GT_DIR" ]; then
  echo "⚠️  Ground truth not found at $BASE_OUTPUT_DIR/ground_truth"
  echo "    Checked: $BASE_OUTPUT_DIR/ground_truth and fallback locations"
  echo "    Attempting to generate using generate_ckb_training_data.sh..."
  if [ -f "$WORK_DIR/generate_ckb_training_data.sh" ]; then
    chmod +x "$WORK_DIR/generate_ckb_training_data.sh" || true
    ( cd "$WORK_DIR" && "$WORK_DIR/generate_ckb_training_data.sh" ) || true
    GT_DIR="$BASE_OUTPUT_DIR/ground_truth"
  fi
fi

if [ ! -d "$GT_DIR" ]; then 
  echo "❌ Ground truth directory not found. Expected at $BASE_OUTPUT_DIR/ground_truth or a ground-truth* folder."
  exit 1
fi

# Final verification - check for TIF files
TIF_COUNT=$(find "$GT_DIR" -maxdepth 1 -name '*.tif' -type f 2>/dev/null | wc -l)
if [ "$TIF_COUNT" -eq 0 ]; then
  echo "❌ No .tif files found in $GT_DIR"
  exit 1
fi

echo "✅ Using ground truth directory: $GT_DIR ($TIF_COUNT TIF files)"

# Tesseract data dirs
TESSDATA_DIR="/usr/share/tesseract-ocr/5/tessdata"
TESSDATA_BEST_DIR="/usr/share/tesseract-ocr/5/tessdata_best"
TESSDATA_FAST_DIR="/usr/share/tesseract-ocr/5/tessdata_fast"
if [ ! -d "$TESSDATA_DIR" ]; then TESSDATA_DIR="/usr/share/tesseract-ocr/4.00/tessdata"; fi
if [ ! -d "$TESSDATA_BEST_DIR" ]; then TESSDATA_BEST_DIR="/usr/share/tesseract-ocr/4.00/tessdata_best"; fi
if [ ! -d "$TESSDATA_FAST_DIR" ]; then TESSDATA_FAST_DIR="/usr/share/tesseract-ocr/4.00/tessdata_fast"; fi

WIN_TESSDATA="/mnt/c/tesseract/tessdata"
WIN_TESSDATA_BEST="/mnt/c/tesseract/tessdata/best"
WIN_TESSDATA_FAST="/mnt/c/tesseract/tessdata/fast"
mkdir -p "$WIN_TESSDATA_BEST" || true
mkdir -p "$WIN_TESSDATA_FAST" || true

IMPORT_REAL_EVAL="${IMPORT_REAL_EVAL:-0}"
REAL_TRAIN_DIR="$WORK_DIR/real_gt/train"
REAL_EVAL_DIR="$WORK_DIR/real_gt/eval"
if [ "$IMPORT_REAL_EVAL" = "1" ]; then
  src_dirs=()
  [ -d "$REAL_TRAIN_DIR" ] && src_dirs+=("$REAL_TRAIN_DIR")
  [ -d "$REAL_EVAL_DIR" ] && src_dirs+=("$REAL_EVAL_DIR")
  if [ ${#src_dirs[@]} -gt 0 ]; then
    echo "➕ Importing real pairs into training set (IMPORT_REAL_EVAL=1): ${src_dirs[*]}"
  fi
  for SRC in "${src_dirs[@]}"; do
    while IFS= read -r -d '' tif; do
    base=$(basename "$tif" .tif)
      gt="$SRC/$base.gt.txt"
    [ -f "$gt" ] || continue
    dst_base="$GT_DIR/real_$base"
    cp -f "$tif" "${dst_base}.tif" 2>/dev/null || true
    cp -f "$gt"  "${dst_base}.gt.txt" 2>/dev/null || true
    if [ ! -f "${dst_base}.box" ]; then
      CKB_TESSDATA="/mnt/c/tesseract/tessdata/best"; [ -f "$CKB_TESSDATA/ckb.traineddata" ] || CKB_TESSDATA="${TESSDATA_BEST_DIR}"
      echo "Bootstrapping boxes for $(basename "$dst_base") using ckb model (psm=$PSM) ..."
      tesseract --tessdata-dir "$CKB_TESSDATA" "${dst_base}.tif" "${dst_base}" -l ckb --oem "$OEM" --psm "$PSM" makebox 2>/dev/null || true
      if [ ! -f "${dst_base}.box" ]; then
        ALT_DIR="$WIN_TESSDATA_BEST"; [ -d "$ALT_DIR" ] || ALT_DIR="$TESSDATA_BEST_DIR"
        if [ -f "$ALT_DIR/ara.traineddata" ]; then
          tesseract --tessdata-dir "$ALT_DIR" "${dst_base}.tif" "${dst_base}" -l ara --oem "$OEM" --psm "$PSM" makebox 2>/dev/null || true
        fi
      fi
    fi
    done < <(find "$SRC" -maxdepth 1 -type f -name '*.tif' -print0)
  done
else
  # Ensure previously imported real_* samples are removed from GT to keep eval data separate from training
  find "$GT_DIR" -maxdepth 1 -type f -name 'real_*.*' -print0 | xargs -0 -r rm -f 2>/dev/null || true
fi

echo "🔧 Checking required tools..."
for tool in tesseract lstmtraining combine_tessdata unicharset_extractor combine_lang_model set_unicharset_properties ; do
  if ! command -v "$tool" >/dev/null 2>&1; then echo "❌ Missing tool: $tool"; exit 1; fi
done

# Locate lstm.train config (allow override via LSTM_TRAIN_CONFIG env)
CONFIG_LSTM="${LSTM_TRAIN_CONFIG:-}"
if [ -z "$CONFIG_LSTM" ]; then
  for c in \
    "/usr/share/tesseract-ocr/5/tessdata/configs/lstm.train" \
    "/usr/local/share/tessdata/configs/lstm.train" \
    "/usr/share/tesseract-ocr/4.00/tessdata/configs/lstm.train" \
    "$WORK_DIR/../tessdata/configs/lstm.train" \
    "$WORK_DIR/tessdata/configs/lstm.train" \
    "/mnt/c/tesseract/tessdata/configs/lstm.train"; do
    if [ -f "$c" ]; then CONFIG_LSTM="$c"; break; fi
  done
fi
if [ -z "$CONFIG_LSTM" ]; then
  echo "❌ Could not find lstm.train config in system tessdata nor repo's tessdata/configs"
  echo "   Checked:"
  echo "     - /usr/share/tesseract-ocr/5/tessdata/configs/lstm.train"
  echo "     - /usr/local/share/tessdata/configs/lstm.train"
  echo "     - /usr/share/tesseract-ocr/4.00/tessdata/configs/lstm.train"
  echo "     - $WORK_DIR/../tessdata/configs/lstm.train"
  echo "     - $WORK_DIR/tessdata/configs/lstm.train"
  echo "     - /mnt/c/tesseract/tessdata/configs/lstm.train"
  echo "   You can set LSTM_TRAIN_CONFIG to an explicit path and retry."
  exit 1
fi
echo "Using lstm.train config: $CONFIG_LSTM"

# Script assets dir (Arabic/Latin/Common.unicharset + radical-stroke.txt)
# Prefer pre-populated local assets under work/charsets if present, else download into tmp/script
DEFAULT_SCRIPT_DIR="$WORK_DIR/training_output/tmp/script"
LOCAL_CHARSETS_DIR="$WORK_DIR/charsets"

use_local_charsets=0
if [ -d "$LOCAL_CHARSETS_DIR" ] \
   && [ -s "$LOCAL_CHARSETS_DIR/Arabic.unicharset" ] \
   && [ -s "$LOCAL_CHARSETS_DIR/Latin.unicharset" ] \
   && [ -s "$LOCAL_CHARSETS_DIR/Common.unicharset" ]; then
  SCRIPT_DIR="$LOCAL_CHARSETS_DIR"
  use_local_charsets=1
else
  SCRIPT_DIR="$DEFAULT_SCRIPT_DIR"
  mkdir -p "$SCRIPT_DIR/ckb"
  fetch_asset() { # $1 dst, $2 url
    local dst="$1"; local url="$2"
    if [ ! -s "$dst" ]; then curl -fsSL -o "$dst" "$url" 2>/dev/null || return 1; fi
  }
  # Try langdata first, then fall back to langdata_lstm
  fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://raw.githubusercontent.com/tesseract-ocr/langdata/main/radical-stroke.txt" || \
  fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://raw.githubusercontent.com/tesseract-ocr/langdata/refs/heads/main/radical-stroke.txt" || \
  fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://github.com/tesseract-ocr/langdata/raw/main/radical-stroke.txt" || \
  fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/main/radical-stroke.txt" || \
  fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://github.com/tesseract-ocr/langdata_lstm/raw/main/radical-stroke.txt" || true
  for s in Arabic Latin Common; do
    # Prefer top-level files in langdata
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://raw.githubusercontent.com/tesseract-ocr/langdata/main/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://raw.githubusercontent.com/tesseract-ocr/langdata/refs/heads/main/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://github.com/tesseract-ocr/langdata/raw/main/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://cdn.jsdelivr.net/gh/tesseract-ocr/langdata@main/${s}.unicharset" || \
    # Legacy locations for compatibility
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://raw.githubusercontent.com/tesseract-ocr/langdata/main/script/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://github.com/tesseract-ocr/langdata/raw/main/script/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/main/script/${s}.unicharset" || \
    fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://github.com/tesseract-ocr/langdata_lstm/raw/main/script/${s}.unicharset" || true
  done
  # Seed local charsets for future runs (optional cache)
  mkdir -p "$LOCAL_CHARSETS_DIR" || true
  for s in Arabic Latin Common; do
    if [ -s "$SCRIPT_DIR/${s}.unicharset" ]; then
      cp -f "$SCRIPT_DIR/${s}.unicharset" "$LOCAL_CHARSETS_DIR/" 2>/dev/null || true
    fi
  done
  if [ -s "$SCRIPT_DIR/radical-stroke.txt" ]; then
    cp -f "$SCRIPT_DIR/radical-stroke.txt" "$LOCAL_CHARSETS_DIR/" 2>/dev/null || true
  fi
  echo "Seeded local charsets at: $LOCAL_CHARSETS_DIR (if downloads succeeded)"
fi
echo "Using script assets from: $SCRIPT_DIR (local=$use_local_charsets)"

# Prefer best tessdata for base models
export TESSDATA_PREFIX="$WIN_TESSDATA_BEST"
if ! ls "$WIN_TESSDATA_BEST"/*.traineddata >/dev/null 2>&1; then
  if ls "$TESSDATA_BEST_DIR"/*.traineddata >/dev/null 2>&1; then export TESSDATA_PREFIX="$TESSDATA_BEST_DIR"; else export TESSDATA_PREFIX="$TESSDATA_DIR"; fi
fi

echo "📦 Ensuring base models (fas, ara) are available..."
for lang in fas ara; do
  # 1) Prefer tessdata_best
  if [ ! -f "$WIN_TESSDATA_BEST/${lang}.traineddata" ] && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ]; then
    curl -fsSL -o "$WIN_TESSDATA_BEST/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/${lang}.traineddata" 2>/dev/null \
      || curl -fsSL -o "$WIN_TESSDATA_BEST/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata_best/raw/main/${lang}.traineddata" 2>/dev/null || true
  fi
  # 2) If best not available, try tessdata_fast
  if [ ! -s "$WIN_TESSDATA_BEST/${lang}.traineddata" ] && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ]; then
    curl -fsSL -o "$WIN_TESSDATA_FAST/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/${lang}.traineddata" 2>/dev/null \
      || curl -fsSL -o "$WIN_TESSDATA_FAST/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata_fast/raw/main/${lang}.traineddata" 2>/dev/null || true
  fi
  # 3) Additional fallback: only for 'fas', pull from tessdata (avoid known 404s for 'ara')
  if [ "$lang" = "fas" ] \
     && [ ! -s "$WIN_TESSDATA/${lang}.traineddata" ] \
     && [ ! -s "$WIN_TESSDATA_BEST/${lang}.traineddata" ] \
     && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ] \
     && [ ! -f "$TESSDATA_FAST_DIR/${lang}.traineddata" ]; then
    curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/${lang}.traineddata" 2>/dev/null \
      || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/${lang}.traineddata" 2>/dev/null || true
  fi
  # 4) Final fallback: try installing via apt to get system models
  if [ ! -f "$WIN_TESSDATA_BEST/${lang}.traineddata" ] && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ] \
     && [ ! -f "$WIN_TESSDATA/${lang}.traineddata" ] && [ ! -f "$TESSDATA_DIR/${lang}.traineddata" ] \
     && [ ! -f "$TESSDATA_FAST_DIR/${lang}.traineddata" ]; then
    if command -v apt-get >/dev/null 2>&1; then
      echo "ℹ️  Attempting to install tesseract-ocr-${lang} via apt..."
      sudo -n apt-get update >/dev/null 2>&1 || true
      sudo -n apt-get install -y "tesseract-ocr-${lang}" >/dev/null 2>&1 || true
    fi
  fi
done

have_model() { # returns path to model
  local l="$1"; for d in "$WIN_TESSDATA_BEST" "$TESSDATA_BEST_DIR" "$WIN_TESSDATA_FAST" "$TESSDATA_FAST_DIR" "$WIN_TESSDATA" "$TESSDATA_DIR"; do [ -f "$d/$l.traineddata" ] && { echo "$d/$l.traineddata"; return 0; }; done; return 1; }

fas_path=$(have_model fas || true)
ara_path=$(have_model ara || true)
BASE_LANGS=(); [ -n "$fas_path" ] && BASE_LANGS+=(fas); [ -n "$ara_path" ] && BASE_LANGS+=(ara)
# If Latin GT exists, try to include English as an auxiliary segmenter to better align Latin text lines
eng_path=$(have_model eng || true)
if [ -n "$eng_path" ]; then BASE_LANGS+=(eng); fi
if [ ${#BASE_LANGS[@]} -eq 0 ]; then echo "❌ No base models (fas/ara) found"; exit 1; fi
echo "Found bases: ${BASE_LANGS[*]}"

###
# Build or locate target traineddata early so we can use ckb for LSTMF generation as fallback
###
ensure_target_traineddata() {
  # Choose or build a ckb traineddata to provide unicharset/recoder
  local target=""
  # Allow forcing a minimal rebuild from GT regardless of existing ckb models
  local force_minimal="${FORCE_MINIMAL:-0}"
  if [ "$force_minimal" = "1" ]; then
    echo "FORCE_MINIMAL=1 requested; skipping existing ckb models and building minimal from GT..." 1>&2
  fi
  # 0) Highest priority: explicit custom override in repo root
  if [ "$force_minimal" != "1" ] && [ -f "$WIN_TESSDATA/ckb_custom.traineddata" ]; then target="$WIN_TESSDATA/ckb_custom.traineddata"; fi
  # 1) Next: repo root tessdata (if user dropped one there)
  if [ "$force_minimal" != "1" ] && [ -z "$target" ] && [ -f "$WIN_TESSDATA/ckb.traineddata" ]; then target="$WIN_TESSDATA/ckb.traineddata"; fi
  # 2) Prefer existing best/fast/system ckb models before building a minimal one
  if [ "$force_minimal" != "1" ] && [ -z "$target" ]; then
    for d in "$WIN_TESSDATA_BEST" "$TESSDATA_BEST_DIR" "$WIN_TESSDATA_FAST" "$TESSDATA_FAST_DIR" "$TESSDATA_DIR"; do
      if [ -f "$d/ckb.traineddata" ]; then target="$d/ckb.traineddata"; break; fi
    done
  fi
  if [ -n "$target" ] && combine_tessdata -d "$target" >/dev/null 2>&1; then echo "$target"; return 0; fi

  echo "� Building minimal $LANG.traineddata (unicharset + recoder) from GT..." 1>&2
  LNX_TMP_DIR="/tmp/tess_ckb_build"; rm -rf "$LNX_TMP_DIR"; mkdir -p "$LNX_TMP_DIR"
  rm -f "$LNX_TMP_DIR/unicharset" "$LNX_TMP_DIR/all.box"
  # Aggregate all .box files to avoid Arg list too long
  find "$GT_DIR" -maxdepth 1 -type f -name '*.box' -print0 | xargs -0 cat -- > "$LNX_TMP_DIR/all.box"
  if [ ! -s "$LNX_TMP_DIR/all.box" ]; then echo "❌ No .box files found in $GT_DIR"; return 1; fi
  # Extract unicharset in the temp folder to ensure predictable output path
  ( cd "$LNX_TMP_DIR" && unicharset_extractor "$LNX_TMP_DIR/all.box" )
  mv -f "$LNX_TMP_DIR/unicharset" "$LNX_TMP_DIR/unicharset" 2>/dev/null || true
  rm -f "$LNX_TMP_DIR/all.box"
  # Set properties using script_dir assets (best-effort)
  set_unicharset_properties -U "$LNX_TMP_DIR/unicharset" -O "$LNX_TMP_DIR/unicharset" --script_dir="$SCRIPT_DIR" || true
  # Build words list from corpus/GT and filter to allowed charset using Python
  cat /dev/null > "$LNX_TMP_DIR/words.raw"
  if [ -f "$WORK_DIR/corpus/ckb.training_text" ]; then cat "$WORK_DIR/corpus/ckb.training_text" >> "$LNX_TMP_DIR/words.raw"; fi
  if [ -f "$WORK_DIR/corpus/ckb.training_text.final" ]; then cat "$WORK_DIR/corpus/ckb.training_text.final" >> "$LNX_TMP_DIR/words.raw"; fi
  cat "$GT_DIR"/*.gt.txt 2>/dev/null >> "$LNX_TMP_DIR/words.raw" || true
  python3 - "$LNX_TMP_DIR" << 'PY'
import sys, re, os
tmp=sys.argv[1]
u=os.path.join(tmp,'unicharset')
allowed=set()
with open(u,'r',encoding='utf-8',errors='ignore') as f:
    lines=f.read().splitlines()
for i,l in enumerate(lines):
    if i==0: continue
    ch=l.split(' ')[0]
    if ch!='NULL':
        allowed.add(ch)
def ok(word):
    return all(c in allowed for c in word)
wr=os.path.join(tmp,'words.raw')
out=os.path.join(tmp,'words.txt')
freq=os.path.join(tmp,'freq_words.txt')
counts={}
with open(wr,'r',encoding='utf-8',errors='ignore') as f:
  for token in re.split(r"\s+", f.read()):
    t=token.strip()
    if not t: continue
    if not ok(t): continue
    counts[t]=counts.get(t,0)+1
with open(out,'w',encoding='utf-8') as g:
  for t in counts.keys():
    g.write(t+"\n")
with open(freq,'w',encoding='utf-8') as g:
  for t,c in sorted(counts.items(), key=lambda kv:(-kv[1], kv[0])):
    g.write(t+"\n")
if os.path.getsize(out)==0:
  with open(out,'w',encoding='utf-8') as g:
    g.write("کورد\nکوردی\nدەنگ\n")
PY
  # Numbers and punctuation filtered to allowed charset to prevent DAWG build errors
  python3 - "$LNX_TMP_DIR" << 'PY'
import os, sys
tmp=sys.argv[1]
u=os.path.join(tmp,'unicharset')
allowed=set()
with open(u,'r',encoding='utf-8',errors='ignore') as f:
    for i,l in enumerate(f.read().splitlines()):
        if i==0: continue
        ch=l.split(' ')[0]
        if ch!='NULL': allowed.add(ch)
arabic_digits="٠١٢٣٤٥٦٧٨٩"
ascii_digits="0123456789"
base_puncs="،؛:؟«»-()٪"
extra=os.environ.get('PUNCS_EXTRA','')
digits=arabic_digits+(ascii_digits if os.environ.get('LATIN_DIGITS','0')=='1' else '')
nums=[c for c in digits if c in allowed]
puncs=[c for c in (base_puncs+extra) if c in allowed]
with open(os.path.join(tmp,'numbers.txt'),'w',encoding='utf-8') as f:
    if nums:
        f.write(''.join(sorted(set(nums), key=nums.index))+'\n')
with open(os.path.join(tmp,'puncs.txt'),'w',encoding='utf-8') as f:
  # Ensure non-empty puncs list for combine_lang_model; fallback to a minimal Arabic punctuation set
  if puncs:
    f.write(''.join(sorted(set(puncs), key=puncs.index))+'\n')
  else:
    f.write('،٪؛\n')
PY
  # Combine to traineddata (use frequency DAWGs if available)
  NUMBERS_OPT=""; [ -s "$LNX_TMP_DIR/numbers.txt" ] && NUMBERS_OPT="--numbers $LNX_TMP_DIR/numbers.txt"
  PUNCS_OPT=""; [ -s "$LNX_TMP_DIR/puncs.txt" ] && PUNCS_OPT="--puncs $LNX_TMP_DIR/puncs.txt"
  combine_lang_model \
    --input_unicharset "$LNX_TMP_DIR/unicharset" \
    --output_dir "$LNX_TMP_DIR" \
    --script_dir "$SCRIPT_DIR" \
    --lang "$LANG" \
    --lang_is_rtl \
    --pass_through_recoder \
    --version_str ckb_minimal \
    --words "$LNX_TMP_DIR/words.txt" \
    ${NUMBERS_OPT} \
    ${PUNCS_OPT} \
    $( [ -s "$LNX_TMP_DIR/freq_words.txt" ] && echo --freq_input "$LNX_TMP_DIR/freq_words.txt" ) || true
  # Handle outputs written either directly to output_dir or inside a lang subfolder
  if [ -f "$LNX_TMP_DIR/$LANG.traineddata" ]; then
    echo "$LNX_TMP_DIR/$LANG.traineddata"; return 0
  fi
  if [ -f "$LNX_TMP_DIR/$LANG/$LANG.traineddata" ]; then
    cp -f "$LNX_TMP_DIR/$LANG/$LANG.traineddata" "$LNX_TMP_DIR/$LANG.traineddata" 2>/dev/null || true
    echo "$LNX_TMP_DIR/$LANG.traineddata"; return 0
  fi
  echo "❌ Failed to build minimal $LANG.traineddata"; return 1
}

TARGET_TRAINEDDATA="$(ensure_target_traineddata)" || { echo "❌ No target traineddata available"; exit 1; }
echo "Using target traineddata: $TARGET_TRAINEDDATA"

echo "�🧩 Generating .lstmf files (hybrid seg: ${BASE_LANGS[*]} + ckb-fallback)..."
LSTMF_LOG="$OUT_DIR/lstmf_build.log"; : > "$LSTMF_LOG"
# Allow OEM/PSM overrides via env (defaults align with earlier behavior)
OEM="${OEM:-1}"
PSM="${PSM:-6}"

# Detect number of CPU cores for parallel processing
NUM_CORES=$(nproc 2>/dev/null || echo 8)
PARALLEL_JOBS=$((NUM_CORES > 4 ? NUM_CORES - 2 : NUM_CORES))  # Use NUM_CORES-2 for system responsiveness

cd "$GT_DIR"
# Normalize ground-truth text filenames: prefer .gt.txt; if only .txt exists, create .gt.txt copies
while IFS= read -r -d '' tif_norm; do
  b=$(basename "$tif_norm" .tif)
  if [ ! -f "$GT_DIR/$b.gt.txt" ] && [ -f "$GT_DIR/$b.txt" ]; then
    cp -f "$GT_DIR/$b.txt" "$GT_DIR/$b.gt.txt"
  fi
done < <(find "$GT_DIR" -maxdepth 1 -type f -name '*.tif' -print0)

# Function to process a single TIF file - OPTIMIZED
process_lstmf() {
    local tif="$1"
    local slot="${2:-?}"  # Worker slot number from parallel
    local base=$(basename "$tif" .tif)
    local work_dir=$(dirname "$tif")  # Auto-detect working directory
    
    # PERFORMANCE BOOST 1: Early exit with single file check (no ls glob)
    # Check only the most likely file (fas) first for speed
    [ -f "$TMP_DIR/$base-fas.lstmf" ] && { echo "C"; return 0; }
    [ -f "$TMP_DIR/$base-ara.lstmf" ] && { echo "C"; return 0; }
    [ -f "$TMP_DIR/$base-eng.lstmf" ] && { echo "C"; return 0; }
    
    local gt_txt="$work_dir/$base.gt.txt"
    [ -f "$gt_txt" ] || return 1
    
    # PERFORMANCE BOOST 2: Direct file check instead of case statement
    # Try fas first (best accuracy, most likely to succeed)
    if [ -f "$fas_path" ]; then
        cp -f "$gt_txt" "$work_dir/$base-fas.gt.txt" 2>/dev/null && \
        OMP_THREAD_LIMIT=1 tesseract --tessdata-dir "$(dirname "$fas_path")" "$tif" "$work_dir/$base-fas" \
            -l fas --oem "$OEM" --psm "$PSM" "$CONFIG_LSTM" 2>/dev/null && \
        [ -f "$work_dir/$base-fas.lstmf" ] && {
            mv -f "$work_dir/$base-fas.lstmf" "$TMP_DIR/" 2>/dev/null
            rm -f "$work_dir/$base-fas.gt.txt" 2>/dev/null
            echo "S"
            return 0
        }
        rm -f "$work_dir/$base-fas.gt.txt" 2>/dev/null
    fi
    
    # Try ara as fallback
    if [ -f "$ara_path" ]; then
        cp -f "$gt_txt" "$work_dir/$base-ara.gt.txt" 2>/dev/null && \
        OMP_THREAD_LIMIT=1 tesseract --tessdata-dir "$(dirname "$ara_path")" "$tif" "$work_dir/$base-ara" \
            -l ara --oem "$OEM" --psm "$PSM" "$CONFIG_LSTM" 2>/dev/null && \
        [ -f "$work_dir/$base-ara.lstmf" ] && {
            mv -f "$work_dir/$base-ara.lstmf" "$TMP_DIR/" 2>/dev/null
            rm -f "$work_dir/$base-ara.gt.txt" 2>/dev/null
            echo "S"
            return 0
        }
        rm -f "$work_dir/$base-ara.gt.txt" 2>/dev/null
    fi
    
    # Try eng as last resort
    if [ -f "$eng_path" ]; then
        cp -f "$gt_txt" "$work_dir/$base-eng.gt.txt" 2>/dev/null && \
        OMP_THREAD_LIMIT=1 tesseract --tessdata-dir "$(dirname "$eng_path")" "$tif" "$work_dir/$base-eng" \
            -l eng --oem "$OEM" --psm "$PSM" "$CONFIG_LSTM" 2>/dev/null && \
        [ -f "$work_dir/$base-eng.lstmf" ] && {
            mv -f "$work_dir/$base-eng.lstmf" "$TMP_DIR/" 2>/dev/null
            rm -f "$work_dir/$base-eng.gt.txt" 2>/dev/null
            echo "S"
            return 0
        }
        rm -f "$work_dir/$base-eng.gt.txt" 2>/dev/null
    fi
    
    return 1
}

export -f process_lstmf
export GT_DIR TMP_DIR CONFIG_LSTM OEM PSM
export fas_path ara_path eng_path TARGET_TRAINEDDATA CKB_MODEL_DIR

# PERFORMANCE BOOST 3: Disable tesseract debug output globally
export TESSERACT_STDOUT_QUIET=1
export TESSERACT_STDERR_QUIET=1
export SEG_LANGS="${BASE_LANGS[*]}"  # Export as space-separated string

# Check if GNU Parallel is available
if command -v parallel >/dev/null 2>&1; then
    echo "🚀 Using parallel processing with $PARALLEL_JOBS workers..."
    
    # Verify ground truth directory is accessible
    if [ ! -d "$GT_DIR" ]; then
        echo "❌ Ground truth directory not accessible: $GT_DIR"
        exit 1
    fi
    
    cd "$GT_DIR" || { echo "❌ Cannot cd to $GT_DIR"; exit 1; }
    
    # Set locale to avoid perl warnings
    export LC_ALL=C
    export LANGUAGE=en_US.UTF-8
    
    # Check for already-processed files (resume capability)
    EXISTING_LSTMF=$(find "$TMP_DIR" -name '*.lstmf' -type f 2>/dev/null | wc -l)
    if [ "$EXISTING_LSTMF" -gt 0 ]; then
        echo "� Found $EXISTING_LSTMF existing LSTMF files - will skip regenerating"
    fi
    
    echo "📊 Processing TIF files..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    START_TIME=$(date +%s)
    
    # Background progress monitor
    (
        sleep 10
        while sleep 5; do
            CURRENT=$(find "$TMP_DIR" -name '*.lstmf' -type f 2>/dev/null | wc -l)
            [ "$CURRENT" -eq 0 ] && continue
            
            ELAPSED=$(($(date +%s) - START_TIME))
            RATE=$((ELAPSED > 10 ? CURRENT * 60 / ELAPSED : 0))
            
            printf "\r⏳ Generated: %d LSTMF files | Speed: %d/min | Time: %dm%ds        " \
                "$CURRENT" "$RATE" "$((ELAPSED/60))" "$((ELAPSED%60))"
        done
    ) &
    PROGRESS_PID=$!
    
    # Simple parallel processing - tried and tested approach
    find "$GT_DIR" -maxdepth 1 -name '*.tif' -type f -print 2>/dev/null | \
        parallel -j "$PARALLEL_JOBS" --will-cite --line-buffer \
            "process_lstmf {} {%}" 2>/dev/null | grep -c "^S" || true
    
    # Stop progress monitor
    kill $PROGRESS_PID 2>/dev/null
    wait $PROGRESS_PID 2>/dev/null
    
    # Final count
    FINAL_COUNT=$(find "$TMP_DIR" -name '*.lstmf' -type f 2>/dev/null | wc -l)
    
    END_TIME=$(date +%s)
    ELAPSED=$((END_TIME - START_TIME))
    MINUTES=$((ELAPSED / 60))
    SECONDS=$((ELAPSED % 60))
    
    echo ""
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ LSTMF Generation Complete!"
    echo "   Files processed: $FINAL_COUNT"
    echo "   Time elapsed: ${MINUTES}m ${SECONDS}s"
    if [ "$ELAPSED" -gt 0 ]; then
        echo "   Average speed: $((FINAL_COUNT * 60 / ELAPSED)) files/min"
    fi
    
    LSTMF_COUNT=$FINAL_COUNT
else
    echo "⚠️  GNU Parallel not found, using sequential processing..."
    LSTMF_COUNT=0
    SEG_LANGS=("${BASE_LANGS[@]}")
    # If we have a target ckb traineddata, also try a ckb segmenter which has the exact recoder we need
    if [ -f "$TARGET_TRAINEDDATA" ]; then SEG_LANGS+=(ckb); fi
    CKB_MODEL_DIR=$(dirname "$TARGET_TRAINEDDATA")
    while IFS= read -r -d '' tif; do
      base=$(basename "$tif" .tif)
      gt_txt="$GT_DIR/$base.gt.txt"
      [ -f "$gt_txt" ] || { echo "⚠️  Missing $base.gt.txt"; continue; }
      for B in "${SEG_LANGS[@]}"; do
        MODEL_PATH=""; MODEL_DIR=""
        case "$B" in
          fas) MODEL_PATH="$fas_path"; MODEL_DIR=$(dirname "$MODEL_PATH");;
          ara) MODEL_PATH="$ara_path"; MODEL_DIR=$(dirname "$MODEL_PATH");;
          eng) MODEL_PATH="$eng_path"; MODEL_DIR=$(dirname "$MODEL_PATH");;
          ckb) MODEL_PATH="$TARGET_TRAINEDDATA"; MODEL_DIR="$CKB_MODEL_DIR";;
        esac
        [ -n "$MODEL_DIR" ] || continue
        # Ensure matching GT for suffixed output base
        cp -f "$gt_txt" "$GT_DIR/$base-$B.gt.txt"
        echo "Creating LSTMF: $base (seg=$B)"
        {
          echo "---- $(date -Iseconds) : $base (seg=$B) ----"
          echo "CMD: tesseract --tessdata-dir '$MODEL_DIR' '$tif' '$base-$B' -l '$B' --oem $OEM --psm $PSM '$CONFIG_LSTM'"
          tesseract --tessdata-dir "$MODEL_DIR" "$tif" "$base-$B" -l "$B" --oem "$OEM" --psm "$PSM" "$CONFIG_LSTM" 2>&1 || true
        } >> "$LSTMF_LOG"
        if [ -f "$GT_DIR/$base-$B.lstmf" ]; then mv -f "$GT_DIR/$base-$B.lstmf" "$TMP_DIR/"; LSTMF_COUNT=$((LSTMF_COUNT+1)); break; else echo "⚠️  Missing $base-$B.lstmf"; fi
        rm -f "$GT_DIR/$base-$B.gt.txt" 2>/dev/null || true
      done
    done < <(find "$GT_DIR" -maxdepth 1 -type f -name '*.tif' -print0)
fi

[ "$LSTMF_COUNT" -gt 0 ] || { echo "❌ No .lstmf generated. See log: $LSTMF_LOG"; exit 1; }
echo "✅ Generated $LSTMF_COUNT .lstmf files"

echo "🗂️  Preparing listfiles..."
cd "$TMP_DIR"
# Create list of files and shuffle to avoid font-bias in train/eval split
find . -maxdepth 1 -type f -name '*.lstmf' -printf '%f\n' | sed 's/^\.\///' > list.all
if command -v shuf >/dev/null 2>&1; then
  shuf list.all -o list.all
else
  # Busybox/alternative fallback
  sort -R list.all -o list.all 2>/dev/null || cat list.all > list.all
fi
TOTAL=$(wc -l < list.all | tr -d ' ')
if [ "$TOTAL" -le 1 ]; then
  cp list.all list.train
  cp list.all list.eval
else
  TRAIN_COUNT=$(( (TOTAL*9 + 9)/10 ))
  head -n "$TRAIN_COUNT" list.all > list.train
  tail -n +$((TRAIN_COUNT+1)) list.all > list.eval
fi
EVAL_COUNT=$(wc -l < list.eval | tr -d ' ')

ensure_target_traineddata_legacy() {
  # Choose or build a ckb traineddata to provide unicharset/recoder
  local target=""
  # Allow forcing a minimal rebuild from GT regardless of existing ckb models
  local force_minimal="${FORCE_MINIMAL:-0}"
  if [ "$force_minimal" = "1" ]; then
    echo "FORCE_MINIMAL=1 requested; skipping existing ckb models and building minimal from GT..." 1>&2
  fi
  # 0) Highest priority: explicit custom override in repo root
  if [ "$force_minimal" != "1" ] && [ -f "$WIN_TESSDATA/ckb_custom.traineddata" ]; then target="$WIN_TESSDATA/ckb_custom.traineddata"; fi
  # 1) Next: repo root tessdata (if user dropped one there)
  if [ "$force_minimal" != "1" ] && [ -z "$target" ] && [ -f "$WIN_TESSDATA/ckb.traineddata" ]; then target="$WIN_TESSDATA/ckb.traineddata"; fi
  # 2) Prefer existing best/fast/system ckb models before building a minimal one
  if [ "$force_minimal" != "1" ] && [ -z "$target" ]; then
    for d in "$WIN_TESSDATA_BEST" "$TESSDATA_BEST_DIR" "$WIN_TESSDATA_FAST" "$TESSDATA_FAST_DIR" "$TESSDATA_DIR"; do
      if [ -f "$d/ckb.traineddata" ]; then target="$d/ckb.traineddata"; break; fi
    done
  fi
  if [ -n "$target" ] && combine_tessdata -d "$target" >/dev/null 2>&1; then echo "$target"; return 0; fi

  echo "🧪 Building minimal $LANG.traineddata (unicharset + recoder) from GT..." 1>&2
  LNX_TMP_DIR="/tmp/tess_ckb_build"; rm -rf "$LNX_TMP_DIR"; mkdir -p "$LNX_TMP_DIR"
  rm -f "$LNX_TMP_DIR/unicharset" "$LNX_TMP_DIR/all.box"
  # Aggregate all .box files to avoid Arg list too long
  find "$GT_DIR" -maxdepth 1 -type f -name '*.box' -print0 | xargs -0 cat -- > "$LNX_TMP_DIR/all.box"
  if [ ! -s "$LNX_TMP_DIR/all.box" ]; then echo "❌ No .box files found in $GT_DIR"; return 1; fi
  # Extract unicharset in the temp folder to ensure predictable output path
  ( cd "$LNX_TMP_DIR" && unicharset_extractor "$LNX_TMP_DIR/all.box" )
  mv -f "$LNX_TMP_DIR/unicharset" "$LNX_TMP_DIR/unicharset" 2>/dev/null || true
  rm -f "$LNX_TMP_DIR/all.box"
  # Set properties using script_dir assets (best-effort)
  set_unicharset_properties -U "$LNX_TMP_DIR/unicharset" -O "$LNX_TMP_DIR/unicharset" --script_dir="$SCRIPT_DIR" || true
  # Build words list from corpus/GT and filter to allowed charset using Python
  cat /dev/null > "$LNX_TMP_DIR/words.raw"
  if [ -f "$WORK_DIR/corpus/ckb.training_text" ]; then cat "$WORK_DIR/corpus/ckb.training_text" >> "$LNX_TMP_DIR/words.raw"; fi
  if [ -f "$WORK_DIR/corpus/ckb.training_text.final" ]; then cat "$WORK_DIR/corpus/ckb.training_text.final" >> "$LNX_TMP_DIR/words.raw"; fi
  cat "$GT_DIR"/*.gt.txt 2>/dev/null >> "$LNX_TMP_DIR/words.raw" || true
  python3 - "$LNX_TMP_DIR" << 'PY'
import sys, re, os
tmp=sys.argv[1]
u=os.path.join(tmp,'unicharset')
allowed=set()
with open(u,'r',encoding='utf-8',errors='ignore') as f:
    lines=f.read().splitlines()
for i,l in enumerate(lines):
    if i==0: continue
    ch=l.split(' ')[0]
    if ch!='NULL':
        allowed.add(ch)
def ok(word):
    return all(c in allowed for c in word)
wr=os.path.join(tmp,'words.raw')
out=os.path.join(tmp,'words.txt')
freq=os.path.join(tmp,'freq_words.txt')
counts={}
with open(wr,'r',encoding='utf-8',errors='ignore') as f:
  for token in re.split(r"\\s+", f.read()):
    t=token.strip()
    if not t: continue
    if not ok(t): continue
    counts[t]=counts.get(t,0)+1
with open(out,'w',encoding='utf-8') as g:
  for t in counts.keys():
    g.write(t+"\n")
with open(freq,'w',encoding='utf-8') as g:
  for t,c in sorted(counts.items(), key=lambda kv:(-kv[1], kv[0])):
    g.write(t+"\n")
if os.path.getsize(out)==0:
  with open(out,'w',encoding='utf-8') as g:
    g.write("کورد\nکوردی\nدەنگ\n")
PY
  # Numbers and punctuation filtered to allowed charset to prevent DAWG build errors
  python3 - "$LNX_TMP_DIR" << 'PY'
import os, sys
tmp=sys.argv[1]
u=os.path.join(tmp,'unicharset')
allowed=set()
with open(u,'r',encoding='utf-8',errors='ignore') as f:
    for i,l in enumerate(f.read().splitlines()):
        if i==0: continue
        ch=l.split(' ')[0]
        if ch!='NULL': allowed.add(ch)
arabic_digits="٠١٢٣٤٥٦٧٨٩"
ascii_digits="0123456789"
base_puncs="،؛:؟«»-()٪"
extra=os.environ.get('PUNCS_EXTRA','')
digits=arabic_digits+(ascii_digits if os.environ.get('LATIN_DIGITS','0')=='1' else '')
nums=[c for c in digits if c in allowed]
puncs=[c for c in (base_puncs+extra) if c in allowed]
with open(os.path.join(tmp,'numbers.txt'),'w',encoding='utf-8') as f:
    if nums:
        f.write(''.join(sorted(set(nums), key=nums.index))+'\n')
with open(os.path.join(tmp,'puncs.txt'),'w',encoding='utf-8') as f:
  # Ensure non-empty puncs list for combine_lang_model; fallback to a minimal Arabic punctuation set
  if puncs:
    f.write(''.join(sorted(set(puncs), key=puncs.index))+'\n')
  else:
    f.write('،٪؛\n')
PY
  # Combine to traineddata (use frequency DAWGs if available)
  NUMBERS_OPT=""; [ -s "$LNX_TMP_DIR/numbers.txt" ] && NUMBERS_OPT="--numbers $LNX_TMP_DIR/numbers.txt"
  PUNCS_OPT=""; [ -s "$LNX_TMP_DIR/puncs.txt" ] && PUNCS_OPT="--puncs $LNX_TMP_DIR/puncs.txt"
  combine_lang_model \
    --input_unicharset "$LNX_TMP_DIR/unicharset" \
    --output_dir "$LNX_TMP_DIR" \
    --script_dir "$SCRIPT_DIR" \
    --lang "$LANG" \
    --lang_is_rtl \
    --pass_through_recoder \
    --version_str ckb_minimal \
    --words "$LNX_TMP_DIR/words.txt" \
    ${NUMBERS_OPT} \
    ${PUNCS_OPT} \
    $( [ -s "$LNX_TMP_DIR/freq_words.txt" ] && echo --freq_input "$LNX_TMP_DIR/freq_words.txt" ) || true
  # Handle outputs written either directly to output_dir or inside a lang subfolder
  if [ -f "$LNX_TMP_DIR/$LANG.traineddata" ]; then
    echo "$LNX_TMP_DIR/$LANG.traineddata"; return 0
  fi
  if [ -f "$LNX_TMP_DIR/$LANG/$LANG.traineddata" ]; then
    cp -f "$LNX_TMP_DIR/$LANG/$LANG.traineddata" "$LNX_TMP_DIR/$LANG.traineddata" 2>/dev/null || true
    echo "$LNX_TMP_DIR/$LANG.traineddata"; return 0
  fi
  echo "❌ Failed to build minimal $LANG.traineddata"; return 1
}

for START_BASE in "${BASE_LANGS[@]}"; do
  echo "🔨 Extracting starter LSTM from $START_BASE.traineddata..."
  MODEL_PATH=""; [ "$START_BASE" = fas ] && MODEL_PATH="$fas_path" || MODEL_PATH="$ara_path"
  if ! combine_tessdata -e "$MODEL_PATH" "$TMP_DIR/$START_BASE.lstm" >/dev/null 2>&1; then
    echo "⚠️  $START_BASE model at $MODEL_PATH is likely a fast (integer) model and cannot be used for continue training. Skipping $START_BASE base."
    continue
  fi
  echo "🏃 Fine-tuning from $START_BASE..."
  MODEL_PREFIX="$OUT_DIR/${LANG}_from_${START_BASE}"
  lstmtraining \
    --continue_from "$TMP_DIR/$START_BASE.lstm" \
    --old_traineddata "$MODEL_PATH" \
    --traineddata "$TARGET_TRAINEDDATA" \
    --model_output "$MODEL_PREFIX" \
    --train_listfile "$TMP_DIR/list.train" \
    --eval_listfile "$TMP_DIR/list.eval" \
    --max_iterations "$MAX_ITERS" \
    --debug_interval "$DEBUG_INTERVAL" ${TRAINING_EXTRA_ARGS:-} || true
  CHECKPOINT=$(ls -t "${MODEL_PREFIX}"_checkpoint* 2>/dev/null | head -1 || true)
  [ -z "${CHECKPOINT:-}" ] && [ -f "${MODEL_PREFIX}_checkpoint" ] && CHECKPOINT="${MODEL_PREFIX}_checkpoint"
  if [ -z "${CHECKPOINT:-}" ]; then echo "❌ No checkpoint produced for $START_BASE"; continue; fi
  echo "✅ Using checkpoint: $(basename "$CHECKPOINT")"
  echo "🧱 Finalizing traineddata for $START_BASE (best + fast)..."
  # Best (float) variant
  lstmtraining --stop_training --continue_from "$CHECKPOINT" --traineddata "$TARGET_TRAINEDDATA" --model_output "$OUT_DIR/${LANG}_from_${START_BASE}.traineddata" || true
  if [ -f "$OUT_DIR/${LANG}_from_${START_BASE}.traineddata" ]; then echo "✅ Created (best): $OUT_DIR/${LANG}_from_${START_BASE}.traineddata"; fi
  # Fast (int8) variant
  lstmtraining --stop_training --continue_from "$CHECKPOINT" --traineddata "$TARGET_TRAINEDDATA" --model_output "$OUT_DIR/${LANG}_from_${START_BASE}_fast.traineddata" --convert_to_int || true
  if [ -f "$OUT_DIR/${LANG}_from_${START_BASE}_fast.traineddata" ]; then echo "✅ Created (fast): $OUT_DIR/${LANG}_from_${START_BASE}_fast.traineddata"; fi
done

# Evaluate models using lstmeval if available and install the better one
eval_checkpoint_cer() {
  # $1 checkpoint
  local ckpt="$1"
  local cer=""
  if command -v lstmeval >/dev/null 2>&1; then
    local logf="$OUT_DIR/eval_$(basename "$ckpt").log"
    lstmeval --model "$ckpt" --traineddata "$TARGET_TRAINEDDATA" --eval_listfile "$TMP_DIR/list.eval" 2>&1 | tee "$logf" >/dev/null || true
    cer=$(grep -Eo 'Character Error Rate[:=][[:space:]]*[0-9]*\.[0-9]+' "$logf" | tail -1 | grep -Eo '[0-9]*\.[0-9]+' || true)
  fi
  echo "$cer"
}

pick_and_install() {
  local fas_best="$OUT_DIR/${LANG}_from_fas.traineddata"
  local fas_fast="$OUT_DIR/${LANG}_from_fas_fast.traineddata"
  local ara_best="$OUT_DIR/${LANG}_from_ara.traineddata"
  local ara_fast="$OUT_DIR/${LANG}_from_ara_fast.traineddata"
  local fas_ckpt="" ara_ckpt="" fas_cer="" ara_cer=""

  fas_ckpt=$(ls -t "$OUT_DIR/${LANG}_from_fas"_checkpoint* 2>/dev/null | head -1 || true)
  ara_ckpt=$(ls -t "$OUT_DIR/${LANG}_from_ara"_checkpoint* 2>/dev/null | head -1 || true)

  # Metrics CSV
  local metrics_csv="$OUT_DIR/metrics.csv"
  if [ ! -f "$metrics_csv" ]; then
    echo "timestamp,base,checkpoint,cer,max_iters,debug_interval,train_count,eval_count,total_lstmf" > "$metrics_csv"
  fi

  if [ -n "${fas_ckpt:-}" ]; then
    fas_cer=$(eval_checkpoint_cer "$fas_ckpt" || true)
    echo "$(date -Iseconds),fas,$(basename "$fas_ckpt"),${fas_cer:-},$MAX_ITERS,$DEBUG_INTERVAL,$TRAIN_COUNT,${EVAL_COUNT:-},$TOTAL" >> "$metrics_csv"
  fi
  if [ -n "${ara_ckpt:-}" ]; then
    ara_cer=$(eval_checkpoint_cer "$ara_ckpt" || true)
    echo "$(date -Iseconds),ara,$(basename "$ara_ckpt"),${ara_cer:-},$MAX_ITERS,$DEBUG_INTERVAL,$TRAIN_COUNT,${EVAL_COUNT:-},$TOTAL" >> "$metrics_csv"
  fi

  local preferred_base=""
  if [ -n "${fas_cer:-}" ] && [ -n "${ara_cer:-}" ]; then
    if awk "BEGIN{exit !($fas_cer < $ara_cer)}"; then preferred_base="fas"; else preferred_base="ara"; fi
  elif [ -f "$fas_best" ] && [ ! -f "$ara_best" ]; then
    preferred_base="fas"
  elif [ -f "$ara_best" ] && [ ! -f "$fas_best" ]; then
    preferred_base="ara"
  elif [ -f "$fas_best" ]; then
    preferred_base="fas"
  elif [ -f "$ara_best" ]; then
    preferred_base="ara"
  fi

  if [ -n "${preferred_base:-}" ]; then
    local preferred_best preferred_fast
    if [ "$preferred_base" = "fas" ]; then
      preferred_best="$fas_best"; preferred_fast="$fas_fast"
    else
      preferred_best="$ara_best"; preferred_fast="$ara_fast"
    fi
    # Write standardized outputs in OUT_DIR
    if [ -f "$preferred_best" ]; then cp -f "$preferred_best" "$OUT_DIR/${LANG}.best.traineddata" 2>/dev/null || true; fi
    if [ -f "$preferred_fast" ]; then cp -f "$preferred_fast" "$OUT_DIR/${LANG}.fast.traineddata" 2>/dev/null || true; fi

    # Install: best -> tessdata_best, fast -> tessdata_fast (keep folders separate)
    if [ -f "$preferred_best" ]; then cp -f "$preferred_best" "$WIN_TESSDATA_BEST/ckb.traineddata" 2>/dev/null || true; fi
    if [ -f "$preferred_fast" ]; then cp -f "$preferred_fast" "$WIN_TESSDATA_FAST/ckb.traineddata" 2>/dev/null || true; fi
    echo "✅ Installed:"
  echo "   best -> C:\\tesseract\\tessdata\\best\\ckb.traineddata"
  if [ -f "$preferred_fast" ]; then echo "   fast -> C:\\tesseract\\tessdata\\fast\\ckb.traineddata"; else echo "   fast -> (not produced)"; fi
    return 0
  fi
  return 1
}

if ! pick_and_install; then
  echo "❌ No trained model finalized"
  exit 1
fi

