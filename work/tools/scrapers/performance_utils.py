"""
Performance Optimization Utilities for Web Scrapers

Features:
- Parallel scraping (multiple sites concurrently)
- Incremental scraping (only new articles)
- Caching strategies
- Performance profiling

Usage:
    from performance_utils import (
        ParallelScraper,
        IncrementalScraper,
        ScraperCache,
        performance_profiler
    )
    
    # Parallel scraping
    parallel = ParallelScraper(max_workers=3)
    results = parallel.scrape_all(['kurdsat', 'rudaw', 'nrt'])
    
    # Incremental scraping
    incremental = IncrementalScraper()
    new_articles = incremental.scrape_since_last('kurdsat')
"""

import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps, lru_cache
import logging


logger = logging.getLogger(__name__)


# ==================== PARALLEL SCRAPING ====================

class ParallelScraper:
    """
    Parallel scraping for multiple websites
    
    Scrapes multiple sites concurrently to reduce total time
    """
    
    def __init__(self, max_workers: int = 3):
        """
        Args:
            max_workers: Maximum number of concurrent scrapers
        """
        self.max_workers = max_workers
        logger.info(f"ParallelScraper initialized with {max_workers} workers")
    
    def scrape_all(
        self,
        scraper_registry,
        websites: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Scrape all websites in parallel
        
        Args:
            scraper_registry: ScraperRegistry instance
            websites: List of website names (None = all enabled)
        
        Returns:
            Dictionary mapping website names to results
        """
        if websites is None:
            websites = scraper_registry.get_enabled_websites()
        
        start_time = time.time()
        results = {}
        errors = {}
        
        logger.info(f"Starting parallel scrape of {len(websites)} websites")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_website = {
                executor.submit(self._scrape_website, scraper_registry, website): website
                for website in websites
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_website):
                website = future_to_website[future]
                try:
                    result = future.result()
                    results[website] = result
                    logger.info(f"✅ {website}: {result.get('sentence_count', 0)} sentences")
                except Exception as e:
                    errors[website] = str(e)
                    logger.error(f"❌ {website}: {e}")
        
        elapsed = time.time() - start_time
        
        summary = {
            'results': results,
            'errors': errors,
            'total_websites': len(websites),
            'successful': len(results),
            'failed': len(errors),
            'total_time': elapsed,
            'avg_time_per_site': elapsed / len(websites) if websites else 0
        }
        
        logger.info(
            f"Parallel scrape completed: {len(results)}/{len(websites)} "
            f"successful in {elapsed:.1f}s"
        )
        
        return summary
    
    def _scrape_website(self, registry, website: str) -> Dict[str, Any]:
        """Scrape a single website (called by executor)"""
        scraper = registry.get_scraper(website)
        
        # This would call the actual scraper methods
        # For now, returning mock structure
        result = {
            'website': website,
            'sentence_count': 0,
            'article_count': 0,
            'categories': []
        }
        
        return result


# ==================== INCREMENTAL SCRAPING ====================

class IncrementalScraper:
    """
    Incremental scraping - only scrape new articles
    
    Tracks last scrape time and article URLs to avoid re-scraping
    """
    
    def __init__(self, db_path: str = 'scraper_state.db'):
        """
        Args:
            db_path: Path to SQLite database for state tracking
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for last scrape times
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS last_scrape (
                website TEXT,
                category TEXT,
                last_scrape_time TEXT,
                PRIMARY KEY (website, category)
            )
        ''')
        
        # Table for scraped articles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_articles (
                url_hash TEXT PRIMARY KEY,
                url TEXT,
                website TEXT,
                category TEXT,
                scraped_at TEXT,
                title TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Incremental scraper database: {self.db_path}")
    
    def is_article_new(self, url: str) -> bool:
        """
        Check if article URL has been scraped before
        
        Args:
            url: Article URL
        
        Returns:
            True if new, False if already scraped
        """
        url_hash = self._hash_url(url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT 1 FROM scraped_articles WHERE url_hash = ?',
            (url_hash,)
        )
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return not exists
    
    def mark_article_scraped(
        self,
        url: str,
        website: str,
        category: str,
        title: Optional[str] = None
    ):
        """
        Mark article as scraped
        
        Args:
            url: Article URL
            website: Website name
            category: Category name
            title: Article title (optional)
        """
        url_hash = self._hash_url(url)
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scraped_articles
            (url_hash, url, website, category, scraped_at, title)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (url_hash, url, website, category, now, title))
        
        conn.commit()
        conn.close()
    
    def get_last_scrape_time(self, website: str, category: str) -> Optional[datetime]:
        """
        Get last scrape time for website/category
        
        Returns:
            datetime of last scrape, or None if never scraped
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_scrape_time FROM last_scrape
            WHERE website = ? AND category = ?
        ''', (website, category))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return datetime.fromisoformat(row[0])
        return None
    
    def update_last_scrape_time(self, website: str, category: str):
        """Update last scrape time to now"""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO last_scrape
            (website, category, last_scrape_time)
            VALUES (?, ?, ?)
        ''', (website, category, now))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about scraped articles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total articles
        cursor.execute('SELECT COUNT(*) FROM scraped_articles')
        total_articles = cursor.fetchone()[0]
        
        # Articles by website
        cursor.execute('''
            SELECT website, COUNT(*) as count
            FROM scraped_articles
            GROUP BY website
            ORDER BY count DESC
        ''')
        by_website = dict(cursor.fetchall())
        
        # Articles by category
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM scraped_articles
            GROUP BY category
            ORDER BY count DESC
        ''')
        by_category = dict(cursor.fetchall())
        
        # Recent scrapes
        cursor.execute('''
            SELECT website, category, last_scrape_time
            FROM last_scrape
            ORDER BY last_scrape_time DESC
            LIMIT 10
        ''')
        recent_scrapes = [
            {'website': row[0], 'category': row[1], 'time': row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'by_website': by_website,
            'by_category': by_category,
            'recent_scrapes': recent_scrapes
        }
    
    @staticmethod
    def _hash_url(url: str) -> str:
        """Generate hash of URL for storage"""
        return hashlib.sha256(url.encode()).hexdigest()


# ==================== CACHING ====================

class ScraperCache:
    """
    Cache for scraper data to avoid redundant operations
    
    Uses LRU cache for frequently accessed data
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries
        """
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        
        logger.info(f"Cache initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if expired
        if datetime.now() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        valid_entries = sum(
            1 for _, (_, timestamp) in self.cache.items()
            if now - timestamp <= self.ttl
        )
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache) - valid_entries,
            'utilization': f"{len(self.cache) / self.max_size:.1%}"
        }


