#!/usr/bin/env python3
"""Debug LvinPress article extraction"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By
import re

print("=" * 70)
print("🔍 DEBUGGING LVINPRESS ARTICLE EXTRACTION")
print("=" * 70)

# Test with a known article
test_url = "https://lvinpress.com/news/7428"

scraper = LvinpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 Testing URL: {test_url}\n")
    
    if not scraper.safe_get(test_url, delay=3):
        print(f"❌ Failed to load article")
        exit(1)
    
    print("=" * 70)
    print("STEP 1: Extract Title")
    print("=" * 70)
    
    try:
        title_elem = scraper.driver.find_element(
            By.CSS_SELECTOR,
            "h1.elementor-heading-title"
        )
        title = title_elem.text.strip()
        print(f"Title: {title}")
        print(f"Title length: {len(title)} chars")
        print(f"Title word count: {len(title.split())} words\n")
    except Exception as e:
        print(f"❌ Title extraction failed: {e}\n")
        title = ""
    
    print("=" * 70)
    print("STEP 2: Extract Content")
    print("=" * 70)
    
    try:
        content_elem = scraper.driver.find_element(
            By.CSS_SELECTOR,
            "div.elementor-widget-theme-post-content div.elementor-widget-container"
        )
        content = content_elem.text.strip()
        print(f"Raw content length: {len(content)} chars")
        print(f"Raw content word count: {len(content.split())} words")
        print(f"\nRaw content:\n{'-'*70}")
        print(content)
        print(f"{'-'*70}\n")
    except Exception as e:
        print(f"❌ Content extraction failed: {e}\n")
        content = ""
    
    print("=" * 70)
    print("STEP 3: Combine Title + Content")
    print("=" * 70)
    
    full_text = f"{title}\n{content}"
    print(f"Full text length: {len(full_text)} chars")
    print(f"Full text word count: {len(full_text.split())} words\n")
    
    print("=" * 70)
    print("STEP 4: Split into Sentences")
    print("=" * 70)
    
    # Current splitting logic
    text = re.sub(r'^لڤین\s*', '', full_text, flags=re.MULTILINE)
    sentences = re.split(r'[؟!۔\.\n]+', text)
    
    print(f"Number of sentences after split: {len(sentences)}\n")
    
    for i, sent in enumerate(sentences, 1):
        sent = sent.strip()
        if sent:
            word_count = len(sent.split())
            kurdish_chars = sum(1 for c in sent if '\u0600' <= c <= '\u06FF')
            total_chars = len(sent)
            ratio = kurdish_chars / total_chars if total_chars > 0 else 0
            
            valid = ""
            if word_count < 10:
                valid = "❌ TOO SHORT"
            elif word_count > 30:
                valid = "❌ TOO LONG"
            elif ratio < 0.7:
                valid = f"❌ LOW Kurdish ratio ({ratio:.2%})"
            else:
                valid = "✅ VALID"
            
            print(f"{i}. [{word_count} words, {ratio:.1%} Kurdish] {valid}")
            print(f"   {sent[:100]}{'...' if len(sent) > 100 else ''}\n")
    
    print("=" * 70)
    print("STEP 5: Apply Quality Control")
    print("=" * 70)
    
    valid_sentences = [s for s in sentences if scraper.is_valid_sentence(s.strip())]
    print(f"Valid sentences: {len(valid_sentences)}")
    
    for i, sent in enumerate(valid_sentences, 1):
        print(f"{i}. {sent}\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()
        print(f"🔄 Browser closed")

print("=" * 70)
