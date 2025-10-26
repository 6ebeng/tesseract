#!/usr/bin/env python3
"""Full test for Lvinpress scraper"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'scrapers'))

from generic_scraper import GenericScraper

print("Creating scraper...")
scraper = GenericScraper('tools/scrapers/configs/')

print("\nScraping Lvinpress kurdistan_news (10 articles)...")
result = scraper.scrape_category('lvinpress', 'kurdistan_news', max_articles=10)

print(f"\n✅ Total: {len(result)} sentences\n")

if result:
    print("First 10 sentences:")
    for i, sent in enumerate(result[:10], 1):
        # Clean HTML tags
        clean = sent.replace('<span data-mce-type="bookmark"', '').replace('</span>', '')
        clean = clean[:120] + '...' if len(clean) > 120 else clean
        print(f"  {i}. {clean}")
else:
    print("❌ No sentences extracted!")
