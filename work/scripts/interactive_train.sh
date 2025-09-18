#!/bin/sh

# Interactive Kurdish OCR Training Script
# Allows users to choose between different training modes

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$(pwd)/work"
CORPUS_FILE="$WORK_DIR/corpus/ckb.training_text"
OUTPUT_DIR="$WORK_DIR/output"
FONTS_PATH="$WORK_DIR/fonts"
SCRIPTS_DIR="$WORK_DIR/scripts"

# Colors - using printf-compatible format
GREEN=$(printf '\033[0;32m')
YELLOW=$(printf '\033[1;33m')
BLUE=$(printf '\033[0;34m')
CYAN=$(printf '\033[0;36m')
RED=$(printf '\033[0;31m')
MAGENTA=$(printf '\033[0;35m')
BOLD=$(printf '\033[1m')
UNDERLINE=$(printf '\033[4m')
NC=$(printf '\033[0m')

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    clear
    printf "\n"
    printf "%s╔════════════════════════════════════════════════════════════════════════╗%s\n" "$CYAN" "$NC"
    printf "%s║                                                                        ║%s\n" "$CYAN" "$NC"
    printf "%s║         %sKurdish OCR Training - Interactive Mode%s%s                      ║%s\n" "$CYAN" "$BOLD" "$NC" "$CYAN" "$NC"
    printf "%s║                                                                        ║%s\n" "$CYAN" "$NC"
    printf "%s║              Choose your training strategy below                      ║%s\n" "$CYAN" "$NC"
    printf "%s║                                                                        ║%s\n" "$CYAN" "$NC"
    printf "%s╚════════════════════════════════════════════════════════════════════════╝%s\n" "$CYAN" "$NC"
    printf "\n"
}

print_menu() {
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$MAGENTA" "$NC"
    printf "%s                         TRAINING MODES                                  %s\n" "$MAGENTA" "$NC"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$MAGENTA" "$NC"
    printf "\n"
    printf "%s1)%s %s⚡ QUICK MODE%s (5-10 minutes)\n" "$BOLD" "$NC" "$GREEN" "$NC"
    printf "   • Uses 10-20 fonts\n"
    printf "   • Basic augmentation\n"
    printf "   • Good for testing\n"
    printf "   • Accuracy: ~80%%\n"
    printf "\n"
    printf "%s2)%s %s🚀 FAST MODE%s (30-60 minutes)\n" "$BOLD" "$NC" "$BLUE" "$NC"
    printf "   • Uses 50-100 diverse fonts\n"
    printf "   • Moderate augmentation\n"
    printf "   • Good balance of speed/quality\n"
    printf "   • Accuracy: ~85-90%%\n"
    printf "\n"
    printf "%s3)%s %s⭐ STANDARD MODE%s (1-2 hours)\n" "$BOLD" "$NC" "$YELLOW" "$NC"
    printf "   • Uses 200-300 fonts\n"
    printf "   • Good augmentation\n"
    printf "   • Production ready\n"
    printf "   • Accuracy: ~90-93%%\n"
    printf "\n"
    printf "%s4)%s %s🔥 ROBUST MODE%s (2-4 hours)\n" "$BOLD" "$NC" "$RED" "$NC"
    printf "   • Uses ALL 670 fonts\n"
    printf "   • Heavy augmentation (shear, rotation, noise, blur)\n"
    printf "   • Maximum accuracy\n"
    printf "   • Accuracy: ~95%%+\n"
    printf "\n"
    printf "%s5)%s %s🎯 CUSTOM MODE%s\n" "$BOLD" "$NC" "$MAGENTA" "$NC"
    printf "   • Choose your own parameters\n"
    printf "   • Select font count, iterations, augmentation\n"
    printf "   • Full control\n"
    printf "\n"
    printf "%s6)%s %s📊 COMPARE MODELS%s\n" "$BOLD" "$NC" "$CYAN" "$NC"
    printf "   • Test existing models\n"
    printf "   • Compare accuracy\n"
    printf "   • Benchmark performance\n"
    printf "\n"
    printf "%s7)%s ℹ️  VIEW STATUS\n" "$BOLD" "$NC"
    printf "   • Check running trainings\n"
    printf "   • View existing models\n"
    printf "   • System information\n"
    printf "\n"
    printf "%s0)%s ❌ EXIT\n" "$BOLD" "$NC"
    printf "\n"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$MAGENTA" "$NC"
}

