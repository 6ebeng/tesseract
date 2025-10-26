#!/usr/bin/env python3
"""
Generic Scraper Test Suite

Tests all websites configured in scrapers/configs/ directory.
Can test all websites or specific ones via command line arguments.

Usage:
    # Test all websites (first category, 5 articles each)
    python3 test_suite.py
    
    # Test specific websites
    python3 test_suite.py yariga avanews
    
    # Test with more articles
    python3 test_suite.py --max-articles 10
    
    # Test specific websites with custom article count
    python3 test_suite.py yariga rudaw --max-articles 15
    
    # Resume from last run
    python3 test_suite.py --resume
    
    # Start fresh (ignore previous state)
    python3 test_suite.py --fresh
    
    # List all available websites
    python3 test_suite.py --list
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from scrapers.generic_scraper import GenericScraper

# State file for resume functionality
STATE_FILE = Path(__file__).parent / '.test_suite_state.json'

def save_state(state):
    """Save current test state to file"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  Warning: Could not save state: {e}")

def load_state():
    """Load previous test state from file"""
    if not STATE_FILE.exists():
        return None
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
            return state
    except Exception as e:
        print(f"⚠️  Warning: Could not load state: {e}")
        return None

def clear_state():
    """Remove state file (fresh start)"""
    if STATE_FILE.exists():
        try:
            STATE_FILE.unlink()
            print(f"🗑️  Cleared previous state")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear state: {e}")

def list_websites(scraper):
    """List all available websites"""
    print("\n" + "="*60)
    print("📋 Available Websites")
    print("="*60)
    
    websites = sorted(scraper.config.keys())
    for i, website in enumerate(websites, 1):
        config = scraper.config[website]
        enabled = config.get('enabled', True)
        status = "✅ ENABLED" if enabled else "❌ DISABLED"
        name = config.get('name', website)
        categories = list(config.get('categories', {}).keys())
        
        print(f"\n{i}. {website}")
        print(f"   Name: {name}")
        print(f"   Status: {status}")
        print(f"   Categories: {', '.join(categories[:5])}")
        if len(categories) > 5:
            print(f"                {', '.join(categories[5:])}")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(websites)} websites")
    print("="*60)

