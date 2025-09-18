#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export FONTCONFIG_FILE="$SCRIPT_DIR/fonts.conf"
FONTS_PATH="$WORK_DIR/fonts"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUT_DIR="$WORK_DIR/output"
LOG_DIR="$OUT_DIR/logs"

mkdir -p "$LOG_DIR"

if [ ! -f "$CORPUS_FILE" ]; then
  echo "Corpus not found: $CORPUS_FILE"; exit 1
fi

SAMPLE_TXT="$LOG_DIR/sample_ckb.txt"
head -n 1 "$CORPUS_FILE" > "$SAMPLE_TXT"

echo "== Debug: font renderability check =="
echo "Fonts dir: $FONTS_PATH"
echo "Sample line: $(cat "$SAMPLE_TXT")"
echo ""

count=0
for TTF in $(find "$FONTS_PATH" -maxdepth 1 -type f -iname '*.ttf' | sort | head -n 20); do
  count=$((count+1))
  base=$(basename "$TTF" .ttf)
  fam=$(fc-scan --format='%{family[0]}\n' "$TTF" 2>/dev/null | tr -d '\r')
  log="$LOG_DIR/dbg_${base}.log"
  rm -f /tmp/t2i_dbg_${base}.* 2>/dev/null || true
  ok=""
  # Try family with fonts_dir
  if text2image --text="$SAMPLE_TXT" --outputbase="/tmp/t2i_dbg_${base}_famdir" --font="$fam" --fonts_dir="$FONTS_PATH" --ptsize=12 --resolution=200 --max_pages=1 --strip_unrenderable_words >/dev/null 2>"$log"; then ok="famdir"; fi
  # Try basename with fonts_dir
  if [ -z "$ok" ] && text2image --text="$SAMPLE_TXT" --outputbase="/tmp/t2i_dbg_${base}_basedir" --font="$base" --fonts_dir="$FONTS_PATH" --ptsize=12 --resolution=200 --max_pages=1 --strip_unrenderable_words >/dev/null 2>>"$log"; then ok="basedir"; fi
  # Try family without fonts_dir
  if [ -z "$ok" ] && text2image --text="$SAMPLE_TXT" --outputbase="/tmp/t2i_dbg_${base}_fam" --font="$fam" --ptsize=12 --resolution=200 --max_pages=1 --strip_unrenderable_words >/dev/null 2>>"$log"; then ok="fam"; fi
  # Try basename without fonts_dir
  if [ -z "$ok" ] && text2image --text="$SAMPLE_TXT" --outputbase="/tmp/t2i_dbg_${base}_base" --font="$base" --ptsize=12 --resolution=200 --max_pages=1 --strip_unrenderable_words >/dev/null 2>>"$log"; then ok="base"; fi
  if [ -n "$ok" ]; then
    echo "[$count] PASS $base (fam='$fam') via $ok"
  else
    echo "[$count] FAIL $base (fam='$fam')"
  fi
done

echo "Logs: $LOG_DIR/dbg_*.log"
