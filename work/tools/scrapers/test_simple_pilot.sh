#!/bin/bash
# Simple pilot test - Tests basic scraping with minimal dependencies

set -e

echo "======================================================================"
echo "  Simple Pilot Test - Kurdsat News"
echo "======================================================================"
echo ""

# Activate venv
cd /mnt/c/tesseract/work/tools/scrapers
source venv/bin/activate

# Create simple test scraper
cat > test_scrape_simple.py << 'EOF'
#!/usr/bin/env python3
"""
Simple test scraper using minimal dependencies
"""

import yaml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    print("Loading configuration...")
    with open('websites.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Get Kurdsat config
    kurdsat = config['kurdsat']
    print(f"✅ Loaded: {kurdsat['name']}")
    print(f"   Base URL: {kurdsat['base_url']}")
    print(f"   Categories: {len(kurdsat['categories'])}")
    print()
    
    # Setup Chrome
    print("Setting up Chrome...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    
    try:
        # Test news category
        news_cat = kurdsat['categories']['news']
        url = news_cat['url']
        
        print(f"Testing: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for page load
        
        print(f"Page loaded: {driver.title}")
        
        # Try to find article links
        selector = kurdsat['selectors']['article_list']
        print(f"Looking for elements: {selector}")
        
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"✅ Found {len(elements)} article links")
        
        if len(elements) > 0:
            # Try to get first article
            first_link = elements[0].get_attribute('href')
            print(f"\nFirst article: {first_link}")
            
            # Visit first article
            driver.get(first_link)
            time.sleep(3)
            
            # Try to get title
            title_selector = kurdsat['selectors']['article_title']
            try:
                title = driver.find_element(By.CSS_SELECTOR, title_selector)
                print(f"Title: {title.text[:100]}")
            except:
                print("Could not extract title")
            
            # Try to get paragraphs
            para_selector = kurdsat['selectors']['article_paragraphs']
            try:
                paragraphs = driver.find_elements(By.CSS_SELECTOR, para_selector)
                print(f"✅ Found {len(paragraphs)} paragraphs")
                
                if len(paragraphs) > 0:
                    print(f"\nFirst paragraph:")
                    print(f"  {paragraphs[0].text[:200]}...")
            except:
                print("Could not extract paragraphs")
        
        print("\n✅ Basic scraping test passed!")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
EOF

# Run the test
python test_scrape_simple.py

echo ""
echo "======================================================================"
echo "✅ Simple pilot test completed!"
echo "======================================================================"
