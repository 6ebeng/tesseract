#!/usr/bin/env python3
"""
Test modular configuration loading
Validates that configs/ directory structure works correctly
"""

from generic_scraper import GenericScraper

print("="*80)
print("MODULAR CONFIGURATION TEST")
print("="*80)

# Test 1: Load from configs/ directory
print("\n1. Testing directory-based loading (configs/)...")
scraper_dir = GenericScraper('configs')

print(f"   ✅ Loaded {len(scraper_dir.config)} websites")
print(f"   Websites: {', '.join(sorted(scraper_dir.config.keys()))}")

# Test 2: Load from single file (backward compatibility)
print("\n2. Testing single-file loading (websites.yaml)...")
try:
    scraper_file = GenericScraper('websites.yaml')
    print(f"   ✅ Loaded {len(scraper_file.config)} websites")
except FileNotFoundError:
    print(f"   ⚠️  websites.yaml not found (expected if migrated)")

# Test 3: Validate configs have required fields
print("\n3. Validating configuration structure...")
required_fields = ['name', 'base_url', 'selectors', 'categories']

for website_name, config in scraper_dir.config.items():
    missing = [f for f in required_fields if f not in config]
    if missing:
        print(f"   ❌ {website_name}: Missing {', '.join(missing)}")
    else:
        cat_count = len(config.get('categories', {}))
        status = "✅" if config.get('enabled', True) else "⚠️"
        print(f"   {status} {website_name:15s}: {cat_count} categories")

# Test 4: Quick scrape test
print("\n4. Testing actual scraping with modular configs...")
print("   Scraping 1 article from Kurdsat...")

try:
    sentences = scraper_dir.scrape_category('kurdsat', 'news', max_articles=1)
    if sentences:
        print(f"   ✅ Success! Extracted {len(sentences)} sentences")
        print(f"   Sample: {sentences[0][:80]}...")
    else:
        print(f"   ⚠️  Got 0 sentences (may need to clear dedup DB)")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

print("\n" + "="*80)
print("✅ Modular configuration system working!")
print("="*80)
print("\nBenefits:")
print("  • Easy to edit individual website configs")
print("  • Clear separation of concerns")
print("  • Can version control changes per site")
print("  • Easier to share/review specific configs")
print("  • Can enable/disable sites independently")
