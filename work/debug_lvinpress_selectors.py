#!/usr/bin/env python3
"""Debug script to check Lvinpress HTML structure"""
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Setup Chrome with explicit path
service = Service('/usr/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=service, options=options)

try:
    # Load an article
    url = "https://lvinpress.com/2025/01/21/turkiye-plans-to-provide-military-equipment-to-syria/"
    print(f"Loading: {url}\n")
    driver.get(url)
    time.sleep(5)  # Wait longer for JS
    
    # Test title selectors
    print("1. Testing title selectors:")
    for selector in ["h1.elementor-heading-title", "h1", "h2.elementor-heading-title", "h2"]:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"   ✓ {selector}: {elem.text[:80]}")
            break
        except:
            print(f"   ✗ {selector} not found")
    
    # Test content selectors
    print("\n2. Testing content selectors:")
    selectors_to_try = [
        "div.elementor-widget-theme-post-content div.elementor-widget-container",
        "div.elementor-widget-theme-post-content",
        "article.post",
        "div.entry-content",
        ".post-content"
    ]
    
    for selector in selectors_to_try:
        try:
            content = driver.find_element(By.CSS_SELECTOR, selector)
            text = content.text.strip()
            print(f"   ✓ {selector}: {len(text)} chars")
            print(f"     First 150 chars: {text[:150]}")
            break
        except:
            print(f"   ✗ {selector} not found")
    
    # Test paragraph selector directly
    print("\n3. Testing paragraph selectors:")
    for selector in ["div.elementor-widget-theme-post-content p", "article p", "p"]:
        try:
            ps = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   ✓ {selector}: {len(ps)} paragraphs")
            if ps:
                for i, p in enumerate(ps[:2], 1):
                    text = p.text.strip()
                    if text and len(text) > 20:
                        print(f"     {i}. {text[:100]}...")
            break
        except Exception as e:
            print(f"   ✗ {selector}: {e}")
    
    # Get page source to see structure
    print("\n4. Checking page structure:")
    source = driver.page_source
    if "elementor" in source:
        print("   ✓ Page has Elementor classes")
    else:
        print("   ✗ No Elementor classes found")
    
    if "<article" in source:
        print("   ✓ Page has <article> tags")
    else:
        print("   ✗ No <article> tags")
    
finally:
    driver.quit()
    print("\n✓ Done")
