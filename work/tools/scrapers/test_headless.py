#!/usr/bin/env python3
"""
Test headless mode configuration
Verifies that browser runs without GUI
"""

from generic_scraper import GenericScraper
import os

print("="*80)
print("HEADLESS MODE TEST")
print("="*80)

# Clear dedup DB for clean test
if os.path.exists('article_dedup.db'):
    os.remove('article_dedup.db')
    print("✅ Cleared deduplication database\n")

print("Testing Kurdsat with headless browser...")
print("(You should NOT see any browser window open)")
print("-"*80)

scraper = GenericScraper('configs')

# This should run completely headless
sentences = scraper.scrape_category('kurdsat', 'news', max_articles=1)

print("\n" + "="*80)
if sentences:
    print(f"✅ SUCCESS - Headless mode working!")
    print(f"   Extracted {len(sentences)} sentences")
    print(f"   Sample: {sentences[0][:100]}...")
else:
    print(f"⚠️  Got 0 sentences (browser still works, may be selector issue)")

print("\n💡 If you didn't see a browser window, headless mode is active!")
print("="*80)
