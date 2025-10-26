#!/usr/bin/env python3
"""
Check what NRT config is loaded
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.generic_scraper import GenericScraper

print("Loading GenericScraper with configs/ directory...\n")

scraper = GenericScraper('scrapers/configs/')

print(f"Total websites loaded: {len(scraper.config)}")
print(f"Websites: {list(scraper.config.keys())}\n")

if 'nrt' in scraper.config:
    nrt = scraper.config['nrt']
    print("✓ NRT Configuration:")
    print(f"  Name: {nrt.get('name')}")
    print(f"  Base URL: {nrt.get('base_url')}")
    print(f"  Enabled: {nrt.get('enabled')}")
    print(f"\n  Selectors:")
    selectors = nrt.get('selectors', {})
    print(f"    article_list: {selectors.get('article_list')}")
    print(f"    article_title: {selectors.get('article_title')}")
    print(f"    article_body: {selectors.get('article_body')}")
    print(f"\n  Pagination:")
    pagination = nrt.get('pagination', {})
    print(f"    type: {pagination.get('type')}")
    print(f"    load_more_button: {pagination.get('load_more_button')}")
    print(f"    clicks: {pagination.get('clicks')}")
    print(f"    delay: {pagination.get('delay')}")
    print(f"\n  Categories: {list(nrt.get('categories', {}).keys())}")
    if 'main' in nrt.get('categories', {}):
        main = nrt['categories']['main']
        print(f"    main URL: {main.get('url')}")
        print(f"    main pagination: {main.get('pagination')}")
else:
    print("❌ NRT not found in loaded configs")
