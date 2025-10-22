#!/usr/bin/env python3
"""Check what's in video article content"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By

test_url = "https://lvinpress.com/video/7431"

scraper = LvinpressScraper()

try:
    scraper.init_driver()
    scraper.safe_get(test_url, delay=3)
    
    title_elem = scraper.driver.find_element(By.CSS_SELECTOR, "h2.elementor-heading-title")
    title = title_elem.text.strip()
    
    content_elem = scraper.driver.find_element(
        By.CSS_SELECTOR,
        "div.elementor-widget-theme-post-content div.elementor-widget-container"
    )
    content = content_elem.text.strip()
    
    full_text = f"{title}\n{content}"
    
    print("=" * 70)
    print("FULL TEXT:")
    print("=" * 70)
    print(full_text)
    print("\n" + "=" * 70)
    
    sentences = scraper.split_sentences(full_text)
    print(f"\nSENTENCES ({len(sentences)}):")
    print("=" * 70)
    for i, sent in enumerate(sentences, 1):
        sent = sent.strip()
        words = len(sent.split())
        print(f"{i}. [{words} words] {sent}")
    
finally:
    if scraper.driver:
        scraper.driver.quit()
