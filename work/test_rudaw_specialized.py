#!/usr/bin/env python3
"""Quick test of Rudaw specialized categories including Interview"""

import sys
sys.path.insert(0, '/mnt/c/tesseract/work/tools')

from scrapers import RudawScraper

print("=" * 70)
print("🧪 TESTING RUDAW SPECIALIZED (with Interview)")
print("=" * 70)

scraper = RudawScraper()

# Test specialized categories with just 2 scrolls each for speed
print("\n📚 Testing 5 specialized categories (2 scrolls each)")
print("=" * 70)

sentences = scraper.scrape_specialized(articles_per_category=20)

print(f"\n✅ Total sentences collected: {len(scraper.sentences)}")
print("=" * 70)
