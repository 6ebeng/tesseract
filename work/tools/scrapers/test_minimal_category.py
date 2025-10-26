#!/usr/bin/env python3
"""Quick test of minimal category with intelligent defaults"""

from generic_scraper import GenericScraper
import os

# Remove dedup
if os.path.exists('article_dedup.db'):
    os.remove('article_dedup.db')

scraper = GenericScraper('configs')

print("Testing MINIMAL category (health - URL only)...")
print("Should inherit: type=pagination, pages=3, enabled=true, all selectors\n")

try:
    sentences = scraper.scrape_category('kurdsat', 'health', max_articles=2)
    print(f"✅ SUCCESS! Extracted {len(sentences)} sentences")
    if sentences:
        print(f"\nFirst 3 sentences:")
        for s in sentences[:3]:
            print(f"  • {s[:100]}...")
    else:
        print("⚠️ No sentences (check selectors)")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
