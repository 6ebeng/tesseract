"""
Generic YAML-Driven Web Scraper (Refactored with Mixins)

Universal scraper that reads configuration from YAML files.
Handles all category types: pagination, infinite scroll, click-based.

Architecture:
- BaseScraper: Core configuration and lifecycle
- PaginationMixin: All pagination strategies
- ExtractionMixin: Content extraction logic
- URLFilteringMixin: Deduplication and filtering
- DriverMixin: Browser and page interaction

Usage:
    from generic_scraper import GenericScraper
    
    scraper = GenericScraper('websites.yaml')
    results = scraper.scrape_website('kurdsat')
    
    # Or scrape specific category
    results = scraper.scrape_category('kurdsat', 'politics')
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import centralized utilities
try:
    from .feature_registry import FeatureRegistry
    from .core.base_scraper import BaseScraper
    from .core.pagination_mixin import PaginationMixin
    from .core.extraction_mixin import ExtractionMixin
    from .core.url_filtering_mixin import URLFilteringMixin
    from .core.driver_mixin import DriverMixin
except ImportError:
    # Fallback for standalone execution
    from feature_registry import FeatureRegistry
    from core.base_scraper import BaseScraper
    from core.pagination_mixin import PaginationMixin
    from core.extraction_mixin import ExtractionMixin
    from core.url_filtering_mixin import URLFilteringMixin
    from core.driver_mixin import DriverMixin

# Get optional features via registry
LanguageDetector = FeatureRegistry.get('language_detector')
ArticleDeduplicator = FeatureRegistry.get('deduplicator')
ScraperMonitor = FeatureRegistry.get('monitor')
ScrapeResult = FeatureRegistry.get('scrape_result')
RateLimiter = FeatureRegistry.get('rate_limiter')
SimpleQC = FeatureRegistry.get('simple_qc')

# Feature availability flags
HAS_ADVANCED = FeatureRegistry.is_available('language_detector')
HAS_MONITOR = FeatureRegistry.is_available('monitor')
HAS_BASE_SCRAPER = FeatureRegistry.is_available('simple_qc')

# Fallback ScrapeResult if not available
if ScrapeResult is None:
    class ScrapeResult:
        def __init__(self, website, success=True, articles_scraped=0, 
                     sentences_extracted=0, duplicates_skipped=0, duration=0, error=None):
            self.website = website
            self.success = success
            self.articles_scraped = articles_scraped
            self.sentences_extracted = sentences_extracted
            self.duplicates_skipped = duplicates_skipped
            self.duration = duration
            self.error = error


logger = logging.getLogger(__name__)


class GenericScraper(ExtractionMixin, PaginationMixin, URLFilteringMixin, DriverMixin, BaseScraper):
    """
    Generic scraper using mixin architecture.
    
    Inheritance chain:
    - BaseScraper: Core configuration loading and lifecycle
    - DriverMixin: Browser driver and page interaction
    - URLFilteringMixin: URL filtering and deduplication
    - PaginationMixin: All pagination strategies
    - ExtractionMixin: Content extraction logic
    
    This provides:
    - Multiple selector types (CSS, XPath)
    - Fallback selector chains
    - All pagination types (url_template, infinite_scroll, click_load_more)
    - Wait strategies (selector-based, manual delays)
    - Per-website and per-category configuration
    - Language detection and filtering
    - Article deduplication
    - FlareSolverr support for Cloudflare bypass
    """
    
    def __init__(self, config_path: str = 'websites.yaml'):
        """
        Initialize generic scraper.
        
        Args:
            config_path: Path to YAML configuration file or directory
        """
        # Initialize base scraper (loads config)
        super().__init__(config_path)
        
        # Initialize name for compatibility
        self.name = "Generic"
        
        # Initialize quality control if available
        self.qc = SimpleQC() if HAS_BASE_SCRAPER and SimpleQC else None
        
        # Initialize advanced features (if available) - will be configured per-website
        self.lang_detector = LanguageDetector() if HAS_ADVANCED and LanguageDetector else None
        self.deduplicator = ArticleDeduplicator() if HAS_ADVANCED and ArticleDeduplicator else None
        self.monitor = ScraperMonitor() if HAS_MONITOR and ScraperMonitor else None
        
        # Website-specific advanced features (initialized per website)
        self.rate_limiter = None
        self.redis_cache = None
        self.retry_handler = None
        self.proxy_rotator = None
        
        # Driver and session state
        self.driver = None
        self.current_website = None
        self.flaresolverr_session = None
        
        # Article link deduplication
        self.scraped_article_links = set()
        self.article_link_db_path = Path('scraped_articles.db')
        
        # Statistics
        self.stats = {
            'articles_processed': 0,
            'sentences_extracted': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }
        
        # URL tracking and filtering
        self.url_debug_mode = False
        self.tracked_urls = []
        self._tracked_url_set = set()
        self.url_whitelist = []
        self._default_blocked_resources = [
            '.css', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', 
            '.ttf', '.eot', '.mp4', '.mp3', '.webm', '.avi', '.mov', '.flv',
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com/tr', 'twitter.com/i/adsct', 'ads', 'analytics', 'tracking'
        ]
        self.blocked_resources = list(self._default_blocked_resources)
        
        # Performance optimizations
        self._selector_cache = {}  # Cache parsed selectors
        self._http_session = None  # Lazy-initialized HTTP session with connection pooling
    
    # ========================================================================
    # Advanced Features Initialization
    # ========================================================================
    
    def _init_advanced_features(self, website_config: Dict):
        """
        Initialize advanced features based on website configuration.
        
        Reads optional feature configs from YAML and initializes them if enabled:
        - rate_limiting: Polite scraping with request rate control
        - caching: Redis-based page/article caching
        - retry: Automatic retry on failures
        - proxy: Proxy rotation for IP blocking bypass
        
        Args:
            website_config: Website configuration dict from YAML
        """
        # 1. Rate Limiting
        rate_config = website_config.get('rate_limiting', {})
        if rate_config.get('enabled', False):
            try:
                if RateLimiter:
                    max_rpm = rate_config.get('max_requests_per_minute', 30)
                    self.rate_limiter = RateLimiter(requests_per_minute=max_rpm)
                    logger.info(f"✅ Rate limiting enabled: {max_rpm} requests/min")
                else:
                    logger.warning("⚠️  Rate limiting configured but RateLimiter not available")
            except Exception as e:
                logger.error(f"❌ Failed to initialize rate limiter: {e}")
                self.rate_limiter = None
        else:
            self.rate_limiter = None
        
        # 2. Redis Caching
        cache_config = website_config.get('caching', {})
        if cache_config.get('enabled', False):
            try:
                # Lazy import - only when caching is enabled
                try:
                    from .advanced_features import RedisCache
                except ImportError:
                    from advanced_features import RedisCache
                
                redis_host = cache_config.get('redis_host', 'localhost')
                redis_port = cache_config.get('redis_port', 6379)
                ttl_hours = cache_config.get('ttl_hours', 24)
                
                self.redis_cache = RedisCache(
                    host=redis_host,
                    port=redis_port,
                    ttl_hours=ttl_hours,
                    prefix=f"{self.current_website}:"
                )
                logger.info(f"✅ Redis caching enabled: {redis_host}:{redis_port} (TTL: {ttl_hours}h)")
            except ImportError:
                logger.warning("⚠️  Redis caching configured but RedisCache not available")
                self.redis_cache = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize Redis cache: {e}")
                logger.info("💡 Continuing without caching (is Redis running?)")
                self.redis_cache = None
        else:
            self.redis_cache = None
        
        # 3. Retry Logic
        retry_config = website_config.get('retry', {})
        if retry_config.get('enabled', False):
            try:
                # Lazy import - only when retry is enabled
                try:
                    from .advanced_features import RetryHandler
                except ImportError:
                    from advanced_features import RetryHandler
                
                max_attempts = retry_config.get('max_attempts', 3)
                delay_seconds = retry_config.get('delay_seconds', 2)
                
                self.retry_handler = RetryHandler(
                    max_attempts=max_attempts,
                    delay_seconds=delay_seconds
                )
                logger.info(f"✅ Retry logic enabled: {max_attempts} attempts, {delay_seconds}s delay")
            except ImportError:
                logger.warning("⚠️  Retry configured but RetryHandler not available")
                self.retry_handler = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize retry handler: {e}")
                self.retry_handler = None
        else:
            self.retry_handler = None
        
        # 4. Proxy Rotation
        proxy_config = website_config.get('proxy', {})
        if proxy_config.get('enabled', False):
            try:
                # Lazy import - only when proxy is enabled
                try:
                    from .advanced_features import ProxyRotator
                except ImportError:
                    from advanced_features import ProxyRotator
                
                proxy_file = proxy_config.get('file', 'proxies.txt')
                strategy = proxy_config.get('strategy', 'round-robin')
                
                self.proxy_rotator = ProxyRotator(
                    proxy_file=proxy_file,
                    rotation_strategy=strategy
                )
                logger.info(f"✅ Proxy rotation enabled: {proxy_file} ({strategy})")
            except ImportError:
                logger.warning("⚠️  Proxy configured but ProxyRotator not available")
                self.proxy_rotator = None
            except FileNotFoundError:
                logger.warning(f"⚠️  Proxy file not found: {proxy_config.get('file')}")
                logger.info("💡 Continuing without proxy rotation")
                self.proxy_rotator = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize proxy rotator: {e}")
                self.proxy_rotator = None
        else:
            self.proxy_rotator = None
    
    # ========================================================================
    # Performance Optimization Methods
    # ========================================================================
    
    def _get_http_session(self):
        """
        Get or create HTTP session with connection pooling.
        
        This provides:
        - Connection pooling (30-50% faster requests)
        - Automatic retries
        - Keep-alive connections
        
        Returns:
            requests.Session configured for performance
        """
        if self._http_session is None:
            # Lazy import - only when needed
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            self._http_session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )
            
            # Configure connection pooling
            adapter = HTTPAdapter(
                pool_connections=10,  # Number of connection pools
                pool_maxsize=20,      # Max connections per pool
                max_retries=retry_strategy
            )
            
            self._http_session.mount('http://', adapter)
            self._http_session.mount('https://', adapter)
        
        return self._http_session
    
    def _get_cached_selector(self, selector_config):
        """
        Get parsed selector from cache or parse and cache it.
        
        Args:
            selector_config: Selector configuration (str, dict, or list)
        
        Returns:
            Cached selector object
        """
        cache_key = str(selector_config)
        if cache_key not in self._selector_cache:
            # Cache miss - this is fine, just store the config as-is
            # The actual parsing happens in _find_element/_find_elements
            self._selector_cache[cache_key] = selector_config
        return self._selector_cache[cache_key]
    
    # ========================================================================
    # High-Level Scraping Methods
    # ========================================================================

    
    def scrape_website(
        self,
        website_name: str,
        categories: Optional[List[str]] = None,
        max_articles: Optional[int] = None
    ) -> ScrapeResult:
        """
        Scrape entire website or specific categories.
        
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
        
        # Initialize website-specific advanced features
        self._init_advanced_features(website_config)
        
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
            
            # Log to monitor if available
            if self.monitor:
                self.monitor.log_scrape(result)
            
            logger.info(f"\n✅ Website scraping complete!")
            logger.info(f"   Articles: {self.stats['articles_processed']}")
            logger.info(f"   Sentences: {len(all_sentences)}")
            logger.info(f"   Duplicates skipped: {self.stats['duplicates_skipped']}")
            logger.info(f"   Duration: {result.duration:.2f}s\n")
            
            # Save tracked URLs if debugging was enabled
            if self.url_debug_mode and self.tracked_urls:
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
            
            if self.monitor:
                self.monitor.log_scrape(result)
            return result
            
        finally:
            self.cleanup()
    
    def scrape_category(
        self,
        website_name: str,
        category_name: str,
        max_articles: Optional[int] = None
    ) -> List[str]:
        """
        Scrape a specific category.
        
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

        # Initialize website-specific advanced features (if not already done)
        if not hasattr(self, '_features_initialized') or self.current_website != website_name:
            self.current_website = website_name
            self._init_advanced_features(website_config)
            self._features_initialized = True

        # Load previously scraped articles for deduplication
        if not hasattr(self, '_scraped_articles_loaded'):
            self.load_scraped_articles()
            self._scraped_articles_loaded = True

        # Enable URL debugging when requested at website level
        if website_config.get('debug_urls', False) and not self.url_debug_mode:
            self.enable_url_debugging()
        
        # Check if category is enabled
        if category_config.get('enabled', True) is False:
            logger.warning(f"Category '{category_name}' is explicitly disabled")
            return []
        
        logger.info(f"\n📂 Scraping Category: {category_name}")
        logger.info(f"   URL: {category_config['url']}")
        
        # Initialize FlareSolverr if enabled for this website
        if not self.flaresolverr_session:
            self._init_flaresolverr(website_config)
        
        # Apply defaults (category overrides website overrides hard-coded)
        merged_config = self._apply_defaults(website_config, category_config)
        
        # Apply rate limiting if enabled
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
            
            # Wait for collection page to load
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
            sentences = self._extract_from_articles_click_through(
                website_config,
                merged_config,
                max_articles=max_articles
            )
        else:
            # Standard extraction: navigate to each article URL
            sentences = self._extract_from_articles(
                article_links,
                website_config,
                merged_config
            )
        
        logger.info(f"   ✅ Extracted {len(sentences)} sentences from {category_name}")
        return sentences


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
    else:
        result = scraper.scrape_website(args.website, max_articles=args.max_articles)
        print(f"\n✅ Scraping complete: {result.articles_scraped} articles, {result.sentences_extracted} sentences")
