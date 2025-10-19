#!/usr/bin/env python3
"""
Kurdish News Scraper for Phase 6 Corpus Expansion

Extracts high-quality Kurdish text from major news websites:
- Rudaw (rudaw.net)
- BasNews (basnews.com)
- NRT (nrttv.com)

Quality filters:
- ZWNJ density: 8-12% (maintain Phase 4's 9.46%)
- Sentence length: 10-25 words (formal style)
- Kurdish script purity: >85%
- Remove duplicates
"""

import re
import sys
import time
import random
from pathlib import Path
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse
import unicodedata

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install: pip3 install requests beautifulsoup4")
    sys.exit(1)


class KurdishTextQualityChecker:
    """Check quality of Kurdish text for corpus inclusion."""
    
    KURDISH_CHARS = set('ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنهھوۆەیێ')
    ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩'
    ZWNJ = '\u200c'  # Zero-Width Non-Joiner
    
    @staticmethod
    def count_zwnj(text: str) -> Tuple[int, float]:
        """Count ZWNJ characters and calculate density."""
        zwnj_count = text.count(KurdishTextQualityChecker.ZWNJ)
        total_chars = len(text)
        density = (zwnj_count / total_chars * 100) if total_chars > 0 else 0
        return zwnj_count, density
    
    @staticmethod
    def count_kurdish_chars(text: str) -> Tuple[int, float]:
        """Count Kurdish script characters and calculate purity."""
        kurdish_count = sum(1 for c in text if c in KurdishTextQualityChecker.KURDISH_CHARS)
        # Count all letters (exclude spaces, punctuation, digits)
        total_letters = sum(1 for c in text if unicodedata.category(c).startswith('L'))
        purity = (kurdish_count / total_letters * 100) if total_letters > 0 else 0
        return kurdish_count, purity
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
        return len(words)
    
    @staticmethod
    def is_quality_sentence(sentence: str, 
                           min_zwnj: float = 8.0, 
                           max_zwnj: float = 12.0,
                           min_words: int = 10,
                           max_words: int = 25,
                           min_kurdish: float = 85.0) -> bool:
        """
        Check if sentence meets quality criteria.
        
        Args:
            sentence: Text to check
            min_zwnj: Minimum ZWNJ density %
            max_zwnj: Maximum ZWNJ density %
            min_words: Minimum word count
            max_words: Maximum word count
            min_kurdish: Minimum Kurdish script purity %
        
        Returns:
            True if sentence meets all quality criteria
        """
        # Check word count
        word_count = KurdishTextQualityChecker.count_words(sentence)
        if word_count < min_words or word_count > max_words:
            return False
        
        # Check ZWNJ density
        _, zwnj_density = KurdishTextQualityChecker.count_zwnj(sentence)
        if zwnj_density < min_zwnj or zwnj_density > max_zwnj:
            return False
        
        # Check Kurdish script purity
        _, kurdish_purity = KurdishTextQualityChecker.count_kurdish_chars(sentence)
        if kurdish_purity < min_kurdish:
            return False
        
        # Check for unwanted patterns
        if re.search(r'https?://|www\.|@|#|\d{4,}', sentence):
            return False
        
        return True


