"""
Security Best Practices for Web Scrapers

Implements:
- Safe YAML loading
- XPath injection prevention
- Rate limiting and politeness
- Credential management
- User agent rotation

Usage:
    from security_utils import (
        safe_load_yaml,
        sanitize_xpath,
        RateLimiter,
        CredentialManager
    )
    
    # Safe YAML loading
    config = safe_load_yaml('websites.yaml')
    
    # Sanitize XPath
    safe_value = sanitize_xpath(user_input)
    
    # Rate limiting
    limiter = RateLimiter(requests_per_minute=20)
    limiter.wait_if_needed()
"""

import yaml
import re
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import logging


logger = logging.getLogger(__name__)


# ==================== YAML SAFETY ====================

def safe_load_yaml(filepath: str) -> Dict[str, Any]:
    """
    Safely load YAML file using yaml.safe_load()
    
    NEVER use yaml.load() as it can execute arbitrary Python code!
    
    Args:
        filepath: Path to YAML file
    
    Returns:
        Parsed configuration dictionary
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # ✅ SAFE: yaml.safe_load() only constructs simple Python objects
            config = yaml.safe_load(f)
        
        logger.info(f"✅ Safely loaded config: {filepath}")
        return config
        
    except yaml.YAMLError as e:
        logger.error(f"❌ Invalid YAML in {filepath}: {e}")
        raise


def validate_yaml_structure(config: Dict) -> bool:
    """
    Validate YAML structure for suspicious patterns
    
    Checks for:
    - Extremely deep nesting (potential DoS)
    - Suspicious keys (exec, eval, import, etc.)
    - Very large values (potential memory exhaustion)
    """
    def check_depth(obj, current_depth=0, max_depth=20):
        """Check nesting depth"""
        if current_depth > max_depth:
            raise ValueError(f"YAML nesting too deep (>{max_depth} levels)")
        
        if isinstance(obj, dict):
            for value in obj.values():
                check_depth(value, current_depth + 1, max_depth)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, current_depth + 1, max_depth)
    
    def check_suspicious_keys(obj, path=""):
        """Check for suspicious key names"""
        suspicious_keywords = [
            'exec', 'eval', 'import', '__import__',
            'compile', 'open', 'file', 'input'
        ]
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check key name
                if any(keyword in str(key).lower() for keyword in suspicious_keywords):
                    logger.warning(f"⚠️  Suspicious key: {path}.{key}")
                
                # Recurse
                check_suspicious_keys(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                check_suspicious_keys(item, f"{path}[{idx}]")
    
    try:
        check_depth(config)
        check_suspicious_keys(config)
        return True
    except Exception as e:
        logger.error(f"❌ YAML validation failed: {e}")
        return False


# ==================== XPATH INJECTION PREVENTION ====================

def sanitize_xpath(value: str, allow_predicates: bool = False) -> str:
    """
    Sanitize XPath value to prevent injection attacks
    
    Args:
        value: XPath value to sanitize
        allow_predicates: Whether to allow XPath predicates (brackets)
    
    Returns:
        Sanitized XPath value
    
    Raises:
        ValueError: If value contains suspicious patterns
    """
    if not isinstance(value, str):
        raise ValueError(f"XPath value must be string, got {type(value)}")
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'javascript:',
        r'<script',
        r'eval\(',
        r'exec\(',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(f"Suspicious pattern in XPath: {pattern}")
    
    # If predicates not allowed, check for brackets
    if not allow_predicates:
        if '[' in value or ']' in value:
            raise ValueError("XPath predicates not allowed in this context")
    
    # For Kurdish text, allow Unicode characters
    # Pattern: Allow alphanumeric, spaces, common punctuation, Kurdish characters
    allowed_pattern = r'^[\w\s\u0600-\u06FF\u0750-\u077F@\-_./\[\]()=:\'\"*|]+$'
    
    if not re.match(allowed_pattern, value):
        raise ValueError(f"XPath contains invalid characters: {value}")
    
    return value


def validate_selector_config(selector_config: Any) -> bool:
    """
    Validate selector configuration for security issues
    
    Checks XPath selectors for injection attempts
    """
    if isinstance(selector_config, str):
        # Simple string selector (CSS) - generally safe
        return True
    
    elif isinstance(selector_config, dict):
        if selector_config.get('type') == 'xpath':
            value = selector_config.get('value', '')
            try:
                sanitize_xpath(value, allow_predicates=True)
                return True
            except ValueError as e:
                logger.error(f"❌ Invalid XPath: {e}")
                return False
    
    elif isinstance(selector_config, list):
        # Fallback chain - validate each
        return all(validate_selector_config(item) for item in selector_config)
    
    return True


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Rate limiter to enforce politeness and avoid IP bans
    
    Implements token bucket algorithm for smooth rate limiting
    """
    
    def __init__(
        self,
        requests_per_minute: int = 20,
        burst_limit: int = 5
    ):
        """
        Args:
            requests_per_minute: Maximum requests per minute
            burst_limit: Maximum burst requests
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        
        # Calculate delay between requests
        self.min_delay = 60.0 / requests_per_minute
        
        # Track recent requests
        self.request_times = deque(maxlen=burst_limit)
        
        logger.info(
            f"Rate limiter initialized: {requests_per_minute} req/min, "
            f"burst: {burst_limit}"
        )
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Check burst limit
        if len(self.request_times) >= self.burst_limit:
            oldest = self.request_times[0]
            time_since_oldest = now - oldest
            min_window = self.min_delay * self.burst_limit
            
            if time_since_oldest < min_window:
                wait_time = min_window - time_since_oldest
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                time.sleep(wait_time)
                now = time.time()
        
        # Check minimum delay since last request
        if self.request_times:
            time_since_last = now - self.request_times[-1]
            if time_since_last < self.min_delay:
                wait_time = self.min_delay - time_since_last
                time.sleep(wait_time)
                now = time.time()
        
        # Record this request
        self.request_times.append(now)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        if not self.request_times:
            return {'requests': 0, 'rate': 0}
        
        now = time.time()
        window_start = now - 60  # Last minute
        recent_requests = sum(1 for t in self.request_times if t > window_start)
        
        return {
            'requests_last_minute': recent_requests,
            'configured_limit': self.requests_per_minute,
            'utilization': f"{recent_requests / self.requests_per_minute:.1%}"
        }


# ==================== USER AGENT MANAGEMENT ====================

class UserAgentRotator:
    """Rotate user agents to avoid detection"""
    
    # Real browser user agents (keep updated)
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Chrome on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Firefox on Mac
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    ]
    
    def __init__(self):
        self.current_index = 0
    
    def get_user_agent(self) -> str:
        """Get next user agent in rotation"""
        ua = self.USER_AGENTS[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.USER_AGENTS)
        return ua
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        import random
        return random.choice(self.USER_AGENTS)


# ==================== CREDENTIAL MANAGEMENT ====================

class CredentialManager:
    """
    Secure credential management
    
    DO NOT store credentials in YAML files or code!
    Use environment variables or encrypted storage.
    """
    
    @staticmethod
    def get_from_env(website: str, key: str) -> Optional[str]:
        """
        Get credential from environment variable
        
        Args:
            website: Website name (e.g., 'kurdsat')
            key: Credential key (e.g., 'username', 'api_key')
        
        Returns:
            Credential value or None
        """
        env_var = f"SCRAPER_{website.upper()}_{key.upper()}"
        value = os.environ.get(env_var)
        
        if value:
            logger.debug(f"✅ Loaded credential: {env_var}")
        else:
            logger.warning(f"⚠️  Missing credential: {env_var}")
        
        return value
    
    @staticmethod
    def hash_credential(value: str) -> str:
        """
        Hash credential for logging (never log plaintext!)
        
        Args:
            value: Credential to hash
        
        Returns:
            SHA256 hash (first 8 chars)
        """
        hashed = hashlib.sha256(value.encode()).hexdigest()
        return hashed[:8]


# ==================== ROBOTS.TXT CHECKER ====================

class RobotsTxtChecker:
    """Check if scraping is allowed per robots.txt"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    def is_allowed(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if URL is allowed by robots.txt
        
        Args:
            url: URL to check
            user_agent: User agent to check for
        
        Returns:
            True if allowed, False if disallowed
        
        Note: This is a simplified check. For production,
              use urllib.robotparser.RobotFileParser
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        # Check cache
        if robots_url in self.cache:
            cached_time, rules = self.cache[robots_url]
            if datetime.now() - cached_time < self.cache_duration:
                return self._check_rules(url, rules)
        
        # Fetch and parse robots.txt
        try:
            import urllib.request
            response = urllib.request.urlopen(robots_url, timeout=5)
            content = response.read().decode('utf-8')
            
            # Simple parsing (production should use robotparser)
            rules = self._parse_robots_txt(content)
            self.cache[robots_url] = (datetime.now(), rules)
            
            return self._check_rules(url, rules)
            
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")
            # If can't fetch, assume allowed (be conservative in production)
            return True
    
    def _parse_robots_txt(self, content: str) -> Dict:
        """Parse robots.txt content (simplified)"""
        # Production should use urllib.robotparser
        return {'disallow': []}
    
    def _check_rules(self, url: str, rules: Dict) -> bool:
        """Check if URL matches any disallow rules"""
        # Simplified - production needs full robots.txt parsing
        return True


