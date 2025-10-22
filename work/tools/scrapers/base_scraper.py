"""
Base scraper class and utilities for Kurdish corpus expansion
"""

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import unicodedata


class SimpleQC:
    """Simple Quality Control for Kurdish text"""
    
    def __init__(self, min_words=10, max_words=30, min_kurdish_ratio=0.7):
        self.min_words = min_words
        self.max_words = max_words
        self.min_kurdish_ratio = min_kurdish_ratio
        
        # Kurdish character ranges
        self.kurdish_chars = set(
            'ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆهھەیێ'
            'ًٌٍَُِّْ'  # Diacritics
            '٠١٢٣٤٥٦٧٨٩'  # Arabic-Indic digits
            '،؛؟'  # Punctuation
        )
    
    def check(self, text):
        """Check if text passes quality requirements"""
        if not text or not isinstance(text, str):
            return False
        
        text = text.strip()
        if not text:
            return False
        
        # Check word count
        words = text.split()
        if len(words) < self.min_words or len(words) > self.max_words:
            return False
        
        # Check Kurdish character ratio
        total_chars = 0
        kurdish_count = 0
        
        for char in text:
            if char.isalpha() or char in self.kurdish_chars:
                total_chars += 1
                if char in self.kurdish_chars or '\u0600' <= char <= '\u06FF':
                    kurdish_count += 1
        
        if total_chars == 0:
            return False
        
        ratio = kurdish_count / total_chars
        return ratio >= self.min_kurdish_ratio


class BaseScraper(ABC):
    """Base class for all Kurdish news scrapers"""
    
    def __init__(self, name, headless=True):
        self.name = name
        self.sentences = set()
        self.stats = {}
        self.qc = SimpleQC()
        self.driver = None
        self.headless = headless
    
    @staticmethod
    def clean_error(exception):
        """Extract clean, concise error message from exception"""
        error_str = str(exception)
        
        # Get just the first line of error message
        first_line = error_str.split('\n')[0]
        
        # Simplify common Selenium errors
        if 'no such element' in first_line.lower():
            return "Element not found"
        elif 'timeout' in first_line.lower():
            return "Page timeout"
        elif 'stale element' in first_line.lower():
            return "Element changed"
        elif 'session' in first_line.lower() and 'deleted' in first_line.lower():
            return "Browser session lost"
        elif len(first_line) > 100:
            # Truncate very long error messages
            return first_line[:100] + "..."
        else:
            return first_line
    
    def init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver:
            return
        
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(
            service=Service('/usr/bin/chromedriver'),
            options=options
        )
        self.driver.set_page_load_timeout(30)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def add_sentence(self, text):
        """Add a sentence if it passes QC"""
        if text and self.qc.check(text):
            self.sentences.add(text.strip())
            return True
        return False
    
    def wait_for_element(self, selector, timeout=10, by=By.CSS_SELECTOR):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except:
            return None
    
    def safe_get(self, url, retries=3, delay=2):
        """Safely get URL with retries"""
        for attempt in range(retries):
            try:
                self.driver.get(url)
                time.sleep(delay)
                return True
            except Exception as e:
                if attempt < retries - 1:
                    print(f"      ⚠️  Retry {attempt + 1}/{retries}: {e}")
                    time.sleep(delay * 2)
                else:
                    print(f"      ❌ Failed to load: {url}")
                    return False
        return False
    
    @abstractmethod
    def scrape_political(self, **kwargs):
        """Scrape political news - must be implemented by subclass"""
        pass
    
    def scrape_specialized(self, **kwargs):
        """Scrape specialized categories - optional override"""
        raise NotImplementedError(f"{self.name} does not implement specialized scraping")
    
    def get_stats(self):
        """Get scraping statistics"""
        return {
            'name': self.name,
            'sentences': len(self.sentences),
            'stats': self.stats
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', sentences={len(self.sentences)})>"
