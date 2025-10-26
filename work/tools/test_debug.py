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

    # Track all URLs fetched during scraping (helps identify what to block)
    python3 test_debug.py rudaw --category kurdistan --track-urls

    # Combine multiple options
    python3 test_debug.py rudaw --category kurdistan --max-articles 3 --headful --verbose --screenshots --track-urls
"""

import sys
import os
import argparse
import time
import traceback
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

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
    
    def __init__(self, website_name, headless=True, verbose=False, screenshots=False, track_urls=False):
        self.website_name = website_name
        self.headless = headless
        self.verbose = verbose
        self.screenshots = screenshots
        self.track_urls = track_urls
        self.screenshot_dir = Path('debug_screenshots')
        self.tracked_urls = defaultdict(list)  # {url_type: [urls]}
        self.base_domain = None
        
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
    
    def enable_network_tracking(self):
        """Enable network request tracking via Chrome DevTools Protocol"""
        if not self.track_urls or not hasattr(self.scraper, 'driver') or not self.scraper.driver:
            return
        
        try:
            # Enable performance logging
            self.scraper.driver.execute_cdp_cmd('Network.enable', {})
            logger.info("✅ Network tracking enabled")
        except Exception as e:
            logger.warning(f"⚠️  Could not enable network tracking: {e}")
            self.track_urls = False
    
    def collect_network_requests(self, url=None):
        """Collect all network requests from browser logs"""
        if not self.track_urls or not hasattr(self.scraper, 'driver') or not self.scraper.driver:
            return
        
        try:
            # Set base domain if URL provided
            if url:
                parsed = urlparse(url)
                self.base_domain = parsed.netloc
            
            # Get performance logs
            logs = self.scraper.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log_data = json.loads(entry['message'])
                    message = log_data.get('message', {})
                    
                    # Track different request types
                    if message.get('method') == 'Network.requestWillBeSent':
                        params = message.get('params', {})
                        request = params.get('request', {})
                        request_url = request.get('url', '')
                        request_type = params.get('type', 'other').lower()
                        
                        if request_url and not request_url.startswith('data:'):
                            # Categorize URL
                            parsed = urlparse(request_url)
                            is_third_party = self.base_domain and parsed.netloc != self.base_domain
                            
                            # Store URL with metadata
                            self.tracked_urls[request_type].append({
                                'url': request_url,
                                'domain': parsed.netloc,
                                'third_party': is_third_party,
                                'timestamp': entry.get('timestamp', 0)
                            })
                
                except (json.JSONDecodeError, KeyError) as e:
                    continue
        
        except Exception as e:
            logger.warning(f"⚠️  Error collecting network requests: {e}")
    
    def display_url_tracking_summary(self):
        """Display comprehensive URL tracking summary with filter suggestions"""
        if not self.track_urls or not self.tracked_urls:
            return
        
        print("\n" + "="*80)
        print("🌐 NETWORK REQUEST TRACKING SUMMARY")
        print("="*80)
        
        # Collect statistics
        total_requests = sum(len(urls) for urls in self.tracked_urls.values())
        third_party_domains = set()
        first_party_urls = []
        third_party_urls = []
        
        for request_type, urls in self.tracked_urls.items():
            for url_info in urls:
                if url_info['third_party']:
                    third_party_domains.add(url_info['domain'])
                    third_party_urls.append(url_info)
                else:
                    first_party_urls.append(url_info)
        
        print(f"\n📊 Overview:")
        print(f"   Total Requests: {total_requests}")
        print(f"   First-Party: {len(first_party_urls)} requests")
        print(f"   Third-Party: {len(third_party_urls)} requests from {len(third_party_domains)} domains")
        print(f"   Base Domain: {self.base_domain or 'N/A'}")
        
        # Breakdown by type
        print(f"\n📋 Requests by Type:")
        for request_type in sorted(self.tracked_urls.keys()):
            urls = self.tracked_urls[request_type]
            if urls:
                third_party_count = sum(1 for u in urls if u['third_party'])
                print(f"   {request_type.upper():15} {len(urls):4} total ({third_party_count} third-party)")
        
        # Third-party domains
        if third_party_domains:
            print(f"\n🌍 Third-Party Domains ({len(third_party_domains)}):")
            domain_counts = defaultdict(int)
            for url_info in third_party_urls:
                domain_counts[url_info['domain']] += 1
            
            for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {count:4}x  {domain}")
        
        # Suggest filter patterns
        print(f"\n💡 Suggested Blacklist Patterns (Third-Party Services):")
        if third_party_domains:
            # Common analytics/tracking domains
            tracking_keywords = ['analytics', 'tracking', 'metric', 'tag', 'pixel', 'stats', 'collect']
            ad_keywords = ['ads', 'adserver', 'doubleclick', 'adsystem', 'advertising']
            social_keywords = ['facebook', 'twitter', 'instagram', 'linkedin', 'social']
            
            tracking_domains = [d for d in third_party_domains if any(k in d.lower() for k in tracking_keywords)]
            ad_domains = [d for d in third_party_domains if any(k in d.lower() for k in ad_keywords)]
            social_domains = [d for d in third_party_domains if any(k in d.lower() for k in social_keywords)]
            
            if tracking_domains:
                print(f"   # Analytics/Tracking ({len(tracking_domains)} domains):")
                for domain in sorted(tracking_domains)[:5]:
                    print(f"   '*.{domain}'")
            
            if ad_domains:
                print(f"   # Advertising ({len(ad_domains)} domains):")
                for domain in sorted(ad_domains)[:5]:
                    print(f"   '*.{domain}'")
            
            if social_domains:
                print(f"   # Social Media ({len(social_domains)} domains):")
                for domain in sorted(social_domains)[:5]:
                    print(f"   '*.{domain}'")
            
            # Other third-party
            other_domains = third_party_domains - set(tracking_domains) - set(ad_domains) - set(social_domains)
            if other_domains:
                print(f"   # Other Third-Party ({len(other_domains)} domains):")
                for domain in sorted(other_domains)[:10]:
                    print(f"   '*.{domain}'")
        else:
            print("   (No third-party requests detected)")
        
        print(f"\n💡 Suggested Whitelist Patterns (Main Content):")
        if self.base_domain:
            print(f"   '*.{self.base_domain}'  # Main website")
            
            # Check for CDN domains
            cdn_keywords = ['cdn', 'static', 'media', 'assets', 'content']
            cdn_domains = [d for d in third_party_domains if any(k in d.lower() for k in cdn_keywords)]
            if cdn_domains:
                print(f"   # CDN/Media ({len(cdn_domains)} domains):")
                for domain in sorted(cdn_domains)[:5]:
                    print(f"   '*.{domain}'")
        
        # Request type patterns
        print(f"\n💡 Path-Based Patterns:")
        print(f"   # Block common tracking paths:")
        print(f"   '*/analytics/*'")
        print(f"   '*/tracking/*'")
        print(f"   '*/pixel/*'")
        print(f"   '*/beacon/*'")
        print(f"   '*/collect*'")
        
        print("\n" + "="*80)
    
    def save_url_tracking_report(self, filename=None):
        """Save URL tracking data to JSON file"""
        if not self.track_urls or not self.tracked_urls:
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"url_tracking_{self.website_name}_{timestamp}.json"
        
        report = {
            'website': self.website_name,
            'base_domain': self.base_domain,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_requests': sum(len(urls) for urls in self.tracked_urls.values()),
                'request_types': {k: len(v) for k, v in self.tracked_urls.items()}
            },
            'requests': {}
        }
        
        # Convert to serializable format
        for request_type, urls in self.tracked_urls.items():
            report['requests'][request_type] = urls
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📁 URL tracking report saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save URL tracking report: {e}")
    
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
            
            # Enable network tracking if requested
            if self.track_urls:
                self.enable_network_tracking()
            
            if category_name:
                # Scrape specific category
                print(f"\n📂 Scraping category: {category_name}")
                
                # Get category URL for tracking
                if self.track_urls and self.website_name in self.scraper.config:
                    cat_config = self.scraper.config[self.website_name].get('categories', {}).get(category_name, {})
                    cat_url = cat_config.get('url')
                    if cat_url:
                        self.collect_network_requests(cat_url)
                
                sentences = self.scraper.scrape_category(
                    self.website_name,
                    category_name,
                    max_articles=max_articles
                )
                
                # Collect network requests after scraping
                if self.track_urls:
                    time.sleep(2)  # Wait for remaining requests
                    self.collect_network_requests()
            else:
                # Scrape entire website
                print(f"\n🌐 Scraping entire website")
                
                # Get base URL for tracking
                if self.track_urls and self.website_name in self.scraper.config:
                    base_url = self.scraper.config[self.website_name].get('base_url')
                    if base_url:
                        self.collect_network_requests(base_url)
                
                result = self.scraper.scrape_website(
                    self.website_name,
                    max_articles=max_articles
                )
                sentences = []
                if result.success:
                    # Collect all sentences from all categories
                    for cat_sentences in result.metadata.get('sentences_by_category', {}).values():
                        sentences.extend(cat_sentences)
                
                # Collect network requests after scraping
                if self.track_urls:
                    time.sleep(2)  # Wait for remaining requests
                    self.collect_network_requests()
            
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
            
            # Display URL tracking summary
            if self.track_urls:
                self.display_url_tracking_summary()
                self.save_url_tracking_report()
            
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
    parser.add_argument('--track-urls', '-t', action='store_true',
                       help='Track and display all URLs fetched during scraping')
    
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
        screenshots=args.screenshots,
        track_urls=args.track_urls
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
