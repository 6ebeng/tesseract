# -*- coding: utf-8 -*-
"""
Advanced Features for Web Scrapers

Implements:
- Multi-language support (detection, filtering, per-language selectors)
- Article deduplication (content similarity detection)
- Browser fingerprinting prevention (stealth mode)
- Language-specific text processing
- Rate limiting (prevent server overload and blocking)
- Redis caching (page HTML and extracted articles)
- Retry logic (handle network errors and timeouts)
- Proxy rotation (bypass IP-based blocking)

Usage:
    from advanced_features import (
        LanguageDetector,
        ArticleDeduplicator,
        StealthBrowser,
        MultiLanguageConfig,
        RateLimiter,
        RedisCache,
        RetryHandler,
        ProxyRotator
    )
    
    # Language detection
    detector = LanguageDetector()
    lang = detector.detect('هەواڵی نوێ')  # Returns 'ckb' (Kurdish)
    
    # Deduplication
    dedup = ArticleDeduplicator()
    is_duplicate, reason = dedup.is_duplicate(article_dict, url, title, content)
    
    # Stealth mode
    stealth = StealthBrowser()
    driver = stealth.create_driver()
    
    # Rate limiting
    rate_limiter = RateLimiter(max_requests_per_minute=30)
    rate_limiter.wait_if_needed()  # Enforces rate limit
    
    # Redis caching
    cache = RedisCache(ttl_hours=24)
    html = cache.get_page_html(url)  # Returns cached or None
    cache.set_page_html(url, html)   # Cache for 24 hours
    
    # Retry logic
    retry = RetryHandler(max_attempts=3, delay_seconds=2.0)
    result, success, attempts = retry.execute_with_retry(scrape_function, url)
    
    # Proxy rotation
    proxies = ProxyRotator('proxies.txt', rotation_strategy='round_robin')
    proxy = proxies.get_next_proxy()  # Get next proxy
    selenium_config = proxies.get_selenium_proxy_config(proxy)
    flare_config = proxies.get_flaresolverr_proxy_config(proxy)
"""

import hashlib
import difflib
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import logging
import json
from datetime import datetime
import sqlite3
from collections import Counter
import time
import random
import requests


logger = logging.getLogger(__name__)

# Try to import Redis (optional dependency)
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logger.warning("Redis not installed. Caching feature will be disabled. Install: pip install redis")


# ==================== MULTI-LANGUAGE SUPPORT ====================