def test_website(scraper, website_name, max_articles=5, state=None):
    """Test a single website - all enabled categories
    
    Args:
        scraper: GenericScraper instance
        website_name: Name of the website to test
        max_articles: Maximum articles to scrape per category
        state: Previous state dict for resume (optional)
    """
    if website_name not in scraper.config:
        print(f"❌ Website '{website_name}' not found in configs")
        return False
    
    config = scraper.config[website_name]
    
    # Check if enabled
    if not config.get('enabled', True):
        print(f"⚠️  {website_name}: DISABLED - skipping")
        return None
    
    # Get all categories (enabled by default unless explicitly disabled)
    all_categories = config.get('categories', {})
    if not all_categories:
        print(f"❌ {website_name}: No categories defined")
        return False
    
    # Filter to enabled categories
    enabled_categories = {
        cat_name: cat_config 
        for cat_name, cat_config in all_categories.items()
        if cat_config.get('enabled', True)  # Default to enabled if not specified
    }
    
    if not enabled_categories:
        print(f"⚠️  {website_name}: All categories disabled - skipping")
        return None
    
    # Check if resuming from previous state
    completed_categories = set()
    if state and website_name in state.get('completed', {}):
        website_state = state['completed'][website_name]
        completed_categories = set(website_state.get('categories', []))
        if completed_categories:
            print(f"   📌 Resuming: {len(completed_categories)} categories already completed")
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing {website_name}")
    print(f"   Categories: {len(enabled_categories)}/{len(all_categories)} enabled")
    if completed_categories:
        remaining = len(enabled_categories) - len(completed_categories)
        print(f"   Remaining: {remaining} categories to test")
    print(f"{'='*60}")
    
    all_sentences = []
    category_results = {}
    overall_start = datetime.now()
    
    # Test each enabled category (skip already completed ones)
    for cat_name in enabled_categories.keys():
        # Skip if already completed in previous run
        if cat_name in completed_categories:
            print(f"\n   ✓ Category: {cat_name} (already completed)")
            continue
        
        print(f"\n   📂 Category: {cat_name}")
        
        try:
            start_time = datetime.now()
            
            sentences = scraper.scrape_category(
                website_name,
                cat_name,
                max_articles=max_articles
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            all_sentences.extend(sentences)
            category_results[cat_name] = {
                'success': True,
                'sentences': len(sentences),
                'duration': duration
            }
            
            print(f"      ✅ {len(sentences)} sentences in {duration:.1f}s")
            
            # Mark this category as completed
            completed_categories.add(cat_name)
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            category_results[cat_name] = {
                'success': False,
                'sentences': 0,
                'duration': 0,
                'error': str(e)
            }
    
    overall_duration = (datetime.now() - overall_start).total_seconds()
    
    # Summary for this website
    successful_cats = [c for c, r in category_results.items() if r['success']]
    failed_cats = [c for c, r in category_results.items() if not r['success']]
    
    print(f"\n{'='*60}")
    print(f"{'✅' if len(failed_cats) == 0 else '⚠️ '} {website_name}: {'SUCCESS' if len(failed_cats) == 0 else 'PARTIAL'}")
    print(f"   Categories tested: {len(category_results)}")
    print(f"   Successful: {len(successful_cats)}")
    if failed_cats:
        print(f"   Failed: {len(failed_cats)} ({', '.join(failed_cats)})")
    print(f"   Total sentences: {len(all_sentences)}")
    print(f"   Total duration: {overall_duration:.1f}s")
    
    if all_sentences:
        print(f"\n   📝 Sample sentences:")
        for i, sent in enumerate(all_sentences[:3], 1):
            preview = sent[:80] + "..." if len(sent) > 80 else sent
            print(f"   {i}. {preview}")
    
    print(f"{'='*60}")
    
    # Return results including completed categories list
    return {
        'success': len(failed_cats) == 0,
        'completed_categories': list(completed_categories),
        'total_categories': len(enabled_categories)
    }

def main():
    """Main test suite"""
    parser = argparse.ArgumentParser(
        description='Test Kurdish news scraper websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Test all websites
  %(prog)s yariga avanews            # Test specific websites
  %(prog)s --max-articles 10         # Test all with 10 articles each
  %(prog)s yariga --max-articles 15  # Test yariga with 15 articles
  %(prog)s --resume                  # Resume from last run
  %(prog)s --fresh                   # Start fresh (clear previous state)
  %(prog)s --list                    # List all available websites
        """
    )
    
    parser.add_argument(
        'websites',
        nargs='*',
        help='Specific websites to test (space-separated). If omitted, tests all.'
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=5,
        help='Maximum articles to scrape per website (default: 5)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available websites and exit'
    )
    
    parser.add_argument(
        '--enabled-only',
        action='store_true',
        help='Only test enabled websites (skip disabled ones)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last interrupted run'
    )
    
    parser.add_argument(
        '--fresh',
        action='store_true',
        help='Start fresh (ignore previous state)'
    )
    
    args = parser.parse_args()
    
    # Handle fresh start
    if args.fresh:
        clear_state()
    
    # Initialize scraper
    print("\n🔧 Initializing Generic Scraper...")
    scraper = GenericScraper('scrapers/configs/')
    
    # List websites if requested
    if args.list:
        list_websites(scraper)
        return 0
    
    # Load previous state if resuming
    state = None
    if args.resume or (not args.fresh and not args.websites):
        state = load_state()
        if state:
            print(f"📌 Loaded previous state from {state.get('timestamp', 'unknown time')}")
            completed_count = len(state.get('completed', {}))
            if completed_count > 0:
                print(f"   {completed_count} website(s) already completed")
        elif args.resume:
            print(f"⚠️  No previous state found - starting fresh")
    
    # Determine which websites to test
    if args.websites:
        # Test specific websites
        websites_to_test = args.websites
        print(f"\n📝 Testing {len(websites_to_test)} specific website(s)")
    else:
        # Test all websites (exclude examples/templates)
        exclude_patterns = ['EXAMPLE', 'TEMPLATE', 'TEST']
        websites_to_test = sorted([
            w for w in scraper.config.keys()
            if not any(pattern in w.upper() for pattern in exclude_patterns)
        ])
        
        if args.enabled_only:
            websites_to_test = [
                w for w in websites_to_test 
                if scraper.config[w].get('enabled', True)
            ]
            print(f"\n📝 Testing {len(websites_to_test)} enabled website(s) (excluding examples)")
        else:
            print(f"\n📝 Testing all {len(websites_to_test)} website(s) (excluding examples)")
        
        # Filter out fully completed websites if resuming
        if state:
            completed_websites = state.get('completed', {})
            remaining_websites = []
            for w in websites_to_test:
                if w in completed_websites:
                    # Check if all categories completed
                    website_state = completed_websites[w]
                    total_cats = website_state.get('total_categories', 0)
                    completed_cats = len(website_state.get('categories', []))
                    if completed_cats >= total_cats:
                        print(f"   ✓ {w}: Already completed ({completed_cats}/{total_cats} categories)")
                        continue
                remaining_websites.append(w)
            
            websites_to_test = remaining_websites
            if not websites_to_test:
                print("\n✅ All websites already completed!")
                return 0
            
            print(f"\n   📋 {len(websites_to_test)} website(s) remaining to test")
    
    print(f"   Max articles per website: {args.max_articles}")
    
    # Initialize state if not loaded
    if state is None:
        state = {
            'timestamp': datetime.now().isoformat(),
            'max_articles': args.max_articles,
            'completed': {}
        }
    
    # Run tests
    results = {}
    try:
        for i, website in enumerate(websites_to_test, 1):
            print(f"\n{'='*60}")
            print(f"Progress: {i}/{len(websites_to_test)}")
            print(f"{'='*60}")
            
            result = test_website(scraper, website, args.max_articles, state)
            results[website] = result
            
            # Update state after each website
            if result and isinstance(result, dict):
                state['completed'][website] = {
                    'categories': result.get('completed_categories', []),
                    'total_categories': result.get('total_categories', 0),
                    'timestamp': datetime.now().isoformat()
                }
                save_state(state)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print(f"💾 State saved - use --resume to continue from where you left off")
        save_state(state)
        return 1
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = []
    failed = []
    skipped = []
    
    for w, r in results.items():
        if r is None:
            skipped.append(w)
        elif isinstance(r, dict):
            if r.get('success'):
                successful.append(w)
            else:
                failed.append(w)
        elif r is True:
            successful.append(w)
        else:
            failed.append(w)
    
    print(f"\n✅ Successful: {len(successful)}")
    for w in successful:
        print(f"   - {w}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for w in failed:
            print(f"   - {w}")
    
    if skipped:
        print(f"\n⚠️  Skipped: {len(skipped)}")
        for w in skipped:
            print(f"   - {w}")
    
    total = len(results)
    success_rate = (len(successful) / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"Success Rate: {success_rate:.1f}% ({len(successful)}/{total})")
    print(f"{'='*60}\n")
    
    # Clear state if all tests completed successfully
    if len(failed) == 0 and len(successful) > 0:
        print("✅ All tests completed successfully!")
        clear_state()
    elif len(failed) > 0:
        print(f"💾 State saved - use --resume to retry failed tests")
    
    # Exit code: 0 if all tests passed, 1 if any failed
    return 0 if len(failed) == 0 else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
