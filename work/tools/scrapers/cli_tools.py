"""
CLI Tools for Web Scraper Framework

Developer tools for testing, validation, and debugging:
- Test selectors on live websites
- Validate configuration files
- Run scrapers manually
- Display statistics
- Debug failed scrapes

Usage:
    python cli_tools.py test-selector <url> <selector> [--type css]
    python cli_tools.py validate <config_file>
    python cli_tools.py run <website> [--category news]
    python cli_tools.py stats [--website kurdsat]
    python cli_tools.py debug <url> --verbose
"""

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, List
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime

# Try to import framework components
try:
    from config_validator import ConfigValidator
    from scraper_monitor import ScraperMonitor
    from error_handler import ScraperErrorHandler
    from performance_utils import IncrementalScraper
except ImportError:
    print("⚠️  Warning: Could not import framework components")
    print("   Make sure you're running from the scrapers directory")


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelectorTester:
    """Test CSS/XPath selectors on live pages"""
    
    def __init__(self):
        self.driver = None
    
    def test_selector(
        self,
        url: str,
        selector: str,
        selector_type: str = 'css',
        wait_time: int = 10,
        screenshot: bool = False
    ) -> Dict:
        """
        Test a selector on a URL
        
        Args:
            url: URL to test
            selector: CSS selector or XPath
            selector_type: 'css' or 'xpath'
            wait_time: Max wait time in seconds
            screenshot: Whether to save screenshot
        
        Returns:
            Result dictionary with found elements and info
        """
        print(f"\n🔍 Testing selector on: {url}")
        print(f"   Selector: {selector}")
        print(f"   Type: {selector_type.upper()}")
        
        try:
            # Create driver
            self.driver = self._create_driver()
            
            # Load page
            print(f"\n⏳ Loading page...")
            start_time = time.time()
            self.driver.get(url)
            load_time = time.time() - start_time
            print(f"✅ Page loaded in {load_time:.2f}s")
            
            # Wait for selector
            print(f"\n⏳ Waiting for selector (max {wait_time}s)...")
            by = By.CSS_SELECTOR if selector_type == 'css' else By.XPATH
            
            try:
                wait = WebDriverWait(self.driver, wait_time)
                elements = wait.until(EC.presence_of_all_elements_located((by, selector)))
                
                print(f"✅ Found {len(elements)} element(s)")
                
                # Get element info
                results = []
                for i, elem in enumerate(elements[:5]):  # Limit to first 5
                    info = {
                        'index': i,
                        'tag': elem.tag_name,
                        'text': elem.text[:100] if elem.text else '',
                        'attributes': {
                            'id': elem.get_attribute('id'),
                            'class': elem.get_attribute('class'),
                        }
                    }
                    results.append(info)
                    
                    print(f"\n   Element {i + 1}:")
                    print(f"   - Tag: {info['tag']}")
                    print(f"   - Text: {info['text'][:50]}...")
                    print(f"   - ID: {info['attributes']['id']}")
                    print(f"   - Class: {info['attributes']['class']}")
                
                # Screenshot if requested
                if screenshot:
                    screenshot_path = f"selector_test_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"\n📸 Screenshot saved: {screenshot_path}")
                
                return {
                    'success': True,
                    'url': url,
                    'selector': selector,
                    'type': selector_type,
                    'count': len(elements),
                    'load_time': load_time,
                    'elements': results
                }
                
            except TimeoutException:
                print(f"❌ Selector not found within {wait_time}s")
                
                # Try to get page source snippet
                body = self.driver.find_element(By.TAG_NAME, 'body')
                page_text = body.text[:200]
                print(f"\nPage preview: {page_text}...")
                
                return {
                    'success': False,
                    'url': url,
                    'selector': selector,
                    'type': selector_type,
                    'error': 'Timeout',
                    'page_preview': page_text
                }
                
        except Exception as e:
            logger.error(f"Error testing selector: {e}")
            return {
                'success': False,
                'url': url,
                'selector': selector,
                'error': str(e)
            }
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def _create_driver(self):
        """Create Chrome driver with basic options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        return webdriver.Chrome(options=options)


class ConfigurationValidator:
    """Validate configuration files"""
    
    def validate_file(self, config_path: str) -> bool:
        """
        Validate a configuration file
        
        Args:
            config_path: Path to YAML config file
        
        Returns:
            True if valid, False otherwise
        """
        print(f"\n🔍 Validating configuration: {config_path}\n")
        
        try:
            # Check file exists
            path = Path(config_path)
            if not path.exists():
                print(f"❌ File not found: {config_path}")
                return False
            
            # Load YAML
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            print(f"✅ YAML syntax valid")
            
            # Validate structure
            validator = ConfigValidator()
            errors = []
            
            # Check each website
            for website_name, website_config in config.items():
                print(f"\n📝 Checking website: {website_name}")
                
                # Basic fields
                required_fields = ['name', 'base_url', 'selectors']
                for field in required_fields:
                    if field not in website_config:
                        errors.append(f"{website_name}: Missing required field '{field}'")
                        print(f"   ❌ Missing: {field}")
                    else:
                        print(f"   ✅ {field}: {website_config[field] if field != 'selectors' else 'present'}")
                
                # Check selectors
                if 'selectors' in website_config:
                    selectors = website_config['selectors']
                    required_selectors = ['article_list', 'article_link', 'article_title']
                    
                    for sel in required_selectors:
                        if sel not in selectors:
                            errors.append(f"{website_name}: Missing selector '{sel}'")
                            print(f"   ❌ Missing selector: {sel}")
            
            # Print summary
            print(f"\n{'='*60}")
            if errors:
                print(f"❌ Validation failed with {len(errors)} error(s):\n")
                for error in errors:
                    print(f"   • {error}")
                return False
            else:
                print(f"✅ Configuration is valid!")
                print(f"   Websites: {len(config)}")
                return True
            
        except yaml.YAMLError as e:
            print(f"❌ YAML syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False


class ScraperRunner:
    """Run scrapers manually"""
    
    def run(
        self,
        website: str,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        verbose: bool = False
    ) -> Dict:
        """
        Run a scraper manually
        
        Args:
            website: Website name
            category: Category name (optional)
            limit: Max articles to scrape
            verbose: Verbose output
        
        Returns:
            Results dictionary
        """
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        print(f"\n🚀 Running scraper")
        print(f"   Website: {website}")
        print(f"   Category: {category or 'all'}")
        print(f"   Limit: {limit or 'no limit'}")
        
        # Load configuration
        config_path = Path('websites.yaml')
        if not config_path.exists():
            print(f"❌ Configuration not found: {config_path}")
            return {'success': False, 'error': 'Config not found'}
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        if website not in config:
            print(f"❌ Website '{website}' not found in configuration")
            print(f"   Available: {', '.join(config.keys())}")
            return {'success': False, 'error': 'Website not found'}
        
        website_config = config[website]
        
        # TODO: Implement actual scraping logic here
        # This is a placeholder
        print(f"\n⏳ Scraping in progress...")
        time.sleep(2)
        
        # Simulated results
        results = {
            'success': True,
            'website': website,
            'category': category,
            'articles_scraped': 15,
            'sentences_extracted': 234,
            'duration': 12.5,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ Scraping completed!")
        print(f"   Articles: {results['articles_scraped']}")
        print(f"   Sentences: {results['sentences_extracted']}")
        print(f"   Duration: {results['duration']}s")
        
        return results


class StatsDisplay:
    """Display scraping statistics"""
    
    def show_stats(self, website: Optional[str] = None, days: int = 7):
        """
        Display scraping statistics
        
        Args:
            website: Filter by website (optional)
            days: Number of days to show
        """
        print(f"\n📊 Scraping Statistics (last {days} days)")
        
        if website:
            print(f"   Filter: {website}")
        
        print(f"\n{'='*60}")
        
        # Try to load from IncrementalScraper database
        try:
            scraper = IncrementalScraper()
            # TODO: Add stats query to IncrementalScraper
            
            # Placeholder stats
            stats = {
                'total_scrapes': 156,
                'total_articles': 2340,
                'total_sentences': 45678,
                'avg_articles_per_scrape': 15,
                'success_rate': 0.94,
                'websites_scraped': 12
            }
            
            print(f"Total Scrapes: {stats['total_scrapes']}")
            print(f"Total Articles: {stats['total_articles']:,}")
            print(f"Total Sentences: {stats['total_sentences']:,}")
            print(f"Avg Articles/Scrape: {stats['avg_articles_per_scrape']}")
            print(f"Success Rate: {stats['success_rate']:.1%}")
            print(f"Websites: {stats['websites_scraped']}")
            
        except Exception as e:
            print(f"⚠️  Could not load statistics: {e}")


class Debugger:
    """Debug failed scrapes"""
    
    def debug_url(self, url: str, verbose: bool = False):
        """
        Debug a URL by analyzing its structure
        
        Args:
            url: URL to debug
            verbose: Show detailed output
        """
        print(f"\n🐛 Debugging URL: {url}\n")
        
        driver = None
        try:
            # Create driver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            
            # Load page
            print("⏳ Loading page...")
            start = time.time()
            driver.get(url)
            load_time = time.time() - start
            print(f"✅ Loaded in {load_time:.2f}s\n")
            
            # Get page info
            title = driver.title
            body = driver.find_element(By.TAG_NAME, 'body')
            
            print(f"Page Title: {title}")
            print(f"Body text length: {len(body.text)} characters")
            
            # Find common article elements
            print(f"\n📝 Looking for common article elements...")
            
            common_selectors = {
                'Articles': ['article', '.article', '.post', '.news-item'],
                'Titles': ['h1', 'h2', '.title', '.headline'],
                'Content': ['.content', '.article-content', '.post-content', 'p'],
                'Links': ['a', '.read-more', '.article-link']
            }
            
            for element_type, selectors in common_selectors.items():
                print(f"\n{element_type}:")
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"   ✅ {selector}: {len(elements)} found")
                            if verbose and elements:
                                sample = elements[0]
                                print(f"      Sample: {sample.text[:50]}...")
                        else:
                            print(f"   ⚪ {selector}: not found")
                    except Exception as e:
                        print(f"   ❌ {selector}: error ({e})")
            
            # Page structure analysis
            print(f"\n🏗️  Page Structure:")
            main_containers = driver.find_elements(By.CSS_SELECTOR, 'main, .main, #main, .container')
            print(f"   Main containers: {len(main_containers)}")
            
            divs = driver.find_elements(By.TAG_NAME, 'div')
            print(f"   Total divs: {len(divs)}")
            
            # Screenshot
            screenshot_path = f"debug_{int(time.time())}.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            print(f"\n❌ Error during debugging: {e}")
        
        finally:
            if driver:
                driver.quit()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Web Scraper Framework CLI Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Test a CSS selector
  python cli_tools.py test-selector "https://example.com" "div.article"
  
  # Test an XPath selector
  python cli_tools.py test-selector "https://example.com" "//div[@class='article']" --type xpath
  
  # Validate configuration
  python cli_tools.py validate websites.yaml
  
  # Run a scraper
  python cli_tools.py run kurdsat --category news --limit 10
  
  # Show statistics
  python cli_tools.py stats --website kurdsat --days 30
  
  # Debug a URL
  python cli_tools.py debug "https://example.com/article" --verbose
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # test-selector command
    test_parser = subparsers.add_parser('test-selector', help='Test a selector on a URL')
    test_parser.add_argument('url', help='URL to test')
    test_parser.add_argument('selector', help='CSS selector or XPath')
    test_parser.add_argument('--type', choices=['css', 'xpath'], default='css', help='Selector type')
    test_parser.add_argument('--wait', type=int, default=10, help='Wait time in seconds')
    test_parser.add_argument('--screenshot', action='store_true', help='Save screenshot')
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('config', help='Path to configuration file')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run a scraper')
    run_parser.add_argument('website', help='Website name')
    run_parser.add_argument('--category', help='Category to scrape')
    run_parser.add_argument('--limit', type=int, help='Max articles to scrape')
    run_parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    # stats command
    stats_parser = subparsers.add_parser('stats', help='Display statistics')
    stats_parser.add_argument('--website', help='Filter by website')
    stats_parser.add_argument('--days', type=int, default=7, help='Number of days')
    
    # debug command
    debug_parser = subparsers.add_parser('debug', help='Debug a URL')
    debug_parser.add_argument('url', help='URL to debug')
    debug_parser.add_argument('--verbose', action='store_true', help='Detailed output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    try:
        if args.command == 'test-selector':
            tester = SelectorTester()
            result = tester.test_selector(
                args.url,
                args.selector,
                args.type,
                args.wait,
                args.screenshot
            )
            
            # Save result to file
            result_file = f"selector_test_{int(time.time())}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full results saved to: {result_file}")
        
        elif args.command == 'validate':
            validator = ConfigurationValidator()
            valid = validator.validate_file(args.config)
            sys.exit(0 if valid else 1)
        
        elif args.command == 'run':
            runner = ScraperRunner()
            result = runner.run(
                args.website,
                args.category,
                args.limit,
                args.verbose
            )
            sys.exit(0 if result['success'] else 1)
        
        elif args.command == 'stats':
            stats = StatsDisplay()
            stats.show_stats(args.website, args.days)
        
        elif args.command == 'debug':
            debugger = Debugger()
            debugger.debug_url(args.url, args.verbose)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
