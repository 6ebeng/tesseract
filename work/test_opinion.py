#!/usr/bin/env python3
"""Test Opinion category specifically"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper

print("=" * 70)
print("🔍 TESTING SHARPRESS OPINION CATEGORY")
print("=" * 70)

url = 'https://www.sharpress.net/opinion.aspx?Cor=Birura&Nawnishan=%D8%A8%DB%8C%D8%B1%D9%88%DA%95%D8%A7'

scraper = SharpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 Testing URL: {url}")
    
    result = scraper._scrape_category("Opinion", url, pages=1)
    
    print(f"\n✅ Opinion: {result} sentences collected")
    
except Exception as e:
    print(f"❌ Opinion failed: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()
        print(f"🔄 Browser closed")

print("=" * 70)
