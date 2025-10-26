#!/usr/bin/env python3
"""
Extract configuration from all legacy scrapers
Creates a summary of URLs, selectors, and pagination types
"""

import re
import os

SCRAPERS = [
    'rudaw_scraper.py',
    'khak_scraper.py',
    'awene_scraper.py',
    'kurdistan24_scraper.py',
    'xendan_scraper.py',
    'sekokurd_scraper.py',
    'govkrd_scraper.py',
    'sharpress_scraper.py',
    'lvinpress_scraper.py',
    'balinde_scraper.py'
]

def extract_info(filepath):
    """Extract key info from scraper file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'name': os.path.basename(filepath).replace('_scraper.py', ''),
        'base_urls': [],
        'selectors': {
            'article_list': [],
            'title': [],
            'content': [],
            'paragraphs': []
        },
        'pagination_type': None,
        'methods': []
    }
    
    # Extract base URLs
    urls = re.findall(r'https?://[^\s\'"]+', content)
    info['base_urls'] = list(set(urls))
    
    # Extract CSS selectors
    css_selectors = re.findall(r'By\.CSS_SELECTOR,\s*["\']([^"\']+)["\']', content)
    info['all_selectors'] = list(set(css_selectors))
    
    # Detect pagination type
    if 'scrollTo' in content or 'scrollHeight' in content:
        info['pagination_type'] = 'infinite_scroll'
    elif 'click' in content.lower() and ('load' in content.lower() or 'more' in content.lower()):
        info['pagination_type'] = 'click_load_more'
    elif 'page' in content.lower() or 'next' in content.lower():
        info['pagination_type'] = 'pagination'
    else:
        info['pagination_type'] = 'unknown'
    
    # Extract methods
    methods = re.findall(r'def (scrape_\w+)', content)
    info['methods'] = methods
    
    return info

print("="*80)
print("LEGACY SCRAPER CONFIGURATION EXTRACTION")
print("="*80)

for scraper_file in SCRAPERS:
    filepath = os.path.join(os.path.dirname(__file__), scraper_file)
    
    if not os.path.exists(filepath):
        print(f"\n❌ {scraper_file}: NOT FOUND")
        continue
    
    info = extract_info(filepath)
    
    print(f"\n{'─'*80}")
    print(f"📄 {info['name'].upper()}")
    print(f"{'─'*80}")
    print(f"Base URLs: {len(info['base_urls'])}")
    for url in info['base_urls'][:3]:
        print(f"  • {url}")
    if len(info['base_urls']) > 3:
        print(f"  ... and {len(info['base_urls']) - 3} more")
    
    print(f"\nPagination: {info['pagination_type']}")
    print(f"Methods: {', '.join(info['methods'])}")
    
    print(f"\nKey Selectors ({len(info['all_selectors'])}):")
    for sel in info['all_selectors'][:5]:
        print(f"  • {sel}")
    if len(info['all_selectors']) > 5:
        print(f"  ... and {len(info['all_selectors']) - 5} more")

print("\n" + "="*80)
print("✅ Extraction complete")
print("="*80)
