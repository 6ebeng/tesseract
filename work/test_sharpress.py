#!/usr/bin/env python3
"""Test Sharpress scraper with updated categories"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper

print("=" * 70)
print("🧪 SHARPRESS SCRAPER TEST (Updated Categories)")
print("=" * 70)
print("\nNew Categories:")
print("  Political: Kurdistan political news")
print("  Specialized: Economy, Sport, Culture, Health, Opinion, Research and Analysis")
print("=" * 70)

scraper = SharpressScraper()

# Test Political (2 pages)
print("\n🧪 Testing Political Scraping (2 pages)...")
try:
    scraper.init_driver()
    political = scraper.scrape_political(pages=2)
    print(f"\n✅ Political: {political} sentences")
except Exception as e:
    print(f"\n❌ Political error: {e}")
finally:
    if scraper.driver:
        scraper.driver.quit()

# Test Specialized (2 pages per category)
print("\n\n🧪 Testing Specialized Scraping (2 pages per category)...")
try:
    scraper.init_driver()
    specialized = scraper.scrape_specialized(pages=2)
    print(f"\n✅ Specialized: {specialized} sentences")
except Exception as e:
    print(f"\n❌ Specialized error: {e}")
finally:
    if scraper.driver:
        scraper.driver.quit()

print("\n" + "=" * 70)
print("✅ RESULTS:")
print(f"Political: {scraper.stats.get('political', 0)} sentences")
print(f"Specialized: {scraper.stats.get('specialized', 0)} sentences")
print(f"Total: {scraper.stats.get('political', 0) + scraper.stats.get('specialized', 0)} sentences")
print("=" * 70)
