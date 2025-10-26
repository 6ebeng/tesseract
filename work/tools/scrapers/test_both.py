#!/usr/bin/env python3
from generic_scraper import GenericScraper

print("="*70)
print("Testing Both Websites")
print("="*70)

s = GenericScraper('websites.yaml')

# Test Kurdsat
print("\n1. Testing Kurdsat (news category)...")
kurdsat_sentences = s.scrape_category('kurdsat', 'news', max_articles=3)
print(f"   ✅ Extracted {len(kurdsat_sentences)} sentences")
if kurdsat_sentences:
    print(f"   Sample: {kurdsat_sentences[0][:100]}...")

# Reset stats
s.stats = {'articles_processed': 0, 'sentences_extracted': 0, 'duplicates_skipped': 0, 'errors': 0}

# Test NRT
print("\n2. Testing NRT (kurdistan category)...")
nrt_sentences = s.scrape_category('nrt', 'kurdistan', max_articles=3)
print(f"   ✅ Extracted {len(nrt_sentences)} sentences")
if nrt_sentences:
    print(f"   Sample: {nrt_sentences[0][:100]}...")

print("\n" + "="*70)
print(f"TOTAL: {len(kurdsat_sentences) + len(nrt_sentences)} sentences from 6 articles")
print("="*70)
