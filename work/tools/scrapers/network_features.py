"""
Network Advanced Features for Web Scrapers

Implements:
- HTTP Session Management with connection pooling
- Response Caching (disk and memory)
- Automatic Retry with exponential backoff
- Proxy Support (rotation, health checking)
- Request/Response compression
- Connection pooling and keep-alive

Usage:
    from network_features import (
        SessionManager,
        ResponseCache,
        RetryHandler,
        ProxyManager
    )
    
    # Session with all features
    session_mgr = SessionManager(
        use_cache=True,
        use_retry=True,
        use_proxy=True
    )
    
    response = session_mgr.get('https://example.com')
    
    # Individual components
    cache = ResponseCache(cache_dir='cache/')
    retry = RetryHandler(max_retries=3, backoff_factor=2)
    proxy_mgr = ProxyManager(proxies=['http://proxy1:8080'])
"""

import requests
import time
import hashlib
import json
import pickle
import fnmatch
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
import logging
from urllib.parse import urlparse
import random


logger = logging.getLogger(__name__)


# ==================== URL FILTERING (WHITELIST/BLACKLIST) ====================

class URLFilter:
    """
    URL filtering with whitelist/blacklist and wildcard support
    
    Features:
    - Whitelist: Only allow matching URLs
    - Blacklist: Block matching URLs
    - Wildcard patterns: *, ?, [abc], etc.
    - Domain matching: *.example.com
    - Path matching: /api/*/data
    - Query parameter matching
    
    Usage:
        # Allow only specific domains
        filter = URLFilter(
            whitelist=['*.kurdsat.tv', '*.nrt.tv']
        )
        
        # Block specific paths
        filter = URLFilter(
            blacklist=['*/admin/*', '*/private/*']
        )
        
        # Combined
        filter = URLFilter(
            whitelist=['*.kurdsat.tv'],
            blacklist=['*/ads/*', '*/tracking/*']
        )
    """
    
    def __init__(
        self,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
        case_sensitive: bool = False
    ):
        """
        Args:
            whitelist: List of URL patterns to allow (if empty, allow all)
            blacklist: List of URL patterns to block (checked after whitelist)
            case_sensitive: Whether pattern matching is case-sensitive
        """
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []
        self.case_sensitive = case_sensitive
        
        # Statistics
        self.stats = {
            'total_checked': 0,
            'whitelist_passed': 0,
            'whitelist_blocked': 0,
            'blacklist_blocked': 0,
            'allowed': 0
        }
        
        logger.info(
            f"URLFilter initialized: "
            f"whitelist={len(self.whitelist)}, blacklist={len(self.blacklist)}"
        )
    
    def is_allowed(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL is allowed
        
        Args:
            url: URL to check
        
        Returns:
            (is_allowed, reason)
        
        Rules:
            1. If whitelist exists and URL doesn't match: BLOCKED
            2. If URL matches blacklist: BLOCKED
            3. Otherwise: ALLOWED
        """
        self.stats['total_checked'] += 1
        
        # Normalize URL for matching
        check_url = url if self.case_sensitive else url.lower()
        
        # Check whitelist (if exists)
        if self.whitelist:
            matched = False
            for pattern in self.whitelist:
                check_pattern = pattern if self.case_sensitive else pattern.lower()
                if self._match_pattern(check_url, check_pattern):
                    matched = True
                    self.stats['whitelist_passed'] += 1
                    break
            
            if not matched:
                self.stats['whitelist_blocked'] += 1
                return (False, 'not_in_whitelist')
        
        # Check blacklist
        for pattern in self.blacklist:
            check_pattern = pattern if self.case_sensitive else pattern.lower()
            if self._match_pattern(check_url, check_pattern):
                self.stats['blacklist_blocked'] += 1
                return (False, f'blacklist_match: {pattern}')
        
        # Allowed
        self.stats['allowed'] += 1
        return (True, 'allowed')
    
    def _match_pattern(self, url: str, pattern: str) -> bool:
        """
        Match URL against pattern with wildcard support
        
        Patterns:
            - * matches any characters
            - ? matches single character
            - [abc] matches any character in brackets
            - *.domain.com matches subdomains
            - /path/* matches path prefix
        
        Examples:
            - '*.kurdsat.tv' matches 'https://www.kurdsat.tv/news'
            - '*/api/*' matches 'https://example.com/api/data'
            - 'https://example.com/page?' matches 'page1', 'page2', etc.
        """
        # Handle domain-only patterns (*.example.com)
        if pattern.startswith('*.'):
            domain = pattern[2:]  # Remove *.
            parsed = urlparse(url)
            return parsed.netloc.endswith(domain)
        
        # Handle full URL patterns with wildcards
        # Use fnmatch for glob-style matching
        if fnmatch.fnmatch(url, pattern):
            return True
        
        # Try matching just the path
        parsed = urlparse(url)
        path_pattern = pattern.lstrip('*')
        if fnmatch.fnmatch(parsed.path, path_pattern):
            return True
        
        # Try matching domain + path
        domain_path = f"{parsed.netloc}{parsed.path}"
        if fnmatch.fnmatch(domain_path, pattern.lstrip('*/')):
            return True
        
        return False
    
    def add_whitelist(self, pattern: str):
        """Add pattern to whitelist"""
        if pattern not in self.whitelist:
            self.whitelist.append(pattern)
            logger.info(f"Added to whitelist: {pattern}")
    
    def add_blacklist(self, pattern: str):
        """Add pattern to blacklist"""
        if pattern not in self.blacklist:
            self.blacklist.append(pattern)
            logger.info(f"Added to blacklist: {pattern}")
    
    def remove_whitelist(self, pattern: str):
        """Remove pattern from whitelist"""
        if pattern in self.whitelist:
            self.whitelist.remove(pattern)
            logger.info(f"Removed from whitelist: {pattern}")
    
    def remove_blacklist(self, pattern: str):
        """Remove pattern from blacklist"""
        if pattern in self.blacklist:
            self.blacklist.remove(pattern)
            logger.info(f"Removed from blacklist: {pattern}")
    
    def clear_whitelist(self):
        """Clear whitelist"""
        self.whitelist.clear()
        logger.info("Whitelist cleared")
    
    def clear_blacklist(self):
        """Clear blacklist"""
        self.blacklist.clear()
        logger.info("Blacklist cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get filter statistics"""
        stats = self.stats.copy()
        
        if stats['total_checked'] > 0:
            stats['whitelist_pass_rate'] = (
                f"{stats['whitelist_passed'] / stats['total_checked'] * 100:.1f}%"
            )
            stats['blacklist_block_rate'] = (
                f"{stats['blacklist_blocked'] / stats['total_checked'] * 100:.1f}%"
            )
            stats['allow_rate'] = (
                f"{stats['allowed'] / stats['total_checked'] * 100:.1f}%"
            )
        
        return stats


# ==================== HTTP SESSION MANAGEMENT ====================

class SessionManager:
    """
    Advanced HTTP session with connection pooling, caching, retry, and proxy support
    
    Features:
    - Connection pooling for better performance
    - Request/response compression
    - Custom headers and user agents
    - Timeout management
    - Integration with cache, retry, and proxy managers
    """
    
    def __init__(
        self,
        use_cache: bool = True,
        use_retry: bool = True,
        use_proxy: bool = False,
        cache_dir: str = 'cache/',
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 30,
        max_pool_connections: int = 10,
        max_pool_size: int = 20,
        proxies: Optional[List[str]] = None,
        url_whitelist: Optional[List[str]] = None,
        url_blacklist: Optional[List[str]] = None
    ):
        """
        Args:
            use_cache: Enable response caching
            use_retry: Enable automatic retry
            use_proxy: Enable proxy rotation
            cache_dir: Directory for cache storage
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff multiplier
            timeout: Request timeout in seconds
            max_pool_connections: Max connections per host
            max_pool_size: Max total connections in pool
            proxies: List of proxy URLs
            url_whitelist: URL patterns to allow (if set, only these are allowed)
            url_blacklist: URL patterns to block
        """
        # Create base session
        self.session = requests.Session()
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max_pool_connections,
            pool_maxsize=max_pool_size,
            max_retries=0  # We handle retries ourselves
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set default headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,ku;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Initialize components
        self.cache = ResponseCache(cache_dir=cache_dir) if use_cache else None
        self.retry_handler = RetryHandler(max_retries=max_retries, backoff_factor=backoff_factor) if use_retry else None
        self.proxy_manager = ProxyManager(proxies=proxies) if use_proxy and proxies else None
        self.url_filter = URLFilter(whitelist=url_whitelist, blacklist=url_blacklist) if (url_whitelist or url_blacklist) else None
        
        self.timeout = timeout
        self.use_cache = use_cache
        self.use_retry = use_retry
        self.use_proxy = use_proxy
        
        # Statistics
        self.stats = {
            'requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'retries': 0,
            'failures': 0,
            'proxy_switches': 0,
            'url_filtered': 0
        }
        
        logger.info(
            f"SessionManager initialized: "
            f"cache={use_cache}, retry={use_retry}, proxy={use_proxy}"
        )
    
    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        bypass_cache: bool = False,
        **kwargs
    ) -> requests.Response:
        """
        GET request with caching, retry, and proxy support
        
        Args:
            url: URL to fetch
            params: Query parameters
            headers: Additional headers
            bypass_cache: Skip cache lookup
            **kwargs: Additional requests.get arguments
        
        Returns:
            Response object
        
        Raises:
            requests.RequestException: If all retries fail
            ValueError: If URL is blocked by filter
        """
        self.stats['requests'] += 1
        
        # Check URL filter
        if self.url_filter:
            is_allowed, reason = self.url_filter.is_allowed(url)
            if not is_allowed:
                self.stats['url_filtered'] += 1
                raise ValueError(f"URL blocked by filter: {url} (reason: {reason})")
        
        # Check cache first
        if self.use_cache and not bypass_cache:
            cached = self.cache.get(url, params)
            if cached:
                self.stats['cache_hits'] += 1
                logger.debug(f"💾 Cache HIT: {url}")
                return cached
            else:
                self.stats['cache_misses'] += 1
        
        # Merge headers
        req_headers = self.session.headers.copy()
        if headers:
            req_headers.update(headers)
        
        # Set timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Retry loop
        last_exception = None
        
        for attempt in range((self.retry_handler.max_retries if self.retry_handler else 1) + 1):
            try:
                # Get proxy if enabled
                proxy_dict = None
                if self.use_proxy and self.proxy_manager:
                    proxy = self.proxy_manager.get_proxy()
                    if proxy:
                        proxy_dict = {'http': proxy, 'https': proxy}
                
                # Make request
                response = self.session.get(
                    url,
                    params=params,
                    headers=req_headers,
                    proxies=proxy_dict,
                    **kwargs
                )
                
                # Check response
                response.raise_for_status()
                
                # Cache successful response
                if self.use_cache and response.status_code == 200:
                    self.cache.set(url, params, response)
                
                # Mark proxy as working
                if self.use_proxy and self.proxy_manager and proxy:
                    self.proxy_manager.mark_success(proxy)
                
                return response
                
            except requests.RequestException as e:
                last_exception = e
                
                # Mark proxy as failed
                if self.use_proxy and self.proxy_manager and proxy_dict:
                    self.proxy_manager.mark_failure(list(proxy_dict.values())[0])
                    self.stats['proxy_switches'] += 1
                
                # Check if we should retry
                if self.retry_handler and attempt < self.retry_handler.max_retries:
                    wait_time = self.retry_handler.get_wait_time(attempt)
                    logger.warning(
                        f"⚠️  Request failed (attempt {attempt + 1}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                    self.stats['retries'] += 1
                else:
                    # Out of retries
                    self.stats['failures'] += 1
                    logger.error(f"❌ Request failed after {attempt + 1} attempts: {url}")
                    raise
        
        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise requests.RequestException("Request failed with unknown error")
    
    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        POST request with retry and proxy support
        
        Note: POST requests are not cached by default
        
        Raises:
            ValueError: If URL is blocked by filter
        """
        self.stats['requests'] += 1
        
        # Check URL filter
        if self.url_filter:
            is_allowed, reason = self.url_filter.is_allowed(url)
            if not is_allowed:
                self.stats['url_filtered'] += 1
                raise ValueError(f"URL blocked by filter: {url} (reason: {reason})")
        
        # Merge headers
        req_headers = self.session.headers.copy()
        if headers:
            req_headers.update(headers)
        
        # Set timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        # Retry loop
        last_exception = None
        
        for attempt in range((self.retry_handler.max_retries if self.retry_handler else 1) + 1):
            try:
                # Get proxy if enabled
                proxy_dict = None
                if self.use_proxy and self.proxy_manager:
                    proxy = self.proxy_manager.get_proxy()
                    if proxy:
                        proxy_dict = {'http': proxy, 'https': proxy}
                
                # Make request
                response = self.session.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=req_headers,
                    proxies=proxy_dict,
                    **kwargs
                )
                
                response.raise_for_status()
                
                # Mark proxy as working
                if self.use_proxy and self.proxy_manager and proxy:
                    self.proxy_manager.mark_success(proxy)
                
                return response
                
            except requests.RequestException as e:
                last_exception = e
                
                # Mark proxy as failed
                if self.use_proxy and self.proxy_manager and proxy_dict:
                    self.proxy_manager.mark_failure(list(proxy_dict.values())[0])
                    self.stats['proxy_switches'] += 1
                
                # Check if we should retry
                if self.retry_handler and attempt < self.retry_handler.max_retries:
                    wait_time = self.retry_handler.get_wait_time(attempt)
                    logger.warning(
                        f"⚠️  POST request failed (attempt {attempt + 1}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                    self.stats['retries'] += 1
                else:
                    self.stats['failures'] += 1
                    raise
        
        if last_exception:
            raise last_exception
        raise requests.RequestException("POST request failed with unknown error")
    
    def set_user_agent(self, user_agent: str):
        """Set custom user agent"""
        self.session.headers['User-Agent'] = user_agent
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        stats = self.stats.copy()
        
        # Add cache stats
        if self.cache:
            cache_stats = self.cache.get_stats()
            stats['cache_size'] = cache_stats['total_entries']
            stats['cache_size_mb'] = cache_stats['total_size_mb']
            stats['cache_hit_rate'] = (
                f"{self.stats['cache_hits'] / max(1, self.stats['requests']) * 100:.1f}%"
            )
        
        # Add proxy stats
        if self.proxy_manager:
            proxy_stats = self.proxy_manager.get_stats()
            stats['available_proxies'] = proxy_stats['healthy_proxies']
            stats['total_proxies'] = proxy_stats['total_proxies']
        
        # Add URL filter stats
        if self.url_filter:
            filter_stats = self.url_filter.get_stats()
            stats['url_filter'] = filter_stats
        
        return stats
    
    def close(self):
        """Close session and cleanup"""
        self.session.close()
        logger.info(f"Session closed. Stats: {self.get_stats()}")


# ==================== RESPONSE CACHING ====================

class ResponseCache:
    """
    HTTP response cache with disk and memory storage
    
    Features:
    - Memory cache (LRU) for hot data
    - Disk cache for persistence
    - TTL-based expiration
    - Automatic cleanup of old entries
    """
    
    def __init__(
        self,
        cache_dir: str = 'cache/',
        ttl_seconds: int = 3600,  # 1 hour
        max_memory_items: int = 100,
        max_disk_size_mb: int = 500
    ):
        """
        Args:
            cache_dir: Directory for disk cache
            ttl_seconds: Time-to-live for cache entries
            max_memory_items: Maximum items in memory cache
            max_disk_size_mb: Maximum disk cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_memory_items = max_memory_items
        self.max_disk_size_mb = max_disk_size_mb
        
        # Memory cache (LRU)
        self.memory_cache: Dict[str, Tuple[datetime, requests.Response]] = {}
        self.access_order: deque = deque(maxlen=max_memory_items)
        
        logger.info(f"ResponseCache initialized: {cache_dir} (TTL={ttl_seconds}s)")
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from URL and parameters"""
        if params:
            # Sort params for consistent hashing
            param_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
            key_str = f"{url}?{param_str}"
        else:
            key_str = url
        
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get filesystem path for cache key"""
        # Use first 2 chars as subdirectory for better performance
        subdir = cache_key[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(exist_ok=True)
        
        return cache_subdir / f"{cache_key}.pkl"
    
    def get(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Get cached response
        
        Returns:
            Response object or None if not cached/expired
        """
        cache_key = self._get_cache_key(url, params)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_time, response = self.memory_cache[cache_key]
            
            # Check if expired
            if datetime.now() - cached_time < self.ttl:
                # Update access order
                if cache_key in self.access_order:
                    self.access_order.remove(cache_key)
                self.access_order.append(cache_key)
                
                logger.debug(f"Memory cache hit: {url[:50]}")
                return response
            else:
                # Expired - remove from memory
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                
                cached_time = cached_data['timestamp']
                
                # Check if expired
                if datetime.now() - cached_time < self.ttl:
                    # Reconstruct response object
                    response = self._reconstruct_response(cached_data)
                    
                    # Add to memory cache
                    self._add_to_memory(cache_key, response)
                    
                    logger.debug(f"Disk cache hit: {url[:50]}")
                    return response
                else:
                    # Expired - delete file
                    cache_path.unlink()
                    logger.debug(f"Cache expired: {url[:50]}")
            
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")
                # Delete corrupted cache file
                cache_path.unlink(missing_ok=True)
        
        return None
    
    def set(self, url: str, params: Optional[Dict], response: requests.Response):
        """Cache response"""
        cache_key = self._get_cache_key(url, params)
        
        # Add to memory cache
        self._add_to_memory(cache_key, response)
        
        # Save to disk
        try:
            cache_data = {
                'timestamp': datetime.now(),
                'url': url,
                'params': params,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.content,
                'encoding': response.encoding
            }
            
            cache_path = self._get_cache_path(cache_key)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug(f"Cached: {url[:50]}")
            
            # Check disk size and cleanup if needed
            self._cleanup_if_needed()
            
        except Exception as e:
            logger.warning(f"Error caching response: {e}")
    
    def _add_to_memory(self, cache_key: str, response: requests.Response):
        """Add response to memory cache with LRU eviction"""
        # Add to cache
        self.memory_cache[cache_key] = (datetime.now(), response)
        
        # Update access order
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
        
        # Evict oldest if over limit
        if len(self.memory_cache) > self.max_memory_items:
            oldest_key = self.access_order.popleft()
            if oldest_key in self.memory_cache:
                del self.memory_cache[oldest_key]
    
    def _reconstruct_response(self, cached_data: Dict) -> requests.Response:
        """Reconstruct Response object from cached data"""
        response = requests.Response()
        response.status_code = cached_data['status_code']
        response.headers = requests.structures.CaseInsensitiveDict(cached_data['headers'])
        response._content = cached_data['content']
        response.encoding = cached_data['encoding']
        response.url = cached_data['url']
        
        return response
    
    def _cleanup_if_needed(self):
        """Remove old cache files if size limit exceeded"""
        total_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*.pkl'))
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb > self.max_disk_size_mb:
            logger.info(f"Cache size ({total_size_mb:.1f}MB) exceeds limit, cleaning up...")
            
            # Get all cache files with timestamps
            cache_files = [
                (f, f.stat().st_mtime)
                for f in self.cache_dir.rglob('*.pkl')
            ]
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[1])
            
            # Delete oldest files until under limit
            for cache_file, _ in cache_files:
                cache_file.unlink()
                
                # Recalculate size
                total_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*.pkl'))
                total_size_mb = total_size / (1024 * 1024)
                
                if total_size_mb <= self.max_disk_size_mb * 0.8:  # Leave 20% headroom
                    break
            
            logger.info(f"Cache cleanup complete. New size: {total_size_mb:.1f}MB")
    
    def clear(self):
        """Clear all cached data"""
        # Clear memory cache
        self.memory_cache.clear()
        self.access_order.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.rglob('*.pkl'):
            cache_file.unlink()
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        disk_files = list(self.cache_dir.rglob('*.pkl'))
        total_size = sum(f.stat().st_size for f in disk_files)
        
        return {
            'memory_entries': len(self.memory_cache),
            'disk_entries': len(disk_files),
            'total_entries': len(self.memory_cache) + len(disk_files),
            'total_size_mb': total_size / (1024 * 1024),
            'ttl_seconds': self.ttl.total_seconds()
        }


# ==================== RETRY HANDLER ====================

class RetryHandler:
    """
    Automatic retry with exponential backoff
    
    Features:
    - Exponential backoff with jitter
    - Configurable retry conditions
    - Per-error-type retry limits
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        max_backoff: float = 60.0,
        jitter: bool = True,
        retry_on_status: Optional[List[int]] = None
    ):
        """
        Args:
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff multiplier
            max_backoff: Maximum backoff time in seconds
            jitter: Add random jitter to backoff
            retry_on_status: HTTP status codes to retry on
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.jitter = jitter
        
        # Default: retry on server errors and rate limits
        self.retry_on_status = retry_on_status or [
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504   # Gateway Timeout
        ]
        
        logger.info(
            f"RetryHandler initialized: max={max_retries}, "
            f"backoff={backoff_factor}, jitter={jitter}"
        )
    
    def get_wait_time(self, attempt: int) -> float:
        """
        Calculate wait time for retry attempt
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Wait time in seconds
        """
        # Exponential backoff: backoff_factor ^ attempt
        wait = self.backoff_factor ** attempt
        
        # Cap at max_backoff
        wait = min(wait, self.max_backoff)
        
        # Add jitter to avoid thundering herd
        if self.jitter:
            wait = wait * (0.5 + random.random())  # Random factor between 0.5 and 1.5
        
        return wait
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if request should be retried
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number
        
        Returns:
            True if should retry
        """
        if attempt >= self.max_retries:
            return False
        
        # Check if it's a requests exception
        if isinstance(exception, requests.RequestException):
            # Check response status if available
            if hasattr(exception, 'response') and exception.response is not None:
                if exception.response.status_code in self.retry_on_status:
                    return True
            
            # Retry on connection errors
            if isinstance(exception, (
                requests.ConnectionError,
                requests.Timeout,
                requests.ConnectTimeout,
                requests.ReadTimeout
            )):
                return True
        
        return False


# ==================== PROXY MANAGER ====================

class ProxyManager:
    """
    Proxy rotation and health checking
    
    Features:
    - Automatic proxy rotation
    - Health checking and failure tracking
    - Proxy blacklisting
    - Support for HTTP/HTTPS/SOCKS proxies
    """
    
    def __init__(
        self,
        proxies: List[str],
        health_check_url: str = 'http://httpbin.org/ip',
        health_check_interval: int = 300,  # 5 minutes
        max_failures: int = 3,
        blacklist_duration: int = 600  # 10 minutes
    ):
        """
        Args:
            proxies: List of proxy URLs (e.g., ['http://proxy1:8080', 'socks5://proxy2:1080'])
            health_check_url: URL to test proxy health
            health_check_interval: Seconds between health checks
            max_failures: Maximum failures before blacklisting
            blacklist_duration: Seconds to blacklist failed proxy
        """
        self.proxies = proxies
        self.health_check_url = health_check_url
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self.blacklist_duration = blacklist_duration
        
        # Proxy state tracking
        self.proxy_stats: Dict[str, Dict[str, Any]] = {}
        self.blacklist: Dict[str, datetime] = {}
        self.current_index = 0
        self.last_health_check = datetime.min
        
        # Initialize stats
        for proxy in proxies:
            self.proxy_stats[proxy] = {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'consecutive_failures': 0,
                'last_success': None,
                'last_failure': None,
                'avg_response_time': 0.0
            }
        
        logger.info(f"ProxyManager initialized with {len(proxies)} proxies")
        
        # Run initial health check
        self._health_check()
    
    def get_proxy(self) -> Optional[str]:
        """
        Get next healthy proxy
        
        Returns:
            Proxy URL or None if no healthy proxies available
        """
        # Periodic health check
        if datetime.now() - self.last_health_check > timedelta(seconds=self.health_check_interval):
            self._health_check()
        
        # Clean expired blacklist entries
        self._clean_blacklist()
        
        # Get list of available proxies (not blacklisted)
        available = [
            p for p in self.proxies
            if p not in self.blacklist
        ]
        
        if not available:
            logger.warning("⚠️  No healthy proxies available!")
            return None
        
        # Round-robin selection
        proxy = available[self.current_index % len(available)]
        self.current_index += 1
        
        self.proxy_stats[proxy]['requests'] += 1
        
        return proxy
    
    def mark_success(self, proxy: str):
        """Mark proxy request as successful"""
        if proxy not in self.proxy_stats:
            return
        
        stats = self.proxy_stats[proxy]
        stats['successes'] += 1
        stats['consecutive_failures'] = 0
        stats['last_success'] = datetime.now()
        
        # Remove from blacklist if present
        if proxy in self.blacklist:
            del self.blacklist[proxy]
            logger.info(f"✅ Proxy recovered: {proxy}")
    
    def mark_failure(self, proxy: str):
        """Mark proxy request as failed"""
        if proxy not in self.proxy_stats:
            return
        
        stats = self.proxy_stats[proxy]
        stats['failures'] += 1
        stats['consecutive_failures'] += 1
        stats['last_failure'] = datetime.now()
        
        # Blacklist if too many consecutive failures
        if stats['consecutive_failures'] >= self.max_failures:
            self.blacklist[proxy] = datetime.now()
            logger.warning(
                f"⚠️  Proxy blacklisted ({stats['consecutive_failures']} failures): {proxy}"
            )
    
    def _clean_blacklist(self):
        """Remove expired blacklist entries"""
        now = datetime.now()
        expired = [
            proxy for proxy, blacklist_time in self.blacklist.items()
            if (now - blacklist_time).total_seconds() > self.blacklist_duration
        ]
        
        for proxy in expired:
            del self.blacklist[proxy]
            logger.info(f"✅ Proxy blacklist expired: {proxy}")
    
    def _health_check(self):
        """Check health of all proxies"""
        logger.info("🔍 Running proxy health check...")
        
        healthy = 0
        
        for proxy in self.proxies:
            if proxy in self.blacklist:
                continue
            
            try:
                start = time.time()
                response = requests.get(
                    self.health_check_url,
                    proxies={'http': proxy, 'https': proxy},
                    timeout=10
                )
                response_time = time.time() - start
                
                if response.status_code == 200:
                    self.mark_success(proxy)
                    
                    # Update average response time
                    stats = self.proxy_stats[proxy]
                    if stats['avg_response_time'] == 0:
                        stats['avg_response_time'] = response_time
                    else:
                        # Exponential moving average
                        stats['avg_response_time'] = (
                            0.7 * stats['avg_response_time'] + 0.3 * response_time
                        )
                    
                    healthy += 1
                    logger.debug(f"  ✅ {proxy} - {response_time:.2f}s")
                else:
                    self.mark_failure(proxy)
            
            except Exception as e:
                self.mark_failure(proxy)
                logger.debug(f"  ❌ {proxy} - {e}")
        
        self.last_health_check = datetime.now()
        logger.info(f"Health check complete: {healthy}/{len(self.proxies)} proxies healthy")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy manager statistics"""
        healthy = len([p for p in self.proxies if p not in self.blacklist])
        
        return {
            'total_proxies': len(self.proxies),
            'healthy_proxies': healthy,
            'blacklisted_proxies': len(self.blacklist),
            'proxy_details': [
                {
                    'proxy': proxy,
                    'requests': stats['requests'],
                    'success_rate': (
                        f"{stats['successes'] / max(1, stats['requests']) * 100:.1f}%"
                    ),
                    'avg_response_time': f"{stats['avg_response_time']:.2f}s",
                    'blacklisted': proxy in self.blacklist
                }
                for proxy, stats in self.proxy_stats.items()
            ]
        }


# ==================== EXAMPLE USAGE ====================

if __name__ == '__main__':
    import sys
    
    print("🚀 Network Advanced Features Demo\n")
    
    # 0. URL Filter Demo
    print("0. URL Filter (Whitelist/Blacklist):")
    url_filter = URLFilter(
        whitelist=['*.kurdsat.tv', '*.nrt.tv'],
        blacklist=['*/ads/*', '*/tracking/*']
    )
    
    test_urls = [
        'https://www.kurdsat.tv/news/politics',  # Should pass
        'https://nrt.tv/breaking-news',           # Should pass
        'https://example.com/article',            # Blocked (not in whitelist)
        'https://kurdsat.tv/ads/banner',          # Blocked (blacklist)
    ]
    
    for url in test_urls:
        allowed, reason = url_filter.is_allowed(url)
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"   {status}: {url}")
        if not allowed:
            print(f"            Reason: {reason}")
    
    filter_stats = url_filter.get_stats()
    print(f"\n   Filter stats: {filter_stats['allowed']} allowed, "
          f"{filter_stats['whitelist_blocked'] + filter_stats['blacklist_blocked']} blocked\n")
    
    # 1. Basic Session Manager
    print("1. Session Manager (no cache/retry/proxy):")
    session = SessionManager(use_cache=False, use_retry=False, use_proxy=False)
    
    try:
        response = session.get('https://httpbin.org/get')
        print(f"   ✅ GET successful: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GET failed: {e}")
    
    print(f"   Stats: {session.get_stats()}\n")
    session.close()
    
    # 2. Session with Caching
    print("2. Session Manager with Caching:")
    session = SessionManager(use_cache=True, cache_dir='test_cache/')
    
    # First request (cache miss)
    response1 = session.get('https://httpbin.org/uuid')
    print(f"   First request: {response1.status_code}")
    
    # Second request (cache hit)
    response2 = session.get('https://httpbin.org/uuid')
    print(f"   Second request: {response2.status_code} (should be cached)")
    
    stats = session.get_stats()
    print(f"   Cache hits: {stats['cache_hits']}, misses: {stats['cache_misses']}")
    print(f"   Hit rate: {stats['cache_hit_rate']}\n")
    session.close()
    
    # 3. Retry Handler
    print("3. Retry Handler:")
    retry = RetryHandler(max_retries=3, backoff_factor=2.0)
    
    for attempt in range(4):
        wait = retry.get_wait_time(attempt)
        print(f"   Attempt {attempt}: wait {wait:.2f}s")
    
    print()
    
    # 4. Response Cache
    print("4. Response Cache:")
    cache = ResponseCache(cache_dir='test_cache/', ttl_seconds=3600)
    stats = cache.get_stats()
    print(f"   Cache stats: {stats}")
    
    print("\n✅ Demo complete!")

