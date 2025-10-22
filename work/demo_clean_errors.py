#!/usr/bin/env python3
"""Force an error to demonstrate clean error messages"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By

print("=" * 70)
print("🧪 DEMONSTRATING CLEAN vs UGLY ERROR MESSAGES")
print("=" * 70)

scraper = LvinpressScraper()
scraper.init_driver()

try:
    # Load a page
    scraper.safe_get("https://lvinpress.com/news/7428", delay=2)
    
    print("\n" + "=" * 70)
    print("BEFORE: Ugly Selenium stacktrace")
    print("=" * 70)
    print("This is what you used to see:\n")
    print("   ⚠️  Content extraction failed: Message: no such element: Unable to locate element")
    print("   (Session info: chrome=141.0.7390.54); For documentation on this error...")
    print("   Stacktrace:")
    print("   #0 0x562acbe3995a <unknown>")
    print("   #1 0x562acb8da536 <unknown>")
    print("   #2 0x562acb92b484 <unknown>")
    print("   ... (18 more lines)")
    
    print("\n" + "=" * 70)
    print("AFTER: Clean concise error")
    print("=" * 70)
    print("This is what you see now:\n")
    
    # Trigger a real error
    try:
        scraper.driver.find_element(By.CSS_SELECTOR, "h1.this-does-not-exist")
    except Exception as e:
        print(f"   ⚠️  {scraper.clean_error(e)} (skipped)")
    
    print("\n✅ Much cleaner!")
    
finally:
    if scraper.driver:
        scraper.driver.quit()

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE")
print("=" * 70)
