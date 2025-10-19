#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

url = 'https://www.rudaw.net/sorani'
print(f"Fetching: {url}")

try:
    r = requests.get(url, timeout=15, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)} bytes")
    
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Find all links
    links = soup.find_all('a', href=True)
    print(f"\nTotal links found: {len(links)}")
    
    # Find article links
    article_links = [a['href'] for a in links if '/sorani/' in a['href']]
    print(f"Links with /sorani/: {len(article_links)}")
    
    # Show first 10
    print("\nFirst 10 article links:")
    for i, link in enumerate(article_links[:10], 1):
        print(f"{i}. {link}")
    
except Exception as e:
    print(f"Error: {e}")