class LanguageDetector:
    """
    Detect language of text content
    
    Supports Kurdish (Sorani, Kurmanji), Arabic, English, Persian
    """
    
    # Character ranges for different scripts
    KURDISH_CHARS = set('ئاآبپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهھەیێ')
    ARABIC_CHARS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويى')
    PERSIAN_CHARS = set('پچژکگی')  # Distinct Persian letters
    LATIN_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    # Kurdish-specific letters (Sorani)
    SORANI_SPECIFIC = set('ڕڵەۆێ')
    
    # Kurdish-specific letters (Kurmanji - Latin script)
    KURMANJI_LATIN = set('çêîşûĈÊÎŞÛ')
    
    def detect(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
        
        Returns:
            Language code: 'ckb' (Kurdish Sorani), 'kmr' (Kurdish Kurmanji),
                          'ar' (Arabic), 'fa' (Persian), 'en' (English), 'unknown'
        """
        if not text or len(text.strip()) < 10:
            return 'unknown'
        
        # Count character types
        kurdish_count = sum(1 for c in text if c in self.KURDISH_CHARS)
        arabic_count = sum(1 for c in text if c in self.ARABIC_CHARS)
        persian_count = sum(1 for c in text if c in self.PERSIAN_CHARS)
        latin_count = sum(1 for c in text if c in self.LATIN_CHARS)
        sorani_count = sum(1 for c in text if c in self.SORANI_SPECIFIC)
        kurmanji_count = sum(1 for c in text if c in self.KURMANJI_LATIN)
        
        total_chars = len(text)
        
        # Calculate percentages
        kurdish_pct = kurdish_count / total_chars
        arabic_pct = arabic_count / total_chars
        latin_pct = latin_count / total_chars
        
        # Kurdish Sorani (has specific Kurdish letters)
        if sorani_count > 0 or (kurdish_pct > 0.3 and kurdish_count > arabic_count):
            return 'ckb'
        
        # Kurdish Kurmanji (Latin script with Kurdish letters)
        if kurmanji_count > 0 and latin_pct > 0.5:
            return 'kmr'
        
        # Persian (has Persian-specific letters or high Arabic ratio with Persian markers)
        if persian_count > 0 or (arabic_pct > 0.3 and 'ی' in text):
            return 'fa'
        
        # Arabic (high Arabic character ratio)
        if arabic_pct > 0.3:
            return 'ar'
        
        # English (high Latin ratio)
        if latin_pct > 0.7:
            return 'en'
        
        return 'unknown'
    
    def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """
        Detect language with confidence score
        
        Returns:
            (language_code, confidence_score)
        """
        lang = self.detect(text)
        
        # Calculate confidence based on character frequency
        if not text:
            return ('unknown', 0.0)
        
        # Simple confidence: ratio of language-specific characters
        lang_chars = {
            'ckb': self.KURDISH_CHARS | self.SORANI_SPECIFIC,
            'ar': self.ARABIC_CHARS,
            'en': self.LATIN_CHARS,
            'fa': self.ARABIC_CHARS | self.PERSIAN_CHARS
        }
        
        if lang in lang_chars:
            specific_count = sum(1 for c in text if c in lang_chars[lang])
            confidence = min(1.0, specific_count / len(text) * 2)
        else:
            confidence = 0.5
        
        return (lang, confidence)
    
    def filter_by_language(
        self,
        articles: List[Dict],
        target_languages: List[str]
    ) -> List[Dict]:
        """
        Filter articles by language
        
        Args:
            articles: List of article dictionaries
            target_languages: List of language codes to keep
        
        Returns:
            Filtered articles
        """
        filtered = []
        
        for article in articles:
            text = article.get('content', '') or article.get('title', '')
            lang = self.detect(text)
            
            if lang in target_languages:
                article['detected_language'] = lang
                filtered.append(article)
            else:
                logger.debug(f"Filtered out {article.get('url')}: language={lang}")
        
        return filtered


class MultiLanguageConfig:
    """
    Handle multi-language configuration
    
    Allows per-language selectors and processing rules
    """
    
    def __init__(self, config: Dict):
        """
        Args:
            config: Website configuration with optional language sections
        """
        self.config = config
        self.default_language = config.get('default_language', 'ckb')
    
    def get_selectors(self, language: str) -> Dict:
        """
        Get selectors for specific language
        
        Falls back to default if language-specific not found
        """
        # Check for language-specific selectors
        lang_config = self.config.get('languages', {}).get(language, {})
        lang_selectors = lang_config.get('selectors', {})
        
        # Merge with default selectors
        default_selectors = self.config.get('selectors', {})
        
        return {**default_selectors, **lang_selectors}
    
    def get_enabled_languages(self) -> List[str]:
        """Get list of enabled languages"""
        languages = self.config.get('languages', {})
        return [
            lang for lang, lang_config in languages.items()
            if lang_config.get('enabled', True)
        ]


# ==================== ARTICLE DEDUPLICATION ====================

class ArticleDeduplicator:
    """
    Detect and prevent duplicate articles
    
    Uses multiple strategies:
    - URL exact match
    - Title similarity
    - Content similarity (fuzzy matching)
    """
    
    def __init__(self, db_path: str = 'article_dedup.db'):
        """
        Args:
            db_path: Path to SQLite database for storing article hashes
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize deduplication database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for article fingerprints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                url_hash TEXT PRIMARY KEY,
                url TEXT,
                title_hash TEXT,
                content_hash TEXT,
                title TEXT,
                first_seen TEXT,
                last_seen TEXT,
                seen_count INTEGER DEFAULT 1
            )
        ''')
        
        # Index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_title_hash 
            ON articles(title_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_content_hash 
            ON articles(content_hash)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deduplication database: {self.db_path}")
    
    def is_duplicate(
        self,
        article: Dict,
        url: str,
        title: str,
        content: str,
        title_threshold: float = 0.85,
        content_threshold: float = 0.90
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if article is duplicate
        
        Args:
            article: Article metadata
            url: Article URL
            title: Article title
            content: Article content
            title_threshold: Similarity threshold for title (0-1)
            content_threshold: Similarity threshold for content (0-1)
        
        Returns:
            (is_duplicate, reason)
        """
        # Check URL exact match
        url_hash = self._hash_text(url)
        if self._check_url_exists(url_hash):
            self._update_seen_count(url_hash)
            return (True, 'exact_url_match')
        
        # Check title similarity
        title_hash = self._hash_text(self._normalize_text(title))
        similar_titles = self._find_similar_titles(title_hash, title, title_threshold)
        
        if similar_titles:
            self._update_seen_count(url_hash)
            return (True, f'similar_title (match: {similar_titles[0][1]:.2f})')
        
        # Check content similarity
        content_hash = self._hash_text(self._normalize_text(content[:500]))  # First 500 chars
        similar_content = self._find_similar_content(content_hash, content, content_threshold)
        
        if similar_content:
            self._update_seen_count(url_hash)
            return (True, f'similar_content (match: {similar_content[0][1]:.2f})')
        
        # Not a duplicate - store for future comparison
        self._store_article(url_hash, url, title_hash, content_hash, title)
        
        return (False, None)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Lowercase
        text = text.lower()
        # Remove common punctuation
        text = text.replace('.', '').replace(',', '').replace('!', '').replace('?', '')
        return text
    
    def _hash_text(self, text: str) -> str:
        """Generate hash of text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _check_url_exists(self, url_hash: str) -> bool:
        """Check if URL hash exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM articles WHERE url_hash = ?', (url_hash,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def _find_similar_titles(
        self,
        title_hash: str,
        title: str,
        threshold: float
    ) -> List[Tuple[str, float]]:
        """Find similar titles using fuzzy matching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all titles with same hash prefix (fast pre-filter)
        hash_prefix = title_hash[:8]
        cursor.execute(
            'SELECT url, title FROM articles WHERE title_hash LIKE ?',
            (hash_prefix + '%',)
        )
        
        candidates = cursor.fetchall()
        conn.close()
        
        # Calculate similarity
        normalized_title = self._normalize_text(title)
        similar = []
        
        for url, stored_title in candidates:
            normalized_stored = self._normalize_text(stored_title)
            similarity = difflib.SequenceMatcher(
                None,
                normalized_title,
                normalized_stored
            ).ratio()
            
            if similarity >= threshold:
                similar.append((url, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)
    
    def _find_similar_content(
        self,
        content_hash: str,
        content: str,
        threshold: float
    ) -> List[Tuple[str, float]]:
        """Find similar content using fuzzy matching"""
        # Similar to _find_similar_titles but for content
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        hash_prefix = content_hash[:8]
        cursor.execute(
            'SELECT url FROM articles WHERE content_hash LIKE ?',
            (hash_prefix + '%',)
        )
        
        candidates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # For content, we use a simpler check (exact hash match)
        # Full fuzzy matching would be too slow
        if candidates:
            return [(candidates[0], 1.0)]
        
        return []
    
    def _store_article(
        self,
        url_hash: str,
        url: str,
        title_hash: str,
        content_hash: str,
        title: str
    ):
        """Store article in database"""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO articles 
            (url_hash, url, title_hash, content_hash, title, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (url_hash, url, title_hash, content_hash, title, now, now))
        
        conn.commit()
        conn.close()
    
    def _update_seen_count(self, url_hash: str):
        """Update seen count for duplicate"""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE articles 
            SET seen_count = seen_count + 1, last_seen = ?
            WHERE url_hash = ?
        ''', (now, url_hash))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get deduplication statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total unique articles
        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0]
        
        # Total duplicates detected
        cursor.execute('SELECT SUM(seen_count - 1) FROM articles')
        duplicates = cursor.fetchone()[0] or 0
        
        # Most duplicated
        cursor.execute('''
            SELECT url, title, seen_count 
            FROM articles 
            ORDER BY seen_count DESC 
            LIMIT 5
        ''')
        most_duplicated = [
            {'url': row[0], 'title': row[1], 'count': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'unique_articles': total,
            'duplicates_detected': duplicates,
            'deduplication_rate': f"{duplicates / (total + duplicates) * 100:.1f}%" if total > 0 else "0%",
            'most_duplicated': most_duplicated
        }


# ==================== BROWSER FINGERPRINTING PREVENTION ====================

class StealthBrowser:
    """
    Create stealthy browser instances
    
    Implements anti-detection techniques:
    - User agent randomization
    - WebRTC blocking
    - Canvas fingerprinting prevention
    - Timezone spoofing
    - Language/locale randomization
    """
    
    # Real user agents (keep updated)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    def get_stealth_options(self) -> Dict:
        """
        Get Chrome options for stealth mode
        
        Returns configuration dict (not actual ChromeOptions to avoid selenium import)
        """
        import random
        
        options = {
            'user_agent': random.choice(self.USER_AGENTS),
            'arguments': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ],
            'experimental_options': {
                'excludeSwitches': ['enable-automation'],
                'useAutomationExtension': False,
                'prefs': {
                    'credentials_enable_service': False,
                    'profile.password_manager_enabled': False,
                    'webrtc.ip_handling_policy': 'disable_non_proxied_udp',
                    'webrtc.multiple_routes_enabled': False,
                    'webrtc.nonproxied_udp_enabled': False
                }
            },
            'execute_cdp_cmd': [
                # Override navigator properties
                ('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['en-US', 'en', 'ar', 'ku']
                        });
                    '''
                }),
            ]
        }
        
        return options
    
    def apply_stealth_mode(self, driver):
        """
        Apply stealth settings to existing driver
        
        Args:
            driver: Selenium WebDriver instance
        """
        # Execute stealth JavaScript
        stealth_js = '''
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'ar', 'ku']
            });
            
            // Mock platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Canvas fingerprinting protection
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                if (context) {
                    // Add slight noise to prevent fingerprinting
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                    }
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
        '''
        
        driver.execute_script(stealth_js)
        
        logger.info("✅ Stealth mode applied to browser")


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Rate limiting for web scraping
    
    Prevents overwhelming servers and reduces risk of being blocked.
    Configurable per-website with max requests per minute.
    """
    
    def __init__(self, max_requests_per_minute: int = 30):
        """
        Args:
            max_requests_per_minute: Maximum requests allowed per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.min_delay = 60.0 / max_requests_per_minute if max_requests_per_minute > 0 else 0
        self.request_times = []
        
        logger.info(f"⏱️  Rate limiter initialized: {max_requests_per_minute} req/min (min delay: {self.min_delay:.2f}s)")
    
    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limit
        
        Tracks request times and enforces minimum delay between requests
        """
        if self.max_requests_per_minute <= 0:
            return  # No rate limiting
        
        now = time.time()
        
        # Remove old request times (older than 1 minute)
        cutoff = now - 60
        self.request_times = [t for t in self.request_times if t > cutoff]
        
        # Check if we've hit the limit
        if len(self.request_times) >= self.max_requests_per_minute:
            # Calculate how long to wait
            oldest_request = self.request_times[0]
            wait_until = oldest_request + 60
            wait_time = wait_until - now
            
            if wait_time > 0:
                logger.info(f"⏳ Rate limit reached ({self.max_requests_per_minute} req/min). Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                now = time.time()
        
        # Enforce minimum delay between consecutive requests
        if self.request_times:
            time_since_last = now - self.request_times[-1]
            if time_since_last < self.min_delay:
                delay = self.min_delay - time_since_last
                time.sleep(delay)
                now = time.time()
        
        # Record this request
        self.request_times.append(now)
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        now = time.time()
        cutoff = now - 60
        recent_requests = [t for t in self.request_times if t > cutoff]
        
        return {
            'max_requests_per_minute': self.max_requests_per_minute,
            'min_delay_seconds': self.min_delay,
            'requests_last_minute': len(recent_requests),
            'current_rate': f"{len(recent_requests)}/min",
            'remaining_capacity': max(0, self.max_requests_per_minute - len(recent_requests))
        }


# ==================== CACHING (REDIS) ====================

class RedisCache:
    """
    Redis-based caching for web scraping
    
    Caches both page HTML and extracted articles to reduce redundant scraping.
    Supports configurable TTL (time-to-live) in hours.
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl_hours: int = 24,
        prefix: str = 'scraper:'
    ):
        """
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            ttl_hours: Cache TTL in hours
            prefix: Key prefix for namespacing
        """
        if not HAS_REDIS:
            raise ImportError("Redis not installed. Install: pip install redis")
        
        self.ttl_seconds = ttl_hours * 3600
        self.prefix = prefix
        
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test connection
            self.redis.ping()
            logger.info(f"✅ Redis cache connected: {host}:{port} (TTL: {ttl_hours}h)")
        
        except redis.ConnectionError as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    def _make_key(self, key_type: str, identifier: str) -> str:
        """Generate namespaced cache key"""
        # Hash long URLs/identifiers for consistent key length
        hashed = hashlib.md5(identifier.encode()).hexdigest()
        return f"{self.prefix}{key_type}:{hashed}"
    
    def get_page_html(self, url: str) -> Optional[str]:
        """
        Get cached page HTML
        
        Args:
            url: Page URL
        
        Returns:
            Cached HTML or None if not found/expired
        """
        key = self._make_key('html', url)
        
        try:
            html = self.redis.get(key)
            if html:
                logger.debug(f"✅ Cache HIT (HTML): {url[:50]}...")
                return html
            else:
                logger.debug(f"❌ Cache MISS (HTML): {url[:50]}...")
                return None
        
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set_page_html(self, url: str, html: str):
        """
        Cache page HTML
        
        Args:
            url: Page URL
            html: Page HTML content
        """
        key = self._make_key('html', url)
        
        try:
            self.redis.setex(key, self.ttl_seconds, html)
            logger.debug(f"💾 Cached HTML: {url[:50]}... (TTL: {self.ttl_seconds}s)")
        
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def get_articles(self, category_url: str) -> Optional[List[Dict]]:
        """
        Get cached extracted articles for a category
        
        Args:
            category_url: Category page URL
        
        Returns:
            List of cached articles or None if not found/expired
        """
        key = self._make_key('articles', category_url)
        
        try:
            data = self.redis.get(key)
            if data:
                articles = json.loads(data)
                logger.debug(f"✅ Cache HIT (Articles): {category_url[:50]}... ({len(articles)} articles)")
                return articles
            else:
                logger.debug(f"❌ Cache MISS (Articles): {category_url[:50]}...")
                return None
        
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set_articles(self, category_url: str, articles: List[Dict]):
        """
        Cache extracted articles for a category
        
        Args:
            category_url: Category page URL
            articles: List of extracted articles
        """
        key = self._make_key('articles', category_url)
        
        try:
            data = json.dumps(articles, ensure_ascii=False)
            self.redis.setex(key, self.ttl_seconds, data)
            logger.debug(f"💾 Cached Articles: {category_url[:50]}... ({len(articles)} articles, TTL: {self.ttl_seconds}s)")
        
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def invalidate(self, pattern: str = '*'):
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Key pattern to match (default: all)
        """
        try:
            full_pattern = f"{self.prefix}{pattern}"
            keys = self.redis.keys(full_pattern)
            
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"🗑️  Invalidated {deleted} cache entries: {pattern}")
            else:
                logger.info(f"No cache entries found for pattern: {pattern}")
        
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            # Count keys by type
            html_keys = len(self.redis.keys(f"{self.prefix}html:*"))
            article_keys = len(self.redis.keys(f"{self.prefix}articles:*"))
            total_keys = html_keys + article_keys
            
            # Get Redis info
            info = self.redis.info('memory')
            memory_used = info.get('used_memory_human', 'N/A')
            
            return {
                'total_cached_items': total_keys,
                'cached_html_pages': html_keys,
                'cached_article_sets': article_keys,
                'ttl_hours': self.ttl_seconds / 3600,
                'memory_used': memory_used
            }
        
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {'error': str(e)}


# ==================== RETRY LOGIC ====================

class RetryHandler:
    """
    Retry logic for web scraping
    
    Handles network errors, timeouts, and empty results with configurable
    retry attempts and fixed delays.
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay_seconds: float = 2.0,
        retry_on_empty: bool = True
    ):
        """
        Args:
            max_attempts: Maximum retry attempts (including first try)
            delay_seconds: Fixed delay between retries
            retry_on_empty: Retry if result is empty
        """
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds
        self.retry_on_empty = retry_on_empty
        
        # Track retry statistics
        self.total_attempts = 0
        self.successful_retries = 0
        self.failed_after_retries = 0
        
        logger.info(f"🔁 Retry handler initialized: {max_attempts} attempts, {delay_seconds}s delay")
    
    def execute_with_retry(
        self,
        func,
        *args,
        **kwargs
    ) -> Tuple[Optional[any], bool, int]:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            (result, success, attempts_used)
        """
        last_error = None
        
        for attempt in range(1, self.max_attempts + 1):
            self.total_attempts += 1
            
            try:
                logger.debug(f"Attempt {attempt}/{self.max_attempts}...")
                
                result = func(*args, **kwargs)
                
                # Check if result is empty (if retry_on_empty enabled)
                if self.retry_on_empty and self._is_empty_result(result):
                    logger.warning(f"⚠️  Empty result on attempt {attempt}/{self.max_attempts}")
                    
                    if attempt < self.max_attempts:
                        logger.info(f"⏳ Retrying in {self.delay_seconds}s...")
                        time.sleep(self.delay_seconds)
                        continue
                    else:
                        logger.error(f"❌ All {self.max_attempts} attempts returned empty results")
                        self.failed_after_retries += 1
                        return (result, False, attempt)
                
                # Success!
                if attempt > 1:
                    logger.info(f"✅ Succeeded on attempt {attempt}/{self.max_attempts}")
                    self.successful_retries += 1
                
                return (result, True, attempt)
            
            except (
                # Network errors
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException,
                # Selenium errors
                Exception  # Catch-all for selenium errors (TimeoutException, etc.)
            ) as e:
                last_error = e
                error_type = type(e).__name__
                
                logger.warning(f"⚠️  {error_type} on attempt {attempt}/{self.max_attempts}: {str(e)[:100]}")
                
                if attempt < self.max_attempts:
                    logger.info(f"⏳ Retrying in {self.delay_seconds}s...")
                    time.sleep(self.delay_seconds)
                else:
                    logger.error(f"❌ All {self.max_attempts} attempts failed")
                    self.failed_after_retries += 1
        
        # All attempts failed
        return (None, False, self.max_attempts)
    
    def _is_empty_result(self, result) -> bool:
        """Check if result is considered empty"""
        if result is None:
            return True
        
        if isinstance(result, (list, dict, str)) and len(result) == 0:
            return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Get retry statistics"""
        success_rate = (
            (self.total_attempts - self.failed_after_retries) / self.total_attempts * 100
            if self.total_attempts > 0
            else 0
        )
        
        return {
            'max_attempts': self.max_attempts,
            'delay_seconds': self.delay_seconds,
            'retry_on_empty': self.retry_on_empty,
            'total_attempts': self.total_attempts,
            'successful_retries': self.successful_retries,
            'failed_after_retries': self.failed_after_retries,
            'success_rate': f"{success_rate:.1f}%"
        }


# ==================== PROXY SUPPORT ====================

class ProxyRotator:
    """
    Rotating proxy support for web scraping
    
    Loads proxies from file and rotates through them.
    Works with both direct Selenium and FlareSolverr.
    """
    
    def __init__(
        self,
        proxy_file: str,
        rotation_strategy: str = 'round_robin'
    ):
        """
        Args:
            proxy_file: Path to file with proxy list (one per line)
            rotation_strategy: 'round_robin' or 'random'
        """
        self.proxy_file = Path(proxy_file)
        self.rotation_strategy = rotation_strategy
        self.proxies = []
        self.current_index = 0
        
        # Track proxy usage
        self.proxy_stats = {}
        
        self._load_proxies()
        
        logger.info(f"🔄 Proxy rotator initialized: {len(self.proxies)} proxies ({rotation_strategy})")
    
    def _load_proxies(self):
        """Load proxies from file"""
        if not self.proxy_file.exists():
            raise FileNotFoundError(f"Proxy file not found: {self.proxy_file}")
        
        with open(self.proxy_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse proxy format
                proxy = self._parse_proxy(line)
                if proxy:
                    self.proxies.append(proxy)
                    self.proxy_stats[proxy['url']] = {
                        'uses': 0,
                        'successes': 0,
                        'failures': 0
                    }
        
        if not self.proxies:
            raise ValueError(f"No valid proxies found in {self.proxy_file}")
        
        logger.info(f"📋 Loaded {len(self.proxies)} proxies from {self.proxy_file}")
    
    def _parse_proxy(self, line: str) -> Optional[Dict]:
        """
        Parse proxy string
        
        Formats supported:
        - http://proxy:port
        - http://user:pass@proxy:port
        - socks5://proxy:port
        - proxy:port (assumes http)
        """
        try:
            # Add http:// if no protocol specified
            if '://' not in line:
                line = f'http://{line}'
            
            # Parse URL
            from urllib.parse import urlparse
            parsed = urlparse(line)
            
            proxy_dict = {
                'url': line,
                'protocol': parsed.scheme,
                'host': parsed.hostname,
                'port': parsed.port,
                'username': parsed.username,
                'password': parsed.password
            }
            
            return proxy_dict
        
        except Exception as e:
            logger.warning(f"Invalid proxy format: {line} ({e})")
            return None
    
    def get_next_proxy(self) -> Dict:
        """
        Get next proxy based on rotation strategy
        
        Returns:
            Proxy dict with connection details
        """
        if not self.proxies:
            raise ValueError("No proxies available")
        
        if self.rotation_strategy == 'random':
            proxy = random.choice(self.proxies)
        else:  # round_robin
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Track usage
        self.proxy_stats[proxy['url']]['uses'] += 1
        
        logger.debug(f"🔄 Using proxy: {proxy['host']}:{proxy['port']}")
        
        return proxy
    
    def mark_success(self, proxy: Dict):
        """Mark proxy as successful"""
        self.proxy_stats[proxy['url']]['successes'] += 1
    
    def mark_failure(self, proxy: Dict):
        """Mark proxy as failed"""
        self.proxy_stats[proxy['url']]['failures'] += 1
        
        # Calculate failure rate
        stats = self.proxy_stats[proxy['url']]
        total = stats['successes'] + stats['failures']
        failure_rate = stats['failures'] / total if total > 0 else 0
        
        # Warn if failure rate is high
        if failure_rate > 0.5 and total >= 5:
            logger.warning(f"⚠️  High failure rate for proxy {proxy['host']}:{proxy['port']} ({failure_rate:.1%})")
    
    def get_selenium_proxy_config(self, proxy: Dict) -> Dict:
        """
        Get Selenium proxy configuration
        
        Args:
            proxy: Proxy dict
        
        Returns:
            Dict with Selenium proxy settings
        """
        config = {
            'proxyType': 'MANUAL',
            'httpProxy': f"{proxy['host']}:{proxy['port']}",
            'sslProxy': f"{proxy['host']}:{proxy['port']}",
        }
        
        # Add SOCKS proxy if needed
        if proxy['protocol'] == 'socks5':
            config['socksProxy'] = f"{proxy['host']}:{proxy['port']}"
            config['socksVersion'] = 5
        
        return config
    
    def get_flaresolverr_proxy_config(self, proxy: Dict) -> str:
        """
        Get FlareSolverr proxy configuration
        
        Args:
            proxy: Proxy dict
        
        Returns:
            Proxy URL string for FlareSolverr
        """
        # FlareSolverr expects: protocol://user:pass@host:port
        if proxy['username'] and proxy['password']:
            return f"{proxy['protocol']}://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        else:
            return f"{proxy['protocol']}://{proxy['host']}:{proxy['port']}"
    
    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        total_uses = sum(s['uses'] for s in self.proxy_stats.values())
        total_successes = sum(s['successes'] for s in self.proxy_stats.values())
        total_failures = sum(s['failures'] for s in self.proxy_stats.values())
        
        # Find best/worst proxies
        proxy_performance = []
        for url, stats in self.proxy_stats.items():
            total = stats['successes'] + stats['failures']
            success_rate = stats['successes'] / total if total > 0 else 0
            
            proxy_performance.append({
                'url': url,
                'uses': stats['uses'],
                'success_rate': f"{success_rate:.1%}",
                'successes': stats['successes'],
                'failures': stats['failures']
            })
        
        # Sort by success rate
        proxy_performance.sort(key=lambda x: float(x['success_rate'].rstrip('%')), reverse=True)
        
        return {
            'total_proxies': len(self.proxies),
            'rotation_strategy': self.rotation_strategy,
            'total_uses': total_uses,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'overall_success_rate': f"{total_successes / (total_successes + total_failures) * 100:.1f}%" if (total_successes + total_failures) > 0 else "0%",
            'proxy_performance': proxy_performance
        }


# Example configuration with multi-language support
EXAMPLE_MULTILANG_CONFIG = '''
kurdsat:
  name: "Kurdsat"
  base_url: "https://kurdsat.tv"
  default_language: "ckb"
  
  # Enable language detection and filtering
  language_detection:
    enabled: true
    filter: ["ckb", "ar", "en"]  # Only keep Kurdish, Arabic, English
    
  # Default selectors (used for all languages)
  selectors:
    article_list: "div.post-card"
    article_link: "a"
    article_title: "h1"
    article_content: "div.content"
  
  # Per-language overrides
  languages:
    ckb:  # Kurdish Sorani
      enabled: true
      selectors:
        # Kurdish articles might have different structure
        article_content:
          - "div.ناوەرۆک"  # Kurdish class name
          - "div.content-ku"
          - "div.content"
      processing:
        normalize_digits: true  # Convert Eastern Arabic to Western
    
    ar:  # Arabic
      enabled: true
      selectors:
        article_content:
          - "div.content-ar"
          - "div.content"
    
    en:  # English
      enabled: false  # Don't scrape English articles
