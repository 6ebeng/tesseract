#!/usr/bin/env python3
"""Check raw HTML structure of Lvinpress article"""

import requests
from bs4 import BeautifulSoup

url = 'https://lvinpress.com/2025/01/21/turkiye-plans-to-provide-military-equipment-to-syria/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print('=== Checking for title ===')
h1 = soup.find('h1')
print(f'h1: {h1.get_text(strip=True) if h1 else "Not found"}')

print('\n=== Checking for article content ===')
article = soup.find('article')
print(f'article tag: {"Found" if article else "Not found"}')

print('\n=== Checking for entry-content ===')
entry = soup.find(class_='entry-content')
print(f'entry-content: {"Found" if entry else "Not found"}')
if entry:
    paragraphs = entry.find_all('p')
    print(f'Paragraphs in entry-content: {len(paragraphs)}')
    if paragraphs:
        print(f'First paragraph: {paragraphs[0].get_text(strip=True)[:100]}...')

print('\n=== Looking for post content ===')
post = soup.find(class_='post-content')
print(f'post-content: {"Found" if post else "Not found"}')

print('\n=== Checking all article-like classes ===')
for cls in ['ast-article-inner', 'site-content', 'entry-content', 'ast-post-content', 'main-content']:
    elem = soup.find(class_=cls)
    if elem:
        print(f'{cls}: Found')
        ps = elem.find_all('p')
        print(f'  Contains {len(ps)} paragraphs')
        if ps:
            print(f'  Sample: {ps[0].get_text(strip=True)[:80]}...')

print('\n=== Looking for WordPress post content ===')
main = soup.find('main')
if main:
    print('main tag: Found')
    # Look for content divs
    content_divs = main.find_all('div', recursive=False)
    print(f'Direct child divs: {len(content_divs)}')
