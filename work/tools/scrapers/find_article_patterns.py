#!/usr/bin/env python3
"""Find actual article link patterns on kurdsat"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

try:
    # Test multiple category pages
    test_urls = [
        ('health', 'https://kurdsat.tv/ckb/categories/8'),
        ('science', 'https://kurdsat.tv/ckb/categories/16'),
        ('tech', 'https://kurdsat.tv/ckb/categories/9'),
    ]
    
    for name, url in test_urls:
        print(f"\n{'='*80}")
        print(f"Testing {name.upper()}: {url}")
        print('='*80)
        
        driver.get(url)
        time.sleep(3)
        
        # Get ALL links
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"\nTotal links on page: {len(all_links)}")
        
        # Filter for article-like URLs
        article_links = []
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/ckb/' in href:
                # Exclude common non-article patterns
                if not any(x in href for x in ['categories', 'menu', 'logo', 'header', 'footer']):
                    article_links.append(href)
        
        print(f"Potential article links: {len(article_links)}")
        
        # Show samples
        unique_links = list(set(article_links))[:5]
        for i, link in enumerate(unique_links, 1):
            print(f"  {i}. {link}")
        
        # Analyze URL patterns
        if article_links:
            patterns = {}
            for link in article_links:
                parts = link.split('/')
                if len(parts) >= 5:
                    pattern = '/'.join(parts[3:5])  # Get pattern after domain
                    patterns[pattern] = patterns.get(pattern, 0) + 1
            
            print(f"\nCommon URL patterns:")
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"  /{pattern}/... ({count} occurrences)")
        
        # Break after first URL for detailed analysis
        break

finally:
    driver.quit()
