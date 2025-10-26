#!/usr/bin/env python3
"""
Test script for Balinde scraper
"""

import sys
from generic_scraper import GenericScraper
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_balinde_quick():
    """Quick test: 2 articles from kurdish_poetry"""
    print("="*80)
    print("🧪 QUICK TEST: BALINDE KURDISH POETRY (2 articles)")
    print("="*80)
    print()
    
    scraper = GenericScraper('configs/')
    
    try:
        print("🔍 Starting scraping...\n")
        sentences = scraper.scrape_category('balinde', 'kurdish_poetry', max_articles=2)
        
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        print(f"Sentences extracted: {len(sentences)}")
        
        if sentences:
            print(f"\nFirst 5 sentences:")
            for i, sent in enumerate(sentences[:5], 1):
                # Truncate long poetry lines
                display = sent[:100] + "..." if len(sent) > 100 else sent
                print(f"  {i}. {display}")
            
            print(f"\n✅ QUICK TEST PASSED!")
            return True
        else:
            print(f"\n❌ QUICK TEST FAILED - No sentences extracted")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_balinde():
    """Full test: Both categories"""
    print("="*80)
    print("🧪 FULL TEST: BALINDE (Kurdish Poetry + Articles)")
    print("="*80)
    print()
    
    scraper = GenericScraper('configs/')
    
    categories = ['kurdish_poetry', 'articles']
    results = {}
    
    try:
        for category in categories:
            print(f"\n{'='*60}")
            print(f"📂 Testing category: {category}")
            print('='*60)
            
            sentences = scraper.scrape_category('balinde', category, max_articles=5)
            results[category] = len(sentences)
            
            print(f"\n✅ {category}: {len(sentences)} sentences")
            
            if sentences:
                print(f"Sample (first 3):")
                for i, sent in enumerate(sentences[:3], 1):
                    display = sent[:80] + "..." if len(sent) > 80 else sent
                    print(f"  {i}. {display}")
        
        print("\n" + "="*60)
        print("📊 FINAL RESULTS")
        print("="*60)
        for cat, count in results.items():
            print(f"  {cat}: {count} sentences")
        
        total = sum(results.values())
        print(f"\n  TOTAL: {total} sentences")
        
        if total > 0:
            print(f"\n✅ FULL TEST PASSED!")
            return True
        else:
            print(f"\n❌ FULL TEST FAILED - No sentences extracted")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Balinde scraper')
    parser.add_argument('--quick', action='store_true', help='Run quick test (2 articles)')
    parser.add_argument('--full', action='store_true', help='Run full test (both categories)')
    
    args = parser.parse_args()
    
    if args.full:
        success = test_balinde()
    else:
        # Default to quick test
        success = test_balinde_quick()
    
    sys.exit(0 if success else 1)
