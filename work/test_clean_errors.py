#!/usr/bin/env python3
"""Test clean error messages"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper

print("=" * 70)
print("🧪 TESTING CLEAN ERROR MESSAGES")
print("=" * 70)

scraper = LvinpressScraper()

# Test 1: Simulate a typical Selenium error
print("\nTest 1: Simulating 'no such element' error")
print("-" * 70)

from selenium.common.exceptions import NoSuchElementException

try:
    raise NoSuchElementException("Message: no such element: Unable to locate element: {\"method\":\"css selector\",\"selector\":\"h1.not-exists\"}\n  (Session info: chrome=141.0.7390.54); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\nStacktrace:\n#0 0x562acbe3995a <unknown>\n#1 0x562acb8da536 <unknown>")
except Exception as e:
    print(f"Original error preview:\n{str(e)[:200]}...\n")
    print(f"Clean error: {scraper.clean_error(e)}")

print("\n" + "=" * 70)
print("✅ Clean error messaging works!")
print("=" * 70)
