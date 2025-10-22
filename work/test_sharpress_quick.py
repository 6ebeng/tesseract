#!/usr/bin/env python3
"""Quick test of Sharpress scraper with updated categories"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper

print("=" * 70)
print("🧪 SHARPRESS SCRAPER QUICK TEST")
print("=" * 70)
print("\nTesting Updated Categories:")
print("  Political: Kurdistan political news")
print("  Specialized: Economy, Sport, Culture, Health, Opinion, Research")
print("=" * 70)

scraper = SharpressScraper()

# Test Political (1 page only for quick verification)
print("\n🧪 Testing Political (1 page)...")
try:
    scraper.init_driver()
    political = scraper.scrape_political(pages=1)
    print(f"✅ Political: {political} sentences")
except Exception as e:
    print(f"❌ Political error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if scraper.driver:
        scraper.driver.quit()

# Test Specialized (1 page per category for quick verification)
print("\n🧪 Testing Specialized (1 page per category)...")
try:
    scraper.init_driver()
    specialized = scraper.scrape_specialized(pages=1)
    print(f"✅ Specialized: {specialized} sentences")
except Exception as e:
    print(f"❌ Specialized error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if scraper.driver:
        scraper.driver.quit()

print("\n" + "=" * 70)
print("✅ FINAL RESULTS:")
print(f"Political: {scraper.stats.get('political', 0)} sentences")
print(f"Specialized: {scraper.stats.get('specialized', 0)} sentences")
print(f"Total: {scraper.stats.get('political', 0) + scraper.stats.get('specialized', 0)} sentences")
print("=" * 70)
