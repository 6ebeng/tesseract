#!/usr/bin/env python3
"""
Create test images by screenshot-ing real Kurdish news articles
This gives us authentic real-world test cases
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def setup_driver():
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=opts)

def screenshot_article(driver, url, output_name):
    """Screenshot a single article and extract its text"""
    try:
        print(f"  📸 {url[:60]}...")
        driver.get(url)
        time.sleep(3)  # Wait for page load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try different selectors
        article = soup.select_one('.article-body') or \
                 soup.select_one('.bodyContentMainParent') or \
                 soup.select_one('.html-content')
        
        if not article:
            print(f"    ❌ Could not find article content")
            return False
        
        # Extract text
        paragraphs = article.find_all(['p', 'div'])
        text_lines = []
        for p in paragraphs:
            txt = ' '.join(p.get_text(separator=' ', strip=True).split())
            if len(txt) > 50:  # Only meaningful paragraphs
                text_lines.append(txt)
        
        if len(text_lines) < 3:
            print(f"    ❌ Not enough text content")
            return False
        
        # Save ground truth
        gt_text = '\n'.join(text_lines[:20])  # First 20 lines
        with open(f'/mnt/c/tesseract/work/real_gt/eval_multi/{output_name}.gt.txt', 
                  'w', encoding='utf-8') as f:
            f.write(gt_text)
        
        # Take screenshot (full page)
        driver.save_screenshot(f'/mnt/c/tesseract/work/real_gt/eval_multi/{output_name}.png')
        
        chars = len(gt_text)
        lines = len(text_lines[:20])
        print(f"    ✅ Saved ({lines} lines, {chars} chars)")
        return True
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    print("="*70)
    print("📸 Creating Real Test Images from Kurdish News Sites")
    print("="*70)
    
    os.makedirs('/mnt/c/tesseract/work/real_gt/eval_multi', exist_ok=True)
    
    driver = setup_driver()
    
    try:
        # Test articles from different sources
        test_articles = [
            # Kurdsat articles
            ('https://kurdsatnews.com/ckb/news/1/52404', 'kurdsat1'),
            ('https://kurdsatnews.com/ckb/news/30/52224', 'kurdsat2'),
            ('https://kurdsatnews.com/ckb/news/2/52375', 'kurdsat3'),
            
            # Rudaw articles  
            ('https://www.rudaw.net/sorani/kurdistan/1910202516', 'rudaw1'),
            ('https://www.rudaw.net/sorani/middleeast/iraq/191020257', 'rudaw2'),
            
            # Khak TV articles
            ('https://www.khaktv.net/article/20167', 'khak1'),
            ('https://www.khaktv.net/article/20159', 'khak2'),
        ]
        
        print(f"\n📋 Capturing {len(test_articles)} articles...\n")
        
        success = 0
        for url, name in test_articles:
            if screenshot_article(driver, url, name):
                success += 1
            time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"✅ Successfully captured {success}/{len(test_articles)} articles")
        print(f"{'='*70}")
        
        # List created files
        print("\n📁 Created test files:")
        os.system('ls -lh /mnt/c/tesseract/work/real_gt/eval_multi/*.png 2>/dev/null')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
