#!/bin/bash

# Execute LSTM fine-tuning from generated ground-truth to produce ckb.traineddata
# Flow: generate .lstmf (hybrid fas+ara seg), choose/build target ckb traineddata, fine-tune from fas and ara, finalize and install.

set -euo pipefail

WORK_DIR="/mnt/c/tesseract/work"
GT_DIR="$WORK_DIR/training_output/ground_truth"
TMP_DIR="$WORK_DIR/training_output/tmp"
OUT_DIR="$WORK_DIR/training_output/model"
LANG="ckb"

mkdir -p "$TMP_DIR" "$OUT_DIR"
# Resolve ground truth directory with fallbacks if default is missing
if [ ! -d "$GT_DIR" ]; then
  for cand in \
    "$WORK_DIR/ground-truth" \
    "$WORK_DIR/ground-truth-robust" \
    "$WORK_DIR/ground-truth-system" \
    "$WORK_DIR/ground-truth-final" \
    "$WORK_DIR/ground-truth-workaround" \
    "$WORK_DIR/ground-truth-corpus"; do
    if [ -d "$cand" ]; then GT_DIR="$cand"; break; fi
  done
fi
if [ ! -d "$GT_DIR" ]; then
  echo "⚠️  Ground truth not found. Attempting to generate using generate_ckb_training_data.sh..."
  if [ -f "$WORK_DIR/generate_ckb_training_data.sh" ]; then
    chmod +x "$WORK_DIR/generate_ckb_training_data.sh" || true
    ( cd "$WORK_DIR" && "$WORK_DIR/generate_ckb_training_data.sh" ) || true
    GT_DIR="$WORK_DIR/training_output/ground_truth"
  fi
fi
if [ ! -d "$GT_DIR" ]; then echo "❌ Ground truth not found. Expected at $WORK_DIR/training_output/ground_truth or a ground-truth* folder."; exit 1; fi

# Tesseract data dirs
TESSDATA_DIR="/usr/share/tesseract-ocr/5/tessdata"
TESSDATA_BEST_DIR="/usr/share/tesseract-ocr/5/tessdata_best"
TESSDATA_FAST_DIR="/usr/share/tesseract-ocr/5/tessdata_fast"
if [ ! -d "$TESSDATA_DIR" ]; then TESSDATA_DIR="/usr/share/tesseract-ocr/4.00/tessdata"; fi
if [ ! -d "$TESSDATA_BEST_DIR" ]; then TESSDATA_BEST_DIR="/usr/share/tesseract-ocr/4.00/tessdata_best"; fi
if [ ! -d "$TESSDATA_FAST_DIR" ]; then TESSDATA_FAST_DIR="/usr/share/tesseract-ocr/4.00/tessdata_fast"; fi

WIN_TESSDATA="/mnt/c/tesseract/tessdata"
WIN_TESSDATA_BEST="/mnt/c/tesseract/tessdata_best"
mkdir -p "$WIN_TESSDATA_BEST" || true

echo "🔧 Checking required tools..."
for tool in tesseract lstmtraining combine_tessdata unicharset_extractor combine_lang_model set_unicharset_properties ; do
  if ! command -v "$tool" >/dev/null 2>&1; then echo "❌ Missing tool: $tool"; exit 1; fi
done

# Locate lstm.train config
CONFIG_LSTM=""
for c in \
  "/usr/share/tesseract-ocr/5/tessdata/configs/lstm.train" \
  "/usr/local/share/tessdata/configs/lstm.train" \
  "/usr/share/tesseract-ocr/4.00/tessdata/configs/lstm.train"; do
  if [ -f "$c" ]; then CONFIG_LSTM="$c"; break; fi
done
if [ -z "$CONFIG_LSTM" ]; then echo "❌ Could not find lstm.train config"; exit 1; fi

# Script assets dir (Arabic/Latin/Common.unicharset + radical-stroke.txt)
SCRIPT_DIR="$WORK_DIR/training_output/tmp/script"
mkdir -p "$SCRIPT_DIR/ckb"
fetch_asset() { # $1 url
  local dst="$1"; local url="$2"
  if [ ! -s "$dst" ]; then curl -fsSL -o "$dst" "$url" || return 1; fi
}
fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/main/radical-stroke.txt" || \
fetch_asset "$SCRIPT_DIR/radical-stroke.txt" "https://github.com/tesseract-ocr/langdata_lstm/raw/main/radical-stroke.txt" || true
for s in Arabic Latin Common; do
  fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://raw.githubusercontent.com/tesseract-ocr/langdata_lstm/main/script/${s}.unicharset" || \
  fetch_asset "$SCRIPT_DIR/${s}.unicharset" "https://github.com/tesseract-ocr/langdata_lstm/raw/main/script/${s}.unicharset" || true
