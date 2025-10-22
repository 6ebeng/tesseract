#!/usr/bin/env python3
"""Test Sharpress scraper"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers.sharpress_scraper import SharpressScraper

print("="*70)
print("TESTING SHARPRESS SCRAPER")
print("="*70)

scraper = SharpressScraper()

try:
    print("\n🧪 Testing Political Scraping (2 pages)...")
    pol_count = scraper.scrape_political(pages=2)
    
    print(f"\n✅ Political: {pol_count} sentences")
    
    # Clear for specialized test
    scraper.sentences.clear()
    
    print("\n🧪 Testing Specialized Scraping (2 pages per category)...")
    spec_count = scraper.scrape_specialized(pages=2)
    
    print(f"\n{'='*70}")
    print(f"✅ RESULTS:")
    print(f"   Political: {pol_count} sentences")
    print(f"   Specialized: {spec_count} sentences")
    print(f"   Total: {pol_count + spec_count} sentences")
    print(f"{'='*70}")
    
    if scraper.sentences:
        print(f"\n📄 Sample sentences:")
        for i, sent in enumerate(list(scraper.sentences)[:5], 1):
            print(f"{i}. {sent[:80]}...")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    scraper.cleanup()
    print("\n✅ Test complete")
