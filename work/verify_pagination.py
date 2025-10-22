#!/usr/bin/env python3
"""Verify Sharpress pagination - check if different articles are found on each page"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper
from selenium.webdriver.common.by import By
import time

print("=" * 70)
print("🔍 VERIFYING SHARPRESS PAGINATION")
print("=" * 70)

url = 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'

scraper = SharpressScraper()

try:
    scraper.init_driver()
    print(f"✅ Browser initialized")
    print(f"📄 URL: {url}\n")
    
    # Test pages 1, 2, and 3
    for page_num in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"📄 Testing Page {page_num}")
        print(f"{'='*70}")
        
        # Load the base URL
        if not scraper.safe_get(url, delay=3):
            print(f"❌ Failed to load base URL")
            break
        
        # If not page 1, click on the page number
        if page_num > 1:
            time.sleep(2)
            try:
                pagination = scraper.driver.find_element(By.ID, "ctl00_Main_PeopleDataPager")
                page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.numericbutton")
                
                clicked = False
                for button in page_buttons:
                    button_text = button.text.strip()
                    if button_text == str(page_num):
                        print(f"   Clicking page {page_num} button...")
                        scraper.driver.execute_script("arguments[0].scrollIntoView();", button)
                        time.sleep(1)
                        button.click()
                        time.sleep(3)
                        clicked = True
                        print(f"   ✅ Clicked page {page_num}")
                        break
                
                if not clicked:
                    print(f"   ❌ Page {page_num} button not found")
                    break
            except Exception as e:
                print(f"   ❌ Pagination error: {e}")
                break
        
        # Find articles on this page
        article_links = scraper.driver.find_elements(By.CSS_SELECTOR, "div.more-news-page ul li a")
        
        articles = []
        for link_elem in article_links[:5]:  # Just check first 5
            try:
                href = link_elem.get_attribute('href')
                title = link_elem.find_element(By.TAG_NAME, "h2").text.strip()
                if href and 'all-detail.aspx' in href:
                    articles.append({
                        'url': href,
                        'title': title[:50] + "..." if len(title) > 50 else title
                    })
            except:
                continue
        
        print(f"   Found {len(articles)} articles:")
        for i, art in enumerate(articles, 1):
            article_id = art['url'].split('=')[-1] if '=' in art['url'] else 'unknown'
            print(f"   {i}. ID:{article_id} - {art['title']}")
    
    print(f"\n{'='*70}")
    print(f"✅ Verification complete")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper.driver:
        scraper.driver.quit()
        print(f"🔄 Browser closed")

print("=" * 70)