'''


if __name__ == '__main__':
    print("🚀 Advanced Features Demo\n")
    
    # Language Detection
    print("1. Language Detection:")
    detector = LanguageDetector()
    
    test_texts = [
        ("هەواڵی نوێ لە کوردستان", "Kurdish Sorani"),
        ("خەبەری تازە", "Kurdish"),
        ("الأخبار الجديدة", "Arabic"),
        ("New breaking news", "English"),
    ]
    
    for text, expected in test_texts:
        lang, confidence = detector.detect_with_confidence(text)
        print(f"   '{text[:20]}...' → {lang} ({confidence:.2f}) [{expected}]")
    
    print()
    
    # Article Deduplication
    print("2. Article Deduplication:")
    dedup = ArticleDeduplicator('test_dedup.db')
    
    # Simulate checking articles
    article1 = {
        'url': 'https://test.com/article1',
        'title': 'Breaking News from Kurdistan',
        'content': 'This is the full content of the article...'
    }
    
    is_dup, reason = dedup.is_duplicate(
        article1,
        article1['url'],
        article1['title'],
        article1['content']
    )
    print(f"   First check: Duplicate={is_dup}")
    
    # Check same article again
    is_dup, reason = dedup.is_duplicate(
        article1,
        article1['url'],
        article1['title'],
        article1['content']
    )
    print(f"   Second check: Duplicate={is_dup}, Reason={reason}")
    
    stats = dedup.get_stats()
    print(f"   Stats: {stats['unique_articles']} unique, {stats['duplicates_detected']} duplicates")
    
    print()
    
    # Stealth Browser
    print("3. Browser Fingerprinting Prevention:")
    stealth = StealthBrowser()
    options = stealth.get_stealth_options()
    print(f"   User Agent: {options['user_agent'][:50]}...")
    print(f"   Arguments: {len(options['arguments'])} stealth flags")
    print(f"   WebRTC: Disabled")
    print(f"   Canvas fingerprinting: Protected")
    
    print()
    
    # Rate Limiting
    print("4. Rate Limiting:")
    rate_limiter = RateLimiter(max_requests_per_minute=30)
    print(f"   Max requests: {rate_limiter.max_requests_per_minute}/min")
    print(f"   Min delay: {rate_limiter.min_delay:.2f}s")
    
    # Simulate requests
    for i in range(3):
        rate_limiter.wait_if_needed()
        print(f"   Request {i+1} sent")
    
    stats = rate_limiter.get_stats()
    print(f"   Current rate: {stats['current_rate']}, Remaining: {stats['remaining_capacity']}")
    
    print()
    
    # Redis Cache (if available)
    print("5. Redis Cache:")
    if HAS_REDIS:
        try:
            cache = RedisCache(ttl_hours=24)
            
            # Test caching
            test_url = 'https://test.com/article'
            test_html = '<html><body>Test content</body></html>'
            
            # Set cache
            cache.set_page_html(test_url, test_html)
            
            # Get cache
            cached = cache.get_page_html(test_url)
            print(f"   Cache test: {'✅ PASS' if cached == test_html else '❌ FAIL'}")
            
            stats = cache.get_stats()
            print(f"   Cached items: {stats['total_cached_items']} (HTML: {stats['cached_html_pages']}, Articles: {stats['cached_article_sets']})")
            print(f"   Memory used: {stats['memory_used']}")
            
            # Cleanup test data
            cache.invalidate('*')
        
        except Exception as e:
            print(f"   ⚠️  Redis not available: {e}")
            print(f"   Install Redis: https://redis.io/docs/getting-started/")
    else:
        print(f"   ⚠️  Redis module not installed")
        print(f"   Install: pip install redis")
    
    print()
    
    # Retry Logic
    print("6. Retry Logic:")
    retry_handler = RetryHandler(max_attempts=3, delay_seconds=1.0)
    
    # Test function that fails twice then succeeds
    class Counter:
        def __init__(self):
            self.count = 0
    
    counter = Counter()
    
    def flaky_function():
        counter.count += 1
        if counter.count < 3:
            raise Exception("Simulated network error")
        return "Success!"
    
    result, success, attempts = retry_handler.execute_with_retry(flaky_function)
    print(f"   Result: {result}")
    print(f"   Success: {success}, Attempts: {attempts}")
    
    stats = retry_handler.get_stats()
    print(f"   Total attempts: {stats['total_attempts']}, Success rate: {stats['success_rate']}")
    
    print()
    
    # Proxy Rotation
    print("7. Proxy Rotation:")
    
    # Create sample proxy file
    sample_proxies = """# Proxy list - one per line
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:3128
socks5://proxy3.example.com:1080
"""
    
    proxy_file = Path('test_proxies.txt')
    proxy_file.write_text(sample_proxies)
    
    try:
        proxy_rotator = ProxyRotator('test_proxies.txt', rotation_strategy='round_robin')
        
        # Get proxies
        for i in range(3):
            proxy = proxy_rotator.get_next_proxy()
            print(f"   Proxy {i+1}: {proxy['protocol']}://{proxy['host']}:{proxy['port']}")
            
            # Simulate success
            proxy_rotator.mark_success(proxy)
        
        stats = proxy_rotator.get_stats()
        print(f"   Total proxies: {stats['total_proxies']}")
        print(f"   Strategy: {stats['rotation_strategy']}")
        print(f"   Total uses: {stats['total_uses']}")
        
        # Cleanup
        proxy_file.unlink()
    
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        if proxy_file.exists():
            proxy_file.unlink()
    
    print()
    print("✅ Demo complete!")

