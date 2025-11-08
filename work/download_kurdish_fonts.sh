#!/bin/bash

# Download additional high-quality Kurdish/Arabic fonts
# More font variety = better accuracy

set -euo pipefail

FONTS_DIR="fonts"
mkdir -p "$FONTS_DIR"

echo "═══════════════════════════════════════════════════════════════════"
echo "  Downloading Additional Kurdish/Arabic Fonts"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Google Noto Fonts (comprehensive Arabic coverage)
NOTO_FONTS=(
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoNaskhArabic/full/ttf/NotoNaskhArabic-Regular.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoNaskhArabic/full/ttf/NotoNaskhArabic-Bold.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoNaskhArabic/full/ttf/NotoNaskhArabic-Medium.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoNaskhArabic/full/ttf/NotoNaskhArabic-SemiBold.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoKufiArabic/full/ttf/NotoKufiArabic-Regular.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoKufiArabic/full/ttf/NotoKufiArabic-Bold.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoSansArabic/full/ttf/NotoSansArabic-Regular.ttf"
    "https://github.com/notofonts/arabic/raw/main/fonts/NotoSansArabic/full/ttf/NotoSansArabic-Bold.ttf"
)

# Traditional Arabic fonts (common in Kurdish documents)
TRADITIONAL_FONTS=(
    "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
    "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf"
    "https://github.com/google/fonts/raw/main/ofl/amiriguran/AmiriQuran-Regular.ttf"
    "https://github.com/google/fonts/raw/main/ofl/scheherazade/Scheherazade-Regular.ttf"
    "https://github.com/google/fonts/raw/main/ofl/scheherazade/Scheherazade-Bold.ttf"
    "https://github.com/google/fonts/raw/main/ofl/lateef/Lateef-Regular.ttf"
)

# Modern Arabic fonts
MODERN_FONTS=(
    "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Regular.ttf"
    "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"
    "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-SemiBold.ttf"
    "https://github.com/google/fonts/raw/main/ofl/tajawal/Tajawal-Regular.ttf"
    "https://github.com/google/fonts/raw/main/ofl/tajawal/Tajawal-Bold.ttf"
)

download_font() {
    local url="$1"
    local filename=$(basename "$url")
    local dest="$FONTS_DIR/$filename"
    
    # Skip if already exists
    if [ -f "$dest" ]; then
        echo "  ✓ Already exists: $filename"
        return 0
    fi
    
    echo "  Downloading: $filename"
    if curl -fsSL -o "$dest" "$url" 2>/dev/null; then
        if [ -s "$dest" ]; then
            echo "  ✅ Success: $filename"
            return 0
        else
            rm -f "$dest"
            echo "  ❌ Failed (empty): $filename"
            return 1
        fi
    else
        rm -f "$dest"
        echo "  ❌ Failed (download error): $filename"
        return 1
    fi
}

TOTAL=0
SUCCESS=0
FAILED=0

echo "Downloading Noto Fonts (Standard)..."
for url in "${NOTO_FONTS[@]}"; do
    ((TOTAL++))
    if download_font "$url"; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "Downloading Traditional Fonts (Amiri, Scheherazade, Lateef)..."
for url in "${TRADITIONAL_FONTS[@]}"; do
    ((TOTAL++))
    if download_font "$url"; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "Downloading Modern Fonts (Cairo, Tajawal)..."
for url in "${MODERN_FONTS[@]}"; do
    ((TOTAL++))
    if download_font "$url"; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Download Summary"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Total attempted: $TOTAL"
echo "Successfully downloaded: $SUCCESS"
echo "Failed: $FAILED"
echo ""

# Count total fonts now
FONT_COUNT=$(ls "$FONTS_DIR"/*.ttf 2>/dev/null | wc -l)
echo "Total fonts available: $FONT_COUNT"
echo ""

if [ "$FONT_COUNT" -ge 15 ]; then
    echo "✅ Excellent! You have $FONT_COUNT fonts for training."
    echo "   More fonts = better accuracy and robustness"
elif [ "$FONT_COUNT" -ge 10 ]; then
    echo "✅ Good! You have $FONT_COUNT fonts for training."
else
    echo "⚠️  Warning: Only $FONT_COUNT fonts available."
    echo "   Consider manually downloading more fonts for better results."
fi

echo ""
echo "🚀 Next step: Run improved training generation"
echo "   ./generate_ckb_training_data_improved.sh"
echo ""
