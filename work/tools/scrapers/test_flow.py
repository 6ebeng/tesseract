#!/usr/bin/env python3
"""
Test the complete scrape_category flow
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Import scraper
from generic_scraper import GenericScraper

print("="*70)
print("Testing Complete scrape_category Flow")
print("="*70)

print("\n1. Creating scraper...")
scraper = GenericScraper('websites.yaml')
print(f"   ✅ Scraper created")
print(f"   Config has {len(scraper.config)} websites")

print("\n2. Calling scrape_category...")
print(f"   Website: kurdsat")
print(f"   Category: news")
print(f"   Max articles: 1")

sentences = scraper.scrape_category('kurdsat', 'news', max_articles=1)

print(f"\n3. Results:")
print(f"   Type: {type(sentences)}")
print(f"   Length: {len(sentences)}")

if sentences:
    print(f"\n4. Sample sentences:")
    for i, sent in enumerate(sentences[:5]):
        print(f"   [{i+1}] {sent[:100]}...")
else:
    print(f"\n❌ NO SENTENCES EXTRACTED")
    print(f"\nDumping scraper stats:")
    print(f"   {scraper.stats}")

print("\n" + "="*70)
