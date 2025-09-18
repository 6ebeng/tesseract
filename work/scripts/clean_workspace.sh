#!/bin/sh
# Safe cleanup for a fresh training build on WSL
# Removes generated artifacts while preserving source data, fonts, configs.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Cleaning workspace under: $WORK_DIR"

# Directories of generated artifacts
DIRS_TO_CLEAN="\
  $WORK_DIR/ground-truth-robust \
  $WORK_DIR/ground-truth-final \
  $WORK_DIR/ground-truth-auto \
  $WORK_DIR/ground-truth-batch \
  $WORK_DIR/ground-truth-quick \
  $WORK_DIR/ground-truth-wsl \
  $WORK_DIR/ground-truth-installed \
  $WORK_DIR/ground-truth-workaround \
  $WORK_DIR/output \
  $WORK_DIR/tessdata_tmp \
  $WORK_DIR/tmp \
  $WORK_DIR/training \
"

# Files of generated artifacts
FILES_TO_CLEAN="\
  $WORK_DIR/output/ckb_robust.traineddata \
  $WORK_DIR/output/robust-lstmf.txt \
  $WORK_DIR/output/*.checkpoint \
  $WORK_DIR/output/logs/robust_*.log \
"

timestamp() { date +%s; }

safe_remove_dir() {
  d="$1"
  if [ -d "$d" ]; then
    rm -rf "$d" 2>/dev/null || mv "$d" "${d}.old.$(timestamp)" 2>/dev/null || true
    echo "- cleaned dir: $d"
  fi
}

safe_remove_glob() {
  pattern="$1"
  # shellcheck disable=SC2086
  for f in $pattern; do
    [ -e "$f" ] || continue
    rm -f "$f" 2>/dev/null || mv "$f" "${f}.old.$(timestamp)" 2>/dev/null || true
    echo "- cleaned file: $f"
  done
}

for d in $DIRS_TO_CLEAN; do
  safe_remove_dir "$d"
done

for p in $FILES_TO_CLEAN; do
  safe_remove_glob "$p"
done

mkdir -p "$WORK_DIR/output/logs"
echo "Cleanup complete."
