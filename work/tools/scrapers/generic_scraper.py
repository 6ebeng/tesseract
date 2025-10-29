"""
Generic YAML-Driven Web Scraper

Universal scraper that reads configuration from YAML files.
Handles all category types: pagination, infinite scroll, click-based.

Usage:
    from generic_scraper import GenericScraper
    
    scraper = GenericScraper('websites.yaml')
    results = scraper.scrape_website('kurdsat')
    
    # Or scrape specific category
    results = scraper.scrape_category('kurdsat', 'politics')
"""

import yaml
import time
import logging
import requests
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

# Import framework components
try:
    from base_scraper import BaseScraper, SimpleQC
    HAS_BASE_SCRAPER = True
except ImportError:
    BaseScraper = object
    SimpleQC = None
    HAS_BASE_SCRAPER = False

# Optional advanced features
try:
    from error_handler import ScraperErrorHandler
    HAS_ERROR_HANDLER = True
except ImportError:
    ScraperErrorHandler = None
    HAS_ERROR_HANDLER = False

try:
    from scraper_monitor import ScraperMonitor, ScrapeResult
    HAS_MONITOR = True
except ImportError:
    # Minimal ScrapeResult for standalone operation
    class ScrapeResult:
        def __init__(self, website_name, success=True, articles_scraped=0, 
                     sentences_extracted=0, duplicates_skipped=0, errors=None):
            self.website_name = website_name
            self.success = success
            self.articles_scraped = articles_scraped
            self.sentences_extracted = sentences_extracted
            self.duplicates_skipped = duplicates_skipped
            self.errors = errors or []
            self.start_time = datetime.now()
            self.end_time = datetime.now()
    
    ScraperMonitor = None
    HAS_MONITOR = False

try:
    from advanced_features import LanguageDetector, ArticleDeduplicator, StealthBrowser
    HAS_ADVANCED = True
except ImportError:
    LanguageDetector = None
    ArticleDeduplicator = None
    StealthBrowser = None
    HAS_ADVANCED = False

try:
    from security_utils import safe_load_yaml, RateLimiter
    HAS_SECURITY = True
except ImportError:
    safe_load_yaml = None
    RateLimiter = None
    HAS_SECURITY = False

try:
    from network_features import SessionManager, ResponseCache, RetryHandler, ProxyManager
    HAS_NETWORK = True
except ImportError:
    SessionManager = None
    ResponseCache = None
    RetryHandler = None
    ProxyManager = None
    HAS_NETWORK = False


logger = logging.getLogger(__name__)


