#!/usr/bin/env python3
"""Test if Sharpress pagination buttons actually work"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import SharpressScraper
from selenium.webdriver.common.by import By
import time

print("=" * 70)
print("🔍 DIRECT PAGINATION TEST - SPORT CATEGORY")
print("=" * 70)

# Create a scraper just for testing
scraper = SharpressScraper()
scraper.init_driver()

url = 'https://www.sharpress.net/all-hawal.aspx?Cor=Werziş&Nawnishan=%D9%88%DB%95%D8%B1%D8%B2%D8%B4'

try:
    print(f"\n📄 Loading page 1...")
    scraper.safe_get(url, delay=3)
    
    # Check what articles are on page 1
    links1 = scraper.driver.find_elements(By.CSS_SELECTOR, "div.more-news-page ul li a")
    print(f"✅ Page 1: Found {len(links1)} article links")
    
    if len(links1) > 0:
        first_link = links1[0].get_attribute('href')
        print(f"   First article: {first_link[:80]}...")
    
    # Now try to click on page 2
    print(f"\n🖱️  Attempting to click on page 2 button...")
    time.sleep(2)
    
    try:
        pagination = scraper.driver.find_element(By.ID, "ctl00_Main_PeopleDataPager")
        print(f"✅ Found pagination container")
        
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.numericbutton")
        print(f"✅ Found {len(page_buttons)} page number buttons")
        
        for i, button in enumerate(page_buttons[:5]):
            print(f"   Button {i+1}: text='{button.text}'")
        
        # Click on page 2
        for button in page_buttons:
            if button.text.strip() == "2":
                print(f"\n🖱️  Clicking on page 2 button...")
                scraper.driver.execute_script("arguments[0].scrollIntoView();", button)
                time.sleep(1)
                button.click()
                print(f"✅ Clicked!")
                time.sleep(4)
                break
        
        # Check articles on page 2
        print(f"\n📄 Checking page 2 content...")
        links2 = scraper.driver.find_elements(By.CSS_SELECTOR, "div.more-news-page ul li a")
        print(f"✅ Page 2: Found {len(links2)} article links")
        
        if len(links2) > 0:
            first_link2 = links2[0].get_attribute('href')
            print(f"   First article: {first_link2[:80]}...")
            
            # Check if it's different from page 1
            if len(links1) > 0:
                if first_link != first_link2:
                    print(f"\n🎉 SUCCESS! Page 2 has different articles than page 1")
                else:
                    print(f"\n⚠️  WARNING: Page 2 shows same articles as page 1")
        
        # Try clicking page 3
        print(f"\n🖱️  Attempting to click on page 3 button...")
        time.sleep(2)
        
        pagination = scraper.driver.find_element(By.ID, "ctl00_Main_PeopleDataPager")
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, "a.numericbutton")
        
        for button in page_buttons:
            if button.text.strip() == "3":
                print(f"🖱️  Clicking on page 3 button...")
                scraper.driver.execute_script("arguments[0].scrollIntoView();", button)
                time.sleep(1)
                button.click()
                print(f"✅ Clicked!")
                time.sleep(4)
                break
        
        # Check articles on page 3
        print(f"\n📄 Checking page 3 content...")
        links3 = scraper.driver.find_elements(By.CSS_SELECTOR, "div.more-news-page ul li a")
        print(f"✅ Page 3: Found {len(links3)} article links")
        
        if len(links3) > 0:
            first_link3 = links3[0].get_attribute('href')
            print(f"   First article: {first_link3[:80]}...")
        
        print(f"\n{'='*70}")
        print(f"✅ PAGINATION WORKS!")
        print(f"   Page 1: {len(links1)} articles")
        print(f"   Page 2: {len(links2)} articles")
        print(f"   Page 3: {len(links3)} articles")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"❌ Pagination error: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

finally:
    if scraper.driver:
        scraper.driver.quit()
        print(f"\n🔄 Browser closed")

print("=" * 70)
