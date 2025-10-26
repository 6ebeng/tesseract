#!/usr/bin/env python3
"""
Test script for GovKRD (Kurdistan Regional Government) scraper
"""

import sys
from generic_scraper import GenericScraper
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_govkrd_quick():
    """Quick test: 2 articles from activities"""
    print("="*80)
    print("🧪 QUICK TEST: GOVKRD ACTIVITIES (2 articles)")
    print("="*80)
    print()
    
    scraper = GenericScraper('configs/')
    
    try:
        print("🔍 Starting scraping...\n")
        sentences = scraper.scrape_category('govkrd', 'activities', max_articles=2)
        
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        print(f"Sentences extracted: {len(sentences)}")
        
        if sentences:
            print(f"\nFirst 5 sentences:")
            for i, sent in enumerate(sentences[:5], 1):
                # Truncate long sentences
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

def test_govkrd():
    """Full test: More articles and pages"""
    print("="*80)
    print("🧪 FULL TEST: GOVKRD ACTIVITIES (10 articles)")
    print("="*80)
    print()
    
    scraper = GenericScraper('configs/')
    
    try:
        print("🔍 Starting scraping...\n")
        sentences = scraper.scrape_category('govkrd', 'activities', max_articles=10)
        
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        print(f"Sentences extracted: {len(sentences)}")
        
        if sentences:
            print(f"\nFirst 5 sentences:")
            for i, sent in enumerate(sentences[:5], 1):
                display = sent[:100] + "..." if len(sent) > 100 else sent
                print(f"  {i}. {display}")
            
            print(f"\nLast 3 sentences:")
            for i, sent in enumerate(sentences[-3:], len(sentences)-2):
                display = sent[:100] + "..." if len(sent) > 100 else sent
                print(f"  {i}. {display}")
            
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
    
    parser = argparse.ArgumentParser(description='Test GovKRD scraper')
    parser.add_argument('--quick', action='store_true', help='Run quick test (2 articles)')
    parser.add_argument('--full', action='store_true', help='Run full test (10 articles)')
    
    args = parser.parse_args()
    
    if args.full:
        success = test_govkrd()
    else:
        # Default to quick test
        success = test_govkrd_quick()
    
    sys.exit(0 if success else 1)
