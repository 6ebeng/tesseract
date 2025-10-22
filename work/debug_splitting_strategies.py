#!/usr/bin/env python3
"""Test different sentence splitting strategies for LvinPress"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import LvinpressScraper
from selenium.webdriver.common.by import By
import re

print("=" * 70)
print("🔍 TESTING SENTENCE SPLITTING STRATEGIES")
print("=" * 70)

# Test with a longer article
test_url = "https://lvinpress.com/news/kurdistan/7337"

scraper = LvinpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 Testing URL: {test_url}\n")
    
    if not scraper.safe_get(test_url, delay=3):
        print(f"❌ Failed to load article")
        exit(1)
    
    # Extract content
    title_elem = scraper.driver.find_element(By.CSS_SELECTOR, "h1.elementor-heading-title")
    title = title_elem.text.strip()
    
    content_elem = scraper.driver.find_element(
        By.CSS_SELECTOR,
        "div.elementor-widget-theme-post-content div.elementor-widget-container"
    )
    content = content_elem.text.strip()
    
    full_text = f"{title}\n{content}"
    
    # Remove لڤین prefix
    text = re.sub(r'^لڤین\s*', '', full_text, flags=re.MULTILINE)
    
    print(f"Full text length: {len(text)} chars")
    print(f"Full text word count: {len(text.split())} words\n")
    
    print("=" * 70)
    print("STRATEGY 1: Current (split on ؟!۔.\\n)")
    print("=" * 70)
    
    sentences1 = re.split(r'[؟!۔\.\n]+', text)
    sentences1 = [s.strip() for s in sentences1 if s.strip()]
    valid1 = [s for s in sentences1 if scraper.is_valid_sentence(s)]
    
    print(f"Total sentences: {len(sentences1)}")
    print(f"Valid sentences: {len(valid1)}")
    print(f"\nFirst 5 sentences:")
    for i, sent in enumerate(sentences1[:5], 1):
        words = len(sent.split())
        print(f"{i}. [{words} words] {sent[:80]}...")
    
    print("\n" + "=" * 70)
    print("STRATEGY 2: Split only on ؟! (question/exclamation)")
    print("=" * 70)
    
    sentences2 = re.split(r'[؟!]+', text)
    sentences2 = [s.strip() for s in sentences2 if s.strip()]
    valid2 = [s for s in sentences2 if scraper.is_valid_sentence(s)]
    
    print(f"Total sentences: {len(sentences2)}")
    print(f"Valid sentences: {len(valid2)}")
    print(f"\nFirst 5 sentences:")
    for i, sent in enumerate(sentences2[:5], 1):
        words = len(sent.split())
        print(f"{i}. [{words} words] {sent[:80]}...")
    
    print("\n" + "=" * 70)
    print("STRATEGY 3: Treat each paragraph as unit, split by newline only")
    print("=" * 70)
    
    sentences3 = re.split(r'\n+', text)
    sentences3 = [s.strip() for s in sentences3 if s.strip()]
    
    # Further split long paragraphs by ۔.؟!
    final_sentences = []
    for para in sentences3:
        if len(para.split()) > 30:
            # Split long paragraph
            parts = re.split(r'[۔\.؟!]+', para)
            final_sentences.extend([p.strip() for p in parts if p.strip()])
        else:
            final_sentences.append(para)
    
    valid3 = [s for s in final_sentences if scraper.is_valid_sentence(s)]
    
    print(f"Total sentences: {len(final_sentences)}")
    print(f"Valid sentences: {len(valid3)}")
    print(f"\nFirst 5 sentences:")
    for i, sent in enumerate(final_sentences[:5], 1):
        words = len(sent.split())
        print(f"{i}. [{words} words] {sent[:80]}...")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print(f"Strategy 1 (current): {len(valid1)} valid sentences")
    print(f"Strategy 2 (minimal): {len(valid2)} valid sentences")
    print(f"Strategy 3 (paragraph): {len(valid3)} valid sentences")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()

print("=" * 70)
