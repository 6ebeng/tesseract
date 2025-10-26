#!/usr/bin/env python3
"""
Test script for Lvinpress website scraper
"""

import sys
import os
import sqlite3

# Add tools/scrapers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'scrapers'))

from generic_scraper import GenericScraper

def clear_dedup_db():
    """Clear the article deduplication database."""
    db_path = 'article_dedup.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Cleared {db_path}\n")

def main():
    print("=" * 80)
    print("LVINPRESS TEST")
    print("=" * 80)
    
    # Clear deduplication database
    clear_dedup_db()
    
    # Test configuration
    config_path = 'tools/scrapers/configs/'
    
    print("📋 Configuration:")
    print(f"   Website: Lvinpress")
    print(f"   Category: kurdistan_news (2 pages, max 10 articles)")
    print()
    
    print("-" * 80)
    print("SCRAPING KURDISTAN NEWS")
    print("-" * 80)
    print()
    
    try:
        scraper = GenericScraper(config_path)
        sentences = scraper.scrape_category(
            website_name='lvinpress',
            category_name='kurdistan_news',
            max_articles=10
        )
        
        print()
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        print(f"✓ Total sentences extracted: {len(sentences)}")
        print()
        
        if sentences:
            print("📝 Sample sentences:")
            for i, sentence in enumerate(sentences[:5], 1):
                display = sentence[:100] + '...' if len(sentence) > 100 else sentence
                print(f"   {i}. {display}")
            
            if len(sentences) > 5:
                print(f"   ... and {len(sentences) - 5} more")
            
            print()
            print("✅ SUCCESS: Lvinpress scraper working!")
        else:
            print("❌ No sentences extracted!")
            print()
            print("Possible issues:")
            print("   1. Website structure may have changed")
            print("   2. Selectors need updating")
            print("   3. Pagination URL format incorrect")
            sys.exit(1)
            
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print()
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
