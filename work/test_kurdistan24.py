#!/usr/bin/env python3
"""
Test script for Kurdistan24 website scraper with FlareSolverr support.
"""

import sys
import os
import sqlite3
import requests
import time

# Add tools/scrapers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'scrapers'))

from generic_scraper import GenericScraper

def check_flaresolverr():
    """Check if FlareSolverr is running and responsive."""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get('http://localhost:8191', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ FlareSolverr is running: v{data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ FlareSolverr returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for FlareSolverr to start (attempt {attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                print("❌ FlareSolverr is not running on http://localhost:8191")
                print("   Start it with: sudo docker start flaresolverr")
                return False
        except Exception as e:
            print(f"❌ Error checking FlareSolverr: {e}")
            return False
    
    return False

def clear_dedup_db():
    """Clear the article deduplication database."""
    db_path = 'article_dedup.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Cleared {db_path}\n")
    else:
        print(f"✓ No existing {db_path}\n")

def main():
    print("=" * 80)
    print("KURDISTAN24 TEST - FlareSolverr Required")
    print("=" * 80)
    
    # Check FlareSolverr availability
    if not check_flaresolverr():
        print("\n❌ FlareSolverr is required for Kurdistan24")
        print("   This website uses Cloudflare protection")
        sys.exit(1)
    
    print()
    
    # Clear deduplication database
    clear_dedup_db()
    
    # Test configuration
    config_path = 'tools/scrapers/configs/'
    output_file = 'output/kurdistan24_test.txt'
    
    print("📋 Test Configuration:")
    print(f"   Config Dir: {config_path}")
    print(f"   Output: {output_file}")
    print(f"   Website: kurdistan24")
    print(f"   Category: politics (1 page, max 5 articles)")
    print()
    
    # Run scraper
    print("-" * 80)
    print("SCRAPING KURDISTAN24")
    print("-" * 80)
    print()
    
    try:
        scraper = GenericScraper(config_path)
        sentences = scraper.scrape_category(
            website_name='kurdistan24',
            category_name='politics',
            max_articles=5
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
                # Truncate long sentences for display
                display = sentence[:100] + '...' if len(sentence) > 100 else sentence
                print(f"   {i}. {display}")
            
            if len(sentences) > 5:
                print(f"   ... and {len(sentences) - 5} more")
            
            print()
            print(f"✓ Sentences can be written to: {output_file}")
            print()
            print("✅ SUCCESS: Kurdistan24 scraper working with FlareSolverr!")
        else:
            print("❌ No sentences extracted!")
            print()
            print("Possible issues:")
            print("   1. FlareSolverr might be timing out")
            print("   2. Website structure may have changed")
            print("   3. Cloudflare challenge not being solved")
            print("   4. Check selectors in kurdistan24.yaml")
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
