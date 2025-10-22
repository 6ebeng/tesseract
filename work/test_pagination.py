#!/usr/bin/env python3
"""Test Sharpress pagination"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper

print("=" * 70)
print("🔍 TESTING SHARPRESS PAGINATION")
print("=" * 70)

# Test with Opinion category (now working) with 3 pages
url = 'https://www.sharpress.net/opinion.aspx?Cor=Birura&Nawnishan=%D8%A8%DB%8C%D8%B1%D9%88%DA%95%D8%A7'

scraper = SharpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 Testing Opinion category with 3 pages")
    print(f"URL: {url}\n")
    
    result = scraper._scrape_category("Opinion", url, pages=3)
    
    print(f"\n{'='*70}")
    print(f"✅ RESULT: {result} sentences collected from 3 pages")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()
        print(f"🔄 Browser closed")

print("=" * 70)
