#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORK_DIR="$REPO_DIR/work"

echo "Cleaning generated training artifacts..."
rm -rf "$WORK_DIR/ground-truth-wsl" 2>/dev/null || true
rm -rf "$WORK_DIR/output/wsl-corpus-lstmf.txt" 2>/dev/null || true
rm -rf "$WORK_DIR/output/starter.lstm" 2>/dev/null || true
rm -rf "$WORK_DIR/output"/*.checkpoint 2>/dev/null || true
find "$WORK_DIR/output/logs" -type f -name '*.log' -size 0 -delete 2>/dev/null || true
echo "Done."
