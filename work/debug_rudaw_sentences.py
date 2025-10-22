#!/usr/bin/env python3
"""Debug why Rudaw shows same sentence count for all categories"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import RudawScraper
from selenium.webdriver.common.by import By
import time
import re

print("=" * 70)
print("🔍 DEBUGGING RUDAW SENTENCE EXTRACTION")
print("=" * 70)

scraper = RudawScraper()

# Test Interview category in detail
url = 'https://www.rudaw.net/sorani/news?CategoryID=412627'

try:
    scraper.init_driver()
    
    print(f"\n📄 Loading: {url}")
    if not scraper.safe_get(url, delay=3):
        print("❌ Failed to load")
        exit(1)
    
    print("✅ Page loaded")
    
    # Scroll 2 times
    print("\n📜 Scrolling to load more articles...")
    for i in range(2):
        scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
    print("✅ Scrolled")
    
    # Find article links
    articles = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")
    print(f"\n✅ Found {len(articles)} total links")
    
    # Filter for actual article links (ending with numbers)
    article_urls = []
    for article in articles[:50]:
        try:
            link = article.get_attribute('href')
            if link and '/sorani/' in link and re.search(r'/\d+$', link):
                if link not in article_urls:
                    article_urls.append(link)
        except:
            continue
    
    print(f"✅ Filtered to {len(article_urls)} article URLs")
    
    # Visit first 3 articles
    print("\n" + "=" * 70)
    print("VISITING FIRST 3 ARTICLES")
    print("=" * 70)
    
    for idx, link in enumerate(article_urls[:3], 1):
        print(f"\n📄 Article {idx}: {link}")
        
        if not scraper.safe_get(link, delay=2):
            print("   ⚠️  Failed to load")
            continue
        
        # Try to find content
        try:
            content_divs = scraper.driver.find_elements(By.CSS_SELECTOR, ".content div")
            print(f"   Found {len(content_divs)} content divs")
            
            if len(content_divs) == 0:
                # Try alternative selectors
                print("   Trying alternative selectors...")
                content_divs = scraper.driver.find_elements(By.CSS_SELECTOR, "div.content")
                print(f"   Found {len(content_divs)} with 'div.content'")
            
            total_text = 0
            sentences_found = 0
            
            for div in content_divs:
                text = div.text.strip()
                if len(text) < 30:
                    continue
                
                total_text += len(text)
                
                # Split into sentences
                sents = re.split(r'[.؟!،]\s*', text)
                for sent in sents:
                    sent = sent.strip()
                    if scraper.qc.check(sent):
                        sentences_found += 1
            
            print(f"   ✅ Total text: {total_text} chars")
            print(f"   ✅ Valid sentences: {sentences_found}")
            
        except Exception as e:
            print(f"   ❌ Error: {scraper.clean_error(e)}")
    
    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)
    
finally:
    if scraper.driver:
        scraper.driver.quit()
