#!/bin/sh

# Script to monitor the progress of the robust training

echo "=== Training Progress Monitor ==="
echo ""

WORK_DIR="$(pwd)/work"
GROUND_TRUTH_DIR="$WORK_DIR/ground-truth-robust"
OUTPUT_DIR="$WORK_DIR/output"

while true; do
    clear
    echo "=== Training Progress Monitor ==="
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # Count generated files
    if [ -d "$GROUND_TRUTH_DIR" ]; then
        TIF_COUNT=$(find "$GROUND_TRUTH_DIR" -name "*.tif" 2>/dev/null | wc -l)
        GT_COUNT=$(find "$GROUND_TRUTH_DIR" -name "*.gt.txt" 2>/dev/null | wc -l)
        LSTMF_COUNT=$(find "$GROUND_TRUTH_DIR" -name "*.lstmf" 2>/dev/null | wc -l)
        
        echo "Generated Files:"
        echo "  TIF images: $TIF_COUNT"
        echo "  Ground truth: $GT_COUNT"
        echo "  LSTMF files: $LSTMF_COUNT"
        echo ""
        
        # Show disk usage
        if [ "$TIF_COUNT" -gt 0 ]; then
            SIZE=$(du -sh "$GROUND_TRUTH_DIR" 2>/dev/null | cut -f1)
            echo "Disk usage: $SIZE"
            echo ""
        fi
        
        # Show latest processed font
        LATEST=$(ls -t "$GROUND_TRUTH_DIR"/*.tif 2>/dev/null | head -1)
        if [ -n "$LATEST" ]; then
            echo "Latest processed:"
            echo "  $(basename "$LATEST")"
            echo ""
        fi
    else
        echo "Training directory not yet created..."
    fi
    
    # Check for checkpoint files
    if [ -d "$OUTPUT_DIR" ]; then
        CHECKPOINT=$(ls -t "$OUTPUT_DIR"/ckb_robust*.checkpoint 2>/dev/null | head -1)
        if [ -n "$CHECKPOINT" ]; then
            echo "Training checkpoint found:"
            echo "  $(basename "$CHECKPOINT")"
            CHECKPOINT_SIZE=$(du -h "$CHECKPOINT" | cut -f1)
            echo "  Size: $CHECKPOINT_SIZE"
        fi
        
        # Check for LSTMF list
        if [ -f "$OUTPUT_DIR/robust-lstmf.txt" ]; then
            LSTMF_LIST_COUNT=$(wc -l < "$OUTPUT_DIR/robust-lstmf.txt")
            echo ""
            echo "LSTMF list entries: $LSTMF_LIST_COUNT"
        fi
    fi
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "(Updates every 10 seconds)"
    
    sleep 10
done
