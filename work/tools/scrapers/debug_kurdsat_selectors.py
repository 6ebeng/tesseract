#!/usr/bin/env python3
"""Debug kurdsat health category selectors"""

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
    url = 'https://kurdsat.tv/ckb/categories/8'
    print(f"Loading: {url}\n")
    
    driver.get(url)
    time.sleep(3)
    
    # Check current selector
    print("1. Testing current selector: a[href*='/ckb/news/']")
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/ckb/news/"]')
    print(f"   Found {len(links)} links")
    if links:
        for i, link in enumerate(links[:3], 1):
            print(f"   {i}. {link.get_attribute('href')}")
    
    # Try alternative selectors
    print("\n2. Testing: a[href*='/ckb/']")
    links2 = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/ckb/"]')
    print(f"   Found {len(links2)} links")
    
    print("\n3. Testing: article a")
    links3 = driver.find_elements(By.CSS_SELECTOR, 'article a')
    print(f"   Found {len(links3)} links")
    
    print("\n4. Testing: .card a")
    links4 = driver.find_elements(By.CSS_SELECTOR, '.card a')
    print(f"   Found {len(links4)} links")
    
    print("\n5. Page source sample:")
    source = driver.page_source
    if 'article' in source.lower():
        print("   ✅ Contains 'article' tag")
    if 'card' in source.lower():
        print("   ✅ Contains 'card' class")
    
    # Check for actual article structure
    print("\n6. Looking for article containers...")
    containers = driver.find_elements(By.TAG_NAME, 'article')
    if containers:
        print(f"   Found {len(containers)} article tags")
        first = containers[0]
        html = first.get_attribute('outerHTML')[:300]
        print(f"   First article HTML: {html}...")

finally:
    driver.quit()
