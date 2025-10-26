#!/usr/bin/env python3
"""
Migration Test - All 12 Websites
Tests each website with generic_scraper to validate migration
"""

import sys
import time
from generic_scraper import GenericScraper

# Test configuration: (website, category, max_articles)
TESTS = [
    ('kurdsat', 'news', 2),
    ('nrt', 'kurdistan', 2),
    ('rudaw', 'kurdistan', 2),
    ('khak', 'politics', 2),
    ('awene', 'politics', 2),
    ('kurdistan24', 'health', 2),
    ('xendan', 'kurdistan', 2),
    ('sekokurd', 'literature', 2),
    ('govkrd', 'activities', 2),
    ('sharpress', 'kurdistan', 2),
    ('lvinpress', 'all', 2),
    ('balinde', 'all', 2),
]

def main():
    print("="*80)
    print("MIGRATION TEST - ALL 12 WEBSITES")
    print("="*80)
    print(f"Testing {len(TESTS)} website/category combinations")
    print(f"Target: 2 articles per site = ~24-48 sentences total")
    print("="*80)
    
    # Clear deduplication DB
    import os
    if os.path.exists('article_dedup.db'):
        os.remove('article_dedup.db')
        print("✅ Cleared deduplication database\n")
    
    results = {}
    total_sentences = 0
    total_time = 0
    scraper = GenericScraper('websites.yaml')
    
    for i, (website, category, max_articles) in enumerate(TESTS, 1):
        print(f"\n[{i}/{len(TESTS)}] Testing {website.upper()} - {category}")
        print("─"*80)
        
        start = time.time()
        
        try:
            # Reset stats for each test
            scraper.stats = {
                'articles_processed': 0,
                'sentences_extracted': 0,
                'duplicates_skipped': 0,
                'errors': 0
            }
            
            sentences = scraper.scrape_category(website, category, max_articles=max_articles)
            elapsed = time.time() - start
            
            results[website] = {
                'success': True,
                'sentences': len(sentences),
                'articles': scraper.stats['articles_processed'],
                'time': elapsed,
                'sample': sentences[0][:100] if sentences else None
            }
            
            total_sentences += len(sentences)
            total_time += elapsed
            
            print(f"✅ {website}: {len(sentences)} sentences from {scraper.stats['articles_processed']} articles ({elapsed:.1f}s)")
            if sentences:
                print(f"   Sample: {sentences[0][:80]}...")
            
        except Exception as e:
            elapsed = time.time() - start
            results[website] = {
                'success': False,
                'error': str(e),
                'time': elapsed
            }
            total_time += elapsed
            
            print(f"❌ {website}: FAILED - {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*80)
    print("MIGRATION TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results.values() if r.get('success'))
    failed = len(results) - successful
    
    print(f"\nResults:")
    print(f"  ✅ Successful: {successful}/{len(TESTS)}")
    print(f"  ❌ Failed: {failed}/{len(TESTS)}")
    print(f"  📊 Total Sentences: {total_sentences}")
    print(f"  ⏱️  Total Time: {total_time:.1f}s")
    print(f"  ⚡ Avg Speed: {total_sentences/total_time:.1f} sentences/sec")
    
    print("\n" + "─"*80)
    print("Per-Website Results:")
    print("─"*80)
    
    for website, result in sorted(results.items()):
        if result.get('success'):
            print(f"  ✅ {website:15s}: {result['sentences']:3d} sentences from {result['articles']} articles ({result['time']:.1f}s)")
        else:
            print(f"  ❌ {website:15s}: FAILED - {result.get('error', 'Unknown')[:50]}")
    
    print("\n" + "="*80)
    
    # Exit code based on success
    if failed > 0:
        print(f"⚠️  {failed} websites failed - check errors above")
        return 1
    else:
        print("✅ All websites migrated successfully!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
