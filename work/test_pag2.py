#!/usr/bin/env python3
"""Test Sharpress pagination with fresh browser per page - simpler version"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper

print("=" * 70)
print("🔍 TESTING PAGINATION - 2 PAGES")
print("=" * 70)

# Test with Sport category (simple structure)
url = 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'

scraper = SharpressScraper()

try:
    result = scraper._scrape_category("Sport", url, pages=2)
    
    print(f"\n{'='*70}")
    print(f"✅ FINAL: {result} sentences from 2 pages")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if hasattr(scraper, 'driver') and scraper.driver:
        try:
            scraper.driver.quit()
        except:
            pass

print("=" * 70)
