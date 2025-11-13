#!/bin/bash
# Batch LSTMF Processor - Processes training data in batches for network drives
set -e

NETWORK_GT="/mnt/z/training_output_best/ground_truth"
NETWORK_TMP="/mnt/z/training_output_best/tmp"
LOCAL_TMP="/mnt/c/tesseract/work/training_output_best/tmp"
LOCAL_BATCH="/mnt/c/tesseract/work/training_output_best/batch_tmp"
LOG_DIR="/mnt/c/tesseract/work/training_output_best/logs"
BATCH_SIZE=${BATCH_SIZE:-5000}
WORKERS=${WORKERS:-22}

# Create log directory
mkdir -p "$LOG_DIR" 2>/dev/null || true
FAILED_FILES_LOG="$LOG_DIR/failed_files_$(date +%Y%m%d_%H%M%S).log"
BATCH_LOG="$LOG_DIR/batch_processing_$(date +%Y%m%d_%H%M%S).log"

echo "╔════════════════════════════════════════════╗"
echo "║     BATCH LSTMF PROCESSOR                  ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Batch size: $BATCH_SIZE files"
echo "Workers: $WORKERS parallel"
echo "Local cache: $LOCAL_BATCH"
echo "Local output: $LOCAL_TMP"
echo ""

# Ensure Z: drive is mounted
if [ ! -d "$NETWORK_GT" ]; then
    echo "Mounting Z: drive..."
    sudo mount -t drvfs 'Z:' /mnt/z -o metadata,uid=1000,gid=1000 2>/dev/null || true
    sleep 2
fi

if [ ! -d "$NETWORK_GT" ]; then
    echo "ERROR: Cannot access $NETWORK_GT"
    exit 1
fi

# Create local tmp directory
mkdir -p "$LOCAL_TMP"

# Model paths
fas_model="/mnt/c/tesseract/tessdata/best/fas.traineddata"
ara_model="/mnt/c/tesseract/tessdata/best/ara.traineddata"
eng_model="/mnt/c/tesseract/tessdata/best/eng.traineddata"
lstm_config="/mnt/c/tesseract/tessdata/configs/lstm.train"

# Check which models actually exist
AVAILABLE_MODELS=""
[ -f "$fas_model" ] && AVAILABLE_MODELS="fas "
[ -f "$ara_model" ] && AVAILABLE_MODELS="${AVAILABLE_MODELS}ara "
[ -f "$eng_model" ] && AVAILABLE_MODELS="${AVAILABLE_MODELS}eng"
echo "Available models: ${AVAILABLE_MODELS:-none}"
echo ""

# Model success counters (tracked in final summary)
FAS_SUCCESS=0
ARA_SUCCESS=0
ENG_SUCCESS=0

echo "Counting files and validating complete sets..."
TOTAL_FILES=$(find "$NETWORK_GT" -maxdepth 1 -name '*.tif' -type f 2>/dev/null | wc -l)
echo "Found: $TOTAL_FILES TIF files"

# Check and move any LSTMF files that are in the wrong location
STRAY_LSTMF=$(find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f 2>/dev/null | wc -l)
if [ "$STRAY_LSTMF" -gt 0 ]; then
    echo "⚠️  Found $STRAY_LSTMF LSTMF files in ground_truth folder"
    echo "   Moving them to tmp folder..."
    find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f -exec mv {} "$NETWORK_TMP/" \; 2>/dev/null
    echo "   ✓ Moved to correct location"
fi

