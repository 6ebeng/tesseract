#!/bin/bash
# Monitor scraper progress

echo "==================================="
echo "Scraper Progress Monitor"
echo "==================================="
echo ""

# Check if process is running
PID=$(cat /tmp/scraper.pid 2>/dev/null)
if [ -n "$PID" ]; then
    if ps -p $PID > /dev/null 2>&1; then
        echo "✓ Scraper is RUNNING (PID: $PID)"
    else
        echo "✗ Scraper process finished"
    fi
else
    echo "✗ No PID file found"
fi

echo ""
echo "Recent log output:"
echo "-----------------------------------"
tail -20 /tmp/scraper_full.log 2>/dev/null || echo "No log yet"
echo ""
echo "-----------------------------------"
echo ""

# Check collected sentences
if [ -f /mnt/c/tesseract/work/corpus/kurdish_news_batch2.txt ]; then
    LINES=$(wc -l < /mnt/c/tesseract/work/corpus/kurdish_news_batch2.txt)
    echo "Sentences collected: $((LINES - 7)) (raw lines: $LINES)"
else
    echo "No output file yet"
fi

echo ""
echo "To watch live: tail -f /tmp/scraper_full.log"
echo "To stop: kill $(cat /tmp/scraper.pid 2>/dev/null)"
