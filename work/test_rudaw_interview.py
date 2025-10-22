#!/usr/bin/env python3
"""Test Rudaw Interview category"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import RudawScraper

print("=" * 70)
print("🧪 TESTING RUDAW INTERVIEW CATEGORY")
print("=" * 70)

scraper = RudawScraper()

# Test Interview category (5 scrolls)
print("\n📂 Testing Interview category (5 scrolls)")
print("=" * 70)

try:
    scraper.init_driver()
    
    url = 'https://www.rudaw.net/sorani/news?CategoryID=412627'
    
    if not scraper.safe_get(url, delay=3):
        print("❌ Failed to load Interview category")
        exit(1)
    
    print(f"✅ Loaded: {url}")
    
    # Scroll to load more articles
    import time
    for i in range(5):
        scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        print(f"   Scrolled {i+1}/5 times...")
    
    # Find article links
    from selenium.webdriver.common.by import By
    articles = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/sorani/']")
    
    print(f"\n✅ Found {len(articles)} article links")
    
    # Try to visit first 3 articles
    import re
    visited = 0
    sentences = 0
    
    for article in articles[:30]:
        if visited >= 3:
            break
        
        try:
            link = article.get_attribute('href')
            if not link or '/sorani/' not in link:
                continue
            
            # Only actual articles (URLs ending with numbers)
            if not re.search(r'/\d+$', link):
                continue
            
            print(f"\n   [{visited+1}] {link}")
            
            if not scraper.safe_get(link, delay=1):
                continue
            
            visited += 1
            
            # Extract content
            content_divs = scraper.driver.find_elements(By.CSS_SELECTOR, ".content div")
            
            article_sents = 0
            for div in content_divs:
                text = div.text.strip()
                if len(text) < 30:
                    continue
                
                # Split into sentences
                sents = re.split(r'[.؟!،]\s*', text)
                for sent in sents:
                    if scraper.add_sentence(sent):
                        article_sents += 1
                        sentences += 1
            
            print(f"       ✅ {article_sents} sentences")
            
        except Exception as e:
            print(f"       ⚠️  {scraper.clean_error(e)}")
            continue
    
    print("\n" + "=" * 70)
    print(f"✅ Interview category test complete")
    print(f"   Visited: {visited} articles")
    print(f"   Collected: {sentences} sentences")
    print("=" * 70)
    
finally:
    if scraper.driver:
        scraper.driver.quit()