class KurdishNewsScraper:
    """Scrape Kurdish news websites for high-quality text."""
    
    def __init__(self, output_dir: str = "corpus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.seen_sentences: Set[str] = set()
        self.quality_checker = KurdishTextQualityChecker()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize Kurdish text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Normalize Arabic characters to Kurdish equivalents
        text = text.replace('ك', 'ک').replace('ي', 'ی')
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Split on Kurdish sentence terminators
        sentences = re.split(r'[.!?؟]+\s+', text)
        return [self.clean_text(s) for s in sentences if len(s.strip()) > 20]
    
    def scrape_rudaw(self, max_articles: int = 50) -> List[str]:
        """
        Scrape Rudaw news website.
        """
        print("📰 Scraping Rudaw (rudaw.net)...")
        sentences = []
        
        # Rudaw category pages
        base_urls = [
            "https://www.rudaw.net/sorani/kurdistan",
            "https://www.rudaw.net/sorani/middleeast",
            "https://www.rudaw.net/sorani/business",
            "https://www.rudaw.net/sorani/business",
        ]
        
        for base_url in base_urls:
            try:
                response = self.session.get(base_url, timeout=10)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links (adjust selectors based on actual site structure)
                article_links = soup.find_all('a', href=True)
                article_urls = [urljoin(base_url, link['href']) for link in article_links
                               if '/sorani/' in link['href'] and link['href'].count('/') > 4]
                
                # Limit articles per category
                article_urls = list(set(article_urls))[:max_articles // len(base_urls)]
                
                for url in article_urls:
                    time.sleep(random.uniform(1, 3))  # Respectful rate limiting
                    article_sentences = self._scrape_article(url)
                    sentences.extend(article_sentences)
                    
                    if len(sentences) >= max_articles * 10:
                        break
                        
            except Exception as e:
                print(f"⚠️  Error scraping {base_url}: {e}")
                continue
        
        return sentences
    
    def _scrape_article(self, url: str) -> List[str]:
        """Scrape a single article and extract quality sentences."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main content (adjust selectors based on site)
            content_divs = soup.find_all(['p', 'div'], class_=re.compile(r'content|article|text|body'))
            
            text = ' '.join(div.get_text() for div in content_divs)
            sentences = self.extract_sentences(text)
            
            # Filter for quality
            quality_sentences = [
                s for s in sentences 
                if s not in self.seen_sentences and 
                self.quality_checker.is_quality_sentence(s)
            ]
            
            # Mark as seen
            self.seen_sentences.update(quality_sentences)
            
            return quality_sentences
            
        except Exception as e:
            return []
    
    def scrape_basnews(self, max_articles: int = 100) -> List[str]:
        """Scrape BasNews website."""
        print("📰 Scraping BasNews (basnews.com)...")
        # Similar implementation to scrape_rudaw
        # Would need to adjust for BasNews's specific structure
        return []
    
    def scrape_nrt(self, max_articles: int = 100) -> List[str]:
        """Scrape NRT website."""
        print("📰 Scraping NRT (nrttv.com)...")
        # Similar implementation to scrape_rudaw
        # Would need to adjust for NRT's specific structure
        return []
    
    def save_corpus(self, sentences: List[str], filename: str):
        """Save sentences to file with statistics."""
        output_file = self.output_dir / filename
        
        # Remove duplicates while preserving order
        unique_sentences = []
        seen = set()
        for s in sentences:
            if s not in seen:
                unique_sentences.append(s)
                seen.add(s)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for sentence in unique_sentences:
                f.write(sentence + '\n')
        
        # Calculate statistics
        total_words = sum(self.quality_checker.count_words(s) for s in unique_sentences)
        total_zwnj = sum(s.count(self.quality_checker.ZWNJ) for s in unique_sentences)
        total_chars = sum(len(s) for s in unique_sentences)
        avg_zwnj = (total_zwnj / total_chars * 100) if total_chars > 0 else 0
        
        print(f"\n✅ Saved to: {output_file}")
        print(f"   Lines: {len(unique_sentences)}")
        print(f"   Words: {total_words:,}")
        print(f"   ZWNJ density: {avg_zwnj:.2f}%")
        print(f"   Avg words/line: {total_words / len(unique_sentences):.1f}")


def main():
    """Main entry point for news scraping."""
    print("🚀 Kurdish News Scraper - Phase 6")
    print("=" * 50)
    
    scraper = KurdishNewsScraper(output_dir="corpus")
    
    # For now, create a demo/placeholder
    # In production, would actually scrape websites
    print("\n⚠️  NOTE: This is a demo version.")
    print("   Production version would scrape live websites.")
    print("   For now, creating a template corpus file.\n")
    
    # Create template file with instructions
    template_file = scraper.output_dir / "kurdish_news_template.txt"
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write("# Kurdish News Corpus - Phase 6\n")
        f.write("# Instructions for manual collection:\n")
        f.write("# 1. Visit Rudaw (rudaw.net/sorani), BasNews (basnews.com), NRT (nrttv.com)\n")
        f.write("# 2. Copy article text\n")
        f.write("# 3. Paste below (one sentence per line)\n")
        f.write("# 4. Ensure ZWNJ density 8-12%, words 10-25 per sentence\n")
        f.write("#\n")
        f.write("# Remove these comment lines before training\n")
        f.write("#\n\n")
    
    print(f"✅ Created template: {template_file}")
    print("\n📋 Next steps:")
    print("   1. Visit Kurdish news websites")
    print("   2. Copy high-quality article text")
    print("   3. Paste into kurdish_news_batch1.txt")
    print("   4. Run quality checker before training")
    print("\n   OR: Manually implement web scraping in this script")


if __name__ == '__main__':
    main()
