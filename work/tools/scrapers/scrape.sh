#!/bin/bash
# Quick launcher for production scraper with common configurations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        KURDISH NEWS SCRAPER - PRODUCTION          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Show menu
echo -e "${GREEN}Select scraping mode:${NC}"
echo "  1) Production Mode - All websites (3 workers, with deduplication)"
echo "  2) Fresh Scrape - All websites (clear deduplication first)"
echo "  3) Test Mode - Single website (avanews only)"
echo "  4) Custom - Specify websites and workers"
echo "  5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo -e "${GREEN}Starting production scrape...${NC}"
        python3 run_production_display.py --config configs/websites --all --parallel --workers 3
        ;;
    2)
        echo -e "${YELLOW}WARNING: This will clear deduplication database!${NC}"
        read -p "Are you sure? (y/N): " confirm
        if [[ $confirm == [yY] ]]; then
            echo -e "${GREEN}Starting fresh scrape...${NC}"
            python3 run_production_display.py --config configs/websites --all --parallel --workers 3 --fresh
        else
            echo "Cancelled."
        fi
        ;;
    3)
        echo -e "${GREEN}Starting test scrape (avanews)...${NC}"
        python3 run_production_display.py --config configs/websites --websites avanews --workers 1
        ;;
    4)
        read -p "Enter websites (comma-separated, or 'all'): " websites
        read -p "Enter number of workers [1-5]: " workers
        workers=${workers:-3}
        
        if [[ $websites == "all" ]]; then
            echo -e "${GREEN}Starting scrape with $workers workers...${NC}"
            python3 run_production_display.py --config configs/websites --all --parallel --workers $workers
        else
            echo -e "${GREEN}Starting scrape for: $websites (workers: $workers)${NC}"
            python3 run_production_display.py --config configs/websites --websites $websites --parallel --workers $workers
        fi
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Scraping completed!${NC}"
echo "Check corpus files in: corpus/"
echo "Check logs in: logs/"
