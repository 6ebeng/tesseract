#!/usr/bin/env python3
"""Check what's actually in the Selenium page source"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

service = Service('/usr/bin/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://lvinpress.com/2025/01/21/turkiye-plans-to-provide-military-equipment-to-syria/"
    print(f"Loading: {url}\n")
    driver.get(url)
    time.sleep(10)  # Try waiting longer
    
    page_source = driver.page_source
    
    print("Checking for key classes/tags in page source:")
    print(f"  'entry-content' class: {'✓ Found' if 'entry-content' in page_source else '✗ Not found'}")
    print(f"  'elementor-widget-theme-post-content': {'✓ Found' if 'elementor-widget-theme-post-content' in page_source else '✗ Not found'}")
    print(f"  'elementor-heading-title': {'✓ Found' if 'elementor-heading-title' in page_source else '✗ Not found'}")
    print(f"  '<article': {'✓ Found' if '<article' in page_source else '✗ Not found'}")
    print(f"  '<h1': {'✓ Found' if '<h1' in page_source else '✗ Not found'}")
    
    # Try to find the content with legacy selectors
    print("\nTrying legacy selectors:")
    from selenium.webdriver.common.by import By
    
    try:
        title = driver.find_element(By.CSS_SELECTOR, "h1.elementor-heading-title")
        print(f"  ✓ h1.elementor-heading-title: {title.text[:60]}...")
    except Exception as e:
        print(f"  ✗ h1.elementor-heading-title: {str(e)[:80]}")
    
    try:
        content = driver.find_element(By.CSS_SELECTOR, "div.elementor-widget-theme-post-content div.elementor-widget-container")
        print(f"  ✓ Content div found, text length: {len(content.text)} chars")
        if content.text:
            print(f"    First 100 chars: {content.text[:100]}")
    except Exception as e:
        print(f"  ✗ Content div: {str(e)[:80]}")
    
    # Check what's actually in entry-content
    print("\nChecking entry-content:")
    try:
        entry = driver.find_element(By.CLASS_NAME, "entry-content")
        print(f"  ✓ entry-content found")
        print(f"    Text length: {len(entry.text)} chars")
        print(f"    First 150 chars: {entry.text[:150]}")
        
        # Check paragraphs
        paragraphs = entry.find_elements(By.TAG_NAME, "p")
        print(f"    Contains {len(paragraphs)} <p> tags")
        if paragraphs:
            print(f"    First <p>: {paragraphs[0].text[:100]}")
    except Exception as e:
        print(f"  ✗ entry-content: {e}")

finally:
    driver.quit()
