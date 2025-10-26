#!/bin/bash
# Pilot Migration Test Script
# Tests the new YAML-based scraper system with Kurdsat and NRT

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Tesseract Scraper Migration - Pilot Test${NC}"
echo -e "${BLUE}  Testing: Kurdsat + NRT${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Activate virtual environment
echo -e "${YELLOW}[1/7] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Validate configuration
echo -e "${YELLOW}[2/7] Validating YAML configuration...${NC}"
python cli_tools.py validate websites.yaml
echo ""

# Test Kurdsat - Single Category (News)
echo -e "${YELLOW}[3/7] Testing Kurdsat (News category, 3 articles)...${NC}"
echo -e "${BLUE}Command: python generic_scraper.py --website kurdsat --category news --max-articles 3${NC}"
python generic_scraper.py --website kurdsat --category news --max-articles 3 2>&1 | tee logs/pilot_kurdsat_news.log
echo -e "${GREEN}✅ Kurdsat news test completed${NC}"
echo ""

# Test Kurdsat - Multiple Categories
echo -e "${YELLOW}[4/7] Testing Kurdsat (Multiple categories, 2 articles each)...${NC}"
echo -e "${BLUE}Command: python generic_scraper.py --website kurdsat --max-articles 2${NC}"
python generic_scraper.py --website kurdsat --max-articles 2 2>&1 | tee logs/pilot_kurdsat_full.log
echo -e "${GREEN}✅ Kurdsat full test completed${NC}"
echo ""

# Test NRT - Single Category
echo -e "${YELLOW}[5/7] Testing NRT (Kurdistan category, 3 articles)...${NC}"
echo -e "${BLUE}Command: python generic_scraper.py --website nrt --category kurdistan --max-articles 3${NC}"
python generic_scraper.py --website nrt --category kurdistan --max-articles 3 2>&1 | tee logs/pilot_nrt_kurdistan.log
echo -e "${GREEN}✅ NRT kurdistan test completed${NC}"
echo ""

# Test NRT - Multiple Categories
echo -e "${YELLOW}[6/7] Testing NRT (Multiple categories, 2 articles each)...${NC}"
echo -e "${BLUE}Command: python generic_scraper.py --website nrt --max-articles 2${NC}"
python generic_scraper.py --website nrt --max-articles 2 2>&1 | tee logs/pilot_nrt_full.log
echo -e "${GREEN}✅ NRT full test completed${NC}"
echo ""

# Summary
echo -e "${YELLOW}[7/7] Generating summary...${NC}"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  PILOT MIGRATION TEST - SUMMARY${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Count sentences from logs
KURDSAT_NEWS=$(grep -o "Sentences extracted: [0-9]*" logs/pilot_kurdsat_news.log | grep -o "[0-9]*" || echo "0")
KURDSAT_FULL=$(grep -o "Sentences extracted: [0-9]*" logs/pilot_kurdsat_full.log | grep -o "[0-9]*" || echo "0")
NRT_KURDISTAN=$(grep -o "Sentences extracted: [0-9]*" logs/pilot_nrt_kurdistan.log | grep -o "[0-9]*" || echo "0")
NRT_FULL=$(grep -o "Sentences extracted: [0-9]*" logs/pilot_nrt_full.log | grep -o "[0-9]*" || echo "0")

echo -e "${GREEN}Kurdsat Results:${NC}"
echo "  • News (3 articles): $KURDSAT_NEWS sentences"
echo "  • All categories (2 articles each): $KURDSAT_FULL sentences"
echo ""

echo -e "${GREEN}NRT Results:${NC}"
echo "  • Kurdistan (3 articles): $NRT_KURDISTAN sentences"
echo "  • All categories (2 articles each): $NRT_FULL sentences"
echo ""

TOTAL=$((KURDSAT_NEWS + KURDSAT_FULL + NRT_KURDISTAN + NRT_FULL))
echo -e "${GREEN}Total sentences extracted: $TOTAL${NC}"
echo ""

# Check for errors
ERROR_COUNT=$(grep -c "ERROR" logs/pilot_*.log 2>/dev/null || echo "0")
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors detected${NC}"
else
    echo -e "${YELLOW}⚠️  $ERROR_COUNT errors detected (check logs for details)${NC}"
fi
echo ""

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Log files saved to:${NC}"
echo -e "${BLUE}  - logs/pilot_kurdsat_news.log${NC}"
echo -e "${BLUE}  - logs/pilot_kurdsat_full.log${NC}"
echo -e "${BLUE}  - logs/pilot_nrt_kurdistan.log${NC}"
echo -e "${BLUE}  - logs/pilot_nrt_full.log${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

echo -e "${GREEN}✅ Pilot migration test completed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review the log files for any issues"
echo "  2. Validate sentence quality in corpus files"
echo "  3. Compare with old scraper results"
echo "  4. If successful, proceed with remaining 10 websites"
echo ""