class GenericScraper:
    """
    Generic scraper that reads configuration from YAML
    
    Supports:
    - Multiple selector types (CSS, XPath)
    - Fallback selector chains
    - All pagination types (next_page, infinite_scroll, click_load_more)
    - Wait strategies (selector, manual, time-based)
    - Per-website and per-category configuration
    - Error handling and retry
    - Language detection and filtering
    - Article deduplication
    
    Note: Does not inherit from BaseScraper to avoid abstract method requirements.
    Implements similar interface for compatibility.
    """
    
    def __init__(self, config_path: str = 'websites.yaml'):
        """
        Initialize generic scraper
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.name = "Generic"
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize quality control if available
        self.qc = SimpleQC() if HAS_BASE_SCRAPER and SimpleQC else None
        
        # Initialize advanced features (if available)
        self.lang_detector = LanguageDetector() if HAS_ADVANCED and LanguageDetector else None
        self.deduplicator = ArticleDeduplicator() if HAS_ADVANCED and ArticleDeduplicator else None
        self.stealth = StealthBrowser() if HAS_ADVANCED and StealthBrowser else None
        self.error_handler = ScraperErrorHandler() if HAS_ERROR_HANDLER and ScraperErrorHandler else None
        self.monitor = ScraperMonitor() if HAS_MONITOR and ScraperMonitor else None
        self.rate_limiter = RateLimiter(requests_per_minute=20) if HAS_SECURITY and RateLimiter else None
        
        # Initialize network features (if available and configured)
        self.session_manager = None
        if HAS_NETWORK and SessionManager:
            # Check for network config in environment or config
            use_cache = True  # Enable by default
            use_retry = True  # Enable by default
            use_proxy = False  # Disabled by default (needs proxy list)
            
            self.session_manager = SessionManager(
                use_cache=use_cache,
                use_retry=use_retry,
                use_proxy=use_proxy,
                cache_dir='cache/',
                max_retries=3,
                backoff_factor=2.0
            )
            logger.info("✅ Network features enabled: caching, retry")
        
        self.driver = None
        self.current_website = None
        self.flaresolverr_session = None  # FlareSolverr session ID
        
        # Article link deduplication (tracks scraped URLs to skip duplicates)
        self.scraped_article_links = set()  # URLs that have been scraped
        self.article_link_db_path = Path('scraped_articles.db')  # Persistent storage
        self.stats = {
            'articles_processed': 0,
            'sentences_extracted': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }
        
        # URL tracking and whitelisting for performance optimization
        self.url_debug_mode = False  # Enable with debug_urls: true in config
        self.tracked_urls = []  # List of all URLs requested
        self._tracked_url_set = set()  # Fast lookup for tracked URLs
        self.url_whitelist = []  # Whitelist of URL patterns to allow
        self._default_blocked_resources = [  # Default blocked resources for faster loading
            '.css', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', 
            '.ttf', '.eot', '.mp4', '.mp3', '.webm', '.avi', '.mov', '.flv',
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com/tr', 'twitter.com/i/adsct', 'ads', 'analytics', 'tracking'
        ]
        self.blocked_resources = list(self._default_blocked_resources)
    
    def _load_config(self) -> Dict:
        """
        Load and validate YAML configuration
        
        Supports two modes:
        1. Single file: websites.yaml with all configs
        2. Directory: configs/ with individual website YAML files
        """
        config = {}
        
        # Check if config_path is a directory (configs/)
        if self.config_path.is_dir():
            logger.info(f"Loading configurations from directory: {self.config_path}")
            
            # Check for websites subdirectory (new structure)
            websites_dir = self.config_path / 'websites'
            if websites_dir.exists() and websites_dir.is_dir():
                logger.info(f"  Using websites subdirectory: {websites_dir}")
                config_dir = websites_dir
            else:
                config_dir = self.config_path
            
            # Load all YAML files from directory
            yaml_files = sorted(config_dir.glob('*.yaml'))
            yaml_files = [f for f in yaml_files if f.name != 'index.yaml']  # Skip index
            
            for yaml_file in yaml_files:
                try:
                    website_name = yaml_file.stem  # filename without extension
                    
                    if HAS_SECURITY and safe_load_yaml:
                        website_config = safe_load_yaml(str(yaml_file))
                    else:
                        with open(yaml_file, 'r', encoding='utf-8') as f:
                            website_config = yaml.safe_load(f)
                    
                    config[website_name] = website_config
                    logger.debug(f"  ✅ Loaded {website_name} from {yaml_file.name}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to load {yaml_file.name}: {e}")
            
            logger.info(f"✅ Loaded {len(config)} websites from {len(yaml_files)} config files")
        
        # Single file mode (backward compatible)
        else:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            logger.info(f"Loading configuration from: {self.config_path}")
            
            # Use safe YAML loading
            if HAS_SECURITY and safe_load_yaml:
                config = safe_load_yaml(str(self.config_path))
            else:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            
            logger.info(f"✅ Loaded {len(config)} websites from configuration")
        
        return config
    
    def _apply_defaults(self, website_config: Dict, category_config: Dict) -> Dict:
        """
        Apply intelligent defaults with fallback chain (V4.0):
        Category-specific > Website defaults > Hard-coded defaults
        
        V4.0 Structure:
        - Website has pagination{} at top level
        - Categories can override with pagination{}
        - Selectors at website level, categories can override
        
        Returns merged configuration with all defaults applied
        """
        merged = {}
        
        # Get default configurations (V4.0)
        website_pagination = website_config.get('pagination', {})
        website_selectors = website_config.get('selectors', {})
        website_wait = website_config.get('wait', {})
        
        # Get category overrides (V4.0)
        category_pagination = category_config.get('pagination', {})
        category_selectors = category_config.get('selectors', {})
        category_wait = category_config.get('wait', {})
        
        # 1. URL (required, no default)
        merged['url'] = category_config['url']
        
        # 2. Enabled (default: True)
        merged['enabled'] = category_config.get('enabled', True)
        
        # 3. Pagination type (category pagination > website pagination > 'pagination')
        merged['type'] = (
            category_pagination.get('type') or
            website_pagination.get('type', 'pagination')
        )
        
        # 4. Pagination parameters based on type
        if merged['type'] == 'pagination' or merged['type'] == 'url_template':
            merged['pages'] = (
                category_pagination.get('pages') or
                website_pagination.get('pages', 5)
            )
            # For url_template, also get page_param and path
            if merged['type'] == 'url_template':
                merged['page_param'] = (
                    category_pagination.get('page_param') or
                    website_pagination.get('page_param')
                )
                merged['path'] = (
                    category_pagination.get('path') or
                    website_pagination.get('path')
                )
        elif merged['type'] == 'infinite_scroll':
            merged['scrolls'] = (
                category_pagination.get('scrolls') or
                website_pagination.get('scrolls', 20)
            )
        elif merged['type'] == 'click_load_more':
            merged['clicks'] = (
                category_pagination.get('clicks') or
                website_pagination.get('clicks', 10)
            )
            merged['load_more_button'] = (
                category_pagination.get('load_more_button') or
                website_pagination.get('load_more_button', 'button.load-more')
            )
        
        # 5. Wait configuration (category wait > website wait > defaults)
        if category_wait:
            merged['wait'] = category_wait
        elif website_wait:
            merged['wait'] = website_wait
        else:
            # V4.0: Default wait uses selector=null and timeout
            merged['wait'] = {'selector': None, 'timeout': 3}
        
        # 6. Selectors (category selectors > website selectors)
        # V4.0: Use article_body instead of article_content + article_paragraphs
        merged['selectors'] = {}
        selector_keys = ['article_list', 'article_title', 'article_body']
        
        for key in selector_keys:
            merged['selectors'][key] = (
                category_selectors.get(key) or
                website_selectors.get(key)
            )
        
        # 7. Delay time (category pagination > website pagination > 2 seconds)
        merged['delay'] = (
            category_pagination.get('delay') or
            website_pagination.get('delay', 2)
        )
        
        return merged
    
    def scrape_website(
        self,
        website_name: str,
        categories: Optional[List[str]] = None,
        max_articles: Optional[int] = None
    ) -> ScrapeResult:
        """
        Scrape entire website or specific categories
        
        Args:
            website_name: Website identifier from config
            categories: List of category names (None = all enabled)
            max_articles: Maximum articles per category
        
        Returns:
            ScrapeResult with metrics
        """
        if website_name not in self.config:
            raise ValueError(f"Website '{website_name}' not found in configuration")
        
        website_config = self.config[website_name]
        self.current_website = website_name
        
        # Enable URL debugging if configured
        if website_config.get('debug_urls', False):
            self.enable_url_debugging()
        
        # Load URL filtering with preset support
        self._load_url_filtering(website_config)
        
        # Check if website is enabled
        if not website_config.get('enabled', True):
            logger.warning(f"Website '{website_name}' is disabled in configuration")
            return self._create_empty_result(website_name, "Website disabled")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🌐 Scraping Website: {website_config.get('name', website_name)}")
        logger.info(f"{'='*70}\n")
        
        start_time = datetime.now()
        all_sentences = []
        
        try:
            # Initialize driver with stealth mode
            self._init_stealth_driver()
            
            # Get categories to scrape
            if categories is None:
                # Scrape all enabled categories
                categories = [
                    cat_name for cat_name, cat_config 
                    in website_config.get('categories', {}).items()
                    if cat_config.get('enabled', True)
                ]
            
            logger.info(f"📂 Categories to scrape: {', '.join(categories)}")
            
            # Scrape each category
            for category_name in categories:
                try:
                    sentences = self.scrape_category(
                        website_name,
                        category_name,
                        max_articles=max_articles
                    )
                    all_sentences.extend(sentences)
                    
                except Exception as e:
                    logger.error(f"Error scraping category '{category_name}': {e}")
                    self.stats['errors'] += 1
            
            # Create result
            result = ScrapeResult(
                website=website_name,
                success=True,
                articles_scraped=self.stats['articles_processed'],
                sentences_extracted=len(all_sentences),
                duration=(datetime.now() - start_time).total_seconds(),
                error=None
            )
            
            # Log to monitor
            self.monitor.log_scrape(result)
            
            logger.info(f"\n✅ Website scraping complete!")
            logger.info(f"   Articles: {self.stats['articles_processed']}")
            logger.info(f"   Sentences: {len(all_sentences)}")
            logger.info(f"   Duplicates skipped: {self.stats['duplicates_skipped']}")
            logger.info(f"   Duration: {result.duration:.2f}s\n")
            
            # Save tracked URLs if debugging was enabled
            if self.url_debug_mode and self.tracked_urls:
                # Create tracked_urls directory if it doesn't exist
                from pathlib import Path
                tracked_dir = Path(__file__).parent / 'tracked_urls'
                tracked_dir.mkdir(exist_ok=True)
                
                filename = tracked_dir / f"tracked_urls_{website_name}.txt"
                self.save_tracked_urls(str(filename))
                analysis = self.analyze_urls()
                logger.info(f"\n📊 URL Analysis:")
                logger.info(f"   Total URLs: {analysis['total_urls']}")
                logger.info(f"   Unique domains: {analysis['unique_domains']}")
                logger.info(f"   Resource types: {analysis['resource_types']}")
                if analysis['recommendations']:
                    logger.info(f"\n💡 Recommendations:")
                    for rec in analysis['recommendations']:
                        logger.info(f"   • {rec}")
            
            return result
            
        except Exception as e:
            logger.error(f"Website scraping failed: {e}", exc_info=True)
            
            result = ScrapeResult(
                website=website_name,
                success=False,
                articles_scraped=self.stats['articles_processed'],
                sentences_extracted=len(all_sentences),
                duration=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
            
            self.monitor.log_scrape(result)
            return result
            
        finally:
            if self.driver:
                self.driver.quit()
            if self.flaresolverr_session:
                self._destroy_flaresolverr_session()
    
    def scrape_category(
        self,
        website_name: str,
        category_name: str,
        max_articles: Optional[int] = None
    ) -> List[str]:
        """
        Scrape a specific category
        
        Args:
            website_name: Website identifier
            category_name: Category name from config
            max_articles: Maximum articles to scrape
        
        Returns:
            List of extracted sentences
        """
        website_config = self.config[website_name]
        categories = website_config.get('categories', {})
        
        if category_name not in categories:
            raise ValueError(f"Category '{category_name}' not found for {website_name}")
        
        category_config = categories[category_name]

        # Load previously scraped articles for deduplication
        if not hasattr(self, '_scraped_articles_loaded'):
            self.load_scraped_articles()
            self._scraped_articles_loaded = True

        # Enable URL debugging when requested at website level (category run)
        if website_config.get('debug_urls', False) and not self.url_debug_mode:
            self.enable_url_debugging()
        
        # Apply intelligent defaults (enabled by default)
        if category_config.get('enabled', True) is False:
            logger.warning(f"Category '{category_name}' is explicitly disabled")
            return []
        
        logger.info(f"\n📂 Scraping Category: {category_name}")
        logger.info(f"   URL: {category_config['url']}")
        
        # Initialize FlareSolverr if enabled for this website
        flaresolverr_config = website_config.get('flaresolverr', {})
        use_flaresolverr = flaresolverr_config.get('enabled', False)
        # Ensure FlareSolverr session is only active for sites that opt-in.
        # If a session exists from a previous website and the current
        # website does NOT request FlareSolverr, destroy the existing session
        # to avoid accidentally using it.
        if not use_flaresolverr and self.flaresolverr_session:
            logger.debug("🧹 Previous FlareSolverr session exists but not required for this site - destroying session")
            try:
                self._destroy_flaresolverr_session()
            except Exception:
                # Non-fatal - log at debug level and continue
                logger.debug("⚠️  Failed to destroy previous FlareSolverr session cleanly")

        if use_flaresolverr:
            if not self._init_flaresolverr(website_config):
                logger.error("❌ FlareSolverr initialization failed - aborting")
                return []
        
        # Apply configuration defaults with fallback chain
        merged_config = self._apply_defaults(website_config, category_config)
        
        # Rate limiting (if available)
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
        # Get pagination type from merged config
        category_type = merged_config['type']
        
        # Navigate to category page (skip if using URL template pagination)
        page_param = merged_config.get('page_param')
        is_url_template = category_type == 'url_template' or '{page}' in merged_config['url'] or page_param
        if not is_url_template:
            # Only load initial page if not using URL templates
            if not self._safe_get(merged_config['url']):
                return []
            
            # Wait for collection page to load (using merged config)
            self._wait_for_page(website_config, merged_config, page_type='collection')
        
        # Scrape based on pagination type
        if category_type in ['pagination', 'url_template']:
            article_links = self._scrape_pagination(website_config, merged_config)
        elif category_type == 'infinite_scroll':
            article_links = self._scrape_infinite_scroll(website_config, merged_config)
        elif category_type == 'click_load_more':
            article_links = self._scrape_click_load_more(website_config, merged_config)
        else:
            logger.error(f"Unknown category type: {category_type}")
            return []
        
        logger.info(f"   Found {len(article_links)} article links")
        
        # Limit articles if specified
        if max_articles:
            article_links = article_links[:max_articles]
        
        # Check if click-through navigation is required
        click_through = merged_config.get('click_through_navigation', False)
        
        if click_through:
            # Extract sentences using click-through navigation
            logger.info(f"   🖱️  Using click-through navigation (session state preserved)")
            sentences = self._extract_from_articles_click_through(
                website_config,
                merged_config,
                max_articles
            )
        else:
            # Extract sentences from articles (pass merged config)
            sentences = self._extract_from_articles(
                article_links,
                website_config,
                merged_config
            )
        
        logger.info(f"   ✅ Extracted {len(sentences)} sentences from {len(article_links)} articles\n")
        
        # Save tracked URLs if debugging was enabled
        if self.url_debug_mode and self.tracked_urls:
            # Create tracked_urls directory if it doesn't exist
            from pathlib import Path
            tracked_dir = Path(__file__).parent / 'tracked_urls'
            tracked_dir.mkdir(exist_ok=True)
            
            filename = tracked_dir / f"tracked_urls_{website_name}_{category_name}.txt"
            self.save_tracked_urls(str(filename))
            analysis = self.analyze_urls()
            logger.info(f"\n📊 URL Analysis:")
            logger.info(f"   Total URLs: {analysis['total_urls']}")
            logger.info(f"   Unique domains: {analysis['unique_domains']}")
            logger.info(f"   Resource types: {analysis['resource_types']}")
            if analysis['recommendations']:
                logger.info(f"\n💡 Recommendations:")
                for rec in analysis['recommendations']:
                    logger.info(f"   • {rec}")
        
        return sentences
    
    def _scrape_pagination(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """Scrape articles from paginated list (config already has defaults applied)"""
        article_links = []
        max_pages = category_config.get('pages', 5)  # Should always be set by _apply_defaults
        base_url = category_config.get('url', '')
        pagination_type = category_config.get('type', 'pagination')
        page_param = category_config.get('page_param')  # e.g., 'page', 'p', 'pageNum'
        path_template = category_config.get('path')  # e.g., '/page/{page}'
        
        # Clean base URL: remove existing page parameters if page_param is specified
        if page_param and page_param in base_url:
            import re
            # Remove ?param=value or &param=value patterns
            base_url = re.sub(rf'[?&]{page_param}=\d+', '', base_url)
            # Clean up any trailing ? or &
            base_url = base_url.rstrip('?&')
            logger.info(f"   Cleaned URL: {base_url}")
        
        # Check if using URL template pagination
        is_url_template = pagination_type == 'url_template' or '{page}' in base_url or page_param or path_template
        
        for page in range(max_pages):
            logger.info(f"   Page {page + 1}/{max_pages}...")
            
            # Navigate to page if using URL template
            if is_url_template:
                # Build page URL based on config
                if '{page}' in base_url:
                    # Template substitution: url with {page} placeholder
                    page_url = base_url.format(page=page + 1)
                elif path_template:
                    # Path template: append path pattern to base URL
                    # Special case: page 1 usually doesn't need the path suffix
                    if page == 0:
                        page_url = base_url
                    else:
                        path = path_template.format(page=page + 1)
                        page_url = base_url.rstrip('/') + path
                elif page_param:
                    # Parameter appending: ?param=N or &param=N
                    separator = '&' if '?' in base_url else '?'
                    page_url = f"{base_url}{separator}{page_param}={page + 1}"
                else:
                    logger.error("url_template type requires either {page} in URL, page_param, or path")
                    break
                
                # Use FlareSolverr if available, otherwise use Selenium
                if self.flaresolverr_session:
                    html = self._flaresolverr_get(page_url)
                    if not html:
                        logger.info(f"   Failed to load page {page + 1} via FlareSolverr")
                        break
                    # Parse HTML and extract links using BeautifulSoup
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    links = self._extract_article_links_from_soup(soup, category_config)
                    new_links = [l for l in links if l not in article_links]
                    article_links.extend(new_links)
                    logger.info(f"   Found {len(new_links)} new articles on page {page + 1}")
                    
                    # Early exit: if no new articles found on this page, skip remaining pages
                    if not new_links and page > 0:
                        logger.info(f"   No new articles found - skipping remaining pages")
                        break
                    
                    time.sleep(category_config.get('delay', 2))
                    continue  # Skip normal extraction below
                else:
                    if not self._safe_get(page_url):
                        logger.info(f"   Failed to load page {page + 1}")
                        break
                    # Wait for collection page to load
                    self._wait_for_page(website_config, category_config, page_type='collection')
                    time.sleep(category_config.get('delay', 2))
            
            # Extract article links from current page (Selenium mode)
            links = self._extract_article_links(category_config)
            new_links = [l for l in links if l not in article_links]
            article_links.extend(new_links)
            
            logger.info(f"   Found {len(new_links)} new articles on page {page + 1}")
            
            # Early exit: if no new articles found on this page, skip remaining pages
            if not new_links and page > 0:
                logger.info(f"   No new articles found - skipping remaining pages")
                break
            
            # Navigate to next page (if not using URL template)
            if not is_url_template and page < max_pages - 1:
                if not self._go_to_next_page(category_config):
                    logger.info(f"   No more pages available")
                    break
                
                # Wait for collection page after navigation
                self._wait_for_page(website_config, category_config, page_type='collection')
                time.sleep(2)  # Wait between page loads
        
        return article_links
    
    def _scrape_infinite_scroll(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """Scrape articles from infinite scroll page (config already has defaults applied)"""
        article_links = []
        max_scrolls = category_config.get('scrolls', 10)  # Should always be set by _apply_defaults
        
        for scroll in range(max_scrolls):
            self._capture_network_logs()
            # Extract current articles
            links = self._extract_article_links(website_config)
            new_links = [l for l in links if l not in article_links]
            
            if not new_links and scroll > 0:
                logger.info(f"   No new articles found after scroll {scroll}")
                break
            
            article_links.extend(new_links)
            logger.info(f"   Scroll {scroll + 1}/{max_scrolls}: {len(new_links)} new articles")
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            self._capture_network_logs()
        
        return article_links
    
    def _scrape_click_load_more(
        self,
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """Scrape articles by clicking 'Load More' button (category_config has defaults applied)"""
        article_links = []
        max_clicks = category_config.get('clicks', 10)  # Should always be set by _apply_defaults
        load_more_selector = category_config.get('load_more_button', 'button.load-more')  # Should be set
        
        for click in range(max_clicks):
            self._capture_network_logs()
            # Extract current articles (pass category_config with merged selectors)
            links = self._extract_article_links(category_config)
            new_links = [l for l in links if l not in article_links]
            article_links.extend(new_links)
            
            logger.info(f"   Click {click + 1}/{max_clicks}: {len(new_links)} new articles")
            
            # Click load more button
            try:
                button = self._find_element(load_more_selector, category_config)
                
                if not button:
                    logger.info(f"   Load more button not found")
                    break
                
                # Scroll to button and click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                self._capture_network_logs()
                
            except Exception as e:
                logger.debug(f"   Could not click load more: {e}")
                break
        
        return article_links
    
    def _extract_article_links(self, config: Dict) -> List[str]:
        """Extract article links from current page (config has merged selectors)"""
        selectors = config.get('selectors', {})
        
        # Find article containers or direct links
        article_list_selector = selectors.get('article_list')
        
        links = []
        
        try:
            # Find all article elements
            articles = self._find_elements(article_list_selector, config)
            
            for article in articles:
                try:
                    # Check if the element itself is a link
                    href = article.get_attribute('href')
                    if href and href not in links:
                        links.append(href)
                            
                except Exception:
                    continue
        
        except Exception as e:
            logger.warning(f"Error extracting article links: {e}")
        
        return links
    
    def _extract_article_elements(self, config: Dict) -> List:
        """
        Extract article elements (not URLs) for click-through navigation.
        Used when click_through_navigation is enabled.
        
        Returns list of WebElements that can be clicked.
        """
        selectors = config.get('selectors', {})
        article_list_selector = selectors.get('article_list')
        
        elements = []
        
        try:
            # Find all article elements
            articles = self._find_elements(article_list_selector, config)
            elements = articles
            
        except Exception as e:
            logger.warning(f"Error extracting article elements: {e}")
        
        return elements
    
    def _extract_article_links_from_soup(self, soup, config: Dict) -> List[str]:
        """Extract article links from BeautifulSoup object (for FlareSolverr mode)"""
        selectors = config.get('selectors', {})
        article_list_selector = selectors.get('article_list')
        
        links = []
        
        try:
            # Handle multiple selector formats
            if isinstance(article_list_selector, str):
                selectors_to_try = [article_list_selector]
            elif isinstance(article_list_selector, list):
                selectors_to_try = article_list_selector
            else:
                selectors_to_try = []
            
            # Try each selector
            for selector in selectors_to_try:
                # BeautifulSoup CSS selector
                articles = soup.select(selector)
                
                for article in articles:
                    try:
                        # Get href from the element or find 'a' tag inside
                        # For Kurdistan24, we need links with '/story/' or '/opinion/'
                        href = article.get('href')
                        if not href:
                            # Find <a> tags with /story/ or /opinion/ in href
                            a_tag = article.find('a', href=lambda x: x and ('/story/' in x or '/opinion/' in x))
                            if not a_tag:
                                # Fallback: find any <a> tag
                                a_tag = article.find('a')
                            if a_tag:
                                href = a_tag.get('href')
                        
                        if href:
                            # Make absolute URL if needed
                            if href.startswith('/'):
                                base_url = config.get('url', '')
                                if '://' in base_url:
                                    # Extract domain from category URL
                                    from urllib.parse import urlparse
                                    parsed = urlparse(base_url)
                                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                            
                            if href and href not in links and href.startswith('http'):
                                links.append(href)
                    except Exception:
                        continue
                
                if links:
                    break  # Found links with this selector
        
        except Exception as e:
            logger.warning(f"Error extracting article links from soup: {e}")
        
        return links
    
    def _extract_from_articles(
        self,
        article_links: List[str],
        website_config: Dict,
        category_config: Dict
    ) -> List[str]:
        """Extract sentences from article pages"""
        sentences = []
        # V4.0: Use merged selectors from category_config (which has fallback chain applied)
        selectors = category_config.get('selectors', website_config.get('selectors', {}))
        
        for i, link in enumerate(article_links):
            try:
                # Skip if article already scraped
                if self.is_article_scraped(link):
                    logger.debug(f"   ⏭️  Skipping already scraped article: {link}")
                    continue
                
                # Navigate to article (use FlareSolverr if available)
                if self.flaresolverr_session:
                    html = self._flaresolverr_get(link)
                    if not html:
                        continue
                    
                    # Parse with BeautifulSoup (and try lxml for XPath support)
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')

                    # Attempt to load lxml.html for XPath selectors (optional)
                    lxml_doc = None
                    try:
                        import lxml.html as lh
                        lxml_doc = lh.fromstring(html)
                    except Exception:
                        lxml_doc = None

                    # Helper: extract text from a potential lxml node or BeautifulSoup element
                    def _node_text(node):
                        try:
                            # lxml element
                            return node.text_content().strip()
                        except Exception:
                            try:
                                # BeautifulSoup element
                                return node.get_text(strip=True)
                            except Exception:
                                return ''

                    # Extract title
                    title = None
                    title_selector = selectors.get('article_title')
                    if title_selector:
                        # Normalize to list
                        t_selectors = title_selector if isinstance(title_selector, list) else [title_selector]
                        for sel in t_selectors:
                            if not sel:
                                continue
                            # XPath selector - use lxml if available
                            if (isinstance(sel, str) and (sel.startswith('//') or sel.startswith('/'))) and lxml_doc is not None:
                                try:
                                    res = lxml_doc.xpath(sel)
                                    if res:
                                        title = _node_text(res[0])
                                        break
                                except Exception:
                                    pass
                            else:
                                try:
                                    elem = soup.select_one(sel)
                                    if elem:
                                        title = elem.get_text(strip=True)
                                        break
                                except Exception:
                                    continue

                    # Extract content using article_body
                    body_selector = selectors.get('article_body', 'p')
                    paragraphs = []

                    # Check if delimiter is specified in selector config
                    delimiter = None
                    if isinstance(body_selector, dict) and 'delimiter' in body_selector:
                        delimiter = body_selector.get('delimiter', '\\n')
                        if delimiter == '\\n':
                            delimiter = '\n'

                    # Handle dict format: {selector: '...', multiple: true, delimiter: '\n'}
                    actual_selector = body_selector
                    if isinstance(body_selector, dict):
                        actual_selector = body_selector.get('selector', 'p')

                    # Normalize selectors list
                    sel_list = actual_selector if isinstance(actual_selector, list) else [actual_selector]

                    # Try selectors in order; support XPath via lxml_doc when possible
                    found = False
                    for sel in sel_list:
                        if not sel:
                            continue
                        # XPath
                        if isinstance(sel, str) and (sel.startswith('//') or sel.startswith('/')):
                            if lxml_doc is None:
                                # Can't evaluate XPath without lxml; skip
                                continue
                            try:
                                nodes = lxml_doc.xpath(sel)
                                if nodes:
                                    # lxml nodes
                                    paragraphs = nodes
                                    found = True
                                    break
                            except Exception:
                                continue
                        else:
                            try:
                                bs_nodes = soup.select(sel)
                                if bs_nodes:
                                    paragraphs = bs_nodes
                                    found = True
                                    break
                            except Exception:
                                continue

                    # Extract text from paragraphs
                    article_text = []
                    
                    # Include title as first sentence if available
                    if title and len(title.strip()) > 20:
                        article_text.append(title.strip())
                    
                    for p in paragraphs:
                        text = _node_text(p)
                        if len(text) > 20:
                            article_text.append(text)
                    
                else:
                    # Standard Selenium mode
                    if not self._safe_get(link):
                        continue
                    
                    # Wait for article page content
                    self._wait_for_page(website_config, category_config, page_type='article')
                    
                    # Extract title
                    title = self._extract_text(selectors.get('article_title'))
                    
                    # Extract content using V4.0 article_body
                    body_selector = selectors.get('article_body', 'p')
                    paragraphs = self._find_elements(body_selector, website_config)
                    
                    # Check if delimiter is specified in selector config
                    delimiter = None
                    if isinstance(body_selector, dict) and 'delimiter' in body_selector:
                        delimiter = body_selector.get('delimiter', '\\n')
                        # Handle escaped newline
                        if delimiter == '\\n':
                            delimiter = '\n'
                    
                    # Extract text from paragraphs
                    article_text = []
                    
                    # Include title as first sentence if available
                    if title and len(title.strip()) > 20:
                        article_text.append(title.strip())
                    
                    for p in paragraphs:
                        text = p.text.strip()
                        # Clean HTML tags that might be in the text
                        text = re.sub(r'<[^>]+>', '', text)
                        if len(text) > 20:
                            article_text.append(text)
                    
                    # DEBUG: Log extraction results
                    logger.info(f"   📝 Found title + {len(paragraphs)} paragraph elements, {len(article_text)} total with >20 chars")
                    if article_text:
                        logger.info(f"      First: {article_text[0][:80]}...")
                
                # Language detection
                if article_text:
                    full_text = ' '.join(article_text)
                    
                    # Only detect language if detector is available
                    if self.lang_detector:
                        lang = self.lang_detector.detect(full_text)
                        logger.info(f"   🌍 Detected language: {lang}")
                        
                        # Filter by language if configured
                        lang_filter = website_config.get('language_detection', {}).get('filter', [])
                        if lang_filter:
                            logger.info(f"   📋 Language filter: {lang_filter}")
                            if lang not in lang_filter:
                                logger.info(f"   ⚠️  Skipping article (language '{lang}' not in filter {lang_filter})")
                                continue
                    
                    # Deduplication check (if available)
                    if self.deduplicator:
                        is_dup, reason = self.deduplicator.is_duplicate(
                            {},
                            link,
                            title or '',
                            full_text
                        )
                        
                        if is_dup:
                            logger.info(f"   ⚠️  Skipping duplicate: {reason}")
                            self.stats['duplicates_skipped'] += 1
                            continue
                    
                    logger.info(f"   ➕ Adding sentences (delimiter={delimiter})...")
                    # Add sentences - split by delimiter if specified
                    if delimiter:
                        # Join all paragraphs and split by delimiter
                        combined_text = delimiter.join(article_text)
                        split_sentences = [s.strip() for s in combined_text.split(delimiter) if s.strip() and len(s.strip()) > 20]
                        logger.info(f"      Split into {len(split_sentences)} sentences")
                        sentences.extend(split_sentences)
                    else:
                        # Use paragraphs as-is
                        logger.info(f"      Adding {len(article_text)} paragraphs as sentences")
                        sentences.extend(article_text)
                    self.stats['articles_processed'] += 1
                    
                    # Mark article as scraped for deduplication
                    self.save_scraped_article(link)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"   Processed {i + 1}/{len(article_links)} articles...")
                
            except Exception as e:
                logger.debug(f"   Error processing article {link}: {e}")
                continue
        
        self.stats['sentences_extracted'] += len(sentences)
        return sentences
    
    def _extract_from_articles_click_through(
        self,
        website_config: Dict,
        category_config: Dict,
        max_articles: Optional[int] = None
    ) -> List[str]:
        """
        Extract sentences using click-through navigation.
        Clicks article elements from list page instead of navigating to URLs.
        Uses browser back button for efficient navigation - no page refresh needed.
        Preserves session state for websites with anti-scraping protection.
        
        OPTIMIZED: Extracts article list ONCE at the beginning, then uses index-based
        re-selection after each back button press. Much faster than re-extracting entire list!
        """
        sentences = []
        selectors = category_config.get('selectors', website_config.get('selectors', {}))
        
        # Get article wait time
        article_wait = category_config.get('article_wait', website_config.get('article_wait', 2))
        
        # Get back button delay (can be much shorter than article wait)
        back_delay = category_config.get('back_delay', 0.5)  # Default 0.5s - much faster!
        
        # Track the list page URL as backup
        list_page_url = self.driver.current_url
        
        logger.info(f"   🖱️  Click-through mode: Using browser back button for fast navigation")
        
        # OPTIMIZATION: Extract article list ONCE at the beginning
        article_list_selector = selectors.get('article_list')
        initial_elements = self._extract_article_elements(category_config)
        
        if not initial_elements:
            logger.warning("   No article elements found for click-through navigation")
            return []
        
        # Determine how many articles to process
        total_articles = len(initial_elements)
        articles_to_process = min(total_articles, max_articles) if max_articles else total_articles
        
        logger.info(f"   Found {total_articles} articles, will process {articles_to_process}")
        
        # Process each article by index
        for article_index in range(articles_to_process):
            try:
                # Re-select ONLY the current article element (much faster than extracting all!)
                # After back button, elements become stale, so we re-find using the same selector
                current_elements = self._find_elements(article_list_selector, category_config)
                
                if article_index >= len(current_elements):
                    logger.warning(f"   Article {article_index + 1} no longer available, stopping")
                    break
                
                element = current_elements[article_index]
                
                # Get the article URL for logging
                try:
                    article_url = element.get_attribute('href')
                except:
                    article_url = "unknown"
                
                # Skip if article already scraped
                if article_url != "unknown" and self.is_article_scraped(article_url):
                    logger.debug(f"   ⏭️  Skipping already scraped article: {article_url}")
                    continue
                
                # Click the article element
                try:
                    element.click()
                except Exception as click_error:
                    logger.debug(f"   Direct click failed, trying JavaScript click: {click_error}")
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                    except Exception as js_error:
                        logger.warning(f"   Could not click article {article_index + 1}: {js_error}")
                        continue
                
                # Wait for article page to load
                time.sleep(article_wait)
                
                # Extract title
                title = self._extract_text(selectors.get('article_title'))
                
                # Extract content using article_body
                body_selector = selectors.get('article_body', 'p')
                paragraphs = self._find_elements(body_selector, website_config)
                
                # Check if delimiter is specified
                delimiter = None
                if isinstance(body_selector, dict) and 'delimiter' in body_selector:
                    delimiter = body_selector.get('delimiter', '\\n')
                    if delimiter == '\\n':
                        delimiter = '\n'
                
                # Extract text from paragraphs
                article_text = []
                
                # Include title as first sentence if available
                if title and len(title.strip()) > 20:
                    article_text.append(title.strip())
                
                for p in paragraphs:
                    try:
                        text = p.text.strip()
                        if len(text) > 20:
                            article_text.append(text)
                    except:
                        continue
                
                # Process extracted text
                if article_text:
                    full_text = ' '.join(article_text)
                    
                    # Language detection
                    if self.lang_detector:
                        lang = self.lang_detector.detect(full_text)
                        lang_filter = website_config.get('language_detection', {}).get('filter', [])
                        if lang_filter and lang not in lang_filter:
                            logger.debug(f"   Skipping article (language: {lang})")
                            # Navigate back using browser back button (FAST!)
                            self.driver.back()
                            time.sleep(back_delay)
                            continue
                    
                    # Deduplication check
                    if self.deduplicator:
                        is_dup, reason = self.deduplicator.is_duplicate(
                            {},
                            article_url,
                            title or '',
                            full_text
                        )
                        if is_dup:
                            logger.debug(f"   Skipping duplicate: {reason}")
                            self.stats['duplicates_skipped'] += 1
                            # Navigate back using browser back button (FAST!)
                            self.driver.back()
                            time.sleep(back_delay)
                            continue
                    
                    # Add sentences - split by delimiter if specified
                    if delimiter:
                        combined_text = delimiter.join(article_text)
                        split_sentences = [s.strip() for s in combined_text.split(delimiter) if s.strip() and len(s.strip()) > 20]
                        sentences.extend(split_sentences)
                    else:
                        sentences.extend(article_text)
                    
                    self.stats['articles_processed'] += 1
                    
                    # Mark article as scraped for deduplication
                    if article_url != "unknown":
                        self.save_scraped_article(article_url)
                
                # Navigate back to list page using browser back button (FAST!)
                self.driver.back()
                time.sleep(back_delay)  # Much shorter delay - page is cached!
                
                if (article_index + 1) % 5 == 0:
                    logger.info(f"   Processed {article_index + 1}/{articles_to_process} articles...")
                
            except Exception as e:
                logger.warning(f"   Error processing article {article_index + 1}: {e}")
                # Try to get back to list page using back button
                try:
                    self.driver.back()
                    time.sleep(back_delay)
                except:
                    # If back fails, navigate to list page URL (last resort)
                    try:
                        logger.debug("   Back button failed, reloading list page...")
                        self.driver.get(list_page_url)
                        time.sleep(2)
                    except:
                        logger.error("   Could not return to list page, aborting")
                        break
                continue
        
        self.stats['sentences_extracted'] += len(sentences)
        return sentences
    
    def _init_stealth_driver(self):
        """Initialize Selenium driver with stealth mode (always headless)"""
        options = webdriver.ChromeOptions()
        
        # Always run in headless mode for production
        options.add_argument('--headless=new')  # New headless mode (Chrome 109+)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Performance optimization: Block unnecessary resources
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Block images for faster loading
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
        }
        options.add_experimental_option("prefs", prefs)
        
        # Enable performance logging for URL tracking if debug mode
        if self.url_debug_mode:
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        if self.stealth and HAS_ADVANCED:
            # Use stealth mode if available
            options_config = self.stealth.get_stealth_options()
            options.add_argument(f"user-agent={options_config['user_agent']}")
            for arg in options_config['arguments']:
                if arg not in ['--headless', '--headless=new']:  # Don't duplicate headless
                    options.add_argument(arg)
        
        # Specify chromedriver path explicitly to avoid Selenium Manager issues
        try:
            from selenium.webdriver.chrome.service import Service
            import shutil
            chromedriver_path = shutil.which('chromedriver')
            if chromedriver_path:
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Fallback: try without explicit path
                self.driver = webdriver.Chrome(options=options)
        except Exception:
            # Fallback: try without Service
            self.driver = webdriver.Chrome(options=options)
        
        if self.stealth and HAS_ADVANCED:
            self.stealth.apply_stealth_mode(self.driver)
            logger.info("✅ Browser initialized (headless + stealth mode)")
        else:
            logger.info("✅ Browser initialized (headless mode)")

    
    def _init_flaresolverr(self, website_config: Dict) -> bool:
        """
        Initialize FlareSolverr session for Cloudflare bypass
        
        Returns True if session created successfully, False otherwise
        """
        flaresolverr_config = website_config.get('flaresolverr', {})
        
        if not flaresolverr_config.get('enabled', False):
            return False
        
        flaresolverr_url = flaresolverr_config.get('url', 'http://localhost:8191')
        max_timeout = flaresolverr_config.get('max_timeout', 60000)
        
        # Retry logic for FlareSolverr startup
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Check if FlareSolverr is running
                if attempt == 0:
                    logger.info(f"🔍 Checking FlareSolverr at {flaresolverr_url}")
                else:
                    logger.info(f"🔍 Retry {attempt + 1}/{max_retries}...")
                
                response = requests.get(flaresolverr_url, timeout=5)
                
                if response.status_code != 200:
                    logger.error(f"❌ FlareSolverr not responding (status {response.status_code})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False
                
                data = response.json()
                logger.info(f"✅ FlareSolverr v{data.get('version', 'unknown')} is running")
                
                # Create session
                session_id = f"session_{int(time.time())}"
                logger.info(f"🔧 Creating FlareSolverr session: {session_id}")
                
                response = requests.post(
                    f'{flaresolverr_url}/v1',
                    json={
                        "cmd": "sessions.create",
                        "session": session_id,
                        "maxTimeout": max_timeout
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'ok':
                        self.flaresolverr_session = {
                            'id': session_id,
                            'url': flaresolverr_url,
                            'max_timeout': max_timeout
                        }
                        logger.info(f"✅ FlareSolverr session created: {session_id}")
                        return True
                    else:
                        logger.error(f"❌ FlareSolverr session creation failed: {result.get('message')}")
                        return False
                else:
                    logger.error(f"❌ FlareSolverr API error (status {response.status_code})")
                    return False
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⏳ Connection error, waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ Cannot connect to FlareSolverr at {flaresolverr_url} after {max_retries} attempts")
                    logger.error(f"   Make sure FlareSolverr is running: docker start flaresolverr")
                    logger.error(f"   Error: {e}")
                    return False
            except Exception as e:
                logger.error(f"❌ FlareSolverr initialization error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    def _destroy_flaresolverr_session(self):
        """Clean up FlareSolverr session"""
        if not self.flaresolverr_session:
            return
        
        try:
            session_id = self.flaresolverr_session['id']
            flaresolverr_url = self.flaresolverr_session['url']
            
            logger.info(f"🧹 Destroying FlareSolverr session: {session_id}")
            
            response = requests.post(
                f'{flaresolverr_url}/v1',
                json={
                    "cmd": "sessions.destroy",
                    "session": session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ FlareSolverr session destroyed")
            else:
                logger.warning(f"⚠️ Failed to destroy FlareSolverr session (status {response.status_code})")
                
        except Exception as e:
            logger.warning(f"⚠️ Error destroying FlareSolverr session: {e}")
        finally:
            self.flaresolverr_session = None
    
    def _flaresolverr_get(self, url: str) -> Optional[str]:
        """
        Fetch URL using FlareSolverr to bypass Cloudflare
        
        Returns HTML content or None if failed
        """
        if not self.flaresolverr_session:
            logger.error("❌ FlareSolverr session not initialized")
            return None
        
        try:
            session_id = self.flaresolverr_session['id']
            flaresolverr_url = self.flaresolverr_session['url']
            max_timeout = self.flaresolverr_session['max_timeout']
            
            logger.info(f"🌐 Fetching via FlareSolverr: {url}")
            
            response = requests.post(
                f'{flaresolverr_url}/v1',
                json={
                    "cmd": "request.get",
                    "url": url,
                    "session": session_id,
                    "maxTimeout": max_timeout
                },
                timeout=max_timeout / 1000 + 10  # Add 10s buffer to timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'ok':
                    solution = result.get('solution', {})
                    html = solution.get('response')
                    
                    if html:
                        # Include session id in log so it's clear this fetch used FlareSolverr
                        session_id = self.flaresolverr_session.get('id') if self.flaresolverr_session else 'unknown'
                        logger.info(f"✅ FlareSolverr (session={session_id}) fetched {len(html)} bytes")
                        return html
                    else:
                        logger.error(f"❌ FlareSolverr returned empty response")
                        return None
                else:
                    error_msg = result.get('message', 'Unknown error')
                    logger.error(f"❌ FlareSolverr request failed: {error_msg}")
                    return None
            else:
                logger.error(f"❌ FlareSolverr API error (status {response.status_code})")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ FlareSolverr request timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"❌ FlareSolverr request error: {e}")
            return None

    
    def _safe_get(self, url: str, delay: int = 2) -> bool:
        """Safely navigate to URL with error handling"""
        try:
            if not self.driver:
                self._init_stealth_driver()
            
            # Track URL if debugging is enabled
            if self.url_debug_mode and url not in self._tracked_url_set:
                self.tracked_urls.append(url)
                self._tracked_url_set.add(url)
                logger.debug(f"📍 Tracked: {url}")
            
            self.driver.get(url)
            time.sleep(delay)
            self._capture_network_logs()
            return True
        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            return False
    
    def _capture_network_logs(self):
        """Capture network activity from Chrome performance logs when debugging"""
        if not self.url_debug_mode or not self.driver:
            return

        try:
            performance_logs = self.driver.get_log('performance')
        except Exception as exc:
            logger.debug(f"   Unable to fetch performance logs: {exc}")
            return

        for entry in performance_logs:
            try:
                message = json.loads(entry.get('message', '{}'))
                message_data = message.get('message', {})
                method = message_data.get('method')

                if method not in ('Network.requestWillBeSent', 'Network.responseReceived'):
                    continue

                params = message_data.get('params', {})
                url = None

                if method == 'Network.requestWillBeSent':
                    request = params.get('request', {})
                    url = request.get('url')
                elif method == 'Network.responseReceived':
                    response = params.get('response', {})
                    url = response.get('url')

                if not url or not url.startswith(('http://', 'https://')):
                    continue

                if url not in self._tracked_url_set:
                    self.tracked_urls.append(url)
                    self._tracked_url_set.add(url)
            except (json.JSONDecodeError, TypeError):
                continue
            except Exception as exc:
                logger.debug(f"   Failed to parse performance log entry: {exc}")

    def _wait_for_page(
        self,
        website_config: Dict,
        category_config: Dict = None,
        page_type: str = 'collection'
    ):
        """
        Wait for page to load based on configuration (V4.0+)
        
        Args:
            website_config: Website configuration
            category_config: Category configuration (optional)
            page_type: Type of page - 'collection' for list pages, 'article' for article pages
        
        Supports:
            - collection_wait: Wait config for collection/list pages
            - article_wait: Wait config for article pages (can be int seconds or dict)
            - wait: Default wait config for both types (fallback)
        """
        # Determine which wait config to use based on page type
        wait_config = None
        
        if page_type == 'collection':
            # Try collection_wait first, then fall back to wait
            if category_config:
                wait_config = category_config.get('collection_wait')
            if not wait_config and website_config:
                wait_config = website_config.get('collection_wait')
            if not wait_config:
                # Fall back to generic 'wait'
                wait_config = category_config.get('wait') if category_config else None
                if not wait_config:
                    wait_config = website_config.get('wait', {})
        
        elif page_type == 'article':
            # Try article_wait first, then fall back to wait
            if category_config:
                article_wait = category_config.get('article_wait')
                if article_wait is not None:
                    # article_wait can be int (seconds) or dict
                    if isinstance(article_wait, int):
                        wait_config = {'selector': None, 'timeout': article_wait}
                    else:
                        wait_config = article_wait
            
            if not wait_config and website_config:
                article_wait = website_config.get('article_wait')
                if article_wait is not None:
                    if isinstance(article_wait, int):
                        wait_config = {'selector': None, 'timeout': article_wait}
                    else:
                        wait_config = article_wait
            
            if not wait_config:
                # Fall back to generic 'wait'
                wait_config = category_config.get('wait') if category_config else None
                if not wait_config:
                    wait_config = website_config.get('wait', {})
        
        # Default wait config if nothing specified
        if not wait_config:
            wait_config = {}
        
        # V4.0: Use selector + timeout (null selector = manual delay)
        selector = wait_config.get('selector')  # Can be null/None or CSS selector
        timeout = wait_config.get('timeout', 3)  # Default 3 seconds
        
        if selector:
            # Wait for specific selector (V4.0: selector is not null)
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for selector: {selector}")
                # Fallback to manual delay
                time.sleep(timeout)
        else:
            # Manual delay (V4.0: selector is null)
            time.sleep(timeout)

        self._capture_network_logs()
    
    def _find_element(
        self,
        selector: Any,
        website_config: Dict
    ):
        """Find element with fallback support
        
        Supports:
        - String: CSS or XPath (auto-detected if starts with //)
        - List: Array of CSS/XPath strings (tries each until one works)
        - Dict with 'selector' key: {'selector': '//...', 'multiple': true, 'delimiter': '\\n'}
        - Dict with 'type' key: {'type': 'xpath', 'value': '//...'} (legacy)
        """
        if not selector:
            return None
        
        # Normalize to list of selectors
        if isinstance(selector, str):
            selectors = [selector]
        elif isinstance(selector, list):
            selectors = selector
        elif isinstance(selector, dict):
            # Handle dict formats - extract the actual selector
            if 'selector' in selector:
                # New format: {'selector': '//... or CSS or [...array]', 'multiple': true, 'delimiter': '\n'}
                extracted = selector.get('selector')
                # The selector value itself can be a string or array
                if isinstance(extracted, list):
                    selectors = extracted
                else:
                    selectors = [extracted]
            elif 'type' in selector and 'value' in selector:
                # Old format: {'type': 'xpath', 'value': '//...'}
                selectors = [selector.get('value')]
            else:
                return None
        else:
            return None
        
        # Try each selector until one returns an element
        for sel in selectors:
            if not sel or not isinstance(sel, str):
                continue
                
            try:
                # Auto-detect XPath (starts with // or /)
                if sel.startswith('//') or sel.startswith('/'):
                    return self.driver.find_element(By.XPATH, sel)
                else:
                    return self.driver.find_element(By.CSS_SELECTOR, sel)
            except:
                continue
        
        return None
    
    def _find_elements(
        self,
        selector: Any,
        website_config: Dict
    ) -> List:
        """Find elements with fallback support
        
        Supports:
        - String: CSS or XPath (auto-detected if starts with //)
        - List: Array of CSS/XPath strings (tries each until one works)
        - Dict with 'selector' key: {'selector': '//...', 'multiple': true, 'delimiter': '\\n'}
        - Dict with 'type' key: {'type': 'xpath', 'value': '//...'} (legacy)
        """
        if not selector:
            return []
        
        # Normalize to list of selectors
        if isinstance(selector, str):
            selectors = [selector]
        elif isinstance(selector, list):
            selectors = selector
        elif isinstance(selector, dict):
            # Handle dict formats - extract the actual selector
            if 'selector' in selector:
                # New format: {'selector': '//... or CSS or [...array]', 'multiple': true, 'delimiter': '\n'}
                extracted = selector.get('selector')
                # The selector value itself can be a string or array
                if isinstance(extracted, list):
                    selectors = extracted
                else:
                    selectors = [extracted]
            elif 'type' in selector and 'value' in selector:
                # Old format: {'type': 'xpath', 'value': '//...'}
                selectors = [selector.get('value')]
            else:
                return []
        else:
            return []
        
        # Try each selector until one returns elements
        for sel in selectors:
            if not sel or not isinstance(sel, str):
                continue
                
            try:
                # Auto-detect XPath (starts with // or /)
                if sel.startswith('//') or sel.startswith('/'):
                    elements = self.driver.find_elements(By.XPATH, sel)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
                
                if elements:
                    return elements
            except:
                continue
        
        return []
    
    def _extract_text(self, selector: Any) -> str:
        """Extract text from element"""
        elem = self._find_element(selector, {})
        if elem:
            return elem.text.strip()
        return ''
    
    def _go_to_next_page(self, category_config: Dict) -> bool:
        """Navigate to next page"""
        next_button_selector = category_config.get('next_button', 'a.next')
        
        try:
            button = self._find_element(next_button_selector, {})
            if button:
                button.click()
                return True
        except:
            pass
        
        return False
    
    def _create_empty_result(self, website_name: str, reason: str) -> ScrapeResult:
        """Create empty result"""
        return ScrapeResult(
            website=website_name,
            success=False,
            articles_scraped=0,
            sentences_extracted=0,
            duration=0,
            error=reason
        )
    
    # ========================================================================
    # Article Link Deduplication
    # ========================================================================
    
    def load_scraped_articles(self):
        """Load previously scraped article links from database"""
        try:
            import sqlite3
            if not self.article_link_db_path.exists():
                return
            
            conn = sqlite3.connect(str(self.article_link_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM scraped_articles")
            self.scraped_article_links = set(row[0] for row in cursor.fetchall())
            conn.close()
            
            logger.info(f"📚 Loaded {len(self.scraped_article_links)} previously scraped article URLs")
        except Exception as e:
            logger.warning(f"Could not load scraped articles: {e}")
            self.scraped_article_links = set()
    
    def save_scraped_article(self, url: str):
        """Save a scraped article URL to the database"""
        try:
            import sqlite3
            self.scraped_article_links.add(url)
            
            conn = sqlite3.connect(str(self.article_link_db_path))
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_articles (
                    url TEXT PRIMARY KEY,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert the URL
            cursor.execute(
                "INSERT OR IGNORE INTO scraped_articles (url) VALUES (?)",
                (url,)
            )
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Could not save scraped article: {e}")
    
    def clear_scraped_articles(self):
        """Clear the scraped articles database"""
        try:
            if self.article_link_db_path.exists():
                self.article_link_db_path.unlink()
            self.scraped_article_links = set()
            logger.info("🗑️  Cleared scraped articles database")
        except Exception as e:
            logger.warning(f"Could not clear scraped articles: {e}")
    
    def is_article_scraped(self, url: str) -> bool:
        """Check if an article URL has already been scraped"""
        return url in self.scraped_article_links
    
    # ========================================================================
    # URL Tracking & Whitelisting for Performance Optimization
    # ========================================================================
    
    def enable_url_debugging(self):
        """Enable URL tracking to see all requests being made"""
        self.url_debug_mode = True
        self.tracked_urls = []
        self._tracked_url_set = set()
        logger.info("🔍 URL debugging enabled - will track all requests")
    
    def disable_url_debugging(self):
        """Disable URL tracking"""
        self.url_debug_mode = False
        logger.info("🔍 URL debugging disabled")
    
    def get_tracked_urls(self) -> List[str]:
        """Get all tracked URLs"""
        return self.tracked_urls
    
    def save_tracked_urls(self, filename: str = 'tracked_urls.txt'):
        """Save tracked URLs to a file for analysis"""
        if not self.tracked_urls:
            logger.warning("No URLs tracked. Enable URL debugging first.")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tracked URLs ({len(self.tracked_urls)} total)\n")
            f.write(f"# Tracked on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Group by resource type
            html_urls = []
            script_urls = []
            style_urls = []
            image_urls = []
            other_urls = []
            
            for url in self.tracked_urls:
                if any(ext in url.lower() for ext in ['.js']):
                    script_urls.append(url)
                elif any(ext in url.lower() for ext in ['.css']):
                    style_urls.append(url)
                elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']):
                    image_urls.append(url)
                elif any(ext in url.lower() for ext in ['.html', '.htm']) or '?' in url or url.endswith('/'):
                    html_urls.append(url)
                else:
                    other_urls.append(url)
            
            f.write(f"# HTML Pages ({len(html_urls)})\n")
            for url in html_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Scripts ({len(script_urls)})\n")
            for url in script_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Styles ({len(style_urls)})\n")
            for url in style_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Images ({len(image_urls)})\n")
            for url in image_urls:
                f.write(f"{url}\n")
            
            f.write(f"\n# Other ({len(other_urls)})\n")
            for url in other_urls:
                f.write(f"{url}\n")
        
        logger.info(f"✅ Tracked URLs saved to {filename}")
        logger.info(f"   Total: {len(self.tracked_urls)} URLs")
        logger.info(f"   HTML: {len(html_urls)}, Scripts: {len(script_urls)}, Styles: {len(style_urls)}, Images: {len(image_urls)}, Other: {len(other_urls)}")
    
    def set_url_whitelist(self, patterns: List[str]):
        """Set URL whitelist patterns (only these URLs will be loaded)"""
        self.url_whitelist = patterns
        logger.info(f"🔒 URL whitelist set: {len(patterns)} patterns")
    
    def add_to_whitelist(self, pattern: str):
        """Add a pattern to the whitelist"""
        if pattern not in self.url_whitelist:
            self.url_whitelist.append(pattern)
            logger.info(f"✅ Added to whitelist: {pattern}")
    
    def _load_url_filtering(self, website_config: Dict):
        """
        Load URL filtering configuration with preset support
        
        Supports multiple approaches:
        1. Template-based: template: 'rudaw' (uses predefined template)
        2. Preset-based: preset: 'standard' (applies preset patterns)
        3. Manual: Direct whitelist/blacklist arrays in config
        4. Hybrid: Preset + website-specific whitelist/blacklist additions
        
        Processing order:
        - Load preset/template base patterns (if specified)
        - Add website-specific whitelist patterns (merged/extended)
        - Add website-specific blacklist patterns (merged/extended)
        - Add extra_blacklist patterns (always appended)
        """
        url_filtering = website_config.get('url_filtering', {})
        if not url_filtering:
            self.blocked_resources = list(self._default_blocked_resources)
            return

        # Reset filters to defaults before applying overrides
        self.blocked_resources = list(self._default_blocked_resources)
        self.url_whitelist = []

        if url_filtering.get('disabled'):
            self.blocked_resources = []
            logger.info("📭 URL filtering disabled for this website")
            return
        
        # Try to load presets file
        presets_file = self.config_path / 'url_filtering_presets.yaml' if self.config_path.is_dir() else None
        presets = {}
        resource_types = {}
        templates = {}
        
        if presets_file and presets_file.exists():
            try:
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets_data = yaml.safe_load(f) or {}
                    presets = presets_data.get('presets', {})
                    resource_types = presets_data.get('resource_types', {})
                    templates = presets_data.get('templates', {})
                logger.debug(f"📦 Loaded {len(presets)} presets from url_filtering_presets.yaml")
            except Exception as e:
                logger.warning(f"Could not load URL filtering presets: {e}")
        
        # Step 1: Process template (if specified)
        template_whitelist = []
        template_blacklist = []
        
        if url_filtering.get('template'):
            template_name = url_filtering['template']
            if template_name in templates:
                template = templates[template_name]
                logger.info(f"📋 Using URL filtering template: {template_name}")
                
                # Collect template patterns (don't apply yet)
                template_whitelist = template.get('whitelist', [])
                template_blacklist = template.get('blacklist', [])
                
                # Apply template preset to blocked_resources
                if template.get('preset') and template['preset'] in presets:
                    self._apply_preset(presets[template['preset']], resource_types)
            else:
                logger.warning(f"Template '{template_name}' not found in presets file")
        
        # Step 2: Process preset (if specified and no template)
        elif url_filtering.get('preset'):
            preset_name = url_filtering['preset']
            if preset_name in presets:
                preset = presets[preset_name]
                logger.info(f"📦 Using URL filtering preset: {preset_name} - {preset.get('description', '')}")
                self._apply_preset(preset, resource_types)
            else:
                logger.warning(f"Preset '{preset_name}' not found in presets file")
        
        # Step 3: Merge website-specific whitelist with template/preset whitelist
        final_whitelist = []
        
        # Add template whitelist patterns first
        if template_whitelist:
            final_whitelist.extend(template_whitelist)
            logger.info(f"  ✅ Template whitelist: {len(template_whitelist)} patterns")
        
        # Add website-specific whitelist patterns (merged or standalone)
        website_whitelist = url_filtering.get('whitelist', [])
        if website_whitelist:
            # Merge with template patterns (avoid duplicates)
            for pattern in website_whitelist:
                if pattern not in final_whitelist:
                    final_whitelist.append(pattern)
            logger.info(f"  ✅ Website whitelist: {len(website_whitelist)} patterns")
        
        # Apply final merged whitelist
        if final_whitelist:
            self.set_url_whitelist(final_whitelist)
            logger.info(f"📋 Total whitelist patterns: {len(final_whitelist)}")
        
        # Step 4: Add website-specific blacklist patterns
        website_blacklist = url_filtering.get('blacklist', [])
        if template_blacklist:
            self.blocked_resources.extend(template_blacklist)
            logger.info(f"  🚫 Template blacklist: {len(template_blacklist)} patterns")
        
        if website_blacklist:
            self.blocked_resources.extend(website_blacklist)
            logger.info(f"  🚫 Website blacklist: {len(website_blacklist)} patterns")
        
        # Extra blacklist (for preset + custom additions)
        if url_filtering.get('extra_blacklist'):
            self.blocked_resources.extend(url_filtering['extra_blacklist'])
            logger.info(f"🚫 Added {len(url_filtering['extra_blacklist'])} extra blacklist patterns")
    
    def _apply_preset(self, preset: Dict, resource_types: Dict):
        """Apply a URL filtering preset"""
        # Check if preset uses whitelist-only mode
        if preset.get('mode') == 'whitelist_only':
            logger.info("  ⚠️  Whitelist-only mode - must specify whitelist patterns in config")
            return
        
        # Apply blacklist types from preset
        blacklist_types = preset.get('blacklist_types', [])
        for type_name in blacklist_types:
            if type_name in resource_types:
                patterns = resource_types[type_name]
                self.blocked_resources.extend(patterns)
                logger.info(f"  🚫 Blocking {type_name}: {len(patterns)} patterns")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics including URL tracking"""
        stats = self.stats.copy()
        stats['tracked_urls_count'] = len(self.tracked_urls)
        stats['url_debug_mode'] = self.url_debug_mode
        stats['whitelist_patterns'] = len(self.url_whitelist)
        return stats
    
    def analyze_urls(self) -> Dict:
        """Analyze tracked URLs and provide recommendations"""
        if not self.tracked_urls:
            return {"error": "No URLs tracked. Enable URL debugging first."}
        
        analysis = {
            'total_urls': len(self.tracked_urls),
            'unique_domains': len(set(url.split('/')[2] if len(url.split('/')) > 2 else '' for url in self.tracked_urls)),
            'resource_types': {},
            'third_party_urls': [],
            'recommendations': []
        }
        
        # Categorize URLs
        for url in self.tracked_urls:
            if any(ext in url.lower() for ext in self.blocked_resources):
                resource_type = 'blocked_resource'
            elif '.js' in url.lower():
                resource_type = 'javascript'
            elif '.css' in url.lower():
                resource_type = 'stylesheet'
            elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                resource_type = 'image'
            else:
                resource_type = 'html/api'
            
            analysis['resource_types'][resource_type] = analysis['resource_types'].get(resource_type, 0) + 1
            
            # Identify third-party URLs
            if any(tracker in url.lower() for tracker in ['google-analytics', 'facebook', 'twitter', 'ads', 'tracking']):
                analysis['third_party_urls'].append(url)
        
        # Generate recommendations
        if analysis['resource_types'].get('blocked_resource', 0) > 0:
            analysis['recommendations'].append(f"Block {analysis['resource_types']['blocked_resource']} unnecessary resources")
        if len(analysis['third_party_urls']) > 0:
            analysis['recommendations'].append(f"Block {len(analysis['third_party_urls'])} third-party tracking URLs")
        if analysis['resource_types'].get('image', 0) > 10:
            analysis['recommendations'].append("Consider disabling image loading (already implemented)")
        
        return analysis


if __name__ == '__main__':
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Generic YAML-Driven Scraper')
    parser.add_argument('--config', default='websites.yaml', help='YAML config file')
    parser.add_argument('--website', required=True, help='Website to scrape')
    parser.add_argument('--category', help='Specific category (optional)')
    parser.add_argument('--max-articles', type=int, help='Max articles per category')
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = GenericScraper(args.config)
    
    # Scrape
    if args.category:
        sentences = scraper.scrape_category(args.website, args.category, args.max_articles)
        print(f"\n✅ Extracted {len(sentences)} sentences")

        if scraper.url_debug_mode and scraper.tracked_urls:
            filename = f"tracked_urls_{args.website}_{args.category}.txt"
            scraper.save_tracked_urls(filename)
            analysis = scraper.analyze_urls()
            print(f"\n📊 URL Analysis saved to {filename}")
            print(f"   Total URLs: {analysis.get('total_urls', 0)}")
            print(f"   Unique domains: {analysis.get('unique_domains', 0)}")
            resource_types = analysis.get('resource_types', {})
            if resource_types:
                print(f"   Resource types: {resource_types}")
            if analysis.get('recommendations'):
                print("   Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"    - {rec}")
    else:
        result = scraper.scrape_website(args.website, max_articles=args.max_articles)
        print(f"\n✅ {result}")
