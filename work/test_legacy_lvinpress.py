#!/usr/bin/env python3
"""Test if legacy lvinpress scraper still works"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools/scrapers')

from lvinpress_scraper import LvinpressScraper

scraper = LvinpressScraper()
print("Testing legacy Lvinpress scraper...")
print("=" * 60)

sentences = scraper.scrape_political(pages=1)

print("\n" + "=" * 60)
print(f"Result: {len(sentences)} sentences extracted")
if sentences:
    print("\nFirst 3 sentences:")
    for i, sent in enumerate(sentences[:3], 1):
        print(f"  {i}. {sent[:80]}...")
else:
    print("❌ LEGACY SCRAPER IS BROKEN - extracted 0 sentences")
