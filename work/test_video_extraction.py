#!/usr/bin/env python3
"""Test LvinPress with video article"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By

print("=" * 70)
print("🧪 TESTING VIDEO ARTICLE EXTRACTION")
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
    
    # Extract using updated logic
    title = ""
    try:
        title_elem = scraper.driver.find_element(
            By.CSS_SELECTOR,
            "h1.elementor-heading-title"
        )
        title = title_elem.text.strip()
        print(f"✅ Title (h1): {title}")
    except:
        try:
            title_elem = scraper.driver.find_element(
                By.CSS_SELECTOR,
                "h2.elementor-heading-title"
            )
            title = title_elem.text.strip()
            print(f"✅ Title (h2): {title}")
        except:
            print(f"❌ No title found")
    
    # Content
    try:
        content_elem = scraper.driver.find_element(
            By.CSS_SELECTOR,
            "div.elementor-widget-theme-post-content div.elementor-widget-container"
        )
        content = content_elem.text.strip()
        print(f"✅ Content: {len(content)} chars\n")
        
        # Combine and split
        full_text = f"{title}\n{content}"
        sentences = scraper.split_sentences(full_text)
        valid_sentences = [s for s in sentences if scraper.is_valid_sentence(s)]
        
        print(f"Total sentences after split: {len(sentences)}")
        print(f"Valid sentences: {len(valid_sentences)}\n")
        
        print("Valid sentences:")
        for i, sent in enumerate(valid_sentences, 1):
            print(f"{i}. {sent}")
        
    except Exception as e:
        print(f"❌ Content extraction failed: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
