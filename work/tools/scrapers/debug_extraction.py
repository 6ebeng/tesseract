#!/usr/bin/env python3
"""
Detailed debug for generic scraper - track each step
"""

import yaml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("="*70)
print("DETAILED DEBUG - Generic Scraper Article Extraction")
print("="*70)

# Load config
with open('websites.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

kurdsat = config['kurdsat']
news_cat = kurdsat['categories']['news']

print(f"\n1. Configuration:")
print(f"   URL: {news_cat['url']}")
print(f"   Type: {news_cat['type']}")
print(f"   Article list selector: {kurdsat['selectors']['article_list']}")

# Setup browser
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

try:
    print(f"\n2. Loading page...")
    driver.get(news_cat['url'])
    time.sleep(5)
    print(f"   Title: {driver.title}")
    
    print(f"\n3. Finding article elements...")
    article_selector = kurdsat['selectors']['article_list']
    print(f"   Selector: {article_selector}")
    
    articles = driver.find_elements(By.CSS_SELECTOR, article_selector)
    print(f"   ✅ Found {len(articles)} elements")
    
    print(f"\n4. Extracting hrefs...")
    links = []
    for i, article in enumerate(articles[:5]):  # First 5
        href = article.get_attribute('href')
        tag = article.tag_name
        text = article.text[:50] if article.text else "(no text)"
        print(f"   [{i+1}] tag={tag}, href={href[:60] if href else 'None'}")
        print(f"       text: {text}")
        
        if href:
            links.append(href)
    
    print(f"\n5. Summary:")
    print(f"   Total elements: {len(articles)}")
    print(f"   Links extracted: {len(links)}")
    
    if len(links) > 0:
        print(f"\n6. Testing first article...")
        print(f"   URL: {links[0]}")
        driver.get(links[0])
        time.sleep(3)
        
        print(f"   Page title: {driver.title}")
        
        # Try to find title
        title_selectors = kurdsat['selectors']['article_title']
        print(f"   Title selectors: {title_selectors}")
        
        for sel in title_selectors:
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, sel)
                print(f"   ✅ Title found with '{sel}': {title_elem.text[:100]}")
                break
            except:
                print(f"   ❌ Title not found with '{sel}'")
        
        # Try to find paragraphs
        para_selectors = kurdsat['selectors']['article_paragraphs']
        print(f"\n   Paragraph selectors: {para_selectors}")
        
        for sel in para_selectors:
            try:
                paras = driver.find_elements(By.CSS_SELECTOR, sel)
                if paras:
                    print(f"   ✅ Found {len(paras)} paragraphs with '{sel}'")
                    print(f"   First para: {paras[0].text[:150]}...")
                    break
            except:
                print(f"   ❌ No paragraphs with '{sel}'")
    
    print(f"\n" + "="*70)
    print(f"✅ Debug complete")
    print(f"="*70)

finally:
    driver.quit()
