#!/bin/sh
# Summarize current training status

set -e
WORK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$WORK_DIR"

echo "== Status @ $(date) =="

echo "[counts]"
printf "  tif: "; ls ground-truth-robust/*.tif 2>/dev/null | wc -l
printf "  box: "; ls ground-truth-robust/*.box 2>/dev/null | wc -l
printf "  gt : "; ls ground-truth-robust/*.gt.txt 2>/dev/null | wc -l

if [ -f output/robust-lstmf.txt ]; then
  printf "  lstmf list: "; wc -l output/robust-lstmf.txt | awk '{print $1}'
else
  echo "  lstmf list: none"
fi

echo "[artifacts]"
echo -n "  checkpoints: "
ls -1t output/ckb_robust*checkpoint* 2>/dev/null | head -3 || echo none
echo -n "  traineddata: "
ls -1t output/*.traineddata 2>/dev/null | head -3 || echo none

LATEST=$(ls -1t output/logs/robust_* 2>/dev/null | head -1)
if [ -n "$LATEST" ] && [ -f "$LATEST" ]; then
  echo "[log] tail $LATEST"
  tail -n 60 "$LATEST" || true
else
  echo "[log] no logs found"
fi

exit 0
