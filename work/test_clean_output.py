#!/usr/bin/env python3
"""Test LvinPress with clean error output"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper

print("=" * 70)
print("🧪 TESTING LVINPRESS WITH CLEAN ERROR MESSAGES")
print("=" * 70)

scraper = LvinpressScraper()

# Test with Kurdistan category which has some video articles
print("\n📰 Testing Kurdistan News (including video articles)")
print("=" * 70)
sentences = scraper.scrape_political(pages=1)
print(f"\n✅ Collected: {len(sentences)} sentences")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE - Notice the clean error messages!")
print("=" * 70)