EXISTING=$(find "$LOCAL_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
if [ "$EXISTING" -eq 0 ]; then
    EXISTING=$(find "$NETWORK_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
fi

if [ "$EXISTING" -gt 0 ]; then
    echo ""
    echo "🔄 RESUME MODE ENABLED"
    echo "   Found $EXISTING existing LSTMF files"
    echo "   Will skip already-processed file sets"
    # Note: TOTAL_SETS will be calculated after validating complete sets
fi

echo ""
echo "Starting batch processing..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create list of complete file sets (basenames only, where all 3 files exist)
BASENAME_LIST="/tmp/basename_list_$$.txt"
find "$NETWORK_GT" -maxdepth 1 -name '*.tif' -type f 2>/dev/null | while read tif; do
    base=$(basename "$tif" .tif)
    # Only include if all three files exist
    if [ -f "$NETWORK_GT/$base.gt.txt" ] && [ -f "$NETWORK_GT/$base.box" ]; then
        echo "$base"
    fi
done > "$BASENAME_LIST"

TOTAL_SETS=$(wc -l < "$BASENAME_LIST")
echo "Found $TOTAL_SETS complete file sets (TIF+GT+BOX)"

mkdir -p "$LOCAL_BATCH"
GLOBAL_START=$(date +%s)
TOTAL_PROCESSED=0
BATCH_NUM=0

# Track batch times for better ETA
declare -a BATCH_TIMES
AVG_BATCH_TIME=0

while true; do
    BATCH_NUM=$((BATCH_NUM + 1))
    
    # Get next batch of basenames (not file paths)
    BATCH_BASENAMES=$(tail -n +$((TOTAL_PROCESSED + 1)) "$BASENAME_LIST" | head -n $BATCH_SIZE)
    [ -z "$BATCH_BASENAMES" ] && break
    
    BATCH_COUNT=$(echo "$BATCH_BASENAMES" | wc -l)
    [ "$BATCH_COUNT" -eq 0 ] && break
    
    echo "📦 Batch $BATCH_NUM: Processing file sets $(($TOTAL_PROCESSED + 1)) to $(($TOTAL_PROCESSED + BATCH_COUNT))"
    BATCH_START=$(date +%s)
    
    # Copy to local
    echo "   📥 Copying to local SSD..."
    
    # Don't clear batch_tmp if resuming - check for existing files first
    EXISTING_IN_BATCH=$(find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | wc -l)
    if [ "$EXISTING_IN_BATCH" -gt 0 ]; then
        echo "   🔄 Found $EXISTING_IN_BATCH file sets already in batch_tmp (resume mode)"
    else
        rm -rf "$LOCAL_BATCH"/* 2>/dev/null || true
    fi
    mkdir -p "$LOCAL_BATCH" 2>/dev/null || true
    
    # Filter out complete sets that already exist in batch_tmp
    SETS_TO_COPY=""
    for base in $BATCH_BASENAMES; do
        # Check if ALL three files exist locally, otherwise need to copy
        if [ ! -f "$LOCAL_BATCH/$base.tif" ] || [ ! -f "$LOCAL_BATCH/$base.gt.txt" ] || [ ! -f "$LOCAL_BATCH/$base.box" ]; then
            SETS_TO_COPY="$SETS_TO_COPY$base"$'\n'
        fi
    done
    
    # Only copy if there are sets to copy
    if [ -n "$SETS_TO_COPY" ] && [ "$(echo "$SETS_TO_COPY" | grep -c .)" -gt 0 ]; then
        COPY_COUNT=$(echo "$SETS_TO_COPY" | grep -c .)
        TOTAL_FILES_TO_COPY=$((COPY_COUNT * 3))
        echo "   📋 Copying $COPY_COUNT file sets ($TOTAL_FILES_TO_COPY files: TIF+GT+BOX for each set)..."
        
        # Copy all three files together for each basename
        echo "$SETS_TO_COPY" | grep -v '^$' | while read base; do
            # Copy all three files atomically - if any fails, remove all
            if cp "$NETWORK_GT/$base.tif" "$LOCAL_BATCH/" 2>/dev/null && \
               cp "$NETWORK_GT/$base.gt.txt" "$LOCAL_BATCH/" 2>/dev/null && \
               cp "$NETWORK_GT/$base.box" "$LOCAL_BATCH/" 2>/dev/null; then
                :  # Success, all three files copied
            else
                echo "   ❌ Failed to copy complete set: $base"
                rm -f "$LOCAL_BATCH/$base.tif" "$LOCAL_BATCH/$base.gt.txt" "$LOCAL_BATCH/$base.box" 2>/dev/null
            fi
        done
    fi
    
    # Verify files were copied
    COPIED_COUNT=$(find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | wc -l)
    GT_COUNT=$(find "$LOCAL_BATCH" -name '*.gt.txt' -type f 2>/dev/null | wc -l)
    BOX_COUNT=$(find "$LOCAL_BATCH" -name '*.box' -type f 2>/dev/null | wc -l)
    TOTAL_FILES_COPIED=$((COPIED_COUNT + GT_COUNT + BOX_COUNT))
    
    if [ "$COPIED_COUNT" -eq 0 ]; then
        echo "   ❌ Failed to copy files to local batch directory"
        continue
    fi
    
    # Verify all three file types are present and matching
    if [ "$GT_COUNT" -ne "$COPIED_COUNT" ] || [ "$BOX_COUNT" -ne "$COPIED_COUNT" ]; then
        echo "   ⚠️  Incomplete file sets! Sets: TIF=$COPIED_COUNT, GT=$GT_COUNT, BOX=$BOX_COUNT"
        echo "   Cleaning up incomplete sets and re-copying..."
        
        # Remove files that don't have all three components
        find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | while read tif; do
            base=$(basename "$tif" .tif)
            if [ ! -f "$LOCAL_BATCH/$base.gt.txt" ] || [ ! -f "$LOCAL_BATCH/$base.box" ]; then
                echo "   🗑️  Removing incomplete set: $base"
                rm -f "$LOCAL_BATCH/$base.tif" "$LOCAL_BATCH/$base.gt.txt" "$LOCAL_BATCH/$base.box" 2>/dev/null
            fi
        done
        
        # Re-copy missing complete sets
        find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | while read tif; do
            base=$(basename "$tif" .tif)
            if [ ! -f "$LOCAL_BATCH/$base.gt.txt" ] || [ ! -f "$LOCAL_BATCH/$base.box" ]; then
                if [ -f "$NETWORK_GT/$base.tif" ] && [ -f "$NETWORK_GT/$base.gt.txt" ] && [ -f "$NETWORK_GT/$base.box" ]; then
                    cp "$NETWORK_GT/$base.tif" "$LOCAL_BATCH/" 2>/dev/null && \
                    cp "$NETWORK_GT/$base.gt.txt" "$LOCAL_BATCH/" 2>/dev/null && \
                    cp "$NETWORK_GT/$base.box" "$LOCAL_BATCH/" 2>/dev/null || {
                        echo "   ❌ Failed to copy: $base"
                        rm -f "$LOCAL_BATCH/$base.tif" "$LOCAL_BATCH/$base.gt.txt" "$LOCAL_BATCH/$base.box" 2>/dev/null
                    }
                fi
            fi
        done
        
        GT_COUNT=$(find "$LOCAL_BATCH" -name '*.gt.txt' -type f 2>/dev/null | wc -l)
        BOX_COUNT=$(find "$LOCAL_BATCH" -name '*.box' -type f 2>/dev/null | wc -l)
        COPIED_COUNT=$(find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | wc -l)
        TOTAL_FILES_COPIED=$((COPIED_COUNT + GT_COUNT + BOX_COUNT))
        echo "   After cleanup: $COPIED_COUNT sets, $TOTAL_FILES_COPIED total files (TIF=$COPIED_COUNT, GT=$GT_COUNT, BOX=$BOX_COUNT)"
    fi
    
    # Final count message
    TOTAL_FILES_READY=$((COPIED_COUNT * 3))
    echo "   ✓ Ready: $COPIED_COUNT complete file sets = $TOTAL_FILES_READY files (TIF+GT+BOX)"
    
    # Remember count before this batch (for progress calculation)
    TOTAL_IN_TMP_BEFORE=$(find "$LOCAL_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
    
    # Process locally (files are now in LOCAL_BATCH)
    echo "   ⚡ Processing with $WORKERS workers..."
    START_TIME=$(date +%s)
    echo "   Started at: $(date '+%H:%M:%S')"
    
    # Simple loop with background jobs - inline processing (no function export needed)
    WORKER_ID=0
    CHECK_COUNT=0
    LAST_COUNT=0
    TOTAL_FILE_SETS=$(find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | wc -l)
    echo "   Processing $TOTAL_FILE_SETS file sets..."
    
    # Use GNU Parallel for reliable parallel processing
    export LOCAL_BATCH LOCAL_TMP NETWORK_TMP FAILED_FILES_LOG
    
    find "$LOCAL_BATCH" -name '*.tif' -type f 2>/dev/null | parallel -j "$WORKERS" --will-cite '
        base=$(basename {} .tif)
        worker_id={%}
        
        # Skip if already processed
        [ -f "'"$LOCAL_TMP"'/$base-fas.lstmf" ] && exit 0
        [ -f "'"$LOCAL_TMP"'/$base-ara.lstmf" ] && exit 0
        [ -f "'"$LOCAL_TMP"'/$base-eng.lstmf" ] && exit 0
        [ -f "'"$NETWORK_TMP"'/$base-fas.lstmf" ] && exit 0
        [ -f "'"$NETWORK_TMP"'/$base-ara.lstmf" ] && exit 0
        [ -f "'"$NETWORK_TMP"'/$base-eng.lstmf" ] && exit 0
        
        gt="'"$LOCAL_BATCH"'/$base.gt.txt"
        if [ ! -f "$gt" ]; then
            echo "$base.gt.txt:MISSING_GT" >> "'"$FAILED_FILES_LOG"'" 2>/dev/null
            echo "   [W$worker_id $(date +%H:%M:%S)] ✗ FAILED: $base (missing GT file)"
            exit 1
        fi
        
        cd "'"$LOCAL_BATCH"'" || exit 1
        lstm_config="/mnt/c/tesseract/tessdata/configs/lstm.train"
        
        # Try fas
        cp -f "$base.gt.txt" "$base-fas.gt.txt" 2>/dev/null && \
        OMP_THREAD_LIMIT=1 tesseract --tessdata-dir /mnt/c/tesseract/tessdata/best \
            "$base.tif" "$base-fas" -l fas --oem 1 --psm 13 "$lstm_config" 2>/dev/null && \
        [ -f "$base-fas.lstmf" ] && {
            mv "$base-fas.lstmf" "'"$LOCAL_TMP"'/" 2>/dev/null
            rm -f "$base-fas.gt.txt" 2>/dev/null
            echo "   [W$worker_id $(date +%H:%M:%S)] ✓ $base (fas)"
            exit 0
        }
        rm -f "$base-fas.gt.txt" 2>/dev/null
        
        # Try ara
        cp -f "$base.gt.txt" "$base-ara.gt.txt" 2>/dev/null && \
        OMP_THREAD_LIMIT=1 tesseract --tessdata-dir /mnt/c/tesseract/tessdata/best \
            "$base.tif" "$base-ara" -l ara --oem 1 --psm 13 "$lstm_config" 2>/dev/null && \
        [ -f "$base-ara.lstmf" ] && {
            mv "$base-ara.lstmf" "'"$LOCAL_TMP"'/" 2>/dev/null
            rm -f "$base-ara.gt.txt" 2>/dev/null
            echo "   [W$worker_id $(date +%H:%M:%S)] ✓ $base (ara)"
            exit 0
        }
        rm -f "$base-ara.gt.txt" 2>/dev/null
        
        # All attempts failed
        echo "$base:ALL_MODELS_FAILED" >> "'"$FAILED_FILES_LOG"'" 2>/dev/null
        echo "   [W$worker_id $(date +%H:%M:%S)] ✗ FAILED: $base (all models failed)"
        exit 1
    '
    
    
    echo "   Finished at: $(date '+%H:%M:%S')"
    
    # Count LSTMF files generated in this batch
    CURRENT_LSTMF=$(find "$LOCAL_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
    BATCH_GENERATED=$((CURRENT_LSTMF - TOTAL_IN_TMP_BEFORE))
    
    echo "   📊 Generated $BATCH_GENERATED LSTMF files in LOCAL_TMP"
    
    # Move LSTMF files from local to network AFTER EACH BATCH
    if [ "$BATCH_GENERATED" -gt 0 ]; then
        echo "   📤 Moving $BATCH_GENERATED LSTMF files to network..."
        find "$LOCAL_TMP" -name '*.lstmf' -type f -print0 2>/dev/null | xargs -0 -r mv -t "$NETWORK_TMP/" 2>/dev/null
        MOVED_COUNT=$(find "$NETWORK_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
        echo "   ✅ Moved to network. Total in network: $MOVED_COUNT"
    else
        echo "   ⚠️  No new LSTMF files generated in this batch"
    fi
    
    # Cleanup TIF/GT/BOX files only (LSTMF files moved to network already)
    find "$LOCAL_BATCH" -type f \( -name '*.tif' -o -name '*.gt.txt' -o -name '*.box' \) -delete 2>/dev/null
    
    # Safety check: Move any LSTMF files that somehow ended up in network GT
    STRAY_IN_GT=$(find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f 2>/dev/null | wc -l)
    if [ "$STRAY_IN_GT" -gt 0 ]; then
        echo "   ⚠️  Moving $STRAY_IN_GT stray LSTMF files from ground_truth to tmp..."
        find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f -exec mv {} "$NETWORK_TMP/" \; 2>/dev/null
    fi
    
    TOTAL_PROCESSED=$((TOTAL_PROCESSED + BATCH_COUNT))
    BATCH_TIME=$(($(date +%s) - BATCH_START))
    ELAPSED=$(($(date +%s) - GLOBAL_START))
    
    # Track batch times for better ETA
    BATCH_TIMES+=($BATCH_TIME)
    if [ ${#BATCH_TIMES[@]} -gt 0 ]; then
        SUM=0
        for t in "${BATCH_TIMES[@]}"; do
            SUM=$((SUM + t))
        done
        AVG_BATCH_TIME=$((SUM / ${#BATCH_TIMES[@]}))
    fi
    
    # Stats
    PERCENT=$((TOTAL_PROCESSED * 100 / TOTAL_SETS))
    
    # Calculate rate based on actual processed files (use BATCH_GENERATED, not BATCH_COUNT)
    if [ "$ELAPSED" -gt 0 ] && [ "$TOTAL_PROCESSED" -gt 0 ]; then
        OVERALL_RATE=$((MOVED_COUNT * 60 / ELAPSED))
    else
        OVERALL_RATE=0
    fi
    
    # Improved ETA based on average batch time
    REMAINING_BATCHES=$(( (TOTAL_SETS - TOTAL_PROCESSED + BATCH_SIZE - 1) / BATCH_SIZE ))
    if [ "$AVG_BATCH_TIME" -gt 0 ]; then
        ETA_MIN=$(( REMAINING_BATCHES * AVG_BATCH_TIME / 60 ))
    else
        ETA_MIN=0
    fi
    
    # Count model successes
    FAS_COUNT=$(find "$NETWORK_TMP" -name '*-fas.lstmf' -type f 2>/dev/null | wc -l)
    ARA_COUNT=$(find "$NETWORK_TMP" -name '*-ara.lstmf' -type f 2>/dev/null | wc -l)
    ENG_COUNT=$(find "$NETWORK_TMP" -name '*-eng.lstmf' -type f 2>/dev/null | wc -l)
    
    echo "   ✓ Batch completed in ${BATCH_TIME}s (processed: $BATCH_COUNT file sets, generated: $BATCH_GENERATED LSTMF)"
    echo "   📊 Models: FAS=$FAS_COUNT | ARA=$ARA_COUNT | ENG=$ENG_COUNT | Total=$MOVED_COUNT"
    echo "   📊 Progress: $TOTAL_PROCESSED / $TOTAL_SETS ($PERCENT%) | Speed: $OVERALL_RATE files/min | ETA: ${ETA_MIN} min"
    echo ""
done

# All LSTMF files should already be in network tmp (moved after each batch)
echo "📤 Verifying all LSTMF files in network..."
LOCAL_LSTMF_COUNT=$(find "$LOCAL_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
if [ "$LOCAL_LSTMF_COUNT" -gt 0 ]; then
    echo "   ⚠️  Found $LOCAL_LSTMF_COUNT leftover LSTMF files in local tmp"
    echo "   Moving to $NETWORK_TMP..."
    find "$LOCAL_TMP" -name '*.lstmf' -type f -print0 2>/dev/null | xargs -0 -r mv -t "$NETWORK_TMP/" 2>/dev/null
    echo "   ✅ Moved remaining files to network"
else
    echo "   ✓ All files already in network tmp (moved after each batch)"
fi

# Cleanup
rm -f "$BASENAME_LIST"
rm -rf "$LOCAL_BATCH" 2>/dev/null

# Final cleanup: Move any remaining LSTMF files from ground_truth to tmp
echo "🧹 Final cleanup: checking for stray LSTMF files..."
FINAL_STRAY=$(find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f 2>/dev/null | wc -l)
if [ "$FINAL_STRAY" -gt 0 ]; then
    echo "   Moving $FINAL_STRAY LSTMF files to tmp folder..."
    find "$NETWORK_GT" -maxdepth 1 -name '*.lstmf' -type f -exec mv {} "$NETWORK_TMP/" \; 2>/dev/null
    echo "   ✓ Cleanup complete"
fi

# Final stats
FINAL_COUNT=$(find "$NETWORK_TMP" -name '*.lstmf' -type f 2>/dev/null | wc -l)
TOTAL_TIME=$(($(date +%s) - GLOBAL_START))

# Count failures
FAILED_COUNT=0
if [ -f "$FAILED_FILES_LOG" ]; then
    FAILED_COUNT=$(wc -l < "$FAILED_FILES_LOG" 2>/dev/null || echo 0)
fi

# Final model breakdown
FINAL_FAS=$(find "$NETWORK_TMP" -name '*-fas.lstmf' -type f 2>/dev/null | wc -l)
FINAL_ARA=$(find "$NETWORK_TMP" -name '*-ara.lstmf' -type f 2>/dev/null | wc -l)
FINAL_ENG=$(find "$NETWORK_TMP" -name '*-eng.lstmf' -type f 2>/dev/null | wc -l)

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║           PROCESSING COMPLETE!             ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "✅ Total LSTMF files: $FINAL_COUNT"
echo "   📊 Model breakdown:"
echo "      - FAS (Persian): $FINAL_FAS files ($((FINAL_FAS * 100 / (FINAL_COUNT > 0 ? FINAL_COUNT : 1)))%)"
echo "      - ARA (Arabic):  $FINAL_ARA files ($((FINAL_ARA * 100 / (FINAL_COUNT > 0 ? FINAL_COUNT : 1)))%)"
echo "      - ENG (English): $FINAL_ENG files ($((FINAL_ENG * 100 / (FINAL_COUNT > 0 ? FINAL_COUNT : 1)))%)"
if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "⚠️  Failed files: $FAILED_COUNT"
    echo "   See: $FAILED_FILES_LOG"
fi
echo "⏱️  Total time: $((TOTAL_TIME / 60))m $((TOTAL_TIME % 60))s"
echo "🚀 Average speed: $((FINAL_COUNT * 60 / (TOTAL_TIME > 0 ? TOTAL_TIME : 1))) files/min"
echo ""
echo "📁 Output location: $NETWORK_TMP"
if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "📋 Logs: $LOG_DIR"
fi
echo ""
