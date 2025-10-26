#!/usr/bin/env python3
"""
Debug Test Tool for Generic Scraper
Allows detailed debugging of websites and categories with extensive logging and controls.

Usage Examples:
    # Debug entire website
    python3 test_debug.py rudaw

    # Debug specific category
    python3 test_debug.py rudaw --category kurdistan

    # Debug with custom article limit
    python3 test_debug.py rudaw --category kurdistan --max-articles 5

    # Debug pagination only (no article extraction)
    python3 test_debug.py rudaw --category kurdistan --pagination-only

    # Debug with headful browser (see what's happening)
    python3 test_debug.py rudaw --headful

    # Debug with verbose logging
    python3 test_debug.py rudaw --verbose

    # Debug selector extraction only
    python3 test_debug.py rudaw --category kurdistan --test-selectors

    # Debug wait strategies
    python3 test_debug.py rudaw --category kurdistan --debug-waits

    # Save screenshots on errors
    python3 test_debug.py rudaw --category kurdistan --screenshots

    # Combine multiple options
    python3 test_debug.py rudaw --category kurdistan --max-articles 3 --headful --verbose --screenshots
"""

import sys
import os
import argparse
import time
import traceback
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scrapers'))

from scrapers.generic_scraper import GenericScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DebugScraper:
    """Debug wrapper for GenericScraper with enhanced logging and controls"""
    
    def __init__(self, website_name, headless=True, verbose=False, screenshots=False):
        self.website_name = website_name
        self.headless = headless
        self.verbose = verbose
        self.screenshots = screenshots
        self.screenshot_dir = Path('debug_screenshots')
        
        if screenshots:
            self.screenshot_dir.mkdir(exist_ok=True)
        
        # Initialize scraper - use configs directory (V5.0+)
        config_path = Path(__file__).parent / 'scrapers' / 'configs'
        self.scraper = GenericScraper(str(config_path))
        
        # Set verbose logging
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        if not self.screenshots or not hasattr(self.scraper, 'driver') or not self.scraper.driver:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.website_name}_{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            self.scraper.driver.save_screenshot(str(filepath))
            logger.info(f"📸 Screenshot saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
    
    def debug_website_config(self):
        """Debug website configuration"""
        print("\n" + "="*80)
        print(f"🔍 DEBUGGING WEBSITE CONFIGURATION: {self.website_name}")
        print("="*80)
        
        if self.website_name not in self.scraper.config:
            print(f"❌ Website '{self.website_name}' not found in config!")
            print(f"\nAvailable websites: {', '.join(self.scraper.config.keys())}")
            return False
        
        config = self.scraper.config[self.website_name]
        
        print(f"\n📋 Website: {config.get('name', 'N/A')}")
        print(f"🌐 Base URL: {config.get('base_url', 'N/A')}")
        print(f"✅ Enabled: {config.get('enabled', True)}")
        print(f"🔄 Click-through: {config.get('click_through_navigation', False)}")
        print(f"🛡️  FlareSolverr: {config.get('use_flaresolverr', False)}")
        
        # Language detection
        if 'language_detection' in config:
            lang_config = config['language_detection']
            print(f"🌍 Language Detection: {lang_config.get('enabled', False)}")
            if lang_config.get('enabled'):
                print(f"   Filter: {lang_config.get('filter', [])}")
        
        # Wait configurations
        print("\n⏱️  Wait Configurations:")
        if 'wait' in config:
            print(f"   wait: {config['wait']}")
        if 'collection_wait' in config:
            print(f"   collection_wait: {config['collection_wait']}")
        if 'article_wait' in config:
            print(f"   article_wait: {config['article_wait']}")
        if 'back_delay' in config:
            print(f"   back_delay: {config['back_delay']}")
        
        # Selectors
        print("\n🎯 Default Selectors:")
        selectors = config.get('selectors', {})
        for key, value in selectors.items():
            if isinstance(value, dict):
                print(f"   {key}: {value.get('selector', value)}")
            elif isinstance(value, list):
                print(f"   {key}: [fallback chain with {len(value)} selectors]")
            else:
                print(f"   {key}: {value}")
        
        # Categories
        print("\n📂 Categories:")
        categories = config.get('categories', {})
        for cat_name, cat_config in categories.items():
            enabled = cat_config.get('enabled', True)
            status = "✅" if enabled else "⏭️ "
            print(f"   {status} {cat_name}")
            print(f"      URL: {cat_config.get('url', 'N/A')}")
            print(f"      Type: {cat_config.get('type', 'pagination')}")
            
            # Category-specific pagination settings
            if cat_config.get('type') == 'url_template':
                if 'page_param' in cat_config:
                    print(f"      Page Param: {cat_config['page_param']}")
                if 'path_template' in cat_config:
                    print(f"      Path Template: {cat_config['path_template']}")
            elif cat_config.get('type') == 'infinite_scroll':
                print(f"      Scrolls: {cat_config.get('scrolls', 'N/A')}")
            elif cat_config.get('type') == 'click_load_more':
                print(f"      Clicks: {cat_config.get('clicks', 'N/A')}")
            
            # Category-specific selectors
            if 'selectors' in cat_config:
                print(f"      Custom Selectors: {len(cat_config['selectors'])} overrides")
        
        return True
    
    def debug_category_config(self, category_name):
        """Debug specific category configuration"""
        print("\n" + "="*80)
        print(f"🔍 DEBUGGING CATEGORY: {self.website_name} / {category_name}")
        print("="*80)
        
        if self.website_name not in self.scraper.config:
            print(f"❌ Website '{self.website_name}' not found!")
            return False
        
        website_config = self.scraper.config[self.website_name]
        categories = website_config.get('categories', {})
        
        if category_name not in categories:
            print(f"❌ Category '{category_name}' not found!")
            print(f"\nAvailable categories: {', '.join(categories.keys())}")
            return False
        
        category_config = categories[category_name]
        
        print(f"\n📂 Category: {category_name}")
        print(f"🌐 URL: {category_config.get('url', 'N/A')}")
        print(f"✅ Enabled: {category_config.get('enabled', True)}")
        print(f"📄 Type: {category_config.get('type', 'pagination')}")
        
        # Pagination settings
        print("\n🔄 Pagination Settings:")
        pagination_type = category_config.get('type', 'pagination')
        print(f"   Type: {pagination_type}")
        
        if pagination_type == 'url_template':
            print(f"   Pages: {category_config.get('pages', 'N/A')}")
            print(f"   Page Param: {category_config.get('page_param', 'N/A')}")
            print(f"   Path Template: {category_config.get('path_template', 'N/A')}")
            print(f"   Delay: {category_config.get('delay', 'N/A')}s")
        elif pagination_type == 'infinite_scroll':
            print(f"   Scrolls: {category_config.get('scrolls', 'N/A')}")
            print(f"   Delay: {category_config.get('delay', 'N/A')}s")
        elif pagination_type == 'click_load_more':
            print(f"   Clicks: {category_config.get('clicks', 'N/A')}")
            print(f"   Delay: {category_config.get('delay', 'N/A')}s")
        
        # Wait configurations (merged with website defaults)
        print("\n⏱️  Wait Configurations:")
        for wait_key in ['wait', 'collection_wait', 'article_wait', 'back_delay']:
            cat_value = category_config.get(wait_key)
            web_value = website_config.get(wait_key)
            
            if cat_value is not None:
                print(f"   {wait_key}: {cat_value} (category override)")
            elif web_value is not None:
                print(f"   {wait_key}: {web_value} (website default)")
        
        # Selectors (show merged view)
        print("\n🎯 Selectors (merged with website defaults):")
        website_selectors = website_config.get('selectors', {})
        category_selectors = category_config.get('selectors', {})
        
        all_selector_keys = set(website_selectors.keys()) | set(category_selectors.keys())
        for key in sorted(all_selector_keys):
            cat_sel = category_selectors.get(key)
            web_sel = website_selectors.get(key)
            
            if cat_sel is not None:
                if isinstance(cat_sel, dict):
                    print(f"   {key}: {cat_sel.get('selector', cat_sel)} (category override)")
                elif isinstance(cat_sel, list):
                    print(f"   {key}: [fallback chain - {len(cat_sel)} selectors] (category override)")
                else:
                    print(f"   {key}: {cat_sel} (category override)")
            elif web_sel is not None:
                if isinstance(web_sel, dict):
                    print(f"   {key}: {web_sel.get('selector', web_sel)} (website default)")
                elif isinstance(web_sel, list):
                    print(f"   {key}: [fallback chain - {len(web_sel)} selectors] (website default)")
                else:
                    print(f"   {key}: {web_sel} (website default)")
        
        return True
    
    def test_selectors(self, category_name):
        """Test selector extraction without full scraping"""
        print("\n" + "="*80)
        print(f"🧪 TESTING SELECTORS: {self.website_name} / {category_name}")
        print("="*80)
        
        try:
            # Initialize driver (V5.0 uses _init_stealth_driver)
            self.scraper._init_stealth_driver()
            
            website_config = self.scraper.config[self.website_name]
            category_config = website_config['categories'][category_name]
            
            # Navigate to category URL
            url = category_config.get('url')
            print(f"\n🌐 Navigating to: {url}")
            self.scraper.driver.get(url)
            time.sleep(3)
            
            self.take_screenshot("page_loaded")
            
            # Test article_list selector
            print("\n📋 Testing article_list selector...")
            merged_config = {**website_config, **category_config}
            article_list_selector = merged_config.get('selectors', {}).get('article_list')
            
            if article_list_selector:
                print(f"   Selector: {article_list_selector}")
                try:
                    elements = self.scraper._find_elements(article_list_selector, website_config)
                    print(f"   ✅ Found {len(elements)} article elements")
                    
                    # Show first few URLs
                    if elements:
                        print("\n   📎 Sample article links:")
                        for i, elem in enumerate(elements[:5], 1):
                            try:
                                link_selector = merged_config.get('selectors', {}).get('article_link', 'a')
                                if link_selector == 'a':
                                    # Try to find link within element
                                    link = elem.find_element('tag name', 'a')
                                else:
                                    link = self.scraper._find_element(link_selector, website_config)
                                
                                if link:
                                    url = link.get_attribute('href')
                                    print(f"      {i}. {url}")
                            except Exception as e:
                                print(f"      {i}. Error extracting link: {e}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    self.take_screenshot("article_list_error")
            else:
                print("   ⚠️  No article_list selector found")
            
            # Test article page selectors (navigate to first article)
            if elements:
                print("\n📄 Testing article page selectors...")
                try:
                    first_elem = elements[0]
                    link_selector = merged_config.get('selectors', {}).get('article_link', 'a')
                    
                    if link_selector == 'a':
                        link = first_elem.find_element('tag name', 'a')
                    else:
                        link = first_elem.find_element('css selector', link_selector)
                    
                    article_url = link.get_attribute('href')
                    print(f"   Navigating to: {article_url}")
                    
                    self.scraper.driver.get(article_url)
                    time.sleep(2)
                    
                    self.take_screenshot("article_page")
                    
                    # Test title selector
                    title_selector = merged_config.get('selectors', {}).get('article_title')
                    if title_selector:
                        print(f"\n   Testing article_title: {title_selector}")
                        try:
                            title_elem = self.scraper._find_element(title_selector, website_config)
                            if title_elem:
                                title = title_elem.text.strip()
                                print(f"   ✅ Title: {title[:100]}...")
                            else:
                                print(f"   ❌ Title element not found")
                        except Exception as e:
                            print(f"   ❌ Error: {e}")
                            self.take_screenshot("title_error")
                    
                    # Test body selector
                    body_selector = merged_config.get('selectors', {}).get('article_body')
                    if body_selector:
                        print(f"\n   Testing article_body: {body_selector}")
                        try:
                            if isinstance(body_selector, dict) and body_selector.get('multiple'):
                                elements = self.scraper._find_elements(body_selector.get('selector'), website_config)
                                if elements:
                                    text = body_selector.get('delimiter', '\n').join([e.text.strip() for e in elements if e.text.strip()])
                                    print(f"   ✅ Body: {len(elements)} elements, {len(text)} chars")
                                    print(f"   Preview: {text[:200]}...")
                                else:
                                    print(f"   ❌ No body elements found")
                            else:
                                body_elem = self.scraper._find_element(body_selector, website_config)
                                if body_elem:
                                    text = body_elem.text.strip()
                                    print(f"   ✅ Body: {len(text)} chars")
                                    print(f"   Preview: {text[:200]}...")
                                else:
                                    print(f"   ❌ Body element not found")
                        except Exception as e:
                            print(f"   ❌ Error: {e}")
                            self.take_screenshot("body_error")
                    
                except Exception as e:
                    print(f"   ❌ Error navigating to article: {e}")
                    self.take_screenshot("navigation_error")
                    traceback.print_exc()
            
            print("\n✅ Selector testing complete")
            
        except Exception as e:
            print(f"\n❌ Error during selector testing: {e}")
            self.take_screenshot("selector_test_error")
            traceback.print_exc()
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.cleanup()
    
    def test_pagination(self, category_name, max_pages=None):
        """Test pagination without article extraction"""
        print("\n" + "="*80)
        print(f"🔄 TESTING PAGINATION: {self.website_name} / {category_name}")
        print("="*80)
        
        try:
            # Initialize driver (V5.0 uses _init_stealth_driver)
            self.scraper._init_stealth_driver()
            
            website_config = self.scraper.config[self.website_name]
            category_config = website_config['categories'][category_name]
            merged_config = {**website_config, **category_config}
            
            pagination_type = category_config.get('type', 'pagination')
            print(f"\n📄 Pagination Type: {pagination_type}")
            
            url = category_config.get('url')
            print(f"🌐 Starting URL: {url}")
            
            self.scraper.driver.get(url)
            time.sleep(3)
            self.take_screenshot("pagination_start")
            
            if pagination_type == 'url_template':
                pages = max_pages or category_config.get('pages', 3)
                page_param = category_config.get('page_param')
                path_template = category_config.get('path_template')
                
                print(f"\n🔢 Testing URL template pagination ({pages} pages)...")
                
                for page in range(1, pages + 1):
                    if page == 1:
                        page_url = url
                    elif page_param:
                        separator = '&' if '?' in url else '?'
                        page_url = f"{url}{separator}{page_param}={page}"
                    elif path_template:
                        page_url = path_template.format(url=url, page=page)
                    else:
                        print(f"   ⚠️  Page {page}: No pagination config found")
                        break
                    
                    print(f"\n   Page {page}/{pages}: {page_url}")
                    
                    try:
                        self.scraper.driver.get(page_url)
                        time.sleep(2)
                        self.take_screenshot(f"page_{page}")
                        
                        # Count articles
                        article_list_selector = merged_config.get('selectors', {}).get('article_list')
                        if article_list_selector:
                            elements = self.scraper._find_elements(article_list_selector, website_config)
                            print(f"   ✅ Found {len(elements)} articles")
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
            
            elif pagination_type == 'infinite_scroll':
                scrolls = max_pages or category_config.get('scrolls', 10)
                print(f"\n📜 Testing infinite scroll ({scrolls} scrolls)...")
                
                for i in range(1, scrolls + 1):
                    print(f"\n   Scroll {i}/{scrolls}")
                    
                    # Get current article count
                    article_list_selector = merged_config.get('selectors', {}).get('article_list')
                    if article_list_selector:
                        before = len(self.scraper._find_elements(article_list_selector, website_config))
                    else:
                        before = 0
                    
                    # Scroll
                    self.scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    self.take_screenshot(f"scroll_{i}")
                    
                    # Get new article count
                    if article_list_selector:
                        after = len(self.scraper._find_elements(article_list_selector, website_config))
                        print(f"   Articles: {before} → {after} (+{after - before})")
                    
            elif pagination_type == 'click_load_more':
                clicks = max_pages or category_config.get('clicks', 5)
                load_more_selector = merged_config.get('selectors', {}).get('load_more_button')
                
                print(f"\n🖱️  Testing load more button ({clicks} clicks)...")
                print(f"   Button selector: {load_more_selector}")
                
                for i in range(1, clicks + 1):
                    print(f"\n   Click {i}/{clicks}")
                    
                    try:
                        # Get current article count
                        article_list_selector = merged_config.get('selectors', {}).get('article_list')
                        if article_list_selector:
                            before = len(self.scraper._find_elements(article_list_selector, website_config))
                        else:
                            before = 0
                        
                        # Find and click button
                        button = self.scraper._find_element(load_more_selector, website_config)
                        if button:
                            button.click()
                            time.sleep(2)
                            self.take_screenshot(f"click_{i}")
                            
                            # Get new article count
                            if article_list_selector:
                                after = len(self.scraper._find_elements(article_list_selector, website_config))
                                print(f"   Articles: {before} → {after} (+{after - before})")
                        else:
                            print(f"   ⚠️  Load more button not found")
                            break
                    
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        break
            
            print("\n✅ Pagination testing complete")
            
        except Exception as e:
            print(f"\n❌ Error during pagination testing: {e}")
            self.take_screenshot("pagination_error")
            traceback.print_exc()
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.cleanup()
    
    def debug_wait_strategies(self, category_name):
        """Debug wait strategies and page load timing"""
        print("\n" + "="*80)
        print(f"⏱️  DEBUGGING WAIT STRATEGIES: {self.website_name} / {category_name}")
        print("="*80)
        
        try:
            # Initialize driver (V5.0 uses _init_stealth_driver)
            self.scraper._init_stealth_driver()
            
            website_config = self.scraper.config[self.website_name]
            category_config = website_config['categories'][category_name]
            
            url = category_config.get('url')
            print(f"\n🌐 Navigating to: {url}")
            
            # Test initial page load wait
            print("\n1️⃣  Testing collection page load wait...")
            start = time.time()
            self.scraper.driver.get(url)
            
            # Check wait configuration
            collection_wait = category_config.get('collection_wait') or website_config.get('collection_wait')
            wait_config = category_config.get('wait') or website_config.get('wait')
            
            if collection_wait:
                print(f"   collection_wait config: {collection_wait}")
            elif wait_config:
                print(f"   wait config: {wait_config}")
            else:
                print(f"   Using default wait")
            
            # Simulate wait (simplified)
            time.sleep(3)
            elapsed = time.time() - start
            print(f"   ✅ Page loaded in {elapsed:.2f}s")
            
            self.take_screenshot("collection_page_loaded")
            
            # Test article page wait
            print("\n2️⃣  Testing article page load wait...")
            article_list_selector = category_config.get('selectors', {}).get('article_list') or website_config.get('selectors', {}).get('article_list')
            
            if article_list_selector:
                elements = self.scraper._find_elements(article_list_selector, website_config)
                if elements:
                    link_selector = category_config.get('selectors', {}).get('article_link') or website_config.get('selectors', {}).get('article_link', 'a')
                    
                    try:
                        if link_selector == 'a':
                            link = elements[0].find_element('tag name', 'a')
                        else:
                            link = self.scraper._find_element(link_selector, website_config)
                        
                        article_url = link.get_attribute('href')
                        print(f"   Navigating to: {article_url}")
                        
                        start = time.time()
                        self.scraper.driver.get(article_url)
                        
                        # Check article wait configuration
                        article_wait = category_config.get('article_wait') or website_config.get('article_wait')
                        
                        if article_wait:
                            print(f"   article_wait config: {article_wait}")
                        elif wait_config:
                            print(f"   wait config: {wait_config}")
                        else:
                            print(f"   Using default wait")
                        
                        time.sleep(2)
                        elapsed = time.time() - start
                        print(f"   ✅ Article loaded in {elapsed:.2f}s")
                        
                        self.take_screenshot("article_page_loaded")
                    
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
            
            print("\n✅ Wait strategy testing complete")
            
        except Exception as e:
            print(f"\n❌ Error during wait testing: {e}")
            self.take_screenshot("wait_test_error")
            traceback.print_exc()
        finally:
            if hasattr(self.scraper, 'driver') and self.scraper.driver:
                self.scraper.cleanup()
    
    def run_full_debug(self, category_name=None, max_articles=3):
        """Run full scraping with detailed debug output"""
        print("\n" + "="*80)
        print(f"🚀 FULL DEBUG SCRAPE: {self.website_name}")
        if category_name:
            print(f"   Category: {category_name}")
        print("="*80)
        
        try:
            start_time = time.time()
            
            if category_name:
                # Scrape specific category
                print(f"\n📂 Scraping category: {category_name}")
                sentences = self.scraper.scrape_category(
                    self.website_name,
                    category_name,
                    max_articles=max_articles
                )
            else:
                # Scrape entire website
                print(f"\n🌐 Scraping entire website")
                result = self.scraper.scrape_website(
                    self.website_name,
                    max_articles=max_articles
                )
                sentences = []
                if result.success:
                    # Collect all sentences from all categories
                    for cat_sentences in result.metadata.get('sentences_by_category', {}).values():
                        sentences.extend(cat_sentences)
            
            duration = time.time() - start_time
            
            print("\n" + "="*80)
            print("📊 DEBUG RESULTS")
            print("="*80)
            print(f"⏱️  Duration: {duration:.2f}s")
            print(f"📝 Sentences Extracted: {len(sentences)}")
            
            if sentences:
                print(f"\n📄 Sample Sentences (first 5):")
                for i, sentence in enumerate(sentences[:5], 1):
                    print(f"   {i}. {sentence[:100]}...")
            
            return sentences
            
        except Exception as e:
            print(f"\n❌ Error during full debug: {e}")
            self.take_screenshot("full_debug_error")
            traceback.print_exc()
            return []


def main():
    parser = argparse.ArgumentParser(
        description='Debug tool for Generic Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('website', help='Website name to debug')
    parser.add_argument('--category', '-c', help='Specific category to debug')
    parser.add_argument('--max-articles', '-m', type=int, default=3,
                       help='Maximum articles to scrape (default: 3)')
    parser.add_argument('--headful', action='store_true',
                       help='Run browser in headful mode (visible)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose debug logging')
    parser.add_argument('--screenshots', '-s', action='store_true',
                       help='Save screenshots during debugging')
    
    # Test modes
    parser.add_argument('--config-only', action='store_true',
                       help='Only show configuration, no scraping')
    parser.add_argument('--test-selectors', action='store_true',
                       help='Test selector extraction only')
    parser.add_argument('--pagination-only', action='store_true',
                       help='Test pagination without article extraction')
    parser.add_argument('--debug-waits', action='store_true',
                       help='Debug wait strategies and timing')
    parser.add_argument('--max-pages', type=int,
                       help='Maximum pages for pagination testing')
    
    args = parser.parse_args()
    
    # Create debug scraper
    debug = DebugScraper(
        args.website,
        headless=not args.headful,
        verbose=args.verbose,
        screenshots=args.screenshots
    )
    
    # Run selected debug mode
    if args.config_only:
        if args.category:
            debug.debug_category_config(args.category)
        else:
            debug.debug_website_config()
    
    elif args.test_selectors:
        if not args.category:
            print("❌ --test-selectors requires --category")
            return 1
        debug.test_selectors(args.category)
    
    elif args.pagination_only:
        if not args.category:
            print("❌ --pagination-only requires --category")
            return 1
        debug.test_pagination(args.category, max_pages=args.max_pages)
    
    elif args.debug_waits:
        if not args.category:
            print("❌ --debug-waits requires --category")
            return 1
        debug.debug_wait_strategies(args.category)
    
    else:
        # Full debug scrape
        if args.category:
            # Show config first
            debug.debug_category_config(args.category)
        else:
            debug.debug_website_config()
        
        # Then run scrape
        debug.run_full_debug(args.category, max_articles=args.max_articles)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