done

# Prefer best tessdata for base models
export TESSDATA_PREFIX="$WIN_TESSDATA_BEST"
if ! ls "$WIN_TESSDATA_BEST"/*.traineddata >/dev/null 2>&1; then
  if ls "$TESSDATA_BEST_DIR"/*.traineddata >/dev/null 2>&1; then export TESSDATA_PREFIX="$TESSDATA_BEST_DIR"; else export TESSDATA_PREFIX="$TESSDATA_DIR"; fi
fi

echo "📦 Ensuring base models (fas, ara) are available..."
for lang in fas ara; do
  # 1) Prefer tessdata_best
  if [ ! -f "$WIN_TESSDATA_BEST/${lang}.traineddata" ] && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ]; then
    curl -fsSL -o "$WIN_TESSDATA_BEST/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/${lang}.traineddata" \
      || curl -fsSL -o "$WIN_TESSDATA_BEST/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata_best/raw/main/${lang}.traineddata" \
      || true
  fi
  # 2) If best not available, try tessdata_fast
  if [ ! -s "$WIN_TESSDATA_BEST/${lang}.traineddata" ] && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ]; then
    curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/${lang}.traineddata" \
      || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata_fast/raw/main/${lang}.traineddata" \
      || true
  fi
  # 3) As an additional fallback (per user’s earlier request), try tessdata repo for fas; ara may 404 here, but attempt anyway
  if [ ! -s "$WIN_TESSDATA/${lang}.traineddata" ] && [ ! -s "$WIN_TESSDATA_BEST/${lang}.traineddata" ] \
     && [ ! -f "$TESSDATA_BEST_DIR/${lang}.traineddata" ] && [ ! -f "$TESSDATA_FAST_DIR/${lang}.traineddata" ]; then
    if [ "$lang" = "fas" ]; then
        curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata/refs/heads/main/${lang}.traineddata" \
          || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/refs/heads/main/${lang}.traineddata" \
          || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/${lang}.traineddata" \
          || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/${lang}.traineddata" || true
    else
      # Try the refs/heads/main path first (as requested), then fallback to main
      curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata/refs/heads/main/${lang}.traineddata" \
        || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/refs/heads/main/${lang}.traineddata" \
        || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/${lang}.traineddata" \
        || curl -fsSL -o "$WIN_TESSDATA/${lang}.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/${lang}.traineddata" || true
    fi
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
  local l="$1"; for d in "$WIN_TESSDATA_BEST" "$TESSDATA_BEST_DIR" "$WIN_TESSDATA" "$TESSDATA_FAST_DIR" "$TESSDATA_DIR"; do [ -f "$d/$l.traineddata" ] && { echo "$d/$l.traineddata"; return 0; }; done; return 1; }

fas_path=$(have_model fas || true)
ara_path=$(have_model ara || true)
BASE_LANGS=(); [ -n "$fas_path" ] && BASE_LANGS+=(fas); [ -n "$ara_path" ] && BASE_LANGS+=(ara)
if [ ${#BASE_LANGS[@]} -eq 0 ]; then echo "❌ No base models (fas/ara) found"; exit 1; fi
echo "Found bases: ${BASE_LANGS[*]}"

echo "🧩 Generating .lstmf files (hybrid seg: ${BASE_LANGS[*]})..."
cd "$GT_DIR"
# Normalize ground-truth text filenames: prefer .gt.txt; if only .txt exists, create .gt.txt copies
while IFS= read -r -d '' tif_norm; do
  b=$(basename "$tif_norm" .tif)
  if [ ! -f "$GT_DIR/$b.gt.txt" ] && [ -f "$GT_DIR/$b.txt" ]; then
    cp -f "$GT_DIR/$b.txt" "$GT_DIR/$b.gt.txt"
  fi
done < <(find "$GT_DIR" -maxdepth 1 -type f -name '*.tif' -print0)
LSTMF_COUNT=0
while IFS= read -r -d '' tif; do
  base=$(basename "$tif" .tif)
  gt_txt="$GT_DIR/$base.gt.txt"
  [ -f "$gt_txt" ] || { echo "⚠️  Missing $base.gt.txt"; continue; }
  for B in "${BASE_LANGS[@]}"; do
    MODEL_PATH=""; [ "$B" = fas ] && MODEL_PATH="$fas_path" || MODEL_PATH="$ara_path"
    MODEL_DIR=$(dirname "$MODEL_PATH")
    # Ensure matching GT for suffixed output base
    cp -f "$gt_txt" "$GT_DIR/$base-$B.gt.txt"
    echo "Creating LSTMF: $base (seg=$B)"
    tesseract --tessdata-dir "$MODEL_DIR" "$tif" "$base-$B" -l "$B" --oem 1 --psm 6 "$CONFIG_LSTM" >/dev/null 2>&1 || true
    if [ -f "$GT_DIR/$base-$B.lstmf" ]; then mv -f "$GT_DIR/$base-$B.lstmf" "$TMP_DIR/"; LSTMF_COUNT=$((LSTMF_COUNT+1)); else echo "⚠️  Missing $base-$B.lstmf"; fi
    rm -f "$GT_DIR/$base-$B.gt.txt" 2>/dev/null || true
  done
done < <(find "$GT_DIR" -maxdepth 1 -type f -name '*.tif' -print0)
[ "$LSTMF_COUNT" -gt 0 ] || { echo "❌ No .lstmf generated"; exit 1; }
echo "✅ Generated $LSTMF_COUNT .lstmf files"

echo "🗂️  Preparing listfiles..."
cd "$TMP_DIR"; ls *.lstmf > list.all
TOTAL=$(wc -l < list.all | tr -d ' ')
if [ "$TOTAL" -le 1 ]; then cp list.all list.train; cp list.all list.eval; else TRAIN_COUNT=$(( (TOTAL*9 + 9)/10 )); head -n "$TRAIN_COUNT" list.all > list.train; tail -n +$((TRAIN_COUNT+1)) list.all > list.eval; fi

ensure_target_traineddata() {
  # Choose or build a ckb traineddata to provide unicharset/recoder
  local target=""
  if [ -f "$WIN_TESSDATA/ckb_custom.traineddata" ]; then target="$WIN_TESSDATA/ckb_custom.traineddata"; fi
  if [ -z "$target" ] && [ -f "$WIN_TESSDATA/ckb.traineddata" ]; then target="$WIN_TESSDATA/ckb.traineddata"; fi
  if [ -n "$target" ] && combine_tessdata -d "$target" >/dev/null 2>&1; then echo "$target"; return 0; fi

  echo "🧪 Building minimal $LANG.traineddata (unicharset + recoder) from GT..."
  LNX_TMP_DIR="/tmp/tess_ckb_build"; rm -rf "$LNX_TMP_DIR"; mkdir -p "$LNX_TMP_DIR"
  cd "$GT_DIR"; rm -f "$LNX_TMP_DIR/unicharset"; unicharset_extractor *.box; mv -f unicharset "$LNX_TMP_DIR/unicharset"
  # Set properties using script_dir assets (best-effort)
  set_unicharset_properties -U "$LNX_TMP_DIR/unicharset" -O "$LNX_TMP_DIR/unicharset" --script_dir="$SCRIPT_DIR" || true
  # Build words list from corpus/GT and filter to allowed charset using Python
  cat /dev/null > "$LNX_TMP_DIR/words.raw"
  if [ -f "$WORK_DIR/corpus/ckb.training_text" ]; then cat "$WORK_DIR/corpus/ckb.training_text" >> "$LNX_TMP_DIR/words.raw"; fi
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
seen=set()
with open(wr,'r',encoding='utf-8',errors='ignore') as f, open(out,'w',encoding='utf-8') as g:
  for token in re.split(r"\\s+", f.read()):
    t=token.strip()
    if t and ok(t) and t not in seen:
      seen.add(t); g.write(t+"\n")
if os.path.getsize(out)==0:
  with open(out,'w',encoding='utf-8') as g:
    g.write("کورد\nکوردی\nدەنگ\n")
PY
  # Numbers and punctuation strictly from charset presence
  cat > "$LNX_TMP_DIR/numbers.txt" << 'EOF'
٠١٢٣٤٥٦٧٨٩
EOF
  cat > "$LNX_TMP_DIR/puncs.txt" << 'EOF'
،؛:؟«»-()٪
EOF
  # Combine to traineddata
  combine_lang_model \
    --input_unicharset "$LNX_TMP_DIR/unicharset" \
    --output_dir "$LNX_TMP_DIR" \
    --script_dir "$SCRIPT_DIR" \
    --lang "$LANG" \
    --lang_is_rtl \
    --pass_through_recoder \
    --version_str ckb_minimal \
    --words "$LNX_TMP_DIR/words.txt" \
    --numbers "$LNX_TMP_DIR/numbers.txt" \
    --puncs "$LNX_TMP_DIR/puncs.txt" || true
  if [ -f "$LNX_TMP_DIR/$LANG.traineddata" ]; then echo "$LNX_TMP_DIR/$LANG.traineddata"; return 0; fi
  echo "❌ Failed to build minimal $LANG.traineddata"; return 1
}

TARGET_TRAINEDDATA="$(ensure_target_traineddata)" || { echo "❌ No target traineddata available"; exit 1; }
echo "Using target traineddata: $TARGET_TRAINEDDATA"

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
    --max_iterations 1500 \
    --debug_interval 0 || true
  CHECKPOINT=$(ls -t "${MODEL_PREFIX}"_checkpoint* 2>/dev/null | head -1 || true)
  [ -z "${CHECKPOINT:-}" ] && [ -f "${MODEL_PREFIX}_checkpoint" ] && CHECKPOINT="${MODEL_PREFIX}_checkpoint"
  if [ -z "${CHECKPOINT:-}" ]; then echo "❌ No checkpoint produced for $START_BASE"; continue; fi
  echo "✅ Using checkpoint: $(basename "$CHECKPOINT")"
  echo "🧱 Finalizing traineddata for $START_BASE..."
  lstmtraining --stop_training --continue_from "$CHECKPOINT" --traineddata "$TARGET_TRAINEDDATA" --model_output "$OUT_DIR/${LANG}_from_${START_BASE}.traineddata" || true
  if [ -f "$OUT_DIR/${LANG}_from_${START_BASE}.traineddata" ]; then echo "✅ Created: $OUT_DIR/${LANG}_from_${START_BASE}.traineddata"; fi
done

# Install preferred: compare BCER from checkpoint filenames if available
choose_best_model() {
  local fas_ckpt ara_ckpt fas_err ara_err
  fas_ckpt=$(ls -t "$OUT_DIR/ckb_from_fas_"*_*.checkpoint 2>/dev/null | head -1 || true)
  ara_ckpt=$(ls -t "$OUT_DIR/ckb_from_ara_"*_*.checkpoint 2>/dev/null | head -1 || true)
  if [ -n "$fas_ckpt" ]; then fas_err=$(echo "$fas_ckpt" | sed -E 's/.*_([0-9]+\.[0-9]+)_.*/\1/'); fi
  if [ -n "$ara_ckpt" ]; then ara_err=$(echo "$ara_ckpt" | sed -E 's/.*_([0-9]+\.[0-9]+)_.*/\1/'); fi
  # If both errors available, choose lower
  if [ -n "${fas_err:-}" ] && [ -n "${ara_err:-}" ]; then
    awk "BEGIN{exit !($fas_err < $ara_err)}" && echo "$OUT_DIR/${LANG}_from_fas.traineddata" && return 0 || true
    echo "$OUT_DIR/${LANG}_from_ara.traineddata"; return 0
  fi
  # If only one exists, choose it
  if [ -f "$OUT_DIR/${LANG}_from_fas.traineddata" ] && [ ! -f "$OUT_DIR/${LANG}_from_ara.traineddata" ]; then echo "$OUT_DIR/${LANG}_from_fas.traineddata"; return 0; fi
  if [ -f "$OUT_DIR/${LANG}_from_ara.traineddata" ] && [ ! -f "$OUT_DIR/${LANG}_from_fas.traineddata" ]; then echo "$OUT_DIR/${LANG}_from_ara.traineddata"; return 0; fi
  # Fallback: prefer fas then ara
  if [ -f "$OUT_DIR/${LANG}_from_fas.traineddata" ]; then echo "$OUT_DIR/${LANG}_from_fas.traineddata"; return 0; fi
  if [ -f "$OUT_DIR/${LANG}_from_ara.traineddata" ]; then echo "$OUT_DIR/${LANG}_from_ara.traineddata"; return 0; fi
  return 1
}

PREFERRED="$(choose_best_model || true)"
if [ -n "$PREFERRED" ] && [ -f "$PREFERRED" ]; then
  cp "$PREFERRED" "$OUT_DIR/$LANG.traineddata" || true
  cp "$PREFERRED" "$WIN_TESSDATA/ckb.traineddata" || true
  echo "✅ Installed to C:\\tesseract\\tessdata\\ckb.traineddata"
else
  echo "❌ No trained model finalized"
  exit 1
fi

