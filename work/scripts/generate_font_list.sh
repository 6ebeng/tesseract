#!/bin/sh
# This script generates a clean list of available fonts from text2image.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FONTS_PATH="$WORK_DIR/fonts"
# Allow overriding the output location to avoid Windows permission issues
FONT_LIST_FILE="${FONT_LIST_OUTPUT:-$WORK_DIR/font-test/fontlist.txt}"
export FONTCONFIG_FILE="$(cd "$SCRIPT_DIR" && pwd)/fonts.conf"

# Ensure the output directory exists if it's under a directory tree
mkdir -p "$(dirname "$FONT_LIST_FILE")" 2>/dev/null || true

# Generate the font list using awk for robust parsing
TMP_OUT="${FONT_LIST_FILE}.tmp"
rm -f "$TMP_OUT" 2>/dev/null || true

text2image --list_available_fonts --strip_unrenderable_words 2>/dev/null | \
    awk -F': ' '{
        match($0, /: /)
        if (RSTART > 0) { print substr($0, RSTART + RLENGTH) }
    }' > "$TMP_OUT" || true

# If text2image failed or produced an empty list, fall back to filenames
if [ ! -s "$TMP_OUT" ]; then
    echo "text2image font listing failed or returned empty; falling back to filenames..." 1>&2
    # Build list from font filenames (strip extension), preserve spaces
    : > "$TMP_OUT"
    find "$FONTS_PATH" -maxdepth 1 -type f \( -iname '*.ttf' -o -iname '*.otf' \) -print 2>/dev/null | \
        sed 's#.*/##' | sed -E 's/\.(ttf|otf)$//' | sort -u > "$TMP_OUT"
fi

mv -f "$TMP_OUT" "$FONT_LIST_FILE" 2>/dev/null || cp "$TMP_OUT" "$FONT_LIST_FILE"

if [ -s "$FONT_LIST_FILE" ]; then
    echo "Successfully generated font list at: $FONT_LIST_FILE"
    echo "Total fonts found: $(wc -l < "$FONT_LIST_FILE")"
else
    echo "Failed to generate font list."
    exit 1
fi
