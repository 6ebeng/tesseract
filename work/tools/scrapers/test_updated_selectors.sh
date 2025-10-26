#!/bin/bash
# Test updated selectors based on legacy scrapers

set -e

cd /mnt/c/tesseract/work/tools/scrapers
source venv/bin/activate

echo "======================================================================"
echo "  Testing Updated Selectors (Based on Legacy Scrapers)"
echo "======================================================================"
echo ""

# Validate updated configuration
echo "[1/3] Validating updated YAML configuration..."
python cli_tools.py validate websites.yaml
echo ""

# Create improved test script
cat > test_selectors.py << 'EOF'
#!/usr/bin/env python3
"""
Test selectors from updated websites.yaml
"""

import yaml
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def test_selector_list(driver, selectors, name="selector"):
    """Test a list of selectors and return first working one"""
    if isinstance(selectors, str):
        selectors = [selectors]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and len(elements) > 0:
                print(f"   ✅ {name}: '{selector}' found {len(elements)} elements")
                return elements
        except:
            pass
    
    print(f"   ❌ {name}: No working selector from {selectors}")
    return []

def main():
    print("\nLoading configuration...")
    with open('websites.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Setup Chrome
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    
    try:
        # Test Kurdsat News
        print("\n" + "="*60)
        print("KURDSAT - News Category")
        print("="*60)
        
        kurdsat = config['kurdsat']
        url = kurdsat['categories']['news']['url']
        
        print(f"\n1. Loading: {url}")
        driver.get(url)
        time.sleep(5)
        
        print(f"   Page title: {driver.title}")
        
        # Test article list selector
        article_selector = kurdsat['selectors']['article_list']
        articles = test_selector_list(driver, article_selector, "Article list")
        
        if len(articles) > 0:
            first_link = articles[0].get_attribute('href')
            print(f"\n2. Testing article page: {first_link}")
            driver.get(first_link)
            time.sleep(3)
            
            # Test title selector
            title_selectors = kurdsat['selectors']['article_title']
            titles = test_selector_list(driver, title_selectors, "Title")
            if titles:
                print(f"   Title text: {titles[0].text[:100]}")
            
            # Test paragraph selector
            para_selectors = kurdsat['selectors']['article_paragraphs']
            paras = test_selector_list(driver, para_selectors, "Paragraphs")
            if paras:
                print(f"   First paragraph: {paras[0].text[:150]}...")
        
        # Test Kurdsat Opinion (different selectors)
        print("\n" + "="*60)
        print("KURDSAT - Opinion Category")
        print("="*60)
        
        opinion_url = kurdsat['categories']['opinion']['url']
        print(f"\n1. Loading: {opinion_url}")
        driver.get(opinion_url)
        time.sleep(5)
        
        opinion_selector = kurdsat['categories']['opinion']['selectors']['article_list']
        articles = test_selector_list(driver, opinion_selector, "Opinion articles")
        
        if len(articles) > 0:
            first_link = articles[0].get_attribute('href')
            print(f"\n2. Testing opinion article: {first_link}")
            driver.get(first_link)
            time.sleep(3)
            
            # Opinion uses different title selector
            title_selectors = kurdsat['categories']['opinion']['selectors']['article_title']
            titles = test_selector_list(driver, title_selectors, "Opinion title")
            if titles:
                print(f"   Title text: {titles[0].text[:100]}")
        
        # Test NRT
        print("\n" + "="*60)
        print("NRT - Kurdistan Category")
        print("="*60)
        
        nrt = config['nrt']
        nrt_url = nrt['categories']['kurdistan']['url']
        
        print(f"\n1. Loading: {nrt_url}")
        driver.get(nrt_url)
        time.sleep(5)
        
        print(f"   Page title: {driver.title}")
        
        # Test article list
        article_selector = nrt['selectors']['article_list']
        articles = test_selector_list(driver, article_selector, "Article list")
        
        # Test titles on list page
        title_selector = nrt['selectors']['article_title']
        titles = test_selector_list(driver, title_selector, "Titles (h2.Name)")
        
        # Test descriptions
        desc_selector = nrt['selectors'].get('article_description', 'p.de')
        descs = test_selector_list(driver, desc_selector, "Descriptions (p.de)")
        
        if len(articles) > 0:
            first_link = articles[0].get_attribute('href')
            print(f"\n2. Testing article page: {first_link}")
            driver.get(first_link)
            time.sleep(3)
            
            # Test content div
            content_selectors = nrt['selectors']['article_content']
            content = test_selector_list(driver, content_selectors, "Content div")
            
            # Test paragraphs
            para_selectors = nrt['selectors']['article_paragraphs']
            paras = test_selector_list(driver, para_selectors, "Paragraphs")
            if paras:
                print(f"   First paragraph: {paras[0].text[:150]}...")
        
        print("\n" + "="*60)
        print("✅ Selector testing completed!")
        print("="*60)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
EOF

# Run selector tests
echo "[2/3] Testing selectors on live pages..."
python test_selectors.py

echo ""
echo "[3/3] Summary..."
echo "✅ Updated selectors based on legacy scrapers tested"
echo ""
echo "Next: Run full extraction test"
echo "  python generic_scraper.py --website kurdsat --category news --max-articles 3"
echo ""
