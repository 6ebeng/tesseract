#!/usr/bin/env python3
"""
Test updated configs with legacy selectors
"""

from generic_scraper import GenericScraper
import os

# Remove dedup
if os.path.exists('article_dedup.db'):
    os.remove('article_dedup.db')

print("="*80)
print("TESTING UPDATED CONFIGS WITH LEGACY SELECTORS")
print("="*80)

scraper = GenericScraper('configs')

# Test sites that were updated
test_sites = [
    ('kurdsat', 'health', 'Health category with /articles/ selector'),
    ('khak', 'politics', 'Politics with main tag extraction'),
    ('lvinpress', 'all', 'Lvinpress with .entry-content p'),
    ('balinde', 'all', 'Balinde with .entry-content p'),
]

results = {}

for website, category, description in test_sites:
    print(f"\n{'='*80}")
    print(f"Testing {website.upper()} - {category}")
    print(f"Description: {description}")
    print('='*80)
    
    try:
        sentences = scraper.scrape_category(website, category, max_articles=2)
        results[f"{website}/{category}"] = len(sentences)
        
        if sentences:
            print(f"✅ SUCCESS: {len(sentences)} sentences")
            print(f"\nSample sentences:")
            for i, s in enumerate(sentences[:3], 1):
                print(f"  {i}. {s[:100]}...")
        else:
            print(f"⚠️  No sentences extracted (may be dedup or page load issue)")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        results[f"{website}/{category}"] = f"Error: {str(e)[:50]}"

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

for site_cat, result in results.items():
    if isinstance(result, int):
        status = "✅" if result > 0 else "⚠️ "
        print(f"{status} {site_cat}: {result} sentences")
    else:
        print(f"❌ {site_cat}: {result}")

print("\n" + "="*80)
print("Next: Test remaining sites and compare with legacy baseline")
print("="*80)