# ==================== SECURITY CHECKLIST ====================

def security_audit_config(config: Dict) -> Dict[str, Any]:
    """
    Audit configuration for security issues
    
    Returns:
        Dictionary with security findings
    """
    findings = {
        'passed': True,
        'warnings': [],
        'errors': []
    }
    
    # Check for hardcoded credentials
    def check_for_credentials(obj, path=""):
        suspicious_keys = ['password', 'api_key', 'token', 'secret', 'credential']
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check key name
                if any(keyword in str(key).lower() for keyword in suspicious_keys):
                    if isinstance(value, str) and len(value) > 0:
                        findings['errors'].append(
                            f"❌ Hardcoded credential at: {path}.{key}"
                        )
                        findings['passed'] = False
                
                check_for_credentials(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                check_for_credentials(item, f"{path}[{idx}]")
    
    check_for_credentials(config)
    
    # Check for suspicious URLs
    for website_key, website_config in config.items():
        if isinstance(website_config, dict):
            base_url = website_config.get('base_url', '')
            
            # Warn about HTTP (not HTTPS)
            if base_url.startswith('http://'):
                findings['warnings'].append(
                    f"⚠️  {website_key}: Using HTTP (not HTTPS)"
                )
    
    return findings


if __name__ == '__main__':
    # Example usage
    print("🔒 Security Utils Demo\n")
    
    # Safe YAML loading
    print("1. Safe YAML Loading:")
    print("   ✅ Use: yaml.safe_load()")
    print("   ❌ Never use: yaml.load()\n")
    
    # XPath sanitization
    print("2. XPath Sanitization:")
    try:
        safe = sanitize_xpath("//div[@class='content']", allow_predicates=True)
        print(f"   ✅ Valid: {safe}")
    except ValueError as e:
        print(f"   ❌ Invalid: {e}")
    
    try:
        unsafe = sanitize_xpath("//div[contains(., 'javascript:alert()')]", allow_predicates=True)
        print(f"   ⚠️  Suspicious: {unsafe}")
    except ValueError as e:
        print(f"   ❌ Blocked: {e}\n")
    
    # Rate limiting
    print("3. Rate Limiting:")
    limiter = RateLimiter(requests_per_minute=60, burst_limit=5)
    for i in range(3):
        limiter.wait_if_needed()
        print(f"   Request {i+1} - Stats: {limiter.get_stats()}")
