#!/usr/bin/env python3
"""Debug video article structure"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By

print("=" * 70)
print("🔍 DEBUGGING VIDEO ARTICLE HTML STRUCTURE")
print("=" * 70)

test_url = "https://lvinpress.com/video/7431"

scraper = LvinpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 Testing URL: {test_url}\n")
    
    if not scraper.safe_get(test_url, delay=3):
        print(f"❌ Failed to load article")
        exit(1)
    
    print("=" * 70)
    print("TEST 1: Check for h1.elementor-heading-title")
    print("=" * 70)
    
    try:
        title_elem = scraper.driver.find_element(By.CSS_SELECTOR, "h1.elementor-heading-title")
        print(f"✅ Found: {title_elem.text.strip()}")
    except:
        print(f"❌ Not found - trying alternatives...\n")
        
        # Try alternative selectors
        selectors = [
            "h1",
            "h1.entry-title",
            "h2.elementor-heading-title",
            "div.elementor-widget-heading h1",
            "div.elementor-widget-heading h2",
            "article h1",
            "article h2"
        ]
        
        for selector in selectors:
            try:
                elem = scraper.driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found with '{selector}': {elem.text.strip()[:60]}...")
                break
            except:
                print(f"   ❌ '{selector}' not found")
    
    print("\n" + "=" * 70)
    print("TEST 2: Check for content div")
    print("=" * 70)
    
    try:
        content_elem = scraper.driver.find_element(
            By.CSS_SELECTOR,
            "div.elementor-widget-theme-post-content div.elementor-widget-container"
        )
        content = content_elem.text.strip()
        print(f"✅ Found content ({len(content)} chars)")
        print(f"First 200 chars: {content[:200]}...")
    except:
        print(f"❌ Not found - trying alternatives...\n")
        
        # Try alternative selectors
        selectors = [
            "div.entry-content",
            "div.post-content",
            "article div.content",
            "div.elementor-widget-container p",
            "div.elementor-text-editor"
        ]
        
        for selector in selectors:
            try:
                elem = scraper.driver.find_element(By.CSS_SELECTOR, selector)
                content = elem.text.strip()
                print(f"✅ Found with '{selector}' ({len(content)} chars)")
                print(f"First 200 chars: {content[:200]}...")
                break
            except:
                print(f"   ❌ '{selector}' not found")
    
    print("\n" + "=" * 70)
    print("TEST 3: Show page source excerpt")
    print("=" * 70)
    
    # Get page source and find relevant parts
    page_source = scraper.driver.page_source
    
    # Find title section
    if '<h1' in page_source:
        start = page_source.find('<h1')
        end = page_source.find('</h1>', start) + 5
        print("H1 section:")
        print(page_source[start:end])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()

print("=" * 70)