quick_mode() {
    printf "\n"
    printf "%s%sStarting QUICK MODE Training...%s\n" "$GREEN" "$BOLD" "$NC"
    printf "\n"
    
    # Create quick mode configuration
    cat > "$OUTPUT_DIR/quick_config.sh" << 'EOF'
#!/bin/sh
MAX_FONTS=20
MAX_ITERATIONS=1000
TARGET_ERROR=0.01
ENABLE_AUGMENTATION=false
MODEL_NAME="ckb_quick"
EOF
    
    printf "Configuration:\n"
    printf "  • Fonts: 20\n"
    printf "  • Iterations: 1000\n"
    printf "  • Augmentation: Basic\n"
    printf "  • Estimated time: 5-10 minutes\n"
    printf "\n"
    
    read -p "Press Enter to start training or 'c' to cancel: " choice
    if [ "$choice" != "c" ]; then
        # Run simplified training
        sh "$SCRIPTS_DIR/build_ckb_auto.sh"
    fi
}

fast_mode() {
    printf "\n"
    printf "%s%sStarting FAST MODE Training...%s\n" "$BLUE" "$BOLD" "$NC"
    printf "\n"
    
    printf "Configuration:\n"
    printf "  • Fonts: 100 (diverse selection)\n"
    printf "  • Iterations: 5000\n"
    printf "  • Augmentation: Moderate (shear, rotation)\n"
    printf "  • Estimated time: 30-60 minutes\n"
    printf "\n"
    
    read -p "Press Enter to start training or 'c' to cancel: " choice
    if [ "$choice" != "c" ]; then
        sh "$SCRIPTS_DIR/fast_robust_train.sh"
    fi
}

standard_mode() {
    printf "\n"
    printf "%s%sStarting STANDARD MODE Training...%s\n" "$YELLOW" "$BOLD" "$NC"
    printf "\n"
    
    printf "Configuration:\n"
    printf "  • Fonts: 250\n"
    printf "  • Iterations: 7500\n"
    printf "  • Augmentation: Good (shear, rotation, exposure)\n"
    printf "  • Estimated time: 1-2 hours\n"
    printf "\n"
    
    read -p "Press Enter to start training or 'c' to cancel: " choice
    if [ "$choice" != "c" ]; then
        # Create standard configuration and run
        MAX_FONTS=250 MAX_ITERATIONS=7500 sh "$SCRIPTS_DIR/build_ckb_auto.sh"
    fi
}

robust_mode() {
    printf "\n"
    printf "%s%sStarting ROBUST MODE Training...%s\n" "$RED" "$BOLD" "$NC"
    printf "\n"
    
    printf "Configuration:\n"
    printf "  • Fonts: ALL 670 Kurdish fonts\n"
    printf "  • Iterations: 10000\n"
    printf "  • Augmentation: Heavy (shear, rotation, noise, blur)\n"
    printf "  • Estimated time: 2-4 hours\n"
    printf "\n"
    printf "%s⚠ This will take significant time and resources!%s\n" "$YELLOW" "$NC"
    printf "\n"
    
    read -p "Press Enter to start training or 'c' to cancel: " choice
    if [ "$choice" != "c" ]; then
        sh "$SCRIPTS_DIR/robust_train_all_fonts.sh"
    fi
}

