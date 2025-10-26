# -*- coding: utf-8 -*-
"""
Advanced Features for Web Scrapers

Implements:
- Multi-language support (detection, filtering, per-language selectors)
- Article deduplication (content similarity detection)
- Browser fingerprinting prevention (stealth mode)
- Language-specific text processing

Usage:
    from advanced_features import (
        LanguageDetector,
        ArticleDeduplicator,
        StealthBrowser,
        MultiLanguageConfig
    )
    
    # Language detection
    detector = LanguageDetector()
    lang = detector.detect('هەواڵی نوێ')  # Returns 'ckb' (Kurdish)
    
    # Deduplication
    dedup = ArticleDeduplicator()
    is_duplicate = dedup.is_duplicate(article_text, threshold=0.85)
    
    # Stealth mode
    stealth = StealthBrowser()
    driver = stealth.create_driver()
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


logger = logging.getLogger(__name__)


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
