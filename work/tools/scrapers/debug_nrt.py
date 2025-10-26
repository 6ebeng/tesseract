#!/usr/bin/env python3
"""Debug NRT specifically"""

from generic_scraper import GenericScraper
import time

print("Testing NRT Kurdistan category...")
scraper = GenericScraper('websites.yaml')

# Get config
nrt_config = scraper.config['nrt']
print(f"\nNRT Config:")
print(f"  Base URL: {nrt_config['base_url']}")
print(f"  Category: {nrt_config['categories']['kurdistan']}")

# Try scraping
sentences = scraper.scrape_category('nrt', 'kurdistan', max_articles=1)
print(f"\nResult: {len(sentences)} sentences")

if not sentences:
    print("\n❌ No sentences extracted - debugging...")
    print(f"Stats: {scraper.stats}")
