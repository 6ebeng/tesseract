#!/usr/bin/env python3
"""
Test Awene Scraper with V4.0 Config
Tests the generic scraper against awene.yaml config
"""

import sys
import os
from pathlib import Path

# Add scrapers directory to path
scrapers_dir = Path(__file__).parent
sys.path.insert(0, str(scrapers_dir))

from generic_scraper import GenericScraper


def test_awene_quick():
    """Quick test - politics category with 2 articles"""
    print("=" * 80)
    print("🧪 QUICK TEST: AWENE POLITICS (2 articles)")
    print("=" * 80)
    print()
    
    config_dir = scrapers_dir / 'configs'
    
    try:
        # Enable logging for debugging
        import logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        scraper = GenericScraper(str(config_dir))
        print("\n🔍 Starting scraping...")
        sentences = scraper.scrape_category('awene', 'politics', max_articles=2)
        
        print(f"\n{'=' * 60}")
        print("📊 RESULTS")
        print('=' * 60)
        print(f"Sentences extracted: {len(sentences)}")
        
        if sentences:
            print(f"\nFirst 5 sentences:")
            for i, sent in enumerate(sentences[:5], 1):
                print(f"  {i}. {sent[:100]}..." if len(sent) > 100 else f"  {i}. {sent}")
        
        if len(sentences) > 0:
            print("\n✅ QUICK TEST PASSED!")
            return True
        else:
            print("\n❌ QUICK TEST FAILED - No sentences extracted")
            return False
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_awene():
    """Test Awene scraper with all categories"""
    print("=" * 80)
    print("🧪 TESTING AWENE NEWSPAPER SCRAPER (V4.0 Config)")
    print("=" * 80)
    print()
    
    # Initialize scraper with configs directory
    config_dir = scrapers_dir / 'configs'
    print(f"📁 Loading configs from: {config_dir}")
    
    try:
        scraper = GenericScraper(str(config_dir))
        print("✅ Scraper initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return False
    
    # Test categories
    categories = ['politics', 'culture', 'economy']
    
    results = {}
    
    for category in categories:
        print(f"\n{'=' * 60}")
        print(f"📂 Testing Category: {category.upper()}")
        print('=' * 60)
        
        try:
            sentences = scraper.scrape_category('awene', category, max_articles=3)
            
            results[category] = {
                'success': len(sentences) > 0,
                'articles': 3,  # We requested 3
                'sentences': len(sentences),
                'errors': 0
            }
            
            # Print results
            if len(sentences) > 0:
                print(f"✅ {category.upper()}: SUCCESS")
                print(f"   📝 Sentences: {len(sentences)}")
                if sentences:
                    print(f"   Sample: {sentences[0][:80]}...")
            else:
                print(f"❌ {category.upper()}: FAILED - No sentences extracted")
        
        except Exception as e:
            print(f"❌ {category.upper()}: EXCEPTION")
            print(f"   ⚠️  Error: {e}")
            results[category] = {
                'success': False,
                'articles': 0,
                'sentences': 0,
                'errors': 1
            }
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total_articles = sum(r['articles'] for r in results.values())
    total_sentences = sum(r['sentences'] for r in results.values())
    successful = sum(1 for r in results.values() if r['success'])
    
    print(f"\n✅ Successful Categories: {successful}/{len(categories)}")
    print(f"📰 Total Articles Scraped: {total_articles}")
    print(f"📝 Total Sentences Extracted: {total_sentences}")
    
    print("\nDetailed Results:")
    for cat, res in results.items():
        status = "✅" if res['success'] else "❌"
        print(f"  {status} {cat:12} - Articles: {res['articles']:3} | Sentences: {res['sentences']:4} | Errors: {res['errors']}")
    
    print("\n" + "=" * 80)
    
    # Overall success
    if successful == len(categories) and total_sentences > 0:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        print("=" * 80)
        return False


if __name__ == '__main__':
    # Check command line argument
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        success = test_awene_quick()
    else:
        success = test_awene()
    
    sys.exit(0 if success else 1)
