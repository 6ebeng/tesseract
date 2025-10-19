#!/usr/bin/env python3
"""Test Kurdsat button clicking"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

print('Testing Kurdsat button clicking...\n')

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

d = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=opts)
d.get('https://kurdsat.tv/ckb/news')
time.sleep(3)

# Count initial articles
soup = BeautifulSoup(d.page_source, 'html.parser')
links = set()
for a in soup.find_all('a', href=True):
    if 'kurdsatnews.com' in a['href'] and '/news/' in a['href']:
        links.add(a['href'])

print(f'Initial articles: {len(links)}')

# Try clicking button 3 times
for i in range(3):
    try:
        # Try multiple button selectors
        selectors = [
            "//button[contains(text(),'زیاتر ببینە')]",
            "//button[contains(text(),'زیاتر')]",
            "//button[@class and contains(@class,'flex') and contains(text(),'زیاتر')]"
        ]
        
        clicked = False
        for sel in selectors:
            try:
                btn = d.find_element(By.XPATH, sel)
                btn.click()
                print(f'  Click {i+1}: Used selector {sel}')
                clicked = True
                break
            except:
                continue
        
        if not clicked:
            print(f'  Click {i+1}: No button found')
            break
        
        time.sleep(3)  # Wait longer for content to load
        
        # Count articles again
        soup = BeautifulSoup(d.page_source, 'html.parser')
        new_links = set()
        for a in soup.find_all('a', href=True):
            if 'kurdsatnews.com' in a['href'] and '/news/' in a['href']:
                new_links.add(a['href'])
        
        print(f'  After click {i+1}: {len(new_links)} articles (added {len(new_links) - len(links)} new)')
        links = new_links
        
    except Exception as e:
        print(f'  Error on click {i+1}: {e}')
        break

print(f'\nFinal count: {len(links)} unique articles')
print('\nSample articles:')
for url in list(links)[:5]:
    print(f'  - {url}')

d.quit()
