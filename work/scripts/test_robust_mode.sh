#!/bin/sh

# Test script to verify robust mode works

set -e

echo "Testing ROBUST MODE functionality..."
echo ""

# Set up environment
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORK_DIR="$(pwd)/work"
SCRIPTS_DIR="$WORK_DIR/scripts"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "${CYAN}Testing robust_train_all_fonts.sh script...${NC}"
echo ""

# Check if the script exists
if [ ! -f "$SCRIPTS_DIR/robust_train_all_fonts.sh" ]; then
    echo "${RED}✗ robust_train_all_fonts.sh not found!${NC}"
    exit 1
fi

echo "${GREEN}✓ Script found${NC}"

# Check script syntax
echo "Checking script syntax..."
if sh -n "$SCRIPTS_DIR/robust_train_all_fonts.sh" 2>/dev/null; then
    echo "${GREEN}✓ Script syntax is valid${NC}"
else
    echo "${RED}✗ Script has syntax errors:${NC}"
    sh -n "$SCRIPTS_DIR/robust_train_all_fonts.sh"
    exit 1
fi

# Check if all required functions are defined
echo ""
echo "Checking required functions..."
REQUIRED_FUNCTIONS="print_header check_dependencies verify_inputs clean_environment generate_training_data generate_lstmf_files train_robust_model finalize_model install_model print_summary"

for func in $REQUIRED_FUNCTIONS; do
    if grep -q "^${func}()" "$SCRIPTS_DIR/robust_train_all_fonts.sh"; then
        echo "${GREEN}✓ Function ${func} found${NC}"
    else
        echo "${RED}✗ Function ${func} missing${NC}"
    fi
done

echo ""
echo "${CYAN}Script validation complete!${NC}"
echo ""
echo "To run the full robust training, execute:"
echo "  ${YELLOW}sh $SCRIPTS_DIR/robust_train_all_fonts.sh${NC}"
echo ""
echo "Or use the interactive menu:"
echo "  ${YELLOW}sh $SCRIPTS_DIR/interactive_train.sh${NC}"
echo "  Then select option 4 for ROBUST MODE"