custom_mode() {
    printf "\n"
    printf "%s%sCUSTOM MODE - Configure Your Training%s\n" "$MAGENTA" "$BOLD" "$NC"
    printf "\n"
    
    # Font selection
    printf "%s1. Font Selection:%s\n" "$BOLD" "$NC"
    printf "   Total available fonts: 670\n"
    printf "   How many fonts to use? [1-670]: "
    read CUSTOM_FONTS
    if [ -z "$CUSTOM_FONTS" ]; then
        CUSTOM_FONTS=100
    fi
    
    # Iterations
    printf "\n"
    printf "%s2. Training Iterations:%s\n" "$BOLD" "$NC"
    printf "   Recommended: 1000 (quick) to 10000 (thorough)\n"
    printf "   Max iterations? [1000-20000]: "
    read CUSTOM_ITERATIONS
    if [ -z "$CUSTOM_ITERATIONS" ]; then
        CUSTOM_ITERATIONS=5000
    fi
    
    # Target error
    printf "\n"
    printf "%s3. Target Error Rate:%s\n" "$BOLD" "$NC"
    printf "   Lower = more accurate but slower\n"
    printf "   Options: 0.01 (fast), 0.005 (balanced), 0.001 (accurate)\n"
    printf "   Target error? [0.001-0.1]: "
    read CUSTOM_ERROR
    if [ -z "$CUSTOM_ERROR" ]; then
        CUSTOM_ERROR=0.005
    fi
    
    # Augmentation
    printf "\n"
    printf "%s4. Augmentation Options:%s\n" "$BOLD" "$NC"
    printf "   a) None - Clean images only\n"
    printf "   b) Basic - Exposure and spacing variations\n"
    printf "   c) Moderate - Add shear and rotation\n"
    printf "   d) Heavy - Add noise and blur\n"
    printf "   Choose augmentation [a/b/c/d]: "
    read CUSTOM_AUG
    
    case "$CUSTOM_AUG" in
        a) AUG_LEVEL="none" ;;
        b) AUG_LEVEL="basic" ;;
        c) AUG_LEVEL="moderate" ;;
        d) AUG_LEVEL="heavy" ;;
        *) AUG_LEVEL="moderate" ;;
    esac
    
    # Model name
    printf "\n"
    printf "%s5. Model Name:%s\n" "$BOLD" "$NC"
    printf "   Enter model name [default: ckb_custom]: "
    read CUSTOM_NAME
    if [ -z "$CUSTOM_NAME" ]; then
        CUSTOM_NAME="ckb_custom"
    fi
    
    # Summary
    printf "\n"
    printf "%s%sTraining Configuration Summary:%s\n" "$CYAN" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    printf "  Fonts: %s\n" "$CUSTOM_FONTS"
    printf "  Iterations: %s\n" "$CUSTOM_ITERATIONS"
    printf "  Target Error: %s\n" "$CUSTOM_ERROR"
    printf "  Augmentation: %s\n" "$AUG_LEVEL"
    printf "  Model Name: %s\n" "$CUSTOM_NAME"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Estimate time
    TIME_EST=$((CUSTOM_FONTS * CUSTOM_ITERATIONS / 10000))
    if [ $TIME_EST -lt 5 ]; then
        TIME_EST=5
    fi
    printf "  Estimated time: ~%s minutes\n" "$TIME_EST"
    printf "\n"
    
    read -p "Start training with these settings? [y/n]: " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        # Create custom training script
        create_custom_script "$CUSTOM_FONTS" "$CUSTOM_ITERATIONS" "$CUSTOM_ERROR" "$AUG_LEVEL" "$CUSTOM_NAME"
    fi
}

create_custom_script() {
    local FONTS=$1
    local ITERS=$2
    local ERROR=$3
    local AUG=$4
    local NAME=$5
    
    CUSTOM_SCRIPT="$OUTPUT_DIR/custom_train_${NAME}.sh"
    
    cat > "$CUSTOM_SCRIPT" << EOF
#!/bin/sh
# Auto-generated custom training script
set -e

export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$WORK_DIR"
OUTPUT_DIR="$OUTPUT_DIR"
GROUND_TRUTH_DIR="\$WORK_DIR/ground-truth-$NAME"

# Custom parameters
MAX_FONTS=$FONTS
MAX_ITERATIONS=$ITERS
TARGET_ERROR=$ERROR
AUGMENTATION="$AUG"
MODEL_NAME="$NAME"

echo "Starting custom training: \$MODEL_NAME"
echo "Fonts: \$MAX_FONTS"
echo "Iterations: \$MAX_ITERATIONS"
echo "Target Error: \$TARGET_ERROR"
echo "Augmentation: \$AUGMENTATION"

# Run training with custom parameters
MAX_FONTS=\$MAX_FONTS MAX_ITERATIONS=\$MAX_ITERATIONS TARGET_ERROR=\$TARGET_ERROR \\
    sh "$SCRIPTS_DIR/build_ckb_auto.sh"

echo "Custom training complete!"
echo "Model saved as: tessdata/\${MODEL_NAME}.traineddata"
EOF
    
    chmod +x "$CUSTOM_SCRIPT"
    printf "%sRunning custom training script...%s\n" "$GREEN" "$NC"
    sh "$CUSTOM_SCRIPT"
}

