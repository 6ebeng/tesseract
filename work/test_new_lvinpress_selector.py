#!/usr/bin/env python3
"""Test new Lvinpress selectors"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

service = Service('/usr/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=service, options=options)

try:
    # Test on category page
    url = "https://lvinpress.com/category/news/kurdistan"
    print(f"Testing article list selector on: {url}\n")
    driver.get(url)
    time.sleep(5)
    
    # Test new selector
    print("Testing: article.elementor-post > div > a")
    try:
        articles = driver.find_elements(By.CSS_SELECTOR, "article.elementor-post > div > a")
        print(f"✓ Found {len(articles)} article links\n")
        
        if articles:
            print("First 5 article URLs:")
            for i, article in enumerate(articles[:5], 1):
                url = article.get_attribute('href')
                print(f"  {i}. {url}")
            
            # Test loading first article
            if articles:
                first_url = articles[0].get_attribute('href')
                print(f"\n{'='*60}")
                print(f"Testing article extraction: {first_url}")
                print('='*60)
                
                driver.get(first_url)
                time.sleep(5)
                
                # Check page structure
                page_source = driver.page_source
                print("\nPage source contains:")
                print(f"  'entry-content': {'✓' if 'entry-content' in page_source else '✗'}")
                print(f"  'ast-article-single': {'✓' if 'ast-article-single' in page_source else '✗'}")
                print(f"  'elementor-widget-theme-post-content': {'✓' if 'elementor-widget-theme-post-content' in page_source else '✗'}")
                
                # Try different content selectors
                print("\nTrying content selectors:")
                
                selectors = [
                    ".entry-content",
                    ".entry-content p",
                    "article p",
                    ".ast-article-single p",
                    "main p"
                ]
                
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            total_text = " ".join([e.text for e in elements if e.text.strip()])
                            print(f"  ✓ {selector}: {len(elements)} elements, {len(total_text)} chars")
                            if total_text:
                                print(f"    Sample: {total_text[:100]}...")
                    except Exception as e:
                        print(f"  ✗ {selector}: {str(e)[:60]}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Compare with old selector
    print("\n" + "="*60)
    print("Comparing with old selector:")
    print("="*60)
    driver.get("https://lvinpress.com/category/news/kurdistan")
    time.sleep(5)
    
    print("\nOld: article.elementor-post h3.elementor-post__title a")
    try:
        old_articles = driver.find_elements(By.CSS_SELECTOR, "article.elementor-post h3.elementor-post__title a")
        print(f"  Found {len(old_articles)} articles")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\nNew: article.elementor-post > div > a")
    try:
        new_articles = driver.find_elements(By.CSS_SELECTOR, "article.elementor-post > div > a")
        print(f"  Found {len(new_articles)} articles")
    except Exception as e:
        print(f"  ✗ Error: {e}")

finally:
    driver.quit()
