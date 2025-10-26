#!/usr/bin/env python3
"""
Simple debug test for generic scraper
"""

import sys
import yaml
from pathlib import Path

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

print("="*60)
print("DEBUG: Testing Generic Scraper")
print("="*60)

try:
    print("\n1. Loading configuration...")
    with open('websites.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"   ✅ Config loaded: {len(config)} websites")
    
    print("\n2. Checking Kurdsat config...")
    kurdsat = config.get('kurdsat')
    if not kurdsat:
        print("   ❌ Kurdsat not found in config!")
        sys.exit(1)
    print(f"   ✅ Kurdsat found: {kurdsat.get('name')}")
    print(f"   Categories: {list(kurdsat.get('categories', {}).keys())}")
    
    print("\n3. Importing generic_scraper...")
    from generic_scraper import GenericScraper
    print("   ✅ Import successful")
    
    print("\n4. Creating scraper instance...")
    scraper = GenericScraper('websites.yaml')
    print(f"   ✅ Scraper created: {scraper.name}")
    print(f"   Config path: {scraper.config_path}")
    print(f"   Websites in config: {len(scraper.config)}")
    
    print("\n5. Testing scrape_category method...")
    print("   Calling: scrape_category('kurdsat', 'news', max_articles=1)")
    
    result = scraper.scrape_category('kurdsat', 'news', max_articles=1)
    
    print(f"\n6. Results:")
    print(f"   Type: {type(result)}")
    print(f"   Result: {result}")
    
    if hasattr(result, '__dict__'):
        for key, value in result.__dict__.items():
            print(f"   {key}: {value}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ Debug test completed")
print("="*60)