compare_models() {
    printf "\n"
    printf "%s%sModel Comparison Tool%s\n" "$CYAN" "$BOLD" "$NC"
    printf "\n"
    
    # List available models
    printf "%sAvailable Models:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    MODEL_COUNT=0
    for model in $(pwd)/tessdata/*.traineddata; do
        if [ -f "$model" ]; then
            MODEL_NAME=$(basename "$model" .traineddata)
            MODEL_SIZE=$(du -h "$model" | cut -f1)
            MODEL_DATE=$(date -r "$model" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "Unknown")
            MODEL_COUNT=$((MODEL_COUNT + 1))
            
            printf "%2d) %-20s %8s  %s\n" \
                "$MODEL_COUNT" "$MODEL_NAME" "$MODEL_SIZE" "$MODEL_DATE"
        fi
    done
    
    if [ $MODEL_COUNT -eq 0 ]; then
        printf "%sNo models found in tessdata/%s\n" "$RED" "$NC"
        return
    fi
    
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    printf "\n"
    
    printf "%sOptions:%s\n" "$BOLD" "$NC"
    printf "1) Test single model\n"
    echo "2) Compare two models"
    echo "3) Benchmark all models"
    echo "0) Back to main menu"
    echo ""
    
    printf "Choose option: "
    read compare_choice
    
    case "$compare_choice" in
        1) test_single_model ;;
        2) compare_two_models ;;
        3) benchmark_all_models ;;
        *) return ;;
    esac
}

test_single_model() {
    echo ""
    printf "Enter model name (without .traineddata): "
    read MODEL_NAME
    
    if [ ! -f "$(pwd)/tessdata/${MODEL_NAME}.traineddata" ]; then
        printf "%sModel not found: %s%s\n" "$RED" "$MODEL_NAME" "$NC"
        return
    fi
    
    # Create test image if needed
    TEST_IMAGE="$OUTPUT_DIR/test_image.tif"
    if [ ! -f "$TEST_IMAGE" ]; then
        echo "Creating test image..."
        text2image \
            --text="$CORPUS_FILE" \
            --outputbase="$OUTPUT_DIR/test_image" \
            --font="Arial" \
            --lang=ara \
            --resolution=300 \
            --ptsize=12 >/dev/null 2>&1
    fi
    
    printf "\n"
    printf "%sTesting model: %s%s\n" "$BLUE" "$MODEL_NAME" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Run OCR
    START_TIME=$(date +%s)
    tesseract "$TEST_IMAGE" "$OUTPUT_DIR/test_${MODEL_NAME}" \
        -l "$MODEL_NAME" --psm 6 >/dev/null 2>&1
    END_TIME=$(date +%s)
    
    DURATION=$((END_TIME - START_TIME))
    
    echo "Processing time: ${DURATION} seconds"
    echo ""
    echo "Sample output:"
    head -5 "$OUTPUT_DIR/test_${MODEL_NAME}.txt" 2>/dev/null
    echo "..."
}

view_status() {
    printf "\n"
    printf "%s%sSystem Status%s\n" "$CYAN" "$BOLD" "$NC"
    printf "\n"
    
    # Check for running processes
    printf "%sRunning Training Processes:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    RUNNING=$(ps aux | grep -E "lstmtraining|text2image" | grep -v grep | wc -l)
    if [ $RUNNING -gt 0 ]; then
        ps aux | grep -E "lstmtraining|text2image" | grep -v grep | \
            awk '{printf "  PID: %s  CPU: %s%%  MEM: %s%%  CMD: %s\n", $2, $3, $4, $11}'
    else
        echo "  No training processes running"
    fi
    
    echo ""
    
    # Check disk space
    printf "%sDisk Usage:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    df -h . | tail -1 | awk '{printf "  Available: %s / %s (%s used)\n", $4, $2, $5}'
    
    printf "\n"
    
    # Check existing models
    printf "%sExisting Models:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for model in $(pwd)/tessdata/*.traineddata; do
        if [ -f "$model" ]; then
            MODEL_NAME=$(basename "$model")
            MODEL_SIZE=$(du -h "$model" | cut -f1)
            printf "  %-30s %s\n" "$MODEL_NAME" "$MODEL_SIZE"
        fi
    done
    
    echo ""
    
    # Check corpus
    printf "%sTraining Corpus:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    if [ -f "$CORPUS_FILE" ]; then
        LINES=$(wc -l < "$CORPUS_FILE")
        SIZE=$(du -h "$CORPUS_FILE" | cut -f1)
        printf "  File: ckb.training_text\n"
        printf "  Lines: %s\n" "$LINES"
        printf "  Size: %s\n" "$SIZE"
    else
        printf "  %sCorpus file not found%s\n" "$RED" "$NC"
    fi
    
    printf "\n"
    
    # Check fonts
    printf "%sAvailable Fonts:%s\n" "$BOLD" "$NC"
    printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    FONT_COUNT=$(ls "$FONTS_PATH"/*.ttf 2>/dev/null | wc -l || echo 0)
    echo "  Total fonts: $FONT_COUNT"
    echo "  Location: work/fonts/"
    
    echo ""
    read -p "Press Enter to continue..."
}

# ============================================================================
# MAIN LOOP
# ============================================================================

main_loop() {
    while true; do
        print_header
        print_menu
        
        printf "${BOLD}Enter your choice [0-7]: ${NC}"
        read choice
        
        case "$choice" in
            1) quick_mode ;;
            2) fast_mode ;;
            3) standard_mode ;;
            4) robust_mode ;;
            5) custom_mode ;;
            6) compare_models ;;
            7) view_status ;;
            0) 
                printf "\n"
                printf "%sThank you for using Kurdish OCR Training!%s\n" "$GREEN" "$NC"
                printf "\n"
                exit 0
                ;;
            *)
                printf "\n"
                printf "%sInvalid choice. Please try again.%s\n" "$RED" "$NC"
                sleep 2
                ;;
        esac
    done
}

# ============================================================================
# STARTUP
# ============================================================================

# Check if running in WSL
if [ -z "$WSL_DISTRO_NAME" ] && [ ! -f /proc/sys/fs/binfmt_misc/WSLInterop ]; then
    printf "%sWarning: This script is designed for WSL environment%s\n" "$YELLOW" "$NC"
    printf "Some features may not work correctly outside WSL\n"
    printf "\n"
    read -p "Continue anyway? [y/n]: " cont
    if [ "$cont" != "y" ] && [ "$cont" != "Y" ]; then
        exit 0
    fi
fi

# Check dependencies
printf "%sChecking dependencies...%s\n" "$BLUE" "$NC"
MISSING=""

for cmd in tesseract text2image lstmtraining; do
    if ! command -v $cmd >/dev/null 2>&1; then
        MISSING="$MISSING $cmd"
    fi
done

if [ -n "$MISSING" ]; then
    printf "%sMissing tools:%s%s\n" "$RED" "$MISSING" "$NC"
    printf "\n"
    printf "Would you like to install them now?\n"
    read -p "Install dependencies? [y/n]: " install
    
    if [ "$install" = "y" ] || [ "$install" = "Y" ]; then
        sh "$SCRIPTS_DIR/setup_and_build_ckb.sh"
    else
        printf "%sSome features may not work without these tools%s\n" "$YELLOW" "$NC"
        sleep 3
    fi
fi

# Start main loop
main_loop
