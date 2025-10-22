#!/usr/bin/env python3
"""Quick test for LvinPress scraper"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper

print("=" * 70)
print("🧪 TESTING LVINPRESS SCRAPER")
print("=" * 70)

scraper = LvinpressScraper()

# Test Kurdistan News category (1 page only)
print("\n" + "=" * 70)
print("📰 Testing Kurdistan News (1 page)")
print("=" * 70)
sentences = scraper.scrape_political(pages=1)
print(f"\n✅ Kurdistan News: {len(sentences)} sentences collected")

# Test Specialized categories (1 page each)
print("\n" + "=" * 70)
print("📂 Testing Specialized Categories (1 page each)")
print("=" * 70)
sentences = scraper.scrape_specialized(pages=1)
print(f"\n✅ Specialized: {len(sentences)} sentences collected")

print("\n" + "=" * 70)
print("✅ LVINPRESS TEST COMPLETE")
print("=" * 70)
