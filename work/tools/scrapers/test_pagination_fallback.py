#!/usr/bin/env python3
"""
Test Pagination Fallback Pattern
Demonstrates how category settings override website defaults
"""

import yaml
from pathlib import Path

print("="*80)
print("PAGINATION FALLBACK PATTERN TEST")
print("="*80)

# Load Kurdsat config to demonstrate fallback
config_path = Path('configs/kurdsat.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

website_defaults = config.get('pagination', {})

print("\n1. Website Defaults (Kurdsat):")
print(f"   Type: {website_defaults.get('type', 'NOT SET')}")
print(f"   Pages: {website_defaults.get('pages', 'NOT SET')}")

print("\n2. Category Configurations:")
print("-"*80)

for cat_name, cat_config in config['categories'].items():
    print(f"\n📂 {cat_name.upper()}")
    print(f"   URL: {cat_config['url']}")
    
    # Show what's configured
    cat_type = cat_config.get('type')
    cat_pages = cat_config.get('pages')
    cat_clicks = cat_config.get('clicks')
    cat_scrolls = cat_config.get('scrolls')
    
    # Determine effective settings (with fallback)
    effective_type = cat_type or website_defaults.get('type', 'pagination')
    
    if effective_type == 'pagination':
        effective_pages = cat_pages or website_defaults.get('pages', 5)
        print(f"   Effective Type: {effective_type}")
        print(f"   Effective Pages: {effective_pages}")
        
        if cat_type:
            print(f"   ✅ Type explicitly set in category")
        else:
            print(f"   ⬇️  Type inherited from website default")
        
        if cat_pages:
            print(f"   ✅ Pages explicitly set in category")
        else:
            print(f"   ⬇️  Pages inherited from website default")
    
    elif effective_type == 'click_load_more':
        effective_clicks = cat_clicks or website_defaults.get('clicks', 10)
        print(f"   Effective Type: {effective_type}")
        print(f"   Effective Clicks: {effective_clicks}")
        print(f"   Load More Button: {cat_config.get('load_more_button', 'NOT SET')}")
        print(f"   ✅ Type explicitly set in category (overrides website default)")
    
    elif effective_type == 'infinite_scroll':
        effective_scrolls = cat_scrolls or website_defaults.get('scrolls', 20)
        print(f"   Effective Type: {effective_type}")
        print(f"   Effective Scrolls: {effective_scrolls}")

print("\n" + "="*80)
print("FALLBACK PATTERN BENEFITS")
print("="*80)
print("""
✅ DRY Principle:
   • Set common pagination once at website level
   • Categories inherit unless they need something different

✅ Maintainability:
   • Change default pagination in one place
   • Affects all categories that don't override

✅ Flexibility:
   • Each category can completely override pagination type
   • Or just tweak specific settings (e.g., more pages)

✅ Clarity:
   • Easy to see which categories are "special"
   • Default behavior is explicit in website config
""")

print("="*80)
print("Testing with GenericScraper...")
print("="*80)

from generic_scraper import GenericScraper

scraper = GenericScraper('configs')

print(f"\n✅ Loaded {len(scraper.config)} websites with fallback pattern support")
print("\nExample: Scraping Kurdsat health category (uses website defaults)...")

# This should work with the fallback pattern
try:
    # Clear dedup for test
    import os
    if os.path.exists('article_dedup.db'):
        os.remove('article_dedup.db')
    
    sentences = scraper.scrape_category('kurdsat', 'health', max_articles=1)
    print(f"   ✅ Success! Extracted {len(sentences)} sentences")
    if sentences:
        print(f"   Sample: {sentences[0][:80]}...")
except Exception as e:
    print(f"   Error: {str(e)[:100]}")

print("\n" + "="*80)
