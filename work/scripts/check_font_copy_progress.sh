#!/bin/sh

# Quick script to check font copying progress

USER_FONTS="$HOME/.local/share/fonts/kurdish"
SYSTEM_FONTS="/usr/share/fonts/truetype/kurdish"

echo "=== Font Installation Progress ==="
echo ""

# Check user fonts directory
if [ -d "$USER_FONTS" ]; then
    COUNT=$(ls "$USER_FONTS"/*.ttf 2>/dev/null | wc -l)
    echo "User fonts directory: $USER_FONTS"
    echo "Fonts copied so far: $COUNT"
    
    if [ $COUNT -gt 0 ]; then
        echo "Latest fonts copied:"
        ls -lt "$USER_FONTS"/*.ttf 2>/dev/null | head -5 | awk '{print "  - " $9}'
    fi
else
    echo "User fonts directory not found"
fi

echo ""

# Check system fonts directory
if [ -d "$SYSTEM_FONTS" ]; then
    COUNT=$(ls "$SYSTEM_FONTS"/*.ttf 2>/dev/null | wc -l)
    echo "System fonts directory: $SYSTEM_FONTS"
    echo "Fonts copied: $COUNT"
else
    echo "System fonts directory not found"
fi

echo ""
echo "Total expected fonts: ~751"