# Decorator for caching function results
def cached(ttl_seconds: int = 3600):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl_seconds=1800)
        def expensive_operation(arg):
            ...
    """
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            if key in cache:
                value, timestamp = cache[key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    return value
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache[key] = (result, datetime.now())
            
            return result
        
        return wrapper
    return decorator


# ==================== PERFORMANCE PROFILING ====================

def performance_profiler(func: Callable) -> Callable:
    """
    Decorator to profile function performance
    
    Logs execution time and can detect slow operations
    
    Usage:
        @performance_profiler
        def slow_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            if elapsed > 10:  # Slow operation threshold
                logger.warning(
                    f"⚠️  Slow operation: {func.__name__} took {elapsed:.2f}s"
                )
            else:
                logger.debug(f"⏱️  {func.__name__} completed in {elapsed:.2f}s")
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"❌ {func.__name__} failed after {elapsed:.2f}s: {e}"
            )
            raise
    
    return wrapper


# ==================== BATCH OPERATIONS ====================

class BatchProcessor:
    """Process articles in batches for better performance"""
    
    def __init__(self, batch_size: int = 50):
        """
        Args:
            batch_size: Number of articles per batch
        """
        self.batch_size = batch_size
    
    def process_in_batches(
        self,
        items: List[Any],
        processor: Callable[[List[Any]], None]
    ):
        """
        Process items in batches
        
        Args:
            items: List of items to process
            processor: Function that processes a batch
        """
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        
        logger.info(
            f"Processing {len(items)} items in {total_batches} batches "
            f"(size={self.batch_size})"
        )
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            
            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            processor(batch)


# Example usage
if __name__ == '__main__':
    print("🚀 Performance Utils Demo\n")
    
    # Incremental scraper
    print("1. Incremental Scraper:")
    incremental = IncrementalScraper('test_scraper.db')
    
    # Simulate checking articles
    test_urls = [
        'https://test.com/article1',
        'https://test.com/article2'
    ]
    
    for url in test_urls:
        is_new = incremental.is_article_new(url)
        print(f"   {url}: {'NEW' if is_new else 'SEEN'}")
        
        if is_new:
            incremental.mark_article_scraped(url, 'test', 'politics')
    
    stats = incremental.get_stats()
    print(f"   Total articles tracked: {stats['total_articles']}\n")
    
    # Cache demo
    print("2. Caching:")
    cache = ScraperCache(max_size=100, ttl_seconds=300)
    cache.set('test_key', 'test_value')
    value = cache.get('test_key')
    print(f"   Cached value: {value}")
    print(f"   Cache stats: {cache.get_stats()}\n")
    
    # Performance profiling
    print("3. Performance Profiling:")
    
    @performance_profiler
    def test_slow_function():
        time.sleep(0.1)
        return "done"
    
    result = test_slow_function()
    print(f"   Result: {result}")
